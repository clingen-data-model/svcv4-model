# Reference Scorer — Intronic & Synonymous (SM 12) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_intronic_synonymous` (SM 12, five paths) — a new `_BRANCH` table on the existing, tested `score_spl_workflow` + `SplBranchSpec` (Inc A). No helper changes.

**Architecture:** `IntronicSynonymousAssessment` is field-identical to `CanonicalSpliceAssessment`, so the scorer is a branch table + a one-line delegation, mirroring `pfd/canonical_splice.py`. Non-authoritative; SPA/FXN consumed raw; scoring stays out of root `__all__` (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Deltas from Canonical (the fidelity points — all confirmed in spec-review):** PRD tops at +3 (not +6); orange has an explicit held `prd_spa −1..+6`; blue's second held `prd_spa_fxn` is +9 (the default — NOT canonical's +8).

---

## Task 1: `reference_score_intronic_synonymous` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/intronic_synonymous.py`, `tests/test_intronic_synonymous_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_intronic_synonymous_scoring.py`

```python
"""Tests for reference_score_intronic_synonymous (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.intronic_synonymous import IntronicSynonymousAssessment
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.scoring import reference_score_intronic_synonymous
from svcv4_model.splice import SplicePredictionOutcome, SplicePredictiveEvidence

MOD = GeneDiseaseValidity.MODERATE


def _mer() -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(
        gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
    )


def _inf(cls: VariantClassification, n: int) -> InformativeVariantsEvidence:
    return InformativeVariantsEvidence(
        variants=[InformativeVariant(id=f"v{i}", classification=cls) for i in range(n)]
    )


def test_yellow_maximal_prd_3() -> None:
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(),
        spa_points=3.0,  # near-complete doubles +3 -> +3 delta
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.sub_code_points["PRD"] == 3.0
    assert r.held_combined["PRD+SPA"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(6+8, +9)
    assert r.parent_total == 10.0  # cap(9+2, +10)


def test_orange_held_prd_spa_cap_6() -> None:
    # explicit orange first-held -1..+6 (distinct from canonical's default)
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.FRAMESHIFT_NO_NMD,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(),
        spa_points=5.0,
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == 6.0  # cap(3+5, [-1, 6])


def test_blue_second_held_9() -> None:
    # THE SM12-vs-SM11 difference: blue second held caps at +9 (canonical was +8)
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.UNCERTAIN,
        predictive=SplicePredictiveEvidence(initial_points=0.0),
        spa_points=2.0,
        fxn_points=8.0,
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(2+8, +9) -- not +8
    assert r.parent_total == 8.0  # parent clamps to +8


def test_lilac_benignity() -> None:
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.UNLIKELY,
        predictive=SplicePredictiveEvidence(initial_points=-1.0),
        spa_points=-2.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),  # +2 clamped to 0
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == -3.0  # cap(-3, [-3, 0])
    assert r.sub_code_points["INF"] == 0.0
    assert r.parent_total == -3.0


def test_orange_prd_floor() -> None:
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT,
        predictive=SplicePredictiveEvidence(initial_points=-5.0),
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.sub_code_points["PRD"] == -1.0  # cap(-5, [-1, 3])


def test_spa_nd() -> None:
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(),
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert "SPA" not in r.sub_code_points
    assert r.held_combined["PRD+SPA"] == 3.0


def test_all_five_outcomes() -> None:
    for outcome in SplicePredictionOutcome:
        r = reference_score_intronic_synonymous(
            IntronicSynonymousAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code == "SPL"


def test_empty_is_all_nd() -> None:
    r = reference_score_intronic_synonymous(
        IntronicSynonymousAssessment(), gene_disease_validity=MOD
    )
    assert r.parent_code == "SPL"
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect ModuleNotFoundError.** `uv run pytest tests/test_intronic_synonymous_scoring.py -q`

- [ ] **Step 3: Implement `scoring/pfd/intronic_synonymous.py`**

```python
"""Reference (non-authoritative) scorer for the Intronic & Synonymous workflow (SM 12)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.intronic_synonymous import IntronicSynonymousAssessment
from svcv4_model.scoring.pfd._spl_common import SplBranchSpec, score_spl_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.splice import SplicePredictionOutcome

# SPA scales the PRD *up* here, so orange carries an explicit -1..+6 first held cap.
_ORANGE = SplBranchSpec(-1.0, 3.0, prd_spa_lo=-1.0, prd_spa_hi=6.0)

_BRANCH: dict[SplicePredictionOutcome, SplBranchSpec] = {
    SplicePredictionOutcome.NMD_PREDICTED: SplBranchSpec(0.0, 3.0),
    SplicePredictionOutcome.FRAMESHIFT_NO_NMD: _ORANGE,
    SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT: _ORANGE,
    SplicePredictionOutcome.UNCERTAIN: SplBranchSpec(0.0, 0.0, parent_hi=8.0),
    SplicePredictionOutcome.UNLIKELY: SplBranchSpec(
        -1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0, prd_spa_fxn_hi=0.0, inf_hi=0.0, parent_hi=0.0
    ),
}


def reference_score_intronic_synonymous(
    assessment: IntronicSynonymousAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Intronic & Synonymous total (SM 12, five paths).

    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). Field-identical to Canonical Splice but with a lower
    +3 PRD ceiling, an explicit orange held ``prd_spa`` cap (SPA scales the PRD up here), and a
    +9 blue second-held cap. SPA is consumed raw. The lilac (UNLIKELY) path is benignity-only.
    """
    return score_spl_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
```

Note: the two orange `SplBranchSpec(...)` lines are ~99 cols — under LL 100, but if ruff flags E501, wrap the keyword args onto a continuation line as the lilac entry does.

- [ ] **Step 4: Add the export** — `scoring/__init__.py`: add the import (alphabetical, after `frameshift`) + `"reference_score_intronic_synonymous"` into `__all__` (after `reference_score_frameshift`, before `reference_score_nonsense`).

- [ ] **Step 5: Run** `uv run pytest tests/test_intronic_synonymous_scoring.py -q` — all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/pfd/intronic_synonymous.py tests/test_intronic_synonymous_scoring.py src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_score_intronic_synonymous (SM 12, 5 paths)"
```

---

## Task 2: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — after the Canonical Splice bullet, add:

```markdown
- **Intronic & Synonymous** (SM 12) — `reference_score_intronic_synonymous`, five paths (the
  same `score_spl_workflow`, a new `SplBranchSpec` table). Field-identical to Canonical Splice;
  the point values differ — PRD tops at +3, the orange paths carry an explicit held `PRD+SPA`
  cap (`−1..+6`, since SPA scales the PRD *up* here), and blue's second held caps at +9.
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (0 warnings).

- [ ] **Step 3: Commit** — `git commit -am "docs: note the Intronic & Synonymous reference scorer"`

---

## Task 3: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`git diff --quiet -- schemas/json docs/workflows/case-model.md` after `export_schemas.py`); `mkdocs build --strict`; no scorer schema leaked; clean tree (except pre-existing untracked).

---

## Notes for the implementer

- No changes to `_spl_common.py` or `canonical_splice.py`. The helper + Canonical scorer tests must stay green.
- Blue relies on the **default** `prd_spa_fxn_hi=9` (do NOT override to 8 — that is canonical's value; SM 12 blue is +9).
- SPA is consumed raw (the coded delta) — here it *scales the PRD up* (analyst codes the positive delta), unlike canonical where it reduces; the scorer just sums, unchanged.
- Scoring is NOT in the root `__all__` (no schema). Line length 100.
