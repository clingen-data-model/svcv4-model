"""Reference (non-authoritative) scorer for Population evidence (SM 3, POP_FRQ + POP_HMZ)."""

from __future__ import annotations

from svcv4_model.case import MOI, TriState
from svcv4_model.population import PopulationEvidence
from svcv4_model.scoring.result import ScoreResult

_X_LINKED = frozenset({MOI.XLD, MOI.XLR})


def _pop_frq_points(faf: float | None, daft: float | None) -> float | None:
    """POP_FRQ benignity by FAF/DAFT fold (SM 3). None when no fold is computable."""
    if faf is None or daft is None or daft <= 0:
        return None
    fold = faf / daft
    if fold < 1.5:
        return 0.0
    if fold < 5.0:
        return -1.0
    if fold < 15.0:
        return -3.0
    return -6.0


def _pop_hmz_weight(moi: MOI | None) -> float:
    """Per-observation POP_HMZ weight (SM 3 Table 7): AD is -1.0, everything else -0.5."""
    return -1.0 if moi == MOI.AD else -0.5


def _pop_hmz_points(evidence: PopulationEvidence, moi: MOI | None) -> float | None:
    """POP_HMZ benignity from eligible occurrences (SM 3 Table 7). None when not applicable."""
    if evidence.hmz_eligible != TriState.TRUE:
        return None
    homo = evidence.homozygote_count
    hemi = evidence.hemizygote_count if moi in _X_LINKED else None
    if homo is None and hemi is None:
        return None
    count = (homo or 0) + (hemi or 0)
    return _pop_hmz_weight(moi) * max(count - 1, 0)


def reference_score_population(
    evidence: PopulationEvidence,
    *,
    moi: MOI | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Population points (SM 3): POP_FRQ + POP_HMZ.

    CSpec is authoritative. Both codes are benignity-only (<= 0). ``moi`` is required (consumed
    only by POP_HMZ, for X-linked hemizygote counting; pass explicit None when unknown ->
    homozygotes only). ``parent_code`` is the grouping label ``"POP"`` (not an SVCv4 parent code);
    ``parent_total`` is the sum of the recorded sub-codes (a convenience subtotal, no SM 3 cap).
    """
    prov: list[str] = [
        'POP: "POP" is a grouping label (POP_FRQ/POP_HMZ are independent case-level codes), '
        "not an SVCv4 parent code; parent_total is a convenience subtotal (no SM 3 combined cap)."
    ]
    sub: dict[str, float] = {}

    frq = _pop_frq_points(evidence.faf, evidence.daft)
    if frq is None:
        prov.append("POP_FRQ: _ND (no FAF and/or DAFT; absent-in-db is faf=0.0 -> 0.0, not None)")
    else:
        sub["POP_FRQ"] = frq
        prov.append(
            f"POP_FRQ: FAF {evidence.faf} / DAFT {evidence.daft} = "
            f"{evidence.faf / evidence.daft:.3g}x -> {frq} "
            "(bands <1.5x/5x/15x, lower edge inclusive -- SM 3 boundary assumption)"
        )

    hmz = _pop_hmz_points(evidence, moi)
    if hmz is None:
        prov.append("POP_HMZ: _ND (not hmz_eligible, or no homozygote/hemizygote count)")
    else:
        sub["POP_HMZ"] = hmz
        weight = _pop_hmz_weight(moi)
        prov.append(
            f"POP_HMZ: {hmz} (weight {weight}/obs from the 2nd -- SM 3 Table 7; "
            "AD -1.0 vs prose -0.5 conflict, encoded to Table 7)"
        )

    total = sum(sub.values()) if sub else None
    if total is not None:
        prov.append(f"POP total: {total} (POP_FRQ + POP_HMZ; no SM 3 combined cap)")

    return ScoreResult(
        parent_code="POP",
        sub_code_points=sub,
        parent_total=total,
        provenance=prov,
        authoritative=False,
    )
