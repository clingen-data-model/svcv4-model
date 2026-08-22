"""Tests for reference_score_intronic_synonymous (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.intronic_synonymous import IntronicSynonymousAssessment
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.scoring import reference_score_intronic_synonymous
from svcv4_model.splice import SplicePredictionOutcome, SplicePredictiveEvidence

MOD = GeneDiseaseValidity.MODERATE


def _mer() -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(
        gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
    )


def _inf(cls: VariantClassification, n: int) -> InformativeVariantsEvidence:
    return InformativeVariantsEvidence(
        variants=[InformativeVariant(id=f"v{i}", classification=cls) for i in range(n)]
    )


def test_yellow_maximal_prd_3() -> None:
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(),
        spa_points=3.0,  # near-complete doubles +3 -> +3 delta
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.sub_code_points["PRD"] == 3.0
    assert r.held_combined["PRD+SPA"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(6+8, +9)
    assert r.parent_total == 10.0  # cap(9+2, +10)


def test_orange_held_prd_spa_cap_6() -> None:
    # explicit orange first-held -1..+6 (distinct from canonical's default)
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.FRAMESHIFT_NO_NMD,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(),
        spa_points=5.0,
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == 6.0  # cap(3+5, [-1, 6])


def test_blue_second_held_9() -> None:
    # THE SM12-vs-SM11 difference: blue second held caps at +9 (canonical was +8)
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.UNCERTAIN,
        predictive=SplicePredictiveEvidence(initial_points=0.0),
        spa_points=2.0,
        fxn_points=8.0,
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(2+8, +9) -- not +8
    assert r.parent_total == 8.0  # parent clamps to +8


def test_lilac_benignity() -> None:
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.UNLIKELY,
        predictive=SplicePredictiveEvidence(initial_points=-1.0),
        spa_points=-2.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),  # +2 clamped to 0
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == -3.0  # cap(-3, [-3, 0])
    assert r.sub_code_points["INF"] == 0.0
    assert r.parent_total == -3.0


def test_orange_prd_floor() -> None:
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT,
        predictive=SplicePredictiveEvidence(initial_points=-5.0),
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert r.sub_code_points["PRD"] == -1.0  # cap(-5, [-1, 3])


def test_spa_nd() -> None:
    a = IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(),
    )
    r = reference_score_intronic_synonymous(a, gene_disease_validity=MOD)
    assert "SPA" not in r.sub_code_points
    assert r.held_combined["PRD+SPA"] == 3.0


def test_all_five_outcomes() -> None:
    for outcome in SplicePredictionOutcome:
        r = reference_score_intronic_synonymous(
            IntronicSynonymousAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code == "SPL"


def test_empty_is_all_nd() -> None:
    r = reference_score_intronic_synonymous(
        IntronicSynonymousAssessment(), gene_disease_validity=MOD
    )
    assert r.parent_code == "SPL"
    assert r.sub_code_points == {}
    assert r.parent_total is None
