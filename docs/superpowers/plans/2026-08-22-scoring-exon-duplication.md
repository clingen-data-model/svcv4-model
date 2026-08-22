# Reference Scorer — Exon Duplication (SM 14) + FXN-NA + whole-gene-NA — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `BranchSpec.fxn_na` (gain paths skip FXN) + the helper change, then add `reference_score_exon_duplication` (SM 14, six scored branches + a WHOLE_GENE_NA wrapper short-circuit). Finishes the NUL_/CDS_ scorer family.

**Architecture:** `fxn_na=True` → helper records `FXN: NA`, carries PRD forward (`held_val=prd`), records no `held_combined`. WHOLE_GENE_NA is handled in the scorer wrapper (all-NA `ScoreResult`), not the branch table. Behaviour-preserving for the five existing scorers (`fxn_na` defaults False; the `else` path is today's logic verbatim). Non-authoritative.

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Confirmed:** `ExonDuplicationOutcome.{TANDEM_NMD,TANDEM_NO_NMD,TANDEM_TERMINAL_EXON,GAIN_NMD,GAIN_NO_NMD,GAIN_TERMINAL_EXON,WHOLE_GENE_NA}`; `ExonDuplicationAssessment` satisfies `NulCdsAssessment`.

---

## Task 1: `fxn_na` (BranchSpec + helper)

**Files:** Modify `src/svcv4_model/scoring/pfd/_common.py`
**Guards (unchanged):** all five existing scoring test files.

- [ ] **Step 1: Add `fxn_na` to `BranchSpec`** — after `sm18_mechanism_only`:

```python
    sm18_mechanism_only: bool = False
    fxn_na: bool = False
```

- [ ] **Step 2: Replace the helper's FXN + held block** with the `fxn_na` branch. The `else`
clause is TODAY'S logic VERBATIM (including the `held PRD+FXN` provenance line):

```python
    # FXN (consumed raw on non-NA branches; skipped as NA on the gain paths)
    if branch is not None and branch.fxn_na:
        prov.append("FXN: NA (functional not considered on this gain path)")
        held_val = prd  # no PRD+FXN combine when FXN is NA
    else:
        fxn = assessment.fxn_points
        if fxn is None:
            prov.append("FXN: _ND (no coded fxn_points captured; OddsPath not recomputed)")
        else:
            sub["FXN"] = fxn
            prov.append(f"FXN: consumed coded value {fxn}")
        held_hi = branch.held_hi if branch else _DEFAULT_HELD_HI
        held_val = hold_combined(prd, fxn, lo=_HELD_LO, hi=held_hi)
        if held_val is not None:
            held["PRD+FXN"] = held_val
            prov.append(f"held PRD+FXN: {held_val} (cap [{_HELD_LO}, {held_hi}])")
```

(The INF and parent-total steps that follow are unchanged — they already read `held_val`.)

- [ ] **Step 3: Run the regression guards**

Run: `uv run pytest tests/test_scoring_primitives.py tests/test_nonsense_scoring.py tests/test_frameshift_scoring.py tests/test_start_lost_scoring.py tests/test_stop_lost_scoring.py tests/test_exon_deletion_scoring.py -q`
Expected: all PASS unchanged (fxn_na defaults False → the else path runs today's exact logic + provenance).

- [ ] **Step 4: Commit**

```bash
git add src/svcv4_model/scoring/pfd/_common.py
git commit -m "feat(scoring): add BranchSpec.fxn_na (gain paths skip the FXN step)"
```

---

## Task 2: `reference_score_exon_duplication` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/exon_duplication.py`, `tests/test_exon_duplication_scoring.py`; modify `scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_exon_duplication_scoring.py`

```python
"""Tests for reference_score_exon_duplication (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.exon_duplication import (
    ExonDuplicationAssessment,
    ExonDuplicationOutcome,
    ExonDuplicationPredictiveEvidence,
)
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_exon_duplication

MOD = GeneDiseaseValidity.MODERATE
B = VariantClassification.BENIGN
P = VariantClassification.PATHOGENIC


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def _inf(cls: VariantClassification, n: int) -> InformativeVariantsEvidence:
    return InformativeVariantsEvidence(
        variants=[InformativeVariant(id=f"v{i}", classification=cls) for i in range(n)]
    )


def test_tandem_yellow_maximal() -> None:
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.TANDEM_NMD,
        parent_code=PfdParentCode.NUL,
        predictive=ExonDuplicationPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.sub_code_points["FXN"] == 8.0
    assert r.held_combined["PRD+FXN"] == 10.0  # 6+8 capped at +10


def test_upper_orange_held_9() -> None:
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.TANDEM_NO_NMD,
        predictive=ExonDuplicationPredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 3.0
    assert r.held_combined["PRD+FXN"] == 9.0  # 3+8 capped at +9


def test_gain_blue_fxn_is_na() -> None:
    # blue GAIN_NMD: FXN is NA -> fxn_points=8.0 is IGNORED; parent floors at -1 (PRD suppressed)
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.GAIN_NMD,
        fxn_points=8.0,          # must be ignored
        informative=_inf(B, 1),  # one benign -> INF -2.0
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert "FXN" not in r.sub_code_points        # FXN NA, not consumed
    assert "PRD+FXN" not in r.held_combined      # no held combine on a gain path
    assert r.sub_code_points["INF"] == -2.0
    assert r.parent_total == -1.0                # cap(-2, [-1, 6]) -> -1.0 (proves parent_lo=-1)


def test_gain_blue_inf_ceiling_6() -> None:
    # blue: PRD +4 (Established x All) + a big positive INF -> parent clamps to +6
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.GAIN_NMD,
        predictive=ExonDuplicationPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        informative=_inf(P, 6),  # +2 first P + 5x+1 = +7 -> capped to +6 by inf_hi=6
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.sub_code_points["PRD"] == 4.0
    assert r.sub_code_points["INF"] == 6.0        # +7 tally clamped by inf_hi=6
    assert r.parent_total == 6.0                  # cap(4+6, [-1, 6]) -> 6.0


def test_gain_green_benignity_only() -> None:
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.GAIN_TERMINAL_EXON,
        informative=_inf(P, 1),  # a P tally +2 clamped to 0 by inf_hi=0
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert "FXN" not in r.sub_code_points
    assert r.sub_code_points["INF"] == 0.0
    assert r.parent_total == 0.0


def test_whole_gene_na() -> None:
    a = ExonDuplicationAssessment(prediction_outcome=ExonDuplicationOutcome.WHOLE_GENE_NA)
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.parent_total is None
    assert r.sub_code_points == {}
    assert any("NA" in p for p in r.provenance)


def test_all_seven_outcomes_score_without_error() -> None:
    for outcome in ExonDuplicationOutcome:
        r = reference_score_exon_duplication(
            ExonDuplicationAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code in {"NUL", "CDS"}


def test_empty_is_all_nd() -> None:
    r = reference_score_exon_duplication(ExonDuplicationAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect failure.**

- [ ] **Step 3: Implement `scoring/pfd/exon_duplication.py`**

```python
"""Reference (non-authoritative) scorer for the Exon Duplication/Gain workflow (SM 14)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.exon_duplication import ExonDuplicationAssessment, ExonDuplicationOutcome
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult

_BRANCH: dict[ExonDuplicationOutcome, BranchSpec] = {
    # tandem paths consume FXN (SM 20)
    ExonDuplicationOutcome.TANDEM_NMD: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    ExonDuplicationOutcome.TANDEM_NO_NMD: BranchSpec("CDS", 0.0, 3.0, held_hi=9.0),
    ExonDuplicationOutcome.TANDEM_TERMINAL_EXON: BranchSpec("CDS", 0.0, 0.0, held_hi=9.0),
    # gain paths: FXN is NA (not considered)
    ExonDuplicationOutcome.GAIN_NMD: BranchSpec(
        "NUL", 0.0, 4.0, fxn_na=True, parent_lo=-1.0, parent_hi=6.0, inf_hi=6.0
    ),
    ExonDuplicationOutcome.GAIN_NO_NMD: BranchSpec(
        "CDS", 0.0, 2.0, fxn_na=True, parent_lo=-1.0, parent_hi=6.0, inf_hi=6.0
    ),
    ExonDuplicationOutcome.GAIN_TERMINAL_EXON: BranchSpec(
        "CDS", 0.0, 0.0, fxn_na=True, parent_hi=0.0, inf_hi=0.0
    ),
    # WHOLE_GENE_NA handled in the wrapper (all NA)
}


def reference_score_exon_duplication(
    assessment: ExonDuplicationAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Exon Duplication/Gain point total (SM 14).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). The gain paths code functional data as NA (FXN
    skipped); whole-gene duplication is CDS_NA (all steps not applicable).
    """
    if assessment.prediction_outcome == ExonDuplicationOutcome.WHOLE_GENE_NA:
        return ScoreResult(
            parent_code="CDS",
            parent_total=None,
            provenance=["WHOLE_GENE_NA: CDS_NA (evaluated, determined not applicable)"],
            authoritative=False,
        )
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
```

- [ ] **Step 4: Add the export** — `scoring/__init__.py`: add the import + `"reference_score_exon_duplication"` into `__all__`, sorted (`exon_deletion` < `exon_duplication` < `frameshift`):

```python
from svcv4_model.scoring.pfd.exon_deletion import reference_score_exon_deletion
from svcv4_model.scoring.pfd.exon_duplication import reference_score_exon_duplication
from svcv4_model.scoring.pfd.frameshift import reference_score_frameshift
...
__all__ = [
    "ScoreResult",
    "reference_score_exon_deletion",
    "reference_score_exon_duplication",
    "reference_score_frameshift",
    "reference_score_nonsense",
    "reference_score_start_lost",
    "reference_score_stop_lost",
]
```

- [ ] **Step 5: Run** `uv run pytest tests/test_exon_duplication_scoring.py -q` — all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/pfd/exon_duplication.py tests/test_exon_duplication_scoring.py src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_score_exon_duplication (SM 14, FXN-NA gain paths + whole-gene NA)"
```

---

## Task 3: Docs

**Files:** Modify `docs/reference/scoring.md`

- [ ] **Step 1: Extend the list** — after the Exon Deletion line, add:

```markdown
- **Exon Duplication** (SM 14) — `reference_score_exon_duplication`, six scored branches + a
  whole-gene-NA outcome (the gain paths code functional data as NA; the shared helper skips
  FXN on those branches via `BranchSpec.fxn_na`). **All six NUL_/CDS_ scorers are now modeled.**
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (0 warnings).

- [ ] **Step 3: Commit** — `git commit -am "docs: note the Exon Duplication reference scorer (NUL_/CDS_ family complete)"`

---

## Task 4: Full quality gates

- [ ] **Step 1:** `uv run pytest -q`; `uv run ruff check .`; drift gate; `mkdocs build --strict`; `uv run python scripts/export_schemas.py && git status --porcelain schemas/json` (empty); `git status --porcelain`. All clean except pre-existing untracked files.
- [ ] **Step 2:** Ready for code review + PR.

---

## Notes for the implementer

- Task 1 is behaviour-preserving — the `else` clause is TODAY'S FXN+held block VERBATIM, including the `held PRD+FXN` provenance line. Do not drop that line. The five existing scoring test files are the guard.
- `WHOLE_GENE_NA` is NOT in `_BRANCH` — the wrapper short-circuits it (parent_code "CDS", all NA).
- Blue `GAIN_NMD` is `NUL_` but parent −1..+6 (not −8..+10) — the trap; the BranchSpec `parent_lo=-1, parent_hi=6` encodes it.
- Do NOT add scoring to the root `__all__` (schema). Line length 100.
