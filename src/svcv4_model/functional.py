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
            "Whether local sequence similarity around the VBC is high (for some variant types)."
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
