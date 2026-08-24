"""Tests for reference_finalize_cln (CLN_CCS exclusivity + POP_FRQ gate, Inc 3c)."""

from __future__ import annotations

from svcv4_model.scoring import ScoreResult, reference_finalize_cln


def _sr(subs: dict[str, float]) -> ScoreResult:
    total = sum(subs.values()) if subs else None
    return ScoreResult(parent_code="CLN", sub_code_points=dict(subs), parent_total=total)


def test_no_ccs_rare_unchanged() -> None:
    r = reference_finalize_cln(
        _sr({"CLN_AFF": 1.0, "CLN_DNV": 7.0, "CLN_UAF": -4.0}), None, pop_frq_points=0.0
    )
    assert r.sub_code_points == {"CLN_AFF": 1.0, "CLN_DNV": 7.0, "CLN_UAF": -4.0}
    assert r.parent_total == 4.0


def test_no_ccs_not_rare_gates_aff_dnv() -> None:
    r = reference_finalize_cln(
        _sr({"CLN_AFF": 1.0, "CLN_DNV": 7.0, "CLN_UAF": -4.0}), None, pop_frq_points=-0.5
    )
    assert r.sub_code_points == {"CLN_UAF": -4.0}
    assert r.parent_total == -4.0


def test_pop_none_gates() -> None:
    r = reference_finalize_cln(_sr({"CLN_AFF": 1.0, "CLN_DNV": 7.0}), None, pop_frq_points=None)
    assert "CLN_AFF" not in r.sub_code_points
    assert "CLN_DNV" not in r.sub_code_points


def test_ccs_rare_keeps_ccs_and_dnv() -> None:
    r = reference_finalize_cln(
        _sr({"CLN_AFF": 1.0, "CLN_DNV": 7.0, "CLN_ALT": -0.5}),
        _sr({"CLN_CCS": 4.0}),
        pop_frq_points=-1.0,
    )
    assert r.sub_code_points == {"CLN_CCS": 4.0, "CLN_DNV": 7.0}
    assert r.parent_total == 11.0


def test_ccs_not_rare_only_ccs() -> None:
    r = reference_finalize_cln(
        _sr({"CLN_AFF": 1.0, "CLN_DNV": 7.0}),
        _sr({"CLN_CCS": 4.0}),
        pop_frq_points=None,
    )
    assert r.sub_code_points == {"CLN_CCS": 4.0}


def test_ccs_zero_still_fires_exclusivity() -> None:
    r = reference_finalize_cln(
        _sr({"CLN_AFF": 1.0, "CLN_DNV": 7.0, "CLN_UAF": -4.0}),
        _sr({"CLN_CCS": 0.0}),
        pop_frq_points=0.0,
    )
    assert r.sub_code_points == {"CLN_CCS": 0.0, "CLN_DNV": 7.0}


def test_all_na_is_nd() -> None:
    r = reference_finalize_cln(_sr({"CLN_AFF": 1.0, "CLN_DNV": 7.0}), None, pop_frq_points=None)
    assert r.parent_total is None
    assert r.sub_code_points == {}


def test_nd_subtotal_plus_ccs() -> None:
    r = reference_finalize_cln(
        ScoreResult(parent_code="CLN"), _sr({"CLN_CCS": 4.0}), pop_frq_points=-1.0
    )
    assert r.sub_code_points == {"CLN_CCS": 4.0}


def test_ccs_nd_does_not_fire() -> None:
    r = reference_finalize_cln(
        _sr({"CLN_AFF": 1.0}), ScoreResult(parent_code="CLN"), pop_frq_points=0.0
    )
    assert r.sub_code_points == {"CLN_AFF": 1.0}
