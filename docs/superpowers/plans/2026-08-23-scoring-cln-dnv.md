# Reference Scorer — CLN_DNV (SM 4 Table 3) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_cln_dnv` (SM 4 Table 3) — the de-novo pathogenic clinical code, additive on CLN_AFF. Per-`Case`; `parent_code="CLN"`, single sub-code `CLN_DNV`. First CLN scorer to **consume** `moi` (the biallelic fold).

**Architecture:** Extends `scoring/hod/clinical.py`. Non-authoritative; scoring out of root `__all__` (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Table 3 (spec-verified):** SPECIFIC (mono only) confirmed `+7.0` / unconfirmed `+2.0`; CONSISTENT confirmed `+4.0` / unconfirmed `+1.0`; INCONSISTENT `+0.0`. Biallelic disorder (`moi in {AR, XLR}`) folds SPECIFIC→CONSISTENT. Confirmed = `confirmed_parental_relationship == TRUE`. The `+7.0` `**` region caveat is not applied (no VBC-region field) — flagged in provenance.

---

## Task 1: `reference_score_cln_dnv` (TDD)

**Files:** Modify `src/svcv4_model/scoring/hod/clinical.py`, create `tests/test_cln_dnv_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_cln_dnv_scoring.py`

```python
"""Tests for reference_score_cln_dnv (SM 4 Table 3, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import MOI, Case, PhenoSpecificity, TriState
from svcv4_model.scoring import reference_score_cln_dnv

SPEC = PhenoSpecificity.SPECIFIC
CONS = PhenoSpecificity.CONSISTENT
INC = PhenoSpecificity.INCONSISTENT


def _dnv(case: Case, moi: MOI = MOI.AD) -> float | None:
    return reference_score_cln_dnv(case, moi=moi).sub_code_points.get("CLN_DNV")


def test_specific_mono_confirmed_and_unconfirmed() -> None:
    conf = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.TRUE)
    unconf = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.FALSE)
    r = reference_score_cln_dnv(conf, moi=MOI.AD)
    assert r.parent_code == "CLN"
    assert r.sub_code_points["CLN_DNV"] == 7.0
    assert r.parent_total == 7.0
    assert _dnv(unconf) == 2.0


def test_consistent_confirmed_and_unconfirmed() -> None:
    conf = Case(pheno_specificity_for_mde=CONS, confirmed_parental_relationship=TriState.TRUE)
    unconf = Case(pheno_specificity_for_mde=CONS, confirmed_parental_relationship=TriState.FALSE)
    assert _dnv(conf) == 4.0
    assert _dnv(unconf) == 1.0


def test_inconsistent_is_recorded_zero() -> None:
    c = Case(pheno_specificity_for_mde=INC, confirmed_parental_relationship=TriState.TRUE)
    r = reference_score_cln_dnv(c, moi=MOI.AD)
    assert r.sub_code_points["CLN_DNV"] == 0.0
    assert r.parent_total == 0.0


def test_biallelic_disorder_folds_specific_to_consistent() -> None:
    # SPECIFIC row is mono-only; AR/XLR disorders use the CONSISTENT row
    conf = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.TRUE)
    assert _dnv(conf, moi=MOI.AR) == 4.0
    assert _dnv(conf, moi=MOI.XLR) == 4.0
    assert _dnv(conf, moi=MOI.AD) == 7.0  # mono keeps SPECIFIC


def test_unconfirmed_when_parental_none_or_unknown() -> None:
    none_case = Case(pheno_specificity_for_mde=SPEC)  # confirmed_parental_relationship None
    unk = Case(
        pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.UNKNOWN
    )
    assert _dnv(none_case) == 2.0
    assert _dnv(unk) == 2.0


def test_provenance_flags_plus7_caveat() -> None:
    c = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.TRUE)
    r = reference_score_cln_dnv(c, moi=MOI.AD)
    assert any("coding" in p or "**" in p for p in r.provenance)


def test_nd_when_pheno_specificity_none() -> None:
    r = reference_score_cln_dnv(Case(), moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect ImportError.** `uv run pytest tests/test_cln_dnv_scoring.py -q`

- [ ] **Step 3: Implement `reference_score_cln_dnv`** in `clinical.py` (add a module constant near `_CLN_AFF_POINTS`; `MOI`/`PhenoSpecificity`/`TriState` already imported):

```python
_CLN_DNV_POINTS = {
    PhenoSpecificity.SPECIFIC: (7.0, 2.0),  # (confirmed, unconfirmed)
    PhenoSpecificity.CONSISTENT: (4.0, 1.0),
    PhenoSpecificity.INCONSISTENT: (0.0, 0.0),
}
_BIALLELIC_MOI = frozenset({MOI.AR, MOI.XLR})


def reference_score_cln_dnv(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_DNV de-novo points for one affected proband
    (SM 4 Table 3), additive on CLN_AFF. CSpec is authoritative. ``moi`` selects the mono-vs-
    biallelic phenotype-consistency fold (AR/XLR disorders use the CONSISTENT row; SPECIFIC is
    mono-only). The +7.0 region caveat is not applied (no VBC-region annotation).
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (cross-proband sum + summing '
        "CLN_AFF + CLN_DNV per proband deferred to case aggregation)."
    ]
    pheno = case.pheno_specificity_for_mde
    if pheno is None:
        prov.append("CLN_DNV: _ND (no pheno_specificity_for_mde)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    row = pheno
    if moi in _BIALLELIC_MOI and pheno == PhenoSpecificity.SPECIFIC:
        row = PhenoSpecificity.CONSISTENT
        prov.append(
            "CLN_DNV: biallelic disorder (AR/XLR) -> SPECIFIC folds to CONSISTENT "
            "(XLR-by-sex + SD summing deferred to aggregation)."
        )

    confirmed = case.confirmed_parental_relationship == TriState.TRUE
    pts = _CLN_DNV_POINTS[row][0 if confirmed else 1]
    if row == PhenoSpecificity.SPECIFIC and confirmed:
        prov.append(
            "CLN_DNV: +7.0 ** -- SM 4 recommends reducing this if the VBC is outside "
            "coding/adjacent-intronic regions; not applied (no VBC-region annotation)."
        )
    prov.append(f"CLN_DNV: {pts} (row={row.value}, confirmed_parental={confirmed})")

    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_DNV": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 4: Export** — `scoring/__init__.py`: add `reference_score_cln_dnv` to the clinical import (alphabetical: `cln_aff_biallelic` < `cln_aff_mono` < `cln_alt` < `cln_dnv` < `cln_uaf`) and to `__all__` (same position, after `reference_score_cln_alt`).

- [ ] **Step 5: Run** `uv run pytest tests/test_cln_dnv_scoring.py -q` — all PASS.
- [ ] **Step 6: Commit** — `git commit -am "feat(scoring): add reference_score_cln_dnv (SM 4 Table 3)"`

---

## Task 2: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — update the CLN bullet: CLN_AFF now joined by `reference_score_cln_dnv` (Table 3, de-novo, additive on CLN_AFF — phenotype consistency × parental confirmation; biallelic disorders fold SPECIFIC→CONSISTENT via `moi`; the `+7.0` region caveat is un-applied/flagged). CLN_CCS + LOC follow.

- [ ] **Step 2 (optional): `known-gaps.md`** — a Model-gap row: no VBC-region/molecular-consequence annotation, so the SM 4 CLN_DNV `+7.0` reduction (VBC outside coding/adjacent-intronic) can't be computed.

- [ ] **Step 3: Build strict** — `uv run mkdocs build --strict` (exit 0).
- [ ] **Step 4: Commit** — `git commit -am "docs: note the CLN_DNV scorer; log the VBC-region annotation gap"`

---

## Task 3: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`export_schemas.py` then `git diff --quiet -- schemas/json docs/workflows/case-model.md`); `mkdocs build --strict` (exit 0); no scorer schema leaked; clean tree.

---

## Notes for the implementer

- `moi` **is consumed** here (the AR/XLR biallelic fold) — do not treat it as unused.
- `_CLN_DNV_POINTS[row]` is safe: `row` is always a `PhenoSpecificity` member (pheno non-None past the guard; `CONSISTENT` on the fold), all three are keys.
- `_CLN_DNV_POINTS`/`_BIALLELIC_MOI` module-private. Watch LL 100 on the provenance strings.
