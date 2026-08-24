"""Reference (non-authoritative) classification band (SM 1): points -> category + VUS subclass.

CSpec is authoritative. Maps a summed Bayesian point total to the SM 1 pathogenicity descriptor
(``SM01-glossary.txt`` L6-14). Pure and total -- every finite point value maps to exactly one
band; there is no No-Data return (that concept belongs to the per-code scorers). ``VusSubclass``
lives here (not the model) so it stays off the JSON-Schema surface. The summing that produces
``points`` and the open global-sum-clamp question live in later aggregation increments.
"""

from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple

from svcv4_model.informative import VariantClassification


class VusSubclass(StrEnum):
    """The three SM 1 VUS subclasses (low is LB-adjacent; high is LP-adjacent)."""

    LOW = "VUS-low"
    MID = "VUS-mid"
    HIGH = "VUS-high"


class Classification(NamedTuple):
    """A banded result: the 5-way category, plus the VUS subclass iff category is VUS."""

    category: VariantClassification
    vus_subclass: VusSubclass | None


def reference_classify(points: float) -> Classification:
    """Map a Bayesian point total to the reference (NON-AUTHORITATIVE) SM 1 band.

    ``>=+10`` P; ``[+6,+10)`` LP; ``[+4,+6)`` VUS-high; ``[+2,+4)`` VUS-mid; ``(-1,+2)`` VUS-low;
    ``(-4,-1]`` LB; ``<=-4`` B. Not clamped (SM 1 P is open-ended ``>=+10``); the global-sum-clamp
    question is deferred to the cross-code-combination increment.
    """
    if points >= 10.0:
        return Classification(VariantClassification.PATHOGENIC, None)
    if points >= 6.0:
        return Classification(VariantClassification.LIKELY_PATHOGENIC, None)
    if points >= 4.0:
        return Classification(VariantClassification.VUS, VusSubclass.HIGH)
    if points >= 2.0:
        return Classification(VariantClassification.VUS, VusSubclass.MID)
    if points > -1.0:
        return Classification(VariantClassification.VUS, VusSubclass.LOW)
    if points > -4.0:
        return Classification(VariantClassification.LIKELY_BENIGN, None)
    return Classification(VariantClassification.BENIGN, None)
