"""Statement — the core VA-Spec 1.1.0 entity for an SVCv4 classification.

Per VA-Spec 1.1.0-ballot.2026-09, an *Evidence Line is not a distinct class* — it
is a ``Statement`` referenced from another Statement via ``hasEvidenceLines``.
Statement is therefore **recursive**: the top-level classification and every
nested evidence-line assessment are all Statements.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.data_item import DataItem
from svcv4_model.method import Method
from svcv4_model.proposition import Proposition


class Statement(BaseModel):
    """A VA-Spec 1.1.0 ``Statement``, profiled for SVCv4.

    Used at two levels:

    1. **Top level** — the rolled-up Variant Pathogenicity Classification: a
       ``proposition`` (the SPOQ assertion about a VBC and MDE), the final
       ``score`` / ``direction`` / ``outcome``, the applied specification
       version (``specifiedBy``), and the composing ``hasEvidenceLines``.
    2. **Evidence-line level** — one CSpec method/rule assessment nested under a
       parent via ``hasEvidenceLines``: its ``code``, ``score``, ``direction``,
       ``strength``, ``outcome``, the ``hasEvidenceItems`` it consumed, and any
       deeper ``hasEvidenceLines`` (concept → code → subcode).

    ``score`` and ``quality`` are deprecated in VA-Spec core; SVCv4 continues to
    use ``score`` for its Bayesian points. ``code`` and ``provisional`` are SVCv4
    profile extensions.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str | None = Field(
        default=None,
        description="VA-Spec `id` (0..1): stable identifier for this Statement.",
    )
    type: Literal["Statement"] = Field(
        default="Statement",
        description="VA-Spec entity `type` (1..1); always `Statement`.",
    )
    name: str | None = Field(
        default=None,
        description="VA-Spec `name` (0..1): a short human-readable label.",
    )
    aliases: list[str] = Field(
        default_factory=list,
        description="VA-Spec `aliases` (0..m): alternate names/identifiers.",
    )
    extensions: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "VA-Spec `extensions` (0..m): profile/implementation-specific Extension objects."
        ),
    )
    proposition: Proposition | None = Field(
        default=None,
        description=(
            "The SPOQ proposition (VBC subject / predicate / MDE object). "
            "Present on the top-level classification; omitted on nested "
            "evidence-line Statements (0..1 per VA-Spec 1.1.0)."
        ),
    )
    specified_by: Method | None = Field(
        default=None,
        alias="specifiedBy",
        description=(
            "VA-Spec `specifiedBy`: the Method this Statement was produced by. "
            "At top level, the applied SVCv4 specification version (baseline or "
            "VCEP-specialised, resolving into CSpec); at line level, the CSpec "
            "method/rule invoked."
        ),
    )
    code: str | None = Field(
        default=None,
        description=(
            "SVCv4 profile extension: the Evidence Code / subcode identity of an "
            "evidence-line Statement (e.g. `POP_FRQ`, `MIS_PRD`). Omitted on the "
            "top-level classification."
        ),
    )
    score: float = Field(
        description=(
            "The composed (top level) or produced (line level) SVCv4 points. "
            "VA-Spec core deprecates `score`; SVCv4 retains it as its Bayesian "
            "point value."
        ),
    )
    direction: Literal["supports", "neutral", "disputes"] = Field(
        description=(
            "VA-Spec direction relative to the proposition (required, 1..1 per "
            "1.1.0-ballot.2026-09): `supports` when `score` > 0, `neutral` when "
            "`score` == 0, `disputes` when `score` < 0."
        ),
    )
    strength: str | None = Field(
        default=None,
        description=(
            "VA-Spec strength (0..1, Mappable Concept; open vocabulary) — e.g. "
            "`supporting`, `moderate`, `strong`."
        ),
    )
    outcome: str | None = Field(
        default=None,
        description=(
            "VA-Spec outcome (0..1, Mappable Concept): the coded result label — "
            "the classification tier at top level (e.g. `likely_pathogenic`) or "
            "the spec-nomenclature code at line level (e.g. `POP_FRQ_-3`)."
        ),
    )
    provisional: bool = Field(
        default=False,
        description=(
            "SVCv4 profile extension: True when `code` is a provisional SVCv4 "
            "code/subcode (combination-cap or deeper method-level) not yet in "
            "the official code list."
        ),
    )
    contribution: float | None = Field(
        default=None,
        description="Optional weighted contribution to the parent Statement's score.",
    )
    has_evidence_items: list[DataItem] = Field(
        default_factory=list,
        alias="hasEvidenceItems",
        description=(
            "VA-Spec `hasEvidenceItems` (0..m): the Data Items / Study Results "
            "consumed by this Statement."
        ),
    )
    has_evidence_lines: list[Statement] = Field(
        default_factory=list,
        alias="hasEvidenceLines",
        description=(
            "VA-Spec `hasEvidenceLines` (0..m Statement): nested evidence-line "
            "assessments composing into this Statement (concept → code → "
            "subcode)."
        ),
    )
    description: str | None = Field(
        default=None,
        description="Optional prose summary.",
    )


# Resolve the self-referential ``hasEvidenceLines`` forward reference.
Statement.model_rebuild()
