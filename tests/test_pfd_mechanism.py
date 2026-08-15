"""Tests for the SVCv4 PFD Molecular Mechanism & Exon Relevance model (SM 18)."""

from __future__ import annotations

import pytest

from svcv4_model.mechanism import (
    ExonRelevance,
    GenccMechanism,
    ManeStatus,
    MechanismExonRelevanceEvidence,
)


def _maximal() -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(
        gencc_mechanism=GenccMechanism.ESTABLISHED,
        exon_relevance=ExonRelevance.ALL,
        mane_status=ManeStatus.MANE_SELECT,
        exon_known_irrelevant=False,
        exon_has_established_pathogenic=True,
    )


def test_mechanism_evidence_round_trips_json() -> None:
    original = _maximal()
    rehydrated = MechanismExonRelevanceEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_mechanism_evidence_is_permissive_when_empty() -> None:
    assert MechanismExonRelevanceEvidence().gencc_mechanism is None


def test_mechanism_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MechanismExonRelevanceEvidence(not_a_field=1)


def test_enums_round_trip() -> None:
    for level in GenccMechanism:
        assert MechanismExonRelevanceEvidence(gencc_mechanism=level).gencc_mechanism is level
    for rel in ExonRelevance:
        assert MechanismExonRelevanceEvidence(exon_relevance=rel).exon_relevance is rel
    for mane in ManeStatus:
        assert MechanismExonRelevanceEvidence(mane_status=mane).mane_status is mane


def test_override_flags_accept_booleans() -> None:
    for flag in (True, False):
        ev = MechanismExonRelevanceEvidence(
            exon_known_irrelevant=flag, exon_has_established_pathogenic=flag
        )
        assert ev.exon_known_irrelevant is flag
        assert ev.exon_has_established_pathogenic is flag


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "MechanismExonRelevanceEvidence" in svcv4_model.__all__
