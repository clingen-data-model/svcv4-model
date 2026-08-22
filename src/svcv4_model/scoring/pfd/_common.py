"""Shared scoring pipeline for the NUL_/CDS_ LoF workflows (non-authoritative).

The Nonsense/Frameshift/Exon-Deletion/Exon-Duplication/Start-Lost/Stop-Lost scorers share one
pipeline (PRD -> SM 18 -> FXN -> held PRD+FXN -> INF -> capped parent); only the per-branch
caps differ, carried in each workflow's ``branch_table`` of ``BranchSpec``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import InformativeVariant
from svcv4_model.mechanism import ExonRelevance, GenccMechanism
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
)
from svcv4_model.scoring.result import ScoreResult


class _MechExon(Protocol):
    gencc_mechanism: GenccMechanism | None
    exon_relevance: ExonRelevance | None


class _Predictive(Protocol):
    initial_points: float | None


class _Informative(Protocol):
    variants: list[InformativeVariant]


class NulCdsAssessment(Protocol):
    """Structural type the shared NUL_/CDS_ helper reads."""

    prediction_outcome: object
    parent_code: PfdParentCode | None
    predictive: _Predictive | None
    mechanism_exon_relevance: _MechExon | None
    fxn_points: float | None
    informative: _Informative | None


_PARENT_LO, _PARENT_HI = -8.0, 10.0
_INF_LO, _INF_HI = -8.0, 8.0
_HELD_LO = -8.0
_DEFAULT_HELD_HI = 9.0


@dataclass(frozen=True)
class BranchSpec:
    """Per-branch caps for a NUL_/CDS_ workflow.

    Defaults match the shared constants; a workflow overrides only where SM says its branch
    differs (e.g. Start-Lost's -4 parent floor, or a benignity-only INF/parent ceiling).
    """

    parent_code: str
    prd_lo: float
    prd_hi: float
    held_hi: float = _DEFAULT_HELD_HI
    parent_lo: float = _PARENT_LO
    parent_hi: float = _PARENT_HI
    inf_lo: float = _INF_LO
    inf_hi: float = _INF_HI
    sm18_mechanism_only: bool = False
    fxn_na: bool = False


def score_nul_cds_workflow(
    assessment: NulCdsAssessment,
    branch_table: Mapping[object, BranchSpec],
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult:
    """Reference (NON-AUTHORITATIVE) score for a NUL_/CDS_ LoF workflow. CSpec is authoritative.

    ``branch_table`` maps ``prediction_outcome`` -> ``BranchSpec``. FXN is consumed raw from
    ``fxn_points`` (already coded; OddsPath not recomputed). ``gene_disease_validity`` is
    required (pass explicit None for a below-Moderate MDE).
    """
    prov: list[str] = []
    sub: dict[str, float] = {}
    held: dict[str, float] = {}

    outcome = assessment.prediction_outcome
    branch = branch_table.get(outcome) if outcome is not None else None
    parent_code = branch.parent_code if branch else None

    # PRD
    prd: float | None = None
    initial = assessment.predictive.initial_points if assessment.predictive else None
    mer = assessment.mechanism_exon_relevance
    mech = mer.gencc_mechanism if mer else None
    exon = mer.exon_relevance if mer else None
    if initial is None or branch is None:
        prov.append("PRD: _ND (no initial points and/or unknown branch)")
    else:
        adj = apply_sm18_multiplier(
            initial,
            mech,
            exon,
            gene_disease_validity,
            mechanism_only=branch.sm18_mechanism_only,
        )
        prd = cap(adj, branch.prd_lo, branch.prd_hi)
        sub["PRD"] = prd
        prov.append(
            f"PRD: initial {initial} x SM18(mech={mech}, exon={exon}, "
            f"gdv={gene_disease_validity}) = {adj}, capped "
            f"[{branch.prd_lo}, {branch.prd_hi}] -> {prd}"
        )

    # FXN (consumed raw on non-NA branches; skipped as NA on the gain paths)
    if branch is not None and branch.fxn_na:
        prov.append("FXN: NA (functional not considered on this gain path)")
        held_val = prd  # no PRD+FXN combine when FXN is NA
    else:
        fxn = assessment.fxn_points
        if fxn is None:
            prov.append("FXN: _ND (no coded fxn_points captured; OddsPath not recomputed)")
        else:
            sub["FXN"] = fxn
            prov.append(f"FXN: consumed coded value {fxn}")
        held_hi = branch.held_hi if branch else _DEFAULT_HELD_HI
        held_val = hold_combined(prd, fxn, lo=_HELD_LO, hi=held_hi)
        if held_val is not None:
            held["PRD+FXN"] = held_val
            prov.append(f"held PRD+FXN: {held_val} (cap [{_HELD_LO}, {held_hi}])")

    # INF
    inf: float | None = None
    inf_lo = branch.inf_lo if branch else _INF_LO
    inf_hi = branch.inf_hi if branch else _INF_HI
    if assessment.informative is not None:
        inf = cap(informative_points(assessment.informative.variants), inf_lo, inf_hi)
    if inf is None:
        prov.append("INF: _ND (no classified informative variants)")
    else:
        sub["INF"] = inf
        prov.append(f"INF: {inf} (cap [{inf_lo}, {inf_hi}])")

    # parent total
    parent_lo = branch.parent_lo if branch else _PARENT_LO
    parent_hi = branch.parent_hi if branch else _PARENT_HI
    parent_total = hold_combined(held_val, inf, lo=parent_lo, hi=parent_hi)
    if parent_total is not None:
        prov.append(f"parent_total: {parent_total} (cap [{parent_lo}, {parent_hi}])")

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
