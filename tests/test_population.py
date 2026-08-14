"""Tests for the SVCv4 Population (POP) evidence model."""

from __future__ import annotations

import pytest

from svcv4_model.case import TriState
from svcv4_model.population import (
    DaftCalculatorInputs,
    DaftMethod,
    PopulationEvidence,
)


def _maximal() -> PopulationEvidence:
    return PopulationEvidence(
        faf=0.00062,
        faf_source="gnomAD v4.1.1",
        daft=0.000118,
        daft_method=DaftMethod.CALCULATOR,
        daft_calculator_inputs=DaftCalculatorInputs(
            prevalence_denominator=5000,
            penetrance=0.85,
            locus_heterogeneity=1.0,
            allelic_heterogeneity=0.10,
        ),
        homozygote_count=3,
        hemizygote_count=0,
        hmz_eligible=TriState.TRUE,
    )


def test_population_evidence_round_trips_json() -> None:
    original = _maximal()
    rehydrated = PopulationEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_population_evidence_is_permissive_when_empty() -> None:
    assert PopulationEvidence().faf is None


def test_population_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        PopulationEvidence(not_a_field=1)


def test_daft_method_values_round_trip() -> None:
    for method in DaftMethod:
        pe = PopulationEvidence(daft_method=method)
        assert pe.daft_method is method
    assert DaftMethod.VCEP_CURATED.value == "VCEP_CURATED"


def test_hmz_eligible_accepts_each_tristate() -> None:
    for state in TriState:
        assert PopulationEvidence(hmz_eligible=state).hmz_eligible is state


def test_population_evidence_importable_from_package_root() -> None:
    import svcv4_model

    assert "PopulationEvidence" in svcv4_model.__all__
