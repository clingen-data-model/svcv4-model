"""Statement — the top-level VA-Spec entity for an SVCv4 classification."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.classification import VariantPathogenicityClassification
from svcv4_model.evidence_line import EvidenceLine
from svcv4_model.method import Method
from svcv4_model.proposition import Proposition


class Statement(BaseModel):
    """A SVCv4 Variant Pathogenicity Classification expressed as a VA-Spec Statement.

    The Statement is the canonical entry point into the model. It carries:

    - a `Proposition` (the SPOQ-structured assertion about a VBC and an
      MDE);
    - the `score` and `outcome` for the curation;
    - a `method` reference identifying the **applied SVCv4
      specification version** — baseline SVCv4 or a VCEP-specialised
      version selected via gene-disease-MOI scoping (resolves into
      CSpec); and
    - the collection of `evidence_lines` whose scores compose into
      `score`.

    Worked examples in `examples/` validate against `Statement`.
    """

    model_config = ConfigDict(extra="forbid")

    proposition: Proposition
    method: Method = Field(
        description=(
            "Reference identifying the **applied SVCv4 specification "
            "version** — baseline SVCv4 or a VCEP-specialised version "
            "selected for this (VBC, MDE) curation. Resolves into CSpec."
        ),
    )
    score: float = Field(
        description="The Statement's final composed score.",
    )
    outcome: VariantPathogenicityClassification = Field(
        description=(
            "Categorical classification produced by mapping "
            "`score` to the Benign ↔ Pathogenic spectrum."
        ),
    )
    strength: str | None = Field(
        default=None,
        description="Optional strength label for the score (e.g. `strong`, `supporting`).",
    )
    direction: Literal["supports", "neutral", "disputes"] = Field(
        description=(
            "VA-Spec direction of the evidence relative to the proposition "
            "(required, 1..1 per 1.1.0-ballot.2026-09): `supports` when "
            "`score` > 0, `neutral` when `score` == 0, `disputes` when "
            "`score` < 0."
        ),
    )
    contribution: float | None = Field(
        default=None,
        description=(
            "Reserved VA-Spec slot; currently unused at the Statement "
            "level. Retained for forward compatibility."
        ),
    )
    evidence_lines: list[EvidenceLine] = Field(
        default_factory=list,
        description=(
            "Evidence Lines whose scores compose into `score`. "
            "Each Evidence Line is the artifact of one CSpec "
            "method/rule invocation."
        ),
    )
    description: str | None = Field(
        default=None,
        description="Optional prose summary of the classification.",
    )
