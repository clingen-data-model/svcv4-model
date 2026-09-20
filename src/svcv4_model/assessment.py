"""Assessment registry — the reusable rulesets that produce SVCv4 evidence-line scores.

Every scored branch of a workflow is an **assessment**. Its stable name is the
``methodType`` carried on the ``specifiedBy`` (``Method``) of an evidence-line
``Statement``. This module defines:

- ``AssessmentType`` — the *shape* of an assessment (data items it needs, what it
  produces, which parameters may be reconfigured). Keyed by ``method_type`` in
  ``ASSESSMENT_TYPES``. Stable across baseline and every specialization.
- ``MethodConfig`` — a *configured instance* of an assessment: the baseline
  framework's settings, or a specialised alternative for a gene / disease area.
  Identified by a namespaced, versioned id ``svcv4-<scope>:<method_type>:<version>``.

The split is deliberate: ``methodType`` keeps results **comparable** ("this is a
mechanism-exon assessment"); ``specifiedBy.id`` keeps them **reproducible** (exactly
which configured ruleset ran). A specialisation reuses the same ``method_type`` but
mints a new ``id`` under its own scope — it does not mint a new code each time.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --------------------------------------------------------------------------- #
# vocabularies
# --------------------------------------------------------------------------- #


GROUP = Literal["router", "initial", "adjuster", "module", "gate"]
DATA_ROLE = Literal["input", "gate", "router", "provenance"]
OUTPUT_KIND = Literal["points", "multiplier", "route"]


class DataItemSpec(BaseModel):
    """One evidence data item an assessment consumes."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(description="Stable key for the data item (a DataItem subtype).")
    role: DATA_ROLE = Field(
        description="Why it's needed: input (scored), gate, router, or provenance."
    )
    description: str | None = Field(default=None)
    example: str | None = Field(default=None, description="A concrete example value, for docs.")


class AssessmentType(BaseModel):
    """The reusable *shape* of an assessment — stable across configurations."""

    model_config = ConfigDict(extra="forbid")

    method_type: str = Field(
        description="Stable assessment name; the value of `specifiedBy.methodType`."
    )
    title: str = Field(description="Human-readable label.")
    group: GROUP = Field(description="Pipeline role.")
    output_kind: OUTPUT_KIND = Field(
        description="`points` (adds a score), `multiplier` (scales), or `route` (picks a lane)."
    )
    produces: list[str] = Field(
        default_factory=list,
        description="Code(s) / code-patterns this assessment can emit.",
    )
    score_min: float | None = Field(default=None)
    score_max: float | None = Field(default=None)
    data_items: list[DataItemSpec] = Field(default_factory=list)
    params: list[str] = Field(
        default_factory=list,
        description="Parameter names a MethodConfig may set/override.",
    )
    description: str | None = Field(default=None)


class MethodConfig(BaseModel):
    """A configured instance of an ``AssessmentType`` — baseline or specialised."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        description="`svcv4-<scope>:<method_type>:<version>` — the value of `specifiedBy.id`."
    )
    method_type: str = Field(description="The AssessmentType this configures.")
    scope: str = Field(description="`baseline`, or a specialisation scope e.g. `gene-MYH7`.")
    version: str = Field(description="Config version (independent of the framework version).")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Configured parameter values (overrides of the baseline).",
    )
    description: str | None = Field(default=None)

    @field_validator("id")
    @classmethod
    def _id_shape(cls, v: str) -> str:
        if not v.startswith("svcv4-") or v.count(":") != 2:
            raise ValueError("Method id must be 'svcv4-<scope>:<method_type>:<version>'")
        return v


# --------------------------------------------------------------------------- #
# id helpers
# --------------------------------------------------------------------------- #


def make_method_id(scope: str, method_type: str, version: str) -> str:
    """Build a Method id: ``svcv4-<scope>:<method_type>:<version>``."""
    return f"svcv4-{scope}:{method_type}:{version}"


def parse_method_id(method_id: str) -> tuple[str, str, str]:
    """Return ``(scope, method_type, version)`` from a Method id."""
    ns, method_type, version = method_id.split(":")
    return ns.removeprefix("svcv4-"), method_type, version


# --------------------------------------------------------------------------- #
# registry helpers
# --------------------------------------------------------------------------- #


def _di(
    key: str, role: DATA_ROLE, example: str | None = None, description: str | None = None
) -> DataItemSpec:
    return DataItemSpec(key=key, role=role, example=example, description=description)


def register_assessment(a: AssessmentType) -> AssessmentType:
    ASSESSMENT_TYPES[a.method_type] = a
    return a


def register_config(c: MethodConfig) -> MethodConfig:
    scope, mt, _ = parse_method_id(c.id)
    if mt != c.method_type:
        raise ValueError(f"id method_type '{mt}' != config.method_type '{c.method_type}'")
    if c.method_type not in ASSESSMENT_TYPES:
        raise ValueError(f"unknown method_type '{c.method_type}'")
    METHOD_CONFIGS[c.id] = c
    return c


def resolve(method_id: str) -> MethodConfig:
    """Resolve a ``specifiedBy.id`` to its registered ``MethodConfig``."""
    return METHOD_CONFIGS[method_id]


ASSESSMENT_TYPES: dict[str, AssessmentType] = {}
METHOD_CONFIGS: dict[str, MethodConfig] = {}


# --------------------------------------------------------------------------- #
# PRD-family assessment types (grounded in SM 6 / 8 / 11 / 18 / 20)
# --------------------------------------------------------------------------- #

register_assessment(
    AssessmentType(
        method_type="nmd-prediction-assessment",
        title="NMD prediction (router)",
        group="router",
        output_kind="route",
        produces=["routes NUL/CDS"],
        params=["nmd_upstream_nt"],
        data_items=[
            _di("ptc_vs_last_junction", "router", "60 nt upstream ⇒ NMD"),
            _di("exon_count", "router", "single-exon ⇒ no NMD"),
            _di("start_proximity", "provenance", "possible 5′ NMD escape"),
        ],
        description="PTC ≥ nmd_upstream_nt upstream of the last junction ⇒ NUL lane; else CDS.",
    )
)
register_assessment(
    AssessmentType(
        method_type="alt-met-rescue-assessment",
        title="Alternative-Met rescue (router)",
        group="router",
        output_kind="route",
        produces=["routes NUL/CDS"],
        params=[],
        data_items=[
            _di("alt_met_functional_rescue", "router", "truncated protein retains function"),
            _di("no_plp_between_starts", "router", "no P/LP between Met1 and alt-Met"),
        ],
        description="Rescue evidence ⇒ leave NUL for the CDS lane.",
    )
)
register_assessment(
    AssessmentType(
        method_type="insilico-missense-predictor-assessment",
        title="In-silico missense predictor",
        group="initial",
        output_kind="points",
        produces=["MIS_PRD_INIT_*"],
        score_min=-4.0,
        score_max=4.0,
        params=["predictor", "calibration_thresholds"],
        data_items=[
            _di("predictor", "input", "REVEL"),
            _di("raw_score", "input", "0.972 ⇒ +4.0"),
            _di("calibration", "provenance", "REVEL ≥ 0.932 ⇒ +4.0"),
        ],
        description="One pre-selected calibrated predictor sets the missense initial points.",
    )
)
register_assessment(
    AssessmentType(
        method_type="nmd-initial-points-assessment",
        title="NMD initial points",
        group="initial",
        output_kind="points",
        produces=["NUL_PRD"],
        score_min=0.0,
        score_max=6.0,
        params=["award"],
        data_items=[_di("nmd_predicted", "input", "true ⇒ +6.0")],
        description="Fixed initial points when NMD is predicted (no alt-Met rescue).",
    )
)
register_assessment(
    AssessmentType(
        method_type="protein-loss-assessment",
        title="Protein-loss / critical-domain",
        group="initial",
        output_kind="points",
        produces=["CDS_PRD"],
        score_min=-1.0,
        score_max=6.0,
        params=["tier_points"],
        data_items=[
            _di("protein_fraction_reduced", "input", ">50% lost ⇒ +6.0"),
            _di("critical_domain_loss", "input", "alters critical motif ⇒ +6.0"),
            _di("alt_met_functional", "input", "functional alt-start ⇒ −1.0"),
        ],
        description="Initial points for CDS lanes: protein lost / criticality (first hit wins).",
    )
)
register_assessment(
    AssessmentType(
        method_type="splice-prediction-assessment",
        title="Splice prediction",
        group="initial",
        output_kind="points",
        produces=["SPL_PRD"],
        score_min=0.0,
        score_max=3.0,
        params=["predictor", "calibration_thresholds"],
        data_items=[
            _di("splice_prediction", "input", "SpliceAI Δ 0.82 ⇒ likely"),
            _di("splice_frameshift_nmd", "router", "PTC ≥50 nt upstream ⇒ NMD sub-path"),
        ],
        description="In-silico splice prediction; sub-routes on frameshift & NMD.",
    )
)
register_assessment(
    AssessmentType(
        method_type="exon-transcript-relevance-assessment",
        title="Exon / transcript relevance",
        group="adjuster",
        output_kind="multiplier",
        produces=["MIS_PRD_EXON_*"],
        score_min=0.0,
        score_max=1.0,
        params=["tier_multipliers"],
        data_items=[
            _di("exon_relevance", "input", "All ⇒ ×1.0 · Few ⇒ ×0"),
            _di("mane_status", "gate", "not in MANE ⇒ only Few"),
            _di("tissue_expression", "provenance", "GTEx / pext"),
        ],
        description="Exon axis only (missense) — mechanism axis is not applied on MIS_PRD.",
    )
)
register_assessment(
    AssessmentType(
        method_type="mechanism-exon-relevance-assessment",
        title="Mechanism × exon relevance (SM 18)",
        group="adjuster",
        output_kind="multiplier",
        produces=["NUL_PRD", "CDS_PRD", "SPL_PRD"],
        score_min=0.0,
        score_max=1.0,
        params=["matrix", "gdv_gate"],
        data_items=[
            _di("gencc_mechanism", "input", "Established ⇒ 1.0 · Suspected ⇒ 0.25"),
            _di("gene_disease_validity", "gate", "below Moderate ⇒ Uncertain ⇒ ×0"),
            _di("exon_relevance", "input", "Most ⇒ ×0.5"),
            _di("mane_status", "gate", "not in MANE ⇒ only Few"),
        ],
        description="Full SM 18 matrix — both mechanism and exon axes, on positive initial points.",
    )
)
register_assessment(
    AssessmentType(
        method_type="splice-assay-assessment",
        title="Splice assay",
        group="module",
        output_kind="points",
        produces=["SPL_SPA"],
        score_min=0.0,
        score_max=6.0,
        params=["calibration"],
        data_items=[
            _di("aberrant_product_level", "input", "near-complete ⇒ 100% of SPL_PRD"),
            _di("concordance", "gate", "discordant ⇒ re-route"),
        ],
        description="RNA/splice data supplementing the SPL_PRD prediction.",
    )
)
register_assessment(
    AssessmentType(
        method_type="functional-assay-assessment",
        title="Functional assay (generic)",
        group="module",
        output_kind="points",
        produces=["*_FXN"],
        score_min=-8.0,
        score_max=8.0,
        params=["calibration"],
        data_items=[
            _di("assay_result", "input", "loss of transactivation ⇒ +4"),
            _di("calibrated_weight", "input", "OddsPath / MaveDB"),
            _di("flow_concordance", "gate", "must confirm this flow's prediction"),
        ],
        description="Generic functional module appended in every flow (*_FXN).",
    )
)
register_assessment(
    AssessmentType(
        method_type="informative-variants-assessment",
        title="Informative variants (generic)",
        group="module",
        output_kind="points",
        produces=["*_INF"],
        score_min=-8.0,
        score_max=8.0,
        params=["point_values", "relatedness_rule"],
        data_items=[
            _di("comparator_variant", "input", "same-AA c.1420G>A"),
            _di("classification_tier", "input", "P ⇒ +4 · LP ⇒ +2"),
            _di("order_first_additional", "input", "first vs additional"),
            _di("relatedness", "gate", "flow-specific relatedness rule"),
            _di("grantham", "provenance", "distinct-AA Grantham comparison"),
        ],
        description="Generic informative-variants module (*_INF); relatedness rule per flow.",
    )
)


# --------------------------------------------------------------------------- #
# baseline configs — one per assessment type
# --------------------------------------------------------------------------- #

for _mt in list(ASSESSMENT_TYPES):
    register_config(
        MethodConfig(
            id=make_method_id("baseline", _mt, "1.0"),
            method_type=_mt,
            scope="baseline",
            version="1.0",
            params={},
            description="Baseline SVCv4 framework configuration.",
        )
    )

# --------------------------------------------------------------------------- #
# example specialisation — a gene-specific missense predictor config
# --------------------------------------------------------------------------- #

register_config(
    MethodConfig(
        id=make_method_id("gene-MYH7", "insilico-missense-predictor-assessment", "1.0"),
        method_type="insilico-missense-predictor-assessment",
        scope="gene-MYH7",
        version="1.0",
        params={
            "predictor": "REVEL(MYH7-recalibrated)",
            "calibration_thresholds": {"+4.0": ">=0.90"},
        },
        description="MYH7 cardiomyopathy specialisation: gene-recalibrated REVEL thresholds. "
        "Same methodType as baseline; distinct id/scope.",
    )
)
