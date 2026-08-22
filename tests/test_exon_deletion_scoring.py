"""Tests for reference_score_exon_deletion (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.exon_deletion import (
    ExonDeletionAssessment,
    ExonDeletionOutcome,
    ExonDeletionPredictiveEvidence,
)
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_exon_deletion

MOD = GeneDiseaseValidity.MODERATE


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def test_whole_gene_maximal() -> None:
    a = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.WHOLE_GENE,
        parent_code=PfdParentCode.NUL,
        predictive=ExonDeletionPredictiveEvidence(initial_points=10.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=0.0,
    )
    r = reference_score_exon_deletion(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 10.0
    assert r.parent_total == 10.0  # capped at +10


def test_whole_gene_is_mechanism_only() -> None:
    # whole-gene: Suspected mechanism + Few exon -> mechanism-only ignores Few -> 10 x 0.25 = 2.5
    wg = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.WHOLE_GENE,
        predictive=ExonDeletionPredictiveEvidence(initial_points=10.0),
        mechanism_exon_relevance=_mer(GenccMechanism.SUSPECTED, ExonRelevance.FEW),
    )
    r = reference_score_exon_deletion(wg, gene_disease_validity=MOD)
    assert r.sub_code_points["PRD"] == 2.5
    # a FULL-mode subgenic branch with the same Suspected+Few zeroes (0.25 x 0.0)
    sub = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.SUBGENIC_NMD,
        predictive=ExonDeletionPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.SUSPECTED, ExonRelevance.FEW),
    )
    r2 = reference_score_exon_deletion(sub, gene_disease_validity=MOD)
    assert r2.sub_code_points["PRD"] == 0.0


def test_subgenic_nmd_held_10() -> None:
    a = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.SUBGENIC_NMD,
        predictive=ExonDeletionPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_exon_deletion(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.held_combined["PRD+FXN"] == 10.0  # 6+8 capped at +10 (NUL_ path)


def test_violet_held_9() -> None:
    a = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.SUBGENIC_NO_NMD,
        predictive=ExonDeletionPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_exon_deletion(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.held_combined["PRD+FXN"] == 9.0  # violet held cap +9


def test_grey_benignity_only() -> None:
    a = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.START_CODON_ALT_START_FUNCTIONAL,
        predictive=ExonDeletionPredictiveEvidence(initial_points=-1.0),
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="p", classification=VariantClassification.PATHOGENIC)]
        ),
    )
    r = reference_score_exon_deletion(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == -1.0
    assert r.sub_code_points["INF"] == 0.0  # +2 tally clamped by inf_hi=0 (benignity-only)
    assert r.parent_total == -1.0  # within [-8, 0]


def test_start_codon_branches_parent_and_held() -> None:
    # the two START_CODON_* branches: green (NUL_, held +10) and blue (CDS_, held +9)
    green = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.START_CODON_NO_ALT_START,
        predictive=ExonDeletionPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    rg = reference_score_exon_deletion(green, gene_disease_validity=MOD)
    assert rg.parent_code == "NUL"
    assert rg.held_combined["PRD+FXN"] == 10.0

    blue = ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.START_CODON_ALT_START_UNPROVEN,
        predictive=ExonDeletionPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    rb = reference_score_exon_deletion(blue, gene_disease_validity=MOD)
    assert rb.parent_code == "CDS"
    assert rb.held_combined["PRD+FXN"] == 9.0


def test_all_six_outcomes_score_without_error() -> None:
    for outcome in ExonDeletionOutcome:
        r = reference_score_exon_deletion(
            ExonDeletionAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code in {"NUL", "CDS"}


def test_empty_is_all_nd() -> None:
    r = reference_score_exon_deletion(ExonDeletionAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
