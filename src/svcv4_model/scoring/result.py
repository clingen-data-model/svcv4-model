"""The reference-scorer result DTO (non-authoritative)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScoreResult:
    """A reference (NON-AUTHORITATIVE) scoring result. CSpec is authoritative.

    Holds the coded sub-code point values, any held-combined intermediates, the capped
    parent-code total, and a human-readable ``provenance`` trail (the rule/cap applied at
    each step). A sub-code that is un-scoreable / No-Data is OMITTED from ``sub_code_points``
    (never recorded as 0.0). ``authoritative`` is fixed False — constructing it True raises,
    so the non-authoritative contract cannot be bypassed.

    ``frozen=True`` prevents attribute reassignment; the ``dict``/``list`` fields are held by
    reference and are not deep-frozen — treat a returned ``ScoreResult`` as read-only.
    """

    parent_code: str | None = None
    sub_code_points: dict[str, float] = field(default_factory=dict)
    held_combined: dict[str, float] = field(default_factory=dict)
    parent_total: float | None = None
    provenance: list[str] = field(default_factory=list)
    authoritative: bool = False

    def __post_init__(self) -> None:
        if self.authoritative:
            raise ValueError(
                "ScoreResult is a reference (non-authoritative) computation; "
                "authoritative must be False — CSpec is the authoritative scorer."
            )
