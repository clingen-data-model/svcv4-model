# Frameshift Variants (`NUL_`/`CDS_`) Workflow — Design Spec

**Date:** 2026-08-20
**Status:** Proposed
**Builds on:** the Nonsense workflow (`NonsenseAssessment`, #36 — the direct
structural precedent), the PFD scaffold, and SM 18/19/20. Same **capture +
document, do not compute** stance.

## 1. Purpose & goal

Model the SVCv4 **Frameshift variants** workflow (SM 9) — the third per-variant-type
workflow. Frameshift variants resolve to a `NUL_` or `CDS_` parent code via one of
**five branches** selected by the predicted consequence (NMD / rescue / no-NMD /
non-stop decay / protein extension).

Scope is capture-only: model the analyst's inputs along whichever branch applies,
and document each branch's pipeline (PRD → FXN → INF → parent total), its point
ranges, and the branch selection; compute no points.

## 2. Source material

- **Supplementary Material 9 (Frameshift)**, verbatim in
  `source-material/svcv4-supplements/SM09-frameshift.txt` — the five branches, the
  point ranges, and the pipeline.
- **Existing architecture:** `src/svcv4_model/nonsense.py` (the direct precedent —
  Frameshift is Nonsense plus the two green branches), `pfd.py` (`PfdParentCode`),
  `mechanism.py`, `functional.py`, `informative.py`.

## 3. Key findings driving this work

### 3.1 Five branches, one shared pipeline

The flow diagram (SM 9 Fig. 1) has five mutually-exclusive branches, chosen per VBC
per MDE (the PTC/consequence position is evaluated, not the VBC position):

- **yellow** — NMD predicted, **no** alternative-Met rescue → **`NUL_`**;
- **orange** — NMD predicted **but** an alternative-Met rescue codon has evidence →
  **`CDS_`**;
- **violet** — **not** predicted to cause NMD (C-terminal truncation) → **`CDS_`**;
- **green-upper** — predicted **non-stop decay** (NSD; ORF runs to the polyA site) →
  **`NUL_`**;
- **green-lower** — predicted **protein extension** (non-native C-terminal amino
  acids, no NSD) → **`CDS_`**.

All five run the same steps — **PRD** (predictive) → **FXN** (functional, SM 20) →
**INF** (informative, SM 19) → **parent** total — with no splice-assay step. Modeled
as **one** `FrameshiftAssessment` parameterized by a `FrameshiftPredictionOutcome`
enum; the parent code is the reused `PfdParentCode` (`NUL`/`CDS`).

### 3.2 Per-branch PRD initial points

- **yellow (`NUL_PRD_`):** fixed **+6.0** (NMD), then SM 18 matrix → `0.0 to +6.0`.
- **orange (`CDS_PRD_`):** **−1.0 to +6.0** from a protein-fraction / critical-AA
  table, then SM 18 matrix → `−1.0 to +6.0`.
- **violet (`CDS_PRD_`):** **0.0 to +6.0** from the same table, then SM 18 →
  `0.0 to +6.0`.
- **green-upper NSD (`NUL_PRD_`):** fixed **+4.0** (no in-frame stop before polyA),
  then SM 18 → `0.0 to +4.0`.
- **green-lower extension (`CDS_PRD_`):** **0.0 to +4.0** from an extension table
  (experimentally-deleterious C-terminal addition → +4.0; some data + ≥30 aa → +3.0;
  some evidence or ≥30 aa → +2.0; else 0.0), then SM 18 → `0.0 to +4.0`.

The **criticality of deleted amino acids** alternative (orange/violet) leans on
**SM 7** Critical Amino Acids (SM 9 cites SM 7 directly here) — deferred, as in
Nonsense. `FrameshiftPredictiveEvidence` captures `protein_fraction_reduced`,
`alternative_met_rescue`, and the two green-branch inputs
`non_stop_decay_predicted` + `extension_length_aa` now.

### 3.3 FXN and INF reuse the shared submodules

FXN is the generic SM 20 module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0`;
the held PRD+FXN combined is capped **`−8.0 to +10.0` (yellow)** or **`−8.0 to +9.0`
(orange / violet / NSD / extension)**. INF is the generic SM 19 pattern
(`InformativeVariantsEvidence`): +2.0 first P / +1.0 first LP / +1.0 each additional
(negatives for B/LB), coded `−8.0 to +8.0`. The INF **position** eligibility differs
per branch (same-exon-as-PTC same-NMD for yellow; between VBC and alt start for
orange; PTC downstream of the VBC / upstream of the normal stop for violet;
termination downstream of the polyA for NSD; same elongation impact for extension) —
a documented eligibility rule, not separate fields.

### 3.4 The green branches are a "take the more pathogenic" choice

SM 9 instructs that the green (NSD / extension) paths be **compared** against the
NMD-not-predicted (violet) path and the **more pathogenic** result applied — the
points are **not additive**. This is an analyst-level selection, so the model
captures the single chosen `prediction_outcome`; the non-additive comparison is
documented, not computed.

### 3.5 One held combined value; parent totals; GoF out of scope

Per SM 9, the model records **both** the separate coded values and the one held
`PRD + FXN` combined value. The parent total is coded `NUL_ −8.0 to +10.0` (yellow /
NSD) or `CDS_ −8.0 to +10.0` (orange / violet / extension). Gain-of-function effects
(truncated / deleted / extended proteins) are explicitly out of scope in SM 9.

### 3.6 A standalone assessment mirroring Nonsense

`FrameshiftAssessment` mirrors `NonsenseAssessment` (which mirrors the scaffold),
adding the two green-branch predictive inputs and the two extra enum values.
Standalone PFD payload — **no** `Workflow` enum entry, no applicability matrix;
`case-model.md` unaffected.

## 4. Scope

**In scope:**

- New module `src/svcv4_model/frameshift.py`: `FrameshiftPredictionOutcome` enum;
  `FrameshiftPredictiveEvidence`, `FrameshiftAssessment` models (§5.1).
- Export the three public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — two new files (§5.3).
- Docs: new `docs/workflows/pfd/frameshift.md` (+ nav + link from `pfd/index.md`),
  `spec-alignment.md` SM 9 row, `known-gaps.md` PFD row, `model.md` (§5.4).
- Tests: new `tests/test_frameshift.py` (§5.5).

**Out of scope / deferred:**

- The critical-domain criticality flag (with SM 7 Critical Amino Acids).
- Gain-of-function variants (SM 9 excludes them).
- All point computation (per-branch ranges, the SM 18 reduction, the green-vs-violet
  comparison, sums).

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/frameshift.py`

```python
"""SVCv4 Frameshift variants workflow (SM 9).

Frameshift variants resolve to a NUL_ or CDS_ parent code via one of five branches
selected by the predicted consequence: NMD + no rescue → NUL_; NMD + rescue → CDS_;
no NMD → CDS_; non-stop decay (NSD) → NUL_; protein extension → CDS_. All five run
the same pipeline — predictive (PRD) → functional (FXN, SM 20) → informative (INF,
SM 19) → parent total — with the SM 18 mechanism/exon matrix applied to the
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


class FrameshiftPredictionOutcome(StrEnum):
    """Which of the five frameshift branches applies to the VBC (SM 9)."""

    NMD_NO_RESCUE = "NMD_NO_RESCUE"
    NMD_WITH_RESCUE = "NMD_WITH_RESCUE"
    NO_NMD = "NO_NMD"
    NON_STOP_DECAY = "NON_STOP_DECAY"
    PROTEIN_EXTENSION = "PROTEIN_EXTENSION"


class FrameshiftPredictiveEvidence(BaseModel):
    """The frameshift predictive (PRD) step of a frameshift branch (SM 9).

    NMD-predicted (yellow) starts at a fixed +6.0 and non-stop decay (green) at
    +4.0; the rescue (orange), no-NMD (violet), and extension (green) branches
    derive initial points from a table. Positive points are reduced by the SM 18
    mechanism/exon matrix.
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
    non_stop_decay_predicted: bool | None = Field(
        default=None,
        description="ORF runs to the polyA with no in-frame stop, predicting NSD (green).",
    )
    extension_length_aa: int | None = Field(
        default=None,
        description="Non-native C-terminal amino acids added past the stop (extension branch).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class FrameshiftAssessment(BaseModel):
    """A frameshift variant (NUL_/CDS_) assessment (SM 9).

    One entity for all five branches, parameterized by ``prediction_outcome``;
    reuses the SM 18/19/20 submodules and the shared ``PfdParentCode`` (NUL/CDS).
    Permissive superset; the per-branch pipeline and its caps are documented, not
    computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: FrameshiftPredictionOutcome | None = Field(
        default=None, description="Which of the five frameshift branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL for yellow/NSD; CDS otherwise)."
    )
    predictive: FrameshiftPredictiveEvidence | None = Field(
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

Add `from svcv4_model.frameshift import (...)` in module order — `frameshift` sorts
**after `evidence_line`** and **before `functional`** (`frameshift` < `functional`:
`fr` < `fu`). Export `FrameshiftAssessment`, `FrameshiftPredictionOutcome`,
`FrameshiftPredictiveEvidence` and add them to `__all__` in sorted position — all
three `Frameshift…` names sort **after `ExonRelevance`** and **before
`FunctionalAssayEvidence`** (`Ex` < `Fr` < `Fu`). Confirm with `sorted()` at
implementation time. `__all__` is hand-sorted (ruff does not sort it). The enum gets
no schema file; the two `BaseModel`s do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **two** new files —
`FrameshiftAssessment.schema.json` (which `$ref`s `FrameshiftPredictiveEvidence`, the
reused `MechanismExonRelevanceEvidence` / `FunctionalAssayEvidence` /
`InformativeVariantsEvidence`, and the `FrameshiftPredictionOutcome` / `PfdParentCode`
enums under `$defs`) and `FrameshiftPredictiveEvidence.schema.json`. **`git add`
both** — the drift gate does not flag untracked files. `export_case_views.py` and
`case-model.md` are unaffected (no `Workflow` entry). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/frameshift.md`** (new) — the Frameshift workflow page.
  Document the five branches (a table: branch → predicted consequence → parent code
  → PRD initial → parent total), the shared PRD → FXN → INF → parent pipeline, the
  SM 18 matrix reduction, the SM 20 (FXN) and SM 19 (INF) reuse with the per-branch
  INF position nuance, the two green-branch inputs (`non_stop_decay_predicted`,
  `extension_length_aa`) and the **green-vs-violet "take the more pathogenic,
  non-additive"** rule, the one held PRD+FXN value (with the `+10` yellow vs `+9`
  others cap nuance), the `parent_code`-follows-`prediction_outcome` note, and the
  GoF-out-of-scope note — all *documented, not computed*. Add a brief footnote that
  the violet `CDS_INF_` upper bound is modeled as `+8.0` (SM 9 L75 has a source typo
  reading `IMP_INF_+8.0`; all INF caps are `−8.0 to +8.0`).
- **`mkdocs.yml`** — add `- Frameshift (NUL_/CDS_): workflows/pfd/frameshift.md`
  under the PFD nav section (after `workflows/pfd/nonsense.md`).
- **`docs/workflows/pfd/index.md`** — in the scaffold section's closing note, add
  Frameshift to the modeled per-variant-type workflows.
- **`docs/reference/spec-alignment.md`** — SM 9 row: from "Not yet modeled" to
  "Modeled (inputs) — `FrameshiftAssessment` (five branches → `NUL_`/`CDS_`, reusing
  SM 18/19/20)".
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: Frameshift now
  joins Missense and Nonsense as a modeled variant-type workflow.
- **`docs/reference/model.md`** — add `::: svcv4_model.FrameshiftAssessment` after
  the `NonsenseAssessment` entry.

### 5.5 Tests: `tests/test_frameshift.py`

- Round-trip a maximal `FrameshiftAssessment` (a `prediction_outcome`, `parent_code`,
  a `FrameshiftPredictiveEvidence` with the green fields set, a **populated**
  `MechanismExonRelevanceEvidence` (e.g. `exon_relevance=ExonRelevance.ALL`), a
  `FunctionalAssayEvidence`, a **populated** `InformativeVariantsEvidence`, all point
  fields) through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields on both models.
- Each `FrameshiftPredictionOutcome` value round-trips; a `PfdParentCode` value
  (`NUL`/`CDS`) round-trips on `parent_code`.
- The three new names are importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_frameshift.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the two new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes (new page in nav; no broken links).

## 7. Follow-up backlog

1. The critical-domain criticality flag with **SM 7** Critical Amino Acids (shared
   with Nonsense and the deferred missense motif variant).
2. The remaining variant-type workflows (Canonical Splice, In-Frame InDel, Start/Stop
   loss, Exon del/dup, …).
3. The full PFD scoring computation.

## 8. Delivery

Branch `feat/pfd-frameshift` off `main`. Single PR for this workflow. CI: pytest,
ruff, the schema/docs drift gate, `mkdocs build --strict`.
