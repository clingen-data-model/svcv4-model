"""SVCv4 Single/Multi-Exon Deletion variants workflow (SM 13).

Deletions of one or more exons up to an entire single gene resolve to a NUL_ or
CDS_ parent code via one of six branches selected by a decision tree (whole-gene? /
includes the first coding exon? / NMD predicted? / alternative in-frame start codon
and its functionality). All six run the same pipeline — predictive (PRD) →
functional (FXN, SM 20) → informative (INF, SM 19) → parent total — with the SM 18
mechanism/exon matrix applied to the predictive points (mechanism-only for the
whole-gene branch). This module captures the analyst's inputs; the scoring is
documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class ExonDeletionOutcome(StrEnum):
    """Which of the six exon-deletion branches applies to the VBC (SM 13)."""

    WHOLE_GENE = "WHOLE_GENE"
    SUBGENIC_NMD = "SUBGENIC_NMD"
    SUBGENIC_NO_NMD = "SUBGENIC_NO_NMD"
    START_CODON_NO_ALT_START = "START_CODON_NO_ALT_START"
    START_CODON_ALT_START_UNPROVEN = "START_CODON_ALT_START_UNPROVEN"
    START_CODON_ALT_START_FUNCTIONAL = "START_CODON_ALT_START_FUNCTIONAL"


class ExonDeletionPredictiveEvidence(BaseModel):
    """The exon-deletion predictive (PRD) step of a deletion branch (SM 13).

    Whole-gene starts at +10.0; the NMD / start-exon branches at +6.0; the no-NMD
    and unproven-alt-start branches derive initial points from the fraction of
    protein removed; the functional-alt-start branch starts at −1.0. Positive points
    are reduced by the SM 18 matrix (mechanism-only for whole-gene).
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None, description="Predictive basis (e.g. whole-gene LoF; NMD; % protein lost)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial PRD points before the SM 18 adjustment."
    )
    protein_fraction_removed: float | None = Field(
        default=None,
        description="Fraction of protein removed (the violet/blue initial-points table).",
    )
    alternative_start_functional: bool | None = Field(
        default=None,
        description="Demonstrated functional alternative in-frame start (the grey branch).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class ExonDeletionAssessment(BaseModel):
    """A single/multi-exon deletion (NUL_/CDS_) assessment (SM 13).

    One entity for all six branches, parameterized by ``prediction_outcome``; reuses
    the SM 18/19/20 submodules and the shared ``PfdParentCode`` (NUL/CDS). Permissive
    superset; the per-branch pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: ExonDeletionOutcome | None = Field(
        default=None, description="Which of the six exon-deletion branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL or CDS per branch)."
    )
    predictive: ExonDeletionPredictiveEvidence | None = Field(
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
