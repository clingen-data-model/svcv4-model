"""SVCv4 Stop-Lost variants workflow (SM 16).

A stop-lost (nonstop / readthrough / nonstop-extension) VBC disrupts the normal stop codon
so it encodes an amino acid, extending the ORF. It resolves to a NUL_ or CDS_ parent code
via one of two branches split on the non-stop decay (NSD) prediction: NSD predicted (yellow
→ NUL_) or not (orange → CDS_). Both run the shared pipeline — predictive (PRD) adjusted by
the SM 18 mechanism/exon matrix, functional (FXN, SM 20), informative (INF, SM 19), parent
total. The orange initial points come from a four-tier scale over the functional evidence
of similar variants and the predicted extension length. This module captures the analyst's
inputs; the scoring is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class StopLostOutcome(StrEnum):
    """Which of the two stop-lost branches applies to the VBC (SM 16)."""

    NSD_PREDICTED = "NSD_PREDICTED"
    NO_NSD = "NO_NSD"


class StopLostInterference(StrEnum):
    """Functional evidence of interference from similar stop-lost variants (SM 16, orange)."""

    LOSS_OF_FUNCTION = "LOSS_OF_FUNCTION"
    SOME_INTERFERENCE = "SOME_INTERFERENCE"
    NONE = "NONE"


class StopLostPredictiveEvidence(BaseModel):
    """The stop-lost predictive (PRD) step of a branch (SM 16).

    NSD-predicted (yellow) starts at +4.0. The no-NSD (orange) branch derives initial points
    from a four-tier scale: loss-of-function in similar variants -> +4.0; some interference
    AND extension >=30 aa -> +3.0; some interference OR extension >=30 aa -> +2.0; no
    functional data -> 0.0. Positive points are then reduced by the SM 18 matrix.
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None,
        description="Predictive basis (e.g. NSD predicted; extension length; interference).",
    )
    initial_points: float | None = Field(
        default=None, description="Initial PRD points before the SM 18 adjustment."
    )
    nsd_predicted: bool | None = Field(
        default=None,
        description="No in-frame stop before the polyA site -> non-stop decay (the yellow gate).",
    )
    similar_variant_interference: StopLostInterference | None = Field(
        default=None,
        description="Functional evidence of interference from similar variants (orange tier).",
    )
    extension_length_aa: int | None = Field(
        default=None,
        description="Predicted extension in amino acids past the native stop (>=30 threshold).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class StopLostAssessment(BaseModel):
    """A stop-lost (NUL_/CDS_) assessment (SM 16).

    One entity for both branches, parameterized by ``prediction_outcome``; reuses the
    SM 18/19/20 submodules and the shared ``PfdParentCode`` (NUL/CDS). Permissive superset;
    the per-branch pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: StopLostOutcome | None = Field(
        default=None, description="Which of the two stop-lost branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL or CDS per branch)."
    )
    predictive: StopLostPredictiveEvidence | None = Field(
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
