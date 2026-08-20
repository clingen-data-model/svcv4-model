# Nonsense Variants (`NUL_`/`CDS_`) Workflow — Design Spec

**Date:** 2026-08-20
**Status:** Proposed
**Builds on:** the PFD scaffold (`PfdCodeAssessment`, #32), the three shared
submodules SM 18/19/20, and the Missense workflow (the composition precedent).
Same **capture + document, do not compute** stance.

## 1. Purpose & goal

Model the SVCv4 **Nonsense variants** workflow (SM 8) — the second per-variant-type
workflow. Nonsense variants resolve to a `NUL_` or `CDS_` parent code via one of
**three branches** selected by two attributes: whether NMD is predicted, and
whether an alternative-Met rescue codon has evidence.

Scope is capture-only: model the analyst's inputs along whichever branch applies,
and document each branch's pipeline (PRD → FXN → INF → parent total), its point
ranges, and the branch selection; compute no points.

## 2. Source material

- **Supplementary Material 8 (Nonsense)**, verbatim in
  `source-material/svcv4-supplements/SM08-nonsense.txt` — the three branches, the
  point ranges, and the pipeline.
- **Existing architecture:** `src/svcv4_model/missense.py` (the per-variant-type
  precedent), `pfd.py` (`PfdParentCode`), `mechanism.py`
  (`MechanismExonRelevanceEvidence`), `functional.py` (`FunctionalAssayEvidence`),
  `informative.py` (`InformativeVariantsEvidence`).

## 3. Key findings driving this work

### 3.1 Three branches, one shared pipeline

The flow diagram (SM 8 Fig. 1) has three mutually-exclusive branches, chosen per
VBC per MDE:

- **yellow** — NMD predicted, **no** alternative-Met rescue → parent code **`NUL_`**;
- **orange** — NMD predicted **but** an alternative-Met rescue codon has evidence →
  parent code **`CDS_`**;
- **violet** — **not** predicted to cause NMD → parent code **`CDS_`**.

All three run the same steps — **PRD** (predictive) → **FXN** (functional, SM 20) →
**INF** (informative, SM 19) → **parent** total — with no splice-assay step and no
dual-path comparison (simpler than the Missense splice paths). This is modeled as
**one** `NonsenseAssessment` parameterized by a `NonsensePredictionOutcome` enum;
the parent code is the reused `PfdParentCode` (`NUL`/`CDS`).

### 3.2 Per-branch PRD initial points

- **yellow (`NUL_PRD_`):** a fixed **+6.0** initial (NMD predicted), then reduced by
  the SM 18 mechanism/exon matrix → `NUL_PRD_ 0.0 to +6.0`.
- **orange (`CDS_PRD_`):** an initial from a protein-fraction / critical-amino-acid
  table (`−1.0 to +6.0`; `−1.0` if the alternative start yields normal function),
  then the SM 18 matrix on positive points → `CDS_PRD_ −1.0 to +6.0`.
- **violet (`CDS_PRD_`):** an initial from the same fraction/criticality table
  (`0.0 to +6.0`), then the SM 18 matrix → `CDS_PRD_ 0.0 to +6.0`.

The **criticality of deleted amino acids** alternative (orange/violet) leans on
SM 7/11 Critical Amino Acids (not yet modeled), so `NonsensePredictiveEvidence`
captures `protein_fraction_reduced` + `alternative_met_rescue` now and **defers**
the critical-domain criticality flag to the SM 7 increment (mirroring the deferred
missense motif variant).

### 3.3 FXN and INF reuse the shared submodules

FXN is the generic SM 20 module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0`;
the held PRD+FXN combined is capped `−8.0 to +10.0` (yellow) or `−8.0 to +9.0`
(orange/violet). INF is the generic SM 19 pattern (`InformativeVariantsEvidence`):
same-exon PTC (nonsense/frameshift) variants with the same NMD consequence
(+2.0 first P / +1.0 first LP / +1.0 each additional; negatives for B/LB), coded
`−8.0 to +8.0`. SM 8 notes the INF *position* criteria differ subtly per branch
(same-exon same-NMD for yellow; between VBC and alt start for orange; PTC
downstream of VBC for violet) — a documented eligibility nuance, not separate
fields.

### 3.4 One held combined value; parent totals

Per SM 8, the model records **both** the separate coded values and the one held
`PRD + FXN` combined value (no distinct code). The parent total is coded `NUL_ −8.0
to +10.0` (yellow) or `CDS_ −8.0 to +10.0` (orange/violet). (SM 8 L53 has a source
typo naming `NUL_` under the orange `CDS_` summing step; L47 and the section
heading give `CDS_` — the model follows `CDS_`.) Gain-of-function truncation effects
are explicitly out of scope in SM 8.

### 3.5 A standalone assessment mirroring the scaffold

`NonsenseAssessment` mirrors `PfdCodeAssessment`'s shape but swaps in the typed
`NonsensePredictiveEvidence` and adds the branch selector, reusing the three shared
submodules. Standalone PFD payload — **no** `Workflow` enum entry, no applicability
matrix; `case-model.md` unaffected.

## 4. Scope

**In scope:**

- New module `src/svcv4_model/nonsense.py`: `NonsensePredictionOutcome` enum;
  `NonsensePredictiveEvidence`, `NonsenseAssessment` models (§5.1).
- Export the three public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — two new files (§5.3).
- Docs: new `docs/workflows/pfd/nonsense.md` (+ nav + link from `pfd/index.md`),
  `spec-alignment.md` SM 8 row, `known-gaps.md` PFD row, `model.md` (§5.4).
- Tests: new `tests/test_nonsense.py` (§5.5).

**Out of scope / deferred:**

- The critical-domain criticality flag (with SM 7/11 Critical Amino Acids).
- Gain-of-function truncation variants (SM 8 excludes them).
- All point computation (per-branch ranges, the SM 18 reduction, sums).

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/nonsense.py`

```python
"""SVCv4 Nonsense variants workflow (SM 8).

Nonsense variants resolve to a NUL_ or CDS_ parent code via one of three branches
selected by whether NMD is predicted and whether an alternative-Met rescue codon
has evidence: NMD + no rescue → NUL_; NMD + rescue → CDS_; no NMD → CDS_. All three
run the same pipeline — predictive (PRD) → functional (FXN, SM 20) → informative
(INF, SM 19) → parent total — with the SM 18 mechanism/exon matrix applied to the
predictive points. This module captures the analyst's inputs; the scoring is
documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class NonsensePredictionOutcome(StrEnum):
    """Which of the three nonsense branches applies to the VBC (SM 8)."""

    NMD_NO_RESCUE = "NMD_NO_RESCUE"
    NMD_WITH_RESCUE = "NMD_WITH_RESCUE"
    NO_NMD = "NO_NMD"


class NonsensePredictiveEvidence(BaseModel):
    """The nonsense predictive (PRD) step of a nonsense branch (SM 8).

    NMD-predicted (yellow) starts at a fixed +6.0; the rescue (orange) and no-NMD
    (violet) branches derive initial points from the fraction of protein lost.
    Positive points are reduced by the SM 18 mechanism/exon matrix.
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None, description="Predictive basis (e.g. NMD prediction; PTC position)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial PRD points before the SM 18 adjustment."
    )
    protein_fraction_reduced: float | None = Field(
        default=None,
        description="Fraction of protein lost (the orange/violet initial-points table).",
    )
    alternative_met_rescue: bool | None = Field(
        default=None,
        description="Evidence an alternative-Met start codon rescues function (orange branch).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class NonsenseAssessment(BaseModel):
    """A nonsense variant (NUL_/CDS_) assessment (SM 8).

    One entity for all three branches, parameterized by ``prediction_outcome``;
    reuses the SM 18/19/20 submodules and the shared ``PfdParentCode`` (NUL/CDS).
    Permissive superset; the per-branch pipeline and its caps are documented, not
    computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: NonsensePredictionOutcome | None = Field(
        default=None, description="Which of the three nonsense branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL for yellow; CDS otherwise)."
    )
    predictive: NonsensePredictiveEvidence | None = Field(
        default=None, description="The PRD predictive step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded PRD point value.")
    fxn_points: float | None = Field(default=None, description="Coded FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded INF point value.")
    prd_fxn_combined: float | None = Field(
        default=None, description="Held PRD + FXN combined value (no distinct code)."
    )
    parent_total: float | None = Field(
        default=None, description="Capped parent-code total (NUL_/CDS_ −8.0 to +10.0)."
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `from svcv4_model.nonsense import (...)` in module order — `nonsense` sorts
**after `missense`** and **before `pfd`** (`missense` < `nonsense` < `pfd`). Export
`NonsenseAssessment`, `NonsensePredictionOutcome`, `NonsensePredictiveEvidence` and
add them to `__all__` in sorted position — all three `Nonsense…` names sort
**after `MolecularMechanism`** and **before `PfdCodeAssessment`** (`Mo` < `No` <
`Pf`). Confirm with `sorted()` at implementation time. `__all__` is hand-sorted
(ruff does not sort it). The enum gets no schema file; the two `BaseModel`s do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **two** new files —
`NonsenseAssessment.schema.json` (which `$ref`s `NonsensePredictiveEvidence`, the
reused `MechanismExonRelevanceEvidence` / `FunctionalAssayEvidence` /
`InformativeVariantsEvidence`, and the `NonsensePredictionOutcome` / `PfdParentCode`
enums under `$defs`) and `NonsensePredictiveEvidence.schema.json`. **`git add`
both** — the drift gate does not flag untracked files. `export_case_views.py` and
`case-model.md` are unaffected (no `Workflow` entry). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/nonsense.md`** (new) — the Nonsense workflow page. Document
  the three branches (a table: branch → NMD? / rescue? → parent code → PRD initial
  → parent total), the shared PRD → FXN → INF → parent pipeline, the SM 18 matrix
  reduction, the SM 20 (FXN) and SM 19 (INF) reuse with the per-branch INF position
  nuance, the one held PRD+FXN value, and the GoF-out-of-scope note — all
  *documented, not computed*. **Surface the held-combined cap nuance**: the held
  `PRD+FXN` cap is `+10.0` for yellow but `+9.0` for orange/violet, even though all
  three *parent* totals cap at `+10.0`. **Note the SM cross-reference divergence**:
  SM 8's text cites "Supplementary Material 11" for Critical Amino Acids, but this
  repo's [Spec coverage](../../reference/spec-alignment.md) canonically maps Critical
  Amino Acids to **SM 7** (SM 11 = Canonical Splice Variants) — treat SM 7 as the
  reference, deferred.
- **`mkdocs.yml`** — add `- Nonsense (NUL_/CDS_): workflows/pfd/nonsense.md` under
  the PFD nav section (after `workflows/pfd/missense.md`).
- **`docs/workflows/pfd/index.md`** — in the scaffold section's closing note, add
  Nonsense to the modeled per-variant-type workflows alongside Missense. **Also fix
  the stale text**: the note currently says the Missense splice (`SPL_`) paths and
  the `MIS_`-vs-`SPL_` comparison are "still to come" — they shipped (#34/#35), so
  update it to state the full Missense workflow and Nonsense are modeled, with the
  remaining variant types + SM 7 still to come.
- **`docs/reference/spec-alignment.md`** — SM 8 row: from "Not yet modeled" to
  "Modeled (inputs) — `NonsenseAssessment` (three branches → NUL_/CDS_, reusing
  SM 18/19/20)".
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: Nonsense now
  joins Missense as a modeled variant-type workflow.
- **`docs/reference/model.md`** — add `::: svcv4_model.NonsenseAssessment` after the
  `MissenseAssessment` entry.

### 5.5 Tests: `tests/test_nonsense.py`

- Round-trip a maximal `NonsenseAssessment` (a `prediction_outcome`, `parent_code`,
  a `NonsensePredictiveEvidence`, a `MechanismExonRelevanceEvidence`, a
  `FunctionalAssayEvidence`, an `InformativeVariantsEvidence`, all point fields
  including the combined) through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields on both models.
- Each `NonsensePredictionOutcome` value round-trips; a `PfdParentCode` value
  (`NUL`/`CDS`) round-trips on `parent_code`.
- The three new names are importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_nonsense.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the two new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes (new page in nav; no broken links).

## 7. Follow-up backlog

1. The critical-domain criticality flag with **SM 7/11** Critical Amino Acids
   (shared with the deferred missense motif variant).
2. The remaining variant-type workflows (Frameshift, Canonical Splice, In-Frame
   InDel, Start/Stop loss, Exon del/dup, …) — several reuse `NUL_`/`CDS_`.
3. The full PFD scoring computation.

## 8. Delivery

Branch `feat/pfd-nonsense` off `main`. Single PR for this workflow. CI: pytest,
ruff, the schema/docs drift gate, `mkdocs build --strict`.
