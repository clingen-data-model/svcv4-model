"""Reference (non-authoritative) scorer for the Missense amino-acid path (SM 6, MIS_)."""

from __future__ import annotations

from svcv4_model.missense import MissenseAminoAcidAssessment
from svcv4_model.scoring.primitives import (
    cap,
    hold_combined,
    missense_informative_points,
    transcript_relevance_points,
)
from svcv4_model.scoring.result import ScoreResult


def reference_score_missense_amino_acid(
    assessment: MissenseAminoAcidAssessment,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Missense amino-acid (MIS_) total (SM 6).

    CSpec is authoritative. Unlike every other scorer, the MIS_ path takes **no**
    ``gene_disease_validity`` -- MIS_PRD is reduced by transcript relevance only, with no
    molecular-mechanism axis and no GDV gate (predictors already capture LoF+GoF). FXN is
    consumed raw; MIS_INF is the computed 4-category tally. The SM 7 motif-variant special
    case and the SPL_ splice path / MIS_-vs-SPL_ comparison are separate increments.
    """
    prov: list[str] = []
    sub: dict[str, float] = {}
    held: dict[str, float] = {}

    # MIS_PRD (computed: transcript relevance only)
    prd: float | None = None
    pred = assessment.predictive
    initial = pred.initial_points if pred else None
    exon = pred.transcript_relevance if pred else None
    if initial is None:
        prov.append("MIS_PRD: _ND (no initial points)")
    else:
        adj = transcript_relevance_points(initial, exon)
        prd = cap(adj, -4.0, 4.0)
        sub["PRD"] = prd
        prov.append(
            f"MIS_PRD: {initial} x transcript-relevance = {adj}, capped [-4.0, 4.0] -> {prd}"
        )

    # MIS_FXN (consumed raw)
    fxn = assessment.fxn_points
    if fxn is None:
        prov.append("MIS_FXN: _ND (no coded fxn_points; OddsPath not recomputed)")
    else:
        sub["FXN"] = fxn
        prov.append(f"MIS_FXN: consumed coded value {fxn}")

    # held PRD+FXN
    prd_fxn = hold_combined(prd, fxn, lo=-8.0, hi=6.0)
    if prd_fxn is not None:
        held["PRD+FXN"] = prd_fxn
        prov.append(f"held PRD+FXN: {prd_fxn} (cap [-8.0, 6.0])")

    # MIS_INF (computed 4-category tally)
    inf: float | None = None
    if assessment.informative is not None:
        inf = cap(missense_informative_points(assessment.informative.variants), -8.0, 8.0)
    if inf is None:
        prov.append("MIS_INF: _ND (no categorized informative variants; SM7 motif deferred)")
    else:
        sub["INF"] = inf
        prov.append(f"MIS_INF: {inf} (cap [-8.0, 8.0]); SM7 motif special-case deferred")

    # mis_total
    mis_total = hold_combined(prd_fxn, inf, lo=-8.0, hi=9.0)
    if mis_total is not None:
        prov.append(f"mis_total: {mis_total} (cap [-8.0, 9.0])")

    return ScoreResult(
        parent_code="MIS",
        sub_code_points=sub,
        held_combined=held,
        parent_total=mis_total,
        provenance=prov,
        authoritative=False,
    )
