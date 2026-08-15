# SM 18 Molecular Mechanism & Exon Relevance — Design Spec

**Date:** 2026-08-14
**Status:** Proposed
**Builds on:** the three shipped capture-only model increments —
`2026-08-13-gene-disease-validity-design.md` (PR #23),
`2026-08-13-pop-modeling-design.md` (PR #25),
`2026-08-13-cln-aff-sm4-fields-design.md` (PR #26). Same **capture + document,
do not compute** stance.

## 1. Purpose & goal

**First sub-increment of PFD (Predictive & Functional Data).** PFD is too large
for one spec; it decomposes into three shared submodules (SM 18 Molecular
Mechanism & Exon Relevance, SM 19 Informative Variants, SM 20 Functional Assays)
plus the per-variant-type workflows that compose them. This spec models the
**SM 18 shared submodule** — the mechanism × exon-relevance multiplier that
*every* PFD variant-type workflow applies to its predictive (PRD) points.

Scope is capture-only: model the structured inputs a curator records
(mechanism level, exon-relevance category, MANE status, two override flags) and
**document** the multiplier; compute no points. This continues the Gene-Disease
Validity work (PR #23): SM 18's mechanism step is gated on GDV, which is already
captured on `WorkflowParameters.gene_disease_validity`.

## 2. Source material (this pass)

- **Supplementary Material 18 (Molecular Mechanism and Exon Relevance)**,
  verbatim in
  `source-material/svcv4-supplements/SM18-molecular-mechanism-exon-relevance.txt`
  (gitignored). Load-bearing passages:
  - "The levels are 'Established', 'Likely', 'Suspected', and 'Uncertain'. The
    mechanism framework should also only be used for human MDEs that have scored
    at moderate or higher level using the ClinGen gene gene-disease validity
    framework. MDEs that are Limited or below … should be considered as being
    'Uncertain' …"
  - "if the LoF mechanism assessment is 'Established', the initial evidence
    points can be used at full strength … 'Likely' … half … 'Suspected' … one
    fourth … 'Unlikely', 'Unknown' or has not been assessed … zeroed out."
  - Exon Relevance: "All" (×1.0), "Most" (×0.5), "Few" (×0); the 25% (Suspected)
    and 50% (Most) reductions are **not compounded**. Overrides: a known-
    irrelevant exon → ×0 (e.g. TRDN exons 9–41); an exon with expert/established
    pathogenic variants → no reduction. MANE Select / MANE Plus Clinical
    transcripts anchor the exon-relevance assessment.
- **Existing architecture:** `src/svcv4_model/population.py` (`PopulationEvidence`
  — the curation-level typed-payload precedent), `src/svcv4_model/case.py`
  (`WorkflowParameters.gene_disease_validity` — the GDV gate SM 18 depends on;
  `StrEnum` + `ConfigDict(extra="forbid")` patterns), `scripts/export_schemas.py`,
  `docs/workflows/pfd/index.md` (the PFD stub), `docs/reference/concepts.md`
  (the GDV entry that references SM 18).

## 3. Key findings driving this work

### 3.1 SM 18 is one matrix with two axes, applied to positive PRD points

The multiplier is mechanism-fraction × exon-relevance-fraction:

| GenCC mechanism | fraction | | Exon relevance | fraction |
|---|---|---|---|---|
| Established | ×1.0 | | All | ×1.0 |
| Likely | ×0.5 | | Most | ×0.5 |
| Suspected | ×0.25 | | Few | ×0 |
| Uncertain (incl. Unlikely/Unknown/not-assessed) | ×0 | | | |

Applied to positive predictive points only, before informative variants; the
two reductions are not compounded. **This model captures the two axes + the
override flags and documents the table; it computes nothing.**

### 3.2 The mechanism axis is gated on Gene-Disease Validity (already shipped)

SM 18: the mechanism framework is usable only for MDEs at **Moderate+**
gene-disease validity; Limited-or-below MDEs are treated as `UNCERTAIN` (→ ×0).
GDV is already captured as `WorkflowParameters.gene_disease_validity` (PR #23).
This spec **documents** that tie-in on the new entity; it does not enforce it.

### 3.3 Two named override cases are worth capturing as flags

SM 18 names two exon-relevance overrides that change the fraction independent of
the All/Most/Few call: a **known-irrelevant exon** (→ ×0) and an **exon
containing established pathogenic variants** (→ no reduction). Modeled as two
optional booleans (`exon_known_irrelevant`, `exon_has_established_pathogenic`).

### 3.4 PFD evidence is a separate payload, no Case applicability matrix

Like `PopulationEvidence`, this is a curation-level typed payload for a PFD
evidence item — **not** part of the `Case` model and **not** in the Case
applicability matrix (PFD has no `Workflow` enum entries). So `case-model.md`
and the per-workflow `case/*` schema views are unaffected; only a new
standalone `schemas/json/MechanismExonRelevanceEvidence.schema.json` is emitted.

## 4. Scope

**In scope:**
- New module `src/svcv4_model/mechanism.py`: `GenccMechanism`, `ExonRelevance`,
  `ManeStatus` enums + `MechanismExonRelevanceEvidence` (§5.1).
- Export the four public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — new `MechanismExonRelevanceEvidence.schema.json` (§5.3).
- Docs: `pfd/index.md`, `concepts.md`, `spec-alignment.md` (SM 18 row),
  `known-gaps.md` (PFD row), `model.md` (§5.4).
- Tests: new `tests/test_pfd_mechanism.py` (§5.5).

**Out of scope / deferred:**
- The multiplier computation (mechanism × exon-relevance → scaled PRD points).
- The PRD/FXN/INF/SPA sub-code scaffold and parent codes (NUL/CDS/SPL/MIS).
- The other shared submodules (SM 19 Informative Variants, SM 20 Functional
  Assays) — separate PFD sub-increments.
- All variant-type workflows and SM 7 (Critical Amino Acids).
- Per-tissue transcript abundance / pext scores beyond a MANE-status enum.

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/mechanism.py`

```python
"""SVCv4 PFD shared submodule — Molecular Mechanism & Exon Relevance (SM 18).

Every PFD variant-type workflow scales its predictive (PRD) points by a
mechanism × exon-relevance multiplier. This module captures that submodule's
inputs; the multiplier itself is documented (see docs/workflows/pfd/index.md),
not computed here. A curation-level payload for a PFD evidence item, like
``PopulationEvidence``.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class GenccMechanism(StrEnum):
    """GenCC level to which loss-of-function is established as the MDE's disease
    mechanism (SM 18). Full strength at ESTABLISHED, halved at LIKELY, quartered
    at SUSPECTED, zeroed at UNCERTAIN. Usable only for MDEs at Moderate+
    gene-disease validity (``WorkflowParameters.gene_disease_validity``);
    Limited-or-below is treated as UNCERTAIN.
    """

    ESTABLISHED = "ESTABLISHED"
    LIKELY = "LIKELY"
    SUSPECTED = "SUSPECTED"
    UNCERTAIN = "UNCERTAIN"


class ExonRelevance(StrEnum):
    """Clinical relevance of the exon containing (or affected by) the VBC across
    disease-relevant transcripts (SM 18): ALL (×1.0), MOST (×0.5), FEW (×0).
    """

    ALL = "ALL"
    MOST = "MOST"
    FEW = "FEW"


class ManeStatus(StrEnum):
    """MANE membership of the assessed transcript, anchoring exon relevance."""

    MANE_SELECT = "MANE_SELECT"
    MANE_PLUS_CLINICAL = "MANE_PLUS_CLINICAL"
    NEITHER = "NEITHER"


class MechanismExonRelevanceEvidence(BaseModel):
    """SM 18 mechanism × exon-relevance inputs for a PFD assessment.

    Permissive superset (every field optional). Captured; the multiplier
    (mechanism fraction × exon-relevance fraction, applied to positive PRD
    points, not compounded) is documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    gencc_mechanism: GenccMechanism | None = Field(
        default=None,
        description=(
            "GenCC level LoF is established as the disease mechanism; gated on "
            "Moderate+ gene-disease validity (see GenccMechanism)."
        ),
    )
    exon_relevance: ExonRelevance | None = Field(
        default=None,
        description="Clinical relevance of the VBC's exon across transcripts (All/Most/Few).",
    )
    mane_status: ManeStatus | None = Field(
        default=None, description="MANE membership of the assessed transcript."
    )
    exon_known_irrelevant: bool | None = Field(
        default=None,
        description=(
            "SM 18 override: the exon is known to be clinically irrelevant "
            "(e.g. TRDN exons 9-41), forcing exon relevance to zero."
        ),
    )
    exon_has_established_pathogenic: bool | None = Field(
        default=None,
        description=(
            "SM 18 override: the exon contains expert/established pathogenic "
            "variants, so no exon-relevance reduction is applied."
        ),
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `ExonRelevance`, `GenccMechanism`, `ManeStatus`,
`MechanismExonRelevanceEvidence` to the imports (new `from
svcv4_model.mechanism import (...)` block, placed by module order) and to
`__all__` (alphabetical). The three `StrEnum`s produce no schema file of their
own; only `MechanismExonRelevanceEvidence` (a `BaseModel`) does.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes a new
`schemas/json/MechanismExonRelevanceEvidence.schema.json` (the three enums
inline as `$defs`). `export_case_views.py` and `docs/workflows/case-model.md`
are **unaffected** (PFD is not a Case workflow). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/index.md`** — in the "shape of the remaining work",
  mark the SM 18 mechanism/exon-relevance submodule as **modeled** (inputs):
  describe `MechanismExonRelevanceEvidence`, the §3.1 multiplier table (documented,
  not computed), the GDV gate (§3.2), and link
  [SM 18](https://docs.google.com/document/d/1BLnsgxLY0TibwylFWz0SeGGeCusWwSokrgU4qsmBiaw/edit).
  Keep the rest of the PFD pipeline framed as still to come. **Also soften the
  top-of-page "Not yet modeled here" admonition** (which currently states PFD is
  flatly "not yet covered by this data model") so it no longer contradicts the
  now-modeled first submodule — e.g. "the first PFD submodule (SM 18) is now
  modeled; the rest of the pipeline is a later phase."
- **`docs/reference/concepts.md`** — the Gene-Disease Validity entry's SM 18
  upstream-gate paragraph gains a pointer to the now-modeled
  `MechanismExonRelevanceEvidence`. Add a one-line note that this entity
  intentionally has **no** `NOT_ASSESSED` mechanism member (unlike GDV's
  `NOT_CLASSIFIED`-vs-`None` distinction): SM 18 treats "not assessed" identically
  to `UNCERTAIN` (×0), so `None` = not captured vs `UNCERTAIN` = ×0 is a lossless
  split — the asymmetry with GDV is deliberate, not an oversight.
- **`docs/reference/spec-alignment.md`** — SM 18 row → "**Modeled (inputs)** —
  `MechanismExonRelevanceEvidence` captures mechanism level + exon relevance +
  MANE status; the multiplier is documented, not computed."
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" content-gap row
  notes the first PFD submodule (SM 18) is now modeled; the rest of the pipeline
  (PRD/FXN/INF scaffold, SM 19, SM 20, variant-type workflows) remains.
- **`docs/reference/model.md`** — add `::: svcv4_model.MechanismExonRelevanceEvidence`
  so the Model reference renders it (the pop.md-link lesson from PR #25).

### 5.5 Tests: `tests/test_pfd_mechanism.py`

- Round-trip a maximal `MechanismExonRelevanceEvidence` (all fields) through
  `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects an unknown field.
- Each `GenccMechanism`, `ExonRelevance`, `ManeStatus` value round-trips; the
  two boolean flags accept `True`/`False`.
- Importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_pfd_mechanism.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100 —
  keep field descriptions wrapped).
- Drift gate clean after committing the new schema:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes.

## 7. Follow-up backlog (the rest of PFD)

1. **SM 19 Informative Variants** and **SM 20 Functional Assays** — the other two
   shared submodules (each its own capture-only sub-increment).
2. **PFD scaffold**: parent codes (NUL/CDS/SPL/MIS) + PRD/FXN/INF/SPA sub-code
   structure + caps.
3. **Variant-type workflows** (Missense, Nonsense, Frameshift, Splice, …) +
   SM 7 (Critical Amino Acids), composing the submodules.
4. The multiplier + full PFD scoring computation (with the deferred rule/method
   enforcement).

## 8. Delivery

Branch `feat/pfd-sm18-mechanism` off `main`. Single PR. CI: pytest, ruff, the
schema/docs drift gate, `mkdocs build --strict`.
