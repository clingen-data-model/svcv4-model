"""Shared scoring pipeline for the SPL_ splice workflows (non-authoritative).

The Canonical-Splice / Intronic-Synonymous / Missense-splice scorers share one pipeline
(PRD -> SPA -> held prd_spa -> FXN -> held prd_spa_fxn -> INF -> parent), with two held
values and a constant SPL_ parent code; per-path caps are carried in a ``SplBranchSpec``.
SPA and FXN are consumed raw (analyst-coded); PRD and INF are computed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import InformativeVariant
from svcv4_model.mechanism import ExonRelevance, GenccMechanism
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
)
from svcv4_model.scoring.result import ScoreResult

_HELD_LO = -8.0


class _MechExon(Protocol):
    gencc_mechanism: GenccMechanism | None
    exon_relevance: ExonRelevance | None


class _Predictive(Protocol):
    initial_points: float | None


class _Informative(Protocol):
    variants: list[InformativeVariant]


class SplAssessment(Protocol):
    """Structural type the shared SPL_ helper reads."""

    prediction_outcome: object
    predictive: _Predictive | None
    mechanism_exon_relevance: _MechExon | None
    spa_points: float | None
    fxn_points: float | None
    informative: _Informative | None


@dataclass(frozen=True)
class SplBranchSpec:
    """Per-path caps for an SPL_ splice workflow (parent code is constant SPL)."""

    prd_lo: float
    prd_hi: float
    prd_spa_lo: float = -8.0
    prd_spa_hi: float = 10.0
    prd_spa_fxn_hi: float = 9.0
    inf_lo: float = -8.0
    inf_hi: float = 8.0
    parent_lo: float = -8.0
    parent_hi: float = 10.0


def score_spl_workflow(
    assessment: SplAssessment,
    branch_table: Mapping[object, SplBranchSpec],
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Reference (NON-AUTHORITATIVE) score for an SPL_ splice workflow. CSpec is authoritative.

    PRD is computed (initial x SM 18, capped); SPA and FXN are consumed raw (analyst-coded);
    INF is the shared tally. Two held values (PRD+SPA, PRD+SPA+FXN) are recorded; the parent
    code is always ``SPL``. ``gene_disease_validity`` is required.
    """
    prov: list[str] = []
    sub: dict[str, float] = {}
    held: dict[str, float] = {}

    outcome = assessment.prediction_outcome
    branch = branch_table.get(outcome) if outcome is not None else None

    # PRD (computed)
    prd: float | None = None
    initial = assessment.predictive.initial_points if assessment.predictive else None
    mer = assessment.mechanism_exon_relevance
    mech = mer.gencc_mechanism if mer else None
    exon = mer.exon_relevance if mer else None
    if initial is None or branch is None:
        prov.append("SPL_PRD: _ND (no initial points and/or unknown path)")
    else:
        adj = apply_sm18_multiplier(initial, mech, exon, gene_disease_validity)
        prd = cap(adj, branch.prd_lo, branch.prd_hi)
        sub["PRD"] = prd
        prov.append(
            f"SPL_PRD: {initial} x SM18 = {adj}, capped [{branch.prd_lo}, {branch.prd_hi}] -> {prd}"
        )

    # SPA (consumed raw)
    spa = assessment.spa_points
    if spa is None:
        prov.append("SPL_SPA: _ND (no coded spa_points)")
    else:
        sub["SPA"] = spa
        prov.append(f"SPL_SPA: consumed coded value {spa}")

    # held PRD+SPA
    prd_spa_lo = branch.prd_spa_lo if branch else -8.0
    prd_spa_hi = branch.prd_spa_hi if branch else 10.0
    prd_spa = hold_combined(prd, spa, lo=prd_spa_lo, hi=prd_spa_hi)
    if prd_spa is not None:
        held["PRD+SPA"] = prd_spa
        prov.append(f"held PRD+SPA: {prd_spa} (cap [{prd_spa_lo}, {prd_spa_hi}])")

    # FXN (consumed raw)
    fxn = assessment.fxn_points
    if fxn is None:
        prov.append("SPL_FXN: _ND (no coded fxn_points; OddsPath not recomputed)")
    else:
        sub["FXN"] = fxn
        prov.append(f"SPL_FXN: consumed coded value {fxn}")

    # held PRD+SPA+FXN
    prd_spa_fxn_hi = branch.prd_spa_fxn_hi if branch else 9.0
    prd_spa_fxn = hold_combined(prd_spa, fxn, lo=_HELD_LO, hi=prd_spa_fxn_hi)
    if prd_spa_fxn is not None:
        held["PRD+SPA+FXN"] = prd_spa_fxn
        prov.append(f"held PRD+SPA+FXN: {prd_spa_fxn} (cap [{_HELD_LO}, {prd_spa_fxn_hi}])")

    # INF (computed)
    inf: float | None = None
    inf_lo = branch.inf_lo if branch else -8.0
    inf_hi = branch.inf_hi if branch else 8.0
    if assessment.informative is not None:
        inf = cap(informative_points(assessment.informative.variants), inf_lo, inf_hi)
    if inf is None:
        prov.append("SPL_INF: _ND (no classified informative variants)")
    else:
        sub["INF"] = inf
        prov.append(f"SPL_INF: {inf} (cap [{inf_lo}, {inf_hi}])")

    # parent total
    parent_lo = branch.parent_lo if branch else -8.0
    parent_hi = branch.parent_hi if branch else 10.0
    parent_total = hold_combined(prd_spa_fxn, inf, lo=parent_lo, hi=parent_hi)
    if parent_total is not None:
        prov.append(f"spl_total: {parent_total} (cap [{parent_lo}, {parent_hi}])")

    return ScoreResult(
        parent_code="SPL",
        sub_code_points=sub,
        held_combined=held,
        parent_total=parent_total,
        provenance=prov,
        authoritative=False,
    )
