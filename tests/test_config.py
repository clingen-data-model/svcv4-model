"""Tests for the ruleset configuration model (svcv4_model.config)."""

from __future__ import annotations

import pytest

from svcv4_model.assessment import RULESETS
from svcv4_model.config import (
    MIS_PRD_INIT_INSILICO_V4,
    InsilicoPredictorConfig,
    ScoreBand,
    insilico_config,
)

BASELINE_ID = "svc:MIS_PRD_INIT_INSILICO:4.0"
MYH7_ID = "svc-gene-MYH7:MIS_PRD_INIT_INSILICO:4.0"


class TestScoreBand:
    def test_interval_notation(self):
        assert ScoreBand(points=-3, max=0.070).interval == "[-inf, 0.07]"
        assert ScoreBand(points=4, min=0.990).interval == "[0.99, +inf]"
        assert ScoreBand(points=0, min=0.1, max=0.2, min_incl=False).interval == "(0.1, 0.2]"

    def test_contains_bounds(self):
        b = ScoreBand(points=0, min=0.170, max=0.791)  # both inclusive
        assert b.contains(0.170) and b.contains(0.791) and b.contains(0.5)
        assert not b.contains(0.169) and not b.contains(0.792)

    def test_contains_exclusive(self):
        b = ScoreBand(points=0, min=0.1, max=0.2, min_incl=False, max_incl=False)
        assert not b.contains(0.1) and not b.contains(0.2)
        assert b.contains(0.15)

    def test_unbounded(self):
        assert ScoreBand(points=-3, max=0.07).contains(-999)
        assert ScoreBand(points=4, min=0.99).contains(999)


class TestBaselineConfig:
    def test_tool_counts(self):
        cfg = MIS_PRD_INIT_INSILICO_V4
        # 4 tools reach -3.0 (8 bands), 3 reach -4.0 (9 bands); OTHER_CALIBRATED has none
        assert len(cfg.selectable_tools) == 8
        assert set(cfg.per_tool_bands) == {
            "AlphaMissense",
            "BayesDel",
            "ESM1b",
            "MutPred2",
            "REVEL",
            "VARITY_R",
            "VEST4",
        }
        reach_minus4 = {t for t, bs in cfg.per_tool_bands.items() if bs[0].points == -4.0}
        assert reach_minus4 == {"MutPred2", "REVEL", "VARITY_R"}

    @pytest.mark.parametrize(
        ("tool", "score", "expected"),
        [
            ("REVEL", 0.86, 2.0),  # PATH_MODERATE — NOT +4 (0.773–0.878)
            ("REVEL", 0.95, 4.0),  # REVEL reaches +4 only at >=0.932
            ("REVEL", 0.016, -4.0),
            ("AlphaMissense", 0.86, 1.0),
            ("AlphaMissense", 0.995, 4.0),
            ("AlphaMissense", 0.05, -3.0),
            ("BayesDel", 0.20, 1.0),
            ("BayesDel", -0.6, -3.0),
            ("ESM1b", -15.0, 3.0),  # inverted scale
            ("ESM1b", 9.0, -3.0),
            ("ESM1b", -30.0, 4.0),
            ("MutPred2", 0.005, -4.0),
            ("VEST4", 0.5, 0.0),
            ("VARITY_R", 0.97, 4.0),
        ],
    )
    def test_points_for(self, tool, score, expected):
        assert MIS_PRD_INIT_INSILICO_V4.points_for(tool, score) == expected

    def test_bands_are_ordered_and_monotonic_in_points(self):
        for tool, bands in MIS_PRD_INIT_INSILICO_V4.per_tool_bands.items():
            pts = [b.points for b in bands]
            assert pts == sorted(pts), f"{tool} points not ascending"
            assert pts[-1] == 4.0, f"{tool} must reach +4.0"

    def test_round_trips_through_params(self):
        dumped = MIS_PRD_INIT_INSILICO_V4.model_dump(exclude_none=True)
        assert insilico_config(dumped) == MIS_PRD_INIT_INSILICO_V4


class TestRegistryWiring:
    def test_baseline_ruleset_carries_config(self):
        r = RULESETS[BASELINE_ID]
        cfg = insilico_config(r.params)
        assert cfg == MIS_PRD_INIT_INSILICO_V4
        assert r.description and "SM 6" in r.description

    def test_specialisation_overrides_baseline(self):
        base = insilico_config(RULESETS[BASELINE_ID].params)
        spec = insilico_config(RULESETS[MYH7_ID].params)
        # same code, new namespace, modified configuration
        assert spec.selectable_tools == ["REVEL"]
        assert spec.selected_tool == "REVEL"
        # recalibrated: 0.70 lands in MYH7 band 0.700–0.899 (+2) but baseline 0.644–0.772 (+1)
        assert spec.points_for("REVEL", 0.70) == 2.0
        assert base.points_for("REVEL", 0.70) == 1.0
        assert spec.per_tool_bands["REVEL"] != base.per_tool_bands["REVEL"]


def test_invalid_config_rejects_unknown_field():
    with pytest.raises(ValueError):
        InsilicoPredictorConfig.model_validate({"selectable_tools": ["REVEL"], "bogus": 1})
