"""Assessment registry — SVCv4 rulesets as a hierarchical method.

Two layers, deliberately separated:

- ``AssessmentType`` — a **pattern** (the general *type* of assessment). Its name
  is the ``methodType`` on an evidence-line ``Statement``. A pattern is **reusable**:
  the same pattern (e.g. ``functional-assay-assessment``) appears in many pathways.
- ``Ruleset`` — a **specific, registered ruleset**: one node of a workflow pathway,
  with a unique id ``svcv4-<scope>:<CODE>:<version>`` named for its SVCv4 code, its
  own configured ``params``, and a ``parent`` (its place in the hierarchy). A
  registered ruleset is **never reused** — each pathway node is its own id, even when
  two nodes share a ``method_type`` pattern (they may carry different values).

The whole **SVCv4 method** is therefore the tree of baseline ``Ruleset`` nodes; a
specialization overrides individual nodes by id (same ``method_type``, new scoped id).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

GROUP = Literal["rollup", "router", "initial", "adjuster", "module"]
DATA_ROLE = Literal["input", "gate", "router", "provenance"]
OUTPUT_KIND = Literal["points", "multiplier", "route"]


class DataItemSpec(BaseModel):
    """One evidence data item a pattern consumes."""

    model_config = ConfigDict(extra="forbid")

    key: str
    role: DATA_ROLE
    description: str | None = None
    example: str | None = None


class AssessmentType(BaseModel):
    """A reusable assessment **pattern** — the value of ``specifiedBy.methodType``."""

    model_config = ConfigDict(extra="forbid")

    method_type: str = Field(description="Stable, descriptive pattern name.")
    title: str
    group: GROUP
    output_kind: OUTPUT_KIND
    score_min: float | None = None
    score_max: float | None = None
    data_items: list[DataItemSpec] = Field(default_factory=list)
    params: list[str] = Field(default_factory=list)
    description: str | None = None


class Ruleset(BaseModel):
    """A specific registered ruleset — one node of a pathway. Its id is never reused."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="`svcv4-<scope>:<CODE>:<version>` — value of `specifiedBy.id`.")
    code: str = Field(description="The SVCv4 code this node produces, e.g. `MIS_PRD_EXON`.")
    label: str = Field(description="Human method name for this exact pathway node.")
    method_type: str = Field(description="The AssessmentType (pattern) this instantiates.")
    scope: str = Field(description="`baseline` or a specialisation scope, e.g. `gene-MYH7`.")
    version: str = Field(default="1.0")
    parent: str | None = Field(default=None, description="Parent ruleset id (hierarchy).")
    params: dict[str, Any] = Field(default_factory=dict)
    description: str | None = None

    @field_validator("id")
    @classmethod
    def _id_shape(cls, v: str) -> str:
        if not v.startswith("svcv4") or v.count(":") != 2:
            raise ValueError(
                "Ruleset id must be 'svcv4:<CODE>:<version>' (baseline) or "
                "'svcv4-<scope>:<CODE>:<version>' (specialisation)"
            )
        return v


# --------------------------------------------------------------------------- #
# id helpers
# --------------------------------------------------------------------------- #


def make_ruleset_id(scope: str, code: str, version: str = "1.0") -> str:
    """Baseline ids are ``svcv4:<CODE>:<version>``; specialisations
    ``svcv4-<scope>:<CODE>:<version>``."""
    ns = "svcv4" if scope == "baseline" else f"svcv4-{scope}"
    return f"{ns}:{code}:{version}"


def parse_ruleset_id(rid: str) -> tuple[str, str, str]:
    ns, code, version = rid.split(":")
    scope = "baseline" if ns == "svcv4" else ns.removeprefix("svcv4-")
    return scope, code, version


# --------------------------------------------------------------------------- #
# registries + helpers
# --------------------------------------------------------------------------- #

ASSESSMENT_TYPES: dict[str, AssessmentType] = {}
RULESETS: dict[str, Ruleset] = {}


def _pat(
    method_type: str,
    title: str,
    group: GROUP,
    output_kind: OUTPUT_KIND,
    smin: float | None = None,
    smax: float | None = None,
    params: tuple[str, ...] = (),
    data_items: tuple[DataItemSpec, ...] = (),
) -> None:
    ASSESSMENT_TYPES[method_type] = AssessmentType(
        method_type=method_type,
        title=title,
        group=group,
        output_kind=output_kind,
        score_min=smin,
        score_max=smax,
        params=list(params),
        data_items=list(data_items),
    )


def _di(key: str, role: DATA_ROLE, example: str | None = None) -> DataItemSpec:
    return DataItemSpec(key=key, role=role, example=example)


def ruleset(
    code: str,
    label: str,
    method_type: str,
    *,
    parent: str | None = None,
    scope: str = "baseline",
    version: str = "1.0",
    params: dict[str, Any] | None = None,
) -> Ruleset:
    if method_type not in ASSESSMENT_TYPES:
        raise ValueError(f"unknown method_type '{method_type}' for {code}")
    rid = make_ruleset_id(scope, code, version)
    if rid in RULESETS:
        raise ValueError(f"ruleset id already registered (no reuse): {rid}")
    parent_id = make_ruleset_id(scope, parent, version) if parent else None
    if parent_id and parent_id not in RULESETS:
        raise ValueError(f"parent {parent_id} not registered before {rid}")
    r = Ruleset(
        id=rid,
        code=code,
        label=label,
        method_type=method_type,
        scope=scope,
        version=version,
        parent=parent_id,
        params=params or {},
    )
    RULESETS[rid] = r
    return r


def resolve(rid: str) -> Ruleset:
    return RULESETS[rid]


def children(rid: str) -> list[Ruleset]:
    return [r for r in RULESETS.values() if r.parent == rid]


def roots(scope: str = "baseline") -> list[Ruleset]:
    return [r for r in RULESETS.values() if r.parent is None and r.scope == scope]


# --------------------------------------------------------------------------- #
# patterns (methodType vocabulary)
# --------------------------------------------------------------------------- #

# HOD — names as specified by the SVCv4 team
_pat("population-observation-assessment", "Population observations (POP)", "rollup", "points")
_pat(
    "population-frequency-assessment",
    "Population allele frequency",
    "initial",
    "points",
    -6.0,
    0.0,
    ("fold_thresholds",),
    (_di("faf", "input", "gnomAD FAF 0.00072"), _di("daft", "input", "0.000118")),
)
_pat(
    "population-observation-homo-hemizygote-assessment",
    "Homozygote / hemizygote burden",
    "initial",
    "points",
    -8.0,
    0.0,
    ("per_obs_weight",),
    (
        _di("homozygote_count", "input"),
        _di("hemizygote_count", "input"),
        _di("moi", "input"),
        _di("hmz_eligible", "gate"),
    ),
)
_pat("clinical-observation-assessment", "Clinical observations (CLN)", "rollup", "points")
_pat(
    "affected-observation-assessment",
    "Affected proband",
    "initial",
    "points",
    -8.0,
    8.0,
    ("mono_table", "biallelic_table"),
    (
        _di("pheno_specificity_for_mde", "input", "SPECIFIC/CONSISTENT/INCONSISTENT"),
        _di("moi", "gate", "selects mono vs biallelic table"),
        _di("pop_frq_points", "gate", "NA unless in {0.0,-1.0}"),
    ),
)
_pat(
    "unaffected-observation-assessment",
    "Unaffected carrier",
    "initial",
    "points",
    -8.0,
    0.0,
    ("point_table",),
    (_di("age_matched_penetrance", "input"), _di("vbc_zygosity", "input")),
)
_pat(
    "affected-alternative-observation-assessment",
    "Alternative cause",
    "initial",
    "points",
    -8.0,
    0.0,
    ("point_table",),
    (_di("pheno_severity", "input"), _di("additional_variants", "input")),
)
_pat(
    "affected-denovo-observation-assessment",
    "De-novo occurrence",
    "initial",
    "points",
    -8.0,
    8.0,
    ("point_table",),
    (_di("confirmed_parental_relationship", "input"), _di("pheno_specificity_for_mde", "input")),
)
_pat(
    "case-control-observation-assessment",
    "Case-control study",
    "initial",
    "points",
    -8.0,
    8.0,
    ("or_thresholds",),
    (_di("odds_ratio", "input"), _di("case_count", "input"), _di("control_count", "input")),
)
_pat("locus-specificity-assessment", "Locus specificity (LOC)", "rollup", "points")
_pat(
    "specific-phenotype-assessment",
    "Phenotype specificity",
    "initial",
    "points",
    -8.0,
    8.0,
    ("specificity_table",),
    (
        _di("gene_specificity_for_phenotypes", "input"),
        _di("testing.diagnostic_yield_for_phenotypes", "input"),
    ),
)
_pat(
    "segregation-with-disease-assessment",
    "Co-segregation",
    "initial",
    "points",
    -4.0,
    4.0,
    ("seg_point_tiers", "nonseg_flip"),
    (
        _di("relatives", "input"),
        _di("cosegregation_count", "input"),
        _di("moi", "gate"),
        _di("non_segregation", "gate"),
    ),
)

# PFD — rollups + MIS_PRD (named by the team) + shared/proposed patterns
_pat("missense-variant-assessment", "Missense variant (MIS)", "rollup", "points")
_pat("null-variant-assessment", "Null / nonsense variant (NUL)", "rollup", "points")
_pat(
    "single-aa-change-prediction-assessment",
    "Single-AA-change prediction (MIS_PRD)",
    "rollup",
    "points",
    -4.0,
    4.0,
)
_pat(
    "null-predictive-assessment", "Null predictive roll-up (NUL_PRD)", "rollup", "points", 0.0, 6.0
)
_pat(
    "insilico-predictor-assessment",
    "In-silico predictor",
    "initial",
    "points",
    -4.0,
    4.0,
    ("predictor", "calibration_thresholds"),
    (_di("predictor", "input", "REVEL"), _di("raw_score", "input", "0.972 ⇒ +4.0")),
)
_pat(
    "exon-relevance-assessment",
    "Exon / transcript relevance",
    "adjuster",
    "multiplier",
    0.0,
    1.0,
    ("tier_multipliers",),
    (_di("exon_relevance", "input", "All/Most/Few"), _di("mane_status", "gate")),
)
_pat(
    "mechanism-exon-relevance-assessment",
    "Mechanism × exon relevance (SM 18)",
    "adjuster",
    "multiplier",
    0.0,
    1.0,
    ("matrix", "gdv_gate"),
    (
        _di("gencc_mechanism", "input", "Established/Likely/Suspected/Uncertain"),
        _di("gene_disease_validity", "gate"),
        _di("exon_relevance", "input"),
    ),
)
_pat(
    "nmd-prediction-assessment",
    "NMD prediction (router)",
    "router",
    "route",
    params=("nmd_upstream_nt",),
    data_items=(_di("ptc_vs_last_junction", "router"), _di("exon_count", "router")),
)
_pat(
    "alt-met-rescue-assessment",
    "Alternative-Met rescue (router)",
    "router",
    "route",
    data_items=(_di("alt_met_functional_rescue", "router"), _di("no_plp_between_starts", "router")),
)
_pat(
    "fixed-initial-points-assessment",
    "Fixed initial points",
    "initial",
    "points",
    0.0,
    6.0,
    ("award",),
    (_di("nmd_predicted", "input", "true ⇒ +6.0"),),
)
_pat(
    "protein-loss-assessment",
    "Protein-loss / critical-domain",
    "initial",
    "points",
    -1.0,
    6.0,
    ("tier_points",),
    (_di("protein_fraction_reduced", "input"), _di("critical_domain_loss", "input")),
)
_pat(
    "splice-prediction-assessment",
    "Splice prediction",
    "initial",
    "points",
    0.0,
    3.0,
    ("predictor", "calibration_thresholds"),
    (_di("splice_prediction", "input", "SpliceAI Δ 0.82"),),
)
_pat(
    "splice-assay-assessment",
    "Splice assay",
    "module",
    "points",
    0.0,
    6.0,
    ("calibration",),
    (_di("aberrant_product_level", "input"),),
)
_pat(
    "functional-assay-assessment",
    "Functional assay (generic)",
    "module",
    "points",
    -8.0,
    8.0,
    ("calibration",),
    (_di("assay_result", "input"), _di("calibrated_weight", "input", "OddsPath/MaveDB")),
)
_pat(
    "informative-variants-assessment",
    "Informative variants (generic)",
    "module",
    "points",
    -8.0,
    8.0,
    ("point_values", "relatedness_rule"),
    (_di("comparator_variant", "input"), _di("classification_tier", "input", "P⇒+4·LP⇒+2")),
)


# --------------------------------------------------------------------------- #
# baseline rulesets (the SVCv4 method as a hierarchy) — parent-first
# --------------------------------------------------------------------------- #

# POP
ruleset("POP", "Population observations", "population-observation-assessment")
ruleset("POP_FRQ", "Population allele frequency", "population-frequency-assessment", parent="POP")
ruleset(
    "POP_HMZ",
    "Homozygote/hemizygote burden",
    "population-observation-homo-hemizygote-assessment",
    parent="POP",
)
# CLN
ruleset("CLN", "Clinical observations", "clinical-observation-assessment")
ruleset("CLN_AFF", "Affected proband", "affected-observation-assessment", parent="CLN")
ruleset("CLN_UAF", "Unaffected carrier", "unaffected-observation-assessment", parent="CLN")
ruleset("CLN_ALT", "Alternative cause", "affected-alternative-observation-assessment", parent="CLN")
ruleset("CLN_DNV", "De-novo occurrence", "affected-denovo-observation-assessment", parent="CLN")
ruleset("CLN_CCS", "Case-control study", "case-control-observation-assessment", parent="CLN")
# LOC
ruleset("LOC", "Locus specificity", "locus-specificity-assessment")
ruleset("LOC_PHE", "Phenotype specificity", "specific-phenotype-assessment", parent="LOC")
ruleset("LOC_SEG", "Co-segregation", "segregation-with-disease-assessment", parent="LOC")
# MIS (amino-acid path)
ruleset("MIS", "Missense variant", "missense-variant-assessment")
ruleset(
    "MIS_PRD", "Single-AA-change prediction", "single-aa-change-prediction-assessment", parent="MIS"
)
ruleset(
    "MIS_PRD_INIT_REVEL",
    "REVEL predictor initial points",
    "insilico-predictor-assessment",
    parent="MIS_PRD",
    params={"predictor": "REVEL"},
)
ruleset("MIS_PRD_EXON", "Exon relevance (missense)", "exon-relevance-assessment", parent="MIS_PRD")
ruleset("MIS_FXN", "Missense functional assay", "functional-assay-assessment", parent="MIS")
ruleset("MIS_INF", "Missense informative variants", "informative-variants-assessment", parent="MIS")
# NUL (NMD path)
ruleset("NUL", "Null / nonsense variant", "null-variant-assessment")
ruleset("NUL_PRD", "Null predictive", "null-predictive-assessment", parent="NUL")
ruleset("NUL_PRD_INIT", "NMD initial points", "fixed-initial-points-assessment", parent="NUL_PRD")
ruleset(
    "NUL_PRD_MECH_EXON",
    "Mechanism × exon (null)",
    "mechanism-exon-relevance-assessment",
    parent="NUL_PRD",
)
ruleset("NUL_FXN", "Null functional assay", "functional-assay-assessment", parent="NUL")
ruleset("NUL_INF", "Null informative variants", "informative-variants-assessment", parent="NUL")


# --------------------------------------------------------------------------- #
# example specialisation — override ONE node by id (same methodType, new scoped id)
# --------------------------------------------------------------------------- #

ruleset(
    "MIS_PRD_INIT_REVEL",
    "REVEL predictor initial points (MYH7-recalibrated)",
    "insilico-predictor-assessment",
    scope="gene-MYH7",
    params={"predictor": "REVEL(MYH7-recalibrated)", "calibration_thresholds": {"+4.0": ">=0.90"}},
)
