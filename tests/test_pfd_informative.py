"""Tests for the SVCv4 PFD Informative Variants model (SM 19)."""

from __future__ import annotations

import pytest

from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    SimilarityBasis,
    VariantClassification,
)


def _maximal_variant() -> InformativeVariant:
    return InformativeVariant(
        id="clinvar:VCV000000009",
        classification=VariantClassification.PATHOGENIC,
        similarity_basis=SimilarityBasis.SAME_EXON,
        distinct_evidence_from_vbc=True,
        star_rating=3,
        circularity_checked=True,
    )


def test_evidence_round_trips_json() -> None:
    original = InformativeVariantsEvidence(variants=[_maximal_variant()])
    rehydrated = InformativeVariantsEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_evidence_is_permissive_when_empty() -> None:
    assert InformativeVariantsEvidence().variants == []


def test_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        InformativeVariantsEvidence(not_a_field=1)


def test_variant_forbids_extra() -> None:
    with pytest.raises(ValueError):
        InformativeVariant(not_a_field=1)


def test_classification_values_round_trip() -> None:
    for cls in VariantClassification:
        assert InformativeVariant(classification=cls).classification is cls


def test_similarity_basis_values_round_trip() -> None:
    for basis in SimilarityBasis:
        assert InformativeVariant(similarity_basis=basis).similarity_basis is basis


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "InformativeVariantsEvidence" in svcv4_model.__all__
