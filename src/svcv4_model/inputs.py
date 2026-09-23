"""Inputs to a Variant Pathogenicity Classification: the VBC and the MDE."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MolecularConsequence(StrEnum):
    """The VBC's predicted molecular consequence — the evidence that routes it to a
    PFD variant-impact family (MIS / NUL / CDS / SPL).

    This is the routing input read by the ``variant-impact-router`` node under PFD.
    Several consequences resolve to NUL *or* CDS via a branch inside their own
    variant-type workflow (NMD / non-stop-decay / alt-start / whole-gene); the
    router names the candidate family set and that branch picks the final one.
    Missense is unambiguous → MIS.
    """

    MISSENSE = "MISSENSE"
    NONSENSE = "NONSENSE"
    FRAMESHIFT = "FRAMESHIFT"
    INFRAME_INDEL = "INFRAME_INDEL"
    START_LOST = "START_LOST"
    STOP_LOST = "STOP_LOST"
    SPLICE = "SPLICE"
    EXON_DELETION = "EXON_DELETION"
    EXON_DUPLICATION = "EXON_DUPLICATION"
    INTRONIC = "INTRONIC"
    SYNONYMOUS = "SYNONYMOUS"


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
    molecular_consequence: MolecularConsequence | None = Field(
        default=None,
        description=(
            "The VBC's predicted molecular consequence (e.g. from VEP against the "
            "relevant transcript). This is the evidence the PFD variant-impact router "
            "reads to select the MIS / NUL / CDS / SPL family. None = not captured."
        ),
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
