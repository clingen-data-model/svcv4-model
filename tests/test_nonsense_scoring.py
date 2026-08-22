"""Tests for reference_score_nonsense (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.nonsense import (
    NonsenseAssessment,
    NonsensePredictionOutcome,
    NonsensePredictiveEvidence,
)
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_nonsense

MOD = GeneDiseaseValidity.MODERATE


def test_yellow_maximal() -> None:
    a = NonsenseAssessment(
        prediction_outcome=NonsensePredictionOutcome.NMD_NO_RESCUE,
        parent_code=PfdParentCode.NUL,
        predictive=NonsensePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        fxn_points=2.0,
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="a", classification=VariantClassification.PATHOGENIC)]
        ),
    )
    r = reference_score_nonsense(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.sub_code_points["FXN"] == 2.0
    assert r.sub_code_points["INF"] == 2.0
    assert r.held_combined["PRD+FXN"] == 8.0
    assert r.parent_total == 10.0  # capped at +10
    assert r.authoritative is False
    assert r.provenance  # non-empty trail


def test_violet_reduced_mechanism_and_fxn_nd() -> None:
    a = NonsenseAssessment(
        prediction_outcome=NonsensePredictionOutcome.NO_NMD,
        parent_code=PfdParentCode.CDS,
        predictive=NonsensePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.LIKELY, exon_relevance=ExonRelevance.MOST
        ),
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="b", classification=VariantClassification.BENIGN)]
        ),
    )
    r = reference_score_nonsense(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 1.5  # 6.0 x 0.5 x 0.5
    assert "FXN" not in r.sub_code_points  # fxn_points absent -> _FXN_ND
    assert r.held_combined["PRD+FXN"] == 1.5  # held = prd alone
    assert r.sub_code_points["INF"] == -2.0
    assert r.parent_total == -0.5


def test_orange_held_cap_is_9() -> None:
    a = NonsenseAssessment(
        prediction_outcome=NonsensePredictionOutcome.NMD_WITH_RESCUE,
        predictive=NonsensePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        fxn_points=8.0,
    )
    r = reference_score_nonsense(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+FXN"] == 9.0  # 6+8 capped at +9 (orange)


def test_empty_assessment_is_all_nd() -> None:
    r = reference_score_nonsense(NonsenseAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.held_combined == {}
    assert r.parent_total is None
    assert r.parent_code is None
