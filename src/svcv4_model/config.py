"""Typed **configuration model** behind SVCv4 codes.

A code (e.g. ``svc:MIS_PRD_INIT_INSILICO``) is only a name; the *behaviour* behind
it — the numbers that turn evidence into points — lives in the ruleset's
``params``. This module gives those params a typed shape so the baseline
configuration can be validated, documented, and **modified** by a specialisation
(a scoped ruleset in its own namespace) without changing the code itself.

The first configured family is the in-silico predictor initial-points code. Its
model is a dictionary keyed by predictor tool, each holding an ordered list of
``(points, score-interval)`` bands transcribed from SM 6, Figure 2. Each tool's
bands are **contiguous and cover 100%** of its ``[min, max]`` domain, so the code
behaves like a small API: given a tool and a score it returns exactly one point
value, or raises if the tool is unknown or the score is out of range.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from svcv4_model.informative import InformativeVariant, VariantClassification


class UnknownTool(ValueError):
    """Raised when a score is requested for a tool that is not configured."""


class ScoreOutOfRange(ValueError):
    """Raised when a score falls outside a tool's covered ``[min, max]`` domain."""


class ScoreBand(BaseModel):
    """One ``(points, score-interval)`` row of a predictor's calibration table.

    The interval is ``min``..``max``; ``None`` means unbounded (−∞ / +∞).
    ``min_incl`` / ``max_incl`` select closed ``[ ]`` vs open ``( )`` at each end.
    Bands default to the half-open form ``[min, max)`` — lower-inclusive,
    upper-exclusive — so that adjacent bands tile a tool's domain without gaps or
    overlaps (a boundary value belongs to exactly one band). A tool whose scale is
    inverted (ESM1b: higher score ⇒ more benign) is handled the same way — the
    intervals still tile the score axis, only the point labels run the other way.
    """

    model_config = ConfigDict(extra="forbid")

    points: float = Field(description="Initial evidence points for scores in this band.")
    min: float | None = Field(default=None, description="Lower bound; None = −∞.")
    max: float | None = Field(default=None, description="Upper bound; None = +∞.")
    min_incl: bool = Field(default=True, description="Lower bound inclusive ([) vs exclusive (().")
    max_incl: bool = Field(default=False, description="Upper bound inclusive (]) vs exclusive ()).")

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

    **The API.** ``evaluate(tool, score)`` is the code's call: the *inputs* are a
    configured tool name and a numeric score; the *output* is the point value of
    the band the score falls in. *Conditions*: the tool must be configured
    (else ``UnknownTool``) and the score must lie within the tool's covered
    ``[min, max]`` domain (else ``ScoreOutOfRange``). Each tool's bands are
    validated on construction to be contiguous and cover that domain 100%.
    """

    model_config = ConfigDict(extra="forbid")

    selectable_tools: list[str]
    per_tool_bands: dict[str, list[ScoreBand]] = Field(default_factory=dict)
    selected_tool: str | None = None

    @model_validator(mode="after")
    def _check_full_coverage(self) -> InsilicoPredictorConfig:
        """Every tool's bands must be contiguous and cover [min, max] with no gap/overlap."""
        for tool, bands in self.per_tool_bands.items():
            if not bands:  # a tool with no baseline bands (e.g. OTHER_CALIBRATED) is allowed
                continue
            ordered = sorted(bands, key=lambda b: float("-inf") if b.min is None else b.min)
            for lower, upper in zip(ordered, ordered[1:], strict=False):
                lo_max = float("inf") if lower.max is None else lower.max
                up_min = float("-inf") if upper.min is None else upper.min
                if lo_max != up_min:
                    raise ValueError(
                        f"{tool}: not contiguous — {lower.interval} then {upper.interval} "
                        f"(gap or overlap between bands)"
                    )
                if lower.max_incl == upper.min_incl:
                    kind = "double-covers" if lower.max_incl else "leaves a gap at"
                    raise ValueError(
                        f"{tool}: boundary {lo_max:g} {kind} — {lower.interval} vs {upper.interval}"
                    )
        return self

    def domain(self, tool: str) -> tuple[float | None, float | None]:
        """The covered ``(min, max)`` for ``tool`` (None = unbounded). Raises UnknownTool."""
        bands = self.per_tool_bands.get(tool)
        if not bands:
            raise UnknownTool(f"tool {tool!r} has no configured bands")
        ordered = sorted(bands, key=lambda b: float("-inf") if b.min is None else b.min)
        return ordered[0].min, ordered[-1].max

    def evaluate(self, tool: str, score: float) -> float:
        """Points for ``score`` under ``tool``. Raises UnknownTool / ScoreOutOfRange."""
        bands = self.per_tool_bands.get(tool)
        if not bands:
            if tool in self.selectable_tools:
                raise UnknownTool(
                    f"tool {tool!r} is selectable but has no configured bands "
                    "(a specialisation must supply them)"
                )
            raise UnknownTool(f"unknown tool {tool!r}; configured: {sorted(self.per_tool_bands)}")
        for band in bands:
            if band.contains(score):
                return band.points
        lo, hi = self.domain(tool)
        lo_s = "-inf" if lo is None else f"{lo:g}"
        hi_s = "+inf" if hi is None else f"{hi:g}"
        raise ScoreOutOfRange(f"{tool} score {score:g} outside covered domain [{lo_s}, {hi_s}]")

    def tools(self) -> list[str]:
        """The list of predictor tools valid for this configuration (the selectable menu)."""
        return list(self.selectable_tools)

    # backward-compatible alias
    def points_for(self, tool: str, score: float) -> float:
        """Alias for :meth:`evaluate`."""
        return self.evaluate(tool, score)


def insilico_config(params: dict) -> InsilicoPredictorConfig:
    """Read a ruleset's ``params`` dict back into the typed config."""
    return InsilicoPredictorConfig.model_validate(params)


class UnknownTier(ValueError):
    """Raised when a relevance tier is not in the configured matrix."""


class UnknownMechanism(ValueError):
    """Raised when a mechanism type or classification is not configured."""


class MissingInput(ValueError):
    """Raised when ``evaluate`` is called without a required argument."""


class RelevanceTier(BaseModel):
    """One row of the exon-relevance matrix — a tier and the fraction it applies."""

    model_config = ConfigDict(extra="forbid")

    tier: str = Field(description="Relevance tier, e.g. 'All' | 'Most' | 'Few'.")
    multiplier: float = Field(
        ge=0.0, le=1.0, description="Fraction the initial points are scaled by (0.0–1.0)."
    )
    criterion: str | None = Field(default=None, description="What the tier means, in words.")


class MechanismClassification(BaseModel):
    """One ``(classification, weight)`` value of a mechanism-classification type."""

    model_config = ConfigDict(extra="forbid")

    classification: str = Field(description="The classification value, e.g. 'Consistent'.")
    weight: float = Field(ge=0.0, le=1.0, description="Its weight, 0.0–1.0 (0–100%).")
    description: str | None = Field(default=None, description="What the value means, in words.")


class MechanismBand(BaseModel):
    """One mechanism-classification **type** — a named set of classifications + weights.

    A rule may configure several types (e.g. molecular mechanism, functional
    mechanism), each with its own value set. ``evaluate`` selects a type by name.
    """

    model_config = ConfigDict(extra="forbid")

    mechanism_type: str = Field(description="Name of this classification type.")
    classifications: list[MechanismClassification]

    def weight_for(self, classification: str) -> float:
        """Weight for ``classification`` (case-insensitive); raises UnknownMechanism."""
        for value in self.classifications:
            if value.classification.casefold() == classification.casefold():
                return value.weight
        known = ", ".join(v.classification for v in self.classifications)
        raise UnknownMechanism(
            f"unknown classification {classification!r} for mechanism type "
            f"{self.mechanism_type!r}; expected one of: {known}"
        )


class ExonRelevanceConfig(BaseModel):
    """Configuration behind an ``exon-relevance-assessment`` code.

    The code outputs a **multiplier** (not points): the initial predictive points
    are scaled by how many clinically-relevant transcripts contain the exon(s)
    harbouring the VBC (``tier_multipliers``), optionally combined with a
    gene-disease **mechanism classification** weight (``mechanism_bands`` — zero or
    more classification *types*, each a set of classifications with 0–100% weights).

    **The API.** ``evaluate(initial_points, tier, mechanism_type, mechanism_class)``:

    - *Input 1* is the initial points being adjusted.
    - If ``only_positive`` is set and ``initial_points <= 0`` → returns ``1.0``
      (no impact — benign/neutral points pass through); no other input is needed.
    - Otherwise ``tier`` is required (``MissingInput`` if absent) and gives the
      tier fraction.
    - If any ``mechanism_bands`` are configured, ``mechanism_type`` and
      ``mechanism_class`` are also required, and the output is
      ``tier_fraction × mechanism_weight``; otherwise it is just ``tier_fraction``.

    A specialisation re-weights the tiers, sets ``only_positive``, or adds /
    re-weights mechanism types — the code is unchanged.
    """

    model_config = ConfigDict(extra="forbid")

    tier_multipliers: list[RelevanceTier]
    only_positive: bool = Field(
        default=False,
        description="If True, the weighting applies only to positive initial points; "
        "non-positive points return a 1.0 (no-impact) factor.",
    )
    mechanism_bands: list[MechanismBand] = Field(default_factory=list)

    @property
    def has_mechanism(self) -> bool:
        """True when at least one mechanism-classification type is configured."""
        return bool(self.mechanism_bands)

    def tiers(self) -> list[str]:
        """The valid relevance tiers, in order (e.g. ['All', 'Most', 'Few'])."""
        return [t.tier for t in self.tier_multipliers]

    def mechanism_types(self) -> list[str]:
        """The valid mechanism-classification types (empty if none configured)."""
        return [b.mechanism_type for b in self.mechanism_bands]

    def classifications(self, mechanism_type: str) -> list[str]:
        """The valid classification values for a mechanism type; raises UnknownMechanism."""
        for band in self.mechanism_bands:
            if band.mechanism_type.casefold() == mechanism_type.casefold():
                return [c.classification for c in band.classifications]
        known = ", ".join(b.mechanism_type for b in self.mechanism_bands) or "(none configured)"
        raise UnknownMechanism(f"unknown mechanism type {mechanism_type!r}; configured: {known}")

    def multiplier_for(self, tier: str) -> float:
        """The fraction for ``tier`` (case-insensitive); raises UnknownTier."""
        for row in self.tier_multipliers:
            if row.tier.casefold() == tier.casefold():
                return row.multiplier
        known = ", ".join(r.tier for r in self.tier_multipliers)
        raise UnknownTier(f"unknown relevance tier {tier!r}; expected one of: {known}")

    def mechanism_weight(self, mechanism_type: str, classification: str) -> float:
        """Weight for a ``(type, classification)`` pair; raises UnknownMechanism."""
        for band in self.mechanism_bands:
            if band.mechanism_type.casefold() == mechanism_type.casefold():
                return band.weight_for(classification)
        known = ", ".join(b.mechanism_type for b in self.mechanism_bands) or "(none configured)"
        raise UnknownMechanism(f"unknown mechanism type {mechanism_type!r}; configured: {known}")

    def evaluate(
        self,
        initial_points: float,
        tier: str | None = None,
        mechanism_type: str | None = None,
        mechanism_class: str | None = None,
    ) -> float:
        """The exon-relevance weighting factor to apply to ``initial_points``.

        See the class docstring for the input/condition contract.
        """
        if self.only_positive and initial_points <= 0:
            return 1.0
        if tier is None:
            raise MissingInput("tier is required to compute the exon-relevance weighting")
        factor = self.multiplier_for(tier)
        if self.mechanism_bands:
            if mechanism_type is None or mechanism_class is None:
                raise MissingInput(
                    "a mechanism type is configured — mechanism_type and "
                    "mechanism_class are both required"
                )
            factor *= self.mechanism_weight(mechanism_type, mechanism_class)
        return factor


def exon_relevance_config(params: dict) -> ExonRelevanceConfig:
    """Read a ruleset's ``params`` dict back into the typed config."""
    return ExonRelevanceConfig.model_validate(params)


def ladder(*rows: tuple[float, float | None]) -> list[ScoreBand]:
    """Build contiguous, 100%-covering bands from ``(points, lower_bound)`` rows.

    Rows are given in ascending score order; ``lower_bound=None`` marks the
    bottom band (−∞). Each band spans ``[lower, next_lower)`` (half-open,
    lower-inclusive); the top band runs to ``+∞``. So the whole real line is
    tiled with no gaps or overlaps. The cut points are the SM 6 Fig 2 band
    lower thresholds; a score of exactly a cut belongs to the higher band.
    """
    out: list[ScoreBand] = []
    for i, (points, lower) in enumerate(rows):
        upper = rows[i + 1][1] if i + 1 < len(rows) else None
        out.append(ScoreBand(points=points, min=lower, max=upper))
    return out


# --------------------------------------------------------------------------- #
# Baseline configuration for svc:MIS_PRD_INIT_INSILICO:4.0
#
# Transcribed from SM 6, Figure 2 ("Initial evidence points for missense variants
# based on in-silico prediction"), as contiguous bands (each band's lower = the
# figure's stated band-start; upper = the next band's start). Four tools reach
# −3.0, three reach −4.0 for benignity; every tool reaches +4.0. Rows are in
# ascending SCORE order — so ESM1b (inverted: higher score ⇒ more benign) runs
# from +4 up to −3. All tools span −∞…+∞, so any real score maps to a band.
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
        "AlphaMissense": ladder(
            (-3, None),
            (-2, 0.071),
            (-1, 0.100),
            (0, 0.170),
            (1, 0.792),
            (2, 0.906),
            (3, 0.972),
            (4, 0.990),
        ),
        "BayesDel": ladder(
            (-3, None),
            (-2, -0.519),
            (-1, -0.359),
            (0, -0.179),
            (1, 0.130),
            (2, 0.270),
            (3, 0.410),
            (4, 0.50),
        ),
        # ESM1b inverted — ascending score runs from most-pathogenic (+4) to benign (−3).
        "ESM1b": ladder(
            (4, None),
            (3, -23.9),
            (2, -13.9),
            (1, -12.1),
            (0, -10.6),
            (-1, -6.3),
            (-2, -3.1),
            (-3, 8.8),
        ),
        "VEST4": ladder(
            (-3, None),
            (-2, 0.078),
            (-1, 0.303),
            (0, 0.450),
            (1, 0.764),
            (2, 0.861),
            (3, 0.909),
            (4, 0.965),
        ),
        # ---- reach −4.0 ----
        "MutPred2": ladder(
            (-4, None),
            (-3, 0.011),
            (-2, 0.032),
            (-1, 0.198),
            (0, 0.392),
            (1, 0.737),
            (2, 0.829),
            (3, 0.895),
            (4, 0.932),
        ),
        "REVEL": ladder(
            (-4, None),
            (-3, 0.017),
            (-2, 0.053),
            (-1, 0.184),
            (0, 0.291),
            (1, 0.644),
            (2, 0.773),
            (3, 0.879),
            (4, 0.932),
        ),
        "VARITY_R": ladder(
            (-4, None),
            (-3, 0.037),
            (-2, 0.063),
            (-1, 0.117),
            (0, 0.252),
            (1, 0.675),
            (2, 0.842),
            (3, 0.915),
            (4, 0.966),
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


def mechanism_band(mechanism_type: str, *pairs: tuple[str, float]) -> MechanismBand:
    """Build a **reusable** mechanism band from ``(classification, weight)`` pairs.

    Define a band once and pass it into any number of exon-relevance configs::

        LOF = mechanism_band("LOF", ("Established", 1.0), ("Likely", 0.5), ...)
        cfg = ExonRelevanceConfig(tier_multipliers=..., mechanism_bands=[LOF])
    """
    return MechanismBand(
        mechanism_type=mechanism_type,
        classifications=[MechanismClassification(classification=c, weight=w) for c, w in pairs],
    )


# Baseline exon-relevance config. All four families share the tier matrix.
# MIS configures NO mechanism; the null / in-frame / splice families (NUL, CDS,
# SPL) each configure a "LOF" mechanism-classification type. Because a band is a
# reusable component, they share ONE LOF_MECHANISM_BAND — but a family may pass a
# different band if its mechanism weights need to differ.

# One reusable mechanism-classification TYPE, "LOF" (loss-of-function): how well
# the established gene-disease molecular mechanism supports LoF for this VBC.
LOF_MECHANISM_BAND = MechanismBand(
    mechanism_type="LOF",
    classifications=[
        MechanismClassification(
            classification="Established",
            weight=1.0,
            description="LOF is the established gene-disease mechanism",
        ),
        MechanismClassification(
            classification="Likely",
            weight=0.5,
            description="LOF is the likely gene-disease mechanism",
        ),
        MechanismClassification(
            classification="Suspected",
            weight=0.25,
            description="LOF is a suspected gene-disease mechanism",
        ),
        MechanismClassification(
            classification="Uncertain or Not LOF",
            weight=0.0,
            description="mechanism uncertain, or not loss-of-function",
        ),
    ],
)


def exon_relevance_baseline(
    only_positive: bool, mechanism_bands: list[MechanismBand] | None = None
) -> ExonRelevanceConfig:
    """Baseline exon-relevance config: SM 6 Fig 2 tier matrix + any reusable bands passed in."""
    return ExonRelevanceConfig(
        tier_multipliers=EXON_RELEVANCE_TIERS,
        only_positive=only_positive,
        mechanism_bands=list(mechanism_bands) if mechanism_bands else [],
    )


# Convenience baseline (missense — no mechanism). Per-family flags live in the registry.
MIS_PRD_EXON_REL_V4 = exon_relevance_baseline(only_positive=True)

# Convenience baseline for the LOF families (null / in-frame / splice) — the reusable
# LOF band passed in. Each family could instead pass its own band if weights diverge.
EXON_REL_LOF_V4 = exon_relevance_baseline(only_positive=True, mechanism_bands=[LOF_MECHANISM_BAND])


# --------------------------------------------------------------------------- #
# Informative-variants configuration (svc:*_INF:4.0) — SM 19
#
# An informative variant is a distinct, ranked-classified variant at the SAME
# CODON as the VBC but a DIFFERENT nucleotide change (on an equivalent transcript).
# Each variant is placed into ONE scoring group by its clinical significance, its
# amino-acid relation to the VBC (same/distinct), and — for distinct-AA — the
# Grantham difference (VBC_grantham − informative_grantham). A group scores
# (count × points_per_variant) + a one-time definitive bonus when it holds at least
# one definitively-classified variant (Path for the clinically-significant groups,
# Benign for the not-significant groups). Group sums add, cap ±8. No qualifying
# informative variants → evaluate returns None and the code reads *_INF_ND.
# --------------------------------------------------------------------------- #

CLINICALLY_SIGNIFICANT = {
    VariantClassification.PATHOGENIC,
    VariantClassification.LIKELY_PATHOGENIC,
}
NOT_CLINICALLY_SIGNIFICANT = {
    VariantClassification.BENIGN,
    VariantClassification.LIKELY_BENIGN,
}


def _clinical_significance(cls: VariantClassification | None) -> str | None:
    """'significant' (P/LP), 'not_significant' (B/LB), or None (Uncertain/VUS)."""
    if cls in CLINICALLY_SIGNIFICANT:
        return "significant"
    if cls in NOT_CLINICALLY_SIGNIFICANT:
        return "not_significant"
    return None


# most-clinically-significant order (Path first) for de-duplicating a variant
_CLIN_RANK = {
    VariantClassification.PATHOGENIC: 0,
    VariantClassification.LIKELY_PATHOGENIC: 1,
    VariantClassification.VUS: 2,
    VariantClassification.LIKELY_BENIGN: 3,
    VariantClassification.BENIGN: 4,
}


class InfGroup(BaseModel):
    """One informative-variant scoring group (SM 19).

    A variant joins the FIRST group whose criteria it meets: ``clinical``
    (significant P/LP · not_significant B/LB · any), ``aa`` (same · distinct · any),
    and ``grantham`` — the sign of ``VBC_grantham − informative_grantham``
    (``non_negative`` ≥ 0 · ``positive`` > 0 · any). The group scores
    ``count × points_per_variant``, plus ``definitive_bonus`` once if any member
    carries ``definitive_classification`` (Path or Benign — the 'established' call).
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    clinical: Literal["significant", "not_significant", "any"] = "any"
    aa: Literal["same", "distinct", "any"] = "any"
    grantham: Literal["non_negative", "positive", "any"] = "any"
    points_per_variant: float = 0.0
    definitive_bonus: float = 0.0
    definitive_classification: VariantClassification | None = None


class InformativeVariantsConfig(BaseModel):
    """Configuration behind an ``informative-variants-assessment`` code (SM 19).

    ``groups`` is the ordered set of scoring groups — the per-family, modifiable
    axis. A variant counts only if its review ranking is at least
    ``min_star_rating`` (default 3 = expert panel / 3-star); duplicate
    classifications of one variant collapse to the highest-ranked, most
    clinically-significant call. Group sums add and cap to ``[cap_min, cap_max]``.

    **API.** ``evaluate(variants, vbc_grantham=None)`` → points, or **None** when
    no qualifying informative variants were found (the code reads ``*_INF_ND``).
    ``classify(variant, vbc_grantham)`` → the group name (or None).
    """

    model_config = ConfigDict(extra="forbid")

    groups: list[InfGroup]
    cap_min: float = -8.0
    cap_max: float = 8.0
    min_star_rating: int = 3
    require_distinct_evidence: bool = False
    require_circularity_check: bool = False

    def group_names(self) -> list[str]:
        """The configured scoring groups, in match order."""
        return [g.name for g in self.groups]

    def _passes_gates(self, v: InformativeVariant) -> bool:
        if v.star_rating is None or v.star_rating < self.min_star_rating:
            return False
        if self.require_distinct_evidence and not v.distinct_evidence_from_vbc:
            return False
        return not (self.require_circularity_check and not v.circularity_checked)

    def _dedup(self, variants: list[InformativeVariant]) -> list[InformativeVariant]:
        """One call per variant id: highest star, then most clinically significant."""

        def key(v: InformativeVariant) -> tuple[float, int]:
            star = v.star_rating if v.star_rating is not None else -1
            return (star, -_CLIN_RANK.get(v.classification, -99))

        best: dict[str, InformativeVariant] = {}
        passthrough: list[InformativeVariant] = []
        for v in variants:
            if v.id is None:
                passthrough.append(v)
            elif v.id not in best or key(v) > key(best[v.id]):
                best[v.id] = v
        return list(best.values()) + passthrough

    @staticmethod
    def _grantham_ok(cond: str, diff: float | None) -> bool:
        if cond == "any":
            return True
        if diff is None:
            return False
        return diff >= 0 if cond == "non_negative" else diff > 0

    def classify(self, v: InformativeVariant, vbc_grantham: float | None = None) -> str | None:
        """The name of the first group this variant matches, or None."""
        clin = _clinical_significance(v.classification)
        aa = v.aa.value if v.aa is not None else None
        diff = None if (v.grantham is None or vbc_grantham is None) else vbc_grantham - v.grantham
        for g in self.groups:
            if g.clinical != "any" and clin != g.clinical:
                continue
            if g.aa != "any" and aa != g.aa:
                continue
            if not self._grantham_ok(g.grantham, diff):
                continue
            return g.name
        return None

    def evaluate(
        self, variants: list[InformativeVariant], vbc_grantham: float | None = None
    ) -> float | None:
        """Informative-variants points, or None (``*_INF_ND``) if none qualify."""
        kept = [v for v in self._dedup(variants) if self._passes_gates(v)]
        if not kept:
            return None  # no qualifying informative variants → _ND

        members: dict[str, list[InformativeVariant]] = {}
        for v in kept:
            name = self.classify(v, vbc_grantham)
            if name is not None:
                members.setdefault(name, []).append(v)

        total = 0.0
        for g in self.groups:
            group = members.get(g.name, [])
            if not group:
                continue
            score = len(group) * g.points_per_variant
            if g.definitive_classification is not None and any(
                v.classification == g.definitive_classification for v in group
            ):
                score += g.definitive_bonus
            total += score
        return max(self.cap_min, min(self.cap_max, total))


def informative_config(params: dict) -> InformativeVariantsConfig:
    """Read a ruleset's ``params`` dict back into the typed config."""
    return InformativeVariantsConfig.model_validate(params)


# --- MIS_INF: the five-group missense model (SM 19) ------------------------- #
# aa = same|distinct amino-acid change vs the VBC (same codon, different nt).
# grantham diff = VBC_grantham − informative_grantham (distinct-AA groups only).
_P = VariantClassification.PATHOGENIC
_B = VariantClassification.BENIGN
MIS_INF_V4 = InformativeVariantsConfig(
    min_star_rating=3,
    groups=[
        InfGroup(  # a) clinically significant, same AA
            name="a_clin_sig_same_aa",
            clinical="significant",
            aa="same",
            points_per_variant=2.0,
            definitive_bonus=2.0,
            definitive_classification=_P,
        ),
        InfGroup(  # b) clinically significant, distinct AA, VBC−INF >= 0
            name="b_clin_sig_distinct_aa_nonneg_grantham",
            clinical="significant",
            aa="distinct",
            grantham="non_negative",
            points_per_variant=1.0,
            definitive_bonus=1.0,
            definitive_classification=_P,
        ),
        InfGroup(  # c) not clinically significant, distinct AA, VBC−INF > 0
            name="c_not_sig_distinct_aa_pos_grantham",
            clinical="not_significant",
            aa="distinct",
            grantham="positive",
            points_per_variant=-1.0,
            definitive_bonus=-1.0,
            definitive_classification=_B,
        ),
        InfGroup(  # d) not clinically significant, same AA
            name="d_not_sig_same_aa",
            clinical="not_significant",
            aa="same",
            points_per_variant=-2.0,
            definitive_bonus=-2.0,
            definitive_classification=_B,
        ),
        InfGroup(name="e_other"),  # e) all other informative variants -> 0
    ],
)


def _inf_generic() -> InformativeVariantsConfig:
    """Provisional NUL/CDS/SPL config: clinically-significant / not-significant /
    other groups at SM 19 base magnitudes — pending each pathway's own rules."""
    return InformativeVariantsConfig(
        groups=[
            InfGroup(
                name="clinically_significant",
                clinical="significant",
                points_per_variant=2.0,
                definitive_bonus=2.0,
                definitive_classification=_P,
            ),
            InfGroup(
                name="not_clinically_significant",
                clinical="not_significant",
                points_per_variant=-2.0,
                definitive_bonus=-2.0,
                definitive_classification=_B,
            ),
            InfGroup(name="other"),
        ]
    )


NUL_INF_V4 = _inf_generic()
CDS_INF_V4 = _inf_generic()
SPL_INF_V4 = _inf_generic()
