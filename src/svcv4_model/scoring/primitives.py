"""Shared, workflow-agnostic reference-scoring primitives (non-authoritative).

CSpec is authoritative. The SM 18 multiplier here encodes one Figure-1-pending assumption
(the Suspected x Most matrix cell = 0.25); see ``apply_sm18_multiplier``.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import InformativeVariant, VariantClassification
from svcv4_model.mechanism import ExonRelevance, GenccMechanism

_MECHANISM_FRACTION: dict[GenccMechanism, float] = {
    GenccMechanism.ESTABLISHED: 1.0,
    GenccMechanism.LIKELY: 0.5,
    GenccMechanism.SUSPECTED: 0.25,
    GenccMechanism.UNCERTAIN: 0.0,
}
_EXON_FRACTION: dict[ExonRelevance, float] = {
    ExonRelevance.ALL: 1.0,
    ExonRelevance.MOST: 0.5,
    ExonRelevance.FEW: 0.0,
}
_GDV_MODERATE_PLUS = frozenset(
    {GeneDiseaseValidity.DEFINITIVE, GeneDiseaseValidity.STRONG, GeneDiseaseValidity.MODERATE}
)


def cap(value: float | None, lo: float, hi: float) -> float | None:
    """Clamp ``value`` to [lo, hi]; ``None`` passes through."""
    if value is None:
        return None
    return max(lo, min(hi, value))


def hold_combined(*parts: float | None, lo: float, hi: float) -> float | None:
    """Sum the non-None ``parts`` and cap; return None if every part is None."""
    present = [p for p in parts if p is not None]
    if not present:
        return None
    return cap(sum(present), lo, hi)


def informative_points(variants: Iterable[InformativeVariant]) -> float | None:
    """SM 19 (+ SM 8) informative tally.

    +2 first P / +1 first LP / +1 each additional P/LP; symmetric negatives for B/LB
    (inferred per SM 8 'similar logic'); VUS -> 0. Returns None when there are no classified
    variants (``_INF_ND``). Uncapped — the caller applies the per-workflow INF cap.
    """
    classes = [v.classification for v in variants if v.classification is not None]
    if not classes:
        return None
    n = Counter(classes)
    n_p = n.get(VariantClassification.PATHOGENIC, 0)
    n_lp = n.get(VariantClassification.LIKELY_PATHOGENIC, 0)
    n_b = n.get(VariantClassification.BENIGN, 0)
    n_lb = n.get(VariantClassification.LIKELY_BENIGN, 0)
    pts = 0.0
    if n_p:
        pts += 2.0
    if n_lp:
        pts += 1.0
    pts += max(n_p - 1, 0) + max(n_lp - 1, 0)
    if n_b:
        pts -= 2.0
    if n_lb:
        pts -= 1.0
    pts -= max(n_b - 1, 0) + max(n_lb - 1, 0)
    return pts


def apply_sm18_multiplier(
    points: float | None,
    gencc_mechanism: GenccMechanism | None,
    exon_relevance: ExonRelevance | None,
    gene_disease_validity: GeneDiseaseValidity | None,
    *,
    mechanism_only: bool = False,
) -> float | None:
    """SM 18 mechanism x exon-relevance reduction, applied ONLY to positive ``points``.

    None/<=0 pass through. GDV below Moderate (incl. None) -> mechanism treated as Uncertain
    -> x0 (documented project gate, SM 18 L11). None mechanism -> 0.0; None exon -> no
    reduction (x1.0, the generous default, asymmetric with mechanism by project choice).
    Suspected x Most is special-cased to 0.25 (Figure-1-pending assumption), not the 0.125
    product SM 18 declined to use. ``mechanism_only`` removes the exon-relevance axis (SM 13
    whole-gene deletion): the reduction is the mechanism fraction alone (exon and the
    Suspected x Most special-case are not consulted).
    """
    if points is None or points <= 0:
        return points
    if gene_disease_validity not in _GDV_MODERATE_PLUS:
        return 0.0
    mech = _MECHANISM_FRACTION.get(gencc_mechanism, 0.0) if gencc_mechanism else 0.0
    if mechanism_only:
        return points * mech
    exon = 1.0 if exon_relevance is None else _EXON_FRACTION.get(exon_relevance, 1.0)
    if gencc_mechanism == GenccMechanism.SUSPECTED and exon_relevance == ExonRelevance.MOST:
        fraction = 0.25
    else:
        fraction = mech * exon
    return points * fraction
