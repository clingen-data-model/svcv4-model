# Reference Scorer — Exon Deletion (SM 13) + mechanism-only SM 18 — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add a `mechanism_only` mode to `apply_sm18_multiplier` (+ `sm18_mechanism_only` to `BranchSpec`), then add `reference_score_exon_deletion` (SM 13, six branches; whole-gene is mechanism-only, grey reuses the benignity ceilings).

**Architecture:** One keyword on the primitive (exon axis removed when True), one `BranchSpec` field (default False), one helper line to pass it. Behaviour-preserving for the four existing scorers (all default False). Non-authoritative; CSpec authoritative.

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Confirmed:** `ExonDeletionOutcome.{WHOLE_GENE,SUBGENIC_NMD,SUBGENIC_NO_NMD,START_CODON_NO_ALT_START,START_CODON_ALT_START_UNPROVEN,START_CODON_ALT_START_FUNCTIONAL}`; `ExonDeletionAssessment` satisfies `NulCdsAssessment`.

---

## Task 1: mechanism-only SM 18 (primitive + BranchSpec + helper)

**Files:** Modify `src/svcv4_model/scoring/primitives.py`, `.../scoring/pfd/_common.py`
**Guards (unchanged):** `tests/test_scoring_primitives.py`, `test_nonsense_scoring.py`, `test_frameshift_scoring.py`, `test_start_lost_scoring.py`, `test_stop_lost_scoring.py`

- [ ] **Step 1: Add `mechanism_only` to `apply_sm18_multiplier`** — `primitives.py`. Change the signature and insert the early return AFTER the `mech` computation, BEFORE the exon/special-case logic:

```python
def apply_sm18_multiplier(
    points: float | None,
    gencc_mechanism: GenccMechanism | None,
    exon_relevance: ExonRelevance | None,
    gene_disease_validity: GeneDiseaseValidity | None,
    *,
    mechanism_only: bool = False,
) -> float | None:
    """... (existing docstring) ...

    ``mechanism_only`` removes the exon-relevance axis (SM 13 whole-gene deletion): the
    reduction is the mechanism fraction alone (exon and the Suspected x Most special-case are
    not consulted).
    """
    if points is None or points <= 0:
        return points
    if gene_disease_validity not in _GDV_MODERATE_PLUS:
        return 0.0
    mech = _MECHANISM_FRACTION.get(gencc_mechanism, 0.0) if gencc_mechanism else 0.0
    if mechanism_only:
        return points * mech
    exon = 1.0 if exon_relevance is None else _EXON_FRACTION.get(exon_relevance, 1.0)
    if gencc_mechanism == GenccMechanism.SUSPECTED and exon_relevance == ExonRelevance.MOST:
        fraction = 0.25
    else:
        fraction = mech * exon
    return points * fraction
```

- [ ] **Step 2: Add `sm18_mechanism_only` to `BranchSpec`** — `_common.py`, after `inf_hi`:

```python
    inf_lo: float = _INF_LO
    inf_hi: float = _INF_HI
    sm18_mechanism_only: bool = False
```

- [ ] **Step 3: Pass it in the helper's PRD step** — `_common.py`, change the `apply_sm18_multiplier` call:

```python
        adj = apply_sm18_multiplier(
            initial, mech, exon, gene_disease_validity,
            mechanism_only=branch.sm18_mechanism_only,
        )
```

- [ ] **Step 4: Run the regression guards**

Run: `uv run pytest tests/test_scoring_primitives.py tests/test_nonsense_scoring.py tests/test_frameshift_scoring.py tests/test_start_lost_scoring.py tests/test_stop_lost_scoring.py -q`
Expected: all PASS unchanged (mechanism_only defaults False everywhere).

- [ ] **Step 5: Commit**

```bash
git add src/svcv4_model/scoring/primitives.py src/svcv4_model/scoring/pfd/_common.py
git commit -m "feat(scoring): add mechanism-only SM 18 mode (for whole-gene deletions)"
```

---

## Task 2: `reference_score_exon_deletion` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/exon_deletion.py`, `tests/test_exon_deletion_scoring.py`; modify `scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_exon_deletion_scoring.py`

```python
"""Tests for reference_score_exon_deletion (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.exon_deletion import (
    ExonDeletionAssessment,
    ExonDeletionOutcome,
    ExonDeletionPredictiveEvidence,
)
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_exon_deletion

MOD = GeneDiseaseValidity.MODERATE


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def test_whole_gene_maximal() -> None:
    a = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.WHOLE_GENE,
        parent_code=PfdParentCode.NUL,
        predictive=ExonDeletionPredictiveEvidence(initial_points=10.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=0.0,
    )
    r = reference_score_exon_deletion(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 10.0
    assert r.parent_total == 10.0  # capped at +10


def test_whole_gene_is_mechanism_only() -> None:
    # whole-gene: Suspected mechanism + Few exon -> mechanism-only ignores Few -> 10 x 0.25 = 2.5
    wg = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.WHOLE_GENE,
        predictive=ExonDeletionPredictiveEvidence(initial_points=10.0),
        mechanism_exon_relevance=_mer(GenccMechanism.SUSPECTED, ExonRelevance.FEW),
    )
    r = reference_score_exon_deletion(wg, gene_disease_validity=MOD)
    assert r.sub_code_points["PRD"] == 2.5
    # a FULL-mode subgenic branch with the same Suspected+Few zeroes (0.25 x 0.0)
    sub = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.SUBGENIC_NMD,
        predictive=ExonDeletionPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.SUSPECTED, ExonRelevance.FEW),
    )
    r2 = reference_score_exon_deletion(sub, gene_disease_validity=MOD)
    assert r2.sub_code_points["PRD"] == 0.0


def test_subgenic_nmd_held_10() -> None:
    a = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.SUBGENIC_NMD,
        predictive=ExonDeletionPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_exon_deletion(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.held_combined["PRD+FXN"] == 10.0  # 6+8 capped at +10 (NUL_ path)


def test_violet_held_9() -> None:
    a = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.SUBGENIC_NO_NMD,
        predictive=ExonDeletionPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_exon_deletion(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.held_combined["PRD+FXN"] == 9.0  # violet held cap +9


def test_grey_benignity_only() -> None:
    a = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.START_CODON_ALT_START_FUNCTIONAL,
        predictive=ExonDeletionPredictiveEvidence(initial_points=-1.0),
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="p", classification=VariantClassification.PATHOGENIC)]
        ),
    )
    r = reference_score_exon_deletion(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == -1.0
    assert r.sub_code_points["INF"] == 0.0  # +2 tally clamped by inf_hi=0 (benignity-only)
    assert r.parent_total == -1.0  # within [-8, 0]


def test_empty_is_all_nd() -> None:
    r = reference_score_exon_deletion(ExonDeletionAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect failure.**

- [ ] **Step 3: Implement `scoring/pfd/exon_deletion.py`**

```python
"""Reference (non-authoritative) scorer for the Single/Multi-Exon Deletion workflow (SM 13)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.exon_deletion import ExonDeletionAssessment, ExonDeletionOutcome
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult

_BRANCH: dict[ExonDeletionOutcome, BranchSpec] = {
    # whole-gene: +10, mechanism-only SM 18 (exon-relevance axis removed)
    ExonDeletionOutcome.WHOLE_GENE: BranchSpec(
        "NUL", 0.0, 10.0, held_hi=10.0, sm18_mechanism_only=True
    ),
    ExonDeletionOutcome.SUBGENIC_NMD: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    ExonDeletionOutcome.SUBGENIC_NO_NMD: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
    ExonDeletionOutcome.START_CODON_NO_ALT_START: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    ExonDeletionOutcome.START_CODON_ALT_START_UNPROVEN: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
    # grey: PRD -1.0 (SM 18 no-op), benignity-only held/parent/INF ceilings = 0
    ExonDeletionOutcome.START_CODON_ALT_START_FUNCTIONAL: BranchSpec(
        "CDS", -1.0, 0.0, held_hi=0.0, parent_hi=0.0, inf_hi=0.0
    ),
}


def reference_score_exon_deletion(
    assessment: ExonDeletionAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Exon Deletion point total (SM 13, six branches).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). The whole-gene branch applies SM 18 mechanism-only
    (exon-relevance removed); the grey functional-alt-start branch is benignity-only.
    """
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
```

- [ ] **Step 4: Add the export** — `scoring/__init__.py`: add the import + `"reference_score_exon_deletion"` into the sorted `__all__` (alphabetical: after `ScoreResult`, before `reference_score_frameshift` — capital `S` sorts first, then `exon_deletion` < `frameshift`):

```python
from svcv4_model.scoring.pfd.exon_deletion import reference_score_exon_deletion
from svcv4_model.scoring.pfd.frameshift import reference_score_frameshift
...
__all__ = [
    "ScoreResult",
    "reference_score_exon_deletion",
    "reference_score_frameshift",
    "reference_score_nonsense",
    "reference_score_start_lost",
    "reference_score_stop_lost",
]
```

- [ ] **Step 5: Run** `uv run pytest tests/test_exon_deletion_scoring.py -q` — all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/pfd/exon_deletion.py tests/test_exon_deletion_scoring.py src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_score_exon_deletion (SM 13, 6 branches, mechanism-only whole-gene)"
```

---

## Task 3: Docs

**Files:** Modify `docs/reference/scoring.md`

- [ ] **Step 1: Extend the "What is modeled so far" list** — after the Stop-Lost line, add:

```markdown
- **Exon Deletion** (SM 13) — `reference_score_exon_deletion`, six branches (the whole-gene
  branch applies SM 18 mechanism-only; the grey functional-alt-start branch is benignity-only).
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (0 warnings).

- [ ] **Step 3: Commit** — `git commit -am "docs: note the Exon Deletion reference scorer"`

---

## Task 4: Full quality gates

- [ ] **Step 1:** `uv run pytest -q`; `uv run ruff check .`; drift gate; `mkdocs build --strict`; `uv run python scripts/export_schemas.py && git status --porcelain schemas/json` (empty); `git status --porcelain`. All clean except pre-existing untracked files.
- [ ] **Step 2:** Ready for code review + PR.

---

## Notes for the implementer

- Task 1 is behaviour-preserving — the five existing scoring test files are the guard. `mechanism_only`/`sm18_mechanism_only` default False everywhere; only whole-gene sets it True.
- The grey `BranchSpec` is byte-identical to the Start-Lost violet pattern (proven benignity ceilings).
- FXN stays consumed raw. Do NOT add scoring to the root `__all__` (schema). Line length 100.
