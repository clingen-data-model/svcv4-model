# PFD Scaffold (`PfdCodeAssessment`) — Design Spec

**Date:** 2026-08-16
**Status:** Proposed
**Builds on:** the three shipped PFD shared submodules — SM 18
`MechanismExonRelevanceEvidence` (#28), SM 19 `InformativeVariantsEvidence`
(#29), SM 20 `FunctionalAssayEvidence` (#30) — and the earlier capture-only
increments. Same **capture + document, do not compute** stance.

## 1. Purpose & goal

The three PFD shared submodules are modeled. This pass builds the **variant-
agnostic scaffold** that composes them into one evidence assessment per **parent
code** — the reusable structure every PFD variant-type workflow (Missense,
Nonsense, Splice, …) instantiates. It is the first of a two-part effort: this
generic scaffold now, the **Missense** workflow (typed predictor/path enums, the
dual MIS/SPL path) as the next increment.

Scope is capture-only: model the assessment structure and document the pipeline
(PRD → SM 18 adjustment → FXN → INF → parent total) and its caps; compute no
points.

## 2. Source material (this pass)

- **Supplementary Material 6 (Missense)** and **Supplementary Material 1
  (Glossary)**, verbatim in `source-material/svcv4-supplements/` (gitignored) —
  the parent-code/sub-code structure, point ranges, and the pipeline shape.
- **Existing architecture:** `src/svcv4_model/mechanism.py`,
  `src/svcv4_model/functional.py`, `src/svcv4_model/informative.py` (the three
  submodule payloads this scaffold embeds); `src/svcv4_model/population.py`
  (the standalone typed-payload precedent); `scripts/export_schemas.py`;
  `docs/workflows/pfd/index.md` (three modeled submodule subsections to build on).

## 3. Key findings driving this work

### 3.1 Every PFD workflow shares one pipeline that yields a parent code

Parent codes: `NUL` (null/LoF), `CDS` (coding sequence), `SPL` (splice), `MIS`
(missense) — plus `NCG`, `REG` named in the glossary. Each is produced by the
same pipeline of sub-codes: **`_PRD`** (in-silico prediction) → adjusted by
**SM 18** (transcript relevance / mechanism × exon-relevance) → **`_FXN`**
(functional, SM 20) → **`_INF`** (informative, SM 19) → **parent-code total**,
with a splice-only **`_SPA`** (splice-assay) step for the `SPL` path. Parent
totals are capped (SM 6 gives `MIS_` −8.0 to +9.0 and `SPL_` −8.0 to +10.0; the
`NUL_`/`CDS_` ranges live in SM 8+), and each sub-code and intermediate has its
own cap.

### 3.2 Software must record separate *and* combined values

Verbatim (SM 6): "there is not a distinct evidence code for the combination of
(`MIS_PRD_` and `MIS_FXN_`) points, this number is just held until the next step.
Variant curation software should record both the separate and combined values."
The scaffold captures the **separate coded sub-code values** (`prd`/`spa`/`fxn`/
`inf` points) and the **parent total**. The path-specific *combined-held*
intermediates (e.g. PRD+FXN for missense vs PRD+SPA+FXN for splice) are deferred
to the variant-type increments, where the exact combination sequence is known.

### 3.3 Compose the submodules by embedding

The scaffold embeds the three submodule payloads as optional fields (like `Case`
embeds its sub-models), rather than referencing them by id. This is the simplest
capture-only shape and matches the existing composition style. It is a standalone
PFD payload — **not** part of `Case`, no `Workflow` enum entry, no applicability
matrix; `case-model.md` is unaffected.

### 3.4 A generic PRD sub-model, typed later

The PRD step is variant-type-specific in its inputs (missense: a single approved
predictor + transcript relevance; nonsense: NMD prediction + % protein; splice:
SpliceAI delta), but shares a shape: an initial score/points, an SM 18
adjustment, a path/color, and the resulting coded `_PRD` value. The scaffold's
`PfdPredictiveEvidence` captures that shape generically (`predictor`/`path_label`
as free strings); the Missense increment adds the typed 7-predictor enum and
color-path enum.

## 4. Scope

**In scope:**

- New module `src/svcv4_model/pfd.py`: `PfdParentCode` enum,
  `PfdPredictiveEvidence`, `PfdCodeAssessment` (§5.1).
- Export the three public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — two new files (§5.3).
- Docs: `pfd/index.md` (scaffold section), `known-gaps.md` (PFD row), `model.md`
  (§5.4).
- Tests: new `tests/test_pfd.py` (§5.5).

**Out of scope / deferred:**

- The typed predictor & path enums; the dual MIS/SPL path + "take the higher"
  rule (the Missense increment).
- The path-specific combined-held point fields; the `SPL_SPA` splice-assay
  evidence entity.
- All point computation (caps, sums, adjustments).
- The other variant-type workflows and SM 7 Critical Amino Acids.

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/pfd.py`

```python
"""SVCv4 PFD scaffold — the shared, variant-agnostic assessment structure.

Every PFD variant-type workflow (missense, nonsense, splice, …) produces a
parent-code score from the same pipeline: predictive (PRD) → adjust by molecular
mechanism / exon relevance (SM 18) → functional (SM 20) → informative (SM 19) →
parent-code total, with a splice-only splice-assay (SPA) step. This module
captures one parent code's assessment, embedding the three shared submodules;
the scoring (see docs/workflows/pfd/index.md) is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence


class PfdParentCode(StrEnum):
    """The PFD parent evidence code a variant-type workflow resolves to (SM 1)."""

    NUL = "NUL"
    CDS = "CDS"
    SPL = "SPL"
    MIS = "MIS"
    NCG = "NCG"
    REG = "REG"


class PfdPredictiveEvidence(BaseModel):
    """The predictive (PRD) step of a PFD assessment.

    Variant-type-agnostic shape: an in-silico prediction, its SM 18 transcript-
    relevance / mechanism adjustment, and the resulting coded ``_PRD`` value.
    Typed predictor/path enums arrive with the per-variant-type workflows.
    """

    model_config = ConfigDict(extra="forbid")

    predictor: str | None = Field(
        default=None, description="In-silico predictor or basis used (e.g. REVEL, NMD prediction)."
    )
    raw_score: float | None = Field(
        default=None, description="The predictor's raw score, if applicable."
    )
    initial_points: float | None = Field(
        default=None, description="Initial evidence points before the SM 18 adjustment."
    )
    path_label: str | None = Field(
        default=None, description="Flow-diagram path/color (e.g. GREEN, YELLOW); typed later."
    )
    transcript_relevance_applied: bool | None = Field(
        default=None,
        description="Whether the SM 18 transcript-relevance step reduced the points.",
    )
    mechanism_applied: bool | None = Field(
        default=None,
        description=(
            "Whether the SM 18 mechanism step applied (not for the missense "
            "amino-acid path, where predictors capture both LoF and GoF)."
        ),
    )
    adjusted_points: float | None = Field(
        default=None,
        description="Coded _PRD points after the SM 18 adjustment.",
    )


class PfdCodeAssessment(BaseModel):
    """One PFD parent-code assessment: the shared pipeline's captured inputs.

    Embeds the three shared submodules (SM 18/19/20) and captures the coded
    sub-code point values and the parent total. Permissive superset; the scoring
    (the pipeline, its caps, the held separate+combined values, the _ND coding)
    is documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    parent_code: PfdParentCode | None = Field(
        default=None, description="The parent evidence code this assessment resolves to."
    )
    predictive: PfdPredictiveEvidence | None = Field(
        default=None, description="The predictive (_PRD) step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded _PRD point value.")
    spa_points: float | None = Field(
        default=None, description="Coded _SPA (splice-assay) point value; splice paths only."
    )
    fxn_points: float | None = Field(default=None, description="Coded _FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded _INF point value.")
    parent_total: float | None = Field(
        default=None, description="Capped parent-code total for this assessment."
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `from svcv4_model.pfd import (...)` in module order (`pfd` sorts after
`method`/`mechanism` and before `population` — `pfd` < `population` at char 2,
`f` < `o`; and after `method`/`mechanism`). Export `PfdCodeAssessment`,
`PfdParentCode`, `PfdPredictiveEvidence` in the imports and `__all__` (ASCII order
— or run `ruff check --fix`). The enum gets no schema file; the two `BaseModel`s
do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes two new files —
`PfdCodeAssessment.schema.json` (which `$ref`s the embedded submodule models,
`PfdPredictiveEvidence`, and the `PfdParentCode` enum under `$defs` — Pydantic v2
emits enum-typed fields as a `$def` + `$ref`, not inlined) and
`PfdPredictiveEvidence.schema.json`. The embedded submodules' own existing schema
files are regenerated identically (independent of `pfd`). **`git add` both** —
the drift gate does not flag a forgotten untracked file. `export_case_views.py`
and `case-model.md` are
**unaffected** (no `Workflow` entry). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/index.md`** — after the three modeled submodule
  subsections, add a "### PFD scaffold ✅ modeled (inputs)" section: the shared
  `PfdCodeAssessment` ties one parent code's pipeline together — a `predictive`
  (`_PRD`) step, the three embedded submodules (SM 18/19/20), the coded sub-code
  point values (`prd`/`spa`/`fxn`/`inf`) and the `parent_total`. Document the
  pipeline order and caps, the "record separate **and** combined values" rule,
  and the `_ND` coding — all *documented, not computed*. Note the typed
  predictor/path enums and the dual-path (missense) come with the per-variant-type
  workflows. **Also flip the two in-page notes that would otherwise contradict the
  new section:** the top "Modeling underway" admonition and the closing "still to
  come" paragraph both currently list the PRD/FXN/INF scaffold + parent codes as
  not-yet-done — move the scaffold out of both, leaving only the per-variant-type
  workflows + SM 7 as remaining.
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: the shared
  scaffold (`PfdCodeAssessment`) now joins the three submodules; remaining = the
  per-variant-type workflows (Missense first), SM 7, the combined-held /
  `SPL_SPA` structuring, and the scoring computation.
- **`docs/reference/model.md`** — add `::: svcv4_model.PfdCodeAssessment` after
  the last entry.

### 5.5 Tests: `tests/test_pfd.py`

- Round-trip a maximal `PfdCodeAssessment` (all point fields set, and each of the
  three embedded submodules populated with a representative instance, plus a
  `PfdPredictiveEvidence`) through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates (`parent_code is None`, embedded fields `None`);
  `extra="forbid"` rejects unknown fields on both `PfdCodeAssessment` and
  `PfdPredictiveEvidence`.
- Each `PfdParentCode` value round-trips.
- Importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_pfd.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the two new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes.

## 7. Follow-up backlog

1. **Missense workflow** (next increment): the typed 7-predictor enum + color-path
   enum, the dual MIS/SPL path with the "take the higher" rule, missense `_INF`
   Grantham categories.
2. The other variant-type workflows (Nonsense, Frameshift, Splice, …) + SM 7.
3. The path-specific combined-held point fields and the `SPL_SPA` splice-assay
   evidence entity.
4. The full PFD scoring computation (caps, sums, SM 18 adjustment) with the
   deferred rule/method enforcement.

## 8. Delivery

Branch `feat/pfd-scaffold-missense` off `main` (scaffold ships first; the Missense
workflow follows on a later branch). Single PR for this increment. CI: pytest,
ruff, the schema/docs drift gate, `mkdocs build --strict`.
