"""Tests for reference_score_missense (the MIS_-vs-SPL_ take-higher)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseAssessment,
    MissensePredictiveEvidence,
    MissenseSpliceAssessment,
)
from svcv4_model.scoring import reference_score_missense
from svcv4_model.splice import SplicePredictionOutcome, SplicePredictiveEvidence

MOD = GeneDiseaseValidity.MODERATE


def _amino(prd: float) -> MissenseAminoAcidAssessment:
    # a positive MIS_PRD via a predictor score at All-transcript relevance
    return MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(
            initial_points=prd, transcript_relevance=ExonRelevance.ALL
        )
    )


def _splice_yellow(fxn: float) -> MissenseSpliceAssessment:
    return MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(initial_points=3.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        fxn_points=fxn,
    )


def test_splice_higher_positive_selects_splice() -> None:
    a = MissenseAssessment(amino_acid=_amino(2.0), splice=_splice_yellow(8.0))
    r = reference_score_missense(a, gene_disease_validity=MOD)
    # amino MIS_ = 2; splice SPL_ = cap(3+8, +9)=9 -> parent 9 (> 2) -> SPLICE
    assert r.selected_path == "SPLICE"
    assert r.applied_parent_code == "SPL"
    assert r.applied_total == 9.0
    assert r.amino_acid.parent_total == 2.0  # both saved
    assert r.splice.parent_total == 9.0


def test_amino_higher_selects_amino() -> None:
    a = MissenseAssessment(amino_acid=_amino(4.0), splice=_splice_yellow(0.0))
    r = reference_score_missense(a, gene_disease_validity=MOD)
    # amino = 4; splice = cap(3+0, +9)=3 -> amino higher -> AMINO_ACID
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 4.0


def test_positive_tie_selects_amino() -> None:
    # amino = 3; splice yellow with fxn 0 -> 3 -> tie -> AMINO_ACID
    a = MissenseAssessment(amino_acid=_amino(3.0), splice=_splice_yellow(0.0))
    r = reference_score_missense(a, gene_disease_validity=MOD)
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 3.0


def test_negative_splice_selects_amino() -> None:
    a = MissenseAssessment(
        amino_acid=_amino(2.0),
        splice=MissenseSpliceAssessment(
            prediction_outcome=SplicePredictionOutcome.UNLIKELY,
            predictive=SplicePredictiveEvidence(initial_points=-1.0),
        ),
    )
    r = reference_score_missense(a, gene_disease_validity=MOD)
    # splice violet -> parent -1 (negative) -> AMINO_ACID
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 2.0


def test_missing_splice_uses_amino() -> None:
    a = MissenseAssessment(amino_acid=_amino(2.0))  # splice None -> empty -> total None
    r = reference_score_missense(a, gene_disease_validity=MOD)
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 2.0


def test_missing_amino_positive_splice_uses_splice() -> None:
    a = MissenseAssessment(splice=_splice_yellow(8.0))  # amino None -> total None; splice 9
    r = reference_score_missense(a, gene_disease_validity=MOD)
    assert r.selected_path == "SPLICE"
    assert r.applied_total == 9.0


def test_both_empty_uses_amino_none_total() -> None:
    r = reference_score_missense(MissenseAssessment(), gene_disease_validity=MOD)
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_parent_code == "MIS"
    assert r.applied_total is None
