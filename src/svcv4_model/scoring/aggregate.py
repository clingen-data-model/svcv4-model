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
