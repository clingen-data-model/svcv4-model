"""Reference (non-authoritative) scorer for the Start-Lost workflow (SM 15)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.start_lost import StartLostAssessment, StartLostOutcome

_BRANCH: dict[StartLostOutcome, BranchSpec] = {
    # yellow: -4 parent floor; no explicit held cap in SM 15 -> parent ceiling +10
    StartLostOutcome.NO_ALT_START: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0, parent_lo=-4.0),
    StartLostOutcome.ALT_START_UNPROVEN: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0, parent_lo=-4.0),
    # violet: PRD -1.0 (SM 18 no-ops on negatives); benignity-only held/parent/INF ceilings = 0
    StartLostOutcome.ALT_START_FUNCTIONAL: BranchSpec(
        "CDS", -1.0, 0.0, held_hi=0.0, parent_hi=0.0, inf_hi=0.0
    ),
}


def reference_score_start_lost(
    assessment: StartLostAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Start-Lost point total (SM 15, three branches).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). Yellow/orange floor the parent total at -4.0; violet
    is benignity-only (parent and INF ceilings 0.0).
    """
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
