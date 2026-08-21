# Canonical Splice Variants (`SPL_`) Workflow — Design Spec

**Date:** 2026-08-20
**Status:** Proposed
**Builds on:** the Missense **splice paths** (`MissenseSpliceAssessment`, #34 — the
structural twin), the PFD scaffold, and SM 18/19/20. Same **capture + document, do
not compute** stance.

## 1. Purpose & goal

Model the SVCv4 **Canonical Splice variants** workflow (SM 11) — the fifth
per-variant-type workflow. Canonical splice variants (the essential `GT` donor +1/+2
or `AG` acceptor −2/−1 dinucleotides) resolve to the **`SPL_`** parent code via one
of **five color paths** — the *same five* the Missense splice half uses. This
increment therefore (a) **hoists the already-generic `Splice*` vocabulary** out of
`missense.py` into a shared `splice.py` module, then (b) adds a canonical-splice
top-level entity that composes it.

Scope is capture-only: model the analyst's inputs along whichever path applies, and
document each path's pipeline (SPL_PRD → SPL_SPA → SPL_FXN → SPL_INF → `SPL_` total),
its point ranges, and the SPA semantics; compute no points.

## 2. Source material

- **Supplementary Material 11 (Canonical Splice)**, verbatim in
  `source-material/svcv4-supplements/SM11-canonical-splice.txt`.
- **Existing architecture:** `src/svcv4_model/missense.py` (currently defines the
  generic `Splice*` types + `MissenseSpliceAssessment`, the structural twin),
  `pfd.py`, `mechanism.py`, `functional.py`, `informative.py`.

## 3. Key findings driving this work

### 3.1 Structurally identical to the Missense splice paths

SM 11 has the same **five color paths** as the Missense splice half (SM 6), each →
`SPL_`, running the same pipeline: **SPL_PRD** → **SPL_SPA** (splice assay) →
**SPL_FXN** (functional, SM 20) → **SPL_INF** (informative, SM 19) → **`SPL_`**
total. The `SplicePredictionOutcome` values (`NMD_PREDICTED`, `FRAMESHIFT_NO_NMD`,
`SPLICE_NO_FRAMESHIFT`, `UNCERTAIN`, `UNLIKELY`), the `SplicePredictiveEvidence` /
`SpliceAssayEvidence` inputs, `SplicePredictor`, and `SpliceAssayResult` all apply
unchanged — only the *point values* and the *SPA semantics* differ (documented, not
computed).

### 3.2 The `Splice*` vocabulary is shared — hoist it to `splice.py`

Those five types already carry **generic** names (`Splice*`, not `MissenseSplice*`).
With a second consumer, they belong in a shared module. This increment moves them
**verbatim** (unchanged docstrings/fields) from `missense.py` into a new
`src/svcv4_model/splice.py`; `missense.py` and the new `canonical_splice.py` both
import from it. Because the class names, fields, and docstrings are unchanged, the
generated JSON Schemas for `SplicePredictiveEvidence` / `SpliceAssayEvidence` are
**byte-identical** (no drift), and `__all__` is unchanged for those five names.
Only `MissenseSpliceAssessment` stays in `missense.py` (it is missense-specific).

### 3.3 Per-path point values differ (documented on the page)

- **yellow (NMD):** SPL_PRD **+6.0** → SM 18 matrix → `0.0 to +6.0`. (In missense the
  yellow initial was +3.0 — this is a genuine per-workflow difference.)
- **upper/lower orange (frameshift / no-frameshift, no NMD):** SPL_PRD `−1.0 to +6.0`
  from a critical-amino-acid table (lower orange adds a protein-deletion in-silico
  tool `+0.5 / −0.5`) → SM 18 → `−1.0 to +6.0`.
- **blue (uncertain):** SPL_PRD **0.0** (no SM 18).
- **violet (unlikely):** SPL_PRD **−1.0** (no SM 18).

### 3.4 SPA semantics and parent ranges differ from Missense

- **SPA (yellow/orange):** the assay **reduces** SPL_PRD (near-complete → 0;
  substantial → −25%; incomplete/none → −100%) — the *opposite* of the missense
  splice paths, where it scaled up. **blue:** additive `−2.0 to +2.0`. **violet:**
  benignity `−2.0 to 0.0` (held PRD+SPA `−3.0 to 0.0`).
- **held combined:** PRD+SPA+FXN capped `−8.0 to +9.0` (yellow/orange), `−8.0 to
  +8.0` (blue), `−8.0 to 0.0` (violet, with SPL_FXN itself capped `−8.0 to 0.0`).
- **parent `SPL_` totals:** yellow/orange `−8.0 to +10.0`; **blue `−8.0 to +8.0`;
  violet `−8.0 to 0.0`.** (Note: the missense splice half had these two *swapped*
  — blue `−8.0 to 0.0`, violet `−8.0 to +8.0`; canonical is the reverse.) The violet
  SPL_INF is restricted to **B/LB only**.

### 3.5 A standalone assessment mirroring `MissenseSpliceAssessment`

`CanonicalSpliceAssessment` is **field-identical** to `MissenseSpliceAssessment`
(prediction_outcome, predictive, mechanism_exon_relevance, splice_assay, functional,
informative, prd/spa/fxn/inf points, the two held-combined values, spl_total; no
`parent_code` — the code is always `SPL_`). Standalone PFD payload — **no**
`Workflow` enum entry, no applicability matrix; `case-model.md` unaffected. GoF
effects are out of scope in SM 11.

## 4. Scope

**In scope:**

- **Refactor:** new `src/svcv4_model/splice.py` holding the five verbatim `Splice*`
  types; `missense.py` imports them from there; `tests/test_missense.py` and
  `__init__.py` import sources updated (§5.1).
- New module `src/svcv4_model/canonical_splice.py`: `CanonicalSpliceAssessment`
  (§5.2).
- Export `CanonicalSpliceAssessment` from `__init__.py` (§5.3).
- Regenerate JSON Schemas — **one** new file; the five moved classes' files are
  byte-identical (§5.4).
- Docs: new `docs/workflows/pfd/canonical-splice.md` (+ nav + link),
  `spec-alignment.md` SM 11 row, `known-gaps.md` PFD row, `model.md` (§5.5).
- Tests: new `tests/test_canonical_splice.py` (§5.6).

**Out of scope / deferred:**

- The critical-domain criticality flag (with SM 7 Critical Amino Acids).
- Gain-of-function splice variants (SM 11 excludes them).
- All point computation (per-path ranges, SPA scaling, the SM 18 reduction, sums).

## 5. Content changes, item by item

### 5.1 Refactor: hoist `Splice*` into `src/svcv4_model/splice.py`

Create `src/svcv4_model/splice.py` with this header, then **move the five classes
verbatim** (lines 135–212 of the current `missense.py`: `SplicePredictionOutcome`,
`SplicePredictor`, `SpliceAssayResult`, `SplicePredictiveEvidence`,
`SpliceAssayEvidence` — unchanged docstrings, fields, and the inline comment):

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


# <the five classes, moved verbatim from missense.py>
```

Then edit `src/svcv4_model/missense.py`:

- **Delete** the five class definitions (they now live in `splice.py`).
- **Add** the import (in module order, after `mechanism`): `from svcv4_model.splice
  import (SpliceAssayEvidence, SplicePredictionOutcome, SplicePredictiveEvidence)` —
  the three that `MissenseSpliceAssessment` references. (`SplicePredictor` and
  `SpliceAssayResult` are used only *inside* the moved models, so `missense.py` does
  not import them directly.)
- Leave `MissenseSpliceAssessment`, the amino-acid path, and the comparison in place.

Edit `tests/test_missense.py`: change the `Splice*` imports from
`from svcv4_model.missense import (...)` to `from svcv4_model.splice import
(SpliceAssayEvidence, SpliceAssayResult, SplicePredictionOutcome,
SplicePredictiveEvidence, SplicePredictor)` (keep the `Missense*` imports from
`svcv4_model.missense`).

**Invariant:** after this refactor, `uv run pytest` is green, `ruff` clean, and the
schema/docs drift gate is **clean with no changes** — the move is verbatim, so
`schemas/json/SplicePredictiveEvidence.schema.json` and
`schemas/json/SpliceAssayEvidence.schema.json` regenerate byte-identical, and
`__all__` is unchanged. (Commit the refactor separately, verifying `git diff --quiet
-- schemas/json` before proceeding.)

### 5.2 New model: `src/svcv4_model/canonical_splice.py`

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

### 5.3 Export (`src/svcv4_model/__init__.py`)

- Change the import **source** of the five `Splice*` names from `svcv4_model.missense`
  to `svcv4_model.splice` (add a `from svcv4_model.splice import (...)` block in
  module order — `splice` sorts after `proposition`/`population`, before `statement`
  — and remove those five names from the `missense` import block). The `missense`
  block keeps `Missense*` names. `__all__` is **unchanged** for the five names.
- Add `from svcv4_model.canonical_splice import CanonicalSpliceAssessment` in module
  order (`canonical_splice` sorts **before `case`** — `canon` < `case`) and add
  `"CanonicalSpliceAssessment"` to `__all__` in sorted position (before the `Case*`
  entries — `Canon` < `Case`). Confirm exact neighbors with `sorted()` at
  implementation time. `__all__` is hand-sorted.

### 5.4 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **one** new file —
`CanonicalSpliceAssessment.schema.json` (which `$ref`s `SplicePredictiveEvidence`,
`SpliceAssayEvidence`, the reused submodules, and the enums under `$defs`). The five
moved classes' schema files (`SplicePredictiveEvidence`, `SpliceAssayEvidence`, and
the enums as `$defs`) are **byte-identical** (verbatim move). `MissenseSpliceAssessment`
and `MissenseAssessment` schemas are unchanged (they still `$ref` the same classes).
**`git add` the one new file.** `export_case_views.py` / `case-model.md` unaffected.
CI drift gate: `git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.5 Docs

- **`docs/workflows/pfd/canonical-splice.md`** (new) — the Canonical Splice workflow
  page. Document the five paths (a table: path → SPL_PRD initial → SPL_ total), the
  shared SPL_PRD → SPL_SPA → SPL_FXN → SPL_INF → `SPL_` pipeline, the SM 18 matrix
  (yellow/orange positive PRD only), the SPA **reduce** semantics for yellow/orange
  (vs additive blue, benignity violet), the SM 20 (FXN) and SM 19 (INF) reuse (violet
  INF is B/LB only), the two held-combined values, and the parent ranges (yellow/
  orange `−8..+10`; blue `−8..+8`; violet `−8..0`). Note it shares the `Splice*`
  vocabulary with the Missense splice page and that the point values / SPA direction
  differ. GoF out of scope. All *documented, not computed*.
- **`mkdocs.yml`** — add `- Canonical Splice (SPL_): workflows/pfd/canonical-splice.md`
  under the PFD nav section (after `workflows/pfd/inframe-indel.md`).
- **`docs/workflows/pfd/index.md`** — in the scaffold section's closing note, add
  Canonical Splice to the modeled per-variant-type workflows.
- **`docs/reference/spec-alignment.md`** — SM 11 row: from "Not yet modeled" to
  "Modeled (inputs) — `CanonicalSpliceAssessment` (five color paths → `SPL_`, reusing
  the shared `Splice*` vocabulary + SM 18/19/20)".
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: Canonical Splice
  now joins the modeled variant-type workflows.
- **`docs/reference/model.md`** — add `::: svcv4_model.CanonicalSpliceAssessment`
  after the `InframeIndelAssessment` entry.

### 5.6 Tests: `tests/test_canonical_splice.py`

- Round-trip a maximal `CanonicalSpliceAssessment` (a `prediction_outcome`, a
  `SplicePredictiveEvidence` (with a `SplicePredictor`), a `MechanismExonRelevanceEvidence`
  (populated), a `SpliceAssayEvidence` (with a `SpliceAssayResult`), a
  `FunctionalAssayEvidence`, a **populated** `InformativeVariantsEvidence`, all point
  fields including both combined) through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields.
- Importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (existing suite after the refactor + new tests).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean: after the refactor the five moved schemas show **no diff**; after
  the new module, only the one new file is added and committed:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes (new page in nav; no broken links).

## 7. Follow-up backlog

1. The critical-domain criticality flag with **SM 7** Critical Amino Acids.
2. The remaining variant-type workflows (Intronic/Synonymous SM 12, Start/Stop loss
   SM 15/16, Exon del/dup SM 13/14).
3. The full PFD scoring computation.

## 8. Delivery

Branch `feat/pfd-canonical-splice` off `main`. Single PR for this workflow (the
`splice.py` refactor + the new workflow). CI: pytest, ruff, the schema/docs drift
gate, `mkdocs build --strict`.
