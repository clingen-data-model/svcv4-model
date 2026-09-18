"""Tests for reference_score_loc_seg (SM 5 Figure 2 co-segregation, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AgeMatchedPenetrance,
    Case,
    CaseRelative,
    TriState,
    Zygosity,
)
from svcv4_model.scoring import reference_score_loc_seg


def _case(
    relatives: list[CaseRelative],
    *,
    penetrance: AgeMatchedPenetrance | None = None,
    vbc_zyg: Zygosity | None = None,
) -> Case:
    return Case(
        age_matched_penetrance=penetrance,
        vbc_zygosity=vbc_zyg,
        relatives=relatives,
    )


def _seg(case: Case, *, moi: MOI | None) -> float | None:
    return reference_score_loc_seg(case, moi=moi).sub_code_points.get("LOC_SEG")


def _aff_carrier(
    zyg: Zygosity = Zygosity.HET, *, comphet: bool = False, severe: bool = False
) -> CaseRelative:
    return CaseRelative(
        affected_w_mde=TriState.TRUE,
        vbc_exists=TriState.TRUE,
        vbc_zygosity=zyg,
        cmp_het_variant_exists=TriState.TRUE if comphet else None,
        severe_phenotype=TriState.TRUE if severe else None,
    )


def _unaff(*, carrier: bool = False, zyg: Zygosity | None = None) -> CaseRelative:
    return CaseRelative(
        affected_w_mde=TriState.FALSE,
        vbc_exists=TriState.TRUE if carrier else TriState.FALSE,
        vbc_zygosity=zyg,
    )


def _affected_no_vbc() -> CaseRelative:  # non-segregation rule (a)
    return CaseRelative(affected_w_mde=TriState.TRUE, vbc_exists=TriState.FALSE)


# --- affected co-segregant tiers (SM 5 Figure 2) -------------------------
def test_ad_affected_het_is_one_each_and_sums() -> None:
    r = reference_score_loc_seg(_case([_aff_carrier(), _aff_carrier(), _aff_carrier()]), moi=MOI.AD)
    assert r.parent_code == "LOC"
    assert r.sub_code_points["LOC_SEG"] == 3.0
    assert r.authoritative is False


def test_sum_caps_at_four() -> None:
    rels = [_aff_carrier() for _ in range(5)]  # 5 x +1.0 = 5.0
    r = reference_score_loc_seg(_case(rels), moi=MOI.AD)
    assert r.sub_code_points["LOC_SEG"] == 4.0
    assert any("capped" in p for p in r.provenance)


def test_ar_affected_hom_or_comphet_is_two() -> None:
    assert _seg(_case([_aff_carrier(Zygosity.HOM)]), moi=MOI.AR) == 2.0
    assert _seg(_case([_aff_carrier(Zygosity.HET, comphet=True)]), moi=MOI.AR) == 2.0
    # AR affected het without a comp-het partner is not an informative AR segregant
    assert (
        reference_score_loc_seg(_case([_aff_carrier(Zygosity.HET)]), moi=MOI.AR).parent_total
        is None
    )


def test_sd_severe_is_two_affected_is_one() -> None:
    assert _seg(_case([_aff_carrier(Zygosity.HOM, severe=True)]), moi=MOI.SD) == 2.0
    assert _seg(_case([_aff_carrier(Zygosity.HET)]), moi=MOI.SD) == 1.0


def test_x_linked_affected_is_one() -> None:
    assert _seg(_case([_aff_carrier(Zygosity.HEMI)]), moi=MOI.XLR) == 1.0
    assert _seg(_case([_aff_carrier(Zygosity.HET)]), moi=MOI.XLD) == 1.0


# --- unaffected co-segregant tiers ---------------------------------------
def test_unaffected_wt_is_one_only_at_near_100() -> None:
    near = _case([_unaff()], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _seg(near, moi=MOI.AD) == 1.0
    # without near-100 penetrance the unaffected WT is not counted -> _ND
    lower = _case([_unaff()], penetrance=AgeMatchedPenetrance.PCT_80_100)
    assert reference_score_loc_seg(lower, moi=MOI.AD).parent_total is None


def test_ar_unaffected_is_point_four_carrier_or_wt() -> None:
    # AR unaffected het carrier OR wild type -> +0.4, not penetrance-gated
    assert _seg(_case([_unaff(carrier=True, zyg=Zygosity.HET)]), moi=MOI.AR) == 0.4
    assert _seg(_case([_unaff()]), moi=MOI.AR) == 0.4


# --- non-segregation terminal branch -------------------------------------
def test_nonseg_flips_minus_four_for_ad() -> None:
    r = reference_score_loc_seg(_case([_affected_no_vbc()]), moi=MOI.AD)
    assert r.sub_code_points["LOC_SEG"] == -4.0
    assert any("non-segregation" in p.lower() for p in r.provenance)


def test_nonseg_flips_minus_four_for_ar_homozygous_only() -> None:
    hom = _case([_affected_no_vbc()], vbc_zyg=Zygosity.HOM)
    assert _seg(hom, moi=MOI.AR) == -4.0
    # plain AR (compound-het / non-homozygous proband): zero, NOT flipped
    het = _case([_affected_no_vbc()], vbc_zyg=Zygosity.HET)
    assert _seg(het, moi=MOI.AR) == 0.0


def test_nonseg_no_flip_for_semidominant() -> None:
    assert _seg(_case([_affected_no_vbc()]), moi=MOI.SD) == 0.0


def test_nonseg_takes_precedence_over_positive_segregations() -> None:
    rels = [_aff_carrier(), _aff_carrier(), _aff_carrier(), _affected_no_vbc()]
    assert _seg(_case(rels), moi=MOI.AD) == -4.0  # not +3.0


def test_ar_unaffected_carrier_is_not_a_nonsegregation() -> None:
    # rule (b) is suppressed for AR, so an unaffected AR carrier scores +0.4, not a flip
    c = _case([_unaff(carrier=True, zyg=Zygosity.HET)], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _seg(c, moi=MOI.AR) == 0.4


def test_ad_unaffected_carrier_near_100_is_nonseg_flip() -> None:
    c = _case([_unaff(carrier=True)], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _seg(c, moi=MOI.AD) == -4.0


# --- No Data -------------------------------------------------------------
def test_moi_none_is_nd() -> None:
    r = reference_score_loc_seg(_case([_aff_carrier()]), moi=None)
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_no_relatives_is_nd() -> None:
    assert reference_score_loc_seg(_case([]), moi=MOI.AD).parent_total is None


def test_uninformative_relatives_is_nd() -> None:
    all_unknown = CaseRelative()  # every field None
    assert reference_score_loc_seg(_case([all_unknown]), moi=MOI.AD).parent_total is None
