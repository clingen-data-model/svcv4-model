# In-Frame InDel Variants (`CDS_`) Workflow — Design Spec

**Date:** 2026-08-20
**Status:** Proposed
**Builds on:** the Nonsense / Frameshift workflows (the CDS-based precedents), the
PFD scaffold, and SM 18/19/20. Same **capture + document, do not compute** stance.

## 1. Purpose & goal

Model the SVCv4 **In-Frame InDel variants** workflow (SM 10) — the fourth
per-variant-type workflow. In-frame InDels (in-frame insertions, duplications,
deletions, and insertion-deletions within a single exon, changing length by a
multiple of three) always resolve to the **`CDS_`** parent code (−8.0 to +10.0)
via one of **two branches** selected by whether the variant is a **simple sequence
repeat** (SSR / tandem repeat) or not.

Scope is capture-only: model the analyst's inputs along whichever branch applies,
and document each branch's pipeline (PRD → FXN → INF → `CDS_` total), its point
ranges, and the branch selection; compute no points.

## 2. Source material

- **Supplementary Material 10 (In-Frame InDel)**, verbatim in
  `source-material/svcv4-supplements/SM10-inframe-indel.txt`.
- **Existing architecture:** `src/svcv4_model/nonsense.py` /
  `src/svcv4_model/frameshift.py` (the CDS-based precedents), `pfd.py`
  (`PfdParentCode`), `mechanism.py`, `functional.py`, `informative.py`.

## 3. Key findings driving this work

### 3.1 Two branches, one shared pipeline, always `CDS_`

The flow diagram (SM 10 Fig. 1) has two scored branches:

- **simple sequence repeat (SSR / tandem repeat)** — the variant changes the length
  of a repeat ≥5 units;
- **non-repeat in-frame InDel** — everything else in scope.

Both run **PRD** (predictive) → **FXN** (functional, SM 20) → **INF** (informative,
SM 19) → the **`CDS_`** parent total. Modeled as **one** `InframeIndelAssessment`
parameterized by an `InframeIndelBranch` enum; `parent_code` is the reused
`PfdParentCode` — **always `CDS`** here (kept for family uniformity with the other
variant-type assessments, documented as invariant).

### 3.2 Per-branch PRD initial points

- **SSR (`CDS_PRD_`):** `0.0` if the repeat is stable in large control sets (e.g.
  gnomAD), `−1.0` if polymorphic; a novel TRE length (thresholds not established)
  scores `0.0`. The SM 18 matrix is **not** applied on the SSR branch. Captured via
  `repeat_stable_in_controls`.
- **non-repeat (`CDS_PRD_`):** from an initial-points table keyed on the fraction of
  protein removed / a critical domain removed (`+6.0` for >50% or a critical
  domain), plus an indel in-silico predictor — **calibrated** tools up to `+2.0`,
  **uncalibrated** `+1.0 to −1.0`. Positive points are then reduced by the SM 18
  matrix → `CDS_PRD_ −1.0 to +6.0`. Captured via `protein_fraction_reduced`,
  `in_silico_predictor` (free string — CADD / CAPICE / PROVEAN / MutationTaster2021
  / …), and `in_silico_calibrated`.

The **critical-domain** axis leans on **SM 7** Critical Amino Acids (SM 10 cites
SM 7) — deferred, as in Nonsense / Frameshift.

### 3.3 FXN and INF reuse the shared submodules

FXN is the generic SM 20 module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0`.
The held PRD+FXN combined is capped **`−8.0 to +8.0` (SSR)** or **`−8.0 to +9.0`
(non-repeat)**. INF is the generic SM 19 pattern (`InformativeVariantsEvidence`):
+2.0 first P / +1.0 first LP / +1.0 each additional (negatives for B/LB), VUS → 0.0,
coded `−8.0 to +8.0`. The INF **eligibility** differs per branch: for SSR, a
*shorter* repeat length for pathogenic informative variants and a *longer* one for
benign; for non-repeat, an informative variant whose predicted effect is the *same
or less damaging* (pathogenic) or *same or more damaging* (benign) than the VBC — a
documented eligibility rule, not separate fields.

### 3.4 One held combined value; parent total; escapes out of scope

Per SM 10, the model records **both** the separate coded values and the one held
`PRD + FXN` combined value. The parent total is coded `CDS_ −8.0 to +10.0`. Two
situations are **out of scope** (documented, not modeled): (a) the **MDE-specific
guidance escape** — when disease-specific repeat guidance exists (e.g. Huntington),
the analyst uses that guidance and does *not* score with this diagram; (b) **splice
effects** — indels at/near an exon/intron junction or creating a cryptic splice site
are assessed via the Missense splice flow (SM 6) / Canonical Splice (SM 11), not
here.

### 3.5 A standalone assessment mirroring the CDS-based workflows

`InframeIndelAssessment` mirrors `NonsenseAssessment` / `FrameshiftAssessment`,
swapping in the InDel-specific predictive inputs. Standalone PFD payload — **no**
`Workflow` enum entry, no applicability matrix; `case-model.md` unaffected.

## 4. Scope

**In scope:**

- New module `src/svcv4_model/inframe_indel.py`: `InframeIndelBranch` enum;
  `InframeIndelPredictiveEvidence`, `InframeIndelAssessment` models (§5.1).
- Export the three public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — two new files (§5.3).
- Docs: new `docs/workflows/pfd/inframe-indel.md` (+ nav + link from `pfd/index.md`),
  `spec-alignment.md` SM 10 row, `known-gaps.md` PFD row, `model.md` (§5.4).
- Tests: new `tests/test_inframe_indel.py` (§5.5).

**Out of scope / deferred:**

- The critical-domain criticality flag (with SM 7 Critical Amino Acids).
- The MDE-specific-guidance escape and splice-effect cross-reference (documented,
  handled by other workflows).
- All point computation (per-branch ranges, the SM 18 reduction, sums).

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/inframe_indel.py`

```python
"""SVCv4 In-Frame InDel variants workflow (SM 10).

In-frame insertions, duplications, deletions, and insertion-deletions within a
single exon (length change a multiple of three) always resolve to the CDS_ parent
code via one of two branches: a simple sequence repeat (SSR / tandem repeat) or a
non-repeat InDel. Both run the same pipeline — predictive (PRD) → functional (FXN,
SM 20) → informative (INF, SM 19) → the CDS_ total — with the SM 18 mechanism/exon
matrix applied to the non-repeat branch's predictive points. This module captures
the analyst's inputs; the scoring is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class InframeIndelBranch(StrEnum):
    """Which of the two in-frame InDel branches applies to the VBC (SM 10)."""

    SIMPLE_SEQUENCE_REPEAT = "SIMPLE_SEQUENCE_REPEAT"
    NON_REPEAT = "NON_REPEAT"


class InframeIndelPredictiveEvidence(BaseModel):
    """The in-frame InDel predictive (CDS_PRD) step (SM 10).

    The SSR branch scores 0.0 (stable in controls) or −1.0 (polymorphic); the
    non-repeat branch derives initial points from the protein fraction removed / a
    critical domain / an indel in-silico predictor, then applies the SM 18 matrix.
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None, description="Predictive basis (e.g. repeat length; deleted fraction)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial CDS_PRD points before the SM 18 adjustment."
    )
    protein_fraction_reduced: float | None = Field(
        default=None,
        description="Fraction of protein removed (the non-repeat initial-points table).",
    )
    in_silico_predictor: str | None = Field(
        default=None,
        description="Indel in-silico predictor used (e.g. MutationTaster2021, PROVEAN).",
    )
    in_silico_calibrated: bool | None = Field(
        default=None,
        description="Whether the indel predictor is calibrated (calibrated reaches +2.0).",
    )
    repeat_stable_in_controls: bool | None = Field(
        default=None,
        description="SSR branch: the repeat is stable in large control sets (else polymorphic).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded CDS_PRD points after the SM 18 adjustment."
    )


class InframeIndelAssessment(BaseModel):
    """An in-frame InDel (CDS_) assessment (SM 10).

    One entity for both branches, parameterized by ``branch``; reuses the SM 18/19/20
    submodules and the shared ``PfdParentCode`` (always CDS here). Permissive
    superset; the per-branch pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    branch: InframeIndelBranch | None = Field(
        default=None, description="Which of the two in-frame InDel branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (always CDS for in-frame InDels)."
    )
    predictive: InframeIndelPredictiveEvidence | None = Field(
        default=None, description="The CDS_PRD predictive step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (CDS_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (CDS_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded CDS_PRD point value.")
    fxn_points: float | None = Field(default=None, description="Coded CDS_FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded CDS_INF point value.")
    prd_fxn_combined: float | None = Field(
        default=None, description="Held CDS_PRD + CDS_FXN combined value (no distinct code)."
    )
    parent_total: float | None = Field(
        default=None, description="Capped CDS_ parent-code total (−8.0 to +10.0)."
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `from svcv4_model.inframe_indel import (...)` in module order — `inframe_indel`
sorts **after `informative`** and **before `inputs`** (`informative` < `inframe` <
`inputs`: at char 4, `o` < `r`, then `inframe` < `inputs` at char 3, `f` < `p`).
Export `InframeIndelAssessment`, `InframeIndelBranch`,
`InframeIndelPredictiveEvidence` and add them to `__all__` in sorted position — all
three `InframeIndel…` names sort **after `InformativeVariantsEvidence`** (`Info` <
`Infr`) and **before `ManeStatus`**. Confirm the exact neighbors with `sorted()` at
implementation time. `__all__` is hand-sorted (ruff does not sort it). The enum gets
no schema file; the two `BaseModel`s do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **two** new files —
`InframeIndelAssessment.schema.json` (which `$ref`s `InframeIndelPredictiveEvidence`,
the reused `MechanismExonRelevanceEvidence` / `FunctionalAssayEvidence` /
`InformativeVariantsEvidence`, and the `InframeIndelBranch` / `PfdParentCode` enums
under `$defs`) and `InframeIndelPredictiveEvidence.schema.json`. **`git add` both** —
the drift gate does not flag untracked files. `export_case_views.py` and
`case-model.md` are unaffected (no `Workflow` entry). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/inframe-indel.md`** (new) — the In-Frame InDel workflow
  page. Document the two branches (a table: branch → PRD initial → held PRD+FXN cap
  → `CDS_` total), the shared PRD → FXN → INF → `CDS_` pipeline, the SM 18 matrix
  reduction (non-repeat only), the SM 20 (FXN) and SM 19 (INF) reuse with the
  per-branch INF eligibility nuance, the one held PRD+FXN value (with the SSR
  `−8..+8` vs non-repeat `−8..+9` cap nuance), the `parent_code`-always-`CDS` note,
  and the two out-of-scope escapes (MDE-specific guidance; splice effects → SM 6 /
  SM 11) — all *documented, not computed*. Add a brief inline note that SM 10 has
  two source typos in the non-repeat section — the CDS_INF heading is mislabeled
  `CDS_FXN_` (L30) and the functional ND code appears as `CDN_FXN_ND` (L46); the
  correct codes are `CDS_INF_` and `CDS_FXN_ND`.
- **`mkdocs.yml`** — add `- In-Frame InDel (CDS_): workflows/pfd/inframe-indel.md`
  under the PFD nav section (after `workflows/pfd/frameshift.md`).
- **`docs/workflows/pfd/index.md`** — in the scaffold section's closing note, add
  In-Frame InDel to the modeled per-variant-type workflows.
- **`docs/reference/spec-alignment.md`** — SM 10 row: from "Not yet modeled" to
  "Modeled (inputs) — `InframeIndelAssessment` (SSR + non-repeat branches → `CDS_`,
  reusing SM 18/19/20)".
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: In-Frame InDel
  now joins the modeled variant-type workflows.
- **`docs/reference/model.md`** — add `::: svcv4_model.InframeIndelAssessment` after
  the `FrameshiftAssessment` entry.

### 5.5 Tests: `tests/test_inframe_indel.py`

- Round-trip a maximal `InframeIndelAssessment` (a `branch`, `parent_code`, an
  `InframeIndelPredictiveEvidence` with both branches' fields set, a **populated**
  `MechanismExonRelevanceEvidence`, a `FunctionalAssayEvidence`, a **populated**
  `InformativeVariantsEvidence`, all point fields) through `model_dump(mode="json")`
  → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields on both models.
- Each `InframeIndelBranch` value round-trips; a `PfdParentCode.CDS` round-trips on
  `parent_code`.
- The three new names are importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_inframe_indel.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the two new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes (new page in nav; no broken links).

## 7. Follow-up backlog

1. The critical-domain criticality flag with **SM 7** Critical Amino Acids.
2. The remaining variant-type workflows (Canonical Splice SM 11, Start/Stop loss
   SM 15/16, Exon del/dup SM 13/14).
3. The full PFD scoring computation.

## 8. Delivery

Branch `feat/pfd-inframe-indel` off `main`. Single PR for this workflow. CI: pytest,
ruff, the schema/docs drift gate, `mkdocs build --strict`.
