"""Tests for the SVCv4 Case model."""

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
    CaseProbandInfo,
    CaseVariant,
    CompoundHetVariant,
    Gene,
    Phase,
    PhenoSeverity,
    PhenoSpecificity,
    Phenotype,
    Sex,
    TriState,
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
        moi=MOI.AR,
        pop_frq_points=-1.0,
        case_proband_info=CaseProbandInfo(
            sex=Sex.F,
            age=Age(value=7, unit=AgeUnit.MONTH, qualifier=AgeQualifier.EXACT, raw="7 mo"),
            phenotypes=[Phenotype(code="HP:0001250", name="Seizure")],
            pheno_specificity_for_gene=PhenoSpecificity.SPECIFIC,
            pheno_severity=PhenoSeverity.MONO_EQ_EXPECTED,
            age_matched_penetrance=AgeMatchedPenetrance.NEAR_100,
            confirmed_parental_relationship=TriState.UNKNOWN,
            all_relevant_genes_tested=TriState.TRUE,
        ),
        vbc=CaseVariant(id="clinvar:VCV000000001", zygosity=Zygosity.HET),
        compound_het_variant=CompoundHetVariant(
            id="clinvar:VCV000000002",
            zygosity=Zygosity.HET,
            phase_in_ref_to_vbc=Phase.TRANS,
            phase_confidence="high",
            classification="P",
        ),
        additional_variant_exists=TriState.TRUE,
        additional_variants=[
            AdditionalVariant(
                id="clinvar:VCV000000003",
                gene=Gene(symbol="ABCA4", mde_associated_gene="ABCA4"),
                zygosity=Zygosity.HOM,
                phase_in_ref_to_vbc=Phase.CIS,
                phase_confidence="low",
                classification="LP",
            )
        ],
    )


def test_case_round_trips_json() -> None:
    original = _maximal_case()
    payload = original.model_dump(mode="json")
    assert payload["additional_variant_exists"] == "TRUE"  # tri-state serializes to token
    rehydrated = Case.model_validate(payload)
    assert rehydrated == original


def test_case_is_permissive_when_empty() -> None:
    # The superset is permissive: an empty Case is valid (applicability is the matrix's job).
    assert Case().model_dump(exclude_none=True) == {"additional_variants": []}


def test_case_forbids_extra() -> None:
    payload = _maximal_case().model_dump(mode="json")
    payload["unexpected"] = "x"
    with pytest.raises(ValueError):
        Case.model_validate(payload)


def test_pop_frq_points_floor() -> None:
    with pytest.raises(ValueError):
        Case(pop_frq_points=-1.5)


def test_case_is_importable_from_package_root() -> None:
    import svcv4_model

    assert "Case" in svcv4_model.__all__
    assert svcv4_model.Case is Case
