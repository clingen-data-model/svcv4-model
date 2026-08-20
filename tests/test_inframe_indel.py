"""Tests for the SVCv4 In-Frame InDel variants (CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.inframe_indel import (
    InframeIndelAssessment,
    InframeIndelBranch,
    InframeIndelPredictiveEvidence,
)
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


def _maximal_assessment() -> InframeIndelAssessment:
    return InframeIndelAssessment(
        branch=InframeIndelBranch.NON_REPEAT,
        parent_code=PfdParentCode.CDS,
        predictive=InframeIndelPredictiveEvidence(
            basis="Removes >50% of the protein",
            initial_points=6.0,
            protein_fraction_reduced=0.6,
            in_silico_predictor="MutationTaster2021",
            in_silico_calibrated=True,
            repeat_stable_in_controls=None,
            adjusted_points=6.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.ALL,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000101",
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


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = InframeIndelAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = InframeIndelAssessment()
    assert empty.branch is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        InframeIndelAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        InframeIndelPredictiveEvidence(not_a_field=1)


def test_branch_values_round_trip() -> None:
    for branch in InframeIndelBranch:
        assert InframeIndelAssessment(branch=branch).branch is branch


def test_parent_code_accepts_cds() -> None:
    assert InframeIndelAssessment(parent_code=PfdParentCode.CDS).parent_code is PfdParentCode.CDS


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "InframeIndelAssessment",
        "InframeIndelBranch",
        "InframeIndelPredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
