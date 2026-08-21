"""Tests for the SVCv4 Start-Lost (NUL_/CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.start_lost import (
    StartLostAssessment,
    StartLostOutcome,
    StartLostPredictiveEvidence,
)


def _maximal_assessment() -> StartLostAssessment:
    return StartLostAssessment(
        prediction_outcome=StartLostOutcome.NO_ALT_START,
        parent_code=PfdParentCode.NUL,
        predictive=StartLostPredictiveEvidence(
            basis="No alternate in-frame MET; P/LP PTC variants block rescue",
            initial_points=6.0,
            alternative_start_present=False,
            rescue_blocked_by_ptc=True,
            protein_fraction_lost=1.0,
            alternative_start_functional=False,
            adjusted_points=6.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.ALL,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000131",
                    classification=VariantClassification.PATHOGENIC,
                )
            ]
        ),
        prd_points=6.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_fxn_combined=8.0,
        parent_total=9.0,
    )


def _alt_start_functional_assessment() -> StartLostAssessment:
    """The violet (ALT_START_FUNCTIONAL) branch: CDS_, skips SM 18, benignity-only FXN/INF."""
    return StartLostAssessment(
        prediction_outcome=StartLostOutcome.ALT_START_FUNCTIONAL,
        parent_code=PfdParentCode.CDS,
        predictive=StartLostPredictiveEvidence(
            basis="Experimentally-proven functional alternative start codon",
            initial_points=-1.0,
            alternative_start_present=True,
            alternative_start_functional=True,
            adjusted_points=-1.0,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000132",
                    classification=VariantClassification.BENIGN,
                )
            ]
        ),
        prd_points=-1.0,
        fxn_points=-2.0,
        inf_points=-2.0,
        parent_total=-5.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = StartLostAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_alt_start_functional_assessment_round_trips_json() -> None:
    original = _alt_start_functional_assessment()
    rehydrated = StartLostAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original
    assert rehydrated.parent_code is PfdParentCode.CDS
    assert rehydrated.mechanism_exon_relevance is None


def test_assessment_is_permissive_when_empty() -> None:
    empty = StartLostAssessment()
    assert empty.prediction_outcome is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        StartLostAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        StartLostPredictiveEvidence(not_a_field=1)


def test_prediction_outcome_values_round_trip() -> None:
    for outcome in StartLostOutcome:
        assert StartLostAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_parent_code_accepts_nul_and_cds() -> None:
    for code in (PfdParentCode.NUL, PfdParentCode.CDS):
        assert StartLostAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "StartLostAssessment",
        "StartLostOutcome",
        "StartLostPredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
