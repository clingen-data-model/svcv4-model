# Reference Scorer — CLN_AFF monoallelic (SM 4 Table 1) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_cln_aff_mono` (SM 4 Table 1) + generalize the shared classifier (`_classify_plp` → `_classify`, adding VUS/B/LB). Per-`Case`; `parent_code="CLN"`, single sub-code `CLN_AFF`.

**Architecture:** Extends `scoring/hod/clinical.py`. The generalized `_classify` requires updating the two merged benign scorers **differently** (cln_uaf: rename only; cln_alt: gate → `in {"P","LP"}`). Non-authoritative; scoring out of root `__all__` (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Table 1 (spec-verified):** SPECIFIC best/middle/plp-alt = `+1.0/+0.5/+0.0`; CONSISTENT = `+0.5/+0.25/+0.0`; INCONSISTENT = `+0.0`. best tier = `covers_all_genes==TRUE AND non_genetic_excluded==TRUE AND no P/LP AND no VUS additional variant` (and `case.testing` not None); P/LP-alt = any P/LP additional variant; else middle.

---

## Task 1: generalize `_classify` (behaviour-preserving refactor, TDD-guarded)

**Files:** Modify `src/svcv4_model/scoring/hod/clinical.py`; the existing `tests/test_cln_benign_scoring.py` is the guard.

- [ ] **Step 1: Rename + extend `_classify_plp` → `_classify`** in `clinical.py`:

```python
def _classify(classification: str | None) -> str | None:
    """Normalize the placeholder ``classification`` string to a category or None.

    Returns 'P' / 'LP' / 'VUS' / 'B' / 'LB' (or None). ``AdditionalVariant`` /
    ``CompoundHetVariant`` carry ``classification`` as a placeholder str (not the
    ``VariantClassification`` enum -- a flagged model gap). Accepts the enum values
    (PATHOGENIC / LIKELY_PATHOGENIC / VUS / BENIGN / LIKELY_BENIGN) and the P / LP / VUS / B / LB
    shorthands, case-insensitively.
    """
    if classification is None:
        return None
    c = classification.strip().upper()
    if c in {"P", "PATHOGENIC"}:
        return "P"
    if c in {"LP", "LIKELY_PATHOGENIC"}:
        return "LP"
    if c == "VUS":
        return "VUS"
    if c in {"B", "BENIGN"}:
        return "B"
    if c in {"LB", "LIKELY_BENIGN"}:
        return "LB"
    return None
```

- [ ] **Step 2: Update the two benign callers** (differently — see spec DD3):
  - `reference_score_cln_uaf`: change the call `_classify_plp(...)` → `_classify(...)` only. Its `{"P":"rec_trans_p","LP":"rec_trans_lp"}.get(trans, "no_trans_plp")` already routes VUS/B/LB/None → `no_trans_plp` (correct per Table 5), so no gate change.
  - `reference_score_cln_alt`: change the filter from `if _classify_plp(v.classification)` (truthy) to `if _classify(v.classification) in {"P", "LP"}` — `_classify` now returns truthy VUS/B/LB, so the truthy filter would wrongly admit them.
  - Update the docstring reference in `_classify` / the test import (`_classify_plp` → `_classify`).

- [ ] **Step 3: Update `tests/test_cln_benign_scoring.py`** — the `test_classify_plp_normalization` test imports `_classify_plp`; rename to `_classify` and add `assert _classify("VUS") == "VUS"`, `assert _classify("B") == "B"`, `assert _classify("benign") == "B"`, `assert _classify("LB") == "LB"`. Keep the P/LP/None cases.

- [ ] **Step 4: Run** `uv run pytest tests/test_cln_benign_scoring.py -q` — all still PASS (behaviour-preserving; the cln_alt VUS-only `_ND` test and the cln_uaf trans-P/LP tests are the guards).

- [ ] **Step 5: Commit** — `git commit -am "refactor(scoring): generalize _classify_plp -> _classify (P/LP/VUS/B/LB); keep benign gates"`

---

## Task 2: `reference_score_cln_aff_mono` (TDD)

**Files:** Modify `src/svcv4_model/scoring/hod/clinical.py`, create `tests/test_cln_aff_mono_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_cln_aff_mono_scoring.py`

```python
"""Tests for reference_score_cln_aff_mono (SM 4 Table 1, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    Case,
    CaseTesting,
    PhenoSpecificity,
    TriState,
)
from svcv4_model.scoring import reference_score_cln_aff_mono

SPEC = PhenoSpecificity.SPECIFIC
CONS = PhenoSpecificity.CONSISTENT
INC = PhenoSpecificity.INCONSISTENT

_THOROUGH = CaseTesting(
    covers_all_genes_relevant_to_mde=TriState.TRUE,
    non_genetic_etiology_excluded=TriState.TRUE,
)


def _av(classification: str) -> AdditionalVariant:
    return AdditionalVariant(classification=classification)


def test_specific_best_middle_plp() -> None:
    best = Case(pheno_specificity_for_mde=SPEC, testing=_THOROUGH)
    middle = Case(
        pheno_specificity_for_mde=SPEC,
        testing=CaseTesting(covers_all_genes_relevant_to_mde=TriState.FALSE),
    )
    vus = Case(pheno_specificity_for_mde=SPEC, testing=_THOROUGH, additional_variants=[_av("VUS")])
    plp = Case(pheno_specificity_for_mde=SPEC, testing=_THOROUGH, additional_variants=[_av("P")])
    assert reference_score_cln_aff_mono(best, moi=MOI.AD).sub_code_points["CLN_AFF"] == 1.0
    assert reference_score_cln_aff_mono(middle, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5
    assert reference_score_cln_aff_mono(vus, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5
    assert reference_score_cln_aff_mono(plp, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.0


def test_consistent_best_middle_plp() -> None:
    best = Case(pheno_specificity_for_mde=CONS, testing=_THOROUGH)
    middle = Case(pheno_specificity_for_mde=CONS)  # testing None -> middle
    plp = Case(pheno_specificity_for_mde=CONS, testing=_THOROUGH, additional_variants=[_av("LP")])
    assert reference_score_cln_aff_mono(best, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5
    assert reference_score_cln_aff_mono(middle, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.25
    assert reference_score_cln_aff_mono(plp, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.0


def test_inconsistent_is_recorded_zero() -> None:
    c = Case(pheno_specificity_for_mde=INC, testing=_THOROUGH)
    r = reference_score_cln_aff_mono(c, moi=MOI.AD)
    assert r.parent_code == "CLN"
    assert r.sub_code_points["CLN_AFF"] == 0.0
    assert r.parent_total == 0.0


def test_best_tier_tristate_edges() -> None:
    # None/UNKNOWN on either testing flag -> middle; a B/LB alt does NOT block best
    unk = Case(
        pheno_specificity_for_mde=SPEC,
        testing=CaseTesting(
            covers_all_genes_relevant_to_mde=TriState.TRUE,
            non_genetic_etiology_excluded=TriState.UNKNOWN,
        ),
    )
    benign_alt = Case(
        pheno_specificity_for_mde=SPEC, testing=_THOROUGH, additional_variants=[_av("B")]
    )
    assert reference_score_cln_aff_mono(unk, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5
    assert reference_score_cln_aff_mono(benign_alt, moi=MOI.AD).sub_code_points["CLN_AFF"] == 1.0


def test_testing_none_does_not_crash() -> None:
    c = Case(pheno_specificity_for_mde=SPEC)  # testing None
    assert reference_score_cln_aff_mono(c, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5


def test_nd_when_pheno_specificity_none() -> None:
    r = reference_score_cln_aff_mono(Case(), moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect ImportError.** `uv run pytest tests/test_cln_aff_mono_scoring.py -q`

- [ ] **Step 3: Implement `reference_score_cln_aff_mono`** in `clinical.py` (add the import `PhenoSpecificity, TriState` to the `from svcv4_model.case import ...` line, MOI-first constant ordering preserved):

```python
_CLN_AFF_POINTS = {
    PhenoSpecificity.SPECIFIC: {"best": 1.0, "middle": 0.5, "plp_alt": 0.0},
    PhenoSpecificity.CONSISTENT: {"best": 0.5, "middle": 0.25, "plp_alt": 0.0},
}


def reference_score_cln_aff_mono(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_AFF pathogenic points for one affected
    monoallelic proband (SM 4 Table 1). CSpec is authoritative. ``moi`` accepted for signature
    parity (Table 1 has no MOI axis; table selection/routing is deferred to aggregation).
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (table selection + cross-proband '
        "sum + the AD +1.0/proband ceiling-on-sum deferred to case aggregation)."
    ]
    pheno = case.pheno_specificity_for_mde
    if pheno is None:
        prov.append("CLN_AFF: _ND (no pheno_specificity_for_mde)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    if pheno == PhenoSpecificity.INCONSISTENT:
        pts = 0.0
        prov.append("CLN_AFF: 0.0 (phenotype INCONSISTENT -- SM 4 Table 1; -> CLN_UAF)")
    else:  # SPECIFIC or CONSISTENT
        cats = {_classify(v.classification) for v in case.additional_variants}
        t = case.testing
        thorough = (
            t is not None
            and t.covers_all_genes_relevant_to_mde == TriState.TRUE
            and t.non_genetic_etiology_excluded == TriState.TRUE
        )
        if cats & {"P", "LP"}:
            tier = "plp_alt"
        elif thorough and "VUS" not in cats:
            tier = "best"
        else:
            tier = "middle"
        pts = _CLN_AFF_POINTS[pheno][tier]
        prov.append(f"CLN_AFF: {pts} (phenotype={pheno}, tier={tier})")

    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_AFF": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 4: Export** — `scoring/__init__.py`: add `reference_score_cln_aff_mono` to the clinical import (`from svcv4_model.scoring.hod.clinical import reference_score_cln_aff_mono, reference_score_cln_alt, reference_score_cln_uaf` — alphabetical: `aff_mono` < `alt` < `uaf`) and to `__all__` after `reference_score_canonical_splice` (canonical_splice < cln_aff_mono < cln_alt < cln_uaf).

- [ ] **Step 5: Run** `uv run pytest tests/test_cln_aff_mono_scoring.py -q` — all PASS.
- [ ] **Step 6: Commit** — `git commit -am "feat(scoring): add reference_score_cln_aff_mono (SM 4 Table 1)"`

---

## Task 3: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — update the CLN bullet to add CLN_AFF (monoallelic):

```markdown
- **Clinical Observations** (SM 4) — `reference_score_cln_uaf` (Table 5) + `reference_score_cln_alt`
  (Table 4) benign codes, and `reference_score_cln_aff_mono` (Table 1) the pathogenic monoallelic
  CLN_AFF (phenotype consistency x testing-thoroughness tier). Per-`Case` (`parent_code="CLN"`);
  cross-proband sum, the CLN_CCS exclusivity rule, the AD `+1.0`/proband ceiling-on-sum, table
  selection / X-linked routing, and semidominant summing are deferred to case aggregation. Shared
  `_classify` normalizes the placeholder variant `classification`. CLN_AFF biallelic (Table 2),
  CLN_DNV, CLN_CCS and the LOC codes follow.
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (exit 0).
- [ ] **Step 3: Commit** — `git commit -am "docs: note the CLN_AFF monoallelic scorer"`

---

## Task 4: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`export_schemas.py` then `git diff --quiet -- schemas/json docs/workflows/case-model.md`); `mkdocs build --strict` (exit 0); no scorer schema leaked; clean tree.

---

## Notes for the implementer

- The `_classify` generalization is the risky bit: `reference_score_cln_alt` MUST switch its filter to `in {"P","LP"}` (the truthy filter would now admit VUS/B/LB); `reference_score_cln_uaf` needs ONLY the rename (its `.get` default handles the rest). The benign tests are the behaviour-preservation guard.
- Guard `case.testing is None` before dereferencing `covers_all_genes_relevant_to_mde` / `non_genetic_etiology_excluded`.
- `_classify` is module-private (not exported). `moi` unused in cln_aff_mono (intentional; ARG not in ruff select). Watch LL 100 on the provenance strings.
