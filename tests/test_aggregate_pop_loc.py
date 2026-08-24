"""Tests for the POP + LOC family subtotals (aggregation Inc 2, non-authoritative)."""

from __future__ import annotations

import pytest

from svcv4_model.scoring import ScoreResult, reference_aggregate_loc, reference_aggregate_pop


def _sr(parent: str, subs: dict[str, float]) -> ScoreResult:
    total = sum(subs.values()) if subs else None
    return ScoreResult(parent_code=parent, sub_code_points=dict(subs), parent_total=total)


def _nd(parent: str) -> ScoreResult:
    return ScoreResult(parent_code=parent)


def test_pop_pass_through() -> None:
    r = reference_aggregate_pop([_sr("POP", {"POP_FRQ": -3.0, "POP_HMZ": -0.5})])
    assert r.parent_code == "POP"
    assert r.parent_total == -3.5
    assert r.sub_code_points == {"POP_FRQ": -3.0, "POP_HMZ": -0.5}
    assert r.held_combined == {}


def test_pop_single_code_zero_is_scored() -> None:
    r = reference_aggregate_pop([_sr("POP", {"POP_FRQ": 0.0})])
    assert r.parent_total == 0.0


def test_pop_recorded_hmz_zero_stays_scored() -> None:
    r = reference_aggregate_pop([_sr("POP", {"POP_HMZ": 0.0})])
    assert r.parent_total == 0.0
    assert r.sub_code_points == {"POP_HMZ": 0.0}


def test_loc_pass_through_cap_not_binding() -> None:
    r = reference_aggregate_loc([_sr("LOC", {"LOC_PHE": 4.0})])
    assert r.parent_total == 4.0
    assert r.held_combined == {}


def test_loc_cap_binds_with_synthetic_seg() -> None:
    r = reference_aggregate_loc([_sr("LOC", {"LOC_PHE": 4.0}), _sr("LOC", {"LOC_SEG": 3.0})])
    assert r.parent_total == 4.0
    assert r.sub_code_points == {"LOC_PHE": 4.0, "LOC_SEG": 3.0}
    assert r.held_combined == {"raw_sum": 7.0}
    assert any("capped" in p for p in r.provenance)


def test_nd_propagation() -> None:
    empty = reference_aggregate_loc([])
    assert empty.parent_total is None
    assert empty.sub_code_points == {}
    single_nd = reference_aggregate_pop([_nd("POP")])
    assert single_nd.parent_total is None
    assert single_nd.sub_code_points == {}


def test_nd_plus_scored_mix() -> None:
    r = reference_aggregate_loc([_nd("LOC"), _sr("LOC", {"LOC_PHE": 2.0})])
    assert r.parent_total == 2.0


def test_duplicate_sub_code_raises() -> None:
    with pytest.raises(ValueError, match="duplicate sub-code"):
        reference_aggregate_loc([_sr("LOC", {"LOC_PHE": 2.0}), _sr("LOC", {"LOC_PHE": 2.0})])


def test_input_invariant_guard_raises() -> None:
    bad = ScoreResult(parent_code="POP", sub_code_points={"POP_FRQ": -3.0}, parent_total=-1.0)
    with pytest.raises(ValueError, match="parent_total"):
        reference_aggregate_pop([bad])
