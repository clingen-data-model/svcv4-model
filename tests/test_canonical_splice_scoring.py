"""Tests for reference_score_canonical_splice (non-authoritative)."""

from __future__ import annotations

from svcv4_model.canonical_splice import CanonicalSpliceAssessment
from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.scoring import reference_score_canonical_splice
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
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(),
        spa_points=0.0,
        fxn_points=2.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.held_combined["PRD+SPA"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 8.0
    assert r.sub_code_points["INF"] == 2.0
    assert r.parent_total == 10.0  # capped at +10


def test_yellow_prd_spa_fxn_cap_9() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(),
        spa_points=0.0,
        fxn_points=8.0,
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # 6+0+8 capped at +9 (not parent +10)


def test_orange_frameshift_prd_floor_and_held_9() -> None:
    # upper-orange FRAMESHIFT_NO_NMD: prd_lo=-1 floor; held PRD+SPA+FXN caps at +9 (not +10)
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.FRAMESHIFT_NO_NMD,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(),
        spa_points=0.0,
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.sub_code_points["PRD"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 9.0  # cap(6+0+8, +9)
    assert r.parent_total == 10.0  # cap(9+2, [-8, 10])


def test_orange_splice_prd_negative_floor() -> None:
    # lower-orange SPLICE_NO_FRAMESHIFT: a very negative PRD input floors at prd_lo=-1
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.SPLICE_NO_FRAMESHIFT,
        predictive=SplicePredictiveEvidence(initial_points=-5.0),  # SM18 no-op on negatives
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.sub_code_points["PRD"] == -1.0  # cap(-5, [-1, 6]) -> -1.0
    assert r.parent_total == -1.0


def test_blue_parent_cap_8() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNCERTAIN,
        predictive=SplicePredictiveEvidence(initial_points=0.0),
        spa_points=2.0,  # additive
        fxn_points=8.0,
        informative=_inf(VariantClassification.PATHOGENIC, 1),
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == 2.0
    assert r.held_combined["PRD+SPA+FXN"] == 8.0  # cap(2+8, +8)
    assert r.parent_total == 8.0  # cap(8+2, [-8, 8])


def test_violet_benignity() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.UNLIKELY,
        predictive=SplicePredictiveEvidence(initial_points=-1.0),
        spa_points=-2.0,  # benignity
        informative=_inf(VariantClassification.PATHOGENIC, 1),  # +2 clamped to 0 by inf_hi=0
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == -3.0  # cap(-3, [-3, 0])
    assert r.sub_code_points["INF"] == 0.0
    assert r.parent_total == -3.0  # within [-8, 0]


def test_spa_nd() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(),
    )
    r = reference_score_canonical_splice(a, gene_disease_validity=MOD)
    assert "SPA" not in r.sub_code_points
    assert r.held_combined["PRD+SPA"] == 6.0  # prd alone (spa _ND)


def test_all_five_outcomes() -> None:
    for outcome in SplicePredictionOutcome:
        r = reference_score_canonical_splice(
            CanonicalSpliceAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code == "SPL"


def test_empty_is_all_nd() -> None:
    r = reference_score_canonical_splice(CanonicalSpliceAssessment(), gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.sub_code_points == {}
    assert r.parent_total is None
