"""Tests for reference_score_exon_duplication (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.exon_duplication import (
    ExonDuplicationAssessment,
    ExonDuplicationOutcome,
    ExonDuplicationPredictiveEvidence,
)
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_exon_duplication

MOD = GeneDiseaseValidity.MODERATE
B = VariantClassification.BENIGN
P = VariantClassification.PATHOGENIC


def _mer(mech: GenccMechanism, exon: ExonRelevance) -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(gencc_mechanism=mech, exon_relevance=exon)


def _inf(cls: VariantClassification, n: int) -> InformativeVariantsEvidence:
    return InformativeVariantsEvidence(
        variants=[InformativeVariant(id=f"v{i}", classification=cls) for i in range(n)]
    )


def test_tandem_yellow_maximal() -> None:
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.TANDEM_NMD,
        parent_code=PfdParentCode.NUL,
        predictive=ExonDuplicationPredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.sub_code_points["FXN"] == 8.0
    assert r.held_combined["PRD+FXN"] == 10.0  # 6+8 capped at +10


def test_upper_orange_held_9() -> None:
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.TANDEM_NO_NMD,
        predictive=ExonDuplicationPredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        fxn_points=8.0,
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 3.0
    assert r.held_combined["PRD+FXN"] == 9.0  # 3+8 capped at +9


def test_gain_blue_fxn_is_na() -> None:
    # blue GAIN_NMD: FXN is NA -> fxn_points=8.0 is IGNORED; parent floors at -1 (PRD suppressed)
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.GAIN_NMD,
        fxn_points=8.0,  # must be ignored
        informative=_inf(B, 1),  # one benign -> INF -2.0
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert "FXN" not in r.sub_code_points  # FXN NA, not consumed
    assert "PRD+FXN" not in r.held_combined  # no held combine on a gain path
    assert r.sub_code_points["INF"] == -2.0
    assert r.parent_total == -1.0  # cap(-2, [-1, 6]) -> -1.0 (proves parent_lo=-1)


def test_gain_blue_inf_ceiling_6() -> None:
    # blue: PRD +4 (Established x All) + a big positive INF -> parent clamps to +6
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.GAIN_NMD,
        predictive=ExonDuplicationPredictiveEvidence(initial_points=4.0),
        mechanism_exon_relevance=_mer(GenccMechanism.ESTABLISHED, ExonRelevance.ALL),
        informative=_inf(P, 6),  # +2 first P + 5x+1 = +7 -> capped to +6 by inf_hi=6
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.sub_code_points["PRD"] == 4.0
    assert r.sub_code_points["INF"] == 6.0  # +7 tally clamped by inf_hi=6
    assert r.parent_total == 6.0  # cap(4+6, [-1, 6]) -> 6.0


def test_gain_green_benignity_only() -> None:
    a = ExonDuplicationAssessment(
        prediction_outcome=ExonDuplicationOutcome.GAIN_TERMINAL_EXON,
        informative=_inf(P, 1),  # a P tally +2 clamped to 0 by inf_hi=0
    )
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert "FXN" not in r.sub_code_points
    assert r.sub_code_points["INF"] == 0.0
    assert r.parent_total == 0.0


def test_whole_gene_na() -> None:
    a = ExonDuplicationAssessment(prediction_outcome=ExonDuplicationOutcome.WHOLE_GENE_NA)
    r = reference_score_exon_duplication(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.parent_total is None
    assert r.sub_code_points == {}
    assert any("NA" in p for p in r.provenance)


def test_all_seven_outcomes_score_without_error() -> None:
    for outcome in ExonDuplicationOutcome:
        r = reference_score_exon_duplication(
            ExonDuplicationAssessment(prediction_outcome=outcome), gene_disease_validity=MOD
        )
        assert r.parent_code in {"NUL", "CDS"}


def test_empty_is_all_nd() -> None:
    r = reference_score_exon_duplication(ExonDuplicationAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.parent_total is None
