"""Tests for reference_score_frameshift (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.frameshift import (
    FrameshiftAssessment,
    FrameshiftPredictionOutcome,
    FrameshiftPredictiveEvidence,
)
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_frameshift

MOD = GeneDiseaseValidity.MODERATE


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def test_yellow_maximal() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NMD_NO_RESCUE,
        parent_code=PfdParentCode.NUL,
        predictive=FrameshiftPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=2.0,
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="a", classification=VariantClassification.PATHOGENIC)]
        ),
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.held_combined["PRD+FXN"] == 8.0
    assert r.sub_code_points["INF"] == 2.0
    assert r.parent_total == 10.0


def test_green_nsd_parent_nul_and_held_cap_9() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NON_STOP_DECAY,
        predictive=FrameshiftPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 4.0
    assert r.held_combined["PRD+FXN"] == 9.0  # 4+8 capped at +9 (NSD green held cap)


def test_green_extension_parent_cds_prd_capped_to_4() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.PROTEIN_EXTENSION,
        predictive=FrameshiftPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 4.0
    assert "FXN" not in r.sub_code_points


def test_orange_held_cap_9() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NMD_WITH_RESCUE,
        predictive=FrameshiftPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.held_combined["PRD+FXN"] == 9.0


def test_violet_reduced_mechanism_and_benign_inf() -> None:
    a = FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NO_NMD,
        predictive=FrameshiftPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.LIKELY, ExonRelevance.MOST),
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="b", classification=VariantClassification.BENIGN)]
        ),
    )
    r = reference_score_frameshift(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 1.5  # 6.0 x 0.5 x 0.5
    assert r.sub_code_points["INF"] == -2.0
    assert r.parent_total == -0.5


def test_empty_assessment_is_all_nd() -> None:
    r = reference_score_frameshift(FrameshiftAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
    assert r.parent_code is None
