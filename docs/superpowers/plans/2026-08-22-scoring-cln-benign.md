# Reference Scorer — CLN benign pair (CLN_UAF + CLN_ALT, SM 4) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_cln_uaf` (Table 5) + `reference_score_cln_alt` (Table 4) — the two benign per-`Case` CLN codes. Two separate per-code functions in `scoring/hod/clinical.py`, each returning a `ScoreResult` for its single code (`parent_code="CLN"`).

**Architecture:** Per-`Case` (one proband); cross-proband sum + CLN_CCS exclusivity deferred to case-aggregation. `moi` is a required kwarg (mirrors POP). A shared `_classify_plp` normalizes the placeholder `classification` string. Non-authoritative; scoring out of root `__all__` (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Tables (spec-verified vs SM 4):** UAF cols dom/rec-homo-hemi/rec-trans-P = `−4/−2/0` by penetrance; rec-trans-LP = `−2/−1/0`. ALT: `MONO_GT_…`→0, `MONO_EQ_…`→−0.5, `BIALLELIC_LT_…`→−1.0 (same-gene + penetrance>80% only, else 0). `>80%` = `{PCT_80_100, NEAR_100}` (flagged).

---

## Task 1: `_classify_plp` + `reference_score_cln_uaf` (TDD)

**Files:** Create `src/svcv4_model/scoring/hod/clinical.py`, `tests/test_cln_benign_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_cln_benign_scoring.py`

```python
"""Tests for the CLN benign-pair scorers (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    AgeMatchedPenetrance,
    Case,
    CompoundHetVariant,
    MOI,
    PhenoSeverity,
    Zygosity,
)
from svcv4_model.scoring import reference_score_cln_alt, reference_score_cln_uaf

NEAR = AgeMatchedPenetrance.NEAR_100
MID = AgeMatchedPenetrance.PCT_80_100
LOW = AgeMatchedPenetrance.LT_80


def test_uaf_dominant_penetrance_rows() -> None:
    for pen, expected in [(NEAR, -4.0), (MID, -2.0), (LOW, 0.0)]:
        c = Case(age_matched_penetrance=pen)
        r = reference_score_cln_uaf(c, moi=MOI.AD)
        assert r.parent_code == "CLN"
        assert r.sub_code_points["CLN_UAF"] == expected
        assert r.parent_total == expected


def test_uaf_recessive_homozygous() -> None:
    c = Case(age_matched_penetrance=NEAR, vbc_zygosity=Zygosity.HOM)
    assert reference_score_cln_uaf(c, moi=MOI.AR).sub_code_points["CLN_UAF"] == -4.0


def test_uaf_xlinked_hemizygous() -> None:
    c = Case(age_matched_penetrance=NEAR, vbc_zygosity=Zygosity.HEMI)
    assert reference_score_cln_uaf(c, moi=MOI.XLR).sub_code_points["CLN_UAF"] == -4.0


def test_uaf_recessive_het_trans_p_vs_lp() -> None:
    # trans-P uses the -4/-2/0 column; trans-LP uses the reduced -2/-1/0 column
    p = Case(
        age_matched_penetrance=NEAR,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=CompoundHetVariant(classification="P"),
    )
    lp_near = Case(
        age_matched_penetrance=NEAR,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=CompoundHetVariant(classification="LP"),
    )
    lp_mid = Case(
        age_matched_penetrance=MID,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=CompoundHetVariant(classification="likely_pathogenic"),
    )
    assert reference_score_cln_uaf(p, moi=MOI.AR).sub_code_points["CLN_UAF"] == -4.0
    assert reference_score_cln_uaf(lp_near, moi=MOI.AR).sub_code_points["CLN_UAF"] == -2.0
    assert reference_score_cln_uaf(lp_mid, moi=MOI.AR).sub_code_points["CLN_UAF"] == -1.0


def test_uaf_recessive_het_no_trans_plp_is_zero() -> None:
    c = Case(age_matched_penetrance=NEAR, vbc_zygosity=Zygosity.HET)  # no compound_het_variant
    assert reference_score_cln_uaf(c, moi=MOI.AR).sub_code_points["CLN_UAF"] == 0.0


def test_uaf_penetrance_none_is_zero() -> None:
    c = Case(vbc_zygosity=Zygosity.HOM)  # penetrance None
    assert reference_score_cln_uaf(c, moi=MOI.AR).sub_code_points["CLN_UAF"] == 0.0


def test_uaf_nd_when_moi_or_zygosity_unknown() -> None:
    assert reference_score_cln_uaf(Case(age_matched_penetrance=NEAR), moi=None).sub_code_points == {}
    # recessive with unknown zygosity -> cannot pick a column
    rec = Case(age_matched_penetrance=NEAR)  # vbc_zygosity None
    r = reference_score_cln_uaf(rec, moi=MOI.AR)
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect ImportError.** `uv run pytest tests/test_cln_benign_scoring.py -q`

- [ ] **Step 3: Implement `scoring/hod/clinical.py`** (both functions; `_classify_plp` + `reference_score_cln_uaf` now, `reference_score_cln_alt` in Task 2 — but write the whole file):

```python
"""Reference (non-authoritative) scorers for Clinical Observations (SM 4, CLN codes).

The two benign per-Case codes: CLN_UAF (unaffected carrier, Table 5) and CLN_ALT (alternative
cause, Table 4). Scored per Case (one proband); the cross-proband sum, the CLN_CCS exclusivity
rule, and the CLN_AFF +1.0/proband ceiling live in the later case-aggregation increment.
"""

from __future__ import annotations

from svcv4_model.case import AgeMatchedPenetrance, Case, MOI, PhenoSeverity, Zygosity
from svcv4_model.scoring.result import ScoreResult

_RECESSIVE_XL = frozenset({MOI.AR, MOI.XLD, MOI.XLR})
_PEN_GT_80 = frozenset({AgeMatchedPenetrance.PCT_80_100, AgeMatchedPenetrance.NEAR_100})


def _classify_plp(classification: str | None) -> str | None:
    """Normalize the placeholder ``classification`` string to 'P' / 'LP' / None (else).

    ``AdditionalVariant``/``CompoundHetVariant`` carry ``classification`` as a placeholder str
    (not the ``VariantClassification`` enum -- a flagged model gap). Accepts the enum values
    (PATHOGENIC / LIKELY_PATHOGENIC) and the P / LP shorthands, case-insensitively.
    """
    if classification is None:
        return None
    c = classification.strip().upper()
    if c in {"P", "PATHOGENIC"}:
        return "P"
    if c in {"LP", "LIKELY_PATHOGENIC"}:
        return "LP"
    return None


def reference_score_cln_uaf(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_UAF benignity for one unaffected Case (SM 4
    Table 5). CSpec is authoritative. ``moi`` is required (picks the table column). Benignity-only.
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (cross-proband sum + CLN_CCS '
        "exclusivity deferred to case aggregation)."
    ]
    pen = case.age_matched_penetrance

    col: str | None = None
    if moi in {MOI.AD, MOI.SD}:
        col = "dom"
    elif moi in _RECESSIVE_XL:
        z = case.vbc_zygosity
        if z in {Zygosity.HOM, Zygosity.HEMI}:
            col = "rec_homo_hemi"
        elif z == Zygosity.HET:
            trans = _classify_plp(
                case.compound_het_variant.classification if case.compound_het_variant else None
            )
            col = {"P": "rec_trans_p", "LP": "rec_trans_lp"}.get(trans, "no_trans_plp")
        # z None -> col stays None -> _ND

    if col is None:
        prov.append("CLN_UAF: _ND (moi unknown, or recessive/XL VBC zygosity unknown)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    if col == "no_trans_plp":
        pts = 0.0
        prov.append("CLN_UAF: 0.0 (recessive/XL HET, no confirmed-trans P/LP -- SM 4 L203)")
    else:
        reduced = col == "rec_trans_lp"
        if pen == AgeMatchedPenetrance.NEAR_100:
            pts = -2.0 if reduced else -4.0
        elif pen == AgeMatchedPenetrance.PCT_80_100:
            pts = -1.0 if reduced else -2.0
        else:  # LT_80 or None -> SM 4 L203: unknown/low penetrance -> no points
            pts = 0.0
        prov.append(f"CLN_UAF: {pts} (col={col}, penetrance={pen})")

    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_UAF": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )


def reference_score_cln_alt(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_ALT benignity for one affected Case whose
    phenotype is explained by a P/LP alternate cause (SM 4 Table 4). CSpec is authoritative.
    ``moi`` accepted for signature parity with the other CLN scorers (not consumed). Benignity-only.
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (cross-proband sum deferred).'
    ]
    # _classify_plp returns truthy "P"/"LP" (or falsy None), so this keeps only P/LP alternates
    plp_alts = [v for v in case.additional_variants if _classify_plp(v.classification)]
    if not plp_alts:
        prov.append("CLN_ALT: _ND (no P/LP alternate-cause variant -- Table 4 gate)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    sev = case.pheno_severity
    if sev is None:
        prov.append("CLN_ALT: _ND (no pheno_severity)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    if sev == PhenoSeverity.MONO_GT_OR_BIALLELIC_EQ_EXPECTED:
        pts = 0.0
    elif sev == PhenoSeverity.MONO_EQ_EXPECTED:
        pts = -0.5
    else:  # BIALLELIC_LT_EXPECTED: -1.0 only if same-gene (ALTV) AND penetrance >80%
        same_gene = any(v.phase_in_ref_to_vbc is not None for v in plp_alts)
        pen_gt_80 = case.age_matched_penetrance in _PEN_GT_80
        pts = -1.0 if (same_gene and pen_gt_80) else 0.0
        prov.append(
            f"CLN_ALT BIALLELIC_LT_EXPECTED: same_gene={same_gene}, "
            f"penetrance>80%={pen_gt_80} (>80% = PCT_80_100/NEAR_100; SM 4 L198-200)"
        )
    prov.append(f"CLN_ALT: {pts} (pheno_severity={sev}; 'in expected zygosity' trusted to input)")

    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_ALT": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 4: Export** — `scoring/__init__.py`: add the import `from svcv4_model.scoring.hod.clinical import reference_score_cln_alt, reference_score_cln_uaf` at the TOP of the block (hod < pfd; `clinical` < `population`, so ABOVE the population line); add `"reference_score_cln_alt"` + `"reference_score_cln_uaf"` to `__all__` after `"reference_score_canonical_splice"`.

- [ ] **Step 5: Run** `uv run pytest tests/test_cln_benign_scoring.py -q` — the UAF tests PASS (ALT tests come in Task 2).

- [ ] **Step 6: Commit** — `git add -A && git commit -m "feat(scoring): add CLN_UAF scorer + _classify_plp (SM 4 Table 5)"`

---

## Task 2: `reference_score_cln_alt` tests

**Files:** `tests/test_cln_benign_scoring.py` (append)

- [ ] **Step 1: Append the failing tests**

```python
from svcv4_model.case import AdditionalVariant, Phase


def _alt(classification: str, *, same_gene: bool) -> AdditionalVariant:
    # same-gene (ALTV) is signalled by a captured phase_in_ref_to_vbc
    return AdditionalVariant(
        classification=classification,
        phase_in_ref_to_vbc=Phase.TRANS if same_gene else None,
    )


def test_alt_mono_severity_rows() -> None:
    for sev, expected in [
        (PhenoSeverity.MONO_GT_OR_BIALLELIC_EQ_EXPECTED, 0.0),
        (PhenoSeverity.MONO_EQ_EXPECTED, -0.5),
    ]:
        c = Case(pheno_severity=sev, additional_variants=[_alt("P", same_gene=False)])
        r = reference_score_cln_alt(c, moi=MOI.AD)
        assert r.parent_code == "CLN"
        assert r.sub_code_points["CLN_ALT"] == expected


def test_alt_biallelic_lt_same_gene_high_penetrance() -> None:
    c = Case(
        pheno_severity=PhenoSeverity.BIALLELIC_LT_EXPECTED,
        age_matched_penetrance=NEAR,
        additional_variants=[_alt("P", same_gene=True)],
    )
    assert reference_score_cln_alt(c, moi=MOI.AD).sub_code_points["CLN_ALT"] == -1.0


def test_alt_biallelic_lt_different_gene_is_zero() -> None:
    c = Case(
        pheno_severity=PhenoSeverity.BIALLELIC_LT_EXPECTED,
        age_matched_penetrance=NEAR,
        additional_variants=[_alt("P", same_gene=False)],  # ALTG -> -1.0 row N/A
    )
    assert reference_score_cln_alt(c, moi=MOI.AD).sub_code_points["CLN_ALT"] == 0.0


def test_alt_biallelic_lt_low_penetrance_is_zero() -> None:
    c = Case(
        pheno_severity=PhenoSeverity.BIALLELIC_LT_EXPECTED,
        age_matched_penetrance=LOW,
        additional_variants=[_alt("P", same_gene=True)],
    )
    assert reference_score_cln_alt(c, moi=MOI.AD).sub_code_points["CLN_ALT"] == 0.0


def test_alt_nd_without_plp_alternate() -> None:
    no_alt = Case(pheno_severity=PhenoSeverity.MONO_EQ_EXPECTED)
    vus_only = Case(
        pheno_severity=PhenoSeverity.MONO_EQ_EXPECTED,
        additional_variants=[_alt("VUS", same_gene=False)],
    )
    assert reference_score_cln_alt(no_alt, moi=MOI.AD).sub_code_points == {}
    assert reference_score_cln_alt(vus_only, moi=MOI.AD).sub_code_points == {}


def test_alt_nd_without_pheno_severity() -> None:
    c = Case(additional_variants=[_alt("P", same_gene=False)])  # pheno_severity None
    r = reference_score_cln_alt(c, moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_classify_plp_normalization() -> None:
    from svcv4_model.scoring.hod.clinical import _classify_plp

    assert _classify_plp("P") == "P"
    assert _classify_plp("pathogenic") == "P"
    assert _classify_plp("LP") == "LP"
    assert _classify_plp("Likely_Pathogenic") == "LP"
    assert _classify_plp("VUS") is None
    assert _classify_plp(None) is None
```

- [ ] **Step 2: Run** `uv run pytest tests/test_cln_benign_scoring.py -q` — all PASS (the impl from Task 1 already includes `reference_score_cln_alt`).

- [ ] **Step 3: Commit** — `git commit -am "feat(scoring): add CLN_ALT scorer (SM 4 Table 4)"`

---

## Task 3: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — after the Population bullet:

```markdown
- **Clinical Observations — benign codes** (SM 4) — `reference_score_cln_uaf` (Table 5) and
  `reference_score_cln_alt` (Table 4), the two benign per-`Case` CLN codes. Scored per proband
  (`parent_code="CLN"`); the cross-proband sum, the CLN_CCS exclusivity rule, and the CLN_AFF
  `+1.0`/proband ceiling are deferred to case aggregation. `moi` is required (picks the CLN_UAF
  column). Both normalize the placeholder variant `classification` via `_classify_plp` (see
  known-gaps). CLN_AFF / CLN_DNV / CLN_CCS and the LOC codes follow.
```

- [ ] **Step 2: Add a `known-gaps.md` Model-gap row** — in the "Model gaps" table:

```markdown
| Variant `classification` is a placeholder `str` | Case model | `AdditionalVariant.classification` and `CompoundHetVariant.classification` are free-text `str` (e.g. "P"/"LP"), not the `VariantClassification` enum. The CLN scorers normalize via `_classify_plp`; typing these fields as `VariantClassification` would remove the string handling. |
```

- [ ] **Step 3: Build strict** — `uv run mkdocs build --strict` (exit 0).
- [ ] **Step 4: Commit** — `git commit -am "docs: CLN benign scorers; log the placeholder-classification model gap"`

---

## Task 4: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`export_schemas.py` then `git diff --quiet -- schemas/json docs/workflows/case-model.md`); `mkdocs build --strict` (exit 0); no scorer schema leaked; clean tree.

---

## Notes for the implementer

- Two separate per-code functions (UAF unaffected / ALT affected are mutually exclusive per Case); each returns `parent_code="CLN"` + a single sub-code (or `{}` when `_ND`).
- `moi` is required on both for signature parity, but `reference_score_cln_alt` does not consume it (Table 4 has no MOI axis). Keep the parameter.
- `_classify_plp` is module-private (not exported from `scoring.__init__`), like POP's `_pop_hmz_weight`.
- Import placement: `scoring.hod.clinical` sorts before `scoring.hod.population` (c < p) and both before `scoring.pfd.*` (hod < pfd). Watch LL 100 on the `plp_alts` list comprehension and the provenance f-strings.
