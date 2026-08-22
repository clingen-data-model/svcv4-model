"""Reference (non-authoritative) scorer for the Exon Duplication/Gain workflow (SM 14)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.exon_duplication import ExonDuplicationAssessment, ExonDuplicationOutcome
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult

_BRANCH: dict[ExonDuplicationOutcome, BranchSpec] = {
    # tandem paths consume FXN (SM 20)
    ExonDuplicationOutcome.TANDEM_NMD: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    ExonDuplicationOutcome.TANDEM_NO_NMD: BranchSpec("CDS", 0.0, 3.0, held_hi=9.0),
    ExonDuplicationOutcome.TANDEM_TERMINAL_EXON: BranchSpec("CDS", 0.0, 0.0, held_hi=9.0),
    # gain paths: FXN is NA (not considered)
    ExonDuplicationOutcome.GAIN_NMD: BranchSpec(
        "NUL", 0.0, 4.0, fxn_na=True, parent_lo=-1.0, parent_hi=6.0, inf_hi=6.0
    ),
    ExonDuplicationOutcome.GAIN_NO_NMD: BranchSpec(
        "CDS", 0.0, 2.0, fxn_na=True, parent_lo=-1.0, parent_hi=6.0, inf_hi=6.0
    ),
    ExonDuplicationOutcome.GAIN_TERMINAL_EXON: BranchSpec(
        "CDS", 0.0, 0.0, fxn_na=True, parent_hi=0.0, inf_hi=0.0
    ),
    # WHOLE_GENE_NA handled in the wrapper (all NA)
}


def reference_score_exon_duplication(
    assessment: ExonDuplicationAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Exon Duplication/Gain point total (SM 14).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). The gain paths code functional data as NA (FXN
    skipped); whole-gene duplication is CDS_NA (all steps not applicable).
    """
    if assessment.prediction_outcome == ExonDuplicationOutcome.WHOLE_GENE_NA:
        return ScoreResult(
            parent_code="CDS",
            parent_total=None,
            provenance=["WHOLE_GENE_NA: CDS_NA (evaluated, determined not applicable)"],
            authoritative=False,
        )
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
