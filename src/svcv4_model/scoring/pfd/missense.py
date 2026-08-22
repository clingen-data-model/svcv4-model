"""Reference (non-authoritative) Missense take-higher: MIS_ amino-acid vs SPL_ splice (SM 6)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseAssessment,
    MissenseSpliceAssessment,
)
from svcv4_model.scoring.pfd.missense_amino_acid import reference_score_missense_amino_acid
from svcv4_model.scoring.pfd.missense_splice import reference_score_missense_splice
from svcv4_model.scoring.result import MissenseScoreResult


def reference_score_missense(
    assessment: MissenseAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> MissenseScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Missense result via the SM 6 take-higher.

    CSpec is authoritative. Scores BOTH the amino-acid (MIS_, no GDV) and splice (SPL_, with GDV)
    paths and applies SM 6 L157: a negative/absent splice total -> the amino-acid path; a positive
    splice total -> the higher of the two; a positive tie -> the amino-acid path (higher prior for
    the amino-acid effect). A None total counts as not-positive (an empty path never wins).
    """
    amino = reference_score_missense_amino_acid(
        assessment.amino_acid or MissenseAminoAcidAssessment()
    )
    splice = reference_score_missense_splice(
        assessment.splice or MissenseSpliceAssessment(),
        gene_disease_validity=gene_disease_validity,
    )
    mis, spl = amino.parent_total, splice.parent_total

    if spl is None or spl <= 0 or (mis is not None and spl <= mis):
        selected, code, applied = "AMINO_ACID", "MIS", mis
    else:
        selected, code, applied = "SPLICE", "SPL", spl

    prov = [
        f"compared MIS_ {mis} vs SPL_ {spl} -> {selected} "
        f"(SM 6 take-higher: negative/absent splice or a positive tie -> amino-acid)"
    ]
    return MissenseScoreResult(
        amino_acid=amino,
        splice=splice,
        selected_path=selected,
        applied_parent_code=code,
        applied_total=applied,
        provenance=prov,
    )
