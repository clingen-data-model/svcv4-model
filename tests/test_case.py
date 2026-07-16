"""Tests for the SVCv4 Case model and workflow parameters."""

from __future__ import annotations

import pytest

from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    Age,
    AgeMatchedPenetrance,
    AgeQualifier,
    AgeUnit,
    Case,
    CaseRelative,
    CaseTesting,
    CompoundHetVariant,
    Gene,
    Mde,
    Phase,
    PhenoSeverity,
    PhenoSpecificity,
    Phenotype,
    Sex,
    TriState,
    Vbc,
    WorkflowParameters,
    Zygosity,
)


def test_enums_serialize_to_tokens() -> None:
    assert MOI.AD.value == "AD"
    assert Sex.U.value == "U"
    assert TriState.UNKNOWN.value == "UNKNOWN"
    assert AgeUnit.MONTH.value == "MONTH"
    assert AgeQualifier.RANGE.value == "RANGE"


def test_age_accepts_point_and_range() -> None:
    point = Age(value=7, unit=AgeUnit.MONTH, qualifier=AgeQualifier.EXACT, raw="7 mo")
    rng = Age(min=5, max=10, unit=AgeUnit.MONTH, qualifier=AgeQualifier.RANGE, raw="5-10 months")
    assert point.value == 7
    assert rng.min == 5 and rng.max == 10


def test_phenotype_either_field_optional() -> None:
    coded = Phenotype(code="HP:0001250", name="Seizure")
    freetext = Phenotype(name="unusual gait")
    assert coded.code == "HP:0001250"
    assert freetext.code is None


def test_age_forbids_extra() -> None:
    with pytest.raises(ValueError):
        Age(value=1, unit=AgeUnit.YEAR, bogus="x")  # type: ignore[call-arg]


def _maximal_case() -> Case:
    return Case(
        id="PROBAND-1",
        family_id="FAM-1",
        sex=Sex.F,
        age=Age(value=7, unit=AgeUnit.MONTH, qualifier=AgeQualifier.EXACT, raw="7 mo"),
        phenotypes=[Phenotype(code="HP:0001250", name="Seizure")],
        pheno_specificity_for_mde=PhenoSpecificity.SPECIFIC,
        gene_specificity_for_phenotypes="50%",
        testing=CaseTesting(
            method="Exome",
            diagnostic_yield_for_phenotypes="100%",
            covers_all_genes_relevant_to_mde=TriState.TRUE,
        ),
        pheno_severity=PhenoSeverity.MONO_EQ_EXPECTED,
        age_matched_penetrance=AgeMatchedPenetrance.NEAR_100,
        confirmed_parental_relationship=TriState.UNKNOWN,
        vbc_exists=TriState.TRUE,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=CompoundHetVariant(
            id="clinvar:VCV000000002",
            phase_confidence="HIGH",
            classification="P",
        ),
        additional_variant_exists=TriState.TRUE,
        additional_variants=[
            AdditionalVariant(
                id="clinvar:VCV000000003",
                gene=Gene(
                    symbol="ABCA4",
                    id="HGNC:34",
                    mde_associated_gene="ABCA4",
                    transcript="NM_000350.3",
                ),
                zygosity=Zygosity.HOM,
                phase_in_ref_to_vbc=Phase.CIS,
                phase_confidence="LOW",
                classification="LP",
            )
        ],
        relatives=[
            CaseRelative(
                parent_of_proband=TriState.TRUE,
                sex=Sex.F,
                affected_w_mde=TriState.TRUE,
                vbc_exists=TriState.TRUE,
                vbc_zygosity=Zygosity.HET,
                cmp_het_variant_exists=TriState.FALSE,
            )
        ],
    )


def test_case_round_trips_json() -> None:
    original = _maximal_case()
    payload = original.model_dump(mode="json")
    assert payload["vbc_exists"] == "TRUE"  # tri-state serializes to token
    assert payload["additional_variant_exists"] == "TRUE"
    rehydrated = Case.model_validate(payload)
    assert rehydrated == original


def test_case_is_permissive_when_empty() -> None:
    # The superset is permissive: an empty Case is valid (applicability is the matrix's job).
    # Only the list fields carry non-None defaults.
    assert Case().model_dump(exclude_none=True) == {
        "phenotypes": [],
        "additional_variants": [],
        "relatives": [],
    }


def test_case_forbids_extra() -> None:
    payload = _maximal_case().model_dump(mode="json")
    payload["unexpected"] = "x"
    with pytest.raises(ValueError):
        Case.model_validate(payload)


def test_case_has_no_vbc_object_but_carries_vbc_status() -> None:
    # The VBC identity is a workflow parameter; the case records only its status.
    assert "vbc" not in Case.model_fields
    assert "vbc_exists" in Case.model_fields
    assert "vbc_zygosity" in Case.model_fields


def _maximal_params() -> WorkflowParameters:
    return WorkflowParameters(
        vbc=Vbc(
            id="clinvar:VCV000000001",
            gene=Gene(symbol="ABCA4", id="HGNC:34", transcript="NM_000350.3"),
        ),
        mde=Mde(curie="MONDO:0007254", label="Stargardt disease"),
        moi=MOI.AR,
        pop_frq_points=-1.0,
    )


def test_workflow_parameters_round_trip() -> None:
    original = _maximal_params()
    rehydrated = WorkflowParameters.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original
    assert "moi" not in Case.model_fields  # parameters live off the Case


def test_pop_frq_points_floor() -> None:
    with pytest.raises(ValueError):
        WorkflowParameters(pop_frq_points=-1.5)


def test_case_is_importable_from_package_root() -> None:
    import svcv4_model

    assert "Case" in svcv4_model.__all__
    assert svcv4_model.Case is Case
    assert svcv4_model.WorkflowParameters is WorkflowParameters
