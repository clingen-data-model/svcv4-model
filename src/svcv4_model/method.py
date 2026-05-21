"""Reference to a method or rule defined and applied by ClinGen CSpec."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Method(BaseModel):
    """A reference to a CSpec-defined method, rule, or specification.

    This class **names**, but does not **define**, a method. Method
    definitions — together with their evaluation logic, scoring rules,
    and version selection — live in ClinGen CSpec, which is outside
    this repository and outside GA4GH GKS VA-Spec.

    Used in two roles:

    1. At the `Statement` level, `method` identifies the **applied
       SVCv4 specification version** — either the baseline SVCv4
       Standard or a specific VCEP-specialised version that was
       selected for the (VBC, MDE) curation.
    2. At the `EvidenceLine` level, `method` identifies the specific
       CSpec method or rule whose invocation produced that Evidence
       Line's score.
    """

    model_config = ConfigDict(extra="forbid")

    code: str = Field(
        description=(
            "Opaque method/rule code as published by CSpec. CURIE-style "
            "scheme TBD; treated as an opaque string for now."
        ),
    )
    label: str | None = Field(
        default=None,
        description="Human-readable label for the method/rule.",
    )
    version: str | None = Field(
        default=None,
        description=(
            "When `code` identifies an SVCv4 specification (baseline or "
            "specialised), the version of that specification."
        ),
    )
    description: str | None = Field(
        default=None,
        description="Optional prose description; usually a pointer into CSpec.",
    )
