"""Tests for the reference-scorer primitives (non-authoritative)."""

from __future__ import annotations

import pytest

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import InformativeVariant, VariantClassification
from svcv4_model.mechanism import ExonRelevance, GenccMechanism
from svcv4_model.scoring import ScoreResult
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
)

MOD = GeneDiseaseValidity.MODERATE


def test_cap_clamps_and_passes_none() -> None:
    assert cap(5.0, -8.0, 10.0) == 5.0
    assert cap(-20.0, -8.0, 10.0) == -8.0
    assert cap(99.0, -8.0, 10.0) == 10.0
    assert cap(None, -8.0, 10.0) is None


def test_hold_combined_sums_caps_and_handles_none() -> None:
    assert hold_combined(6.0, 2.0, lo=-8.0, hi=10.0) == 8.0
    assert hold_combined(6.0, 8.0, lo=-8.0, hi=9.0) == 9.0  # capped
    assert hold_combined(6.0, None, lo=-8.0, hi=10.0) == 6.0
    assert hold_combined(None, None, lo=-8.0, hi=10.0) is None


def test_sm18_multiplier_mechanism_and_exon() -> None:
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) == 6.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.LIKELY, ExonRelevance.ALL, MOD) == 3.0
    assert apply_sm18_multiplier(3.0, GenccMechanism.SUSPECTED, ExonRelevance.ALL, MOD) == 0.75
    assert apply_sm18_multiplier(6.0, GenccMechanism.UNCERTAIN, ExonRelevance.ALL, MOD) == 0.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.FEW, MOD) == 0.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.MOST, MOD) == 3.0


def test_sm18_special_case_suspected_most_is_quarter() -> None:
    # Figure-1-pending assumption: keep the Suspected fraction (0.25), NOT 0.125 and NOT 0.0
    assert apply_sm18_multiplier(4.0, GenccMechanism.SUSPECTED, ExonRelevance.MOST, MOD) == 1.0


def test_sm18_only_positive_and_gdv_gate() -> None:
    assert apply_sm18_multiplier(-1.0, GenccMechanism.UNCERTAIN, ExonRelevance.FEW, MOD) == -1.0
    assert apply_sm18_multiplier(0.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) == 0.0
    assert apply_sm18_multiplier(None, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) is None
    assert (
        apply_sm18_multiplier(
            6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, GeneDiseaseValidity.LIMITED
        )
        == 0.0
    )
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, None) == 0.0
    assert apply_sm18_multiplier(6.0, None, ExonRelevance.ALL, MOD) == 0.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, None, MOD) == 6.0


def _iv(cls: VariantClassification) -> InformativeVariant:
    return InformativeVariant(id="x", classification=cls)


def test_informative_points_tally() -> None:
    p, lp = VariantClassification.PATHOGENIC, VariantClassification.LIKELY_PATHOGENIC
    b, vus = VariantClassification.BENIGN, VariantClassification.VUS
    assert informative_points([_iv(p)]) == 2.0
    assert informative_points([_iv(p), _iv(lp), _iv(lp)]) == 4.0
    assert informative_points([_iv(lp)]) == 1.0
    assert informative_points([_iv(b), _iv(b)]) == -3.0
    assert informative_points([_iv(p), _iv(b)]) == 0.0
    assert informative_points([_iv(vus), _iv(vus)]) == 0.0
    assert informative_points([]) is None
    assert informative_points([InformativeVariant(id="x")]) is None  # classification None


def test_score_result_rejects_authoritative_true() -> None:
    ScoreResult()  # default authoritative=False is fine
    with pytest.raises(ValueError):
        ScoreResult(authoritative=True)
