"""Tests for the SVCv4 Single/Multi-Exon Deletion (NUL_/CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.exon_deletion import (
    ExonDeletionAssessment,
    ExonDeletionOutcome,
    ExonDeletionPredictiveEvidence,
)
from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


def _maximal_assessment() -> ExonDeletionAssessment:
    return ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.WHOLE_GENE,
        parent_code=PfdParentCode.NUL,
        predictive=ExonDeletionPredictiveEvidence(
            basis="Whole-gene deletion (LoF)",
            initial_points=10.0,
            protein_fraction_removed=1.0,
            alternative_start_functional=False,
            adjusted_points=10.0,
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
        prd_points=10.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_fxn_combined=10.0,
        parent_total=10.0,
    )


def _grey_path_assessment() -> ExonDeletionAssessment:
    """The functional-alt-start (grey) branch: CDS_, skips SM 18, benignity-only caps."""
    return ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.START_CODON_ALT_START_FUNCTIONAL,
        parent_code=PfdParentCode.CDS,
        predictive=ExonDeletionPredictiveEvidence(
            basis="Deletes start exon; demonstrated functional alternative in-frame start",
            initial_points=-1.0,
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
        fxn_points=-4.0,
        inf_points=-2.0,
        prd_fxn_combined=-5.0,
        parent_total=-8.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = ExonDeletionAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_grey_path_assessment_round_trips_json() -> None:
    original = _grey_path_assessment()
    rehydrated = ExonDeletionAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original
    assert rehydrated.parent_code is PfdParentCode.CDS
    assert rehydrated.mechanism_exon_relevance is None


def test_assessment_is_permissive_when_empty() -> None:
    empty = ExonDeletionAssessment()
    assert empty.prediction_outcome is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        ExonDeletionAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        ExonDeletionPredictiveEvidence(not_a_field=1)


def test_prediction_outcome_values_round_trip() -> None:
    for outcome in ExonDeletionOutcome:
        assert ExonDeletionAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_parent_code_accepts_nul_and_cds() -> None:
    for code in (PfdParentCode.NUL, PfdParentCode.CDS):
        assert ExonDeletionAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "ExonDeletionAssessment",
        "ExonDeletionOutcome",
        "ExonDeletionPredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
