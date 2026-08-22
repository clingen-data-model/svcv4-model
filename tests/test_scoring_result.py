"""Tests for the reference-scorer result DTOs (non-authoritative)."""

from __future__ import annotations

import pytest

from svcv4_model.scoring.result import MissenseScoreResult, ScoreResult


def test_missense_score_result_holds_both_paths() -> None:
    mis = ScoreResult(parent_code="MIS", parent_total=5.0)
    spl = ScoreResult(parent_code="SPL", parent_total=3.0)
    r = MissenseScoreResult(
        amino_acid=mis,
        splice=spl,
        selected_path="AMINO_ACID",
        applied_parent_code="MIS",
        applied_total=5.0,
        provenance=["compared MIS_ 5.0 vs SPL_ 3.0 -> AMINO_ACID"],
    )
    assert r.amino_acid.parent_total == 5.0
    assert r.splice.parent_total == 3.0
    assert r.selected_path == "AMINO_ACID"
    assert r.applied_total == 5.0
    assert r.authoritative is False


def test_missense_score_result_authoritative_raises() -> None:
    mis = ScoreResult(parent_code="MIS")
    spl = ScoreResult(parent_code="SPL")
    with pytest.raises(ValueError, match="non-authoritative"):
        MissenseScoreResult(
            amino_acid=mis,
            splice=spl,
            selected_path="AMINO_ACID",
            applied_parent_code="MIS",
            applied_total=None,
            provenance=[],
            authoritative=True,
        )
