"""Tests for reference_score_cln_proband (per-proband CLN combine, aggregation Inc 3a)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    AgeMatchedPenetrance,
    Case,
    CaseRelative,
    CaseTesting,
    PhenoSeverity,
    PhenoSpecificity,
    Sex,
    TriState,
    Zygosity,
)
from svcv4_model.scoring import reference_score_cln_proband

_THOROUGH = CaseTesting(
    covers_all_genes_relevant_to_mde=TriState.TRUE,
    non_genetic_etiology_excluded=TriState.TRUE,
)
_DENOVO_PARENTS = [
    CaseRelative(parent_of_proband=TriState.TRUE, vbc_exists=TriState.FALSE),
    CaseRelative(parent_of_proband=TriState.TRUE, vbc_exists=TriState.FALSE),
]


def _affected(**kw: object) -> Case:
    base: dict[str, object] = {
        "pheno_specificity_for_mde": PhenoSpecificity.SPECIFIC,
        "testing": _THOROUGH,
    }
    base.update(kw)
    return Case(**base)


def _codes(r: object) -> dict[str, float]:
    return r.sub_code_points  # type: ignore[attr-defined]


def test_ad_routes_to_mono() -> None:
    r = reference_score_cln_proband(_affected(), moi=MOI.AD)
    assert r.parent_code == "CLN"
    assert "CLN_AFF" in r.sub_code_points
    assert "CLN_UAF" not in r.sub_code_points


def test_xld_routes_to_mono() -> None:
    r = reference_score_cln_proband(_affected(), moi=MOI.XLD)
    assert "CLN_AFF" in r.sub_code_points


def test_ar_routes_biallelic_and_no_alt() -> None:
    # AR proband explained by a P/LP alternate cause: CLN_ALT must NOT be scored (SM 4 L186).
    alt = AdditionalVariant(classification="P", phase_in_ref_to_vbc=None)
    r = reference_score_cln_proband(
        _affected(
            vbc_zygosity=Zygosity.HOM,
            additional_variants=[alt],
            pheno_severity=PhenoSeverity.BIALLELIC_LT_EXPECTED,
        ),
        moi=MOI.AR,
    )
    assert "CLN_AFF" in r.sub_code_points
    assert "CLN_ALT" not in r.sub_code_points


def test_xlr_by_sex() -> None:
    male = reference_score_cln_proband(_affected(sex=Sex.M), moi=MOI.XLR)
    female = reference_score_cln_proband(
        _affected(sex=Sex.F, vbc_zygosity=Zygosity.HOM), moi=MOI.XLR
    )
    none = reference_score_cln_proband(_affected(sex=None), moi=MOI.XLR)
    assert "CLN_AFF" in male.sub_code_points
    assert "CLN_AFF" in female.sub_code_points
    assert "CLN_AFF" not in none.sub_code_points  # XLR needs a known sex


def test_sd_by_zygosity() -> None:
    het = reference_score_cln_proband(_affected(vbc_zygosity=Zygosity.HET), moi=MOI.SD)
    hom = reference_score_cln_proband(_affected(vbc_zygosity=Zygosity.HOM), moi=MOI.SD)
    assert "CLN_AFF" in het.sub_code_points
    assert "CLN_AFF" in hom.sub_code_points


def test_aff_dnv_additivity_when_denovo() -> None:
    r = reference_score_cln_proband(
        _affected(relatives=_DENOVO_PARENTS, confirmed_parental_relationship=TriState.TRUE),
        moi=MOI.AD,
    )
    assert "CLN_AFF" in r.sub_code_points
    assert "CLN_DNV" in r.sub_code_points
    assert r.parent_total == r.sub_code_points["CLN_AFF"] + r.sub_code_points["CLN_DNV"]


def test_dnv_gated_off_when_not_denovo() -> None:
    r = reference_score_cln_proband(_affected(), moi=MOI.AD)  # no parent relatives
    assert "CLN_DNV" not in r.sub_code_points
    assert any("not inferred de-novo" in p for p in r.provenance)


def test_dnv_fold_driven_by_routing() -> None:
    # XLR male routes mono -> SPECIFIC stays -> +7.0; SD-biallelic routes biallelic -> folds -> +4.0
    xlr_male = reference_score_cln_proband(
        _affected(
            sex=Sex.M,
            relatives=_DENOVO_PARENTS,
            confirmed_parental_relationship=TriState.TRUE,
        ),
        moi=MOI.XLR,
    )
    sd_biallelic = reference_score_cln_proband(
        _affected(
            vbc_zygosity=Zygosity.HOM,
            relatives=_DENOVO_PARENTS,
            confirmed_parental_relationship=TriState.TRUE,
        ),
        moi=MOI.SD,
    )
    assert xlr_male.sub_code_points["CLN_DNV"] == 7.0
    assert sd_biallelic.sub_code_points["CLN_DNV"] == 4.0


def test_dnv_not_scored_when_aff_zero_alt_explained() -> None:
    # Affected + de-novo, but explained by a P/LP alternate cause -> CLN_AFF=0.0 -> no DNV.
    r = reference_score_cln_proband(
        _affected(
            additional_variants=[AdditionalVariant(classification="P")],
            relatives=_DENOVO_PARENTS,
            confirmed_parental_relationship=TriState.TRUE,
        ),
        moi=MOI.AD,
    )
    assert r.sub_code_points["CLN_AFF"] == 0.0
    assert "CLN_DNV" not in r.sub_code_points
    assert any("explained by alternate cause" in p for p in r.provenance)


def test_uaf_does_not_cofire_with_aff() -> None:
    # Affected proband that ALSO has age_matched_penetrance set: UAF must NOT fire.
    r = reference_score_cln_proband(
        _affected(age_matched_penetrance=AgeMatchedPenetrance.NEAR_100), moi=MOI.AD
    )
    assert "CLN_AFF" in r.sub_code_points
    assert "CLN_UAF" not in r.sub_code_points


def test_uaf_only_for_unaffected() -> None:
    r = reference_score_cln_proband(
        Case(age_matched_penetrance=AgeMatchedPenetrance.NEAR_100), moi=MOI.AD
    )
    assert "CLN_UAF" in r.sub_code_points
    assert "CLN_AFF" not in r.sub_code_points
    assert "CLN_DNV" not in r.sub_code_points


def test_moi_none_affected_unroutable() -> None:
    r = reference_score_cln_proband(_affected(), moi=None)
    assert "CLN_AFF" not in r.sub_code_points
    assert r.parent_total is None  # nothing scored -> _ND


def test_nd_proband() -> None:
    r = reference_score_cln_proband(Case(), moi=None)  # unaffected path, UAF unroutable
    assert r.parent_total is None
    assert r.sub_code_points == {}
