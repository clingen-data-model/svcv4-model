"""Variant pathogenicity classification — the categorical result of a Statement."""

from __future__ import annotations

from enum import StrEnum


class VariantPathogenicityClassification(StrEnum):
    """Categorical classification of a variant's pathogenicity.

    Maps the Statement's final score onto a position on the
    **Benign ↔ Pathogenic** spectrum.

    This enum is a *placeholder* using the familiar five-tier vocabulary
    (Benign / Likely Benign / Variant of Uncertain Significance /
    Likely Pathogenic / Pathogenic). The SVCv4 working group is
    expected to confirm the canonical labels — and the score → label
    bands — before publication. The values are stable lowercase
    snake_case strings so JSON Schema consumers see a predictable
    enum.
    """

    BENIGN = "benign"
    LIKELY_BENIGN = "likely_benign"
    VARIANT_OF_UNCERTAIN_SIGNIFICANCE = "variant_of_uncertain_significance"
    LIKELY_PATHOGENIC = "likely_pathogenic"
    PATHOGENIC = "pathogenic"
