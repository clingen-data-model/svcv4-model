"""SVCv4 Missense — amino-acid effect path (SM 6).

The "GREEN" upper path of the missense flow diagram, yielding the ``MIS_`` parent
code: a single calibrated in-silico predictor adjusted for transcript relevance
(MIS_PRD) → functional evidence (MIS_FXN, the shared SM 20 module) → the four
summable Grantham informative categories (MIS_INF) → the capped MIS_ total. The
splice paths (SPL_) and the MIS_-vs-SPL_ comparison are separate increments. This
module captures the analyst's inputs; the scoring is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import VariantClassification
from svcv4_model.mechanism import ExonRelevance


class MissensePredictor(StrEnum):
    """A calibrated in-silico missense predictor, pre-selected per VBC (SM 6)."""

    ALPHAMISSENSE = "ALPHAMISSENSE"
    BAYESDEL = "BAYESDEL"
    ESM1B = "ESM1B"
    MUTPRED2 = "MUTPRED2"
    REVEL = "REVEL"
    VARITY_R = "VARITY_R"
    VEST4 = "VEST4"
    OTHER_CALIBRATED = "OTHER_CALIBRATED"


class MissenseInfCategory(StrEnum):
    """One of the four summable MIS_INF informative-variant categories (SM 6)."""

    SAME_AA_PATHOGENIC = "SAME_AA_PATHOGENIC"
    DISTINCT_AA_PATHOGENIC = "DISTINCT_AA_PATHOGENIC"
    DISTINCT_AA_BENIGN = "DISTINCT_AA_BENIGN"
    SAME_AA_BENIGN = "SAME_AA_BENIGN"


class MissensePredictiveEvidence(BaseModel):
    """The amino-acid predictive (MIS_PRD) step: one calibrated predictor.

    Transcript relevance (ExonRelevance) reduces positive points; the molecular-
    mechanism axis is deliberately not applied on the missense amino-acid path,
    since predictors capture both loss- and gain-of-function effects.
    """

    model_config = ConfigDict(extra="forbid")

    predictor: MissensePredictor | None = Field(
        default=None, description="The single pre-selected calibrated predictor."
    )
    raw_score: float | None = Field(
        default=None, description="The predictor's raw score, if applicable."
    )
    initial_points: float | None = Field(
        default=None, description="Calibrated points before the transcript-relevance step."
    )
    transcript_relevance: ExonRelevance | None = Field(
        default=None,
        description="Exon presence across disease-relevant transcripts (All/Most/Few).",
    )
    adjusted_points: float | None = Field(
        default=None,
        description="Coded MIS_PRD points after transcript relevance (−4.0 to +4.0).",
    )


class MissenseInformativeVariant(BaseModel):
    """One MIS_INF informative variant in the same codon as the VBC (SM 6)."""

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None, description="Variant identifier (e.g. a ClinVar VCV).")
    category: MissenseInfCategory | None = Field(
        default=None, description="Which of the four summable MIS_INF categories applies."
    )
    classification: VariantClassification | None = Field(
        default=None, description="The informative variant's classification (P/LP/B/LB)."
    )
    grantham_wt_to_vbc: float | None = Field(
        default=None,
        description="Grantham distance wild-type → VBC amino acid (categories 2 & 3).",
    )
    grantham_wt_to_informative: float | None = Field(
        default=None,
        description="Grantham distance wild-type → informative amino acid (categories 2 & 3).",
    )


class MissenseInformativeEvidence(BaseModel):
    """The MIS_INF step: the summable informative variants for the VBC's codon."""

    model_config = ConfigDict(extra="forbid")

    variants: list[MissenseInformativeVariant] = Field(
        default_factory=list, description="Distinct informative variants; summed, not counted."
    )


class MissenseAminoAcidAssessment(BaseModel):
    """The missense amino-acid (MIS_) path assessment (SM 6).

    Mirrors the PFD scaffold but swaps in the missense-specific predictive step and
    the Grantham informative module, reusing the shared SM 20 functional module.
    Permissive superset; the pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    predictive: MissensePredictiveEvidence | None = Field(
        default=None, description="The MIS_PRD amino-acid predictive step."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (MIS_FXN)."
    )
    informative: MissenseInformativeEvidence | None = Field(
        default=None, description="The four-category Grantham informative evidence (MIS_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded MIS_PRD point value.")
    fxn_points: float | None = Field(default=None, description="Coded MIS_FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded MIS_INF point value.")
    prd_fxn_combined: float | None = Field(
        default=None, description="Held MIS_PRD + MIS_FXN combined value (−8.0 to +6.0)."
    )
    mis_total: float | None = Field(
        default=None, description="Capped MIS_ parent-code total (−8.0 to +9.0)."
    )
