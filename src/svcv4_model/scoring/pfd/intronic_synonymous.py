"""Reference (non-authoritative) scorer for the Intronic & Synonymous workflow (SM 12)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.intronic_synonymous import IntronicSynonymousAssessment
from svcv4_model.scoring.pfd._spl_common import SplBranchSpec, score_spl_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.splice import SplicePredictionOutcome

# SPA scales the PRD *up* here, so orange carries an explicit -1..+6 first held cap.
_ORANGE = SplBranchSpec(-1.0, 3.0, prd_spa_lo=-1.0, prd_spa_hi=6.0)

_BRANCH: dict[SplicePredictionOutcome, SplBranchSpec] = {
    SplicePredictionOutcome.NMD_PREDICTED: SplBranchSpec(0.0, 3.0),
    SplicePredictionOutcome.FRAMESHIFT_NO_NMD: _ORANGE,
    SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT: _ORANGE,
    SplicePredictionOutcome.UNCERTAIN: SplBranchSpec(0.0, 0.0, parent_hi=8.0),
    SplicePredictionOutcome.UNLIKELY: SplBranchSpec(
        -1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0, prd_spa_fxn_hi=0.0, inf_hi=0.0, parent_hi=0.0
    ),
}


def reference_score_intronic_synonymous(
    assessment: IntronicSynonymousAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Intronic & Synonymous total (SM 12, five paths).

    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). Field-identical to Canonical Splice but with a lower
    +3 PRD ceiling, an explicit orange held ``prd_spa`` cap (SPA scales the PRD up here), and a
    +9 blue second-held cap. SPA is consumed raw. The lilac (UNLIKELY) path is benignity-only.
    """
    return score_spl_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
