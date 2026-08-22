# Reference Scorer — Frameshift (SM 9) + shared NUL_/CDS_ helper — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Extract the shared NUL_/CDS_ scoring pipeline into `scoring/pfd/_common.py::score_nul_cds_workflow`, refactor `reference_score_nonsense` to delegate to it (behaviour-preserving), and add `reference_score_frameshift` (SM 9, five branches) as a thin branch-table + delegation.

**Architecture:** The helper holds the whole pipeline (PRD → SM 18 → FXN-consumed-raw → held PRD+FXN → INF → capped parent), parameterized by a per-workflow `branch_table` of `(parent_code, prd_lo, prd_hi, held_hi)`. Shared caps (parent −8..+10, INF −8..+8, held-lo −8) are named constants; **FXN is consumed raw, never re-capped**. Non-authoritative; CSpec authoritative.

**Tech Stack:** Python 3.11+, stdlib, `uv`, ruff (line-length 100), pytest, mkdocs strict.

**Confirmed:** `FrameshiftPredictionOutcome.{NMD_NO_RESCUE,NMD_WITH_RESCUE,NO_NMD,NON_STOP_DECAY,PROTEIN_EXTENSION}`; `FrameshiftAssessment` is field-identical to `NonsenseAssessment` for the helper's needs. Tests flat in `tests/`.

---

## Task 1: Extract `score_nul_cds_workflow` + refactor Nonsense (behaviour-preserving)

**Files:**
- Create: `src/svcv4_model/scoring/pfd/_common.py`
- Modify: `src/svcv4_model/scoring/pfd/nonsense.py`
- Guard (unchanged): `tests/test_nonsense_scoring.py`

- [ ] **Step 1: Create `scoring/pfd/_common.py`** — the generalized body of the current `reference_score_nonsense` (identical logic; branch table + named shared constants):

```python
"""Shared scoring pipeline for the NUL_/CDS_ LoF workflows (non-authoritative).

The Nonsense/Frameshift/Exon-Deletion/Exon-Duplication/Start-Lost/Stop-Lost scorers share one
pipeline (PRD -> SM 18 -> FXN -> held PRD+FXN -> INF -> capped parent); only the per-branch
PRD range and held-PRD+FXN ceiling differ, carried in each workflow's ``branch_table``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.mechanism import ExonRelevance, GenccMechanism
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
)
from svcv4_model.scoring.result import ScoreResult


class _MechExon(Protocol):
    gencc_mechanism: GenccMechanism | None
    exon_relevance: ExonRelevance | None


class _Predictive(Protocol):
    initial_points: float | None


class _Informative(Protocol):
    variants: list


class NulCdsAssessment(Protocol):
    """Structural type the shared helper reads (NonsenseAssessment / FrameshiftAssessment / ...)."""

    prediction_outcome: object
    parent_code: PfdParentCode | None
    predictive: _Predictive | None
    mechanism_exon_relevance: _MechExon | None
    fxn_points: float | None
    informative: _Informative | None


_PARENT_LO, _PARENT_HI = -8.0, 10.0
_INF_LO, _INF_HI = -8.0, 8.0
_HELD_LO = -8.0
_DEFAULT_HELD_HI = 9.0


def score_nul_cds_workflow(
    assessment: NulCdsAssessment,
    branch_table: Mapping[object, tuple[str, float, float, float]],
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Reference (NON-AUTHORITATIVE) score for a NUL_/CDS_ LoF workflow. CSpec is authoritative.

    ``branch_table`` maps ``prediction_outcome`` -> ``(parent_code, prd_lo, prd_hi, held_hi)``.
    FXN is consumed raw from ``fxn_points`` (already coded; OddsPath not recomputed).
    ``gene_disease_validity`` is required (pass explicit None for a below-Moderate MDE).
    """
    prov: list[str] = []
    sub: dict[str, float] = {}
    held: dict[str, float] = {}

    outcome = assessment.prediction_outcome
    branch = branch_table.get(outcome) if outcome is not None else None
    parent_code = branch[0] if branch else None

    # PRD
    prd: float | None = None
    initial = assessment.predictive.initial_points if assessment.predictive else None
    mer = assessment.mechanism_exon_relevance
    mech = mer.gencc_mechanism if mer else None
    exon = mer.exon_relevance if mer else None
    if initial is None or branch is None:
        prov.append("PRD: _ND (no initial points and/or unknown branch)")
    else:
        adj = apply_sm18_multiplier(initial, mech, exon, gene_disease_validity)
        prd = cap(adj, branch[1], branch[2])
        sub["PRD"] = prd
        prov.append(
            f"PRD: initial {initial} x SM18(mech={mech}, exon={exon}, "
            f"gdv={gene_disease_validity}) = {adj}, capped [{branch[1]}, {branch[2]}] -> {prd}"
        )

    # FXN (consumed raw, not recomputed and not re-capped)
    fxn = assessment.fxn_points
    if fxn is None:
        prov.append("FXN: _ND (no coded fxn_points captured; OddsPath not recomputed)")
    else:
        sub["FXN"] = fxn
        prov.append(f"FXN: consumed coded value {fxn}")

    # held PRD+FXN
    held_hi = branch[3] if branch else _DEFAULT_HELD_HI
    held_val = hold_combined(prd, fxn, lo=_HELD_LO, hi=held_hi)
    if held_val is not None:
        held["PRD+FXN"] = held_val
        prov.append(f"held PRD+FXN: {held_val} (cap [{_HELD_LO}, {held_hi}])")

    # INF
    inf: float | None = None
    if assessment.informative is not None:
        inf = cap(informative_points(assessment.informative.variants), _INF_LO, _INF_HI)
    if inf is None:
        prov.append("INF: _ND (no classified informative variants)")
    else:
        sub["INF"] = inf
        prov.append(f"INF: {inf} (cap [{_INF_LO}, {_INF_HI}])")

    # parent total
    parent_total = hold_combined(held_val, inf, lo=_PARENT_LO, hi=_PARENT_HI)
    if parent_total is not None:
        prov.append(f"parent_total: {parent_total} (cap [{_PARENT_LO}, {_PARENT_HI}])")

    # captured parent_code cross-check (report, do not fix)
    captured = assessment.parent_code
    if captured is not None and parent_code is not None and captured.value != parent_code:
        prov.append(f"NOTE: captured parent_code {captured.value} != branch-derived {parent_code}")

    return ScoreResult(
        parent_code=parent_code,
        sub_code_points=sub,
        held_combined=held,
        parent_total=parent_total,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 2: Refactor `scoring/pfd/nonsense.py` to delegate** — replace the whole body with the branch table + a one-line delegation (keep the module + function docstrings):

```python
"""Reference (non-authoritative) scorer for the Nonsense workflow (SM 8)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.nonsense import NonsenseAssessment, NonsensePredictionOutcome
from svcv4_model.scoring.pfd._common import score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult

# per-branch: (parent_code, prd_lo, prd_hi, held_hi)
_BRANCH: dict[NonsensePredictionOutcome, tuple[str, float, float, float]] = {
    NonsensePredictionOutcome.NMD_NO_RESCUE: ("NUL", 0.0, 6.0, 10.0),
    NonsensePredictionOutcome.NMD_WITH_RESCUE: ("CDS", -1.0, 6.0, 9.0),
    NonsensePredictionOutcome.NO_NMD: ("CDS", 0.0, 6.0, 9.0),
}


def reference_score_nonsense(
    assessment: NonsenseAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Nonsense point total (SM 8). CSpec is
    authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE)."""
    return score_nul_cds_workflow(
        assessment, _BRANCH, gene_disease_validity=gene_disease_validity
    )
```

- [ ] **Step 3: Run the nonsense tests (the refactor's regression guard)**

Run: `uv run pytest tests/test_nonsense_scoring.py tests/test_scoring_primitives.py -q`
Expected: all PASS unchanged — behaviour preserved.

- [ ] **Step 4: Commit**

```bash
git add src/svcv4_model/scoring/pfd/_common.py src/svcv4_model/scoring/pfd/nonsense.py
git commit -m "refactor(scoring): extract shared score_nul_cds_workflow; nonsense delegates"
```

---

## Task 2: `reference_score_frameshift` (TDD)

**Files:**
- Create: `src/svcv4_model/scoring/pfd/frameshift.py`
- Modify: `src/svcv4_model/scoring/__init__.py` (export)
- Test: `tests/test_frameshift_scoring.py`

- [ ] **Step 1: Write the failing test** — `tests/test_frameshift_scoring.py`

```python
"""Tests for reference_score_frameshift (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.frameshift import (
    FrameshiftAssessment,
    FrameshiftPredictionOutcome,
    FrameshiftPredictiveEvidence,
)
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_frameshift

MOD = GeneDiseaseValidity.MODERATE


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def test_yellow_maximal() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NMD_NO_RESCUE,
        parent_code=PfdParentCode.NUL,
        predictive=FrameshiftPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=2.0,
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(id="a", classification=VariantClassification.PATHOGENIC)
            ]
        ),
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.held_combined["PRD+FXN"] == 8.0
    assert r.sub_code_points["INF"] == 2.0
    assert r.parent_total == 10.0


def test_green_nsd_parent_nul_and_held_cap_9() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NON_STOP_DECAY,
        predictive=FrameshiftPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 4.0
    assert r.held_combined["PRD+FXN"] == 9.0  # 4+8 capped at +9 (NSD green held cap)


def test_green_extension_parent_cds_prd_capped_to_4() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.PROTEIN_EXTENSION,
        predictive=FrameshiftPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 4.0
    assert "FXN" not in r.sub_code_points


def test_orange_held_cap_9() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NMD_WITH_RESCUE,
        predictive=FrameshiftPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.held_combined["PRD+FXN"] == 9.0


def test_violet_reduced_mechanism_and_benign_inf() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NO_NMD,
        predictive=FrameshiftPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.LIKELY, ExonRelevance.MOST),
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="b", classification=VariantClassification.BENIGN)]
        ),
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 1.5  # 6.0 x 0.5 x 0.5
    assert r.sub_code_points["INF"] == -2.0
    assert r.parent_total == -0.5


def test_empty_assessment_is_all_nd() -> None:
    r = reference_score_frameshift(FrameshiftAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
    assert r.parent_code is None
```

- [ ] **Step 2: Run — expect failure** (`reference_score_frameshift` not importable).

Run: `uv run pytest tests/test_frameshift_scoring.py -q`

- [ ] **Step 3: Implement `scoring/pfd/frameshift.py`**

```python
"""Reference (non-authoritative) scorer for the Frameshift workflow (SM 9)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.frameshift import FrameshiftAssessment, FrameshiftPredictionOutcome
from svcv4_model.scoring.pfd._common import score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult

# per-branch: (parent_code, prd_lo, prd_hi, held_hi)
_BRANCH: dict[FrameshiftPredictionOutcome, tuple[str, float, float, float]] = {
    FrameshiftPredictionOutcome.NMD_NO_RESCUE: ("NUL", 0.0, 6.0, 10.0),
    FrameshiftPredictionOutcome.NMD_WITH_RESCUE: ("CDS", -1.0, 6.0, 9.0),
    FrameshiftPredictionOutcome.NO_NMD: ("CDS", 0.0, 6.0, 9.0),
    FrameshiftPredictionOutcome.NON_STOP_DECAY: ("NUL", 0.0, 4.0, 9.0),
    FrameshiftPredictionOutcome.PROTEIN_EXTENSION: ("CDS", 0.0, 4.0, 9.0),
}


def reference_score_frameshift(
    assessment: FrameshiftAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Frameshift point total (SM 9, five branches).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). The two green (NSD / extension) branches are a
    non-additive analyst choice upstream; this scores the single captured ``prediction_outcome``.
    """
    return score_nul_cds_workflow(
        assessment, _BRANCH, gene_disease_validity=gene_disease_validity
    )
```

- [ ] **Step 4: Add the export** — `scoring/__init__.py`:

```python
from svcv4_model.scoring.pfd.frameshift import reference_score_frameshift
from svcv4_model.scoring.pfd.nonsense import reference_score_nonsense
from svcv4_model.scoring.result import ScoreResult

__all__ = ["ScoreResult", "reference_score_frameshift", "reference_score_nonsense"]
```

- [ ] **Step 5: Run the full suite**

Run: `uv run pytest -q`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/pfd/frameshift.py src/svcv4_model/scoring/__init__.py tests/test_frameshift_scoring.py
git commit -m "feat(scoring): add reference_score_frameshift (SM 9, 5 branches)"
```

---

## Task 3: Docs

**Files:** Modify `docs/reference/scoring.md`

- [ ] **Step 1: Update the "What is modeled so far" list** — OLD:

```markdown
- **Nonsense** (SM 8) — `reference_score_nonsense`, all three branches.
```

NEW:

```markdown
- **Nonsense** (SM 8) — `reference_score_nonsense`, all three branches.
- **Frameshift** (SM 9) — `reference_score_frameshift`, all five branches (shares the
  `score_nul_cds_workflow` pipeline with Nonsense).
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (0 warnings).

- [ ] **Step 3: Commit**

```bash
git add docs/reference/scoring.md
git commit -m "docs: note the Frameshift reference scorer"
```

---

## Task 4: Full quality gates

- [ ] **Step 1: Run everything**

```bash
uv run pytest -q
uv run ruff check .
git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN || echo GATE_DIRTY
uv run mkdocs build --strict
uv run python scripts/export_schemas.py && git status --porcelain schemas/json   # must be empty
git status --porcelain
```

Expected: pytest all pass; ruff clean; `GATE_CLEAN`; strict build clean; **no scoring schema produced**; tree clean except pre-existing untracked files.

- [ ] **Step 2: Ready for code review + PR.**

---

## Notes for the implementer

- The nonsense refactor MUST be behaviour-preserving — `tests/test_nonsense_scoring.py` is unchanged and is the guard. If any nonsense test changes value, the generalization diverged.
- **FXN is consumed raw** (no `cap(fxn, ...)`) — matching Increment 0. Do not add an FXN cap.
- Do NOT add scoring to the root `svcv4_model/__init__.py` `__all__` (would generate a schema).
- Line length 100 (ruff), not the 79 the IDE shows.
- `__all__` in `scoring/__init__.py` is hand-sorted alphabetically: `ScoreResult`, `reference_score_frameshift`, `reference_score_nonsense`.
