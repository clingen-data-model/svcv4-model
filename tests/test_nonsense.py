"""Tests for the SVCv4 Nonsense variants (NUL_/CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import InformativeVariant, InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.nonsense import (
    NonsenseAssessment,
    NonsensePredictionOutcome,
    NonsensePredictiveEvidence,
)
from svcv4_model.pfd import PfdParentCode


def _maximal_assessment() -> NonsenseAssessment:
    return NonsenseAssessment(
        prediction_outcome=NonsensePredictionOutcome.NMD_NO_RESCUE,
        parent_code=PfdParentCode.NUL,
        predictive=NonsensePredictiveEvidence(
            basis="NMD predicted (PTC >=50nt upstream of last exon-intron boundary)",
            initial_points=6.0,
            protein_fraction_reduced=0.9,
            alternative_met_rescue=False,
            adjusted_points=6.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(variants=[InformativeVariant()]),
        prd_points=6.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_fxn_combined=8.0,
        parent_total=9.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = NonsenseAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = NonsenseAssessment()
    assert empty.prediction_outcome is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        NonsenseAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        NonsensePredictiveEvidence(not_a_field=1)


def test_prediction_outcome_values_round_trip() -> None:
    for outcome in NonsensePredictionOutcome:
        assert NonsenseAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_parent_code_accepts_nul_and_cds() -> None:
    for code in (PfdParentCode.NUL, PfdParentCode.CDS):
        assert NonsenseAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "NonsenseAssessment",
        "NonsensePredictionOutcome",
        "NonsensePredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
