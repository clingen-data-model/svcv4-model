# Reference Scorer — Missense splice path + take-higher (SM 6) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Complete the splice family: (1) `reference_score_missense_splice` (SM 6 SPL_ path — a `score_spl_workflow` branch table), (2) a `MissenseScoreResult` DTO, (3) `reference_score_missense` (the MIS_-vs-SPL_ take-higher).

**Architecture:** The splice scorer reuses the Inc-A `score_spl_workflow` unchanged (a new `SplBranchSpec` table). The comparison orchestrates the two sub-scorers (amino-acid — no GDV; splice — with GDV) and applies SM 6 L157. Non-authoritative; scoring stays out of root `__all__`; `MissenseScoreResult` is a frozen dataclass (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Key facts (spec-verified):** the SM 6 blue/violet parent caps are inverted vs SM 11/12 (blue −8..0, violet −8..+8) — encoded faithfully + flagged. The reachable violet max is **+7** (PRD −1 + FXN +8; SPA/INF ≤0), so `parent_hi=8` never binds. Take-higher treats a `None` total as not-positive.

---

## Task 1: `reference_score_missense_splice` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/missense_splice.py`, `tests/test_missense_splice_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_missense_splice_scoring.py`

```python
"""Tests for reference_score_missense_splice (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.missense import MissenseSpliceAssessment
from svcv4_model.scoring import reference_score_missense_splice
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


def test_yellow_maximal() -> None:
    a = MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(),
        spa_points=3.0,  # scales up: held PRD+SPA -> +6
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 4),  # +2+1+1+1 = +5 -> capped +8? (5)
    )
    r = reference_score_missense_splice(a, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.held_combined["PRD+SPA"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(6+8, +9)
    assert r.parent_total == 10.0  # cap(9+INF, +10)


def test_blue_parent_clamped_to_zero() -> None:
    # THE ODDITY (blue side): an uncertain variant's positive evidence is zeroed at the parent
    a = MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNCERTAIN,
        predictive=SplicePredictiveEvidence(initial_points=0.0),
        spa_points=2.0,
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 4),  # big +INF
    )
    r = reference_score_missense_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == 2.0  # cap(0+2, [-2, 2])
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(2+8, +9)
    assert r.parent_total == 0.0  # cap(9+INF, [-8, 0]) -> 0 (the oddity)


def test_violet_reaches_positive_seven() -> None:
    # THE ODDITY (violet side): an unlikely variant reaches +7 via FXN (max; parent_hi=8 never binds)
    a = MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNLIKELY,
        predictive=SplicePredictiveEvidence(initial_points=-1.0),
        fxn_points=8.0,
    )
    r = reference_score_missense_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA+FXN"] == 7.0  # cap(-1+8, +9)
    assert r.parent_total == 7.0  # cap(7, [-8, 8])


def test_violet_inf_benignity_only() -> None:
    a = MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNLIKELY,
        predictive=SplicePredictiveEvidence(initial_points=-1.0),
        informative=_inf(VariantClassification.PATHOGENIC, 1),  # +2 clamped to 0 by inf_hi=0
    )
    r = reference_score_missense_splice(a, gene_disease_validity=MOD)
    assert r.sub_code_points["INF"] == 0.0


def test_all_five_outcomes() -> None:
    for outcome in SplicePredictionOutcome:
        r = reference_score_missense_splice(
            MissenseSpliceAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code == "SPL"


def test_empty_is_all_nd() -> None:
    r = reference_score_missense_splice(MissenseSpliceAssessment(), gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.parent_total is None
```

Note on `test_yellow_maximal`: 4 P informative → informative_points = +2 (first P) + 1 + 1 + 1 = +5, cap(+5, [−8, +8]) = +5; parent = cap(9 + 5, [−8, +10]) = +10. ✓

- [ ] **Step 2: Run — expect ModuleNotFoundError.**

- [ ] **Step 3: Implement `scoring/pfd/missense_splice.py`**

```python
"""Reference (non-authoritative) scorer for the Missense splice path (SM 6, SPL_)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.missense import MissenseSpliceAssessment
from svcv4_model.scoring.pfd._spl_common import SplBranchSpec, score_spl_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.splice import SplicePredictionOutcome

# SPA scales the PRD *up* here, so orange carries an explicit 0..+6 first held cap.
_ORANGE = SplBranchSpec(-1.0, 3.0, prd_spa_lo=0.0, prd_spa_hi=6.0)

# NOTE: SM 6's blue/violet parent caps are INVERTED vs Canonical (SM 11) / Intronic (SM 12) --
# blue UNCERTAIN -> -8..0 and violet UNLIKELY -> -8..+8. This looks like a possible SM 6 typo
# but the merged missense.md encodes it, so it is reproduced faithfully and flagged in
# provenance (a suspected inconsistency to raise with the WG).
_BRANCH: dict[SplicePredictionOutcome, SplBranchSpec] = {
    SplicePredictionOutcome.NMD_PREDICTED: SplBranchSpec(0.0, 3.0, prd_spa_lo=0.0, prd_spa_hi=6.0),
    SplicePredictionOutcome.FRAMESHIFT_NO_NMD: _ORANGE,
    SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT: _ORANGE,
    SplicePredictionOutcome.UNCERTAIN: SplBranchSpec(
        0.0, 0.0, prd_spa_lo=-2.0, prd_spa_hi=2.0, parent_hi=0.0
    ),
    SplicePredictionOutcome.UNLIKELY: SplBranchSpec(
        -1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0, inf_hi=0.0, parent_hi=8.0
    ),
}

_ODDITY_NOTE = (
    "SM 6 blue/violet SPL_ parent caps are inverted vs SM 11/12 (blue -8..0, violet -8..+8); "
    "encoded as documented -- suspected SM 6 inconsistency, flagged for WG review."
)


def reference_score_missense_splice(
    assessment: MissenseSpliceAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Missense splice-path (SPL_) total (SM 6).

    CSpec is authoritative. ``gene_disease_validity`` is required (the splice PRD uses SM 18).
    SPA is consumed raw (it scales the PRD *up* here). The blue/violet parent caps are inverted
    versus the other splice workflows -- see ``_ODDITY_NOTE`` (faithful to SM 6, flagged).
    """
    result = score_spl_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
    result.provenance.append(_ODDITY_NOTE)
    return result
```

(`score_spl_workflow` returns a `ScoreResult` whose `provenance` list is mutable — appending the
note is safe; the dataclass is frozen against reassignment, not list mutation.)

- [ ] **Step 4: Export** — `scoring/__init__.py`: import + `"reference_score_missense_splice"` in `__all__`, sorted AFTER `reference_score_missense_amino_acid` (a<s), before `reference_score_nonsense`. (The `reference_score_missense` top-level fn is added in Task 3.)

- [ ] **Step 5: Run** `uv run pytest tests/test_missense_splice_scoring.py -q` — PASS.
- [ ] **Step 6: Commit** — `git commit -am "feat(scoring): add reference_score_missense_splice (SM 6 SPL_ path; blue/violet oddity flagged)"`

---

## Task 2: `MissenseScoreResult` DTO (TDD)

**Files:** Modify `src/svcv4_model/scoring/result.py`; `tests/test_scoring_result.py` (create if absent, else append)

- [ ] **Step 1: Write the failing test** — `tests/test_scoring_result.py`

```python
"""Tests for the reference-scorer result DTOs (non-authoritative)."""

from __future__ import annotations

import pytest

from svcv4_model.scoring.result import MissenseScoreResult, ScoreResult


def test_missense_score_result_holds_both_paths() -> None:
    mis = ScoreResult(parent_code="MIS", parent_total=5.0)
    spl = ScoreResult(parent_code="SPL", parent_total=3.0)
    r = MissenseScoreResult(
        amino_acid=mis,
        splice=spl,
        selected_path="AMINO_ACID",
        applied_parent_code="MIS",
        applied_total=5.0,
        provenance=["compared MIS_ 5.0 vs SPL_ 3.0 -> AMINO_ACID"],
    )
    assert r.amino_acid.parent_total == 5.0
    assert r.splice.parent_total == 3.0
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 5.0
    assert r.authoritative is False


def test_missense_score_result_authoritative_raises() -> None:
    mis = ScoreResult(parent_code="MIS")
    spl = ScoreResult(parent_code="SPL")
    with pytest.raises(ValueError, match="non-authoritative"):
        MissenseScoreResult(
            amino_acid=mis,
            splice=spl,
            selected_path="AMINO_ACID",
            applied_parent_code="MIS",
            applied_total=None,
            provenance=[],
            authoritative=True,
        )
```

- [ ] **Step 2: Run — expect ImportError.**

- [ ] **Step 3: Implement in `result.py`** — append after `ScoreResult`:

```python
@dataclass(frozen=True)
class MissenseScoreResult:
    """A reference (NON-AUTHORITATIVE) Missense result holding BOTH sub-path scores (SM 6).

    SM 6 requires saving both the amino-acid (``MIS_``) and splice (``SPL_``) path results so a
    future re-evaluation can reconsider the comparison. ``selected_path`` / ``applied_total`` /
    ``applied_parent_code`` record the take-higher outcome. ``authoritative`` is fixed False
    (constructing it True raises); CSpec is the authoritative scorer.
    """

    amino_acid: ScoreResult
    splice: ScoreResult
    selected_path: str
    applied_parent_code: str
    applied_total: float | None
    provenance: list[str] = field(default_factory=list)
    authoritative: bool = False

    def __post_init__(self) -> None:
        if self.authoritative:
            raise ValueError(
                "MissenseScoreResult is a reference (non-authoritative) computation; "
                "authoritative must be False -- CSpec is the authoritative scorer."
            )
```

- [ ] **Step 4: Run** `uv run pytest tests/test_scoring_result.py -q` — PASS.
- [ ] **Step 5: Commit** — `git commit -am "feat(scoring): add MissenseScoreResult DTO (saves both MIS_/SPL_ paths)"`

---

## Task 3: `reference_score_missense` take-higher (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/missense.py`, `tests/test_missense_compare_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_missense_compare_scoring.py`

```python
"""Tests for reference_score_missense (the MIS_-vs-SPL_ take-higher)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import VariantClassification
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissenseSpliceAssessment,
)
from svcv4_model.scoring import reference_score_missense
from svcv4_model.splice import SplicePredictionOutcome, SplicePredictiveEvidence

MOD = GeneDiseaseValidity.MODERATE


def _amino(prd: float) -> MissenseAminoAcidAssessment:
    # a positive MIS_PRD via a predictor score at All-transcript relevance
    return MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(
            initial_points=prd, transcript_relevance=ExonRelevance.ALL
        )
    )


def _splice_yellow(fxn: float) -> MissenseSpliceAssessment:
    return MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        fxn_points=fxn,
    )


def test_splice_higher_positive_selects_splice() -> None:
    a = MissenseAssessment(amino_acid=_amino(2.0), splice=_splice_yellow(8.0))
    r = reference_score_missense(a, gene_disease_validity=MOD)
    # amino MIS_ = 2; splice SPL_ = cap(3+8, +9)=9 -> parent 9 (> 2) -> SPLICE
    assert r.selected_path == "SPLICE"
    assert r.applied_parent_code == "SPL"
    assert r.applied_total == 9.0
    assert r.amino_acid.parent_total == 2.0  # both saved
    assert r.splice.parent_total == 9.0


def test_amino_higher_selects_amino() -> None:
    a = MissenseAssessment(amino_acid=_amino(4.0), splice=_splice_yellow(0.0))
    r = reference_score_missense(a, gene_disease_validity=MOD)
    # amino = 4; splice = cap(3+0, +9)=3 -> amino higher -> AMINO_ACID
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 4.0


def test_positive_tie_selects_amino() -> None:
    # amino = 3; splice yellow with fxn 0 -> 3 -> tie -> AMINO_ACID
    a = MissenseAssessment(amino_acid=_amino(3.0), splice=_splice_yellow(0.0))
    r = reference_score_missense(a, gene_disease_validity=MOD)
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 3.0


def test_negative_splice_selects_amino() -> None:
    a = MissenseAssessment(
        amino_acid=_amino(2.0),
        splice=MissenseSpliceAssessment(
            prediction_outcome=SplicePredictionOutcome.UNLIKELY,
            predictive=SplicePredictiveEvidence(initial_points=-1.0),
        ),
    )
    r = reference_score_missense(a, gene_disease_validity=MOD)
    # splice violet -> parent -1 (negative) -> AMINO_ACID
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 2.0


def test_missing_splice_uses_amino() -> None:
    a = MissenseAssessment(amino_acid=_amino(2.0))  # splice None -> empty -> total None
    r = reference_score_missense(a, gene_disease_validity=MOD)
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 2.0


def test_missing_amino_positive_splice_uses_splice() -> None:
    a = MissenseAssessment(splice=_splice_yellow(8.0))  # amino None -> total None; splice 9
    r = reference_score_missense(a, gene_disease_validity=MOD)
    assert r.selected_path == "SPLICE"
    assert r.applied_total == 9.0


def test_both_empty_uses_amino_none_total() -> None:
    r = reference_score_missense(MissenseAssessment(), gene_disease_validity=MOD)
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_parent_code == "MIS"
    assert r.applied_total is None
```

- [ ] **Step 2: Run — expect ImportError.**

- [ ] **Step 3: Implement `scoring/pfd/missense.py`**

```python
"""Reference (non-authoritative) Missense take-higher: MIS_ amino-acid vs SPL_ splice (SM 6)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseAssessment,
    MissenseSpliceAssessment,
)
from svcv4_model.scoring.pfd.missense_amino_acid import reference_score_missense_amino_acid
from svcv4_model.scoring.pfd.missense_splice import reference_score_missense_splice
from svcv4_model.scoring.result import MissenseScoreResult


def reference_score_missense(
    assessment: MissenseAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> MissenseScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Missense result via the SM 6 take-higher.

    CSpec is authoritative. Scores BOTH the amino-acid (MIS_, no GDV) and splice (SPL_, with GDV)
    paths and applies SM 6 L157: a negative/absent splice total -> the amino-acid path; a positive
    splice total -> the higher of the two; a positive tie -> the amino-acid path (higher prior for
    the amino-acid effect). A None total counts as not-positive (an empty path never wins).
    """
    amino = reference_score_missense_amino_acid(
        assessment.amino_acid or MissenseAminoAcidAssessment()
    )
    splice = reference_score_missense_splice(
        assessment.splice or MissenseSpliceAssessment(), gene_disease_validity=gene_disease_validity
    )
    mis, spl = amino.parent_total, splice.parent_total

    if spl is None or spl <= 0 or (mis is not None and spl <= mis):
        selected, code, applied = "AMINO_ACID", "MIS", mis
    else:
        selected, code, applied = "SPLICE", "SPL", spl

    prov = [
        f"compared MIS_ {mis} vs SPL_ {spl} -> {selected} "
        f"(SM 6 take-higher: negative/absent splice or a positive tie -> amino-acid)"
    ]
    return MissenseScoreResult(
        amino_acid=amino,
        splice=splice,
        selected_path=selected,
        applied_parent_code=code,
        applied_total=applied,
        provenance=prov,
    )
```

Note: the single combined condition `spl is None or spl <= 0 or (mis is not None and spl <= mis)` is the AMINO_ACID branch — it collapses the spec's three cases (absent/non-positive splice; positive tie or amino-higher). The SPLICE branch is the `else` (splice positive AND (amino absent OR splice strictly higher)).

- [ ] **Step 4: Export** — `scoring/__init__.py`: add `MissenseScoreResult` (import from `.result`; in `__all__` before `ScoreResult`) + `reference_score_missense` (import from `.pfd.missense`; in `__all__` before `reference_score_missense_amino_acid`).

- [ ] **Step 5: Run** `uv run pytest tests/test_missense_compare_scoring.py -q` — all PASS.
- [ ] **Step 6: Commit** — `git commit -am "feat(scoring): add reference_score_missense MIS_-vs-SPL_ take-higher (SM 6)"`

---

## Task 4: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — after the Missense amino-acid bullet:

```markdown
- **Missense — splice path + comparison** (SM 6) — `reference_score_missense_splice` (a
  `score_spl_workflow` branch table) and `reference_score_missense`, the `MIS_`-vs-`SPL_`
  **take-higher** (negative/absent splice or a positive tie → the amino-acid path; else the
  higher), returning a `MissenseScoreResult` that saves both sub-path scores. **Note:** SM 6's
  splice blue/violet parent caps are inverted vs SM 11/12 (blue `−8..0`, violet `−8..+8`) —
  encoded faithfully and flagged as a suspected SM 6 inconsistency. This completes the splice
  family (Canonical, Intronic, Missense).
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (exit 0).
- [ ] **Step 3: Commit** — `git commit -am "docs: note the Missense splice path + take-higher (completes the splice family)"`

---

## Task 5: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`export_schemas.py` then `git diff --quiet -- schemas/json docs/workflows/case-model.md` — `MissenseScoreResult` is a dataclass, no schema); `mkdocs build --strict` (exit 0); no scorer schema leaked; clean tree.

---

## Notes for the implementer

- The splice scorer wraps `score_spl_workflow` and **appends** the `_ODDITY_NOTE` to the returned `provenance` list (safe — frozen guards reassignment, not list mutation).
- `reference_score_missense` forwards `gene_disease_validity` ONLY to the splice sub-scorer (the amino-acid scorer takes none).
- The `_BRANCH` dict line for `NMD_PREDICTED` and `UNCERTAIN` may exceed LL 100 — wrap the `UNCERTAIN` `SplBranchSpec(...)` across lines if ruff flags it (as the `UNLIKELY` entry is already wrapped).
- Watch LL 100 on the test constructor lines and the `reference_score_missense_amino_acid(assessment.amino_acid or ...)` line — wrap if needed.
- `MissenseScoreResult` is a frozen dataclass, NOT Pydantic — it must not appear in `schemas/json`.
