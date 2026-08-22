"""Tests for reference_score_missense_amino_acid (non-authoritative)."""

from __future__ import annotations

from svcv4_model.informative import VariantClassification
from svcv4_model.mechanism import ExonRelevance
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
)
from svcv4_model.scoring import reference_score_missense_amino_acid


def _inf(
    *pairs: tuple[MissenseInfCategory, VariantClassification],
) -> MissenseInformativeEvidence:
    return MissenseInformativeEvidence(
        variants=[MissenseInformativeVariant(category=c, classification=cls) for c, cls in pairs]
    )


def test_prd_transcript_relevance() -> None:
    cases = [(ExonRelevance.ALL, 4.0), (ExonRelevance.MOST, 2.0), (ExonRelevance.FEW, 0.0)]
    for exon, expected in cases:
        a = MissenseAminoAcidAssessment(
            predictive=MissensePredictiveEvidence(initial_points=4.0, transcript_relevance=exon)
        )
        r = reference_score_missense_amino_acid(a)
        assert r.parent_code == "MIS"
        assert r.sub_code_points["PRD"] == expected


def test_prd_negative_passthrough() -> None:
    a = MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(
            initial_points=-3.0, transcript_relevance=ExonRelevance.FEW
        )
    )
    r = reference_score_missense_amino_acid(a)
    assert r.sub_code_points["PRD"] == -3.0  # skips relevance, floored -4


def test_maximal_held_and_total() -> None:
    a = MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(
            initial_points=4.0, transcript_relevance=ExonRelevance.ALL
        ),
        fxn_points=8.0,
        informative=_inf(
            (MissenseInfCategory.SAME_AA_PATHOGENIC, VariantClassification.PATHOGENIC)
        ),
    )
    r = reference_score_missense_amino_acid(a)
    assert r.sub_code_points["PRD"] == 4.0
    assert r.sub_code_points["FXN"] == 8.0
    assert r.held_combined["PRD+FXN"] == 6.0  # cap(4+8, +6)
    assert r.sub_code_points["INF"] == 4.0
    assert r.parent_total == 9.0  # cap(6+4, +9)


def test_held_floor() -> None:
    a = MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(initial_points=-4.0),
        fxn_points=-8.0,
    )
    r = reference_score_missense_amino_acid(a)
    assert r.held_combined["PRD+FXN"] == -8.0  # cap(-12, -8)


def test_inf_cap_and_categories() -> None:
    # cat1 P (+4) + cat4 B (-4) -> 0
    a = MissenseAminoAcidAssessment(
        informative=_inf(
            (MissenseInfCategory.SAME_AA_PATHOGENIC, VariantClassification.PATHOGENIC),
            (MissenseInfCategory.SAME_AA_BENIGN, VariantClassification.BENIGN),
        )
    )
    r = reference_score_missense_amino_acid(a)
    assert r.sub_code_points["INF"] == 0.0


def test_fxn_nd_and_inf_nd() -> None:
    a = MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(
            initial_points=4.0, transcript_relevance=ExonRelevance.ALL
        )
    )
    r = reference_score_missense_amino_acid(a)
    assert "FXN" not in r.sub_code_points
    assert "INF" not in r.sub_code_points
    assert r.held_combined["PRD+FXN"] == 4.0  # prd alone
    assert r.parent_total == 4.0


def test_empty_is_all_nd() -> None:
    r = reference_score_missense_amino_acid(MissenseAminoAcidAssessment())
    assert r.parent_code == "MIS"
    assert r.sub_code_points == {}
    assert r.parent_total is None
