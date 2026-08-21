"""SVCv4 Start-Lost variants workflow (SM 15).

A start-lost VBC disrupts the initiator methionine (MET) codon. It resolves to a NUL_ or
CDS_ parent code via one of three branches selected at the first branch point by the
alternative start codon: none-or-blocked (yellow → NUL_), potential-but-unproven (orange →
CDS_), or experimentally-proven-functional (violet → CDS_). The yellow/orange branches run
the shared pipeline — predictive (PRD) adjusted by the SM 18 mechanism/exon matrix,
functional (FXN, SM 20), informative (INF, SM 19), parent total; the violet branch awards a
fixed -1.0, skips SM 18, and restricts FXN and INF to benignity. This module captures the
analyst's inputs; the scoring is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class StartLostOutcome(StrEnum):
    """Which of the three start-lost branches applies to the VBC (SM 15)."""

    NO_ALT_START = "NO_ALT_START"
    ALT_START_UNPROVEN = "ALT_START_UNPROVEN"
    ALT_START_FUNCTIONAL = "ALT_START_FUNCTIONAL"


class StartLostPredictiveEvidence(BaseModel):
    """The start-lost predictive (PRD) step of a branch (SM 15).

    No-alt-start (yellow) starts at +6.0; the potential-alt-start (orange) branch derives
    initial points from the fraction of protein lost if the alternative start is used; the
    functional-alt-start (violet) branch starts at -1.0 and skips the SM 18 matrix. Positive
    points on the yellow/orange branches are reduced by the SM 18 matrix.
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None,
        description="Predictive basis (e.g. no alt-start; % protein lost; proven alt-start).",
    )
    initial_points: float | None = Field(
        default=None, description="Initial PRD points before the SM 18 adjustment."
    )
    alternative_start_present: bool | None = Field(
        default=None, description="A potential alternate in-frame MET start codon exists."
    )
    rescue_blocked_by_ptc: bool | None = Field(
        default=None,
        description="P/LP PTC variants between the VBC and the alt-MET make rescue unlikely.",
    )
    protein_fraction_lost: float | None = Field(
        default=None,
        description="Fraction of protein lost if the alternative start is used (orange table).",
    )
    alternative_start_functional: bool | None = Field(
        default=None,
        description="The alternative start codon is experimentally shown functional (violet).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class StartLostAssessment(BaseModel):
    """A start-lost (NUL_/CDS_) assessment (SM 15).

    One entity for all three branches, parameterized by ``prediction_outcome``; reuses the
    SM 18/19/20 submodules and the shared ``PfdParentCode`` (NUL/CDS). Permissive superset;
    the per-branch pipeline and its caps are documented, not computed. Informative variants
    are restricted (in prose) to the +1/+2/+3 MET-codon positions.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: StartLostOutcome | None = Field(
        default=None, description="Which of the three start-lost branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL or CDS per branch)."
    )
    predictive: StartLostPredictiveEvidence | None = Field(
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
