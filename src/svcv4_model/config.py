"""Typed **configuration model** behind SVCv4 codes.

A code (e.g. ``svc:MIS_PRD_INIT_INSILICO``) is only a name; the *behaviour* behind
it — the numbers that turn evidence into points — lives in the ruleset's
``params``. This module gives those params a typed shape so the baseline
configuration can be validated, documented, and **modified** by a specialisation
(a scoped ruleset in its own namespace) without changing the code itself.

The first configured family is the in-silico predictor initial-points code. Its
model is a dictionary keyed by predictor tool, each holding an ordered list of
``(points, score-interval)`` bands — a faithful encoding of SM 6, Figure 2.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ScoreBand(BaseModel):
    """One ``(points, score-interval)`` row of a predictor's calibration table.

    The interval is ``min``..``max``; ``None`` means unbounded (−∞ / +∞).
    ``min_incl`` / ``max_incl`` select closed ``[ ]`` vs open ``( )`` at each end.
    Intervals are stored **as printed** in SM 6 Fig 2 (``≤T`` → ``(−∞, T]``;
    ``≥T`` → ``[T, +∞)``; ``L to U`` → ``[L, U]``), so a band may cover a
    predictor whose scale is inverted (ESM1b: higher score ⇒ more benign).
    """

    model_config = ConfigDict(extra="forbid")

    points: float = Field(description="Initial evidence points for scores in this band.")
    min: float | None = Field(default=None, description="Lower bound; None = −∞.")
    max: float | None = Field(default=None, description="Upper bound; None = +∞.")
    min_incl: bool = Field(default=True, description="Lower bound inclusive ([) vs exclusive (().")
    max_incl: bool = Field(default=True, description="Upper bound inclusive (]) vs exclusive ()).")

    def contains(self, score: float) -> bool:
        lo_ok = self.min is None or score > self.min or (score == self.min and self.min_incl)
        hi_ok = self.max is None or score < self.max or (score == self.max and self.max_incl)
        return lo_ok and hi_ok

    @property
    def interval(self) -> str:
        lo = "-inf" if self.min is None else f"{self.min:g}"
        hi = "+inf" if self.max is None else f"{self.max:g}"
        return f"{'[' if self.min_incl else '('}{lo}, {hi}{']' if self.max_incl else ')'}"


class InsilicoPredictorConfig(BaseModel):
    """Configuration behind an ``insilico-predictor-assessment`` code.

    ``per_tool_bands[tool]`` is the ordered calibration table for one approved
    predictor. ``selectable_tools`` is the menu an analyst may choose from;
    ``selected_tool`` records the choice on an instance (``None`` on the baseline
    registry entry). A specialisation overrides a tool's bands, narrows
    ``selectable_tools``, or pins ``selected_tool`` — the code is unchanged.
    """

    model_config = ConfigDict(extra="forbid")

    selectable_tools: list[str]
    per_tool_bands: dict[str, list[ScoreBand]] = Field(default_factory=dict)
    selected_tool: str | None = None

    def points_for(self, tool: str, score: float) -> float:
        """Initial points for ``score`` under ``tool`` (nearest band on a sub-precision gap)."""
        bands = self.per_tool_bands[tool]
        for band in bands:
            if band.contains(score):
                return band.points

        def _distance(band: ScoreBand) -> float:
            lo = band.min if band.min is not None else float("-inf")
            hi = band.max if band.max is not None else float("inf")
            return 0.0 if lo <= score <= hi else min(abs(score - lo), abs(score - hi))

        return min(bands, key=_distance).points


def insilico_config(params: dict) -> InsilicoPredictorConfig:
    """Read a ruleset's ``params`` dict back into the typed config."""
    return InsilicoPredictorConfig.model_validate(params)


class RelevanceTier(BaseModel):
    """One row of the exon-relevance matrix — a tier and the fraction it applies."""

    model_config = ConfigDict(extra="forbid")

    tier: str = Field(description="Relevance tier, e.g. 'All' | 'Most' | 'Few'.")
    multiplier: float = Field(description="Fraction the initial points are scaled by (0.0–1.0).")
    criterion: str | None = Field(default=None, description="What the tier means, in words.")


class ExonRelevanceConfig(BaseModel):
    """Configuration behind an ``exon-relevance-assessment`` code.

    The code outputs a **multiplier** (not points): the initial predictive points
    are scaled by how many clinically-relevant transcripts contain the exon(s)
    harbouring the VBC. ``tier_multipliers`` is that matrix. ``include_mechanism``
    folds the gene-disease molecular-mechanism cross-reference into this node —
    baseline missense leaves it ``False`` (predictors already capture mechanism);
    the null / in-frame / splice families set it ``True``. A specialisation may
    re-weight the tiers or flip the mechanism toggle without changing the code.
    """

    model_config = ConfigDict(extra="forbid")

    tier_multipliers: list[RelevanceTier]
    include_mechanism: bool = False

    def multiplier_for(self, tier: str) -> float:
        """The fraction for ``tier`` (case-insensitive); raises on an unknown tier."""
        for row in self.tier_multipliers:
            if row.tier.casefold() == tier.casefold():
                return row.multiplier
        known = ", ".join(r.tier for r in self.tier_multipliers)
        raise ValueError(f"unknown relevance tier {tier!r}; expected one of: {known}")


def exon_relevance_config(params: dict) -> ExonRelevanceConfig:
    """Read a ruleset's ``params`` dict back into the typed config."""
    return ExonRelevanceConfig.model_validate(params)


def _bands(*rows: tuple[float, float | None, float | None]) -> list[ScoreBand]:
    """``(points, min, max)`` → bands. Both ends inclusive (SM 6 Fig 2 printed form)."""
    return [ScoreBand(points=p, min=lo, max=hi) for p, lo, hi in rows]


# --------------------------------------------------------------------------- #
# Baseline configuration for svc:MIS_PRD_INIT_INSILICO:4.0
#
# Transcribed from SM 6, Figure 2 ("Initial evidence points for missense variants
# based on in-silico prediction"). Four tools reach −3.0, three reach −4.0 for
# benignity; every tool reaches +4.0 for pathogenicity. ESM1b's scale is inverted.
# --------------------------------------------------------------------------- #

MIS_PRD_INIT_INSILICO_V4 = InsilicoPredictorConfig(
    selectable_tools=[
        "AlphaMissense",
        "BayesDel",
        "ESM1b",
        "MutPred2",
        "REVEL",
        "VARITY_R",
        "VEST4",
        "OTHER_CALIBRATED",
    ],
    per_tool_bands={
        # ---- reach −3.0 ----
        "AlphaMissense": _bands(
            (-3, None, 0.070),
            (-2, 0.071, 0.099),
            (-1, 0.100, 0.169),
            (0, 0.170, 0.791),
            (1, 0.792, 0.905),
            (2, 0.906, 0.971),
            (3, 0.972, 0.989),
            (4, 0.990, None),
        ),
        "BayesDel": _bands(
            (-3, None, -0.520),
            (-2, -0.519, -0.360),
            (-1, -0.359, -0.180),
            (0, -0.179, 0.129),
            (1, 0.130, 0.269),
            (2, 0.270, 0.409),
            (3, 0.410, 0.499),
            (4, 0.50, None),
        ),
        # ESM1b: inverted — higher score ⇒ more benign, so intervals descend.
        "ESM1b": _bands(
            (-3, 8.8, None),
            (-2, -3.1, 8.7),
            (-1, -6.3, -3.2),
            (0, -10.6, -6.4),
            (1, -12.1, -10.7),
            (2, -13.9, -12.2),
            (3, -23.9, -14.0),
            (4, None, -24.0),
        ),
        "VEST4": _bands(
            (-3, None, 0.077),
            (-2, 0.078, 0.302),
            (-1, 0.303, 0.449),
            (0, 0.450, 0.763),
            (1, 0.764, 0.860),
            (2, 0.861, 0.908),
            (3, 0.909, 0.964),
            (4, 0.965, None),
        ),
        # ---- reach −4.0 ----
        "MutPred2": _bands(
            (-4, None, 0.010),
            (-3, 0.011, 0.031),
            (-2, 0.032, 0.197),
            (-1, 0.198, 0.391),
            (0, 0.392, 0.736),
            (1, 0.737, 0.828),
            (2, 0.829, 0.894),
            (3, 0.895, 0.931),
            (4, 0.932, None),
        ),
        "REVEL": _bands(
            (-4, None, 0.016),
            (-3, 0.017, 0.052),
            (-2, 0.053, 0.183),
            (-1, 0.184, 0.290),
            (0, 0.291, 0.643),
            (1, 0.644, 0.772),
            (2, 0.773, 0.878),
            (3, 0.879, 0.931),
            (4, 0.932, None),
        ),
        "VARITY_R": _bands(
            (-4, None, 0.036),
            (-3, 0.037, 0.062),
            (-2, 0.063, 0.116),
            (-1, 0.117, 0.251),
            (0, 0.252, 0.674),
            (1, 0.675, 0.841),
            (2, 0.842, 0.914),
            (3, 0.915, 0.965),
            (4, 0.966, None),
        ),
        # OTHER_CALIBRATED carries no baseline bands — a specialisation supplies them.
    },
)


# --------------------------------------------------------------------------- #
# Baseline configuration for the exon-relevance codes (svc:*_PRD_EXON_REL:4.0)
#
# The tier → fraction matrix from SM 6, Figure 2 (right box, "Exon Relevance
# Matrix. Multiply Number From Prior Box by this Fraction."). The exon(s)
# containing the VBC (and affected region, if applicable) are present in
# All / Most / Few clinically-relevant transcripts.
# --------------------------------------------------------------------------- #

EXON_RELEVANCE_TIERS = [
    RelevanceTier(
        tier="All",
        multiplier=1.0,
        criterion="exon(s) present in ALL clinically-relevant transcripts",
    ),
    RelevanceTier(
        tier="Most",
        multiplier=0.5,
        criterion="present in MOST clinically-relevant transcripts",
    ),
    RelevanceTier(
        tier="Few",
        multiplier=0.0,
        criterion="present in FEW / no clinically-relevant transcripts",
    ),
]

# Baseline missense: predictors already capture mechanism, so the gene-disease
# mechanism cross-reference is NOT folded in here.
MIS_PRD_EXON_REL_V4 = ExonRelevanceConfig(
    tier_multipliers=EXON_RELEVANCE_TIERS,
    include_mechanism=False,
)

# Null / in-frame / splice families: same matrix, but the gene-disease molecular
# mechanism cross-reference is folded into this node.
EXON_REL_WITH_MECHANISM_V4 = ExonRelevanceConfig(
    tier_multipliers=EXON_RELEVANCE_TIERS,
    include_mechanism=True,
)
