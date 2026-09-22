"""Smoke tests for the svcv4_model placeholder Pydantic classes."""

from __future__ import annotations

import pytest

from svcv4_model import (
    MDE,
    VBC,
    DataItem,
    EvidenceData,
    EvidenceItem,
    Method,
    Predicate,
    Proposition,
    Statement,
)


def _make_statement() -> Statement:
    return Statement(
        proposition=Proposition(
            subject=VBC(variation={"id": "ga4gh:VA.test", "type": "Allele"}),
            object=MDE(curie="MONDO:0007254", label="Test disease"),
        ),
        specified_by=Method(code="svc:baseline", version="test"),
        score=4.0,
        direction="supports",
        outcome="likely_pathogenic",
        has_evidence_lines=[
            Statement(
                code="CLN_AFF",
                specified_by=Method(code="svc:CLN_AFF"),
                has_evidence_items=[DataItem(subtype="clinical_observation", value={"n": 4})],
                score=2.0,
                direction="supports",
            ),
        ],
    )


def test_statement_instantiates() -> None:
    statement = _make_statement()
    assert statement.score == 4.0
    assert statement.outcome == "likely_pathogenic"
    assert statement.proposition.predicate is Predicate.IS_CAUSAL_FOR
    assert len(statement.has_evidence_lines) == 1
    assert statement.has_evidence_lines[0].score == 2.0
    assert statement.has_evidence_lines[0].code == "CLN_AFF"


def test_statement_round_trips_json() -> None:
    original = _make_statement()
    payload = original.model_dump(mode="json", by_alias=True)
    assert "hasEvidenceLines" in payload and "specifiedBy" in payload
    rehydrated = Statement.model_validate(payload)
    assert rehydrated == original


def test_evidence_data_is_evidence_item_alias() -> None:
    """`EvidenceData` is the VA-Spec umbrella name; should be the same class."""
    assert EvidenceData is DataItem and EvidenceItem is DataItem


def test_extra_fields_are_forbidden_on_statement() -> None:
    """`extra='forbid'` keeps the JSON Schema strict — typos fail loudly."""
    payload = _make_statement().model_dump(mode="json", by_alias=True)
    payload["unexpected_field"] = "should fail"
    with pytest.raises(ValueError):
        Statement.model_validate(payload)
