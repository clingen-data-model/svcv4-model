"""Tests for the SVCv4 Missense amino-acid (MIS_) path model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import VariantClassification
from svcv4_model.mechanism import ExonRelevance
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
)


def _maximal_assessment() -> MissenseAminoAcidAssessment:
    return MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(
            predictor=MissensePredictor.REVEL,
            raw_score=0.92,
            initial_points=4.0,
            transcript_relevance=ExonRelevance.ALL,
            adjusted_points=4.0,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=MissenseInformativeEvidence(
            variants=[
                MissenseInformativeVariant(
                    id="clinvar:VCV000000021",
                    category=MissenseInfCategory.DISTINCT_AA_PATHOGENIC,
                    classification=VariantClassification.PATHOGENIC,
                    grantham_wt_to_vbc=100.0,
                    grantham_wt_to_informative=50.0,
                )
            ]
        ),
        prd_points=4.0,
        fxn_points=2.0,
        inf_points=2.0,
        prd_fxn_combined=6.0,
        mis_total=8.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = MissenseAminoAcidAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = MissenseAminoAcidAssessment()
    assert empty.predictive is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.mis_total is None


def test_informative_evidence_defaults_to_empty_list() -> None:
    assert MissenseInformativeEvidence().variants == []


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseAminoAcidAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissensePredictiveEvidence(not_a_field=1)


def test_informative_variant_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseInformativeVariant(not_a_field=1)


def test_informative_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseInformativeEvidence(not_a_field=1)


def test_predictor_values_round_trip() -> None:
    for predictor in MissensePredictor:
        model = MissensePredictiveEvidence(predictor=predictor)
        assert model.predictor is predictor


def test_inf_category_values_round_trip() -> None:
    for category in MissenseInfCategory:
        model = MissenseInformativeVariant(category=category)
        assert model.category is category


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "MissenseAminoAcidAssessment",
        "MissenseInfCategory",
        "MissenseInformativeEvidence",
        "MissenseInformativeVariant",
        "MissensePredictiveEvidence",
        "MissensePredictor",
    ):
        assert name in svcv4_model.__all__
