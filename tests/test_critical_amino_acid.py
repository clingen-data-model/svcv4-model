"""Tests for the SVCv4 Determining Critical Amino Acids (SM 7) shared submodule."""

from __future__ import annotations

import pytest

from svcv4_model.critical_amino_acid import (
    CriticalAminoAcidEvidence,
    CriticalityKind,
)


def _residue_evidence() -> CriticalAminoAcidEvidence:
    return CriticalAminoAcidEvidence(
        criticality_kind=CriticalityKind.CRITICAL_RESIDUE,
        motif_or_domain_name="Gly-X-Y triple-helix glycine",
        function_role_established=True,
        additional_points=2.0,
        max_score_not_reached=True,
        observed_in_affected=True,
        double_counting_considered=True,
    )


def _domain_evidence() -> CriticalAminoAcidEvidence:
    """A critical-domain determination: SM 7 makes no specific point recommendation."""
    return CriticalAminoAcidEvidence(
        criticality_kind=CriticalityKind.CRITICAL_DOMAIN,
        motif_or_domain_name="documented critical functional domain",
        function_role_established=True,
        additional_points=0.0,
        max_score_not_reached=True,
        observed_in_affected=False,
        double_counting_considered=True,
    )


def test_residue_evidence_round_trips_json() -> None:
    original = _residue_evidence()
    rehydrated = CriticalAminoAcidEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original
    assert rehydrated.criticality_kind is CriticalityKind.CRITICAL_RESIDUE


def test_domain_evidence_round_trips_json() -> None:
    original = _domain_evidence()
    rehydrated = CriticalAminoAcidEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original
    assert rehydrated.criticality_kind is CriticalityKind.CRITICAL_DOMAIN


def test_evidence_is_permissive_when_empty() -> None:
    empty = CriticalAminoAcidEvidence()
    assert empty.criticality_kind is None
    assert empty.motif_or_domain_name is None
    assert empty.function_role_established is None
    assert empty.additional_points is None
    assert empty.max_score_not_reached is None
    assert empty.observed_in_affected is None
    assert empty.double_counting_considered is None


def test_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        CriticalAminoAcidEvidence(not_a_field=1)


def test_criticality_kind_values_round_trip() -> None:
    for kind in CriticalityKind:
        assert CriticalAminoAcidEvidence(criticality_kind=kind).criticality_kind is kind


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in ("CriticalAminoAcidEvidence", "CriticalityKind"):
        assert name in svcv4_model.__all__
