"""Evidence Item (alias: Evidence Data) — a single structured datum."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItem(BaseModel):
    """A single structured datum captured by the curator for a (VBC, MDE) curation.

    **Evidence Items are inputs** that the Classification Model provides
    to CSpec methods/rules under the chosen specification version. After
    CSpec evaluates them, the resulting `EvidenceLine` records which
    Items were used and the score that was produced.

    The `data` payload is intentionally generic in this scaffold so that
    the model can carry arbitrary VA-Spec-conformant evidence
    structures; the SVCv4 VA-Spec community profile will constrain it
    per Evidence Code over time.
    """

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(
        default=None,
        description="Stable identifier for the item, when one exists.",
    )
    type: str | None = Field(
        default=None,
        description=(
            "Kind of evidence (e.g. `clinical_observation`, `functional_assay`). Vocabulary TBD."
        ),
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "The structured datum itself. Shape is intentionally open "
            "in the scaffold and will be constrained by the SVCv4 "
            "VA-Spec community profile per Evidence Code."
        ),
    )
    references: list[str] = Field(
        default_factory=list,
        description="CURIEs / URLs sourcing the evidence (e.g. PMIDs).",
    )
    description: str | None = Field(
        default=None,
        description="Optional prose description.",
    )


# VA-Spec umbrella alias for callers that prefer `EvidenceData`.
EvidenceData = EvidenceItem
