"""Tests for the SVCv4 CLN_CCS case-control study model."""

from __future__ import annotations

import pytest

from svcv4_model.case_control import CaseControlStudyEvidence


def _maximal() -> CaseControlStudyEvidence:
    return CaseControlStudyEvidence(
        odds_ratio=5.5,
        ci_lower=3.1,
        ci_upper=9.8,
        case_cohort_size=250,
        case_variant_count=12,
        control_cohort_size=5000,
        controls_matched=True,
        ascertainment_bias_considered=True,
    )


def test_round_trips_json() -> None:
    original = _maximal()
    rehydrated = CaseControlStudyEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_is_permissive_when_empty() -> None:
    assert CaseControlStudyEvidence().odds_ratio is None


def test_forbids_extra() -> None:
    with pytest.raises(ValueError):
        CaseControlStudyEvidence(not_a_field=1)


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "CaseControlStudyEvidence" in svcv4_model.__all__
