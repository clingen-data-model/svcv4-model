"""Tests for reference_combine_case (cross-code combine, aggregation Inc 4)."""

from __future__ import annotations

from svcv4_model.informative import VariantClassification as VC
from svcv4_model.scoring import (
    MissenseScoreResult,
    ScoreResult,
    reference_classify,
    reference_combine_case,
)


def _fam(code: str, total: float | None) -> ScoreResult:
    subs = {} if total is None else {code: total}
    return ScoreResult(parent_code=code, sub_code_points=subs, parent_total=total)


def _mis(applied_parent_code: str, applied_total: float | None) -> MissenseScoreResult:
    empty = ScoreResult(parent_code="MIS")
    return MissenseScoreResult(
        amino_acid=empty,
        splice=empty,
        selected_path="AMINO_ACID",
        applied_parent_code=applied_parent_code,
        applied_total=applied_total,
    )


def test_four_families_sum() -> None:
    r = reference_combine_case(
        [_fam("NUL", 10.0), _fam("POP", -1.0), _fam("CLN", 4.0), _fam("LOC", 4.0)]
    )
    assert r.parent_total == 17.0
    assert set(r.sub_code_points) == {"NUL", "POP", "CLN", "LOC"}


def test_missense_take_higher_input() -> None:
    r = reference_combine_case([_mis("MIS", 9.0), _fam("CLN", 1.0)])
    assert r.sub_code_points == {"MIS": 9.0, "CLN": 1.0}
    assert r.parent_total == 10.0


def test_nd_family_skipped() -> None:
    r = reference_combine_case([_fam("POP", 0.0), _fam("CLN", None)])
    assert r.sub_code_points == {"POP": 0.0}
    assert r.parent_total == 0.0


def test_unclamped_high_and_low() -> None:
    assert reference_combine_case([_fam("NUL", 10.0), _fam("CLN", 8.0)]).parent_total == 18.0
    assert reference_combine_case([_fam("POP", -6.0), _fam("CDS", -8.0)]).parent_total == -14.0


def test_duplicate_family_raises() -> None:
    import pytest

    with pytest.raises(ValueError, match="duplicate family code"):
        reference_combine_case([_fam("CLN", 1.0), _fam("CLN", 2.0)])


def test_all_nd_and_empty() -> None:
    assert reference_combine_case([]).parent_total is None
    r = reference_combine_case([_fam("POP", None), _fam("CLN", None)])
    assert r.parent_total is None
    assert r.sub_code_points == {}


def test_missense_applied_none_contributes_zero() -> None:
    r = reference_combine_case([_mis("MIS", None), _fam("CLN", 2.0)])
    assert r.sub_code_points == {"CLN": 2.0}
    assert r.parent_total == 2.0


def test_chains_to_band() -> None:
    total = reference_combine_case(
        [_fam("NUL", 10.0), _fam("POP", -1.0), _fam("CLN", 4.0), _fam("LOC", 4.0)]
    ).parent_total
    assert total is not None
    assert reference_classify(total).category == VC.PATHOGENIC
