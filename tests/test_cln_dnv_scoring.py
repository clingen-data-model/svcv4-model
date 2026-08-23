"""Tests for reference_score_cln_dnv (SM 4 Table 3, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import MOI, Case, PhenoSpecificity, TriState
from svcv4_model.scoring import reference_score_cln_dnv

SPEC = PhenoSpecificity.SPECIFIC
CONS = PhenoSpecificity.CONSISTENT
INC = PhenoSpecificity.INCONSISTENT


def _dnv(case: Case, moi: MOI = MOI.AD) -> float | None:
    return reference_score_cln_dnv(case, moi=moi).sub_code_points.get("CLN_DNV")


def test_specific_mono_confirmed_and_unconfirmed() -> None:
    conf = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.TRUE)
    unconf = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.FALSE)
    r = reference_score_cln_dnv(conf, moi=MOI.AD)
    assert r.parent_code == "CLN"
    assert r.sub_code_points["CLN_DNV"] == 7.0
    assert r.parent_total == 7.0
    assert _dnv(unconf) == 2.0


def test_consistent_confirmed_and_unconfirmed() -> None:
    conf = Case(pheno_specificity_for_mde=CONS, confirmed_parental_relationship=TriState.TRUE)
    unconf = Case(pheno_specificity_for_mde=CONS, confirmed_parental_relationship=TriState.FALSE)
    assert _dnv(conf) == 4.0
    assert _dnv(unconf) == 1.0


def test_inconsistent_is_recorded_zero() -> None:
    c = Case(pheno_specificity_for_mde=INC, confirmed_parental_relationship=TriState.TRUE)
    r = reference_score_cln_dnv(c, moi=MOI.AD)
    assert r.sub_code_points["CLN_DNV"] == 0.0
    assert r.parent_total == 0.0


def test_biallelic_disorder_folds_specific_to_consistent() -> None:
    # SPECIFIC row is mono-only; AR/XLR disorders use the CONSISTENT row
    conf = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.TRUE)
    assert _dnv(conf, moi=MOI.AR) == 4.0
    assert _dnv(conf, moi=MOI.XLR) == 4.0
    assert _dnv(conf, moi=MOI.AD) == 7.0  # mono keeps SPECIFIC


def test_unconfirmed_when_parental_none_or_unknown() -> None:
    none_case = Case(pheno_specificity_for_mde=SPEC)  # confirmed_parental_relationship None
    unk = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.UNKNOWN)
    assert _dnv(none_case) == 2.0
    assert _dnv(unk) == 2.0


def test_provenance_flags_plus7_caveat() -> None:
    c = Case(pheno_specificity_for_mde=SPEC, confirmed_parental_relationship=TriState.TRUE)
    r = reference_score_cln_dnv(c, moi=MOI.AD)
    assert any("coding" in p or "**" in p for p in r.provenance)


def test_nd_when_pheno_specificity_none() -> None:
    r = reference_score_cln_dnv(Case(), moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
