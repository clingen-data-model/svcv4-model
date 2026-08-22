"""Tests for reference_score_start_lost (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_start_lost
from svcv4_model.start_lost import (
    StartLostAssessment,
    StartLostOutcome,
    StartLostPredictiveEvidence,
)

MOD = GeneDiseaseValidity.MODERATE
B = VariantClassification.BENIGN


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def _benign(n: int) -> InformativeVariantsEvidence:
    return InformativeVariantsEvidence(
        variants=[InformativeVariant(id=f"b{i}", classification=B) for i in range(n)]
    )


def test_yellow_maximal() -> None:
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.NO_ALT_START,
        parent_code=PfdParentCode.NUL,
        predictive=StartLostPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=2.0,
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.held_combined["PRD+FXN"] == 8.0
    assert r.parent_total == 8.0


def test_yellow_minus4_floor() -> None:
    # PRD suppressed (predictive=None -> held None); 5 benign -> INF -6.0 -> parent floored at -4
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.NO_ALT_START,
        informative=_benign(5),
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert "PRD" not in r.sub_code_points
    assert r.sub_code_points["INF"] == -6.0
    assert r.parent_total == -4.0  # shared -8 floor would give -6.0


def test_orange_held_cap_9() -> None:
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.ALT_START_UNPROVEN,
        predictive=StartLostPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.held_combined["PRD+FXN"] == 9.0


def test_violet_benignity_only() -> None:
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.ALT_START_FUNCTIONAL,
        predictive=StartLostPredictiveEvidence(initial_points=-1.0),
        informative=_benign(1),
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == -1.0
    assert r.sub_code_points["INF"] == -2.0
    assert r.parent_total == -3.0  # within [-8, 0]


def test_orange_minus4_floor() -> None:
    # orange also floors the parent total at -4.0 (PRD suppressed so the floor can bite)
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.ALT_START_UNPROVEN,
        informative=_benign(5),  # INF -6.0
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert r.parent_total == -4.0


def test_violet_pathogenic_inf_clamped_to_zero() -> None:
    # violet is benignity-only: a P informative variant that would tally +2 is clamped by
    # the inf_hi=0 ceiling (a default +8 ceiling would leave +2 and lift the parent to +1).
    a = StartLostAssessment(
        prediction_outcome=StartLostOutcome.ALT_START_FUNCTIONAL,
        predictive=StartLostPredictiveEvidence(initial_points=-1.0),
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="p", classification=VariantClassification.PATHOGENIC)]
        ),
    )
    r = reference_score_start_lost(a, gene_disease_validity=MOD)
    assert r.sub_code_points["INF"] == 0.0  # +2 tally clamped to the benignity-only ceiling
    assert r.parent_total == -1.0  # PRD -1 + INF 0, within [-8, 0]


def test_empty_is_all_nd() -> None:
    r = reference_score_start_lost(StartLostAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
