"""Evidence Line — the artifact of one CSpec method/rule invocation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.classification import VariantPathogenicityClassification
from svcv4_model.evidence_item import EvidenceItem
from svcv4_model.method import Method


class EvidenceLine(BaseModel):
    """Result of invoking a CSpec method/rule on a curator's Evidence Items.

    Each Evidence Line records:

    - The **method/rule code** (`method`) that was invoked.
    - The **evidence used** (`evidence`) — the Evidence Items that were
      provided as inputs.
    - The **score** and optional **strength**/**direction** that the
      CSpec method produced.
    - Optional `outcome` if the line maps to a categorical label.

    Per VA-Spec, *any process, rule, or method that produces a score
    maps to an Evidence Line*. The method's *definition* lives in
    CSpec; only the invocation *result* lives here.
    """

    model_config = ConfigDict(extra="forbid")

    method: Method = Field(
        description=(
            "Reference to the CSpec method or rule whose invocation produced this Evidence Line."
        ),
    )
    code: str | None = Field(
        default=None,
        description=(
            "Optional Evidence Code / method-code reference; mirrors "
            "or disambiguates `method.code` where helpful."
        ),
    )
    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description=(
            "Evidence Items used as inputs to the method/rule. May be "
            "a subset of all items captured for the (VBC, MDE) curation."
        ),
    )
    score: float = Field(
        description="Numeric score produced by the method/rule.",
    )
    strength: str | None = Field(
        default=None,
        description=(
            "Optional strength label produced alongside the score "
            "(e.g. `supporting`, `moderate`, `strong`). Vocabulary TBD."
        ),
    )
    direction: str | None = Field(
        default=None,
        description=(
            "Optional direction label produced alongside the score "
            "(e.g. `pathogenic`, `benign`). Vocabulary TBD."
        ),
    )
    outcome: VariantPathogenicityClassification | None = Field(
        default=None,
        description=(
            "Optional categorical classification associated with this "
            "Evidence Line's score, where applicable."
        ),
    )
    contribution: float | None = Field(
        default=None,
        description=(
            "Optional weighted contribution this Evidence Line makes to "
            "the Statement's final score."
        ),
    )
    provisional: bool = Field(
        default=False,
        description=(
            "True when this line's `code` is a **provisional** SVCv4 code or "
            "subcode — one derived to fill a gap in the official Summary "
            "Table (a combination-cap cell) or a deeper method-level "
            "assessment (predictor initial points, exon relevance, "
            "same-/distant-AA tally). Provisional codes follow the SVCv4 "
            "nomenclature but are not yet part of the official code list."
        ),
    )
    evidence_lines: list[EvidenceLine] = Field(
        default_factory=list,
        description=(
            "Nested child Evidence Lines — the lower-level method/rule "
            "assessments (concept → code → subcode) that compose into this "
            "line's `score`. Per VA-Spec 1.1.0, an Evidence Line may nest "
            "further Evidence Lines."
        ),
    )
    description: str | None = Field(
        default=None,
        description="Optional prose summary of the line for human readers.",
    )


# Resolve the self-referential ``evidence_lines`` forward reference.
EvidenceLine.model_rebuild()
