# Reference Scorer — CLN_AFF biallelic (SM 4 Table 2) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_cln_aff_biallelic` (SM 4 Table 2) — completes CLN_AFF. Per-`Case`; `parent_code="CLN"`, single sub-code `CLN_AFF`. Reuses the merged `_classify`.

**Architecture:** Extends `scoring/hod/clinical.py` with a `_TABLE2` constant, a `_biallelic_column` helper, and the scorer. Non-authoritative; scoring out of root `__all__` (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Table 2 (spec-verified, 5 cols × 4 row-classes):** columns `conf_plp/assumed_plp/conf_vus/hom/none`; A1 `3.0/1.5/1.5/1.0/0.0`, A2 `2.0/1.0/1.0/1.0/0.0`, B `1.0/0.75/0.5/0.5/0.0`, zero all `0.0`.

---

## Task 1: `reference_score_cln_aff_biallelic` (TDD)

**Files:** Modify `src/svcv4_model/scoring/hod/clinical.py`, create `tests/test_cln_aff_biallelic_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_cln_aff_biallelic_scoring.py`

```python
"""Tests for reference_score_cln_aff_biallelic (SM 4 Table 2, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    Case,
    CaseTesting,
    CompoundHetVariant,
    CoOccurrenceLikelihood,
    PhaseConfidence,
    PhenoSpecificity,
    TriState,
    Zygosity,
)
from svcv4_model.scoring import reference_score_cln_aff_biallelic

CONS = PhenoSpecificity.CONSISTENT
INC = PhenoSpecificity.INCONSISTENT
LT = CoOccurrenceLikelihood.LT_0_0001
BETWEEN = CoOccurrenceLikelihood.BETWEEN_0_0001_0_01

_THOROUGH = CaseTesting(
    covers_all_genes_relevant_to_mde=TriState.TRUE,
    non_genetic_etiology_excluded=TriState.TRUE,
)


def _ch(classification: str, phase: PhaseConfidence | None, co: CoOccurrenceLikelihood | None):
    return CompoundHetVariant(
        classification=classification, phase_confidence=phase, co_occurrence_likelihood=co
    )


def _het(ch: CompoundHetVariant | None, *, pheno=CONS, testing=_THOROUGH, alts=None) -> Case:
    return Case(
        pheno_specificity_for_mde=pheno,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=ch,
        testing=testing,
        additional_variants=alts or [],
    )


def _score(case: Case) -> float | None:
    return reference_score_cln_aff_biallelic(case, moi=MOI.AR).sub_code_points.get("CLN_AFF")


def test_a1_row_lt_cooccurrence() -> None:
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT))) == 3.0  # conf_plp
    assert _score(_het(_ch("LP", PhaseConfidence.MED, LT))) == 1.5  # assumed_plp
    assert _score(_het(_ch("VUS", PhaseConfidence.HIGH, LT))) == 1.5  # conf_vus
    assert _score(_het(None)) == 0.0  # none (no compound-het)
    hom = Case(pheno_specificity_for_mde=CONS, vbc_zygosity=Zygosity.HOM, testing=_THOROUGH)
    assert reference_score_cln_aff_biallelic(hom, moi=MOI.AR).sub_code_points["CLN_AFF"] == 1.0


def test_a2_row_between_cooccurrence() -> None:
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, BETWEEN))) == 2.0  # conf_plp
    assert _score(_het(_ch("VUS", PhaseConfidence.HIGH, BETWEEN))) == 1.0  # conf_vus


def test_b_row_incomplete_testing() -> None:
    incomplete = CaseTesting(covers_all_genes_relevant_to_mde=TriState.FALSE)
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT), testing=incomplete)) == 1.0
    assert _score(_het(_ch("LP", PhaseConfidence.MED, LT), testing=incomplete)) == 0.75
    assert _score(_het(_ch("VUS", PhaseConfidence.HIGH, LT), testing=incomplete)) == 0.5


def test_b_row_vus_additional_forces_incomplete() -> None:
    vus_alt = [AdditionalVariant(classification="VUS")]
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT), alts=vus_alt)) == 1.0  # B, not A1


def test_b_row_cooccurrence_unassessed() -> None:
    # thorough het but no co-occurrence bucket -> rarity unestablished -> B
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, None))) == 1.0


def test_zero_plp_diff_gene_additional() -> None:
    plp_alt = [AdditionalVariant(classification="P")]
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT), alts=plp_alt)) == 0.0


def test_zero_inconsistent_phenotype() -> None:
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT), pheno=INC)) == 0.0


def test_assumed_vus_scores_none() -> None:
    # VUS not confirmed in trans -> 'none' column -> 0.0 (SM 4 L75)
    assert _score(_het(_ch("VUS", PhaseConfidence.MED, LT))) == 0.0


def test_hom_thorough_cooccurrence_na() -> None:
    hom = Case(pheno_specificity_for_mde=CONS, vbc_zygosity=Zygosity.HOM, testing=_THOROUGH)
    assert reference_score_cln_aff_biallelic(hom, moi=MOI.AR).sub_code_points["CLN_AFF"] == 1.0


def test_nd_when_pheno_or_zygosity_none() -> None:
    no_pheno = Case(vbc_zygosity=Zygosity.HOM)
    no_zyg = Case(pheno_specificity_for_mde=CONS)  # vbc_zygosity None
    assert reference_score_cln_aff_biallelic(no_pheno, moi=MOI.AR).sub_code_points == {}
    r = reference_score_cln_aff_biallelic(no_zyg, moi=MOI.AR)
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect ImportError.** `uv run pytest tests/test_cln_aff_biallelic_scoring.py -q`

- [ ] **Step 3: Implement** in `clinical.py`. Add `CoOccurrenceLikelihood, PhaseConfidence` to the `from svcv4_model.case import (...)` block (keep MOI first, then CamelCase alphabetical: `AgeMatchedPenetrance, Case, CoOccurrenceLikelihood, PhaseConfidence, PhenoSeverity, PhenoSpecificity, TriState, Zygosity`). Then add:

```python
_TABLE2 = {
    "A1": {"conf_plp": 3.0, "assumed_plp": 1.5, "conf_vus": 1.5, "hom": 1.0, "none": 0.0},
    "A2": {"conf_plp": 2.0, "assumed_plp": 1.0, "conf_vus": 1.0, "hom": 1.0, "none": 0.0},
    "B": {"conf_plp": 1.0, "assumed_plp": 0.75, "conf_vus": 0.5, "hom": 0.5, "none": 0.0},
    "zero": {"conf_plp": 0.0, "assumed_plp": 0.0, "conf_vus": 0.0, "hom": 0.0, "none": 0.0},
}


def _biallelic_column(case: Case) -> str | None:
    """SM 4 Table 2 column from the 2nd-variant status. None -> _ND (indeterminate zygosity)."""
    z = case.vbc_zygosity
    if z == Zygosity.HOM:
        return "hom"
    if z != Zygosity.HET:
        return None  # None or HEMI (hemizygous is Table 1, not biallelic) -> _ND
    ch = case.compound_het_variant
    if ch is None:
        return "none"  # no in-trans 2nd variant
    cls = _classify(ch.classification)
    if cls in {"P", "LP"}:
        # CompoundHetVariant asserts in-trans by construction; HIGH = confirmed, else assumed
        return "conf_plp" if ch.phase_confidence == PhaseConfidence.HIGH else "assumed_plp"
    if cls == "VUS":
        # only a confirmed-trans VUS scores; assumed-trans VUS = no points (SM 4 L75)
        return "conf_vus" if ch.phase_confidence == PhaseConfidence.HIGH else "none"
    return "none"


def reference_score_cln_aff_biallelic(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_AFF pathogenic points for one affected
    biallelic proband (SM 4 Table 2). CSpec is authoritative. ``moi`` accepted for signature
    parity (Table 2 has no MOI axis; table selection/routing is deferred to aggregation).
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (table selection + cross-proband '
        "sum + the AD ceiling-on-sum deferred to case aggregation)."
    ]
    pheno = case.pheno_specificity_for_mde
    if pheno is None:
        prov.append("CLN_AFF: _ND (no pheno_specificity_for_mde)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    col = _biallelic_column(case)
    if col is None:
        prov.append("CLN_AFF: _ND (VBC zygosity absent or hemizygous -- not a Table 2 column)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    cats = {_classify(v.classification) for v in case.additional_variants}
    if pheno == PhenoSpecificity.INCONSISTENT:
        row = "zero"
    elif cats & {"P", "LP"}:
        row = "zero"  # a P/LP alt cause -> CLN_ALT (SM 4 Table 2 row C)
    else:
        t = case.testing
        thorough = (
            t is not None
            and t.covers_all_genes_relevant_to_mde == TriState.TRUE
            and t.non_genetic_etiology_excluded == TriState.TRUE
            and "VUS" not in cats
        )
        if not thorough:
            row = "B"
        elif col == "hom":
            row = "A1"  # co-occurrence N/A for a homozygous variant (A1.hom == A2.hom)
        else:
            ch = case.compound_het_variant
            co = ch.co_occurrence_likelihood if ch else None
            if co == CoOccurrenceLikelihood.LT_0_0001:
                row = "A1"
            elif co == CoOccurrenceLikelihood.BETWEEN_0_0001_0_01:
                row = "A2"
            else:
                row = "B"  # rarity unestablished -> incomplete row

    pts = _TABLE2[row][col]
    prov.append(f"CLN_AFF: {pts} (biallelic Table 2, column={col}, row={row})")
    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_AFF": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 4: Export** — `scoring/__init__.py`: add `reference_score_cln_aff_biallelic` to the clinical import (alphabetical: `aff_biallelic` < `aff_mono` < `alt` < `uaf`) and to `__all__` after `reference_score_canonical_splice` (`cln_aff_biallelic` < `cln_aff_mono`).

- [ ] **Step 5: Run** `uv run pytest tests/test_cln_aff_biallelic_scoring.py -q` — all PASS.
- [ ] **Step 6: Commit** — `git commit -am "feat(scoring): add reference_score_cln_aff_biallelic (SM 4 Table 2)"`

---

## Task 2: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — update the CLN bullet: CLN_AFF is now **monoallelic + biallelic** (`reference_score_cln_aff_mono` Table 1, `reference_score_cln_aff_biallelic` Table 2 — the 5-column 2nd-variant status × co-occurrence-likelihood matrix). Keep the deferred-aggregation + `_classify` notes; CLN_DNV/CLN_CCS/LOC follow.

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (exit 0).
- [ ] **Step 3: Commit** — `git commit -am "docs: note the CLN_AFF biallelic scorer (Table 2)"`

---

## Task 3: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`export_schemas.py` then `git diff --quiet -- schemas/json docs/workflows/case-model.md`); `mkdocs build --strict` (exit 0); no scorer schema leaked; clean tree.

---

## Notes for the implementer

- Guard the co-occurrence lookup: `co = ch.co_occurrence_likelihood if ch else None` — the thorough non-`hom` branch can be reached with `compound_het_variant is None` (the `none` column), and a bare `.co_occurrence_likelihood` would `AttributeError`. (The resulting row is immaterial since `none` is `0.0` in every row, but never deref a `None` compound-het.)
- HEMI VBC → `_ND` (hemizygous is scored under Table 1, not Table 2).
- `moi` unused (intentional; ARG not in ruff select). `_TABLE2`/`_biallelic_column` module-private. Watch LL 100 on the `_TABLE2` rows and the provenance strings.
