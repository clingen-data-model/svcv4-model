# Single/Multi-Exon Deletion Variants (`NUL_`/`CDS_`) Workflow — Design Spec

**Date:** 2026-08-20
**Status:** Proposed
**Builds on:** the Nonsense / Frameshift workflows (the `NUL_`/`CDS_` deletion
precedents), the PFD scaffold, and SM 18/19/20. Same **capture + document, do not
compute** stance.

## 1. Purpose & goal

Model the SVCv4 **Single- or Multi-Exon Deletion** workflow (SM 13) — the seventh
per-variant-type workflow. Deletions of one or more exons up to an entire single
gene resolve to a `NUL_` or `CDS_` parent code via one of **six branches** selected
by a decision tree (whole-gene? / includes the first coding exon? / NMD predicted? /
alternative in-frame start codon and its functionality).

Scope is capture-only: model the analyst's inputs along whichever branch applies,
and document each branch's pipeline (PRD → FXN → INF → parent total), its point
ranges, and the branch selection; compute no points.

## 2. Source material

- **Supplementary Material 13 (Single/Multi-Exon Deletions)**, verbatim in
  `source-material/svcv4-supplements/SM13-exon-deletions.txt`.
- **Existing architecture:** `src/svcv4_model/nonsense.py` / `frameshift.py` (the
  `NUL_`/`CDS_` deletion precedents this mirrors), `pfd.py` (`PfdParentCode`),
  `mechanism.py`, `functional.py`, `informative.py`.

## 3. Key findings driving this work

### 3.1 Six branches, one shared pipeline

The flow diagram (SM 13 Fig. 1) has six mutually-exclusive branches:

- **yellow** — whole-gene deletion → **`NUL_`**;
- **orange** — subgenic, does **not** include the first coding exon, **NMD**
  predicted → **`NUL_`**;
- **violet** — subgenic, does **not** include the first coding exon, **no NMD** →
  **`CDS_`**;
- **green** — includes the first coding (start) exon, **no** alternative in-frame
  start → **`NUL_`**;
- **blue** — includes the start codon, an alternative in-frame start exists but is
  **unproven** (no lab evidence of normal function) → **`CDS_`**;
- **grey** — includes the start codon, a **demonstrated functional** alternative
  in-frame start → **`CDS_`**.

All six run the same steps — **PRD** (predictive) → **FXN** (functional, SM 20) →
**INF** (informative, SM 19) → **parent** total — with no splice-assay step. Modeled
as **one** `ExonDeletionAssessment` parameterized by an `ExonDeletionOutcome` enum;
the parent code is the reused `PfdParentCode` (`NUL`/`CDS`).

### 3.2 Per-branch PRD initial points

- **yellow (`NUL_PRD_`):** fixed **+10.0** (whole-gene LoF), then the SM 18 matrix —
  **mechanism only** (the exon-relevance axis is *removed* since the VBC is the
  entire gene) → `0.0 to +10.0`.
- **orange / green (`NUL_PRD_`):** fixed **+6.0** (NMD / start-exon LoF), then the
  SM 18 matrix → `0.0 to +6.0`.
- **violet / blue (`CDS_PRD_`):** **0.0 to +6.0** from an initial-points table keyed
  on the fraction of protein removed / a critical domain removed (violet applies the
  criteria in order; blue may use the highest applicable), then the SM 18 matrix →
  `0.0 to +6.0`.
- **grey (`CDS_PRD_`):** fixed **−1.0** (the alternative start yields normal
  function); the SM 18 matrix is **not** applied (negative points).

The **critical-domain** axis (violet/blue) leans on **SM 7** Critical Amino Acids —
deferred, as in Nonsense / Frameshift. `ExonDeletionPredictiveEvidence` captures
`protein_fraction_removed` and `alternative_start_functional` (the grey gate).

### 3.3 FXN and INF reuse the shared submodules

FXN is the generic SM 20 module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0`;
the held PRD+FXN combined is capped **`−8.0 to +10.0`** (yellow / orange / green,
the `NUL_` paths), **`−8.0 to +9.0`** (violet / blue), or **`−8.0 to 0.0`** (grey,
where FXN is benignity-only). INF is the generic SM 19 pattern
(`InformativeVariantsEvidence`): a variant deleting a similar region / same-exon PTC
(+2.0 first P / +1.0 first LP / +1.0 each additional; negatives for B/LB; VUS → 0),
coded `−8.0 to +8.0` — **grey INF is benignity-only** (`−8.0 to 0.0`). A per-branch
eligibility nuance (whole-gene: similar-region deletion, subgenic P/LP count but
subgenic B/LB do not for benignity; NMD paths: same-exon PTC) is documented, not
separate fields.

### 3.4 One held combined value; parent totals

Per SM 13, the model records **both** the separate coded values and the one held
`PRD + FXN` combined value. The parent total is coded `NUL_ −8.0 to +10.0`
(yellow / orange / green), `CDS_ −8.0 to +10.0` (violet / blue), or `CDS_ −8.0 to
0.0` (grey). (SM 13 L17 has a source typo: the yellow-path no-data functional code
reads `SPL_FXN_ND`; it should be `NUL_FXN_ND`.)

### 3.5 A standalone assessment; escapes out of scope

`ExonDeletionAssessment` mirrors `NonsenseAssessment` / `FrameshiftAssessment`.
Standalone PFD payload — **no** `Workflow` enum entry, no applicability matrix;
`case-model.md` unaffected. Out of scope (documented, handled elsewhere):
multi-gene deletions (→ CNV recommendations), deletions smaller than an exon (→
In-Frame InDel SM 10 / Frameshift SM 9), and deletions flanking a single exon-intron
boundary (→ Canonical Splice SM 11). GoF is not addressed.

## 4. Scope

**In scope:**

- New module `src/svcv4_model/exon_deletion.py`: `ExonDeletionOutcome` enum;
  `ExonDeletionPredictiveEvidence`, `ExonDeletionAssessment` models (§5.1).
- Export the three public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — two new files (§5.3).
- Docs: new `docs/workflows/pfd/exon-deletion.md` (+ nav + link),
  `spec-alignment.md` SM 13 row, `known-gaps.md` PFD row, `model.md` (§5.4).
- Tests: new `tests/test_exon_deletion.py` (§5.5).

**Out of scope / deferred:**

- The critical-domain criticality flag (with SM 7 Critical Amino Acids).
- Multi-gene / sub-exon / exon-intron-boundary deletions (handled by other
  workflows); GoF.
- All point computation.

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/exon_deletion.py`

```python
"""SVCv4 Single/Multi-Exon Deletion variants workflow (SM 13).

Deletions of one or more exons up to an entire single gene resolve to a NUL_ or
CDS_ parent code via one of six branches selected by a decision tree (whole-gene? /
includes the first coding exon? / NMD predicted? / alternative in-frame start codon
and its functionality). All six run the same pipeline — predictive (PRD) →
functional (FXN, SM 20) → informative (INF, SM 19) → parent total — with the SM 18
mechanism/exon matrix applied to the predictive points (mechanism-only for the
whole-gene branch). This module captures the analyst's inputs; the scoring is
documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class ExonDeletionOutcome(StrEnum):
    """Which of the six exon-deletion branches applies to the VBC (SM 13)."""

    WHOLE_GENE = "WHOLE_GENE"
    SUBGENIC_NMD = "SUBGENIC_NMD"
    SUBGENIC_NO_NMD = "SUBGENIC_NO_NMD"
    START_CODON_NO_ALT_START = "START_CODON_NO_ALT_START"
    START_CODON_ALT_START_UNPROVEN = "START_CODON_ALT_START_UNPROVEN"
    START_CODON_ALT_START_FUNCTIONAL = "START_CODON_ALT_START_FUNCTIONAL"


class ExonDeletionPredictiveEvidence(BaseModel):
    """The exon-deletion predictive (PRD) step of a deletion branch (SM 13).

    Whole-gene starts at +10.0; the NMD / start-exon branches at +6.0; the no-NMD
    and unproven-alt-start branches derive initial points from the fraction of
    protein removed; the functional-alt-start branch starts at −1.0. Positive points
    are reduced by the SM 18 matrix (mechanism-only for whole-gene).
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None, description="Predictive basis (e.g. whole-gene LoF; NMD; % protein lost)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial PRD points before the SM 18 adjustment."
    )
    protein_fraction_removed: float | None = Field(
        default=None,
        description="Fraction of protein removed (the violet/blue initial-points table).",
    )
    alternative_start_functional: bool | None = Field(
        default=None,
        description="Demonstrated functional alternative in-frame start (the grey branch).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class ExonDeletionAssessment(BaseModel):
    """A single/multi-exon deletion (NUL_/CDS_) assessment (SM 13).

    One entity for all six branches, parameterized by ``prediction_outcome``; reuses
    the SM 18/19/20 submodules and the shared ``PfdParentCode`` (NUL/CDS). Permissive
    superset; the per-branch pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: ExonDeletionOutcome | None = Field(
        default=None, description="Which of the six exon-deletion branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL or CDS per branch)."
    )
    predictive: ExonDeletionPredictiveEvidence | None = Field(
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
        default=None, description="Capped parent-code total for this branch."
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `from svcv4_model.exon_deletion import (...)` in module order — `exon_deletion`
sorts **after `evidence_line`** and **before `frameshift`** (`ev` < `ex` < `fr`).
Export `ExonDeletionAssessment`, `ExonDeletionOutcome`,
`ExonDeletionPredictiveEvidence` and add them to `__all__` in sorted position — all
three `ExonDeletion…` names sort **before `ExonRelevance`** (`ExonD` < `ExonR`) and
after the `Evidence*` entries. Confirm exact neighbors with `sorted()` at
implementation time. `__all__` is hand-sorted. The enum gets no schema file; the two
`BaseModel`s do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **two** new files —
`ExonDeletionAssessment.schema.json` (which `$ref`s `ExonDeletionPredictiveEvidence`,
the reused submodules, and the `ExonDeletionOutcome` / `PfdParentCode` enums under
`$defs`) and `ExonDeletionPredictiveEvidence.schema.json`. **`git add` both** — the
drift gate does not flag untracked files. `export_case_views.py` / `case-model.md`
unaffected (no `Workflow` entry). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/exon-deletion.md`** (new) — the Exon Deletion workflow page.
  Document the six branches (a table: branch → condition → parent code → PRD initial
  → parent total), the shared PRD → FXN → INF → parent pipeline, the SM 18 matrix
  (mechanism-only for whole-gene; skipped for grey), the SM 20 (FXN) / SM 19 (INF)
  reuse with the per-branch nuances (grey FXN + INF benignity-only), the one held
  PRD+FXN value (`−8..+10` NUL / `−8..+9` violet-blue / `−8..0` grey), and the three
  out-of-scope escapes (multi-gene → CNV; sub-exon → InDel/Frameshift; exon-intron
  boundary → Canonical Splice) — all *documented, not computed*. Note the SM 13 L17
  source typo (`SPL_FXN_ND` should be `NUL_FXN_ND`).
- **`mkdocs.yml`** — add `- Exon Deletion (NUL_/CDS_): workflows/pfd/exon-deletion.md`
  under the PFD nav section (after `workflows/pfd/intronic-synonymous.md`).
- **`docs/workflows/pfd/index.md`** — in the scaffold section's closing note, add
  Exon Deletion to the modeled per-variant-type workflows and bump the count from
  "Six" to "Seven".
- **`docs/reference/spec-alignment.md`** — SM 13 row: from "Not yet modeled" to
  "Modeled (inputs) — `ExonDeletionAssessment` (six branches → `NUL_`/`CDS_`, reusing
  SM 18/19/20)".
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: Exon Deletion now
  joins the modeled variant-type workflows.
- **`docs/reference/model.md`** — add `::: svcv4_model.ExonDeletionAssessment` after
  the `IntronicSynonymousAssessment` entry.

### 5.5 Tests: `tests/test_exon_deletion.py`

- Round-trip a maximal `ExonDeletionAssessment` (a `prediction_outcome`, `parent_code`,
  an `ExonDeletionPredictiveEvidence`, a **populated** `MechanismExonRelevanceEvidence`,
  a `FunctionalAssayEvidence`, a **populated** `InformativeVariantsEvidence`, all
  point fields) through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields on both models.
- Each `ExonDeletionOutcome` value round-trips; a `PfdParentCode` value (`NUL`/`CDS`)
  round-trips on `parent_code`.
- The three new names are importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_exon_deletion.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the two new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes (new page in nav; no broken links).

## 7. Follow-up backlog

1. The critical-domain criticality flag with **SM 7** Critical Amino Acids.
2. The remaining variant-type workflows (Exon Duplication SM 14, Start/Stop loss
   SM 15/16).
3. The full PFD scoring computation.

## 8. Delivery

Branch `feat/pfd-exon-deletion` off `main`. Single PR. CI: pytest, ruff, the
schema/docs drift gate, `mkdocs build --strict`.
