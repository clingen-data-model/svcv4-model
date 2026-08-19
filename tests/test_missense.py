"""Tests for the SVCv4 Missense amino-acid (MIS_) path model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import InformativeVariantsEvidence, VariantClassification
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
    MissenseSpliceAssessment,
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
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


def _maximal_splice_assessment() -> MissenseSpliceAssessment:
    return MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(
            splice_predictor=SplicePredictor.SPLICEAI,
            initial_points=3.0,
            protein_fraction_altered=0.6,
            alternative_start_rescue=False,
            adjusted_points=3.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(),
        splice_assay=SpliceAssayEvidence(
            assay_type="minigene",
            result=SpliceAssayResult.NEAR_COMPLETE_OR_COMPLETE,
            calibrated=False,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(),
        prd_points=3.0,
        spa_points=3.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_spa_combined=6.0,
        prd_spa_fxn_combined=8.0,
        spl_total=9.0,
    )


def test_splice_assessment_round_trips_json() -> None:
    original = _maximal_splice_assessment()
    rehydrated = MissenseSpliceAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_splice_assessment_is_permissive_when_empty() -> None:
    empty = MissenseSpliceAssessment()
    assert empty.prediction_outcome is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.splice_assay is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.spl_total is None


def test_splice_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseSpliceAssessment(not_a_field=1)


def test_splice_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        SplicePredictiveEvidence(not_a_field=1)


def test_splice_assay_forbids_extra() -> None:
    with pytest.raises(ValueError):
        SpliceAssayEvidence(not_a_field=1)


def test_splice_prediction_outcome_values_round_trip() -> None:
    for outcome in SplicePredictionOutcome:
        assert MissenseSpliceAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_splice_predictor_values_round_trip() -> None:
    for predictor in SplicePredictor:
        assert SplicePredictiveEvidence(splice_predictor=predictor).splice_predictor is predictor


def test_splice_assay_result_values_round_trip() -> None:
    for result in SpliceAssayResult:
        assert SpliceAssayEvidence(result=result).result is result


def test_splice_names_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "MissenseSpliceAssessment",
        "SpliceAssayEvidence",
        "SpliceAssayResult",
        "SplicePredictionOutcome",
        "SplicePredictiveEvidence",
        "SplicePredictor",
    ):
        assert name in svcv4_model.__all__
