"""Reference (non-authoritative) scorer for the Stop-Lost workflow (SM 16)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.stop_lost import StopLostAssessment, StopLostOutcome

_BRANCH: dict[StopLostOutcome, BranchSpec] = {
    StopLostOutcome.NSD_PREDICTED: BranchSpec("NUL", 0.0, 4.0, held_hi=9.0),
    StopLostOutcome.NO_NSD: BranchSpec("CDS", 0.0, 4.0, held_hi=9.0),
}


def reference_score_stop_lost(
    assessment: StopLostAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Stop-Lost point total (SM 16, two branches).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). The orange four-tier interference/extension PRD scale
    is analyst-applied and captured as ``initial_points`` (not recomputed here).
    """
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
