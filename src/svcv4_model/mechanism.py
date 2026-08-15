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
