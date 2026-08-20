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
