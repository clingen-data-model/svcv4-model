"""SVCv4 shared splice vocabulary (PFD).

The splice prediction outcome, predictor, assay result, and the SPL_PRD /
SPL_SPA evidence models are shared by every PFD workflow that has a splice path —
the Missense splice half (SM 6) and Canonical Splice variants (SM 11). They are
capture-only; the per-workflow point values and splice-assay semantics are
documented on each workflow page, not computed here.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SplicePredictionOutcome(StrEnum):
    """The in-silico splice-prediction outcome selecting one of five paths (SM 6)."""

    NMD_PREDICTED = "NMD_PREDICTED"
    FRAMESHIFT_NO_NMD = "FRAMESHIFT_NO_NMD"
    SPLICE_NO_FRAMESHIFT = "SPLICE_NO_FRAMESHIFT"
    UNCERTAIN = "UNCERTAIN"
    UNLIKELY = "UNLIKELY"


class SplicePredictor(StrEnum):
    """An in-silico splice-effect predictor (SM 6)."""

    SPLICEAI = "SPLICEAI"
    PANGOLIN = "PANGOLIN"
    OTHER = "OTHER"


class SpliceAssayResult(StrEnum):
    """The qualitative degree of aberrant splice product in a splice assay (SM 6)."""

    NEAR_COMPLETE_OR_COMPLETE = "NEAR_COMPLETE_OR_COMPLETE"
    SUBSTANTIAL = "SUBSTANTIAL"
    INCOMPLETE_OR_NONE = "INCOMPLETE_OR_NONE"


class SplicePredictiveEvidence(BaseModel):
    """The splice predictive (SPL_PRD) step of a splice path (SM 6).

    Positive initial points (yellow/orange paths) are reduced by the SM 18
    mechanism/exon matrix; blue starts at 0.0 and violet at −1.0.
    """

    model_config = ConfigDict(extra="forbid")

    splice_predictor: SplicePredictor | None = Field(
        default=None, description="The in-silico splice predictor used (e.g. SpliceAI)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial SPL_PRD points before the SM 18 adjustment."
    )
    protein_fraction_altered: float | None = Field(
        default=None,
        description="Fraction of protein altered (orange paths' initial-points table).",
    )
    alternative_start_rescue: bool | None = Field(
        default=None,
        description="An alternative start codon rescues the 5' PTC (the −1.0 case).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded SPL_PRD points after the SM 18 adjustment."
    )
    # Note: the lower-orange path's protein-deletion in-silico tool input
    # (MutationTaster/Provean, +2.0 / −0.5; SM 6, not yet calibrated) folds into
    # ``initial_points`` for now rather than a dedicated field.


class SpliceAssayEvidence(BaseModel):
    """The splice-assay (SPL_SPA) step: RNA / minigene evidence for splicing (SM 6).

    Distinct from SM 20 functional evidence (which is SPL_FXN). Semantics vary by
    path: it scales SPL_PRD (yellow/orange), is additive (blue), or adds benignity
    (violet). Absent = SPL_SPA_ND.
    """

    model_config = ConfigDict(extra="forbid")

    assay_type: str | None = Field(
        default=None, description="Assay modality (e.g. RT-PCR, RNAseq, minigene)."
    )
    result: SpliceAssayResult | None = Field(
        default=None, description="Qualitative degree of the aberrant splice product."
    )
    calibrated: bool | None = Field(
        default=None,
        description="Whether an activity-threshold calibration allows adjusted scoring.",
    )
