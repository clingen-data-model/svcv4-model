"""SVCv4 PFD shared submodule — Informative Variants (SM 19).

Observations of variants *other than the VBC* that inform the VBC's
classification. This module captures the structured inputs; the SM 19 scoring
(see docs/workflows/pfd/index.md) is documented, not computed. A curation-level
payload for a PFD evidence item, like ``MechanismExonRelevanceEvidence``.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class VariantClassification(StrEnum):
    """A variant's pathogenicity classification. Introduced for informative
    variants (SM 19), whose scoring keys on P/LP vs B/LB. Not (yet) applied to
    the placeholder ``classification`` strings on other Case sub-models.
    """

    PATHOGENIC = "PATHOGENIC"
    LIKELY_PATHOGENIC = "LIKELY_PATHOGENIC"
    VUS = "VUS"
    LIKELY_BENIGN = "LIKELY_BENIGN"
    BENIGN = "BENIGN"


class SimilarityBasis(StrEnum):
    """Why a variant is informative for the VBC (SM 19) — variant-type dependent."""

    SIMILAR_POSITION = "SIMILAR_POSITION"
    SAME_EXON = "SAME_EXON"
    SIMILAR_EFFECT = "SIMILAR_EFFECT"
    GENE_DELETION = "GENE_DELETION"


class AminoAcidRelation(StrEnum):
    """An informative missense variant's amino-acid change relative to the VBC (SM 19)."""

    SAME = "same"  # same amino-acid change as the VBC (a distinct nucleotide)
    DISTINCT = "distinct"  # a different amino-acid change


class InformativeVariant(BaseModel):
    """A single distinct variant (not the VBC) informative for the VBC's
    classification. Only distinct variants count; observation counts are
    irrelevant (SM 19).
    """

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None, description="Identifier for the informative variant.")
    classification: VariantClassification | None = Field(
        default=None,
        description="The informative variant's own pathogenicity classification.",
    )
    similarity_basis: SimilarityBasis | None = Field(
        default=None,
        description="Why it is informative for the VBC (position/exon/effect/deletion).",
    )
    aa: AminoAcidRelation | None = Field(
        default=None,
        description="Amino-acid change relative to the VBC: same or distinct (SM 19 missense).",
    )
    grantham: float | None = Field(
        default=None,
        description=(
            "Grantham difference of this variant's amino-acid change; compared to the "
            "VBC's Grantham (passed to evaluate) on the distinct-AA scoring paths."
        ),
    )
    distinct_evidence_from_vbc: bool | None = Field(
        default=None,
        description=(
            "Whether it reached its classification via different evidence codes/"
            "weights than the VBC — required for it to count (SM 19)."
        ),
    )
    star_rating: int | None = Field(
        default=None,
        description=(
            "ClinVar review star rating, for external classifications (usable "
            "only at 3-4 stars with circularity avoided)."
        ),
    )
    circularity_checked: bool | None = Field(
        default=None,
        description=(
            "Whether the analyst confirmed the VBC was not used as evidence for "
            "this variant's classification (circularity avoided)."
        ),
    )
    attributes: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Path-matching attributes for SM 19 INF scoring — the criteria the "
            "variant satisfies relative to the VBC. Missense uses `aa` (same|"
            "distinct amino-acid change) and `grantham_vs_vbc` (le|ge); other "
            "families use their own keys."
        ),
    )


class InformativeVariantsEvidence(BaseModel):
    """SM 19 informative-variants inputs for a PFD assessment.

    Captured; the scoring (+2.0 first distinct P / +1.0 each additional, cap
    ±8; mirror negatives for B/LB) is documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    variants: list[InformativeVariant] = Field(
        default_factory=list,
        description="0..many distinct informative variants (observation counts do not matter).",
    )
