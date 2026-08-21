"""SVCv4 Intronic & Synonymous variants workflow (SM 12).

Intronic variants (excluding the essential ±1,2 GT/AG splice sites) and synonymous
variants are evaluated for their splicing potential and resolve to the SPL_ parent
code via one of five paths (NMD / frameshift-no-NMD / no-frameshift / uncertain /
unlikely), each running the shared splice pipeline — predictive (SPL_PRD) → splice
assay (SPL_SPA) → functional (SPL_FXN, SM 20) → informative (SPL_INF, SM 19) → the
capped SPL_ total. Field-identical to the canonical splice assessment (SM 11); the
SM 12 point values track the missense splice half (SM 6) and are documented, not
computed.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
)


class IntronicSynonymousAssessment(BaseModel):
    """An intronic / synonymous variant (SPL_) assessment (SM 12).

    One entity for all five splice paths, parameterized by ``prediction_outcome``;
    reuses the shared splice vocabulary and the SM 18/19/20 submodules. Permissive
    superset; the per-path pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: SplicePredictionOutcome | None = Field(
        default=None, description="Which of the five splice prediction paths applies."
    )
    predictive: SplicePredictiveEvidence | None = Field(
        default=None, description="The SPL_PRD splice-prediction step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    splice_assay: SpliceAssayEvidence | None = Field(
        default=None, description="SM 12 splice-assay evidence (SPL_SPA)."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (SPL_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (SPL_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded SPL_PRD point value.")
    spa_points: float | None = Field(default=None, description="Coded SPL_SPA point value.")
    fxn_points: float | None = Field(default=None, description="Coded SPL_FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded SPL_INF point value.")
    prd_spa_combined: float | None = Field(
        default=None, description="Held SPL_PRD + SPL_SPA combined value."
    )
    prd_spa_fxn_combined: float | None = Field(
        default=None, description="Held SPL_PRD + SPL_SPA + SPL_FXN combined value."
    )
    spl_total: float | None = Field(
        default=None, description="Capped SPL_ parent-code total for this path."
    )
