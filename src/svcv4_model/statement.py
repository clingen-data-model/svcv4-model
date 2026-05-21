"""Statement — the top-level VA-Spec entity for an SVCv4 classification."""

from __future__ import annotations

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
    - the `final_score` and `score_classification` for the curation;
    - a `method` reference identifying the **applied SVCv4
      specification version** — baseline SVCv4 or a VCEP-specialised
      version selected via gene-disease-MOI scoping (resolves into
      CSpec); and
    - the collection of `evidence_lines` whose scores compose into
      `final_score`.

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
    final_score: float = Field(
        description="The Statement's final composed score.",
    )
    score_classification: VariantPathogenicityClassification = Field(
        description=(
            "Categorical classification produced by mapping "
            "`final_score` to the Benign ↔ Pathogenic spectrum."
        ),
    )
    strength_direction: str | None = Field(
        default=None,
        description="Optional strength-direction label for the final score.",
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
            "Evidence Lines whose scores compose into `final_score`. "
            "Each Evidence Line is the artifact of one CSpec "
            "method/rule invocation."
        ),
    )
    description: str | None = Field(
        default=None,
        description="Optional prose summary of the classification.",
    )
