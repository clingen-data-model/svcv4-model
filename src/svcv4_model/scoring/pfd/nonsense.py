"""Reference (non-authoritative) scorer for the Nonsense workflow (SM 8)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.nonsense import NonsenseAssessment, NonsensePredictionOutcome
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
)
from svcv4_model.scoring.result import ScoreResult

# per-branch: (parent_code, prd_lo, prd_hi, held_hi)
_BRANCH: dict[NonsensePredictionOutcome, tuple[str, float, float, float]] = {
    NonsensePredictionOutcome.NMD_NO_RESCUE: ("NUL", 0.0, 6.0, 10.0),
    NonsensePredictionOutcome.NMD_WITH_RESCUE: ("CDS", -1.0, 6.0, 9.0),
    NonsensePredictionOutcome.NO_NMD: ("CDS", 0.0, 6.0, 9.0),
}


def reference_score_nonsense(
    assessment: NonsenseAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None = None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Nonsense point total from a captured
    ``NonsenseAssessment``. CSpec is authoritative. FXN is consumed from ``fxn_points``
    (OddsPath is not recomputed).
    """
    prov: list[str] = []
    sub: dict[str, float] = {}
    held: dict[str, float] = {}

    outcome = assessment.prediction_outcome
    branch = _BRANCH.get(outcome) if outcome is not None else None
    parent_code = branch[0] if branch else None

    # PRD
    prd: float | None = None
    initial = assessment.predictive.initial_points if assessment.predictive else None
    mer = assessment.mechanism_exon_relevance
    mech = mer.gencc_mechanism if mer else None
    exon = mer.exon_relevance if mer else None
    if initial is None or branch is None:
        prov.append("PRD: _ND (no initial points and/or unknown branch)")
    else:
        adj = apply_sm18_multiplier(initial, mech, exon, gene_disease_validity)
        prd = cap(adj, branch[1], branch[2])
        sub["PRD"] = prd
        prov.append(
            f"PRD: initial {initial} x SM18(mech={mech}, exon={exon}, "
            f"gdv={gene_disease_validity}) = {adj}, capped [{branch[1]}, {branch[2]}] -> {prd}"
        )

    # FXN (consumed, not recomputed)
    fxn = assessment.fxn_points
    if fxn is None:
        prov.append("FXN: _ND (no coded fxn_points captured; OddsPath not recomputed)")
    else:
        sub["FXN"] = fxn
        prov.append(f"FXN: consumed coded value {fxn}")

    # held PRD+FXN
    held_hi = branch[3] if branch else 9.0
    held_val = hold_combined(prd, fxn, lo=-8.0, hi=held_hi)
    if held_val is not None:
        held["PRD+FXN"] = held_val
        prov.append(f"held PRD+FXN: {held_val} (cap [-8.0, {held_hi}])")

    # INF
    inf: float | None = None
    if assessment.informative is not None:
        inf = cap(informative_points(assessment.informative.variants), -8.0, 8.0)
    if inf is None:
        prov.append("INF: _ND (no classified informative variants)")
    else:
        sub["INF"] = inf
        prov.append(f"INF: {inf} (cap [-8.0, 8.0])")

    # parent total
    parent_total = hold_combined(held_val, inf, lo=-8.0, hi=10.0)
    if parent_total is not None:
        prov.append(f"parent_total: {parent_total} (cap [-8.0, 10.0])")

    # captured parent_code cross-check (report, do not fix)
    captured = assessment.parent_code
    if captured is not None and parent_code is not None and captured.value != parent_code:
        prov.append(f"NOTE: captured parent_code {captured.value} != branch-derived {parent_code}")

    return ScoreResult(
        parent_code=parent_code,
        sub_code_points=sub,
        held_combined=held,
        parent_total=parent_total,
        provenance=prov,
        authoritative=False,
    )
