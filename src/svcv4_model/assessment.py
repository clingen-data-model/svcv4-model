"""Assessment registry — SVCv4 rulesets as a hierarchical method.

Two layers, deliberately separated:

- ``AssessmentType`` — a **pattern** (the general *type* of assessment). Its name
  is the ``methodType`` on an evidence-line ``Statement``. A pattern is **reusable**:
  the same pattern (e.g. ``functional-assay-assessment``) appears in many pathways.
- ``Ruleset`` — a **specific, registered ruleset**: one node of a workflow pathway,
  with a unique id ``svc-<scope>:<CODE>:<version>`` named for its SVCv4 code, its
  own configured ``params``, and a ``parent`` (its place in the hierarchy). A
  registered ruleset is **never reused** — each pathway node is its own id, even when
  two nodes share a ``method_type`` pattern (they may carry different values).

The whole **SVCv4 method** is therefore the tree of baseline ``Ruleset`` nodes; a
specialization overrides individual nodes by id (same ``method_type``, new scoped id).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from svcv4_model.config import (
    EXON_REL_LOF_V4,
    MIS_PRD_EXON_REL_V4,
    MIS_PRD_INIT_INSILICO_V4,
)

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

    id: str = Field(description="`svc-<scope>:<CODE>:<version>` — value of `specifiedBy.id`.")
    code: str = Field(description="The SVCv4 code this node produces, e.g. `MIS_PRD_EXON_REL`.")
    label: str = Field(description="Human method name for this exact pathway node.")
    method_type: str = Field(description="The AssessmentType (pattern) this instantiates.")
    scope: str = Field(description="`baseline` or a specialisation scope, e.g. `gene-MYH7`.")
    version: str = Field(default="4.0")
    parent: str | None = Field(default=None, description="Parent ruleset id (hierarchy).")
    params: dict[str, Any] = Field(default_factory=dict)
    provisional: bool = Field(
        default=False,
        description="True when this node's CODE is a provisional SVCv4 code/subcode "
        "(a combination-cap roll-up, or a deeper method-level subcode).",
    )
    description: str | None = None

    @field_validator("id")
    @classmethod
    def _id_shape(cls, v: str) -> str:
        if not (v.startswith("svc:") or v.startswith("svc-")) or v.count(":") != 2:
            raise ValueError(
                "Ruleset id must be 'svc:<CODE>:<version>' (baseline) or "
                "'svc-<scope>:<CODE>:<version>' (specialisation)"
            )
        return v


# --------------------------------------------------------------------------- #
# id helpers
# --------------------------------------------------------------------------- #


def make_ruleset_id(scope: str, code: str, version: str = "4.0") -> str:
    """Baseline ids are ``svc:<CODE>:<version>``; specialisations
    ``svc-<scope>:<CODE>:<version>``."""
    ns = "svc" if scope == "baseline" else f"svc-{scope}"
    return f"{ns}:{code}:{version}"


def parse_ruleset_id(rid: str) -> tuple[str, str, str]:
    ns, code, version = rid.split(":")
    scope = "baseline" if ns == "svc" else ns.removeprefix("svc-")
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
    version: str = "4.0",
    params: dict[str, Any] | None = None,
    provisional: bool = False,
    description: str | None = None,
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
        provisional=provisional,
        description=description,
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

_pat("svcv4-method-assessment", "SVCv4 classification method", "rollup", "points")
_pat("human-observational-data-assessment", "Human Observational Data (HOD)", "rollup", "points")
_pat(
    "predictive-functional-data-assessment",
    "Predictive & Functional Data (PRD)",
    "rollup",
    "points",
)
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
# Variant-impact router: reads the VBC molecular consequence and selects the family.
_pat(
    "variant-impact-router",
    "Variant-impact router (PFD family selection)",
    "router",
    "route",
    params=("route_map",),
    data_items=(_di("variant_type", "router", "VBC molecular_consequence, e.g. MISSENSE"),),
)
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
# ---- Predictive-initial SPECTRUM patterns (the OR branches under x_PRD_INIT_*) ---- #
# For a given variant one spectrum is selected; it produces the initial predictive
# points, which the exon-relevance adjuster then scales.
_pat(
    "insilico-predictor-assessment",
    "In-silico predictor spectrum (tool-agnostic)",
    "initial",
    "points",
    -4.0,
    4.0,
    # the TOOL is not in the code; the ruleset params configure the selectable set
    # of tools and each tool's band→points ranges.
    ("selectable_tools", "per_tool_bands", "selected_tool"),
    (_di("predictor", "input", "selected from configured set"), _di("raw_score", "input")),
)
_pat(
    "protein-impact-spectrum-assessment",
    "VBC protein-impact spectrum (_PROT_IMP) — SM9 frameshift-initial common pattern",
    "initial",
    "points",
    -1.0,
    6.0,
    # One common pattern spans all five SM9 (fig. 1) frameshift branches: the analyst
    # selects a single decay_pathway and reads points from the matching sub-table.
    #   NMD_NO_RESCUE (yellow)   → decay=nmd,            100% loss  → +6.0 (fixed)
    #   NON_STOP_DECAY (green)   → decay=non_stop_decay, 100% loss  → +4.0 (fixed)
    #   NO_NMD (violet)          → decay=no_nmd,         fraction   → 0..+6 (fraction_table)
    #   NMD_WITH_RESCUE (orange) → decay=nmd + rescue               → −1..+6 (hands to alt-start)
    #   PROTEIN_EXTENSION(green) → decay=extension,      length     → 0..+4 (extension_table)
    # NMD-100% and non-stop-decay-100% are the same "removes 100% of protein" outcome,
    # differing only by the configured per-pathway award.
    ("pathway_awards", "fraction_table", "extension_table"),
    (
        _di("decay_pathway", "input", "nmd | non_stop_decay | no_nmd | extension"),
        _di("protein_fraction_lost", "input", "1.0 ⇒ 100% removed (truncation axis)"),
        _di("extension_length_aa", "input", "non-native C-terminal extension"),
        _di("alt_met_rescue", "input", "routes NMD → with/without rescue"),
        _di("critical_domain_loss", "input", "SM7 alternative axis (deferred)"),
    ),
)
_pat(
    "alt-start-impact-spectrum-assessment",
    "Alternate start-codon impact spectrum (_ALT_START_IMP)",
    "initial",
    "points",
    0.0,
    6.0,
    ("tier_points",),
    (
        _di("alt_start_present", "input"),
        _di("alt_start_proven", "input", "proven | unproven"),
        _di("position_downstream_of_vbc", "input"),
    ),
)
_pat(
    "alt-start-rescue-assessment",
    "Alternate in-frame-start functional rescue (_ALT_START_FXN)",
    "initial",
    "points",
    -1.0,
    0.0,
    # one-off: functional data shows a shorter protein from a downstream in-frame
    # start retains function vs full-length → benign-leaning.
    ("award",),
    (
        _di("alt_met_functional_rescue", "input", "retains function vs full length"),
        _di("no_plp_between_starts", "input"),
    ),
)
_pat(
    "molecular-mechanism-spectrum-assessment",
    "Region alteration on molecular mechanism spectrum (_MECH_IMP)",
    "initial",
    "points",
    -1.0,
    6.0,
    ("tier_points",),
    (
        _di("gencc_mechanism", "input", "Established/Likely/Suspected/Uncertain"),
        _di("region_alteration", "input"),
        _di("mechanism_match", "input"),
    ),
)
_pat(
    "exon-relevance-assessment",
    "Exon / transcript relevance adjuster (_EXON_REL)",
    "adjuster",
    "multiplier",
    0.0,
    1.0,
    # tier matrix; only_positive (apply weighting to positive points only); and zero
    # or more mechanism-classification types (e.g. LOF) each with weighted values.
    ("tier_multipliers", "only_positive", "mechanism_bands"),
    (
        _di("initial_points", "input", "the points being scaled"),
        _di("exon_relevance", "input", "All/Most/Few"),
        _di("mane_status", "gate"),
        _di("mechanism_type", "input", "optional — required when a mechanism type is configured"),
        _di("mechanism_class", "input", "optional — the classification value for that type"),
    ),
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
_pat("coding-sequence-variant-assessment", "Coding-sequence variant (CDS)", "rollup", "points")
_pat(
    "coding-sequence-prediction-assessment",
    "Coding-sequence prediction (CDS_PRD)",
    "rollup",
    "points",
    -1.0,
    6.0,
)
_pat("splice-variant-assessment", "Splice variant (SPL)", "rollup", "points")
_pat(
    "splice-predictive-assessment",
    "Splice predictive roll-up (SPL_PRD)",
    "rollup",
    "points",
    0.0,
    6.0,
)


_pat(
    "predictive-functional-combination-assessment",
    "Predictive + functional combination cap (x_PRD_FXN)",
    "rollup",
    "points",
)
_pat(
    "predictive-spliceassay-combination-assessment",
    "Splice prediction + assay combination cap (SPL_PRD_SPA)",
    "rollup",
    "points",
)


_pat(
    "case-count-grouping-assessment",
    "Case-count grouping (n x per-case)",
    "initial",
    "points",
    params=("per_case_points", "cap"),
    data_items=(
        _di("case_group", "input", "the grouping cell (specificity x testing x ...)"),
        _di("count", "input", "n unrelated cases/observations in this group"),
    ),
)
_pat("moi-table-subtotal-assessment", "MOI/config subtotal roll-up", "rollup", "points")
_pat(
    "band-selection-assessment",
    "Single-value band selection",
    "initial",
    "points",
    params=("band_thresholds",),
    data_items=(_di("value", "input", "the banded value"),),
)


# --------------------------------------------------------------------------- #
# baseline rulesets (the SVCv4 method as a hierarchy) — parent-first
# --------------------------------------------------------------------------- #

# SVCV4 — the whole method: the top-level classification Statement's specifiedBy.
ruleset("SVCV4", "SVCv4 classification method", "svcv4-method-assessment")
ruleset("HOD", "Human Observational Data", "human-observational-data-assessment", parent="SVCV4")
ruleset(
    "PFD", "Predictive & Functional Data", "predictive-functional-data-assessment", parent="SVCV4"
)
# POP
ruleset("POP", "Population observations", "population-observation-assessment", parent="HOD")
ruleset("POP_FRQ", "Population allele frequency", "population-frequency-assessment", parent="POP")
ruleset(
    "POP_HMZ",
    "Homozygote/hemizygote burden",
    "population-observation-homo-hemizygote-assessment",
    parent="POP",
)
# CLN
ruleset("CLN", "Clinical observations", "clinical-observation-assessment", parent="HOD")
ruleset("CLN_AFF", "Affected proband", "affected-observation-assessment", parent="CLN")
ruleset("CLN_UAF", "Unaffected carrier", "unaffected-observation-assessment", parent="CLN")
ruleset("CLN_ALT", "Alternative cause", "affected-alternative-observation-assessment", parent="CLN")
ruleset("CLN_DNV", "De-novo occurrence", "affected-denovo-observation-assessment", parent="CLN")
ruleset("CLN_CCS", "Case-control study", "case-control-observation-assessment", parent="CLN")
# LOC
ruleset("LOC", "Locus specificity", "locus-specificity-assessment", parent="HOD")
ruleset("LOC_PHE", "Phenotype specificity", "specific-phenotype-assessment", parent="LOC")
ruleset("LOC_SEG", "Co-segregation", "segregation-with-disease-assessment", parent="LOC")

# --- HOD sub-assessments: group similar cases -> n x per-case multiplier (SM 3/4/5) ---
# band-selection leaves (single value -> band)
for _c, _p in [
    ("POP_FRQ_NONE", "POP_FRQ"),
    ("POP_FRQ_SUPP", "POP_FRQ"),
    ("POP_FRQ_MOD", "POP_FRQ"),
    ("POP_FRQ_STRG", "POP_FRQ"),
    ("LOC_PHE_NONE", "LOC_PHE"),
    ("LOC_PHE_LOW", "LOC_PHE"),
    ("LOC_PHE_MOD", "LOC_PHE"),
    ("LOC_PHE_HIGH", "LOC_PHE"),
    ("LOC_PHE_FULL", "LOC_PHE"),
]:
    ruleset(
        _c, _c.replace("_", " ").title(), "band-selection-assessment", parent=_p, provisional=True
    )
# subtotals (roll up their cells)
for _c, _lab, _p in [
    ("CLN_AFF_MONO", "Monoallelic subtotal (Table 1)", "CLN_AFF"),
    ("CLN_AFF_BIAL", "Biallelic subtotal (Table 2)", "CLN_AFF"),
    ("CLN_ALTV", "Alternative variant cause", "CLN_ALT"),
    ("CLN_ALTG", "Alternative gene cause", "CLN_ALT"),
]:
    ruleset(_c, _lab, "moi-table-subtotal-assessment", parent=_p, provisional=True)
# case-count grouping cells (n x per-case)
for _c, _p in [
    ("POP_HMZ_DOM", "POP_HMZ"),
    ("POP_HMZ_OTH", "POP_HMZ"),
    ("CLN_AFF_MONO_SPEC_THOR", "CLN_AFF_MONO"),
    ("CLN_AFF_MONO_SPEC_LIM", "CLN_AFF_MONO"),
    ("CLN_AFF_MONO_CONS_THOR", "CLN_AFF_MONO"),
    ("CLN_AFF_MONO_CONS_LIM", "CLN_AFF_MONO"),
    ("CLN_AFF_MONO_ALT", "CLN_AFF_MONO"),
    ("CLN_AFF_MONO_UAF", "CLN_AFF_MONO"),
    ("CLN_AFF_BIAL_RARE_CTP", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_RARE_CTV", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_RARE_ATP", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_INCP_CTP", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_INCP_CTV", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_INCP_ATP", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_INCP_HOM", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_UNCM_CTP", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_UNCM_CTV", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_UNCM_ATP", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_THOR_HOM", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_ALT", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_UAF", "CLN_AFF_BIAL"),
    ("CLN_AFF_BIAL_NON", "CLN_AFF_BIAL"),
    ("CLN_DNV_SPEC_CONF", "CLN_DNV"),
    ("CLN_DNV_SPEC_UNCONF", "CLN_DNV"),
    ("CLN_DNV_CONS_CONF", "CLN_DNV"),
    ("CLN_DNV_CONS_UNCONF", "CLN_DNV"),
    ("CLN_DNV_INCON", "CLN_DNV"),
    ("CLN_UAF_FULL_HIGH", "CLN_UAF"),
    ("CLN_UAF_FULL_NEAR", "CLN_UAF"),
    ("CLN_UAF_LOW", "CLN_UAF"),
    ("CLN_UAF_NON", "CLN_UAF"),
    ("CLN_ALTV_ONE", "CLN_ALTV"),
    ("CLN_ALTV_BOTH", "CLN_ALTV"),
    ("CLN_ALTV_REC", "CLN_ALTV"),
    ("CLN_ALTG_ONE", "CLN_ALTG"),
    ("CLN_ALTG_BOTH", "CLN_ALTG"),
    ("LOC_SEG_AFF", "LOC_SEG"),
    ("LOC_SEG_UAF", "LOC_SEG"),
    ("LOC_SEG_UAF_AR", "LOC_SEG"),
    ("LOC_SEG_NONSEG", "LOC_SEG"),
]:
    ruleset(
        _c,
        _c.replace("_", " ").title(),
        "case-count-grouping-assessment",
        parent=_p,
        provisional=True,
    )
# PFD variant-impact router — reads the VBC molecular consequence and selects ONE
# family lane. Missense → MIS (unambiguous); the LoF-ish consequences name a
# candidate {NUL, CDS} set that a branch inside that variant-type workflow resolves.
ruleset(
    "PFD_ROUTER",
    "Variant-impact router",
    "variant-impact-router",
    parent="PFD",
    provisional=True,
    params={
        "route_map": {
            "MISSENSE": ["MIS"],
            "NONSENSE": ["NUL", "CDS"],
            "FRAMESHIFT": ["NUL", "CDS"],
            "INFRAME_INDEL": ["CDS"],
            "START_LOST": ["NUL", "CDS"],
            "STOP_LOST": ["NUL", "CDS"],
            "SPLICE": ["SPL"],
            "EXON_DELETION": ["NUL", "CDS"],
            "EXON_DUPLICATION": ["NUL", "CDS"],
            "INTRONIC": ["SPL"],
            "SYNONYMOUS": ["SPL"],
        }
    },
    description=(
        "Selects the PFD variant-impact family from the VBC molecular consequence "
        "(VBC.molecular_consequence). MISSENSE → MIS; SPLICE/INTRONIC/SYNONYMOUS → SPL; "
        "INFRAME_INDEL → CDS; the remaining LoF-type consequences route to a candidate "
        "{NUL, CDS} set that the variant-type workflow's own branch (NMD / non-stop decay "
        "/ alt-start / whole-gene) resolves to one lane. Provisional modeling node — the "
        "routing is implicit in the SM flow diagrams, not an official SVCv4 code."
    ),
)
# MIS: MIS = (MIS_PRD + MIS_FXN -> MIS_PRD_FXN) + MIS_INF
ruleset("MIS", "Missense variant", "missense-variant-assessment", parent="PFD_ROUTER")
ruleset(
    "MIS_PRD_FXN",
    "Missense predictive + functional (combination cap)",
    "predictive-functional-combination-assessment",
    parent="MIS",
    provisional=True,
)
ruleset(
    "MIS_PRD",
    "Single-AA-change prediction",
    "single-aa-change-prediction-assessment",
    parent="MIS_PRD_FXN",
)
# MIS init spectrum: in-silico predictor only (tool selected in params, not the code).
# Missense predictors already capture mechanism, so no _MECH_IMP here and EXON_REL is
# configured WITHOUT the gene-disease mechanism data.
ruleset(
    "MIS_PRD_INIT_INSILICO",
    "In-silico predictor initial points",
    "insilico-predictor-assessment",
    parent="MIS_PRD",
    params=MIS_PRD_INIT_INSILICO_V4.model_dump(exclude_none=True),
    provisional=True,
    description=(
        "Missense in-silico predictor — initial predictive points (SM 6, Fig 2). For a "
        "missense VBC the analyst selects one ClinGen-approved calibrated predictor in "
        "advance; its raw score maps through that tool's calibration table (per_tool_bands) "
        "to an initial point value (−4 benign … +4 pathogenic). These points feed MIS_PRD "
        "and are then scaled by MIS_PRD_EXON_REL. Missense only. A specialisation may "
        "recalibrate a tool's bands, narrow selectable_tools, or pin selected_tool."
    ),
)
ruleset(
    "MIS_PRD_EXON_REL",
    "Exon relevance (missense)",
    "exon-relevance-assessment",
    parent="MIS_PRD",
    params=MIS_PRD_EXON_REL_V4.model_dump(),
    provisional=True,
    description=(
        "Exon relevance (missense) — a multiplier (SM 6, Fig 2 matrix) scaling the initial "
        "predictive points by how many clinically-relevant transcripts contain the exon(s) "
        "harbouring the VBC: All=1.0, Most=0.5, Few=0.0. MIS_PRD = MIS_PRD_INIT × this "
        "multiplier. Missense configures NO mechanism type (predictors already capture "
        "mechanism); only_positive scales positive points only. A specialisation may "
        "re-weight the tiers."
    ),
)
ruleset("MIS_FXN", "Missense functional assay", "functional-assay-assessment", parent="MIS_PRD_FXN")
ruleset("MIS_INF", "Missense informative variants", "informative-variants-assessment", parent="MIS")
# NUL: NUL = (NUL_PRD + NUL_FXN -> NUL_PRD_FXN) + NUL_INF
ruleset("NUL", "Null / nonsense variant", "null-variant-assessment", parent="PFD_ROUTER")
ruleset(
    "NUL_PRD_FXN",
    "Null predictive + functional (combination cap)",
    "predictive-functional-combination-assessment",
    parent="NUL",
    provisional=True,
)
ruleset("NUL_PRD", "Null predictive", "null-predictive-assessment", parent="NUL_PRD_FXN")
# NUL init spectra (OR-selected): protein-impact, alt-start, alt-start functional
# rescue, molecular-mechanism. PROT_IMP's decay_pathway spans the equivalent
# 100%-loss cases (NMD-predicted and non-stop-decay-predicted).
ruleset(
    "NUL_PRD_INIT_PROT_IMP",
    "Protein-impact spectrum (null)",
    "protein-impact-spectrum-assessment",
    parent="NUL_PRD",
    provisional=True,
)
ruleset(
    "NUL_PRD_INIT_ALT_START_IMP",
    "Alternate start-codon impact (null)",
    "alt-start-impact-spectrum-assessment",
    parent="NUL_PRD",
    provisional=True,
)
ruleset(
    "NUL_PRD_INIT_ALT_START_FXN",
    "Alt in-frame-start functional rescue (null)",
    "alt-start-rescue-assessment",
    parent="NUL_PRD",
    provisional=True,
)
ruleset(
    "NUL_PRD_INIT_MECH_IMP",
    "Molecular-mechanism impact spectrum (null)",
    "molecular-mechanism-spectrum-assessment",
    parent="NUL_PRD",
    provisional=True,
)
ruleset(
    "NUL_PRD_EXON_REL",
    "Exon relevance (null)",
    "exon-relevance-assessment",
    parent="NUL_PRD",
    params=EXON_REL_LOF_V4.model_dump(),
    provisional=True,
)
ruleset("NUL_FXN", "Null functional assay", "functional-assay-assessment", parent="NUL_PRD_FXN")
ruleset("NUL_INF", "Null informative variants", "informative-variants-assessment", parent="NUL")
# CDS: CDS = (CDS_PRD + CDS_FXN -> CDS_PRD_FXN) + CDS_INF
ruleset("CDS", "Coding-sequence variant", "coding-sequence-variant-assessment", parent="PFD_ROUTER")
ruleset(
    "CDS_PRD_FXN",
    "CDS predictive + functional (combination cap)",
    "predictive-functional-combination-assessment",
    parent="CDS",
    provisional=True,
)
ruleset(
    "CDS_PRD",
    "Coding-sequence prediction",
    "coding-sequence-prediction-assessment",
    parent="CDS_PRD_FXN",
)
# CDS init spectra (OR-selected): in-frame indels carry an indel in-silico predictor;
# start/stop-lost use protein-impact / alt-start / functional-rescue; plus mechanism.
ruleset(
    "CDS_PRD_INIT_INSILICO",
    "In-silico indel predictor initial points (CDS)",
    "insilico-predictor-assessment",
    parent="CDS_PRD",
    params={"selectable_tools": ["indel_predictor", "OTHER_CALIBRATED"]},
    provisional=True,
)
ruleset(
    "CDS_PRD_INIT_PROT_IMP",
    "Protein-impact spectrum (CDS)",
    "protein-impact-spectrum-assessment",
    parent="CDS_PRD",
    provisional=True,
)
ruleset(
    "CDS_PRD_INIT_ALT_START_IMP",
    "Alternate start-codon impact (CDS)",
    "alt-start-impact-spectrum-assessment",
    parent="CDS_PRD",
    provisional=True,
)
ruleset(
    "CDS_PRD_INIT_ALT_START_FXN",
    "Alt in-frame-start functional rescue (CDS)",
    "alt-start-rescue-assessment",
    parent="CDS_PRD",
    provisional=True,
)
ruleset(
    "CDS_PRD_INIT_MECH_IMP",
    "Molecular-mechanism impact spectrum (CDS)",
    "molecular-mechanism-spectrum-assessment",
    parent="CDS_PRD",
    provisional=True,
)
ruleset(
    "CDS_PRD_EXON_REL",
    "Exon relevance (CDS)",
    "exon-relevance-assessment",
    parent="CDS_PRD",
    params=EXON_REL_LOF_V4.model_dump(),
    provisional=True,
)
ruleset("CDS_FXN", "CDS functional assay", "functional-assay-assessment", parent="CDS_PRD_FXN")
ruleset("CDS_INF", "CDS informative variants", "informative-variants-assessment", parent="CDS")
# SPL: SPL = (SPL_PRD + SPL_SPA -> SPL_PRD_SPA) + SPL_FXN -> SPL_PRD_SPA_FXN
ruleset("SPL", "Splice variant", "splice-variant-assessment", parent="PFD_ROUTER")
ruleset(
    "SPL_PRD_SPA_FXN",
    "Splice (pred+assay) + functional (combination cap)",
    "predictive-functional-combination-assessment",
    parent="SPL",
    provisional=True,
)
ruleset(
    "SPL_PRD_SPA",
    "Splice prediction + assay (combination cap)",
    "predictive-spliceassay-combination-assessment",
    parent="SPL_PRD_SPA_FXN",
    provisional=True,
)
ruleset("SPL_PRD", "Splice predictive", "splice-predictive-assessment", parent="SPL_PRD_SPA")
# SPL init spectra (OR-selected): splice predictor + molecular-mechanism.
ruleset(
    "SPL_PRD_INIT_SPLICE",
    "Splice-prediction spectrum",
    "splice-prediction-assessment",
    parent="SPL_PRD",
    provisional=True,
)
ruleset(
    "SPL_PRD_INIT_MECH_IMP",
    "Molecular-mechanism impact spectrum (splice)",
    "molecular-mechanism-spectrum-assessment",
    parent="SPL_PRD",
    provisional=True,
)
ruleset(
    "SPL_PRD_EXON_REL",
    "Exon relevance (splice)",
    "exon-relevance-assessment",
    parent="SPL_PRD",
    params=EXON_REL_LOF_V4.model_dump(),
    provisional=True,
)
ruleset("SPL_SPA", "Splice assay", "splice-assay-assessment", parent="SPL_PRD_SPA")
ruleset(
    "SPL_FXN", "Splice functional assay", "functional-assay-assessment", parent="SPL_PRD_SPA_FXN"
)
# Frameshift, exon del/dup, start/stop-lost route into the NUL / CDS trees above —
# they add no new code families, only variant-type entry points, and select among the
# x_PRD_INIT_* spectra (protein-impact, alt-start, mechanism) per pathway.


# --------------------------------------------------------------------------- #
# example specialisation — override ONE node by id (same methodType, new scoped id)
# --------------------------------------------------------------------------- #

ruleset(
    "MIS_PRD_INIT_INSILICO",
    "In-silico predictor initial points (MYH7-recalibrated)",
    "insilico-predictor-assessment",
    scope="gene-MYH7",
    params={
        # narrow the menu to the gene's validated predictor and pin it,
        "selectable_tools": ["REVEL"],
        "selected_tool": "REVEL",
        # then recalibrate REVEL's bands for MYH7 (illustrative thresholds).
        # Contiguous half-open bands — must cover [-inf, +inf] with no gap/overlap.
        "per_tool_bands": {
            "REVEL": [
                {"points": -1.0, "min": None, "max": 0.500},
                {"points": 0.0, "min": 0.500, "max": 0.700},
                {"points": 2.0, "min": 0.700, "max": 0.900},
                {"points": 4.0, "min": 0.900, "max": None},
            ]
        },
    },
    description=(
        "Gene-MYH7 recalibration of the missense in-silico initial-points code: same "
        "code and methodType as the baseline, but the selectable set is narrowed to REVEL "
        "and REVEL's bands are re-thresholded for MYH7. Demonstrates modifying a baseline "
        "configuration in a separate namespace without minting a new code."
    ),
)
