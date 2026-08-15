# SM 19 Informative Variants — Design Spec

**Date:** 2026-08-15
**Status:** Proposed
**Builds on:** the shipped capture-only increments — GDV (#23), POP (#25),
CLN_AFF (#26), and **SM 18 Mechanism & Exon Relevance (#28)**, the first PFD
submodule. Same **capture + document, do not compute** stance.

## 1. Purpose & goal

**Second PFD shared submodule.** SM 19 Informative Variants is one of the three
shared submodules (with SM 18 Mechanism & Exon Relevance, shipped, and SM 20
Functional Assays) that every PFD variant-type workflow composes. It captures
observations of variants *other than the VBC* that are informative for the VBC's
classification. Scope is capture-only: model the structured inputs and document
the SM 19 scoring; compute no points.

## 2. Source material (this pass)

- **Supplementary Material 19 (Informative Variants)**, verbatim in
  `source-material/svcv4-supplements/SM19-informative-variants.txt` (gitignored).
- **Existing architecture:** `src/svcv4_model/population.py` and
  `src/svcv4_model/mechanism.py` (the curation-level typed-payload precedents,
  including a list-of-sub-models shape via `Case.relatives`/`additional_variants`
  in `case.py`); `StrEnum` + `ConfigDict(extra="forbid")` conventions;
  `scripts/export_schemas.py`; `docs/workflows/pfd/index.md` (now shows the
  modeled SM 18 subsection to mirror).

## 3. Key findings driving this work

### 3.1 What an informative variant is

Verbatim (SM 19): "Informative variants are distinct from the VBC. Observation(s)
of a variant that is(are) the same as the VBC should be evaluated in the CLN_AFF
evidence category." They are "those that have a similar position to the VBC or a
similar effect. For some variant types, informative variants need to be in the
same exon"; whole-gene deletions "can have quite distinct breakpoints from the
VBC as long as it deletes the entire gene." So the **similarity basis** varies by
variant type: similar position, same exon, similar effect, or gene-deletion.

### 3.2 Scoring (documented, not computed)

Only **distinct** variants count — "A single observation counts the same as ten
observations." Points:

- **+2.0** for the first distinct P (Pathogenic) informative variant, **+1.0**
  each additional distinct P.
- If no P and only LP: **+1.0** first, **+1.0** each subsequent distinct LP.
- Benign/Likely-Benign informative variants contribute **negative** points
  (symmetrically) — SM 19 states positive P/LP values explicitly and a "-8 to
  +8" cap; the negative side is **inferred from the cap**, not spelled out as
  point values in the source. Docs should present it that way (not assert an
  unwritten rule).
- This evidence has "its own cap of -8 to +8."
- INF points are applied **after** the SM 18 matrix and are **not** reduced by it
  ("informative variants … should not be subject to the potential evidence
  reduction due to that matrix").

### 3.3 Eligibility gates worth capturing

1. **Distinct evidence from the VBC (load-bearing).** "We recommend only awarding
   INF points when the informative variant has different evidence codes and
   weights than the VBC" — two nonsense variants both LP by `NUL_PRD_+6` alone do
   not count; one with additional functional/clinical evidence does. Modeled as
   `distinct_evidence_from_vbc: bool | None`.
2. **External-source trust.** External P/LP assertions (ClinVar) are usable "only
   if they are three- or four-star variants and the analyst is satisfied that
   … circularity is avoided (i.e., that the VBC was not used as evidence to
   support the pathogenicity of the informative variant)." Modeled as
   `star_rating: int | None` and `circularity_checked: bool | None`.
3. **Allelic-MDE cross-use** (same mechanism) — documented only, not a field this
   pass (§7).

### 3.4 A structured classification enum is introduced

The scoring keys on P/LP vs B/LB, so a structured classification is load-bearing.
This spec introduces `VariantClassification`
(`PATHOGENIC`/`LIKELY_PATHOGENIC`/`VUS`/`LIKELY_BENIGN`/`BENIGN`). It is **not**
retrofitted onto the existing `CompoundHetVariant.classification` /
`AdditionalVariant.classification` placeholder strings (out of scope; generalize
later — §7).

### 3.5 PFD payload, no Case applicability matrix

Like SM 18 / POP, this is a curation-level typed PFD payload — not part of `Case`
and not in the Case applicability matrix. `case-model.md` and the per-workflow
`case/*` views are unaffected; only the new standalone schema files are emitted.

## 4. Scope

**In scope:**
- New module `src/svcv4_model/informative.py`: `VariantClassification`,
  `SimilarityBasis` enums; `InformativeVariant`; `InformativeVariantsEvidence`
  (§5.1).
- Export the four public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — new `InformativeVariant.schema.json` and
  `InformativeVariantsEvidence.schema.json` (§5.3).
- Docs: `pfd/index.md`, `spec-alignment.md` (SM 19 row), `known-gaps.md` (PFD
  row), `model.md` (§5.4).
- Tests: new `tests/test_pfd_informative.py` (§5.5).

**Out of scope / deferred:**
- The scoring computation (first-vs-additional tally, ±8 cap).
- `allelic_mde_cross_use` / `classified_per_recommendations` as structured fields
  (documented only).
- Generalizing `VariantClassification` to the existing placeholder-string
  classification fields.
- The other PFD pieces (SM 20 Functional Assays, SM 7, the PRD/FXN/INF scaffold,
  variant-type workflows).

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/informative.py`

```python
"""SVCv4 PFD shared submodule — Informative Variants (SM 19).

Observations of variants *other than the VBC* that inform the VBC's
classification. This module captures the structured inputs; the SM 19 scoring
(see docs/workflows/pfd/index.md) is documented, not computed. A curation-level
payload for a PFD evidence item, like ``MechanismExonRelevanceEvidence``.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class VariantClassification(StrEnum):
    """A variant's pathogenicity classification. Introduced for informative
    variants (SM 19), whose scoring keys on P/LP vs B/LB. Not (yet) applied to
    the placeholder ``classification`` strings on other Case sub-models.
    """

    PATHOGENIC = "PATHOGENIC"
    LIKELY_PATHOGENIC = "LIKELY_PATHOGENIC"
    VUS = "VUS"
    LIKELY_BENIGN = "LIKELY_BENIGN"
    BENIGN = "BENIGN"


class SimilarityBasis(StrEnum):
    """Why a variant is informative for the VBC (SM 19) — variant-type dependent."""

    SIMILAR_POSITION = "SIMILAR_POSITION"
    SAME_EXON = "SAME_EXON"
    SIMILAR_EFFECT = "SIMILAR_EFFECT"
    GENE_DELETION = "GENE_DELETION"


class InformativeVariant(BaseModel):
    """A single distinct variant (not the VBC) informative for the VBC's
    classification. Only distinct variants count; observation counts are
    irrelevant (SM 19).
    """

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None, description="Identifier for the informative variant.")
    classification: VariantClassification | None = Field(
        default=None,
        description="The informative variant's own pathogenicity classification.",
    )
    similarity_basis: SimilarityBasis | None = Field(
        default=None,
        description="Why it is informative for the VBC (position/exon/effect/deletion).",
    )
    distinct_evidence_from_vbc: bool | None = Field(
        default=None,
        description=(
            "Whether it reached its classification via different evidence codes/"
            "weights than the VBC — required for it to count (SM 19)."
        ),
    )
    star_rating: int | None = Field(
        default=None,
        description=(
            "ClinVar review star rating, for external classifications (usable "
            "only at 3-4 stars with circularity avoided)."
        ),
    )
    circularity_checked: bool | None = Field(
        default=None,
        description=(
            "Whether the analyst confirmed the VBC was not used as evidence for "
            "this variant's classification (circularity avoided)."
        ),
    )


class InformativeVariantsEvidence(BaseModel):
    """SM 19 informative-variants inputs for a PFD assessment.

    Captured; the scoring (+2.0 first distinct P / +1.0 each additional, cap
    ±8; mirror negatives for B/LB) is documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    variants: list[InformativeVariant] = Field(
        default_factory=list,
        description="0..many distinct informative variants (observation counts do not matter).",
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `InformativeVariant`, `InformativeVariantsEvidence`, `SimilarityBasis`,
`VariantClassification` to the imports (new `from svcv4_model.informative import
(...)` block placed by module order — `informative` sorts **after `evidence_line`
and before `inputs`**: `informative` < `inputs` because they diverge at char 3,
`f` < `p`) and to `__all__` (ASCII order). The two `StrEnum`s get no schema
file; both `BaseModel`s (`InformativeVariant`, `InformativeVariantsEvidence`) do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes two new files —
`InformativeVariant.schema.json` and `InformativeVariantsEvidence.schema.json`
(the latter references the former as a `$ref`; the two enums inline as `$defs`).
`export_case_views.py` and `case-model.md` are **unaffected** (PFD is not a Case
workflow). CI drift gate: `git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/index.md`** — add a modeled "Informative Variants ✅
  (inputs)" subsection mirroring the SM 18 one: describe `InformativeVariantsEvidence`
  / `InformativeVariant`, the §3.2 scoring (documented, not computed), the
  eligibility gates (§3.3), the "not reduced by the SM 18 matrix" note, and link
  [SM 19](https://docs.google.com/document/d/1hNfdtdvDT4dob9oDBrL_UzVV_MYiWnwERfli76EAbyQ/edit).
  Update the "remaining shared sub-modules" sentence to drop Informative Variants
  from the still-to-come list.
- **`docs/reference/spec-alignment.md`** — SM 19 row → "**Modeled (inputs)** —
  `InformativeVariantsEvidence` captures distinct informative variants
  (classification, similarity basis, eligibility flags); scoring documented, not
  computed."
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: note SM 19 is
  now modeled too; remaining = SM 20, SM 7, the PRD/FXN/INF scaffold, variant-type
  workflows, and the scoring computation.
- **`docs/reference/model.md`** — add `::: svcv4_model.InformativeVariantsEvidence`
  after the `MechanismExonRelevanceEvidence` entry.

### 5.5 Tests: `tests/test_pfd_informative.py`

- Round-trip a maximal `InformativeVariantsEvidence` (a populated `variants` list
  with a fully-filled `InformativeVariant`) through `model_dump(mode="json")` →
  `model_validate`.
- Permissive-empty validates (`variants == []`); `extra="forbid"` rejects unknown
  fields on both models.
- Each `VariantClassification` and `SimilarityBasis` value round-trips on an
  `InformativeVariant`.
- Importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_pfd_informative.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100 —
  keep field descriptions wrapped).
- Drift gate clean after committing the two new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes.

## 7. Follow-up backlog

1. **SM 20 Functional Assays** — the third shared PFD submodule.
2. **PFD scaffold** (parent codes NUL/CDS/SPL/MIS + PRD/FXN/INF/SPA), then the
   variant-type workflows composing all three submodules + SM 7.
3. Structure the deferred SM 19 eligibility fields (`allelic_mde_cross_use`,
   `classified_per_recommendations`) if needed.
4. Generalize `VariantClassification` to the existing placeholder `classification`
   strings on `CompoundHetVariant`/`AdditionalVariant`.
5. The full PFD scoring computation (with the deferred rule/method enforcement).

## 8. Delivery

Branch `feat/pfd-sm19-informative` off `main`. Single PR. CI: pytest, ruff, the
schema/docs drift gate, `mkdocs build --strict`.
