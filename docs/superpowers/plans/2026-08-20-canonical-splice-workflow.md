# Canonical Splice Variants (`SPL_`) Workflow Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the SVCv4 Canonical Splice variants workflow (SM 11) as `CanonicalSpliceAssessment`, after first hoisting the shared `Splice*` vocabulary out of `missense.py` into a new `splice.py` module (a verbatim, zero-schema-drift refactor).

**Architecture:** Two parts. **(A)** A **verbatim refactor**: the five already-generic `Splice*` types move from `missense.py` into a new `src/svcv4_model/splice.py`; `missense.py`, `tests/test_missense.py`, and `src/svcv4_model/__init__.py` update their import *sources* only. Because the classes move unchanged (same names, fields, docstrings), the generated JSON Schemas and `__all__` are byte-identical — proven by a clean `git diff -- schemas/json` before proceeding. **(B)** A new `src/svcv4_model/canonical_splice.py` with `CanonicalSpliceAssessment` (field-identical to `MissenseSpliceAssessment`, always `SPL_`), composing the shared splice vocabulary + SM 18/19/20. Standalone PFD payload — no `Case`, no `Workflow` enum entry; `case-model.md` untouched. One new committed JSON schema. Scoring documented, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv`, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-20-canonical-splice-workflow-design.md` (committed on this branch).

**Branch:** `feat/pfd-canonical-splice` (checked out; spec committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/splice.py` | The five shared `Splice*` types (moved verbatim) | Create |
| `src/svcv4_model/missense.py` | Delete the five moved classes; import them from `splice` | Modify |
| `tests/test_missense.py` | Import the five `Splice*` names from `splice` not `missense` | Modify |
| `src/svcv4_model/canonical_splice.py` | `CanonicalSpliceAssessment` (SM 11) | Create |
| `src/svcv4_model/__init__.py` | Move `Splice*` import source; add `CanonicalSpliceAssessment` | Modify |
| `tests/test_canonical_splice.py` | Unit tests for the new assessment | Create |
| `schemas/json/CanonicalSpliceAssessment.schema.json` | Generated (one new file) | Generate + `git add` |
| `docs/workflows/pfd/canonical-splice.md` | New workflow page | Create |
| `mkdocs.yml` | Add the new page to the PFD nav | Modify |
| `docs/workflows/pfd/index.md` | Add Canonical Splice to the modeled workflows | Modify |
| `docs/reference/spec-alignment.md` | SM 11 row → modeled | Modify |
| `docs/reference/known-gaps.md` | "Full PFD modeling" row → Canonical Splice done | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.CanonicalSpliceAssessment` | Modify |

---

## Chunk 1: The refactor (zero-drift) + the new workflow

### Task 1: Hoist the shared `Splice*` vocabulary into `splice.py` (verbatim refactor)

**Files:**
- Create: `src/svcv4_model/splice.py`
- Modify: `src/svcv4_model/missense.py`
- Modify: `src/svcv4_model/__init__.py`
- Modify: `tests/test_missense.py`

- [ ] **Step 1: Create `src/svcv4_model/splice.py` with the five classes moved verbatim**

Create `src/svcv4_model/splice.py`. The five class bodies below are **copied verbatim** from `missense.py` (currently lines 135–212) — do not alter any docstring, field, or the inline comment (that is what keeps the schemas byte-identical):

```python
"""SVCv4 shared splice vocabulary (PFD).

The splice prediction outcome, predictor, assay result, and the SPL_PRD /
SPL_SPA evidence models are shared by every PFD workflow that has a splice path —
the Missense splice half (SM 6) and Canonical Splice variants (SM 11). They are
capture-only; the per-workflow point values and splice-assay semantics are
documented on each workflow page, not computed here.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SplicePredictionOutcome(StrEnum):
    """The in-silico splice-prediction outcome selecting one of five paths (SM 6)."""

    NMD_PREDICTED = "NMD_PREDICTED"
    FRAMESHIFT_NO_NMD = "FRAMESHIFT_NO_NMD"
    SPLICE_NO_FRAMESHIFT = "SPLICE_NO_FRAMESHIFT"
    UNCERTAIN = "UNCERTAIN"
    UNLIKELY = "UNLIKELY"


class SplicePredictor(StrEnum):
    """An in-silico splice-effect predictor (SM 6)."""

    SPLICEAI = "SPLICEAI"
    PANGOLIN = "PANGOLIN"
    OTHER = "OTHER"


class SpliceAssayResult(StrEnum):
    """The qualitative degree of aberrant splice product in a splice assay (SM 6)."""

    NEAR_COMPLETE_OR_COMPLETE = "NEAR_COMPLETE_OR_COMPLETE"
    SUBSTANTIAL = "SUBSTANTIAL"
    INCOMPLETE_OR_NONE = "INCOMPLETE_OR_NONE"


class SplicePredictiveEvidence(BaseModel):
    """The splice predictive (SPL_PRD) step of a splice path (SM 6).

    Positive initial points (yellow/orange paths) are reduced by the SM 18
    mechanism/exon matrix; blue starts at 0.0 and violet at −1.0.
    """

    model_config = ConfigDict(extra="forbid")

    splice_predictor: SplicePredictor | None = Field(
        default=None, description="The in-silico splice predictor used (e.g. SpliceAI)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial SPL_PRD points before the SM 18 adjustment."
    )
    protein_fraction_altered: float | None = Field(
        default=None,
        description="Fraction of protein altered (orange paths' initial-points table).",
    )
    alternative_start_rescue: bool | None = Field(
        default=None,
        description="An alternative start codon rescues the 5' PTC (the −1.0 case).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded SPL_PRD points after the SM 18 adjustment."
    )
    # Note: the lower-orange path's protein-deletion in-silico tool input
    # (MutationTaster/Provean, +2.0 / −0.5; SM 6, not yet calibrated) folds into
    # ``initial_points`` for now rather than a dedicated field.


class SpliceAssayEvidence(BaseModel):
    """The splice-assay (SPL_SPA) step: RNA / minigene evidence for splicing (SM 6).

    Distinct from SM 20 functional evidence (which is SPL_FXN). Semantics vary by
    path: it scales SPL_PRD (yellow/orange), is additive (blue), or adds benignity
    (violet). Absent = SPL_SPA_ND.
    """

    model_config = ConfigDict(extra="forbid")

    assay_type: str | None = Field(
        default=None, description="Assay modality (e.g. RT-PCR, RNAseq, minigene)."
    )
    result: SpliceAssayResult | None = Field(
        default=None, description="Qualitative degree of the aberrant splice product."
    )
    calibrated: bool | None = Field(
        default=None,
        description="Whether an activity-threshold calibration allows adjusted scoring.",
    )
```

- [ ] **Step 2: Delete the five moved classes from `missense.py` and import them from `splice`**

In `src/svcv4_model/missense.py`, **delete** the five class definitions (`SplicePredictionOutcome`, `SplicePredictor`, `SpliceAssayResult`, `SplicePredictiveEvidence`, `SpliceAssayEvidence` — currently ~lines 135–212, the block ending just before `class MissenseSpliceAssessment`). Then **add** this import after the existing `from svcv4_model.mechanism import (...)` line (module order: `mechanism` < `splice`):

```python
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
)
```

(Only these three are referenced by `MissenseSpliceAssessment`; `SplicePredictor` and `SpliceAssayResult` are used solely inside the moved models, so `missense.py` does not import them.)

- [ ] **Step 3: Update the `Splice*` import source in `tests/test_missense.py`**

In `tests/test_missense.py`, **remove** the five `Splice*` names (`SpliceAssayEvidence`, `SpliceAssayResult`, `SplicePredictionOutcome`, `SplicePredictiveEvidence`, `SplicePredictor`) from the `from svcv4_model.missense import (...)` block, and **add** a new block:

```python
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)
```

(Leave all `Missense*` names importing from `svcv4_model.missense`.)

- [ ] **Step 4: Update the `Splice*` import source in `__init__.py`**

In `src/svcv4_model/__init__.py`, **remove** the five `Splice*` names from the `from svcv4_model.missense import (...)` block, and **add** a new import block **after** `from svcv4_model.proposition import Predicate, Proposition` and **before** `from svcv4_model.statement import Statement` (module order: `proposition` < `splice` < `statement`):

```python
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)
```

**Do not touch `__all__`** — the five `Splice*` names stay exactly where they are (only their import source changed).

- [ ] **Step 5: Format + lint the four touched files**

Run: `uv run ruff check --fix src/svcv4_model/splice.py src/svcv4_model/missense.py src/svcv4_model/__init__.py tests/test_missense.py && uv run ruff format --check src/svcv4_model/splice.py src/svcv4_model/missense.py src/svcv4_model/__init__.py tests/test_missense.py`
Expected: both clean (exit 0). `ruff check --fix` may re-sort import blocks; no unused-import (F401) should remain (missense.py still uses `StrEnum` for its own enums and `BaseModel`/`Field` for its own models).

- [ ] **Step 6: Run the full suite — everything still green**

Run: `uv run pytest -q`
Expected: **all tests pass** (the move is behavior-preserving; `test_missense.py` now imports `Splice*` from `splice`).

- [ ] **Step 7: Prove ZERO schema drift**

Run: `uv run python scripts/export_schemas.py && git status --porcelain schemas/json`
Expected: **empty output** — `SplicePredictiveEvidence.schema.json` and `SpliceAssayEvidence.schema.json` regenerate byte-identical (verbatim move), and no new/changed schema files appear. Then confirm the gate:
Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`. **If any schema shows as modified, the move was not verbatim — stop and diff the offending class against the original before continuing.**

- [ ] **Step 8: Commit the refactor on its own**

```bash
git add src/svcv4_model/splice.py src/svcv4_model/missense.py \
        src/svcv4_model/__init__.py tests/test_missense.py
git commit -m "refactor: hoist shared Splice* vocabulary into splice.py

Verbatim move of SplicePredictionOutcome/SplicePredictor/SpliceAssayResult/
SplicePredictiveEvidence/SpliceAssayEvidence out of missense.py into a shared
splice.py; import sources updated in missense.py, __init__.py, test_missense.py.
No schema or __all__ change (byte-identical).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Create `canonical_splice.py` with `CanonicalSpliceAssessment` (TDD)

**Files:**
- Create: `src/svcv4_model/canonical_splice.py`
- Create: `tests/test_canonical_splice.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_canonical_splice.py` (imports from `svcv4_model.canonical_splice`, which doesn't exist yet → collection fails):

```python
"""Tests for the SVCv4 Canonical Splice variants (SPL_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.canonical_splice import CanonicalSpliceAssessment
from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import InformativeVariant, InformativeVariantsEvidence, VariantClassification
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)


def _maximal_assessment() -> CanonicalSpliceAssessment:
    return CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(
            splice_predictor=SplicePredictor.SPLICEAI,
            initial_points=6.0,
            adjusted_points=6.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.ALL,
        ),
        splice_assay=SpliceAssayEvidence(
            assay_type="RNAseq",
            result=SpliceAssayResult.NEAR_COMPLETE_OR_COMPLETE,
            calibrated=False,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000111",
                    classification=VariantClassification.PATHOGENIC,
                )
            ]
        ),
        prd_points=6.0,
        spa_points=0.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_spa_combined=6.0,
        prd_spa_fxn_combined=8.0,
        spl_total=9.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = CanonicalSpliceAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = CanonicalSpliceAssessment()
    assert empty.prediction_outcome is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.splice_assay is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.spl_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        CanonicalSpliceAssessment(not_a_field=1)


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "CanonicalSpliceAssessment" in svcv4_model.__all__
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_canonical_splice.py -q`
Expected: collection **ERROR** — `ModuleNotFoundError: No module named 'svcv4_model.canonical_splice'`.

- [ ] **Step 3: Create the module**

Create `src/svcv4_model/canonical_splice.py` with exactly this content (from spec §5.2; longest line is under 100):

```python
"""SVCv4 Canonical Splice variants workflow (SM 11).

Variants of the essential GT donor (+1/+2) or AG acceptor (−2/−1) dinucleotides
resolve to the SPL_ parent code via one of five color paths (NMD / frameshift-no-NMD
/ no-frameshift / uncertain / unlikely), each running the shared splice pipeline —
predictive (SPL_PRD) → splice assay (SPL_SPA) → functional (SPL_FXN, SM 20) →
informative (SPL_INF, SM 19) → the capped SPL_ total. Structurally identical to the
missense splice half (SM 6); the point values and splice-assay semantics differ and
are documented, not computed.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
)


class CanonicalSpliceAssessment(BaseModel):
    """A canonical splice variant (SPL_) assessment (SM 11).

    One entity for all five color-paths, parameterized by ``prediction_outcome``;
    reuses the shared splice vocabulary and the SM 18/19/20 submodules. Permissive
    superset; the per-path pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: SplicePredictionOutcome | None = Field(
        default=None, description="Which of the five splice prediction paths applies."
    )
    predictive: SplicePredictiveEvidence | None = Field(
        default=None, description="The SPL_PRD splice-prediction step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    splice_assay: SpliceAssayEvidence | None = Field(
        default=None, description="SM 11 splice-assay evidence (SPL_SPA)."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (SPL_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (SPL_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded SPL_PRD point value.")
    spa_points: float | None = Field(default=None, description="Coded SPL_SPA point value.")
    fxn_points: float | None = Field(default=None, description="Coded SPL_FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded SPL_INF point value.")
    prd_spa_combined: float | None = Field(
        default=None, description="Held SPL_PRD + SPL_SPA combined value."
    )
    prd_spa_fxn_combined: float | None = Field(
        default=None, description="Held SPL_PRD + SPL_SPA + SPL_FXN combined value."
    )
    spl_total: float | None = Field(
        default=None, description="Capped SPL_ parent-code total for this path."
    )
```

- [ ] **Step 4: Format + lint the new files**

Run: `uv run ruff format src/svcv4_model/canonical_splice.py tests/test_canonical_splice.py && uv run ruff check --fix src/svcv4_model/canonical_splice.py tests/test_canonical_splice.py`
Expected: `ruff format` reports files unchanged (or reformats trivially — e.g. wrapping the long `informative` import in the test); `ruff check --fix` clean.

- [ ] **Step 5: Run the tests — expect only the package-root import test to fail**

Run: `uv run pytest tests/test_canonical_splice.py -q`
Expected: `test_importable_from_package_root` **FAILS** (name not yet in `svcv4_model.__all__`); all other tests **PASS** (they import from `svcv4_model.canonical_splice` directly).

- [ ] **Step 6: Commit the module + tests**

```bash
git add src/svcv4_model/canonical_splice.py tests/test_canonical_splice.py
git commit -m "feat: add Canonical Splice variants (SPL_) workflow module

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Export `CanonicalSpliceAssessment` from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Add the import**

In `src/svcv4_model/__init__.py`, add the import **before** the `from svcv4_model.case import (` block (module order: `canonical_splice` < `case`):

```python
from svcv4_model.canonical_splice import CanonicalSpliceAssessment
```

- [ ] **Step 2: Add the name to `__all__`, in sorted position**

Insert `"CanonicalSpliceAssessment"` **between `"AnimalModelType"` and `"Case"`** (`Animal` < `Canonical` < `Case`):

```python
    "AnimalModelType",
    "CanonicalSpliceAssessment",
    "Case",
```

- [ ] **Step 3: Verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: both clean.

- [ ] **Step 4: Run the full Canonical Splice test file — all green now**

Run: `uv run pytest tests/test_canonical_splice.py -q`
Expected: **all tests PASS**, including `test_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export Canonical Splice workflow from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Regenerate and commit the JSON schema

**Files:**
- Generate: `schemas/json/CanonicalSpliceAssessment.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: **one new** file — `CanonicalSpliceAssessment.schema.json`. No other schema changes (the moved `Splice*` classes' files are already byte-identical from Task 1).

- [ ] **Step 2: Confirm `git status` shows exactly one new untracked file**

Run: `git status --porcelain schemas/json`
Expected: one `??` line for `CanonicalSpliceAssessment.schema.json` only. **No modifications** to any existing schema. If any existing schema shows modified, stop and investigate.

- [ ] **Step 3: Verify the drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN` (the one new schema is untracked, so `git diff --quiet` ignores it; `case-model.md` unchanged).

- [ ] **Step 4: `git add` the new schema and commit**

```bash
git add schemas/json/CanonicalSpliceAssessment.schema.json
git commit -m "chore: generate Canonical Splice workflow JSON schema

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Documentation

**Files:**
- Create: `docs/workflows/pfd/canonical-splice.md`
- Modify: `mkdocs.yml`
- Modify: `docs/workflows/pfd/index.md`
- Modify: `docs/reference/spec-alignment.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`

- [ ] **Step 1: Create the Canonical Splice workflow page**

Create `docs/workflows/pfd/canonical-splice.md`:

```markdown
# Canonical Splice variants (`SPL_`)

**Canonical splice variants** alter the essential `GT` donor (`+1`/`+2`) or `AG`
acceptor (`−2`/`−1`) dinucleotides. SVCv4 (Supplementary Material 11) routes each
VBC down **one** of five color paths — the *same five* the
[Missense](missense.md) splice half uses — all resolving to the **`SPL_`** parent
code via the shared pipeline: **SPL_PRD** (prediction) → **SPL_SPA** (splice assay)
→ **SPL_FXN** (functional, SM 20) → **SPL_INF** (informative, SM 19) → the capped
`SPL_` total. Modeled as one `CanonicalSpliceAssessment` (`prediction_outcome` =
`SplicePredictionOutcome`); each step is **documented, not computed**.

!!! note "Modeled here — inputs captured"

    `CanonicalSpliceAssessment` reuses the shared splice vocabulary
    (`SplicePredictionOutcome`, `SplicePredictiveEvidence`, `SpliceAssayEvidence`) —
    the same types the missense splice half uses. Only the point values and the
    splice-assay direction differ (documented below), so the *structure* is shared.

| Path (`prediction_outcome`) | Splice prediction | SPL_PRD initial | SPL_ total |
|---|---|---|---|
| `NMD_PREDICTED` (yellow) | frameshift + NMD | `+6.0` | `−8.0 to +10.0` |
| `FRAMESHIFT_NO_NMD` (upper orange) | frameshift, no NMD | `−1.0 to +6.0` | `−8.0 to +10.0` |
| `SPLICE_NO_FRAMESHIFT` (lower orange) | no frameshift, no NMD | `−1.0 to +6.0` | `−8.0 to +10.0` |
| `UNCERTAIN` (blue) | uncertain | `0.0` | `−8.0 to +8.0` |
| `UNLIKELY` (violet) | unlikely | `−1.0` | `−8.0 to 0.0` |

### Predictive (`SPL_PRD_`)

Positive initial points (yellow/orange) are reduced by the
[Molecular Mechanism & Exon Relevance](index.md#molecular-mechanism-exon-relevance-modeled-inputs)
matrix (SM 18); blue and violet skip it. The yellow branch awards a fixed **+6.0**
for a predicted NMD event (note: the missense splice half awards +3.0 here — the
canonical prior is higher). The orange branches read `−1.0 to +6.0` from a
critical-amino-acid table (the lower-orange path may fold in a protein-deletion
in-silico tool, `+0.5` / `−0.5`).

### Splice assay (`SPL_SPA_`)

`SpliceAssayEvidence` captures RNA / minigene / RT-PCR evidence. Its semantics
differ by path — and, for yellow/orange, differ from the missense splice half: here
the assay **reduces** the SPL_PRD evidence (near-complete → 0; substantial → −25%;
incomplete/none → −100% of SPL_PRD), rather than scaling it up. For blue it is
**additive** (`−2.0 to +2.0`); for violet it adds **benignity** (`−2.0 to 0.0`,
with the held PRD+SPA capped `−3.0 to 0.0`). Canonical splice permits patient-sample
splice data on the yellow/orange paths (unlike blue/violet) because of the high
prior that a canonical variant disrupts splicing.

### Functional (`SPL_FXN_`) and informative (`SPL_INF_`)

`SPL_FXN` reuses the generic [Functional Assays](index.md#functional-assays-modeled-inputs)
module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0` (capped `−8.0 to 0.0` on the
violet path). `SPL_INF` reuses the generic
[Informative Variants](index.md#informative-variants-modeled-inputs) module
(`InformativeVariantsEvidence`, SM 19): +2.0 first P / +1.0 first LP / +1.0 each
additional (negatives for B/LB), coded `−8.0 to +8.0` — the **violet path restricts
it to B/LB only**. P/LP informative variants must have the same predicted event and a
VBC prediction of similar-or-higher strength.

### Held combined values and the `SPL_` total

Per SM 11, the model records **both** the separate coded values and the two held
combined values (`prd_spa_combined` = SPL_PRD + SPL_SPA; `prd_spa_fxn_combined` =
SPL_PRD + SPL_SPA + SPL_FXN), then the capped parent `SPL_` total (`spl_total`),
whose range depends on the path (table above). **Gain-of-function** splice effects
are out of scope in SM 11.
```

- [ ] **Step 2: Add the page to the mkdocs nav**

In `mkdocs.yml`, under the PFD nav section, add the Canonical Splice page after In-Frame InDel. Change:

```yaml
          - Frameshift (NUL_/CDS_): workflows/pfd/frameshift.md
          - In-Frame InDel (CDS_): workflows/pfd/inframe-indel.md
```

to:

```yaml
          - Frameshift (NUL_/CDS_): workflows/pfd/frameshift.md
          - In-Frame InDel (CDS_): workflows/pfd/inframe-indel.md
          - Canonical Splice (SPL_): workflows/pfd/canonical-splice.md
```

- [ ] **Step 3: Add Canonical Splice to the closing note in `pfd/index.md`**

In `docs/workflows/pfd/index.md`, replace the closing paragraph:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). Four
per-variant-type workflows are modeled: the full [Missense](missense.md) workflow
(the `MIS_` amino-acid path, the `SPL_` splice paths, and the `MIS_`-vs-`SPL_`
comparison), the [Nonsense](nonsense.md) workflow (`NUL_`/`CDS_`, three branches),
the [Frameshift](frameshift.md) workflow (`NUL_`/`CDS_`, five branches), and the
[In-Frame InDel](inframe-indel.md) workflow (`CDS_`, two branches). The remaining
variant-type workflows and Determining Critical Amino Acids (SM 7) are still to
come.
```

with:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). Five
per-variant-type workflows are modeled: the full [Missense](missense.md) workflow
(the `MIS_` amino-acid path, the `SPL_` splice paths, and the `MIS_`-vs-`SPL_`
comparison), the [Nonsense](nonsense.md) workflow (`NUL_`/`CDS_`, three branches),
the [Frameshift](frameshift.md) workflow (`NUL_`/`CDS_`, five branches), the
[In-Frame InDel](inframe-indel.md) workflow (`CDS_`, two branches), and the
[Canonical Splice](canonical-splice.md) workflow (`SPL_`, five color paths). The
remaining variant-type workflows and Determining Critical Amino Acids (SM 7) are
still to come.
```

- [ ] **Step 4: Update the SM 11 row in `spec-alignment.md`**

In `docs/reference/spec-alignment.md`, replace the SM 11 row:

```markdown
| 11 | [Canonical Splice Variants](https://docs.google.com/document/d/1LGSPW90-n0EbqGjfLKQ2MpTHPK8Ai-hUuMAkqqhyi80/edit) | `SPL_*` | Not yet modeled |
```

with:

```markdown
| 11 | [Canonical Splice Variants](https://docs.google.com/document/d/1LGSPW90-n0EbqGjfLKQ2MpTHPK8Ai-hUuMAkqqhyi80/edit) | `SPL_*` | **Modeled (inputs)** — `CanonicalSpliceAssessment` captures the five color paths → `SPL_`, reusing the shared `Splice*` vocabulary (hoisted to `splice.py`) and SM 18/19/20; the criticality axis (SM 7) is deferred. See [Canonical Splice](../workflows/pfd/canonical-splice.md) |
```

- [ ] **Step 5: Update the "Full PFD modeling" row in `known-gaps.md`**

In `docs/reference/known-gaps.md`, replace the current row:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), the **complete Missense workflow** (`MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`, `MissenseAssessment`), the **Nonsense workflow** (`NonsenseAssessment`, three branches), the **Frameshift workflow** (`FrameshiftAssessment`, five branches → `NUL_`/`CDS_`), and the **In-Frame InDel workflow** (`InframeIndelAssessment`, two branches → `CDS_`) are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

with:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), the **complete Missense workflow** (`MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`, `MissenseAssessment`), the **Nonsense workflow** (`NonsenseAssessment`, three branches), the **Frameshift workflow** (`FrameshiftAssessment`, five branches → `NUL_`/`CDS_`), the **In-Frame InDel workflow** (`InframeIndelAssessment`, two branches → `CDS_`), and the **Canonical Splice workflow** (`CanonicalSpliceAssessment`, five color paths → `SPL_`, reusing the shared `Splice*` vocabulary) are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

- [ ] **Step 6: Append the model.md entry**

In `docs/reference/model.md`, after the **last** `::: svcv4_model.InframeIndelAssessment` entry, append:

```markdown

---

::: svcv4_model.CanonicalSpliceAssessment
```

- [ ] **Step 7: Build the docs strictly**

Run: `uv run mkdocs build --strict 2>&1 | tail -20`
Expected: `Documentation built…` with **no** WARNING lines. The new page must be in the nav (Step 2). The `index.md#…` anchors and `missense.md` link all resolve; if strict flags a broken link, read the warning and fix it. (Use inline notes, not `[^...]` footnotes — the repo does not enable the `footnotes` markdown extension.)

- [ ] **Step 8: Commit the docs**

```bash
git add docs/workflows/pfd/canonical-splice.md mkdocs.yml docs/workflows/pfd/index.md \
        docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: document the Canonical Splice variants (SPL_) workflow

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Full quality gates

**Files:** none (verification only)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -q`
Expected: all tests pass (existing suite after the refactor + new `tests/test_canonical_splice.py`).

- [ ] **Step 2: Lint + format**

Run: `uv run ruff check && uv run ruff format --check .`
Expected: both clean (exit 0).

- [ ] **Step 3: Schema/case-view drift gate**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`.

- [ ] **Step 4: Strict docs build**

Run: `uv run mkdocs build --strict 2>&1 | tail -5`
Expected: built with no warnings.

- [ ] **Step 5: Confirm a clean tree**

Run: `git status --porcelain`
Expected: only pre-existing untracked files unrelated to this work (`docs/Docsite Review Plan.md`, `docs/phenopackets-case-mapping.pptx`, `docs/superpowers/context/`). Nothing from this increment left uncommitted.

---

## Definition of done

- The five `Splice*` types live in `splice.py`; `missense.py` / `__init__.py` / `test_missense.py` import them from there; **no schema or `__all__` change** from the move.
- `CanonicalSpliceAssessment` importable from `svcv4_model`, all-optional, `extra="forbid"`, field-identical to `MissenseSpliceAssessment`.
- One new committed JSON schema; no existing schema changed; `case-model.md` untouched.
- New `pfd/canonical-splice.md` page in the nav; PFD overview lists it; spec-alignment/known-gaps/model docs updated.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR for the refactor + the Canonical Splice workflow, run the `code-review` skill on the diff, address findings, then merge on request. The remaining variant-type workflows (Intronic/Synonymous SM 12, Start/Stop loss SM 15/16, Exon del/dup SM 13/14) and SM 7 Critical Amino Acids remain on the backlog.
