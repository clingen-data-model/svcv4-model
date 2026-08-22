"""Tests for the shared SPL_ scoring pipeline (non-authoritative)."""

from __future__ import annotations

from svcv4_model.canonical_splice import CanonicalSpliceAssessment
from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.scoring.pfd._spl_common import SplBranchSpec, score_spl_workflow
from svcv4_model.splice import SplicePredictionOutcome, SplicePredictiveEvidence

MOD = GeneDiseaseValidity.MODERATE
_BRANCH = {SplicePredictionOutcome.NMD_PREDICTED: SplBranchSpec(0.0, 6.0)}


def test_spl_pipeline_prd_spa_fxn_held_and_parent() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        spa_points=0.0,
        fxn_points=2.0,
    )
    r = score_spl_workflow(a, _BRANCH, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.sub_code_points["SPA"] == 0.0
    assert r.sub_code_points["FXN"] == 2.0
    assert r.held_combined["PRD+SPA"] == 6.0
    assert r.held_combined["PRD+SPA+FXN"] == 8.0


def test_spl_spa_consumed_as_delta() -> None:
    a = CanonicalSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        spa_points=-1.5,  # substantial -25% of +6
    )
    r = score_spl_workflow(a, _BRANCH, gene_disease_validity=MOD)
    assert r.held_combined["PRD+SPA"] == 4.5


def test_spl_empty_is_all_nd_but_parent_code_spl() -> None:
    r = score_spl_workflow(CanonicalSpliceAssessment(), _BRANCH, gene_disease_validity=MOD)
    assert r.parent_code == "SPL"
    assert r.sub_code_points == {}
    assert r.held_combined == {}
    assert r.parent_total is None
