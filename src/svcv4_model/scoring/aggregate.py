"""Reference (non-authoritative) family-subtotal aggregators (aggregation Inc 2).

Collapse a family's per-code ``ScoreResult``(s) into one subtotal ``ScoreResult``, applying the
family cap. POP (SM 3): POP_FRQ + POP_HMZ, no cap (independent case-level codes). LOC (SM 5 L38):
LOC_PHE + LOC_SEG summed then capped at +4.0 -- this is the POSITIVE combine only; the -4.0
non-segregation benign flip is a separate LOC-2 signal (a replacement, not a summand here). CSpec
is authoritative. Aggregators consume and produce ``ScoreResult``s, keeping the pipeline uniform:
per-code scorers -> family subtotals (here) -> cross-code combine (Inc 4) -> classification (Inc 1).
"""

from __future__ import annotations

from collections.abc import Iterable

from svcv4_model.scoring.result import ScoreResult


def _aggregate_family(
    results: Iterable[ScoreResult], *, family: str, cap: float | None
) -> ScoreResult:
    """Merge one family's per-code results into a subtotal ``ScoreResult`` (upper cap optional).

    Relies on the ``ScoreResult`` contract (a No-Data sub-code is omitted, never recorded 0.0), so
    an empty merged dict is ``_ND`` while a recorded 0.0 is scored. A duplicate sub-code across
    inputs raises (POP/LOC codes are singletons per (VBC, MDE); a repeat is a caller bug -- CLN
    cross-proband summing is a different axis, in Inc 3). The uncapped sum is preserved in
    ``held_combined`` when the cap binds.
    """
    merged: dict[str, float] = {}
    for r in results:
        sub_sum = sum(r.sub_code_points.values())
        if r.parent_total is not None and abs(r.parent_total - sub_sum) > 1e-9:
            raise ValueError(
                f"{family}: input parent_total {r.parent_total} != sum(sub_code_points) "
                f"{sub_sum} -- this family aggregator assumes they match."
            )
        for code, pts in r.sub_code_points.items():
            if code in merged:
                raise ValueError(f"{family}: duplicate sub-code {code!r} across inputs.")
            merged[code] = pts
    prov = [f'{family}: "{family}" is the HOD grouping label; family subtotal (reference).']
    if not merged:
        prov.append(f"{family}: _ND (no scored sub-codes)")
        return ScoreResult(parent_code=family, provenance=prov, authoritative=False)
    raw = sum(merged.values())
    total = raw if cap is None else min(raw, cap)
    detail = ", ".join(f"{c}={p}" for c, p in merged.items())
    held: dict[str, float] = {}
    if cap is not None and raw > cap:
        held = {"raw_sum": raw}  # uncapped sum; distinct from the sub-code namespace
        prov.append(f"{family}: subtotal capped {raw} -> {total} (+{cap} cap): {detail}")
    else:
        prov.append(f"{family}: subtotal {total} ({detail}; cap {cap})")
    return ScoreResult(
        parent_code=family,
        sub_code_points=dict(merged),
        held_combined=held,
        parent_total=total,
        provenance=prov,
        authoritative=False,
    )


def reference_aggregate_pop(results: Iterable[ScoreResult]) -> ScoreResult:
    """POP family subtotal: POP_FRQ + POP_HMZ, no cap (SM 3). Pass-through today (its scorer
    already subtotals) -- kept for a uniform family-subtotal layer that Inc 4 consumes."""
    return _aggregate_family(results, family="POP", cap=None)


def reference_aggregate_loc(results: Iterable[ScoreResult]) -> ScoreResult:
    """LOC family subtotal: the positive LOC_PHE + LOC_SEG combine, capped at +4.0 (SM 5 L38).
    The -4.0 non-segregation benign flip is a separate LOC-2 concern, not summed here."""
    return _aggregate_family(results, family="LOC", cap=4.0)


def reference_aggregate_cln_cases(results: Iterable[ScoreResult]) -> ScoreResult:
    """Sum each CLN sub-code across the per-proband ``ScoreResult``s (from
    ``reference_score_cln_proband``) into one CLN subtotal for a (VBC, MDE) (aggregation Inc 3b).

    SM 4: point values for all *unrelated* probands are assessed individually then summed (L29;
    CLN_AFF L80, CLN_DNV L147); there is **no cross-proband cap** (the SM 1 band is the only
    ceiling, downstream). Unlike the family-subtotal aggregators, a repeated sub-code is **summed**
    (cross-proband is the summing axis) -- so SD mono+biallelic summing falls out (both routed
    probands emit CLN_AFF). The caller must pass one *unrelated* index proband per family (SM 4
    L27 -- related individuals are LOC segregation, not CLN counts); that precondition is enforced
    at the case-orchestration layer, not here. CSpec is authoritative.
    """
    merged: dict[str, float] = {}
    n = 0
    for r in results:
        n += 1
        for code, pts in r.sub_code_points.items():
            merged[code] = merged.get(code, 0.0) + pts
    prov = [
        f"CLN: cross-proband subtotal over {n} proband(s) (reference); assumes unrelated index "
        "probands -- one per family (SM 4 L27); related individuals are LOC segregation, not CLN."
    ]
    if not merged:
        prov.append("CLN: _ND (no CLN sub-code scored across probands)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)
    total = sum(merged.values())
    detail = ", ".join(f"{c}={p}" for c, p in merged.items())
    prov.append(f"CLN: summed {detail} -> {total} (no cross-proband cap, SM 4).")
    return ScoreResult(
        parent_code="CLN",
        sub_code_points=merged,
        parent_total=total,
        provenance=prov,
        authoritative=False,
    )


def reference_finalize_cln(
    cln_subtotal: ScoreResult,
    ccs: ScoreResult | None = None,
    *,
    pop_frq_points: float | None,
) -> ScoreResult:
    """Apply the two CLN cross-code override rules to the cross-proband CLN subtotal (Inc 3c),
    completing the CLN family. CSpec is authoritative.

    - **CLN_CCS exclusivity** (SM 4 L25): when a ``CLN_CCS`` sub-code is present (scored, incl.
      0.0 -- "regardless of the point value"), NA ``CLN_AFF`` / ``CLN_ALT`` / ``CLN_UAF``; keep
      ``CLN_CCS`` + ``CLN_DNV``. A non-robust study returns ``_ND`` (no ``CLN_CCS``) so it does
      not fire.
    - **POP_FRQ gate** (SM 4 L27/L10): award the pathogenic *counting* codes only when the VBC is
      rare (``pop_frq_points in {0.0, -1.0}``); otherwise NA ``CLN_AFF`` and ``CLN_DNV`` (DNV is
      the faithful default -- the exact branch is in the image-only SM 4 Figure 1). Benign codes
      are not POP-gated.

    ``ccs`` is the standalone ``reference_score_cln_ccs`` result (or None). Both rules are
    removals, so their NA-sets are unioned and applied once (order-independent).
    """
    sub: dict[str, float] = dict(cln_subtotal.sub_code_points)
    if ccs is not None:
        sub.update(ccs.sub_code_points)  # add CLN_CCS if the study scored (else nothing)
    prov = ["CLN: finalize (reference) -- CLN_CCS exclusivity + POP_FRQ gate (SM 4)."]

    na: set[str] = set()
    if "CLN_CCS" in sub:
        na |= {"CLN_AFF", "CLN_ALT", "CLN_UAF"}  # SM 4 L25: keep CLN_CCS + CLN_DNV
        prov.append("CLN: CLN_CCS applied -> NA CLN_AFF/CLN_ALT/CLN_UAF (keep CLN_CCS + CLN_DNV).")
    if pop_frq_points not in (0.0, -1.0):
        na |= {"CLN_AFF", "CLN_DNV"}  # SM 4 L27 (DNV = flagged faithful default)
        prov.append(
            f"CLN: POP_FRQ gate -- pop_frq_points={pop_frq_points} not in {{0.0, -1.0}} -> "
            "NA CLN_AFF + CLN_DNV (SM 4 L27; DNV-gating is the faithful default, Fig 1 image-gap)."
        )

    kept = {c: p for c, p in sub.items() if c not in na}
    if not kept:
        prov.append("CLN: _ND (all CLN codes NA / none scored after finalize).")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)
    total = sum(kept.values())
    prov.append(f"CLN: final {', '.join(f'{c}={p}' for c, p in kept.items())} -> {total}.")
    return ScoreResult(
        parent_code="CLN",
        sub_code_points=kept,
        parent_total=total,
        provenance=prov,
        authoritative=False,
    )
