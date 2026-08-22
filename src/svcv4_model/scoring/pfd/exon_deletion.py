"""Reference (non-authoritative) scorer for the Single/Multi-Exon Deletion workflow (SM 13)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.exon_deletion import ExonDeletionAssessment, ExonDeletionOutcome
from svcv4_model.scoring.pfd._common import BranchSpec, score_nul_cds_workflow
from svcv4_model.scoring.result import ScoreResult

_BRANCH: dict[ExonDeletionOutcome, BranchSpec] = {
    # whole-gene: +10, mechanism-only SM 18 (exon-relevance axis removed)
    ExonDeletionOutcome.WHOLE_GENE: BranchSpec(
        "NUL", 0.0, 10.0, held_hi=10.0, sm18_mechanism_only=True
    ),
    ExonDeletionOutcome.SUBGENIC_NMD: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    ExonDeletionOutcome.SUBGENIC_NO_NMD: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
    ExonDeletionOutcome.START_CODON_NO_ALT_START: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    ExonDeletionOutcome.START_CODON_ALT_START_UNPROVEN: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
    # grey: PRD -1.0 (SM 18 no-op), benignity-only held/parent/INF ceilings = 0
    ExonDeletionOutcome.START_CODON_ALT_START_FUNCTIONAL: BranchSpec(
        "CDS", -1.0, 0.0, held_hi=0.0, parent_hi=0.0, inf_hi=0.0
    ),
}


def reference_score_exon_deletion(
    assessment: ExonDeletionAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Exon Deletion point total (SM 13, six branches).
    CSpec is authoritative. ``gene_disease_validity`` is required (pass explicit None for a
    not-classified / below-Moderate MDE). The whole-gene branch applies SM 18 mechanism-only
    (exon-relevance removed); the grey functional-alt-start branch is benignity-only.
    """
    return score_nul_cds_workflow(assessment, _BRANCH, gene_disease_validity=gene_disease_validity)
