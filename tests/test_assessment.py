"""Tests for the assessment registry and Method-config id scheme."""

from __future__ import annotations

import pytest

from svcv4_model import (
    ASSESSMENT_TYPES,
    METHOD_CONFIGS,
    MethodConfig,
    make_method_id,
    parse_method_id,
    resolve,
)


def test_every_config_references_a_known_assessment_type() -> None:
    for cfg in METHOD_CONFIGS.values():
        assert cfg.method_type in ASSESSMENT_TYPES


def test_every_assessment_type_has_a_baseline_config() -> None:
    for mt in ASSESSMENT_TYPES:
        assert make_method_id("baseline", mt, "1.0") in METHOD_CONFIGS


def test_id_round_trips() -> None:
    mid = make_method_id("gene-MYH7", "insilico-missense-predictor-assessment", "2.1")
    assert parse_method_id(mid) == (
        "gene-MYH7",
        "insilico-missense-predictor-assessment",
        "2.1",
    )


def test_specialization_reuses_method_type_with_distinct_id() -> None:
    """A specialisation keeps the methodType but has its own namespaced id."""
    base = resolve("svcv4-baseline:insilico-missense-predictor-assessment:1.0")
    spec = resolve("svcv4-gene-MYH7:insilico-missense-predictor-assessment:1.0")
    assert base.method_type == spec.method_type  # comparable
    assert base.id != spec.id and base.scope != spec.scope  # reproducible/distinct
    assert spec.params["predictor"] == "REVEL(MYH7-recalibrated)"


def test_bad_id_is_rejected() -> None:
    with pytest.raises(ValueError):
        MethodConfig(
            id="not-a-valid-id",
            method_type="nmd-prediction-assessment",
            scope="baseline",
            version="1.0",
        )


def test_specifiedby_id_matches_a_registered_config() -> None:
    """The id a Statement would carry on specifiedBy resolves in the registry."""
    cfg = resolve("svcv4-baseline:mechanism-exon-relevance-assessment:1.0")
    assert cfg.method_type == "mechanism-exon-relevance-assessment"
    assert cfg.scope == "baseline"
