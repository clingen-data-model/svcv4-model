"""Reference (non-authoritative) scorer for the Canonical Splice workflow (SM 11)."""

from __future__ import annotations

from svcv4_model.canonical_splice import CanonicalSpliceAssessment
from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.scoring.pfd._spl_common import SplBranchSpec, score_spl_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.splice import SplicePredictionOutcome

_BRANCH: dict[SplicePredictionOutcome, SplBranchSpec] = {
    SplicePredictionOutcome.NMD_PREDICTED: SplBranchSpec(0.0, 6.0),
    SplicePredictionOutcome.FRAMESHIFT_NO_NMD: SplBranchSpec(-1.0, 6.0),
    SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT: SplBranchSpec(-1.0, 6.0),
    SplicePredictionOutcome.UNCERTAIN: SplBranchSpec(0.0, 0.0, prd_spa_fxn_hi=8.0, parent_hi=8.0),
    SplicePredictionOutcome.UNLIKELY: SplBranchSpec(
        -1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0, prd_spa_fxn_hi=0.0, inf_hi=0.0, parent_hi=0.0
    ),
}


def reference_score_canonical_splice(
    assessment: CanonicalSpliceAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Canonical Splice point total (SM 11, five paths).

    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). SPA is consumed raw (the coded delta; on canonical the
    assay reduces the PRD). The violet (UNLIKELY) path is benignity-only.
    """
    return score_spl_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
