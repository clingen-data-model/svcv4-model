"""Data Item — a single structured evidence datum (VA-Spec 1.1.0)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DataItem(BaseModel):
    """A VA-Spec 1.1.0 ``Data Item`` — one structured datum a Statement consumes.

    A curator captures Data Items for a (VBC, MDE) curation; a Statement points at
    them via ``hasEvidenceItems``. Per 1.1.0-ballot.2026-09 the entity ``type`` is
    always ``"DataItem"`` and the datum itself lives in ``value``.

    VA-Spec Data Item has no ``subtype``; SVCv4 adds ``subtype`` as a profile
    extension to carry the evidence *kind* (e.g. ``computational_prediction``).
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str | None = Field(
        default=None,
        description="VA-Spec `id` (0..1): stable identifier for the item.",
    )
    type: Literal["DataItem"] = Field(
        default="DataItem",
        description="VA-Spec entity `type` (1..1); always `DataItem`.",
    )
    subtype: str | None = Field(
        default=None,
        description=(
            "SVCv4 profile extension: the evidence *kind* (e.g. "
            "`computational_prediction`, `functional_assay`). VA-Spec Data Item "
            "has no subtype of its own."
        ),
    )
    name: str | None = Field(
        default=None,
        description="VA-Spec `name` (0..1): short human-readable label.",
    )
    value: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "VA-Spec `value` (0..1): the structured datum. Shape is open in the "
            "scaffold and constrained by the SVCv4 profile per Evidence Code."
        ),
    )
    references: list[str] = Field(
        default_factory=list,
        description="CURIEs / URLs sourcing the evidence (e.g. PMIDs).",
    )
    aliases: list[str] = Field(
        default_factory=list,
        description="VA-Spec `aliases` (0..m).",
    )
    extensions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="VA-Spec `extensions` (0..m).",
    )
    description: str | None = Field(
        default=None,
        description="Optional prose description.",
    )


# Back-compat / VA-Spec umbrella aliases.
EvidenceItem = DataItem
EvidenceData = DataItem
