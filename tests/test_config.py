"""Tests for the ruleset configuration model (svcv4_model.config)."""

from __future__ import annotations

import pytest

from svcv4_model.assessment import RULESETS
from svcv4_model.config import (
    EXON_REL_LOF_V4,
    MIS_PRD_EXON_REL_V4,
    MIS_PRD_INIT_INSILICO_V4,
    ExonRelevanceConfig,
    InsilicoPredictorConfig,
    MechanismBand,
    MechanismClassification,
    MissingInput,
    ScoreBand,
    ScoreOutOfRange,
    UnknownMechanism,
    UnknownTier,
    UnknownTool,
    exon_relevance_config,
    insilico_config,
    ladder,
    mechanism_band,
)

BASELINE_ID = "svc:MIS_PRD_INIT_INSILICO:4.0"
MYH7_ID = "svc-gene-MYH7:MIS_PRD_INIT_INSILICO:4.0"


class TestScoreBand:
    def test_interval_notation(self):
        # default is half-open [min, max)
        assert ScoreBand(points=-3, max=0.070).interval == "[-inf, 0.07)"
        assert ScoreBand(points=4, min=0.990).interval == "[0.99, +inf)"
        assert ScoreBand(points=0, min=0.1, max=0.2, max_incl=True).interval == "[0.1, 0.2]"

    def test_contains_half_open_default(self):
        b = ScoreBand(points=0, min=0.170, max=0.791)  # [0.170, 0.791)
        assert b.contains(0.170) and b.contains(0.5)
        assert not b.contains(0.791)  # upper exclusive
        assert not b.contains(0.169)

    def test_contains_exclusive(self):
        b = ScoreBand(points=0, min=0.1, max=0.2, min_incl=False, max_incl=False)
        assert not b.contains(0.1) and not b.contains(0.2)
        assert b.contains(0.15)

    def test_unbounded(self):
        assert ScoreBand(points=-3, max=0.07).contains(-999)
        assert ScoreBand(points=4, min=0.99).contains(999)


class TestLadder:
    def test_builds_contiguous_covering_bands(self):
        bands = ladder((-1, None), (0, 0.5), (1, 0.9))
        assert [b.interval for b in bands] == ["[-inf, 0.5)", "[0.5, 0.9)", "[0.9, +inf)"]
        # a cut value belongs to the higher band
        assert [b.contains(0.5) for b in bands] == [False, True, False]


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

    def test_every_tool_covers_the_real_line(self):
        cfg = MIS_PRD_INIT_INSILICO_V4
        for tool in cfg.per_tool_bands:
            lo, hi = cfg.domain(tool)
            assert lo is None and hi is None, f"{tool} should span -inf..+inf"
            # +4 is reachable for every tool
            assert 4.0 in {b.points for b in cfg.per_tool_bands[tool]}

    def test_bands_are_contiguous(self):
        # constructing already validated coverage; assert no gaps explicitly too
        for tool, bands in MIS_PRD_INIT_INSILICO_V4.per_tool_bands.items():
            ordered = sorted(bands, key=lambda b: float("-inf") if b.min is None else b.min)
            for lower, upper in zip(ordered, ordered[1:], strict=False):
                assert lower.max == upper.min, f"{tool} gap/overlap"
                assert lower.max_incl != upper.min_incl, f"{tool} boundary not clean"

    def test_round_trips_through_params(self):
        dumped = MIS_PRD_INIT_INSILICO_V4.model_dump(exclude_none=True)
        assert insilico_config(dumped) == MIS_PRD_INIT_INSILICO_V4


class TestInsilicoApi:
    def test_tools_returns_selectable_menu(self):
        tools = MIS_PRD_INIT_INSILICO_V4.tools()
        assert "REVEL" in tools and "OTHER_CALIBRATED" in tools
        assert tools == MIS_PRD_INIT_INSILICO_V4.selectable_tools
        assert tools is not MIS_PRD_INIT_INSILICO_V4.selectable_tools  # a copy

    def test_evaluate_returns_points(self):
        assert MIS_PRD_INIT_INSILICO_V4.evaluate("REVEL", 0.86) == 2.0

    def test_unknown_tool_raises(self):
        with pytest.raises(UnknownTool, match="unknown tool"):
            MIS_PRD_INIT_INSILICO_V4.evaluate("SIFT", 0.5)

    def test_tool_without_bands_raises(self):
        # OTHER_CALIBRATED is selectable but has no baseline bands
        with pytest.raises(UnknownTool, match="no configured bands"):
            MIS_PRD_INIT_INSILICO_V4.evaluate("OTHER_CALIBRATED", 0.5)

    def test_score_out_of_range_raises(self):
        # a bounded tool: only covers [0.0, 1.0)
        cfg = InsilicoPredictorConfig(
            selectable_tools=["Bounded"],
            per_tool_bands={
                "Bounded": [
                    ScoreBand(points=0.0, min=0.0, max=0.5),
                    ScoreBand(points=1.0, min=0.5, max=1.0),
                ]
            },
        )
        assert cfg.evaluate("Bounded", 0.25) == 0.0
        assert cfg.domain("Bounded") == (0.0, 1.0)
        with pytest.raises(ScoreOutOfRange, match="outside covered domain"):
            cfg.evaluate("Bounded", 1.5)
        with pytest.raises(ScoreOutOfRange):
            cfg.evaluate("Bounded", -0.1)

    def test_coverage_validator_rejects_gap(self):
        with pytest.raises(ValueError, match="not contiguous"):
            InsilicoPredictorConfig(
                selectable_tools=["Gappy"],
                per_tool_bands={
                    "Gappy": [
                        ScoreBand(points=0.0, min=None, max=0.4),
                        ScoreBand(points=1.0, min=0.5, max=None),  # gap 0.4–0.5
                    ]
                },
            )

    def test_coverage_validator_rejects_overlap(self):
        with pytest.raises(ValueError, match="not contiguous|double-covers"):
            InsilicoPredictorConfig(
                selectable_tools=["Over"],
                per_tool_bands={
                    "Over": [
                        ScoreBand(points=0.0, min=None, max=0.6),
                        ScoreBand(points=1.0, min=0.4, max=None),  # overlap 0.4–0.6
                    ]
                },
            )


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


EXON_REL_IDS = [
    "svc:MIS_PRD_EXON_REL:4.0",
    "svc:NUL_PRD_EXON_REL:4.0",
    "svc:CDS_PRD_EXON_REL:4.0",
    "svc:SPL_PRD_EXON_REL:4.0",
]


class TestExonRelevanceConfig:
    def test_baseline_matrix(self):
        cfg = MIS_PRD_EXON_REL_V4
        assert [(t.tier, t.multiplier) for t in cfg.tier_multipliers] == [
            ("All", 1.0),
            ("Most", 0.5),
            ("Few", 0.0),
        ]
        assert cfg.tiers() == ["All", "Most", "Few"]
        assert cfg.has_mechanism is False

    @pytest.mark.parametrize(
        ("tier", "expected"),
        [("All", 1.0), ("Most", 0.5), ("Few", 0.0), ("all", 1.0), ("FEW", 0.0)],
    )
    def test_multiplier_for(self, tier, expected):
        assert MIS_PRD_EXON_REL_V4.multiplier_for(tier) == expected

    def test_unknown_tier_raises(self):
        with pytest.raises(UnknownTier, match="unknown relevance tier"):
            MIS_PRD_EXON_REL_V4.multiplier_for("Some")

    def test_round_trips_through_params(self):
        dumped = MIS_PRD_EXON_REL_V4.model_dump()
        assert exon_relevance_config(dumped) == MIS_PRD_EXON_REL_V4

    def test_all_exon_rel_rulesets_carry_the_matrix(self):
        for rid in EXON_REL_IDS:
            cfg = exon_relevance_config(RULESETS[rid].params)
            assert cfg.multiplier_for("All") == 1.0
            assert cfg.multiplier_for("Few") == 0.0

    def test_mechanism_by_family(self):
        # missense has no mechanism; null / in-frame / splice configure "LOF"
        mis = exon_relevance_config(RULESETS["svc:MIS_PRD_EXON_REL:4.0"].params)
        assert mis.has_mechanism is False
        for rid in EXON_REL_IDS[1:]:
            cfg = exon_relevance_config(RULESETS[rid].params)
            assert cfg.has_mechanism is True
            assert [b.mechanism_type for b in cfg.mechanism_bands] == ["LOF"]

    def test_specialisation_can_reweight_tiers(self):
        spec = ExonRelevanceConfig.model_validate(
            {
                "tier_multipliers": [
                    {"tier": "All", "multiplier": 1.0},
                    {"tier": "Most", "multiplier": 0.75},  # re-weighted
                    {"tier": "Few", "multiplier": 0.0},
                ],
            }
        )
        assert spec.multiplier_for("Most") == 0.75
        assert MIS_PRD_EXON_REL_V4.multiplier_for("Most") == 0.5

    def test_weight_must_be_0_to_1(self):
        with pytest.raises(ValueError):
            MechanismClassification(classification="X", weight=1.5)

    def test_introspection_lists(self):
        # each subcode reports valid tiers, mech types, and classes per type
        assert MIS_PRD_EXON_REL_V4.tiers() == ["All", "Most", "Few"]
        assert MIS_PRD_EXON_REL_V4.mechanism_types() == []
        assert EXON_REL_LOF_V4.mechanism_types() == ["LOF"]
        assert EXON_REL_LOF_V4.classifications("LOF") == [
            "Established",
            "Likely",
            "Suspected",
            "Uncertain or Not LOF",
        ]
        assert EXON_REL_LOF_V4.classifications("lof") == EXON_REL_LOF_V4.classifications("LOF")

    def test_classifications_unknown_type_raises(self):
        with pytest.raises(UnknownMechanism, match="mechanism type"):
            EXON_REL_LOF_V4.classifications("GOF")

    def test_subcode_introspection_from_registry(self):
        for rid in EXON_REL_IDS[1:]:  # NUL / CDS / SPL
            cfg = exon_relevance_config(RULESETS[rid].params)
            assert cfg.mechanism_types() == ["LOF"]
            assert "Established" in cfg.classifications("LOF")


class TestReusableMechanismBand:
    def test_builder_makes_a_band(self):
        band = mechanism_band("LOF", ("Established", 1.0), ("Uncertain", 0.0))
        assert band.mechanism_type == "LOF"
        assert band.weight_for("Established") == 1.0
        assert band.weight_for("Uncertain") == 0.0

    def test_one_band_shared_across_configs(self):
        # define once, pass into several exon-relevance configs
        lof = mechanism_band("LOF", ("Established", 1.0), ("Suspected", 0.25))
        nul = ExonRelevanceConfig(
            tier_multipliers=MIS_PRD_EXON_REL_V4.tier_multipliers, mechanism_bands=[lof]
        )
        cds = ExonRelevanceConfig(
            tier_multipliers=MIS_PRD_EXON_REL_V4.tier_multipliers, mechanism_bands=[lof]
        )
        assert nul.evaluate(2.0, "All", "LOF", "Suspected") == 0.25
        assert cds.evaluate(2.0, "All", "LOF", "Suspected") == 0.25

    def test_a_family_may_pass_a_different_band(self):
        strict = mechanism_band("LOF", ("Established", 1.0), ("Suspected", 0.0))
        cfg = ExonRelevanceConfig(
            tier_multipliers=MIS_PRD_EXON_REL_V4.tier_multipliers, mechanism_bands=[strict]
        )
        # same type, re-weighted for this variant-impact family
        assert cfg.evaluate(2.0, "All", "LOF", "Suspected") == 0.0


class TestExonRelevanceApi:
    """evaluate(initial_points, tier, mechanism_type, mechanism_class)."""

    def test_no_mechanism_returns_tier_fraction(self):
        cfg = MIS_PRD_EXON_REL_V4  # only_positive True, no mechanism
        assert cfg.evaluate(2.0, "All") == 1.0
        assert cfg.evaluate(2.0, "Most") == 0.5
        assert cfg.evaluate(2.0, "Few") == 0.0

    def test_only_positive_shortcircuits_nonpositive(self):
        cfg = MIS_PRD_EXON_REL_V4  # only_positive True
        # non-positive initial points → 1.0 regardless of tier (tier optional)
        assert cfg.evaluate(0.0) == 1.0
        assert cfg.evaluate(-3.0) == 1.0
        assert cfg.evaluate(-3.0, "Few") == 1.0  # would be 0.0 if applied

    def test_only_positive_false_applies_to_all(self):
        cfg = ExonRelevanceConfig(
            tier_multipliers=MIS_PRD_EXON_REL_V4.tier_multipliers, only_positive=False
        )
        assert cfg.evaluate(-3.0, "Few") == 0.0  # applied even though non-positive

    def test_tier_required_when_computing(self):
        cfg = ExonRelevanceConfig(
            tier_multipliers=MIS_PRD_EXON_REL_V4.tier_multipliers, only_positive=False
        )
        with pytest.raises(MissingInput, match="tier is required"):
            cfg.evaluate(2.0)

    def test_mechanism_multiplies_tier_and_weight(self):
        cfg = EXON_REL_LOF_V4  # LOF: Established=1.0, Likely=0.5, Suspected=0.25, Uncertain=0.0
        # tier Most (0.5) × LOF Established (1.0) = 0.5
        assert cfg.evaluate(2.0, "Most", "LOF", "Established") == 0.5
        # tier All (1.0) × LOF Suspected (0.25) = 0.25
        assert cfg.evaluate(2.0, "All", "LOF", "Suspected") == 0.25
        # tier All (1.0) × LOF "Uncertain or Not LOF" (0.0) = 0.0
        assert cfg.evaluate(2.0, "All", "LOF", "Uncertain or Not LOF") == 0.0

    def test_mechanism_required_when_configured(self):
        with pytest.raises(MissingInput, match="mechanism"):
            EXON_REL_LOF_V4.evaluate(2.0, "All")

    def test_unknown_mechanism_type_and_class(self):
        with pytest.raises(UnknownMechanism, match="mechanism type"):
            EXON_REL_LOF_V4.evaluate(2.0, "All", "GOF", "Established")
        with pytest.raises(UnknownMechanism, match="classification"):
            EXON_REL_LOF_V4.evaluate(2.0, "All", "LOF", "Maybe")

    def test_only_positive_still_wins_with_mechanism(self):
        # non-positive short-circuits before mechanism args are needed
        assert EXON_REL_LOF_V4.evaluate(-1.0) == 1.0

    def test_multiple_mechanism_types(self):
        cfg = ExonRelevanceConfig(
            tier_multipliers=MIS_PRD_EXON_REL_V4.tier_multipliers,
            mechanism_bands=[
                MechanismBand(
                    mechanism_type="LOF",
                    classifications=[MechanismClassification(classification="Yes", weight=1.0)],
                ),
                MechanismBand(
                    mechanism_type="GOF",
                    classifications=[MechanismClassification(classification="Yes", weight=0.25)],
                ),
            ],
        )
        assert cfg.evaluate(2.0, "All", "LOF", "Yes") == 1.0
        assert cfg.evaluate(2.0, "All", "GOF", "Yes") == 0.25


class TestInformativeVariantsConfig:
    """MIS_INF five-group model (SM 19): count × points + a definitive bonus."""

    def _v(self, cls, aa=None, grantham=None, star=3, vid=None):
        from svcv4_model.informative import InformativeVariant

        return InformativeVariant(
            id=vid, classification=cls, aa=aa, grantham=grantham, star_rating=star
        )

    def test_mis_groups(self):
        from svcv4_model.config import MIS_INF_V4

        assert MIS_INF_V4.group_names() == [
            "a_clin_sig_same_aa",
            "b_clin_sig_distinct_aa_nonneg_grantham",
            "c_not_sig_distinct_aa_pos_grantham",
            "d_not_sig_same_aa",
            "e_other",
        ]
        assert MIS_INF_V4.min_star_rating == 3

    def test_no_variants_is_nd(self):
        from svcv4_model.config import MIS_INF_V4

        assert MIS_INF_V4.evaluate([]) is None  # MIS_INF_ND
        # all below the star minimum → none qualify → ND
        from svcv4_model.informative import AminoAcidRelation as AA
        from svcv4_model.informative import VariantClassification as C

        assert MIS_INF_V4.evaluate([self._v(C.PATHOGENIC, AA.SAME, star=2)]) is None

    def test_group_scoring(self):
        from svcv4_model.config import MIS_INF_V4
        from svcv4_model.informative import AminoAcidRelation as AA
        from svcv4_model.informative import VariantClassification as C

        e = MIS_INF_V4.evaluate
        # a) same-AA: Path → +2 + def +2 = +4 ; LP → +2 (no bonus)
        assert e([self._v(C.PATHOGENIC, AA.SAME)]) == 4.0
        assert e([self._v(C.LIKELY_PATHOGENIC, AA.SAME)]) == 2.0
        # b) distinct-AA P, VBC−INF ≥ 0 → +1 + def +1 = +2  (TP53 comparator)
        tp53 = self._v(C.PATHOGENIC, AA.DISTINCT, grantham=29, vid="p.His214Arg")
        assert (
            MIS_INF_V4.classify(tp53, vbc_grantham=99) == "b_clin_sig_distinct_aa_nonneg_grantham"
        )
        assert e([tp53], vbc_grantham=99) == 2.0
        # d) same-AA Benign → −2 + def −2 = −4
        assert e([self._v(C.BENIGN, AA.SAME)]) == -4.0
        # e) VUS → group e → 0.0 (a value, not ND)
        assert e([self._v(C.VUS, AA.SAME)]) == 0.0

    def test_count_times_points_plus_one_bonus(self):
        from svcv4_model.config import MIS_INF_V4
        from svcv4_model.informative import AminoAcidRelation as AA
        from svcv4_model.informative import VariantClassification as C

        # two same-AA clin-sig: 1 Path + 1 LP → 2×+2 + one definitive bonus +2 = +6
        vs = [
            self._v(C.PATHOGENIC, AA.SAME, vid="x1"),
            self._v(C.LIKELY_PATHOGENIC, AA.SAME, vid="x2"),
        ]
        assert MIS_INF_V4.evaluate(vs) == 6.0
        # two same-AA LP (no Path) → 2×+2 + no bonus = +4
        vs2 = [
            self._v(C.LIKELY_PATHOGENIC, AA.SAME, vid="y1"),
            self._v(C.LIKELY_PATHOGENIC, AA.SAME, vid="y2"),
        ]
        assert MIS_INF_V4.evaluate(vs2) == 4.0

    def test_distinct_aa_grantham_boundaries(self):
        from svcv4_model.config import MIS_INF_V4
        from svcv4_model.informative import AminoAcidRelation as AA
        from svcv4_model.informative import VariantClassification as C

        # clin-sig distinct-AA needs VBC−INF ≥ 0; INF Grantham > VBC → falls to catch-all e → 0
        v = self._v(C.PATHOGENIC, AA.DISTINCT, grantham=120, vid="hi")
        assert MIS_INF_V4.classify(v, vbc_grantham=99) == "e_other"
        assert MIS_INF_V4.evaluate([v], vbc_grantham=99) == 0.0
        # not-sig distinct-AA needs VBC−INF > 0 (strictly); diff 0 → e
        eq = self._v(C.BENIGN, AA.DISTINCT, grantham=99, vid="eq")
        assert MIS_INF_V4.classify(eq, vbc_grantham=99) == "e_other"
        lt = self._v(C.BENIGN, AA.DISTINCT, grantham=40, vid="lt")
        assert MIS_INF_V4.classify(lt, vbc_grantham=99) == "c_not_sig_distinct_aa_pos_grantham"
        # group c: 1 × −1 + definitive(Benign) bonus −1 = −2
        assert MIS_INF_V4.evaluate([lt], vbc_grantham=99) == -2.0

    def test_dedup_keeps_highest_star(self):
        from svcv4_model.config import MIS_INF_V4
        from svcv4_model.informative import AminoAcidRelation as AA
        from svcv4_model.informative import VariantClassification as C

        # same id, two classifications: keep the higher-star one (Path @4 over LP @3)
        dup = [
            self._v(C.LIKELY_PATHOGENIC, AA.SAME, star=3, vid="same"),
            self._v(C.PATHOGENIC, AA.SAME, star=4, vid="same"),
        ]
        # one variant, same-AA Path → +2 + def +2 = +4 (not counted twice)
        assert MIS_INF_V4.evaluate(dup) == 4.0

    def test_cap(self):
        from svcv4_model.config import MIS_INF_V4
        from svcv4_model.informative import AminoAcidRelation as AA
        from svcv4_model.informative import VariantClassification as C

        many = [self._v(C.PATHOGENIC, AA.SAME, vid=f"v{i}") for i in range(10)]
        assert MIS_INF_V4.evaluate(many) == 8.0  # 10×2 + 2 → cap +8

    def test_generic_families_and_registry(self):
        from svcv4_model.assessment import RULESETS
        from svcv4_model.config import informative_config

        for code in ("NUL_INF", "CDS_INF", "SPL_INF"):
            cfg = informative_config(RULESETS[f"svc:{code}:4.0"].params)
            assert cfg.group_names() == [
                "clinically_significant",
                "not_clinically_significant",
                "other",
            ]
        assert "svc:SPL_INF:4.0" in RULESETS
        mis = informative_config(RULESETS["svc:MIS_INF:4.0"].params)
        assert "a_clin_sig_same_aa" in mis.group_names()

    def test_specialisation_can_reweight_a_group(self):
        from svcv4_model.config import InfGroup, InformativeVariantsConfig
        from svcv4_model.informative import AminoAcidRelation as AA
        from svcv4_model.informative import VariantClassification as C

        spec = InformativeVariantsConfig(
            groups=[
                InfGroup(
                    name="a_clin_sig_same_aa",
                    clinical="significant",
                    aa="same",
                    points_per_variant=3.0,
                    definitive_bonus=3.0,
                    definitive_classification=C.PATHOGENIC,
                ),
                InfGroup(name="e_other"),
            ]
        )
        assert spec.evaluate([self._v(C.PATHOGENIC, AA.SAME)]) == 6.0

    def test_motif_variant_award(self):
        from svcv4_model.config import MIS_INF_V4
        from svcv4_model.informative import AminoAcidRelation as AA
        from svcv4_model.informative import VariantClassification as C

        # COL3A1-style: VBC in a robust motif, no informative variants → +2 once (not ND)
        assert MIS_INF_V4.evaluate([], motif_qualifying=True) == 2.0
        assert MIS_INF_V4.evaluate([]) is None  # no motif → ND
        # suppressed by a benign informative variant at the codon
        assert MIS_INF_V4.evaluate([self._v(C.BENIGN, AA.SAME)], motif_qualifying=True) == -4.0
        # not added when a P/LP informative variant already exists
        assert MIS_INF_V4.evaluate([self._v(C.PATHOGENIC, AA.SAME)], motif_qualifying=True) == 4.0
        # VUS does not block the motif award
        assert MIS_INF_V4.evaluate([self._v(C.VUS, AA.SAME)], motif_qualifying=True) == 2.0
        # awarded only once
        assert MIS_INF_V4.evaluate([], motif_qualifying=True) == 2.0

    def test_generic_families_have_no_motif_points(self):
        from svcv4_model.config import CDS_INF_V4, NUL_INF_V4, SPL_INF_V4

        for cfg in (NUL_INF_V4, CDS_INF_V4, SPL_INF_V4):
            assert cfg.motif_points == 0.0
            assert cfg.evaluate([], motif_qualifying=True) is None
