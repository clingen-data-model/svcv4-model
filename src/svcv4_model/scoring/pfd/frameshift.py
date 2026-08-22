"""Reference (non-authoritative) scorer for the Frameshift workflow (SM 9)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.frameshift import FrameshiftAssessment, FrameshiftPredictionOutcome
from svcv4_model.scoring.pfd._common import score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult

# per-branch: (parent_code, prd_lo, prd_hi, held_hi)
_BRANCH: dict[FrameshiftPredictionOutcome, tuple[str, float, float, float]] = {
    FrameshiftPredictionOutcome.NMD_NO_RESCUE: ("NUL", 0.0, 6.0, 10.0),
    FrameshiftPredictionOutcome.NMD_WITH_RESCUE: ("CDS", -1.0, 6.0, 9.0),
    FrameshiftPredictionOutcome.NO_NMD: ("CDS", 0.0, 6.0, 9.0),
    FrameshiftPredictionOutcome.NON_STOP_DECAY: ("NUL", 0.0, 4.0, 9.0),
    FrameshiftPredictionOutcome.PROTEIN_EXTENSION: ("CDS", 0.0, 4.0, 9.0),
}


def reference_score_frameshift(
    assessment: FrameshiftAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Frameshift point total (SM 9, five branches).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). The two green (NSD / extension) branches are a
    non-additive analyst choice upstream; this scores the single captured ``prediction_outcome``.
    """
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
