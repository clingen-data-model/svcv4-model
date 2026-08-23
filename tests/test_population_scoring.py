"""Tests for reference_score_population (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import MOI, TriState
from svcv4_model.population import PopulationEvidence
from svcv4_model.scoring import reference_score_population

_DAFT = 0.000118  # FBN1-Marfan golden fixture (SM 3 L28)


def _frq(faf: float | None, daft: float | None = _DAFT) -> PopulationEvidence:
    return PopulationEvidence(faf=faf, daft=daft)


def test_pop_frq_fbn1_golden_bands() -> None:
    # SM 3 L28 worked example: DAFT 0.000118
    for faf, expected in [
        (0.000100, 0.0),  # < 0.000177 (< 1.5x)
        (0.000300, -1.0),  # 0.000177 .. 0.000590
        (0.001000, -3.0),  # 0.000590 .. 0.001770
        (0.001770, -6.0),  # = 15x, inclusive
        (0.002000, -6.0),  # > 15x
    ]:
        r = reference_score_population(_frq(faf), moi=MOI.AD)
        assert r.parent_code == "POP"
        assert r.sub_code_points["POP_FRQ"] == expected


def test_pop_frq_boundary_assumption_inclusive_lower() -> None:
    # exactly 1.5x and 5x -> the more-benign band (flagged assumption)
    assert reference_score_population(_frq(0.000177), moi=MOI.AD).sub_code_points["POP_FRQ"] == -1.0
    assert reference_score_population(_frq(0.000590), moi=MOI.AD).sub_code_points["POP_FRQ"] == -3.0


def test_pop_frq_nd() -> None:
    for ev in [_frq(None), _frq(0.001, daft=None), _frq(0.001, daft=0.0)]:
        r = reference_score_population(ev, moi=MOI.AD)
        assert "POP_FRQ" not in r.sub_code_points


def test_pop_hmz_ar_minus_half_per_occurrence() -> None:
    ev = PopulationEvidence(homozygote_count=3, hmz_eligible=TriState.TRUE)
    r = reference_score_population(ev, moi=MOI.AR)
    assert r.sub_code_points["POP_HMZ"] == -1.0  # -0.5 x (3 - 1)
    assert "POP_FRQ" not in r.sub_code_points
    assert r.parent_total == -1.0  # single recorded code -> parent_total is that code


def test_pop_hmz_ad_minus_one_per_occurrence() -> None:
    # SM 3 Table 7: AD homozygous is -1.0/observation (NOT the prose -0.5)
    ev = PopulationEvidence(homozygote_count=3, hmz_eligible=TriState.TRUE)
    r = reference_score_population(ev, moi=MOI.AD)
    assert r.sub_code_points["POP_HMZ"] == -2.0  # -1.0 x (3 - 1)


def test_pop_hmz_xlinked_counts_hemizygotes() -> None:
    ev = PopulationEvidence(homozygote_count=1, hemizygote_count=2, hmz_eligible=TriState.TRUE)
    r = reference_score_population(ev, moi=MOI.XLR)
    assert r.sub_code_points["POP_HMZ"] == -1.0  # count 3 -> -0.5 x 2


def test_pop_hmz_hemizygotes_ignored_off_xlinked() -> None:
    ev = PopulationEvidence(homozygote_count=1, hemizygote_count=5, hmz_eligible=TriState.TRUE)
    r = reference_score_population(ev, moi=MOI.AD)
    assert r.sub_code_points["POP_HMZ"] == 0.0  # count 1 (hemi ignored) -> 1 free


def test_pop_hmz_nd_when_ineligible_or_no_counts() -> None:
    ineligible = PopulationEvidence(homozygote_count=3, hmz_eligible=TriState.FALSE)
    no_counts = PopulationEvidence(hmz_eligible=TriState.TRUE)
    assert "POP_HMZ" not in reference_score_population(ineligible, moi=MOI.AR).sub_code_points
    assert "POP_HMZ" not in reference_score_population(no_counts, moi=MOI.AR).sub_code_points


def test_parent_total_sums_recorded_codes() -> None:
    ev = PopulationEvidence(
        faf=0.002000, daft=_DAFT, homozygote_count=3, hmz_eligible=TriState.TRUE
    )
    r = reference_score_population(ev, moi=MOI.AR)
    assert r.sub_code_points["POP_FRQ"] == -6.0
    assert r.sub_code_points["POP_HMZ"] == -1.0
    assert r.parent_total == -7.0


def test_empty_is_all_nd() -> None:
    r = reference_score_population(PopulationEvidence(), moi=MOI.AD)
    assert r.parent_code == "POP"
    assert r.sub_code_points == {}
    assert r.parent_total is None
