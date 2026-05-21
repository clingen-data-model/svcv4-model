"""Inputs to a Variant Pathogenicity Classification: the VBC and the MDE."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VBC(BaseModel):
    """Variant Being Considered — the germline variant under evaluation.

    Eventually typed via a GA4GH VRS `Variation`. Today this is a
    placeholder accepting any VRS-shaped payload as a dict; wiring
    through to `ga4gh.vrs.models.Variation` is a follow-up once the
    SVCv4 VA-Spec community profile is locked.
    """

    model_config = ConfigDict(extra="forbid")

    variation: dict[str, Any] = Field(
        description=(
            "VRS Variation payload — placeholder. Will be typed as "
            "`ga4gh.vrs.models.Variation` in a follow-up PR."
        ),
    )
    label: str | None = Field(
        default=None,
        description="Human-readable label for the variant.",
    )


class MDE(BaseModel):
    """Mendelian Disease Entity — the disease the VBC is being assessed against.

    `curie` is intentionally a flexible string for the scaffold.
    Acceptable namespaces include MONDO, OMIM, and Orphanet; precise
    namespace constraints will be set by the SVCv4 VA-Spec community
    profile.
    """

    model_config = ConfigDict(extra="forbid")

    curie: str = Field(
        description=("CURIE identifier (e.g. `MONDO:0007254`, `OMIM:114480`, `Orphanet:289545`)."),
    )
    label: str | None = Field(
        default=None,
        description="Human-readable label for the disease.",
    )
