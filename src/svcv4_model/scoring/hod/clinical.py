"""Reference (non-authoritative) scorers for Clinical Observations (SM 4, CLN codes).

The two benign per-Case codes: CLN_UAF (unaffected carrier, Table 5) and CLN_ALT (alternative
cause, Table 4). Scored per Case (one proband); the cross-proband sum, the CLN_CCS exclusivity
rule, and the CLN_AFF +1.0/proband ceiling live in the later case-aggregation increment.
"""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AgeMatchedPenetrance,
    Case,
    CoOccurrenceLikelihood,
    PhaseConfidence,
    PhenoSeverity,
    PhenoSpecificity,
    TriState,
    Zygosity,
)
from svcv4_model.scoring.result import ScoreResult

_RECESSIVE_XL = frozenset({MOI.AR, MOI.XLD, MOI.XLR})
_PEN_GT_80 = frozenset({AgeMatchedPenetrance.PCT_80_100, AgeMatchedPenetrance.NEAR_100})


def _classify(classification: str | None) -> str | None:
    """Normalize the placeholder ``classification`` string to a category, or None.

    Returns 'P' / 'LP' / 'VUS' / 'B' / 'LB' (or None). ``AdditionalVariant`` /
    ``CompoundHetVariant`` carry ``classification`` as a placeholder str (not the
    ``VariantClassification`` enum -- a flagged model gap). Accepts the enum values
    (PATHOGENIC / LIKELY_PATHOGENIC / VUS / BENIGN / LIKELY_BENIGN) and the P / LP / VUS / B / LB
    shorthands, case-insensitively. (Keep in sync with VariantClassification if that enum changes.)
    """
    if classification is None:
        return None
    c = classification.strip().upper()
    if c in {"P", "PATHOGENIC"}:
        return "P"
    if c in {"LP", "LIKELY_PATHOGENIC"}:
        return "LP"
    if c == "VUS":
        return "VUS"
    if c in {"B", "BENIGN"}:
        return "B"
    if c in {"LB", "LIKELY_BENIGN"}:
        return "LB"
    return None


def reference_score_cln_uaf(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_UAF benignity for one unaffected Case (SM 4
    Table 5). CSpec is authoritative. ``moi`` is required (picks the table column). Benignity-only.
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (cross-proband sum + CLN_CCS '
        "exclusivity deferred to case aggregation)."
    ]
    pen = case.age_matched_penetrance

    col: str | None = None
    if moi in {MOI.AD, MOI.SD}:
        col = "dom"
    elif moi in _RECESSIVE_XL:
        z = case.vbc_zygosity
        if z in {Zygosity.HOM, Zygosity.HEMI}:
            col = "rec_homo_hemi"
        elif z == Zygosity.HET:
            trans = _classify(
                case.compound_het_variant.classification if case.compound_het_variant else None
            )
            col = {"P": "rec_trans_p", "LP": "rec_trans_lp"}.get(trans, "no_trans_plp")
        # z None -> col stays None -> _ND

    if col is None:
        prov.append("CLN_UAF: _ND (moi unknown, or recessive/XL VBC zygosity unknown)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    if col == "no_trans_plp":
        pts = 0.0
        prov.append("CLN_UAF: 0.0 (recessive/XL HET, no confirmed-trans P/LP -- SM 4 L203)")
    else:
        reduced = col == "rec_trans_lp"
        if pen == AgeMatchedPenetrance.NEAR_100:
            pts = -2.0 if reduced else -4.0
        elif pen == AgeMatchedPenetrance.PCT_80_100:
            pts = -1.0 if reduced else -2.0
        else:  # LT_80 or None -> SM 4 L203: unknown/low penetrance -> no points
            pts = 0.0
        prov.append(f"CLN_UAF: {pts} (col={col}, penetrance={pen})")

    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_UAF": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )


def reference_score_cln_alt(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_ALT benignity for one affected Case whose
    phenotype is explained by a P/LP alternate cause (SM 4 Table 4). CSpec is authoritative.
    ``moi`` accepted for signature parity with the other CLN scorers (not consumed). Benignity-only.
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (cross-proband sum deferred).'
    ]
    # _classify now also returns truthy VUS/B/LB, so gate explicitly on P/LP (not truthiness)
    plp_alts = [v for v in case.additional_variants if _classify(v.classification) in {"P", "LP"}]
    if not plp_alts:
        prov.append("CLN_ALT: _ND (no P/LP alternate-cause variant -- Table 4 gate)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    sev = case.pheno_severity
    if sev is None:
        prov.append("CLN_ALT: _ND (no pheno_severity)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    if sev == PhenoSeverity.MONO_GT_OR_BIALLELIC_EQ_EXPECTED:
        pts = 0.0
    elif sev == PhenoSeverity.MONO_EQ_EXPECTED:
        pts = -0.5
    else:  # BIALLELIC_LT_EXPECTED: -1.0 only if same-gene (ALTV) AND penetrance >80%
        same_gene = any(v.phase_in_ref_to_vbc is not None for v in plp_alts)
        pen_gt_80 = case.age_matched_penetrance in _PEN_GT_80
        pts = -1.0 if (same_gene and pen_gt_80) else 0.0
        prov.append(
            f"CLN_ALT BIALLELIC_LT_EXPECTED: same_gene={same_gene}, "
            f"penetrance>80%={pen_gt_80} (>80% = PCT_80_100/NEAR_100; SM 4 L198-200)"
        )
    prov.append(f"CLN_ALT: {pts} (pheno_severity={sev}; 'in expected zygosity' trusted to input)")

    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_ALT": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )


_CLN_AFF_POINTS = {
    PhenoSpecificity.SPECIFIC: {"best": 1.0, "middle": 0.5, "plp_alt": 0.0},
    PhenoSpecificity.CONSISTENT: {"best": 0.5, "middle": 0.25, "plp_alt": 0.0},
}


def reference_score_cln_aff_mono(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_AFF pathogenic points for one affected
    monoallelic proband (SM 4 Table 1). CSpec is authoritative. ``moi`` accepted for signature
    parity (Table 1 has no MOI axis; table selection/routing is deferred to aggregation).
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (table selection + cross-proband '
        "sum + the AD +1.0/proband ceiling-on-sum deferred to case aggregation)."
    ]
    pheno = case.pheno_specificity_for_mde
    if pheno is None:
        prov.append("CLN_AFF: _ND (no pheno_specificity_for_mde)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    if pheno == PhenoSpecificity.INCONSISTENT:
        pts = 0.0
        prov.append("CLN_AFF: 0.0 (phenotype INCONSISTENT -- SM 4 Table 1; -> CLN_UAF)")
    else:  # SPECIFIC or CONSISTENT
        cats = {_classify(v.classification) for v in case.additional_variants}
        t = case.testing
        thorough = (
            t is not None
            and t.covers_all_genes_relevant_to_mde == TriState.TRUE
            and t.non_genetic_etiology_excluded == TriState.TRUE
        )
        if cats & {"P", "LP"}:
            tier = "plp_alt"
        elif thorough and "VUS" not in cats:
            tier = "best"
        else:
            tier = "middle"
        pts = _CLN_AFF_POINTS[pheno][tier]
        prov.append(f"CLN_AFF: {pts} (phenotype={pheno}, tier={tier})")

    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_AFF": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )


_TABLE2 = {
    "A1": {"conf_plp": 3.0, "assumed_plp": 1.5, "conf_vus": 1.5, "hom": 1.0, "none": 0.0},
    "A2": {"conf_plp": 2.0, "assumed_plp": 1.0, "conf_vus": 1.0, "hom": 1.0, "none": 0.0},
    "B": {"conf_plp": 1.0, "assumed_plp": 0.75, "conf_vus": 0.5, "hom": 0.5, "none": 0.0},
    "zero": {"conf_plp": 0.0, "assumed_plp": 0.0, "conf_vus": 0.0, "hom": 0.0, "none": 0.0},
}


def _biallelic_column(case: Case) -> str | None:
    """SM 4 Table 2 column from the 2nd-variant status. None -> _ND (indeterminate zygosity)."""
    z = case.vbc_zygosity
    if z == Zygosity.HOM:
        return "hom"
    if z != Zygosity.HET:
        return None  # None or HEMI (hemizygous is Table 1, not biallelic) -> _ND
    ch = case.compound_het_variant
    if ch is None:
        return "none"  # no in-trans 2nd variant
    cls = _classify(ch.classification)
    if cls in {"P", "LP"}:
        # CompoundHetVariant asserts in-trans by construction; HIGH = confirmed, else assumed
        return "conf_plp" if ch.phase_confidence == PhaseConfidence.HIGH else "assumed_plp"
    if cls == "VUS":
        # only a confirmed-trans VUS scores; assumed-trans VUS = no points (SM 4 L75)
        return "conf_vus" if ch.phase_confidence == PhaseConfidence.HIGH else "none"
    return "none"


def reference_score_cln_aff_biallelic(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_AFF pathogenic points for one affected
    biallelic proband (SM 4 Table 2). CSpec is authoritative. ``moi`` accepted for signature
    parity (Table 2 has no MOI axis; table selection/routing is deferred to aggregation).
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label; scored per Case (table selection + cross-proband '
        "sum + the AD ceiling-on-sum deferred to case aggregation)."
    ]
    pheno = case.pheno_specificity_for_mde
    if pheno is None:
        prov.append("CLN_AFF: _ND (no pheno_specificity_for_mde)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    col = _biallelic_column(case)
    if col is None:
        prov.append("CLN_AFF: _ND (VBC zygosity absent or hemizygous -- not a Table 2 column)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    cats = {_classify(v.classification) for v in case.additional_variants}
    if pheno == PhenoSpecificity.INCONSISTENT:
        row = "zero"
    elif cats & {"P", "LP"}:
        row = "zero"  # a P/LP alt cause -> CLN_ALT (SM 4 Table 2 row C)
    else:
        t = case.testing
        thorough = (
            t is not None
            and t.covers_all_genes_relevant_to_mde == TriState.TRUE
            and t.non_genetic_etiology_excluded == TriState.TRUE
            and "VUS" not in cats
        )
        if not thorough:
            row = "B"
        elif col == "hom":
            row = "A1"  # co-occurrence N/A for a homozygous variant (A1.hom == A2.hom)
        else:
            ch = case.compound_het_variant
            co = ch.co_occurrence_likelihood if ch else None
            if co == CoOccurrenceLikelihood.LT_0_0001:
                row = "A1"
            elif co == CoOccurrenceLikelihood.BETWEEN_0_0001_0_01:
                row = "A2"
            else:
                row = "B"  # rarity unestablished -> incomplete row

    pts = _TABLE2[row][col]
    prov.append(f"CLN_AFF: {pts} (biallelic Table 2, column={col}, row={row})")
    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_AFF": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )
