"""Reference (non-authoritative) scorers for Clinical Observations (SM 4, CLN codes).

The two benign per-Case codes: CLN_UAF (unaffected carrier, Table 5) and CLN_ALT (alternative
cause, Table 4). Scored per Case (one proband); the cross-proband sum, the CLN_CCS exclusivity
rule, and the CLN_AFF +1.0/proband ceiling live in the later case-aggregation increment.
"""

from __future__ import annotations

from svcv4_model.case import MOI, AgeMatchedPenetrance, Case, PhenoSeverity, Zygosity
from svcv4_model.scoring.result import ScoreResult

_RECESSIVE_XL = frozenset({MOI.AR, MOI.XLD, MOI.XLR})
_PEN_GT_80 = frozenset({AgeMatchedPenetrance.PCT_80_100, AgeMatchedPenetrance.NEAR_100})


def _classify_plp(classification: str | None) -> str | None:
    """Normalize the placeholder ``classification`` string to 'P' / 'LP' / None (else).

    ``AdditionalVariant``/``CompoundHetVariant`` carry ``classification`` as a placeholder str
    (not the ``VariantClassification`` enum -- a flagged model gap). Accepts the enum values
    (PATHOGENIC / LIKELY_PATHOGENIC) and the P / LP shorthands, case-insensitively.
    """
    if classification is None:
        return None
    c = classification.strip().upper()
    if c in {"P", "PATHOGENIC"}:
        return "P"
    if c in {"LP", "LIKELY_PATHOGENIC"}:
        return "LP"
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
            trans = _classify_plp(
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
    # _classify_plp returns truthy "P"/"LP" (or falsy None), so this keeps only P/LP alternates
    plp_alts = [v for v in case.additional_variants if _classify_plp(v.classification)]
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
