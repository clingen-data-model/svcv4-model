"""Tests for the SVCv4 PFD scaffold (PfdCodeAssessment)."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import InformativeVariant, InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import (
    PfdCodeAssessment,
    PfdParentCode,
    PfdPredictiveEvidence,
)


def _maximal_assessment() -> PfdCodeAssessment:
    return PfdCodeAssessment(
        parent_code=PfdParentCode.MIS,
        predictive=PfdPredictiveEvidence(
            predictor="REVEL",
            raw_score=0.92,
            initial_points=4.0,
            path_label="GREEN",
            transcript_relevance_applied=True,
            mechanism_applied=False,
            adjusted_points=4.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(variants=[InformativeVariant()]),
        prd_points=4.0,
        spa_points=0.0,
        fxn_points=2.0,
        inf_points=1.0,
        parent_total=7.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = PfdCodeAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = PfdCodeAssessment()
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        PfdCodeAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        PfdPredictiveEvidence(not_a_field=1)


def test_parent_code_values_round_trip() -> None:
    for code in PfdParentCode:
        assert PfdCodeAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "PfdCodeAssessment" in svcv4_model.__all__
    assert "PfdParentCode" in svcv4_model.__all__
    assert "PfdPredictiveEvidence" in svcv4_model.__all__
