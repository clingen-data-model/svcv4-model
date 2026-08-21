"""Tests for the SVCv4 Single/Multi-Exon Duplication/Gain (NUL_/CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.exon_duplication import (
    ExonDuplicationAssessment,
    ExonDuplicationOutcome,
    ExonDuplicationPredictiveEvidence,
)
from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


def _maximal_assessment() -> ExonDuplicationAssessment:
    return ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.TANDEM_NMD,
        parent_code=PfdParentCode.NUL,
        predictive=ExonDuplicationPredictiveEvidence(
            basis="Molecularly-proven tandem duplication; PTC >50 bp upstream (NMD)",
            initial_points=6.0,
            molecularly_tandem=True,
            nmd_predicted=True,
            includes_terminal_exon_or_utr=False,
            orf_fraction_duplicated=0.4,
            duplicated_domain_critical=False,
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


def _gain_terminal_exon_assessment() -> ExonDuplicationAssessment:
    """The green (GAIN_TERMINAL_EXON) branch: CDS_, no SM 18, FXN-NA, benignity-only INF."""
    return ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.GAIN_TERMINAL_EXON,
        parent_code=PfdParentCode.CDS,
        predictive=ExonDuplicationPredictiveEvidence(
            basis="Not proven tandem; includes first exon/UTR; no initial points",
            initial_points=0.0,
            molecularly_tandem=False,
            includes_terminal_exon_or_utr=True,
            adjusted_points=0.0,
        ),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000132",
                    classification=VariantClassification.BENIGN,
                )
            ]
        ),
        prd_points=0.0,
        inf_points=-2.0,
        parent_total=-2.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = ExonDuplicationAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_gain_terminal_exon_assessment_round_trips_json() -> None:
    original = _gain_terminal_exon_assessment()
    rehydrated = ExonDuplicationAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original
    assert rehydrated.parent_code is PfdParentCode.CDS
    assert rehydrated.functional is None


def test_assessment_is_permissive_when_empty() -> None:
    empty = ExonDuplicationAssessment()
    assert empty.prediction_outcome is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        ExonDuplicationAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        ExonDuplicationPredictiveEvidence(not_a_field=1)


def test_prediction_outcome_values_round_trip() -> None:
    for outcome in ExonDuplicationOutcome:
        assert ExonDuplicationAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_parent_code_accepts_nul_and_cds() -> None:
    for code in (PfdParentCode.NUL, PfdParentCode.CDS):
        assert ExonDuplicationAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "ExonDuplicationAssessment",
        "ExonDuplicationOutcome",
        "ExonDuplicationPredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
