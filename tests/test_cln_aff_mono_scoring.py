"""Tests for reference_score_cln_aff_mono (SM 4 Table 1, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    Case,
    CaseTesting,
    PhenoSpecificity,
    TriState,
)
from svcv4_model.scoring import reference_score_cln_aff_mono

SPEC = PhenoSpecificity.SPECIFIC
CONS = PhenoSpecificity.CONSISTENT
INC = PhenoSpecificity.INCONSISTENT

_THOROUGH = CaseTesting(
    covers_all_genes_relevant_to_mde=TriState.TRUE,
    non_genetic_etiology_excluded=TriState.TRUE,
)


def _av(classification: str) -> AdditionalVariant:
    return AdditionalVariant(classification=classification)


def test_specific_best_middle_plp() -> None:
    best = Case(pheno_specificity_for_mde=SPEC, testing=_THOROUGH)
    middle = Case(
        pheno_specificity_for_mde=SPEC,
        testing=CaseTesting(covers_all_genes_relevant_to_mde=TriState.FALSE),
    )
    vus = Case(pheno_specificity_for_mde=SPEC, testing=_THOROUGH, additional_variants=[_av("VUS")])
    plp = Case(pheno_specificity_for_mde=SPEC, testing=_THOROUGH, additional_variants=[_av("P")])
    assert reference_score_cln_aff_mono(best, moi=MOI.AD).sub_code_points["CLN_AFF"] == 1.0
    assert reference_score_cln_aff_mono(middle, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5
    assert reference_score_cln_aff_mono(vus, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5
    assert reference_score_cln_aff_mono(plp, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.0


def test_consistent_best_middle_plp() -> None:
    best = Case(pheno_specificity_for_mde=CONS, testing=_THOROUGH)
    middle = Case(pheno_specificity_for_mde=CONS)  # testing None -> middle
    plp = Case(pheno_specificity_for_mde=CONS, testing=_THOROUGH, additional_variants=[_av("LP")])
    assert reference_score_cln_aff_mono(best, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5
    assert reference_score_cln_aff_mono(middle, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.25
    assert reference_score_cln_aff_mono(plp, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.0


def test_inconsistent_is_recorded_zero() -> None:
    c = Case(pheno_specificity_for_mde=INC, testing=_THOROUGH)
    r = reference_score_cln_aff_mono(c, moi=MOI.AD)
    assert r.parent_code == "CLN"
    assert r.sub_code_points["CLN_AFF"] == 0.0
    assert r.parent_total == 0.0


def test_best_tier_tristate_edges() -> None:
    # None/UNKNOWN on either testing flag -> middle; a B/LB alt does NOT block best
    unk = Case(
        pheno_specificity_for_mde=SPEC,
        testing=CaseTesting(
            covers_all_genes_relevant_to_mde=TriState.TRUE,
            non_genetic_etiology_excluded=TriState.UNKNOWN,
        ),
    )
    benign_alt = Case(
        pheno_specificity_for_mde=SPEC, testing=_THOROUGH, additional_variants=[_av("B")]
    )
    assert reference_score_cln_aff_mono(unk, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5
    assert reference_score_cln_aff_mono(benign_alt, moi=MOI.AD).sub_code_points["CLN_AFF"] == 1.0


def test_testing_none_does_not_crash() -> None:
    c = Case(pheno_specificity_for_mde=SPEC)  # testing None
    assert reference_score_cln_aff_mono(c, moi=MOI.AD).sub_code_points["CLN_AFF"] == 0.5


def test_nd_when_pheno_specificity_none() -> None:
    r = reference_score_cln_aff_mono(Case(), moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
