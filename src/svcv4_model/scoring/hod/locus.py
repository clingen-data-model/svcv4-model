"""Reference (non-authoritative) scorer for Locus specificity -- phenotype (SM 5, LOC_PHE).

Increment LOC-1: LOC_PHE only. LOC_SEG (co-segregation) and the combined LOC +4.0 cap are
deferred (LOC_SEG's per-MOI affected-segregant point values are in the SM 5 Figure 2 image, not
the text). CSpec is authoritative. ``parent_code="LOC"`` is a display/grouping label (not an
SVCv4 parent code); ``parent_total`` is the recorded LOC_PHE value.
"""

from __future__ import annotations

import re

from svcv4_model.case import MOI, AgeMatchedPenetrance, Case, TriState
from svcv4_model.scoring.result import ScoreResult

_NUM = re.compile(r"[0-9]*\.?[0-9]+")
_RULE_B_SUPPRESSED = frozenset({MOI.AR})  # None also suppresses rule (b)


def _parse_percent(raw: str | None) -> float | None:
    """First numeric token of a yield string as a percent, or None if none found.

    Clean point estimates ('90%', '2.6%') and the LOWER bound of a range ('91-93%' -> 91.0). A
    leading '<' is honored as "just below" (SM 5's idiomatic '<33%' -> band 0.0, not +1.0); a
    leading '>' keeps the number as a conservative floor. The raw string is echoed in provenance.
    """
    if raw is None:
        return None
    m = _NUM.search(raw)
    if m is None:
        return None
    pct = float(m.group())
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
