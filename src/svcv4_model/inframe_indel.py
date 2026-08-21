"""SVCv4 In-Frame InDel variants workflow (SM 10).

In-frame insertions, duplications, deletions, and insertion-deletions within a
single exon (length change a multiple of three) always resolve to the CDS_ parent
code via one of two branches: a simple sequence repeat (SSR / tandem repeat) or a
non-repeat InDel. Both run the same pipeline — predictive (PRD) → functional (FXN,
SM 20) → informative (INF, SM 19) → the CDS_ total — with the SM 18 mechanism/exon
matrix applied to the non-repeat branch's predictive points. This module captures
the analyst's inputs; the scoring is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class InframeIndelBranch(StrEnum):
    """Which of the two in-frame InDel branches applies to the VBC (SM 10)."""

    SIMPLE_SEQUENCE_REPEAT = "SIMPLE_SEQUENCE_REPEAT"
    NON_REPEAT = "NON_REPEAT"


class InframeIndelPredictiveEvidence(BaseModel):
    """The in-frame InDel predictive (CDS_PRD) step (SM 10).

    The SSR branch scores 0.0 (stable in controls) or −1.0 (polymorphic); the
    non-repeat branch derives initial points from the protein fraction removed / a
    critical domain / an indel in-silico predictor, then applies the SM 18 matrix.
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None, description="Predictive basis (e.g. repeat length; deleted fraction)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial CDS_PRD points before the SM 18 adjustment."
    )
    protein_fraction_reduced: float | None = Field(
        default=None,
        description="Fraction of protein removed (the non-repeat initial-points table).",
    )
    in_silico_predictor: str | None = Field(
        default=None,
        description="Indel in-silico predictor used (e.g. MutationTaster2021, PROVEAN).",
    )
    in_silico_calibrated: bool | None = Field(
        default=None,
        description="Whether the indel predictor is calibrated (calibrated reaches +2.0).",
    )
    repeat_stable_in_controls: bool | None = Field(
        default=None,
        description="SSR branch: the repeat is stable in large control sets (else polymorphic).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded CDS_PRD points after the SM 18 adjustment."
    )


class InframeIndelAssessment(BaseModel):
    """An in-frame InDel (CDS_) assessment (SM 10).

    One entity for both branches, parameterized by ``branch``; reuses the SM 18/19/20
    submodules and the shared ``PfdParentCode`` (always CDS here). Permissive
    superset; the per-branch pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    branch: InframeIndelBranch | None = Field(
        default=None, description="Which of the two in-frame InDel branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (always CDS for in-frame InDels)."
    )
    predictive: InframeIndelPredictiveEvidence | None = Field(
        default=None, description="The CDS_PRD predictive step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (CDS_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (CDS_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded CDS_PRD point value.")
    fxn_points: float | None = Field(default=None, description="Coded CDS_FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded CDS_INF point value.")
    prd_fxn_combined: float | None = Field(
        default=None, description="Held CDS_PRD + CDS_FXN combined value (no distinct code)."
    )
    parent_total: float | None = Field(
        default=None, description="Capped CDS_ parent-code total (−8.0 to +10.0)."
    )
