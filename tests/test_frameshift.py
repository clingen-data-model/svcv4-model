"""Tests for the SVCv4 Frameshift variants (NUL_/CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.frameshift import (
    FrameshiftAssessment,
    FrameshiftPredictionOutcome,
    FrameshiftPredictiveEvidence,
)
from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


def _maximal_assessment() -> FrameshiftAssessment:
    return FrameshiftAssessment(
        prediction_outcome=FrameshiftPredictionOutcome.NON_STOP_DECAY,
        parent_code=PfdParentCode.NUL,
        predictive=FrameshiftPredictiveEvidence(
            basis="No in-frame stop before the polyA site (NSD predicted)",
            initial_points=4.0,
            protein_fraction_reduced=0.4,
            alternative_met_rescue=False,
            non_stop_decay_predicted=True,
            extension_length_aa=40,
            adjusted_points=4.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.ALL,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000099",
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


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = FrameshiftAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = FrameshiftAssessment()
    assert empty.prediction_outcome is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        FrameshiftAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        FrameshiftPredictiveEvidence(not_a_field=1)


def test_prediction_outcome_values_round_trip() -> None:
    for outcome in FrameshiftPredictionOutcome:
        assert FrameshiftAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_parent_code_accepts_nul_and_cds() -> None:
    for code in (PfdParentCode.NUL, PfdParentCode.CDS):
        assert FrameshiftAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "FrameshiftAssessment",
        "FrameshiftPredictionOutcome",
        "FrameshiftPredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
