"""SVCv4 PFD scaffold — the shared, variant-agnostic assessment structure.

Every PFD variant-type workflow (missense, nonsense, splice, …) produces a
parent-code score from the same pipeline: predictive (PRD) → adjust by molecular
mechanism / exon relevance (SM 18) → functional (SM 20) → informative (SM 19) →
parent-code total, with a splice-only splice-assay (SPA) step. This module
captures one parent code's assessment, embedding the three shared submodules;
the scoring (see docs/workflows/pfd/index.md) is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence


class PfdParentCode(StrEnum):
    """The PFD parent evidence code a variant-type workflow resolves to (SM 1)."""

    NUL = "NUL"
    CDS = "CDS"
    SPL = "SPL"
    MIS = "MIS"
    NCG = "NCG"
    REG = "REG"


class PfdPredictiveEvidence(BaseModel):
    """The predictive (PRD) step of a PFD assessment.

    Variant-type-agnostic shape: an in-silico prediction, its SM 18 transcript-
    relevance / mechanism adjustment, and the resulting coded ``_PRD`` value.
    Typed predictor/path enums arrive with the per-variant-type workflows.
    """

    model_config = ConfigDict(extra="forbid")

    predictor: str | None = Field(
        default=None, description="In-silico predictor or basis used (e.g. REVEL, NMD prediction)."
    )
    raw_score: float | None = Field(
        default=None, description="The predictor's raw score, if applicable."
    )
    initial_points: float | None = Field(
        default=None, description="Initial evidence points before the SM 18 adjustment."
    )
    path_label: str | None = Field(
        default=None, description="Flow-diagram path/color (e.g. GREEN, YELLOW); typed later."
    )
    transcript_relevance_applied: bool | None = Field(
        default=None,
        description="Whether the SM 18 transcript-relevance step reduced the points.",
    )
    mechanism_applied: bool | None = Field(
        default=None,
        description=(
            "Whether the SM 18 mechanism step applied (not for the missense "
            "amino-acid path, where predictors capture both LoF and GoF)."
        ),
    )
    adjusted_points: float | None = Field(
        default=None,
        description="Coded _PRD points after the SM 18 adjustment.",
    )


class PfdCodeAssessment(BaseModel):
    """One PFD parent-code assessment: the shared pipeline's captured inputs.

    Embeds the three shared submodules (SM 18/19/20) and captures the coded
    sub-code point values and the parent total. Permissive superset; the scoring
    (the pipeline, its caps, the held separate+combined values, the _ND coding)
    is documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    parent_code: PfdParentCode | None = Field(
        default=None, description="The parent evidence code this assessment resolves to."
    )
    predictive: PfdPredictiveEvidence | None = Field(
        default=None, description="The predictive (_PRD) step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded _PRD point value.")
    spa_points: float | None = Field(
        default=None, description="Coded _SPA (splice-assay) point value; splice paths only."
    )
    fxn_points: float | None = Field(default=None, description="Coded _FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded _INF point value.")
    parent_total: float | None = Field(
        default=None, description="Capped parent-code total for this assessment."
    )
