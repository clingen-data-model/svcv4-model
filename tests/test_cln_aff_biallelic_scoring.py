"""Tests for reference_score_cln_aff_biallelic (SM 4 Table 2, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    Case,
    CaseTesting,
    CompoundHetVariant,
    CoOccurrenceLikelihood,
    PhaseConfidence,
    PhenoSpecificity,
    TriState,
    Zygosity,
)
from svcv4_model.scoring import reference_score_cln_aff_biallelic

CONS = PhenoSpecificity.CONSISTENT
INC = PhenoSpecificity.INCONSISTENT
LT = CoOccurrenceLikelihood.LT_0_0001
BETWEEN = CoOccurrenceLikelihood.BETWEEN_0_0001_0_01

_THOROUGH = CaseTesting(
    covers_all_genes_relevant_to_mde=TriState.TRUE,
    non_genetic_etiology_excluded=TriState.TRUE,
)


def _ch(
    classification: str, phase: PhaseConfidence | None, co: CoOccurrenceLikelihood | None
) -> CompoundHetVariant:
    return CompoundHetVariant(
        classification=classification, phase_confidence=phase, co_occurrence_likelihood=co
    )


def _het(
    ch: CompoundHetVariant | None,
    *,
    pheno: PhenoSpecificity = CONS,
    testing: CaseTesting | None = _THOROUGH,
    alts: list[AdditionalVariant] | None = None,
) -> Case:
    return Case(
        pheno_specificity_for_mde=pheno,
        vbc_zygosity=Zygosity.HET,
        compound_het_variant=ch,
        testing=testing,
        additional_variants=alts or [],
    )


def _score(case: Case) -> float | None:
    return reference_score_cln_aff_biallelic(case, moi=MOI.AR).sub_code_points.get("CLN_AFF")


def test_a1_row_lt_cooccurrence() -> None:
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT))) == 3.0  # conf_plp
    assert _score(_het(_ch("LP", PhaseConfidence.MED, LT))) == 1.5  # assumed_plp
    assert _score(_het(_ch("VUS", PhaseConfidence.HIGH, LT))) == 1.5  # conf_vus
    assert _score(_het(None)) == 0.0  # none (no compound-het)


def test_a2_row_between_cooccurrence() -> None:
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, BETWEEN))) == 2.0  # conf_plp
    assert _score(_het(_ch("VUS", PhaseConfidence.HIGH, BETWEEN))) == 1.0  # conf_vus


def test_assumed_plp_when_phase_confidence_none() -> None:
    # DD2: a P/LP compound-het with no phase confidence is 'assumed in trans' (not confirmed)
    assert _score(_het(_ch("P", None, LT))) == 1.5  # assumed_plp, A1


def test_hom_not_thorough_uses_b_row() -> None:
    incomplete = CaseTesting(covers_all_genes_relevant_to_mde=TriState.FALSE)
    hom = Case(pheno_specificity_for_mde=CONS, vbc_zygosity=Zygosity.HOM, testing=incomplete)
    assert reference_score_cln_aff_biallelic(hom, moi=MOI.AR).sub_code_points["CLN_AFF"] == 0.5


def test_b_row_incomplete_testing() -> None:
    incomplete = CaseTesting(covers_all_genes_relevant_to_mde=TriState.FALSE)
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT), testing=incomplete)) == 1.0
    assert _score(_het(_ch("LP", PhaseConfidence.MED, LT), testing=incomplete)) == 0.75
    assert _score(_het(_ch("VUS", PhaseConfidence.HIGH, LT), testing=incomplete)) == 0.5


def test_b_row_vus_additional_forces_incomplete() -> None:
    vus_alt = [AdditionalVariant(classification="VUS")]
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT), alts=vus_alt)) == 1.0  # B, not A1


def test_b_row_cooccurrence_unassessed() -> None:
    # thorough het but no co-occurrence bucket -> rarity unestablished -> B
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, None))) == 1.0


def test_zero_plp_diff_gene_additional() -> None:
    plp_alt = [AdditionalVariant(classification="P")]
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT), alts=plp_alt)) == 0.0


def test_zero_inconsistent_phenotype() -> None:
    assert _score(_het(_ch("P", PhaseConfidence.HIGH, LT), pheno=INC)) == 0.0


def test_assumed_vus_scores_none() -> None:
    # VUS not confirmed in trans -> 'none' column -> 0.0 (SM 4 L75)
    assert _score(_het(_ch("VUS", PhaseConfidence.MED, LT))) == 0.0


def test_hom_thorough_cooccurrence_na() -> None:
    hom = Case(pheno_specificity_for_mde=CONS, vbc_zygosity=Zygosity.HOM, testing=_THOROUGH)
    assert reference_score_cln_aff_biallelic(hom, moi=MOI.AR).sub_code_points["CLN_AFF"] == 1.0


def test_nd_when_pheno_or_zygosity_none() -> None:
    no_pheno = Case(vbc_zygosity=Zygosity.HOM)
    no_zyg = Case(pheno_specificity_for_mde=CONS)  # vbc_zygosity None
    assert reference_score_cln_aff_biallelic(no_pheno, moi=MOI.AR).sub_code_points == {}
    r = reference_score_cln_aff_biallelic(no_zyg, moi=MOI.AR)
    assert r.sub_code_points == {}
    assert r.parent_total is None
