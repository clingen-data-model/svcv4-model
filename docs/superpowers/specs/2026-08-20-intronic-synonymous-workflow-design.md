# Intronic & Synonymous Variants (`SPL_`) Workflow — Design Spec

**Date:** 2026-08-20
**Status:** Proposed
**Builds on:** the shared splice vocabulary (`splice.py`, #39) and its two existing
consumers (`MissenseSpliceAssessment`, `CanonicalSpliceAssessment`), plus SM 18/19/20.
Same **capture + document, do not compute** stance.

## 1. Purpose & goal

Model the SVCv4 **Intronic & Synonymous variants** workflow (SM 12) — the sixth
per-variant-type workflow, and the **third consumer** of the shared `Splice*`
vocabulary. Both intronic variants (SNVs/indels in an intron, excluding the
essential ±1,2 GT/AG sites) and synonymous variants are evaluated for their
**splicing** potential and resolve to the **`SPL_`** parent code via the *same five
paths* as the missense/canonical splice flows.

Scope is capture-only: model the analyst's inputs along whichever path applies, and
document each path's pipeline (SPL_PRD → SPL_SPA → SPL_FXN → SPL_INF → `SPL_` total),
its point ranges, and the SPA semantics; compute no points.

## 2. Source material

- **Supplementary Material 12 (Intronic & Synonymous)**, verbatim in
  `source-material/svcv4-supplements/SM12-intronic-synonymous.txt`.
- **Existing architecture:** `src/svcv4_model/splice.py` (the shared vocabulary),
  `src/svcv4_model/canonical_splice.py` (`CanonicalSpliceAssessment`, the field-model
  this mirrors), `pfd.py` / `mechanism.py` / `functional.py` / `informative.py`.

## 3. Key findings driving this work

### 3.1 Same five-path splice structure, always `SPL_`

An in-silico splice predictor (SpliceAI / Pangolin), trichotomized into likely /
uncertain / unlikely, selects one of five paths — the same `SplicePredictionOutcome`
values as the other splice flows: `NMD_PREDICTED` (yellow), `FRAMESHIFT_NO_NMD`
(upper orange), `SPLICE_NO_FRAMESHIFT` (lower orange), `UNCERTAIN` (blue),
`UNLIKELY` (SM 12 calls it the "lilac" path). Each runs SPL_PRD → SPL_SPA →
SPL_FXN → SPL_INF → the **`SPL_`** parent total. The parent code is **always `SPL_`**
— SM 12 sums every path to `SPL_` (the earlier "`NCG_*` (assumed)" note on the
spec-coverage page was a guess; SM 12 does not use `NCG_`).

### 3.2 Field-identical to `CanonicalSpliceAssessment`

`IntronicSynonymousAssessment` reuses the shared `Splice*` vocabulary and is
**field-identical** to `CanonicalSpliceAssessment` (prediction_outcome, predictive,
mechanism_exon_relevance, splice_assay, functional, informative, prd/spa/fxn/inf
points, the two held-combined values, spl_total; no `parent_code`). Only the
documented point values differ.

### 3.3 Per-path point values (documented on the page)

The SM 12 values track the **missense** splice half (SM 6), not canonical (SM 11):

- **yellow (NMD):** SPL_PRD **+3.0** → SM 18 matrix → `0.0 to +3.0` (lower than a
  nonsense variant because of splice-prediction uncertainty).
- **orange (frameshift-no-NMD / no-frameshift):** SPL_PRD `−1.0 to +3.0` from a
  critical-amino-acid table (lower orange adds an in-frame in-silico deletion tool,
  `+0.5 / −0.5`) → SM 18 → `−1.0 to +3.0`.
- **blue (uncertain):** SPL_PRD **0.0** (no SM 18).
- **lilac (unlikely):** SPL_PRD **−1.0** (no SM 18).

### 3.4 SPA semantics and parent ranges

- **SPA (yellow):** **adds** a fraction of SPL_PRD (near-complete → 100%, substantial
  → 50%, incomplete/none → 0). **orange:** **doubles** (near-complete → +100%,
  substantial → +50%; held PRD+SPA `−1.0 to +6.0`). **blue:** additive `−2.0 to +2.0`.
  **lilac:** benignity `−2.0 to 0.0` (held PRD+SPA `−3.0 to 0.0`). (This is the
  *scale-up* direction of the missense splice half, not canonical's reduce.)
- **held PRD+SPA+FXN caps:** `−8.0 to +9.0` (yellow/orange/blue), `−8.0 to 0.0`
  (lilac, with SPL_FXN itself capped `−8.0 to 0.0`).
- **parent `SPL_` totals:** yellow/orange `−8.0 to +10.0`; **blue `−8.0 to +8.0`;
  lilac `−8.0 to 0.0`** (matching canonical splice — the lilac path restricts
  SPL_INF to B/LB only).

### 3.5 A standalone assessment; escapes out of scope

`IntronicSynonymousAssessment` is a standalone PFD payload — **no** `Workflow` enum
entry, no applicability matrix; `case-model.md` unaffected. GoF is out of scope
(SM 12); intronic genomic rearrangements/CNVs are handled elsewhere; a variant of the
±1,2 dinucleotides whose wild-type is *not* GT/AG uses this flow rather than Canonical
Splice — documented, not a separate field.

## 4. Scope

**In scope:**

- New module `src/svcv4_model/intronic_synonymous.py`: `IntronicSynonymousAssessment`
  (§5.1).
- Export the name from `__init__.py` (§5.2).
- Regenerate JSON Schemas — one new file (§5.3).
- Docs: new `docs/workflows/pfd/intronic-synonymous.md` (+ nav + link),
  `spec-alignment.md` SM 12 row, `known-gaps.md` PFD row, `model.md` (§5.4).
- Tests: new `tests/test_intronic_synonymous.py` (§5.5).

**Out of scope / deferred:**

- The critical-domain criticality flag (with SM 7 Critical Amino Acids).
- GoF, intronic rearrangements/CNVs (handled elsewhere).
- All point computation.

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/intronic_synonymous.py`

```python
"""SVCv4 Intronic & Synonymous variants workflow (SM 12).

Intronic variants (excluding the essential ±1,2 GT/AG splice sites) and synonymous
variants are evaluated for their splicing potential and resolve to the SPL_ parent
code via one of five paths (NMD / frameshift-no-NMD / no-frameshift / uncertain /
unlikely), each running the shared splice pipeline — predictive (SPL_PRD) → splice
assay (SPL_SPA) → functional (SPL_FXN, SM 20) → informative (SPL_INF, SM 19) → the
capped SPL_ total. Field-identical to the canonical splice assessment (SM 11); the
SM 12 point values track the missense splice half (SM 6) and are documented, not
computed.
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


class IntronicSynonymousAssessment(BaseModel):
    """An intronic / synonymous variant (SPL_) assessment (SM 12).

    One entity for all five splice paths, parameterized by ``prediction_outcome``;
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
        default=None, description="SM 12 splice-assay evidence (SPL_SPA)."
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

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `from svcv4_model.intronic_synonymous import IntronicSynonymousAssessment` in
module order — `intronic_synonymous` sorts **after `inputs`** and **before
`mechanism`** (`inputs` < `intronic` < `mechanism`). Add
`"IntronicSynonymousAssessment"` to `__all__` in sorted position — it sorts **after
`InframeIndelPredictiveEvidence`** (`Inframe` < `Intronic`) and **before
`ManeStatus`**. Confirm exact neighbors with `sorted()` at implementation time.
`__all__` is hand-sorted. The model gets one schema file.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **one** new file —
`IntronicSynonymousAssessment.schema.json` (which `$ref`s `SplicePredictiveEvidence`,
`SpliceAssayEvidence`, the reused submodules, and the enums under `$defs`). No
existing schema changes. **`git add`** the new file. `export_case_views.py` /
`case-model.md` unaffected. CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/intronic-synonymous.md`** (new) — the Intronic & Synonymous
  workflow page. Document the scope (intronic excl. ±1,2 GT/AG; synonymous; non-GT/AG
  ±1,2 sites route here), the SpliceAI trichotomy (>0.2 likely / 0.1–0.2 uncertain /
  <0.1 unlikely), the five paths (a table: path → SPL_PRD initial → `SPL_` total), the
  shared pipeline, the SM 18 matrix (yellow/orange positive PRD only), the SPA
  **scale-up** semantics (yellow adds fraction / orange doubles / blue additive /
  lilac benignity), the SM 20 (FXN) and SM 19 (INF) reuse (lilac INF is B/LB only),
  the held-combined values, and the parent ranges (yellow/orange `−8..+10`, blue
  `−8..+8`, lilac `−8..0`). Note it reuses the `Splice*` vocabulary and that the SM 12
  point values match the missense splice half while the parent ranges match canonical.
  GoF out of scope. All *documented, not computed*.
- **`mkdocs.yml`** — add `- Intronic & Synonymous (SPL_): workflows/pfd/intronic-synonymous.md`
  under the PFD nav section (after `workflows/pfd/canonical-splice.md`).
- **`docs/workflows/pfd/index.md`** — in the scaffold section's closing note, add
  Intronic & Synonymous to the modeled per-variant-type workflows and bump the count
  from "Five" to "Six".
- **`src/svcv4_model/splice.py`** — update the **module docstring only** (line 1
  block) to list SM 12 as a third consumer of the shared splice vocabulary. This is
  schema-safe: the per-class JSON Schemas use only the *class* docstrings, so leave
  the five class docstrings untouched (editing them would break the zero-drift
  guarantee). Verify `git diff --quiet -- schemas/json` still holds after the edit.
- **`docs/reference/spec-alignment.md`** — SM 12 row: from "Not yet modeled" to
  "Modeled (inputs) — `IntronicSynonymousAssessment` (five splice paths → `SPL_`,
  reusing the shared `Splice*` vocabulary + SM 18/19/20)"; drop the "`NCG_*` (assumed)"
  qualifier since SM 12 uses `SPL_`.
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: Intronic &
  Synonymous now joins the modeled variant-type workflows.
- **`docs/reference/model.md`** — add `::: svcv4_model.IntronicSynonymousAssessment`
  after the `CanonicalSpliceAssessment` entry.

### 5.5 Tests: `tests/test_intronic_synonymous.py`

- Round-trip a maximal `IntronicSynonymousAssessment` (a `prediction_outcome`, a
  `SplicePredictiveEvidence` (with a `SplicePredictor`), a `MechanismExonRelevanceEvidence`
  (populated), a `SpliceAssayEvidence` (with a `SpliceAssayResult`), a
  `FunctionalAssayEvidence`, a **populated** `InformativeVariantsEvidence`, all point
  fields including both combined) through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields.
- Importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_intronic_synonymous.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the one new schema:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes (new page in nav; no broken links).

## 7. Follow-up backlog

1. The critical-domain criticality flag with **SM 7** Critical Amino Acids.
2. The remaining variant-type workflows (Start/Stop loss SM 15/16, Exon del/dup
   SM 13/14).
3. The full PFD scoring computation.

## 8. Delivery

Branch `feat/pfd-intronic-synonymous` off `main`. Single PR. CI: pytest, ruff, the
schema/docs drift gate, `mkdocs build --strict`.
