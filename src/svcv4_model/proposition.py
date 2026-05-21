"""Proposition — the SPOQ-structured assertion at the heart of a Statement."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.inputs import MDE, VBC


class Predicate(StrEnum):
    """Predicate of a Variant Pathogenicity Proposition.

    Placeholder vocabulary; the SVCv4 VA-Spec community profile will
    confirm the canonical predicate(s).
    """

    IS_CAUSAL_FOR = "is_causal_for"


class Proposition(BaseModel):
    """A SPOQ-structured Proposition: **S**ubject, **P**redicate, **O**bject, **Q**ualifier(s).

    For a Variant Pathogenicity Classification:

    - **Subject** is the `VBC` (the variant under evaluation).
    - **Predicate** is the asserted relationship (default
      `is_causal_for`).
    - **Object** is the `MDE` (the disease being assessed).
    - **Qualifier(s)** carry additional context (mode of inheritance,
      population, tissue, etc.). Open shape in the scaffold.
    """

    model_config = ConfigDict(extra="forbid")

    subject: VBC
    predicate: Predicate = Field(
        default=Predicate.IS_CAUSAL_FOR,
        description="Asserted relationship between the VBC and the MDE.",
    )
    object: MDE
    qualifiers: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Additional contextual qualifiers. Shape will be "
            "constrained by the SVCv4 VA-Spec community profile."
        ),
    )
