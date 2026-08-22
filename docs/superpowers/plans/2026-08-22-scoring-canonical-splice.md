# Reference Scorer — Canonical Splice (SM 11) + SPL_ pipeline helper — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add the `score_spl_workflow` helper (SPL_ pipeline: PRD → SPA → held → FXN → held → INF → parent, two held values, parent always `SPL`) + `SplBranchSpec`, then `reference_score_canonical_splice` (SM 11, five paths). Increment A of the splice family. Non-authoritative; CSpec authoritative.

**Architecture:** New `scoring/pfd/_spl_common.py` (separate from `_common.py` — the SPL_ pipeline differs). Reuses `apply_sm18_multiplier`/`cap`/`hold_combined`/`informative_points`/`ScoreResult`. SPA + FXN consumed raw; PRD + INF computed. NUL_/CDS_ scorers untouched.

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Confirmed:** `SplicePredictionOutcome.{NMD_PREDICTED,FRAMESHIFT_NO_NMD,SPLICE_NO_FRAMESHIFT,UNCERTAIN,UNLIKELY}`; `CanonicalSpliceAssessment` has `prediction_outcome, predictive, mechanism_exon_relevance, spa_points, fxn_points, informative` (+ `SplicePredictiveEvidence.initial_points`).

---

## Task 1: `score_spl_workflow` + `SplBranchSpec` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/_spl_common.py`, `tests/test_spl_common.py`

- [ ] **Step 1: Write the failing test** — `tests/test_spl_common.py`

```python
"""Tests for the shared SPL_ scoring pipeline (non-authoritative)."""

from __future__ import annotations

from svcv4_model.canonical_splice import CanonicalSpliceAssessment
from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.scoring.pfd._spl_common import SplBranchSpec, score_spl_workflow
from svcv4_model.splice import SplicePredictionOutcome, SplicePredictiveEvidence

MOD = GeneDiseaseValidity.MODERATE
_BRANCH = {SplicePredictionOutcome.NMD_PREDICTED: SplBranchSpec(0.0, 6.0)}


def test_spl_pipeline_prd_spa_fxn_held_and_parent() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        spa_points=0.0,
        fxn_points=2.0,
    )
    r = score_spl_workflow(a, _BRANCH, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.sub_code_points["SPA"] == 0.0
    assert r.sub_code_points["FXN"] == 2.0
    assert r.held_combined["PRD+SPA"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 8.0


def test_spl_spa_consumed_as_delta() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        spa_points=-1.5,  # substantial -25% of +6
    )
    r = score_spl_workflow(a, _BRANCH, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == 4.5


def test_spl_empty_is_all_nd_but_parent_code_spl() -> None:
    r = score_spl_workflow(CanonicalSpliceAssessment(), _BRANCH, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.sub_code_points == {}
    assert r.held_combined == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect ModuleNotFoundError.** `uv run pytest tests/test_spl_common.py -q`

- [ ] **Step 3: Implement `scoring/pfd/_spl_common.py`**

```python
"""Shared scoring pipeline for the SPL_ splice workflows (non-authoritative).

The Canonical-Splice / Intronic-Synonymous / Missense-splice scorers share one pipeline
(PRD -> SPA -> held prd_spa -> FXN -> held prd_spa_fxn -> INF -> parent), with two held
values and a constant SPL_ parent code; per-path caps are carried in a ``SplBranchSpec``.
SPA and FXN are consumed raw (analyst-coded); PRD and INF are computed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import InformativeVariant
from svcv4_model.mechanism import ExonRelevance, GenccMechanism
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
)
from svcv4_model.scoring.result import ScoreResult

_HELD_LO = -8.0


class _MechExon(Protocol):
    gencc_mechanism: GenccMechanism | None
    exon_relevance: ExonRelevance | None


class _Predictive(Protocol):
    initial_points: float | None


class _Informative(Protocol):
    variants: list[InformativeVariant]


class SplAssessment(Protocol):
    """Structural type the shared SPL_ helper reads."""

    prediction_outcome: object
    predictive: _Predictive | None
    mechanism_exon_relevance: _MechExon | None
    spa_points: float | None
    fxn_points: float | None
    informative: _Informative | None


@dataclass(frozen=True)
class SplBranchSpec:
    """Per-path caps for an SPL_ splice workflow (parent code is constant SPL)."""

    prd_lo: float
    prd_hi: float
    prd_spa_lo: float = -8.0
    prd_spa_hi: float = 10.0
    prd_spa_fxn_hi: float = 9.0
    inf_lo: float = -8.0
    inf_hi: float = 8.0
    parent_lo: float = -8.0
    parent_hi: float = 10.0


def score_spl_workflow(
    assessment: SplAssessment,
    branch_table: Mapping[object, SplBranchSpec],
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Reference (NON-AUTHORITATIVE) score for an SPL_ splice workflow. CSpec is authoritative.

    PRD is computed (initial x SM 18, capped); SPA and FXN are consumed raw (analyst-coded);
    INF is the shared tally. Two held values (PRD+SPA, PRD+SPA+FXN) are recorded; the parent
    code is always ``SPL``. ``gene_disease_validity`` is required.
    """
    prov: list[str] = []
    sub: dict[str, float] = {}
    held: dict[str, float] = {}

    outcome = assessment.prediction_outcome
    branch = branch_table.get(outcome) if outcome is not None else None

    # PRD (computed)
    prd: float | None = None
    initial = assessment.predictive.initial_points if assessment.predictive else None
    mer = assessment.mechanism_exon_relevance
    mech = mer.gencc_mechanism if mer else None
    exon = mer.exon_relevance if mer else None
    if initial is None or branch is None:
        prov.append("SPL_PRD: _ND (no initial points and/or unknown path)")
    else:
        adj = apply_sm18_multiplier(initial, mech, exon, gene_disease_validity)
        prd = cap(adj, branch.prd_lo, branch.prd_hi)
        sub["PRD"] = prd
        prov.append(f"SPL_PRD: {initial} x SM18 = {adj}, capped [{branch.prd_lo}, {branch.prd_hi}] -> {prd}")

    # SPA (consumed raw)
    spa = assessment.spa_points
    if spa is None:
        prov.append("SPL_SPA: _ND (no coded spa_points)")
    else:
        sub["SPA"] = spa
        prov.append(f"SPL_SPA: consumed coded value {spa}")

    # held PRD+SPA
    prd_spa_lo = branch.prd_spa_lo if branch else -8.0
    prd_spa_hi = branch.prd_spa_hi if branch else 10.0
    prd_spa = hold_combined(prd, spa, lo=prd_spa_lo, hi=prd_spa_hi)
    if prd_spa is not None:
        held["PRD+SPA"] = prd_spa
        prov.append(f"held PRD+SPA: {prd_spa} (cap [{prd_spa_lo}, {prd_spa_hi}])")

    # FXN (consumed raw)
    fxn = assessment.fxn_points
    if fxn is None:
        prov.append("SPL_FXN: _ND (no coded fxn_points; OddsPath not recomputed)")
    else:
        sub["FXN"] = fxn
        prov.append(f"SPL_FXN: consumed coded value {fxn}")

    # held PRD+SPA+FXN
    prd_spa_fxn_hi = branch.prd_spa_fxn_hi if branch else 9.0
    prd_spa_fxn = hold_combined(prd_spa, fxn, lo=_HELD_LO, hi=prd_spa_fxn_hi)
    if prd_spa_fxn is not None:
        held["PRD+SPA+FXN"] = prd_spa_fxn
        prov.append(f"held PRD+SPA+FXN: {prd_spa_fxn} (cap [{_HELD_LO}, {prd_spa_fxn_hi}])")

    # INF (computed)
    inf: float | None = None
    inf_lo = branch.inf_lo if branch else -8.0
    inf_hi = branch.inf_hi if branch else 8.0
    if assessment.informative is not None:
        inf = cap(informative_points(assessment.informative.variants), inf_lo, inf_hi)
    if inf is None:
        prov.append("SPL_INF: _ND (no classified informative variants)")
    else:
        sub["INF"] = inf
        prov.append(f"SPL_INF: {inf} (cap [{inf_lo}, {inf_hi}])")

    # parent total
    parent_lo = branch.parent_lo if branch else -8.0
    parent_hi = branch.parent_hi if branch else 10.0
    parent_total = hold_combined(prd_spa_fxn, inf, lo=parent_lo, hi=parent_hi)
    if parent_total is not None:
        prov.append(f"spl_total: {parent_total} (cap [{parent_lo}, {parent_hi}])")

    return ScoreResult(
        parent_code="SPL",
        sub_code_points=sub,
        held_combined=held,
        parent_total=parent_total,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 4: Run** `uv run pytest tests/test_spl_common.py -q` — all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/svcv4_model/scoring/pfd/_spl_common.py tests/test_spl_common.py
git commit -m "feat(scoring): add score_spl_workflow + SplBranchSpec (SPL_ pipeline, SPA/FXN consumed raw)"
```

---

## Task 2: `reference_score_canonical_splice` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/canonical_splice.py`, `tests/test_canonical_splice_scoring.py`; modify `scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_canonical_splice_scoring.py`

```python
"""Tests for reference_score_canonical_splice (non-authoritative)."""

from __future__ import annotations

from svcv4_model.canonical_splice import CanonicalSpliceAssessment
from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.scoring import reference_score_canonical_splice
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
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(),
        spa_points=0.0,
        fxn_points=2.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.held_combined["PRD+SPA"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 8.0
    assert r.sub_code_points["INF"] == 2.0
    assert r.parent_total == 10.0  # capped at +10


def test_yellow_prd_spa_fxn_cap_9() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(),
        spa_points=0.0,
        fxn_points=8.0,
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # 6+0+8 capped at +9 (not parent +10)


def test_blue_parent_cap_8() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNCERTAIN,
        predictive=SplicePredictiveEvidence(initial_points=0.0),
        spa_points=2.0,  # additive
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == 2.0
    assert r.held_combined["PRD+SPA+FXN"] == 8.0  # cap(2+8, +8)
    assert r.parent_total == 8.0  # cap(8+2, [-8, 8])


def test_violet_benignity() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNLIKELY,
        predictive=SplicePredictiveEvidence(initial_points=-1.0),
        spa_points=-2.0,  # benignity
        informative=_inf(VariantClassification.PATHOGENIC, 1),  # +2 clamped to 0 by inf_hi=0
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == -3.0  # cap(-3, [-3, 0])
    assert r.sub_code_points["INF"] == 0.0
    assert r.parent_total == -3.0  # within [-8, 0]


def test_spa_nd() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(),
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert "SPA" not in r.sub_code_points
    assert r.held_combined["PRD+SPA"] == 6.0  # prd alone (spa _ND)


def test_all_five_outcomes() -> None:
    for outcome in SplicePredictionOutcome:
        r = reference_score_canonical_splice(
            CanonicalSpliceAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code == "SPL"


def test_empty_is_all_nd() -> None:
    r = reference_score_canonical_splice(CanonicalSpliceAssessment(), gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect failure.**

- [ ] **Step 3: Implement `scoring/pfd/canonical_splice.py`**

```python
"""Reference (non-authoritative) scorer for the Canonical Splice workflow (SM 11)."""

from __future__ import annotations

from svcv4_model.canonical_splice import CanonicalSpliceAssessment
from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.scoring.pfd._spl_common import SplBranchSpec, score_spl_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.splice import SplicePredictionOutcome

_BRANCH: dict[SplicePredictionOutcome, SplBranchSpec] = {
    SplicePredictionOutcome.NMD_PREDICTED: SplBranchSpec(0.0, 6.0),
    SplicePredictionOutcome.FRAMESHIFT_NO_NMD: SplBranchSpec(-1.0, 6.0),
    SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT: SplBranchSpec(-1.0, 6.0),
    SplicePredictionOutcome.UNCERTAIN: SplBranchSpec(0.0, 0.0, prd_spa_fxn_hi=8.0, parent_hi=8.0),
    SplicePredictionOutcome.UNLIKELY: SplBranchSpec(
        -1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0, prd_spa_fxn_hi=0.0, inf_hi=0.0, parent_hi=0.0
    ),
}


def reference_score_canonical_splice(
    assessment: CanonicalSpliceAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Canonical Splice point total (SM 11, five paths).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). SPA is consumed raw (the coded delta; on canonical the
    assay reduces the PRD). The violet path is benignity-only.
    """
    return score_spl_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
```

- [ ] **Step 4: Add the export** — `scoring/__init__.py`: add the import + `"reference_score_canonical_splice"` sorted into `__all__` (alphabetical among `reference_score_*`: `canonical_splice` < `exon_deletion`):

```python
from svcv4_model.scoring.pfd.canonical_splice import reference_score_canonical_splice
from svcv4_model.scoring.pfd.exon_deletion import reference_score_exon_deletion
...
__all__ = [
    "ScoreResult",
    "reference_score_canonical_splice",
    "reference_score_exon_deletion",
    "reference_score_exon_duplication",
    "reference_score_frameshift",
    "reference_score_nonsense",
    "reference_score_start_lost",
    "reference_score_stop_lost",
]
```

- [ ] **Step 5: Run** `uv run pytest tests/test_canonical_splice_scoring.py -q` — all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/pfd/canonical_splice.py tests/test_canonical_splice_scoring.py src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_score_canonical_splice (SM 11, 5 paths)"
```

---

## Task 3: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — after the Exon Duplication line, add:

```markdown
- **Canonical Splice** (SM 11) — `reference_score_canonical_splice`, five paths (the first
  `SPL_` scorer: an extra SPL_SPA step and two held values via `score_spl_workflow`; SPA is
  consumed raw as the coded delta).
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (0 warnings).

- [ ] **Step 3: Commit** — `git commit -am "docs: note the Canonical Splice reference scorer (SPL_ pipeline)"`

---

## Task 4: Full quality gates

- [ ] **Step 1:** `uv run pytest -q`; `uv run ruff check .`; drift gate; `mkdocs build --strict`; `uv run python scripts/export_schemas.py && git status --porcelain schemas/json` (empty); `git status --porcelain`. All clean except pre-existing untracked files.
- [ ] **Step 2:** Ready for code review + PR.

---

## Notes for the implementer

- The SPL_ helper is a NEW module (`_spl_common.py`); it does not touch `score_nul_cds_workflow`. The existing scoring tests must stay green (they don't use the SPL_ path).
- SPA and FXN are consumed raw; PRD and INF are computed. `parent_code` is always `"SPL"` (even for an empty assessment / unknown outcome).
- The **`prd_spa_fxn` held cap is +9** for yellow/orange (SM 11 explicit) — not the parent +10. Blue +8, violet 0.
- SPA is a coded DELTA (added to PRD), not a fraction — `held prd_spa = prd + spa`.
- Do NOT add scoring to the root `__all__` (schema). Line length 100.
