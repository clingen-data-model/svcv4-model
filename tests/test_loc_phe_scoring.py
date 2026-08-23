"""Tests for reference_score_loc_phe (SM 5 phenotype specificity, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AgeMatchedPenetrance,
    Case,
    CaseRelative,
    CaseTesting,
    TriState,
)
from svcv4_model.scoring import reference_score_loc_phe


def _case(
    yield_: str | None = None,
    *,
    relatives: list[CaseRelative] | None = None,
    penetrance: AgeMatchedPenetrance | None = None,
    gene_spec: str | None = None,
    no_testing: bool = False,
) -> Case:
    testing = None if no_testing else CaseTesting(diagnostic_yield_for_phenotypes=yield_)
    return Case(
        testing=testing,
        gene_specificity_for_phenotypes=gene_spec,
        age_matched_penetrance=penetrance,
        relatives=relatives or [],
    )


def _phe(case: Case, *, moi: MOI | None = MOI.AD) -> float | None:
    return reference_score_loc_phe(case, moi=moi).sub_code_points.get("LOC_PHE")


# --- bands ---------------------------------------------------------------
def test_band_top() -> None:
    r = reference_score_loc_phe(_case("90%"), moi=MOI.AD)
    assert r.parent_code == "LOC"
    assert r.sub_code_points["LOC_PHE"] == 4.0
    assert r.parent_total == 4.0


def test_bands() -> None:
    assert _phe(_case("45%")) == 1.0
    assert _phe(_case("60%")) == 2.0
    assert _phe(_case("75%")) == 3.0
    assert _phe(_case("20%")) == 0.0
    assert _phe(_case("2.6%")) == 0.0


def test_boundaries() -> None:
    assert _phe(_case("33%")) == 1.0
    assert _phe(_case("50%")) == 1.0
    assert _phe(_case("68%")) == 3.0
    assert _phe(_case("81%")) == 3.0
    assert _phe(_case("81.5%")) == 3.0  # (81,82) sliver folds down
    assert _phe(_case("82%")) == 4.0


def test_range_lower_bound() -> None:
    assert _phe(_case("91-93%")) == 4.0


def test_leading_lt_is_below() -> None:
    assert _phe(_case("<33%")) == 0.0  # NOT +1.0


def test_bare_proportion_scaled_but_ratio_and_subpercent_are_not() -> None:
    assert _phe(_case("0.9")) == 4.0  # proportion -> 90%
    assert _phe(_case("0.45")) == 1.0  # proportion -> 45%
    assert _phe(_case("0.5%")) == 0.0  # explicit sub-1 percent, left as 0.5
    assert _phe(_case("1 in 500")) == 0.0  # ratio parses to 1.0 (not < 1), unchanged


# --- No Data -------------------------------------------------------------
def test_nd_no_testing() -> None:
    r = reference_score_loc_phe(_case(no_testing=True), moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_nd_no_yield() -> None:
    r = reference_score_loc_phe(_case(None), moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_nd_empty_and_unparseable() -> None:
    assert reference_score_loc_phe(_case(""), moi=MOI.AD).parent_total is None
    assert reference_score_loc_phe(_case("not available"), moi=MOI.AD).parent_total is None


# --- non-segregation -----------------------------------------------------
def _affected_no_vbc() -> CaseRelative:
    return CaseRelative(affected_w_mde=TriState.TRUE, vbc_exists=TriState.FALSE)


def _unaffected_carrier() -> CaseRelative:
    return CaseRelative(affected_w_mde=TriState.FALSE, vbc_exists=TriState.TRUE)


def test_nonseg_rule_a_zeroes() -> None:
    r = reference_score_loc_phe(_case("90%", relatives=[_affected_no_vbc()]), moi=MOI.AD)
    assert r.sub_code_points["LOC_PHE"] == 0.0
    assert any("non-segregation" in p.lower() for p in r.provenance)


def test_nonseg_rule_b_zeroes() -> None:
    c = _case("90%", relatives=[_unaffected_carrier()], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _phe(c, moi=MOI.AD) == 0.0


def test_rule_b_needs_near_100() -> None:
    c1 = _case("90%", relatives=[_unaffected_carrier()], penetrance=AgeMatchedPenetrance.PCT_80_100)
    c2 = _case("90%", relatives=[_unaffected_carrier()], penetrance=None)
    assert _phe(c1, moi=MOI.AD) == 4.0
    assert _phe(c2, moi=MOI.AD) == 4.0


def test_rule_b_suppressed_for_ar() -> None:
    c = _case("90%", relatives=[_unaffected_carrier()], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _phe(c, moi=MOI.AR) == 4.0


def test_rule_a_under_ar_zeroes_with_caveat() -> None:
    r = reference_score_loc_phe(_case("90%", relatives=[_affected_no_vbc()]), moi=MOI.AR)
    assert r.sub_code_points["LOC_PHE"] == 0.0
    assert any("AR" in p and "locus" in p for p in r.provenance)


def test_moi_none_rule_a_zeroes_rule_b_does_not() -> None:
    c_a = _case("90%", relatives=[_affected_no_vbc()])
    c_b = _case("90%", relatives=[_unaffected_carrier()], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _phe(c_a, moi=None) == 0.0
    assert _phe(c_b, moi=None) == 4.0


def test_already_zero_plus_nonseg_stays_zero() -> None:
    assert _phe(_case("20%", relatives=[_affected_no_vbc()]), moi=MOI.AD) == 0.0


def test_unknown_none_relatives_do_not_trigger() -> None:
    all_unknown = CaseRelative()  # all fields None
    affected_vbc_unknown = CaseRelative(affected_w_mde=TriState.TRUE)  # vbc_exists None
    unaffected_unknown_affect = CaseRelative(  # affected UNKNOWN + vbc present -> no rule b
        affected_w_mde=TriState.UNKNOWN, vbc_exists=TriState.TRUE
    )
    for rel in (all_unknown, affected_vbc_unknown, unaffected_unknown_affect):
        c = _case("90%", relatives=[rel], penetrance=AgeMatchedPenetrance.NEAR_100)
        assert _phe(c, moi=MOI.AD) == 4.0


def test_gene_specificity_ignored() -> None:
    r = reference_score_loc_phe(_case(None, gene_spec="100%"), moi=MOI.AD)
    assert r.parent_total is None  # gene_specificity is not the band input
