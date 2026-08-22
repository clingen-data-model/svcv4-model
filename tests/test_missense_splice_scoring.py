"""Tests for reference_score_missense_splice (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.missense import MissenseSpliceAssessment
from svcv4_model.scoring import reference_score_missense_splice
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


def test_yellow_maximal() -> None:
    a = MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(),
        spa_points=3.0,  # scales up: held PRD+SPA -> +6
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 4),  # +2+1+1+1 = +5
    )
    r = reference_score_missense_splice(a, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.held_combined["PRD+SPA"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(6+8, +9)
    assert r.parent_total == 10.0  # cap(9+5, +10)


def test_blue_parent_clamped_to_zero() -> None:
    # THE ODDITY (blue): an uncertain variant's positive evidence is zeroed at the parent
    a = MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNCERTAIN,
        predictive=SplicePredictiveEvidence(initial_points=0.0),
        spa_points=2.0,
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 4),  # big +INF
    )
    r = reference_score_missense_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == 2.0  # cap(0+2, [-2, 2])
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(2+8, +9)
    assert r.parent_total == 0.0  # cap(9+INF, [-8, 0]) -> 0 (the oddity)


def test_violet_reaches_positive_seven() -> None:
    # THE ODDITY (violet): an unlikely variant reaches +7 via FXN (parent_hi=8 never binds)
    a = MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNLIKELY,
        predictive=SplicePredictiveEvidence(initial_points=-1.0),
        fxn_points=8.0,
    )
    r = reference_score_missense_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA+FXN"] == 7.0  # cap(-1+8, +9)
    assert r.parent_total == 7.0  # cap(7, [-8, 8])


def test_violet_inf_benignity_only() -> None:
    a = MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNLIKELY,
        predictive=SplicePredictiveEvidence(initial_points=-1.0),
        informative=_inf(VariantClassification.PATHOGENIC, 1),  # +2 clamped to 0 by inf_hi=0
    )
    r = reference_score_missense_splice(a, gene_disease_validity=MOD)
    assert r.sub_code_points["INF"] == 0.0


def test_all_five_outcomes() -> None:
    for outcome in SplicePredictionOutcome:
        r = reference_score_missense_splice(
            MissenseSpliceAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code == "SPL"


def test_empty_is_all_nd() -> None:
    r = reference_score_missense_splice(MissenseSpliceAssessment(), gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.parent_total is None
