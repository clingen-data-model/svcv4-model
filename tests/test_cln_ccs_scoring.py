"""Tests for reference_score_cln_ccs (SM 4 case-control, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case_control import CaseControlStudyEvidence
from svcv4_model.scoring import reference_score_cln_ccs


def _cc(**kw: object) -> CaseControlStudyEvidence:
    # a robust study by default; override per test
    base: dict[str, object] = {
        "odds_ratio": 6.0,
        "case_variant_count": 5,
        "case_cohort_size": 100,
        "controls_matched": True,
    }
    base.update(kw)
    return CaseControlStudyEvidence(**base)


def _ccs(ev: CaseControlStudyEvidence) -> float | None:
    return reference_score_cln_ccs(ev).sub_code_points.get("CLN_CCS")


def test_robust_or_gt5_ci_excludes_one() -> None:
    r = reference_score_cln_ccs(_cc(odds_ratio=6.0, ci_lower=2.0, ci_upper=9.0))
    assert r.parent_code == "CLN"
    assert r.sub_code_points["CLN_CCS"] == 4.0
    assert r.parent_total == 4.0


def test_ci_includes_one_vetoes() -> None:
    assert _ccs(_cc(odds_ratio=5.5, ci_lower=0.9, ci_upper=7.4)) == 0.0


def test_none_ci_does_not_veto() -> None:
    assert _ccs(_cc(odds_ratio=6.0)) == 4.0  # ci_lower/upper None


def test_or_between_one_and_five_is_zero() -> None:
    assert _ccs(_cc(odds_ratio=3.0)) == 0.0


def test_or_le_one_is_zero_benign_flagged() -> None:
    r = reference_score_cln_ccs(_cc(odds_ratio=0.5))
    assert r.sub_code_points["CLN_CCS"] == 0.0
    assert any("benign" in p.lower() for p in r.provenance)


def test_gate_fails_are_nd() -> None:
    assert _ccs(_cc(case_variant_count=4)) is None
    assert _ccs(_cc(case_cohort_size=50)) is None
    assert _ccs(_cc(controls_matched=False)) is None
    assert _ccs(_cc(controls_matched=None)) is None


def test_odds_ratio_none_is_nd() -> None:
    r = reference_score_cln_ccs(_cc(odds_ratio=None))
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_exclusivity_note_in_provenance() -> None:
    r = reference_score_cln_ccs(_cc(odds_ratio=6.0, ci_lower=2.0, ci_upper=9.0))
    assert any("CLN_DNV" in p for p in r.provenance)
