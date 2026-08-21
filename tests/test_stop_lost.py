"""Tests for the SVCv4 Stop-Lost (NUL_/CDS_) workflow model."""

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
from svcv4_model.stop_lost import (
    StopLostAssessment,
    StopLostInterference,
    StopLostOutcome,
    StopLostPredictiveEvidence,
)


def _maximal_assessment() -> StopLostAssessment:
    return StopLostAssessment(
        prediction_outcome=StopLostOutcome.NSD_PREDICTED,
        parent_code=PfdParentCode.NUL,
        predictive=StopLostPredictiveEvidence(
            basis="No in-frame stop before the polyA site; NSD predicted",
            initial_points=4.0,
            nsd_predicted=True,
            similar_variant_interference=StopLostInterference.NONE,
            extension_length_aa=45,
            adjusted_points=4.0,
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
        prd_points=4.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_fxn_combined=6.0,
        parent_total=7.0,
    )


def _no_nsd_assessment() -> StopLostAssessment:
    """The orange (NO_NSD) branch: CDS_ with the interference/extension tier + held combined."""
    return StopLostAssessment(
        prediction_outcome=StopLostOutcome.NO_NSD,
        parent_code=PfdParentCode.CDS,
        predictive=StopLostPredictiveEvidence(
            basis="In-frame stop before polyA; similar-variant LoF; ext >30 aa",
            initial_points=4.0,
            nsd_predicted=False,
            similar_variant_interference=StopLostInterference.LOSS_OF_FUNCTION,
            extension_length_aa=52,
            adjusted_points=4.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.MOST,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000132",
                    classification=VariantClassification.LIKELY_PATHOGENIC,
                )
            ]
        ),
        prd_points=4.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_fxn_combined=6.0,
        parent_total=7.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = StopLostAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_no_nsd_assessment_round_trips_json() -> None:
    original = _no_nsd_assessment()
    rehydrated = StopLostAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original
    assert rehydrated.parent_code is PfdParentCode.CDS
    assert rehydrated.prd_fxn_combined == 6.0
    pred = rehydrated.predictive
    assert pred is not None
    assert pred.similar_variant_interference is StopLostInterference.LOSS_OF_FUNCTION


def test_assessment_is_permissive_when_empty() -> None:
    empty = StopLostAssessment()
    assert empty.prediction_outcome is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        StopLostAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        StopLostPredictiveEvidence(not_a_field=1)


def test_prediction_outcome_values_round_trip() -> None:
    for outcome in StopLostOutcome:
        assert StopLostAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_interference_values_round_trip() -> None:
    for level in StopLostInterference:
        pred = StopLostPredictiveEvidence(similar_variant_interference=level)
        assert pred.similar_variant_interference is level


def test_parent_code_accepts_nul_and_cds() -> None:
    for code in (PfdParentCode.NUL, PfdParentCode.CDS):
        assert StopLostAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "StopLostAssessment",
        "StopLostInterference",
        "StopLostOutcome",
        "StopLostPredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
