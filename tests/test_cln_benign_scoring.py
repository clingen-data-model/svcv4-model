"""Tests for the CLN benign-pair scorers (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    AgeMatchedPenetrance,
    Case,
    CompoundHetVariant,
    Phase,
    PhenoSeverity,
    Zygosity,
)
from svcv4_model.scoring import reference_score_cln_alt, reference_score_cln_uaf

NEAR = AgeMatchedPenetrance.NEAR_100
MID = AgeMatchedPenetrance.PCT_80_100
LOW = AgeMatchedPenetrance.LT_80


def test_uaf_dominant_penetrance_rows() -> None:
    for pen, expected in [(NEAR, -4.0), (MID, -2.0), (LOW, 0.0)]:
        c = Case(age_matched_penetrance=pen)
        r = reference_score_cln_uaf(c, moi=MOI.AD)
        assert r.parent_code == "CLN"
        assert r.sub_code_points["CLN_UAF"] == expected
        assert r.parent_total == expected


def test_uaf_recessive_homozygous() -> None:
    c = Case(age_matched_penetrance=NEAR, vbc_zygosity=Zygosity.HOM)
    assert reference_score_cln_uaf(c, moi=MOI.AR).sub_code_points["CLN_UAF"] == -4.0


def test_uaf_xlinked_hemizygous() -> None:
    c = Case(age_matched_penetrance=NEAR, vbc_zygosity=Zygosity.HEMI)
    assert reference_score_cln_uaf(c, moi=MOI.XLR).sub_code_points["CLN_UAF"] == -4.0


def test_uaf_semidominant_uses_dominant_column() -> None:
    # SD shares the "Dominantly Inherited Or Semidominant" column (SM 4 Table 5)
    c = Case(age_matched_penetrance=NEAR)
    assert reference_score_cln_uaf(c, moi=MOI.SD).sub_code_points["CLN_UAF"] == -4.0


def test_uaf_xld_counts_as_recessive_xlinked() -> None:
    # XLD (like XLR/AR) uses the recessive/X-linked columns
    c = Case(age_matched_penetrance=NEAR, vbc_zygosity=Zygosity.HEMI)
    assert reference_score_cln_uaf(c, moi=MOI.XLD).sub_code_points["CLN_UAF"] == -4.0


def test_uaf_recessive_het_trans_p_vs_lp() -> None:
    # trans-P uses the -4/-2/0 column; trans-LP uses the reduced -2/-1/0 column
    p = Case(
        age_matched_penetrance=NEAR,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=CompoundHetVariant(classification="P"),
    )
    lp_near = Case(
        age_matched_penetrance=NEAR,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=CompoundHetVariant(classification="LP"),
    )
    lp_mid = Case(
        age_matched_penetrance=MID,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=CompoundHetVariant(classification="likely_pathogenic"),
    )
    assert reference_score_cln_uaf(p, moi=MOI.AR).sub_code_points["CLN_UAF"] == -4.0
    assert reference_score_cln_uaf(lp_near, moi=MOI.AR).sub_code_points["CLN_UAF"] == -2.0
    assert reference_score_cln_uaf(lp_mid, moi=MOI.AR).sub_code_points["CLN_UAF"] == -1.0


def test_uaf_recessive_het_no_trans_plp_is_zero() -> None:
    c = Case(age_matched_penetrance=NEAR, vbc_zygosity=Zygosity.HET)  # no compound_het_variant
    assert reference_score_cln_uaf(c, moi=MOI.AR).sub_code_points["CLN_UAF"] == 0.0


def test_uaf_penetrance_none_is_zero() -> None:
    c = Case(vbc_zygosity=Zygosity.HOM)  # penetrance None
    assert reference_score_cln_uaf(c, moi=MOI.AR).sub_code_points["CLN_UAF"] == 0.0


def test_uaf_nd_when_moi_or_zygosity_unknown() -> None:
    r = reference_score_cln_uaf(Case(age_matched_penetrance=NEAR), moi=None)
    assert r.sub_code_points == {}
    # recessive with unknown zygosity -> cannot pick a column
    rec = Case(age_matched_penetrance=NEAR)  # vbc_zygosity None
    r2 = reference_score_cln_uaf(rec, moi=MOI.AR)
    assert r2.sub_code_points == {}
    assert r2.parent_total is None


def _alt(classification: str, *, same_gene: bool) -> AdditionalVariant:
    # same-gene (ALTV) is signalled by a captured phase_in_ref_to_vbc
    return AdditionalVariant(
        classification=classification,
        phase_in_ref_to_vbc=Phase.TRANS if same_gene else None,
    )


def test_alt_mono_severity_rows() -> None:
    for sev, expected in [
        (PhenoSeverity.MONO_GT_OR_BIALLELIC_EQ_EXPECTED, 0.0),
        (PhenoSeverity.MONO_EQ_EXPECTED, -0.5),
    ]:
        c = Case(pheno_severity=sev, additional_variants=[_alt("P", same_gene=False)])
        r = reference_score_cln_alt(c, moi=MOI.AD)
        assert r.parent_code == "CLN"
        assert r.sub_code_points["CLN_ALT"] == expected


def test_alt_biallelic_lt_same_gene_high_penetrance() -> None:
    c = Case(
        pheno_severity=PhenoSeverity.BIALLELIC_LT_EXPECTED,
        age_matched_penetrance=NEAR,
        additional_variants=[_alt("P", same_gene=True)],
    )
    assert reference_score_cln_alt(c, moi=MOI.AD).sub_code_points["CLN_ALT"] == -1.0


def test_alt_biallelic_lt_different_gene_is_zero() -> None:
    c = Case(
        pheno_severity=PhenoSeverity.BIALLELIC_LT_EXPECTED,
        age_matched_penetrance=NEAR,
        additional_variants=[_alt("P", same_gene=False)],  # ALTG -> -1.0 row N/A
    )
    assert reference_score_cln_alt(c, moi=MOI.AD).sub_code_points["CLN_ALT"] == 0.0


def test_alt_biallelic_lt_low_penetrance_is_zero() -> None:
    c = Case(
        pheno_severity=PhenoSeverity.BIALLELIC_LT_EXPECTED,
        age_matched_penetrance=LOW,
        additional_variants=[_alt("P", same_gene=True)],
    )
    assert reference_score_cln_alt(c, moi=MOI.AD).sub_code_points["CLN_ALT"] == 0.0


def test_alt_nd_without_plp_alternate() -> None:
    no_alt = Case(pheno_severity=PhenoSeverity.MONO_EQ_EXPECTED)
    vus_only = Case(
        pheno_severity=PhenoSeverity.MONO_EQ_EXPECTED,
        additional_variants=[_alt("VUS", same_gene=False)],
    )
    assert reference_score_cln_alt(no_alt, moi=MOI.AD).sub_code_points == {}
    assert reference_score_cln_alt(vus_only, moi=MOI.AD).sub_code_points == {}


def test_alt_nd_without_pheno_severity() -> None:
    c = Case(additional_variants=[_alt("P", same_gene=False)])  # pheno_severity None
    r = reference_score_cln_alt(c, moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_classify_plp_normalization() -> None:
    from svcv4_model.scoring.hod.clinical import _classify_plp

    assert _classify_plp("P") == "P"
    assert _classify_plp("pathogenic") == "P"
    assert _classify_plp("LP") == "LP"
    assert _classify_plp("Likely_Pathogenic") == "LP"
    assert _classify_plp("VUS") is None
    assert _classify_plp(None) is None
