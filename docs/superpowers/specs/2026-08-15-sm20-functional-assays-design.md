# SM 20 Functional Assays — Design Spec

**Date:** 2026-08-15
**Status:** Proposed
**Builds on:** the shipped capture-only increments — GDV (#23), POP (#25),
CLN_AFF (#26), and the two prior PFD submodules **SM 18 (#28)** and
**SM 19 (#29)**. Same **capture + document, do not compute** stance.

## 1. Purpose & goal

**Third and last PFD shared submodule.** With SM 18 (Mechanism & Exon Relevance)
and SM 19 (Informative Variants) shipped, this completes the three shared
submodules every PFD variant-type workflow composes. SM 20 captures **functional
assay evidence** — the `*_FXN` contribution. Scope is capture-only: model the
structured inputs and document the SM 20 scoring/eligibility; compute no points.

## 2. Source material (this pass)

- **Supplementary Material 20 (Functional Assay Evidence)**, verbatim in
  `source-material/svcv4-supplements/SM20-functional-assays.txt` (gitignored).
- **Existing architecture:** `src/svcv4_model/informative.py` (the most recent
  typed-payload precedent, incl. a list-of-sub-models field and a new enum);
  `StrEnum` + `ConfigDict(extra="forbid")` conventions; `scripts/export_schemas.py`;
  `docs/workflows/pfd/index.md` (now shows two modeled submodule subsections to
  mirror).

## 3. Key findings driving this work

### 3.1 Two functional-evidence types

Verbatim (SM 20): "Two types of functional evidence are considered here:
Protein/cellular functional evidence and whole animal model evidence."

- **Protein/cellular** (enzyme kinetic, signal transduction, membrane
  conformation, MAVE): calibrated via an **OddsPath / likelihood ratio** (Brnich
  PMID 31892348; Tavtigian PMID 29300386). "It is essential … to use a set of
  controls that include multiple known pathogenic **and** benign variants for
  calibration." Evidence strength scales with control counts. Small experiments
  with **no false positives/negatives** use lookup Tables 1 (pathogenicity) & 2
  (benignity) ("Tables Lambda and Mu"); FP/FN, trichotomized, or MAVE
  experiments "must be calibrated using mathematical analyses that are beyond the
  scope of these recommendations" (→ expert; out of scope here).
- **Animal model** (engineered / naturally-occurring / complementation e.g.
  zebrafish rescue): "This type of evidence would be awarded as `***_FXN_0.0` to
  `+4.0`" per Table 3 ("Figure Lingonberry2"), weighted by phenotype replication
  (specific / key features), inheritance match, and (for some variant types)
  local sequence similarity. Requires the animal gene to be an established
  **ortholog**.

### 3.2 The mechanism-fidelity gate

The assay "must faithfully recapitulate the disease molecular mechanism." SM 20
divides mechanism into **loss-of-function** (complete/partial) vs
**alteration-of-function** (increased function / toxic gain-of-function /
dominant-negative). "If the analyst judges that the assay is not a faithful
recapitulation of the disease pathophysiology, it should be scored as
`MIS_FXN_0.0`." Modeled as `FunctionalAssayEvidence.disease_mechanism`
(`MolecularMechanism`, shared context) + a per-assay `fidelity_to_mechanism` bool.

### 3.3 Combination rules and carve-outs (documented)

- `*_FXN` scores **add** to `*_PRD`. Multiple-assay rules: same readout + same
  direction → strongest only; same readout + opposite direction → sum; distinct
  functions → the most disease-relevant. No functional data → `*_FXN_ND`.
- **Splice-assay carve-out:** RNA splicing assays (RT-PCR / RNAseq / minigene)
  are **not** `*_FXN` — they are `SPL_SPA`, handled in the splice flow diagrams
  (SM 6/11/12). Out of scope for this submodule.
- **Patient-derived samples** generally count as phenotype (`LOC_PHE`), not `_FXN`
  (three narrow exceptions) — documented, not modeled as fields this pass.

### 3.4 PFD payload, no Case applicability matrix

Like the other PFD submodules, this is a curation-level typed PFD payload — not
part of `Case`, not in the applicability matrix. `case-model.md` and the
per-workflow `case/*` views are unaffected; only new standalone schema files are
emitted.

## 4. Scope

**In scope:**
- New module `src/svcv4_model/functional.py`: `MolecularMechanism`,
  `ProteinAssayType`, `AnimalModelType`, `PhenotypeReplication` enums;
  `ProteinFunctionalAssay`, `AnimalModelEvidence`, `FunctionalAssayEvidence`
  (§5.1).
- Export the seven public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — three new files (§5.3).
- Docs: `pfd/index.md`, `spec-alignment.md` (SM 20 row), `known-gaps.md` (PFD
  row), `model.md` (§5.4).
- Tests: new `tests/test_pfd_functional.py` (§5.5).

**Out of scope / deferred:**
- The scoring computation (OddsPath→points, Table 1/2/3 lookups).
- The 3 patient-derived-sample exceptions as structured fields (documented only).
- Complete-vs-partial loss-of-function sub-distinction.
- The remaining PFD pieces (SM 7 Critical Amino Acids, the PRD/FXN/INF scaffold +
  parent codes, variant-type workflows).

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/functional.py`

```python
"""SVCv4 PFD shared submodule — Functional Assay Evidence (SM 20).

The ``*_FXN`` contribution: protein/cellular functional assays (OddsPath-
calibrated) and whole-animal-model evidence. This module captures the structured
inputs; the SM 20 scoring (see docs/workflows/pfd/index.md) is documented, not
computed. A curation-level payload for a PFD evidence item, like
``InformativeVariantsEvidence``.

RNA splicing assays (RT-PCR/RNAseq/minigene) are NOT modeled here — they are
``SPL_SPA`` evidence handled in the splice flow diagrams (SM 6/11/12).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class MolecularMechanism(StrEnum):
    """The MDE's molecular mechanism of disease that an assay must faithfully
    recapitulate to count (SM 20).
    """

    LOSS_OF_FUNCTION = "LOSS_OF_FUNCTION"
    INCREASED_FUNCTION = "INCREASED_FUNCTION"
    TOXIC_GAIN_OF_FUNCTION = "TOXIC_GAIN_OF_FUNCTION"
    DOMINANT_NEGATIVE = "DOMINANT_NEGATIVE"


class ProteinAssayType(StrEnum):
    """Kind of protein/cellular functional assay (SM 20)."""

    ENZYME_KINETIC = "ENZYME_KINETIC"
    SIGNAL_TRANSDUCTION = "SIGNAL_TRANSDUCTION"
    MEMBRANE_CONFORMATION = "MEMBRANE_CONFORMATION"
    MAVE = "MAVE"
    OTHER = "OTHER"


class AnimalModelType(StrEnum):
    """Kind of animal-model functional evidence (SM 20)."""

    ENGINEERED = "ENGINEERED"
    NATURALLY_OCCURRING = "NATURALLY_OCCURRING"
    COMPLEMENTATION = "COMPLEMENTATION"


class PhenotypeReplication(StrEnum):
    """How well the animal model replicates the human phenotype (SM 20, Table 3)."""

    SPECIFIC = "SPECIFIC"
    KEY_FEATURES = "KEY_FEATURES"
    NONE = "NONE"


class ProteinFunctionalAssay(BaseModel):
    """A protein/cellular functional assay, OddsPath-calibrated (SM 20).

    Requires both pathogenic and benign variant controls; small experiments with
    no false positives/negatives use lookup Tables 1/2 (documented, not computed).
    """

    model_config = ConfigDict(extra="forbid")

    assay_type: ProteinAssayType | None = Field(
        default=None, description="Kind of protein/cellular assay."
    )
    odds_path: float | None = Field(
        default=None,
        description="OddsPath / likelihood ratio from the calibrated truth set.",
    )
    has_pathogenic_controls: bool | None = Field(
        default=None, description="Whether known pathogenic variant controls were used."
    )
    has_benign_controls: bool | None = Field(
        default=None, description="Whether known benign variant controls were used."
    )
    pathogenic_control_count: int | None = Field(
        default=None, description="Number of pathogenic controls in the calibration set."
    )
    benign_control_count: int | None = Field(
        default=None, description="Number of benign controls in the calibration set."
    )
    has_false_positives_or_negatives: bool | None = Field(
        default=None,
        description=(
            "Whether the experiment had false positives/negatives (which route "
            "calibration to expert math, beyond the lookup tables)."
        ),
    )
    fidelity_to_mechanism: bool | None = Field(
        default=None,
        description="Whether the assay faithfully recapitulates the disease mechanism.",
    )


class AnimalModelEvidence(BaseModel):
    """Whole-animal-model functional evidence (SM 20); range *_FXN_0.0 to +4.0."""

    model_config = ConfigDict(extra="forbid")

    model_type: AnimalModelType | None = Field(
        default=None, description="Engineered / naturally-occurring / complementation."
    )
    species: str | None = Field(default=None, description="Model organism, e.g. mouse, zebrafish.")
    ortholog_established: bool | None = Field(
        default=None,
        description="Whether the animal gene is an established ortholog of the human gene.",
    )
    phenotype_replication: PhenotypeReplication | None = Field(
        default=None, description="How well the model replicates the human phenotype."
    )
    inheritance_match: bool | None = Field(
        default=None, description="Whether the inheritance pattern matches the human MDE."
    )
    local_sequence_similarity_high: bool | None = Field(
        default=None,
        description=(
            "Whether local sequence similarity around the VBC is high (for some "
            "variant types)."
        ),
    )
    fidelity_to_mechanism: bool | None = Field(
        default=None,
        description="Whether the model faithfully recapitulates the disease mechanism.",
    )


class FunctionalAssayEvidence(BaseModel):
    """SM 20 functional-assay inputs for a PFD assessment.

    Captured; the scoring (OddsPath→points via Tables 1/2 for protein assays;
    Table 3's 0.0 to +4.0 for animal models; the combination rules) is
    documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    disease_mechanism: MolecularMechanism | None = Field(
        default=None,
        description="The MDE's molecular mechanism the assays are evaluated against.",
    )
    protein_assays: list[ProteinFunctionalAssay] = Field(
        default_factory=list, description="0..many protein/cellular functional assays."
    )
    animal_models: list[AnimalModelEvidence] = Field(
        default_factory=list, description="0..many animal-model functional evidence entries."
    )
```

After creating the module, run `uv run ruff format src/svcv4_model/functional.py`
(not just `--check`) to normalize any field-description wrapping to ruff's
canonical form before committing — the `description=(...)` blocks above are
illustrative and ruff may collapse the shorter ones to a single line.

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add a new `from svcv4_model.functional import (...)` block placed by module order
(`functional` sorts after `evidence_line` and before `informative` —
`functional` < `informative` at char 1, `f` < `i`). Export `AnimalModelEvidence`,
`FunctionalAssayEvidence`, `MolecularMechanism`, `PhenotypeReplication`,
`ProteinAssayType`, `ProteinFunctionalAssay`, and `AnimalModelType` in the imports
and `__all__` (ASCII order — or run `ruff check --fix`). The four `StrEnum`s get no
schema file; the three `BaseModel`s do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes three new files —
`FunctionalAssayEvidence.schema.json`, `ProteinFunctionalAssay.schema.json`,
`AnimalModelEvidence.schema.json` (the former `$ref`s the latter two; the enums
inline as `$defs`). `export_case_views.py` and `case-model.md` are **unaffected**
(PFD is not a Case workflow). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/index.md`** — add a modeled "Functional Assays ✅ (inputs)"
  subsection mirroring the SM 18/19 ones: describe the entity + the two sub-models
  and their fields; the documented scoring (protein: OddsPath needing P+B controls,
  Tables 1/2 for small no-FP/FN experiments, FP/FN/MAVE → expert; animal: Table 3
  range 0.0–+4.0); the fidelity gate; the multiple-assay combination rules; the
  `*_FXN` adds-to-`*_PRD` note; and the **splice-assay carve-out** (`SPL_SPA`, not
  `_FXN`). Link
  [SM 20](https://docs.google.com/document/d/1X68otBl4YvdXlP1bOD83JO4kIod0Ol5BoLB4CLxqijA/edit).
  Update the "remaining shared sub-modules (Functional Assays, Determining Critical
  Amino Acids)" sentence to drop Functional Assays (leaving only Determining
  Critical Amino Acids), and note **all three shared submodules are now modeled**.
- **`docs/reference/spec-alignment.md`** — SM 20 row → "**Modeled (inputs)** —
  `FunctionalAssayEvidence` captures protein/cellular assays (OddsPath, controls)
  and animal-model evidence; scoring documented, not computed."
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: all three
  shared submodules (SM 18/19/20) modeled; remaining = SM 7, the PRD/FXN/INF
  scaffold + parent codes, the variant-type workflows, and the scoring computation.
- **`docs/reference/model.md`** — add `::: svcv4_model.FunctionalAssayEvidence`
  after the `InformativeVariantsEvidence` entry.

### 5.5 Tests: `tests/test_pfd_functional.py`

- Round-trip a maximal `FunctionalAssayEvidence` (both lists populated, each
  sub-model fully filled) through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates (both lists `[]`); `extra="forbid"` rejects unknown
  fields on all three models.
- Each enum (`MolecularMechanism`, `ProteinAssayType`, `AnimalModelType`,
  `PhenotypeReplication`) value round-trips on its sub-model.
- Importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_pfd_functional.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100 —
  keep field descriptions wrapped).
- Drift gate clean after committing the three new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes.

## 7. Follow-up backlog

1. **SM 7 Critical Amino Acids** — the small shared helper feeding PRD.
2. **PFD scaffold**: parent codes (NUL/CDS/SPL/MIS) + PRD/FXN/INF/SPA sub-code
   structure, then the variant-type workflows composing all shared submodules.
3. Structure the deferred SM 20 detail (the 3 patient-derived-sample exceptions;
   complete-vs-partial LoF).
4. The full PFD scoring computation (OddsPath→points, Table lookups) with the
   deferred rule/method enforcement.

## 8. Delivery

Branch `feat/pfd-sm20-functional` off `main`. Single PR. CI: pytest, ruff, the
schema/docs drift gate, `mkdocs build --strict`.
