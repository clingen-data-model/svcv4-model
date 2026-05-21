"""Smoke tests for the svcv4_model placeholder Pydantic classes."""

from __future__ import annotations

import pytest

from svcv4_model import (
    MDE,
    VBC,
    EvidenceData,
    EvidenceItem,
    EvidenceLine,
    Method,
    Predicate,
    Proposition,
    Statement,
    VariantPathogenicityClassification,
)


def _make_statement() -> Statement:
    return Statement(
        proposition=Proposition(
            subject=VBC(variation={"id": "ga4gh:VA.test", "type": "Allele"}),
            object=MDE(curie="MONDO:0007254", label="Test disease"),
        ),
        method=Method(code="svcv4:baseline", version="test"),
        final_score=4.0,
        score_classification=VariantPathogenicityClassification.LIKELY_PATHOGENIC,
        evidence_lines=[
            EvidenceLine(
                method=Method(code="svcv4:CLN_AFF"),
                evidence=[EvidenceItem(type="clinical_observation", data={"n": 4})],
                score=2.0,
            ),
        ],
    )


def test_statement_instantiates() -> None:
    statement = _make_statement()
    assert statement.final_score == 4.0
    assert statement.score_classification is VariantPathogenicityClassification.LIKELY_PATHOGENIC
    assert statement.proposition.predicate is Predicate.IS_CAUSAL_FOR
    assert len(statement.evidence_lines) == 1
    assert statement.evidence_lines[0].score == 2.0


def test_statement_round_trips_json() -> None:
    original = _make_statement()
    payload = original.model_dump(mode="json")
    rehydrated = Statement.model_validate(payload)
    assert rehydrated == original


def test_evidence_data_is_evidence_item_alias() -> None:
    """`EvidenceData` is the VA-Spec umbrella name; should be the same class."""
    assert EvidenceData is EvidenceItem


def test_extra_fields_are_forbidden_on_statement() -> None:
    """`extra='forbid'` keeps the JSON Schema strict — typos fail loudly."""
    payload = _make_statement().model_dump(mode="json")
    payload["unexpected_field"] = "should fail"
    with pytest.raises(ValueError):
        Statement.model_validate(payload)
