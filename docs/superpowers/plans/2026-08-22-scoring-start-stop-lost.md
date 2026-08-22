# Reference Scorer — Start-Lost + Stop-Lost + BranchSpec — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Generalize the shared helper's branch descriptor from a tuple to a `BranchSpec` dataclass (per-branch parent + INF caps), refactor Nonsense/Frameshift to it (behaviour-preserving), and add `reference_score_start_lost` (SM 15, 3 branches) + `reference_score_stop_lost` (SM 16, 2 branches).

**Architecture:** `BranchSpec` carries `parent_code, prd_lo, prd_hi, held_hi, parent_lo, parent_hi, inf_lo, inf_hi` with defaults = today's shared constants; the helper reads caps from the spec (falling back to the constants when the outcome is unknown). Non-authoritative; CSpec authoritative. FXN consumed raw (unchanged).

**Tech Stack:** Python 3.11+, stdlib dataclasses, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Confirmed:** `StartLostOutcome.{NO_ALT_START,ALT_START_UNPROVEN,ALT_START_FUNCTIONAL}`; `StopLostOutcome.{NSD_PREDICTED,NO_NSD}`; both assessments satisfy the `NulCdsAssessment` Protocol.

---

## Task 1: `BranchSpec` + generalize helper + refactor Nonsense/Frameshift (behaviour-preserving)

**Files:** Modify `src/svcv4_model/scoring/pfd/_common.py`, `.../nonsense.py`, `.../frameshift.py`
**Guards (unchanged):** `tests/test_nonsense_scoring.py`, `tests/test_frameshift_scoring.py`

- [ ] **Step 1: Add `BranchSpec` + generalize `score_nul_cds_workflow`** in `_common.py`.

Add the dataclass import and the `BranchSpec` (place the shared-constant definitions BEFORE it so the defaults reference them):

```python
from dataclasses import dataclass
```

Replace the current constants block + helper signature/body caps. The constants stay (they are the unknown-branch fallback and the BranchSpec defaults):

```python
_PARENT_LO, _PARENT_HI = -8.0, 10.0
_INF_LO, _INF_HI = -8.0, 8.0
_HELD_LO = -8.0
_DEFAULT_HELD_HI = 9.0


@dataclass(frozen=True)
class BranchSpec:
    """Per-branch caps for a NUL_/CDS_ workflow. Defaults match the shared constants; a
    workflow overrides only where SM says its branch differs (e.g. Start-Lost's -4 parent
    floor, or a benignity-only INF ceiling)."""

    parent_code: str
    prd_lo: float
    prd_hi: float
    held_hi: float = _DEFAULT_HELD_HI
    parent_lo: float = _PARENT_LO
    parent_hi: float = _PARENT_HI
    inf_lo: float = _INF_LO
    inf_hi: float = _INF_HI
```

Change the helper signature `branch_table: Mapping[object, BranchSpec]` and update the body to read from the `BranchSpec` (only the changed lines shown; everything else is unchanged):

```python
    outcome = assessment.prediction_outcome
    branch = branch_table.get(outcome) if outcome is not None else None
    parent_code = branch.parent_code if branch else None
    ...
        adj = apply_sm18_multiplier(initial, mech, exon, gene_disease_validity)
        prd = cap(adj, branch.prd_lo, branch.prd_hi)      # was branch[1], branch[2]
        sub["PRD"] = prd
        prov.append(
            f"PRD: initial {initial} x SM18(mech={mech}, exon={exon}, "
            f"gdv={gene_disease_validity}) = {adj}, capped "
            f"[{branch.prd_lo}, {branch.prd_hi}] -> {prd}"   # was branch[1], branch[2]
        )
    ...
    held_hi = branch.held_hi if branch else _DEFAULT_HELD_HI   # was branch[3]
    held_val = hold_combined(prd, fxn, lo=_HELD_LO, hi=held_hi)
    ...
    inf_lo = branch.inf_lo if branch else _INF_LO
    inf_hi = branch.inf_hi if branch else _INF_HI
    if assessment.informative is not None:
        inf = cap(informative_points(assessment.informative.variants), inf_lo, inf_hi)
    ...
    parent_lo = branch.parent_lo if branch else _PARENT_LO
    parent_hi = branch.parent_hi if branch else _PARENT_HI
    parent_total = hold_combined(held_val, inf, lo=parent_lo, hi=parent_hi)
    if parent_total is not None:
        prov.append(f"parent_total: {parent_total} (cap [{parent_lo}, {parent_hi}])")
```

(The PRD provenance f-string **must also change `branch[1]`/`branch[2]` → `branch.prd_lo`/
`branch.prd_hi`** — `BranchSpec` is not subscriptable, so leaving the old `branch[1]` there
crashes with `TypeError` on every scored-PRD test. The `NulCdsAssessment` Protocol, the FXN/INF
provenance strings, and the captured-parent_code cross-check are otherwise unchanged.)

- [ ] **Step 2: Refactor `nonsense.py`** — branch table becomes `BranchSpec` (behaviour identical):

```python
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow

_BRANCH: dict[NonsensePredictionOutcome, BranchSpec] = {
    NonsensePredictionOutcome.NMD_NO_RESCUE: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    NonsensePredictionOutcome.NMD_WITH_RESCUE: BranchSpec("CDS", -1.0, 6.0, held_hi=9.0),
    NonsensePredictionOutcome.NO_NMD: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
}
```

(The `reference_score_nonsense` function body is unchanged — still delegates.)

- [ ] **Step 3: Refactor `frameshift.py`** — likewise:

```python
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow

_BRANCH: dict[FrameshiftPredictionOutcome, BranchSpec] = {
    FrameshiftPredictionOutcome.NMD_NO_RESCUE: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    FrameshiftPredictionOutcome.NMD_WITH_RESCUE: BranchSpec("CDS", -1.0, 6.0, held_hi=9.0),
    FrameshiftPredictionOutcome.NO_NMD: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
    FrameshiftPredictionOutcome.NON_STOP_DECAY: BranchSpec("NUL", 0.0, 4.0, held_hi=9.0),
    FrameshiftPredictionOutcome.PROTEIN_EXTENSION: BranchSpec("CDS", 0.0, 4.0, held_hi=9.0),
}
```

- [ ] **Step 4: Run the regression guards**

Run: `uv run pytest tests/test_nonsense_scoring.py tests/test_frameshift_scoring.py tests/test_scoring_primitives.py -q`
Expected: all PASS unchanged — the refactor is behaviour-preserving.

- [ ] **Step 5: Commit**

```bash
git add src/svcv4_model/scoring/pfd/_common.py src/svcv4_model/scoring/pfd/nonsense.py src/svcv4_model/scoring/pfd/frameshift.py
git commit -m "refactor(scoring): branch descriptor tuple -> BranchSpec (per-branch parent/INF caps)"
```

---

## Task 2: `reference_score_start_lost` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/start_lost.py`, `tests/test_start_lost_scoring.py`; modify `scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_start_lost_scoring.py`

```python
"""Tests for reference_score_start_lost (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_start_lost
from svcv4_model.start_lost import (
    StartLostAssessment,
    StartLostOutcome,
    StartLostPredictiveEvidence,
)

MOD = GeneDiseaseValidity.MODERATE
B = VariantClassification.BENIGN


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def _benign(n: int) -> InformativeVariantsEvidence:
    return InformativeVariantsEvidence(
        variants=[InformativeVariant(id=f"b{i}", classification=B) for i in range(n)]
    )


def test_yellow_maximal() -> None:
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.NO_ALT_START,
        parent_code=PfdParentCode.NUL,
        predictive=StartLostPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=2.0,
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.held_combined["PRD+FXN"] == 8.0
    assert r.parent_total == 8.0


def test_yellow_minus4_floor() -> None:
    # PRD suppressed (predictive=None -> held None); 5 benign -> INF -6.0 -> parent floored at -4
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.NO_ALT_START,
        informative=_benign(5),
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert "PRD" not in r.sub_code_points
    assert r.sub_code_points["INF"] == -6.0
    assert r.parent_total == -4.0  # shared -8 floor would give -6.0


def test_orange_held_cap_9() -> None:
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.ALT_START_UNPROVEN,
        predictive=StartLostPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.held_combined["PRD+FXN"] == 9.0


def test_violet_benignity_only() -> None:
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.ALT_START_FUNCTIONAL,
        predictive=StartLostPredictiveEvidence(initial_points=-1.0),
        informative=_benign(1),
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == -1.0
    assert r.sub_code_points["INF"] == -2.0
    assert r.parent_total == -3.0  # within [-8, 0]


def test_empty_is_all_nd() -> None:
    r = reference_score_start_lost(StartLostAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect failure.** `uv run pytest tests/test_start_lost_scoring.py -q`

- [ ] **Step 3: Implement `scoring/pfd/start_lost.py`**

```python
"""Reference (non-authoritative) scorer for the Start-Lost workflow (SM 15)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.start_lost import StartLostAssessment, StartLostOutcome

_BRANCH: dict[StartLostOutcome, BranchSpec] = {
    # yellow: -4 parent floor; no explicit held cap in SM 15 -> parent ceiling +10
    StartLostOutcome.NO_ALT_START: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0, parent_lo=-4.0),
    StartLostOutcome.ALT_START_UNPROVEN: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0, parent_lo=-4.0),
    # violet: PRD -1.0 (SM 18 no-ops on negatives); benignity-only held/parent/INF ceilings = 0
    StartLostOutcome.ALT_START_FUNCTIONAL: BranchSpec(
        "CDS", -1.0, 0.0, held_hi=0.0, parent_hi=0.0, inf_hi=0.0
    ),
}


def reference_score_start_lost(
    assessment: StartLostAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Start-Lost point total (SM 15, three branches).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). Yellow/orange floor the parent total at -4.0; violet
    is benignity-only (parent and INF ceilings 0.0)."""
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
```

- [ ] **Step 4: Add the export** — `scoring/__init__.py` (add the import + name, keep `__all__` sorted). Full file after Task 3 shown there.

- [ ] **Step 5: Run** `uv run pytest tests/test_start_lost_scoring.py -q` — all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/pfd/start_lost.py tests/test_start_lost_scoring.py src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_score_start_lost (SM 15, 3 branches, -4 parent floor)"
```

---

## Task 3: `reference_score_stop_lost` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/stop_lost.py`, `tests/test_stop_lost_scoring.py`; modify `scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_stop_lost_scoring.py`

```python
"""Tests for reference_score_stop_lost (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_stop_lost
from svcv4_model.stop_lost import (
    StopLostAssessment,
    StopLostOutcome,
    StopLostPredictiveEvidence,
)

MOD = GeneDiseaseValidity.MODERATE


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def test_yellow_nsd() -> None:
    a = StopLostAssessment(
        prediction_outcome=StopLostOutcome.NSD_PREDICTED,
        parent_code=PfdParentCode.NUL,
        predictive=StopLostPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_stop_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 4.0
    assert r.held_combined["PRD+FXN"] == 9.0  # 4+8 capped at +9


def test_orange_no_nsd() -> None:
    a = StopLostAssessment(
        prediction_outcome=StopLostOutcome.NO_NSD,
        predictive=StopLostPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
    )
    r = reference_score_stop_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 4.0
    assert "FXN" not in r.sub_code_points


def test_empty_is_all_nd() -> None:
    r = reference_score_stop_lost(StopLostAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect failure.**

- [ ] **Step 3: Implement `scoring/pfd/stop_lost.py`**

```python
"""Reference (non-authoritative) scorer for the Stop-Lost workflow (SM 16)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.stop_lost import StopLostAssessment, StopLostOutcome

_BRANCH: dict[StopLostOutcome, BranchSpec] = {
    StopLostOutcome.NSD_PREDICTED: BranchSpec("NUL", 0.0, 4.0, held_hi=9.0),
    StopLostOutcome.NO_NSD: BranchSpec("CDS", 0.0, 4.0, held_hi=9.0),
}


def reference_score_stop_lost(
    assessment: StopLostAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Stop-Lost point total (SM 16, two branches).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). The orange four-tier interference/extension PRD scale
    is analyst-applied and captured as ``initial_points`` (not recomputed here)."""
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
```

- [ ] **Step 4: Update `scoring/__init__.py`** — final state with all four scorers + ScoreResult:

```python
from svcv4_model.scoring.pfd.frameshift import reference_score_frameshift
from svcv4_model.scoring.pfd.nonsense import reference_score_nonsense
from svcv4_model.scoring.pfd.start_lost import reference_score_start_lost
from svcv4_model.scoring.pfd.stop_lost import reference_score_stop_lost
from svcv4_model.scoring.result import ScoreResult

__all__ = [
    "ScoreResult",
    "reference_score_frameshift",
    "reference_score_nonsense",
    "reference_score_start_lost",
    "reference_score_stop_lost",
]
```

- [ ] **Step 5: Run the full suite** — `uv run pytest -q` — all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/pfd/stop_lost.py tests/test_stop_lost_scoring.py src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_score_stop_lost (SM 16, 2 branches)"
```

---

## Task 4: Docs

**Files:** Modify `docs/reference/scoring.md`

- [ ] **Step 1: Extend the "What is modeled so far" list** — after the Frameshift line, add:

```markdown
- **Start-Lost** (SM 15) — `reference_score_start_lost`, three branches (yellow/orange floor
  the parent total at −4.0; violet is benignity-only).
- **Stop-Lost** (SM 16) — `reference_score_stop_lost`, two branches.

The shared `score_nul_cds_workflow` now carries per-branch caps via a `BranchSpec` (parent
floor/ceiling, held ceiling, INF ceiling), so each LoF scorer is just its branch table.
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (0 warnings).

- [ ] **Step 3: Commit** — `git commit -am "docs: note the Start-Lost + Stop-Lost reference scorers"`

---

## Task 5: Full quality gates

- [ ] **Step 1: Run everything**

```bash
uv run pytest -q
uv run ruff check .
git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN || echo GATE_DIRTY
uv run mkdocs build --strict
uv run python scripts/export_schemas.py && git status --porcelain schemas/json   # must be empty
git status --porcelain
```

Expected: all pass; `GATE_CLEAN`; no scoring schema; tree clean except pre-existing untracked files.

- [ ] **Step 2: Ready for code review + PR.**

---

## Notes for the implementer

- The Nonsense/Frameshift refactor MUST be behaviour-preserving — their unchanged tests are the guard. BranchSpec defaults (`parent -8..+10`, `INF -8..+8`, `held_hi 9.0`) equal the old shared constants, so defaulted conversions are identical.
- **The −4-floor test REQUIRES `predictive=None`** (so held is None) — with a +6 PRD the floor cannot bite (min reachable is −2). Do not "simplify" the test to include PRD.
- FXN stays consumed raw (no cap) — violet's benignity-only FXN is the analyst's coded value.
- Do NOT add scoring to the root `svcv4_model/__init__.py` `__all__` (schema).
- Line length 100 (ruff). `__all__` hand-sorted.
