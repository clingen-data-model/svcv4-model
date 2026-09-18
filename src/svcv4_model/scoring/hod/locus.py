"""Reference (non-authoritative) scorers for Locus specificity (SM 5): LOC_PHE + LOC_SEG.

LOC_PHE = phenotype specificity / diagnostic yield (SM 5 Figure 1). LOC_SEG = co-segregation
(SM 5 Figure 2, resolved 2026-09-18 -- per-co-segregation point tiers by MOI). The combined
LOC +4.0 cap is applied in case aggregation (``reference_aggregate_loc``). CSpec is
authoritative. ``parent_code="LOC"`` is a display/grouping label (not an SVCv4 parent code);
``parent_total`` is the recorded code value.
"""

from __future__ import annotations

import re

from svcv4_model.case import MOI, AgeMatchedPenetrance, Case, TriState, Zygosity
from svcv4_model.scoring.primitives import cap
from svcv4_model.scoring.result import ScoreResult

_NUM = re.compile(r"[0-9]*\.?[0-9]+")
_RULE_B_SUPPRESSED = frozenset({MOI.AR})  # None also suppresses rule (b)

_SEG_CAP_HI = 4.0  # LOC_SEG summed co-segregations cap (SM 5 L38)
_SEG_FLIP = -4.0  # non-segregation benign flip (SM 5 Figure 2)
_X_LINKED = frozenset({MOI.XLD, MOI.XLR})
_NONSEG_FLIP_MOI = frozenset({MOI.AD, MOI.XLD, MOI.XLR})  # + AR only when homozygous


def _parse_percent(raw: str | None) -> float | None:
    """First numeric token of a yield string as a percent, or None if none found.

    Clean point estimates ('90%', '2.6%') and the LOWER bound of a range ('91-93%' -> 91.0). A
    leading '<' is honored as "just below" (SM 5's idiomatic '<33%' -> band 0.0, not +1.0); a
    leading '>' keeps the number as a conservative floor. A bare proportion with no '%' and a
    value below 1.0 ('0.9' -> 90.0) is scaled to a percent -- but '0.5%' (an explicit sub-1
    percent) and '1 in 500' (a ratio parsing to 1.0, not < 1) are left as-is. The raw string is
    echoed in provenance.
    """
    if raw is None:
        return None
    m = _NUM.search(raw)
    if m is None:
        return None
    pct = float(m.group())
    if "%" not in raw and pct < 1.0:
        pct *= 100.0
    if raw.lstrip().startswith("<"):
        pct -= 1e-9
    return pct


def _loc_phe_band(pct: float) -> float:
    """SM 5 Figure 1 phenotype-specificity points. The +2.0 band and the (81,82) sliver are
    inferred (SM 5 gives no explicit anchor) -- see known-gaps.md."""
    if pct < 33.0:
        return 0.0
    if pct <= 50.0:
        return 1.0
    if pct < 68.0:
        return 2.0
    if pct < 82.0:
        return 3.0
    return 4.0


def _non_segregation(case: Case, *, moi: MOI | None) -> list[str]:
    """Reasons (one per triggering relative) a non-segregation was observed; empty if none.

    Two-case rule (MOI-gated): (a) affected + VBC-absent (MOI-independent); (b) unaffected
    VBC-carrier at NEAR_100 penetrance, suppressed for AR and moi None. Uses ``==``/``!=`` so
    UNKNOWN/None never trigger.
    """
    reasons: list[str] = []
    rule_b_ok = moi is not None and moi not in _RULE_B_SUPPRESSED
    near_100 = case.age_matched_penetrance == AgeMatchedPenetrance.NEAR_100
    for i, r in enumerate(case.relatives):
        if r.affected_w_mde == TriState.TRUE and r.vbc_exists == TriState.FALSE:
            reasons.append(f"relative[{i}] affected but VBC-absent (rule a)")
        elif (
            rule_b_ok
            and near_100
            and r.affected_w_mde == TriState.FALSE
            and r.vbc_exists == TriState.TRUE
        ):
            reasons.append(f"relative[{i}] unaffected VBC-carrier at ~100% penetrance (rule b)")
    return reasons


def reference_score_loc_phe(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) LOC_PHE phenotype-specificity points (SM 5).

    CSpec is authoritative. Bands ``testing.diagnostic_yield_for_phenotypes`` (SM 5 Figure 1),
    then zeroes on an observed non-segregation. ``moi`` is required for signature parity but is
    consumed ONLY for the AR non-segregation gate -- the band itself has no MOI axis.
    LOC_SEG and the combined LOC +4.0 cap are deferred to LOC-2 / case aggregation.
    """
    prov: list[str] = [
        'LOC: "LOC" is the HOD grouping label. LOC_SEG (co-segregation) and the combined '
        "LOC +4.0 cap are computed in LOC-2 / case aggregation."
    ]
    raw = case.testing.diagnostic_yield_for_phenotypes if case.testing is not None else None
    pct = _parse_percent(raw)
    if pct is None:
        prov.append(f"LOC_PHE: _ND (no parseable diagnostic yield; raw={raw!r})")
        return ScoreResult(parent_code="LOC", provenance=prov, authoritative=False)

    pts = _loc_phe_band(pct)
    prov.append(
        f"LOC_PHE: +{pts} from diagnostic yield (raw={raw!r}); robustness caveats (sample size, "
        "95% CI, methodology match) and most-specific-proband selection not verifiable from "
        "captured inputs -- reference-only."
    )
    if pts > 0.0:
        reasons = _non_segregation(case, moi=moi)
        if reasons:
            prov.append("LOC_PHE: zeroed to 0.0 -- non-segregation observed: " + "; ".join(reasons))
            if moi == MOI.AR:
                prov.append(
                    "LOC_PHE: AR caveat -- an AR non-segregation may reflect another causative "
                    "locus, not benignity; the LOC_SEG -4.0 flip is not applied (LOC_SEG is "
                    "deferred to LOC-2)."
                )
            pts = 0.0
    return ScoreResult(
        parent_code="LOC",
        sub_code_points={"LOC_PHE": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )


def _seg_points(r, moi: MOI, *, near_100: bool) -> float | None:
    """Points for one relative's co-segregation (SM 5 Figure 2), or None if not an informative
    segregant. Non-segregation events (affected+VBC-absent; unaffected carrier at ~100%) are
    detected separately and are NOT scored here.
    """
    aff = r.affected_w_mde
    carrier = r.vbc_exists
    zyg = r.vbc_zygosity
    comphet = r.cmp_het_variant_exists == TriState.TRUE
    severe = r.severe_phenotype == TriState.TRUE

    if aff == TriState.TRUE and carrier == TriState.TRUE:  # affected, carrying the VBC
        if moi == MOI.AD:
            return 1.0 if zyg == Zygosity.HET else None
        if moi == MOI.AR:
            return 2.0 if (zyg == Zygosity.HOM or comphet) else None
        if moi == MOI.SD:
            if severe and (zyg == Zygosity.HOM or comphet):
                return 2.0
            return 1.0 if zyg == Zygosity.HET else None
        if moi in _X_LINKED:  # hemizygous male / hom-or-comphet female / het female -> +1.0
            return 1.0 if (zyg in (Zygosity.HEMI, Zygosity.HOM, Zygosity.HET) or comphet) else None
        return None

    if aff == TriState.FALSE:  # unaffected co-segregant
        if moi == MOI.AR:  # het carrier OR wild type -> +0.4 (recessive; not penetrance-gated)
            if carrier == TriState.FALSE:
                return 0.4
            if carrier == TriState.TRUE and zyg == Zygosity.HET:
                return 0.4
            return None
        # AD / SD / X-linked: unaffected wild type at ~100% penetrance -> +1.0
        if near_100 and carrier == TriState.FALSE:
            return 1.0
        return None

    return None


def reference_score_loc_seg(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) LOC_SEG co-segregation points (SM 5 Figure 2).

    CSpec is authoritative. Sums per-co-segregation points across ``case.relatives`` (tiers by
    ``moi`` per SM 5 Figure 2), capped 0.0..+4.0. An observed non-segregation is a terminal
    branch: it zeroes LOC_SEG and, for AD / AR-homozygous / X-linked, flips it to -4.0 (a plain
    AR / semidominant non-segregation may reflect another causative locus, not benignity, so it
    is not flipped). ``moi`` is required to tier the segregations. The combined LOC +4.0 cap
    with LOC_PHE is applied in ``reference_aggregate_loc``.
    """
    prov: list[str] = [
        'LOC: "LOC" is the HOD grouping label; the combined LOC +4.0 cap (with LOC_PHE) is '
        "applied in case aggregation."
    ]
    if moi is None:
        prov.append("LOC_SEG: _ND (MOI is required to tier co-segregations, SM 5 Figure 2)")
        return ScoreResult(parent_code="LOC", provenance=prov, authoritative=False)

    prov.append(
        "LOC_SEG: the SM 5 Figure 2 entry gate (>1 locus AND phenocopy rate very low/zero) is "
        "not captured in the model -- assumed satisfied; reference-only (see known-gaps)."
    )

    reasons = _non_segregation(case, moi=moi)
    if reasons:
        joined = "; ".join(reasons)
        flip = moi in _NONSEG_FLIP_MOI or (moi == MOI.AR and case.vbc_zygosity == Zygosity.HOM)
        if flip:
            prov.append(
                f"LOC_SEG: {_SEG_FLIP} -- non-segregation observed ({joined}); AD / AR-homozygous "
                "/ X-linked benign flip (SM 5 Figure 2). This also zeroes LOC_PHE."
            )
            return ScoreResult(
                parent_code="LOC",
                sub_code_points={"LOC_SEG": _SEG_FLIP},
                parent_total=_SEG_FLIP,
                provenance=prov,
                authoritative=False,
            )
        prov.append(
            f"LOC_SEG: 0.0 -- non-segregation observed ({joined}); the {_SEG_FLIP} flip is NOT "
            f"applied for moi={moi.value} (a plain-AR / semidominant non-segregation may reflect "
            "another causative locus, not benignity). This also zeroes LOC_PHE."
        )
        return ScoreResult(
            parent_code="LOC",
            sub_code_points={"LOC_SEG": 0.0},
            parent_total=0.0,
            provenance=prov,
            authoritative=False,
        )

    near_100 = case.age_matched_penetrance == AgeMatchedPenetrance.NEAR_100
    total = 0.0
    counted = 0
    for i, r in enumerate(case.relatives):
        pts = _seg_points(r, moi, near_100=near_100)
        if pts is not None:
            total += pts
            counted += 1
            prov.append(f"LOC_SEG: relative[{i}] +{pts} co-segregation ({moi.value})")

    if counted == 0:
        prov.append("LOC_SEG: _ND (no informative co-segregations among captured relatives)")
        return ScoreResult(parent_code="LOC", provenance=prov, authoritative=False)

    capped = cap(total, 0.0, _SEG_CAP_HI)
    if capped != total:
        prov.append(f"LOC_SEG: raw sum {total} capped to {capped} (0.0..+4.0, SM 5 L38)")
    return ScoreResult(
        parent_code="LOC",
        sub_code_points={"LOC_SEG": capped},
        parent_total=capped,
        provenance=prov,
        authoritative=False,
    )
