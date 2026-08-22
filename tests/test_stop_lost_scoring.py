"""Tests for reference_score_stop_lost (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_stop_lost
from svcv4_model.stop_lost import (
    StopLostAssessment,
    StopLostOutcome,
    StopLostPredictiveEvidence,
)

MOD = GeneDiseaseValidity.MODERATE


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def test_yellow_nsd() -> None:
    a = StopLostAssessment(
        prediction_outcome=StopLostOutcome.NSD_PREDICTED,
        parent_code=PfdParentCode.NUL,
        predictive=StopLostPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_stop_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 4.0
    assert r.held_combined["PRD+FXN"] == 9.0  # 4+8 capped at +9


def test_orange_no_nsd() -> None:
    a = StopLostAssessment(
        prediction_outcome=StopLostOutcome.NO_NSD,
        predictive=StopLostPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
    )
    r = reference_score_stop_lost(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 4.0
    assert "FXN" not in r.sub_code_points


def test_empty_is_all_nd() -> None:
    r = reference_score_stop_lost(StopLostAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
