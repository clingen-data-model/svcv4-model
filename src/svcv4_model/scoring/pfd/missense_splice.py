"""Reference (non-authoritative) scorer for the Missense splice path (SM 6, SPL_)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.missense import MissenseSpliceAssessment
from svcv4_model.scoring.pfd._spl_common import SplBranchSpec, score_spl_workflow
from svcv4_model.scoring.result import ScoreResult
from svcv4_model.splice import SplicePredictionOutcome

# SPA scales the PRD *up* here, so orange carries an explicit 0..+6 first held cap.
_ORANGE = SplBranchSpec(-1.0, 3.0, prd_spa_lo=0.0, prd_spa_hi=6.0)

# NOTE: SM 6's blue/violet parent caps are INVERTED vs Canonical (SM 11) / Intronic (SM 12) --
# blue UNCERTAIN -> -8..0 and violet UNLIKELY -> -8..+8. This looks like a possible SM 6 typo
# but the merged missense.md encodes it, so it is reproduced faithfully and flagged in
# provenance (a suspected inconsistency to raise with the WG).
_BRANCH: dict[SplicePredictionOutcome, SplBranchSpec] = {
    SplicePredictionOutcome.NMD_PREDICTED: SplBranchSpec(0.0, 3.0, prd_spa_lo=0.0, prd_spa_hi=6.0),
    SplicePredictionOutcome.FRAMESHIFT_NO_NMD: _ORANGE,
    SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT: _ORANGE,
    SplicePredictionOutcome.UNCERTAIN: SplBranchSpec(
        0.0, 0.0, prd_spa_lo=-2.0, prd_spa_hi=2.0, parent_hi=0.0
    ),
    SplicePredictionOutcome.UNLIKELY: SplBranchSpec(
        -1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0, inf_hi=0.0, parent_hi=8.0
    ),
}

_ODDITY_NOTE = (
    "SM 6 blue/violet SPL_ parent caps are inverted vs SM 11/12 (blue -8..0, violet -8..+8); "
    "encoded as documented -- suspected SM 6 inconsistency, flagged for WG review."
)


def reference_score_missense_splice(
    assessment: MissenseSpliceAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Missense splice-path (SPL_) total (SM 6).

    CSpec is authoritative. ``gene_disease_validity`` is required (the splice PRD uses SM 18).
    SPA is consumed raw (it scales the PRD *up* here). The blue/violet parent caps are inverted
    versus the other splice workflows -- see ``_ODDITY_NOTE`` (faithful to SM 6, flagged).
    """
    result = score_spl_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
    result.provenance.append(_ODDITY_NOTE)
    return result
