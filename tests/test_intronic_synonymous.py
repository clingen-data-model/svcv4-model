"""Tests for the SVCv4 Intronic & Synonymous variants (SPL_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.intronic_synonymous import IntronicSynonymousAssessment
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)


def _maximal_assessment() -> IntronicSynonymousAssessment:
    return IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(
            splice_predictor=SplicePredictor.SPLICEAI,
            initial_points=3.0,
            adjusted_points=3.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.ALL,
        ),
        splice_assay=SpliceAssayEvidence(
            assay_type="RNAseq",
            result=SpliceAssayResult.NEAR_COMPLETE_OR_COMPLETE,
            calibrated=False,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000121",
                    classification=VariantClassification.PATHOGENIC,
                )
            ]
        ),
        prd_points=3.0,
        spa_points=3.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_spa_combined=6.0,
        prd_spa_fxn_combined=8.0,
        spl_total=9.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = IntronicSynonymousAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = IntronicSynonymousAssessment()
    assert empty.prediction_outcome is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.splice_assay is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.spl_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        IntronicSynonymousAssessment(not_a_field=1)


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "IntronicSynonymousAssessment" in svcv4_model.__all__
