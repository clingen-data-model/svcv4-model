"""Tests for reference_aggregate_cln_cases (cross-proband CLN summation, Inc 3b)."""

from __future__ import annotations

from svcv4_model.scoring import ScoreResult, reference_aggregate_cln_cases


def _sr(subs: dict[str, float]) -> ScoreResult:
    total = sum(subs.values()) if subs else None
    return ScoreResult(parent_code="CLN", sub_code_points=dict(subs), parent_total=total)


def _nd() -> ScoreResult:
    return ScoreResult(parent_code="CLN")


def test_sum_one_code_across_probands() -> None:
    r = reference_aggregate_cln_cases([_sr({"CLN_AFF": 1.0}), _sr({"CLN_AFF": 1.0})])
    assert r.parent_code == "CLN"
    assert r.sub_code_points == {"CLN_AFF": 2.0}
    assert r.parent_total == 2.0


def test_distinct_codes_union() -> None:
    r = reference_aggregate_cln_cases([_sr({"CLN_AFF": 1.0}), _sr({"CLN_DNV": 7.0})])
    assert r.sub_code_points == {"CLN_AFF": 1.0, "CLN_DNV": 7.0}
    assert r.parent_total == 8.0


def test_multi_code_proband_plus_cross_proband_sum() -> None:
    r = reference_aggregate_cln_cases(
        [_sr({"CLN_AFF": 1.0, "CLN_DNV": 7.0}), _sr({"CLN_AFF": 0.5})]
    )
    assert r.sub_code_points == {"CLN_AFF": 1.5, "CLN_DNV": 7.0}
    assert r.parent_total == 8.5


def test_pathogenic_benign_mix() -> None:
    r = reference_aggregate_cln_cases([_sr({"CLN_AFF": 1.0}), _sr({"CLN_UAF": -4.0})])
    assert r.parent_total == -3.0


def test_nd_and_empty() -> None:
    empty = reference_aggregate_cln_cases([])
    assert empty.parent_total is None
    assert empty.sub_code_points == {}
    single_nd = reference_aggregate_cln_cases([_nd()])
    assert single_nd.parent_total is None


def test_nd_plus_scored_mix() -> None:
    r = reference_aggregate_cln_cases([_nd(), _sr({"CLN_AFF": 1.0})])
    assert r.sub_code_points == {"CLN_AFF": 1.0}


def test_recorded_zero_stays_scored() -> None:
    r = reference_aggregate_cln_cases([_sr({"CLN_AFF": 0.0}), _sr({"CLN_AFF": 0.0})])
    assert r.sub_code_points == {"CLN_AFF": 0.0}
    assert r.parent_total == 0.0
