"""Reference (non-authoritative) scorer for the Nonsense workflow (SM 8)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.nonsense import NonsenseAssessment, NonsensePredictionOutcome
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult

_BRANCH: dict[NonsensePredictionOutcome, BranchSpec] = {
    NonsensePredictionOutcome.NMD_NO_RESCUE: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    NonsensePredictionOutcome.NMD_WITH_RESCUE: BranchSpec("CDS", -1.0, 6.0, held_hi=9.0),
    NonsensePredictionOutcome.NO_NMD: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
}


def reference_score_nonsense(
    assessment: NonsenseAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Nonsense point total (SM 8). CSpec is
    authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE).
    """
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
