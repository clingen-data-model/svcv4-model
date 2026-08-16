"""Tests for the SVCv4 PFD Functional Assay Evidence model (SM 20)."""

from __future__ import annotations

import pytest

from svcv4_model.functional import (
    AnimalModelEvidence,
    AnimalModelType,
    FunctionalAssayEvidence,
    MolecularMechanism,
    PhenotypeReplication,
    ProteinAssayType,
    ProteinFunctionalAssay,
)


def _maximal_protein() -> ProteinFunctionalAssay:
    return ProteinFunctionalAssay(
        assay_type=ProteinAssayType.ENZYME_KINETIC,
        odds_path=8.42,
        has_pathogenic_controls=True,
        has_benign_controls=True,
        pathogenic_control_count=11,
        benign_control_count=10,
        has_false_positives_or_negatives=False,
        fidelity_to_mechanism=True,
    )


def _maximal_animal() -> AnimalModelEvidence:
    return AnimalModelEvidence(
        model_type=AnimalModelType.ENGINEERED,
        species="mouse",
        ortholog_established=True,
        phenotype_replication=PhenotypeReplication.SPECIFIC,
        inheritance_match=True,
        local_sequence_similarity_high=True,
        fidelity_to_mechanism=True,
    )


def _maximal() -> FunctionalAssayEvidence:
    return FunctionalAssayEvidence(
        disease_mechanism=MolecularMechanism.LOSS_OF_FUNCTION,
        protein_assays=[_maximal_protein()],
        animal_models=[_maximal_animal()],
    )


def test_evidence_round_trips_json() -> None:
    original = _maximal()
    rehydrated = FunctionalAssayEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_evidence_is_permissive_when_empty() -> None:
    ev = FunctionalAssayEvidence()
    assert ev.protein_assays == []
    assert ev.animal_models == []


def test_all_three_models_forbid_extra() -> None:
    for model in (FunctionalAssayEvidence, ProteinFunctionalAssay, AnimalModelEvidence):
        with pytest.raises(ValueError):
            model(not_a_field=1)


def test_mechanism_values_round_trip() -> None:
    for mech in MolecularMechanism:
        assert FunctionalAssayEvidence(disease_mechanism=mech).disease_mechanism is mech


def test_protein_enums_round_trip() -> None:
    for at in ProteinAssayType:
        assert ProteinFunctionalAssay(assay_type=at).assay_type is at


def test_animal_enums_round_trip() -> None:
    for mt in AnimalModelType:
        assert AnimalModelEvidence(model_type=mt).model_type is mt
    for pr in PhenotypeReplication:
        assert AnimalModelEvidence(phenotype_replication=pr).phenotype_replication is pr


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "FunctionalAssayEvidence" in svcv4_model.__all__
