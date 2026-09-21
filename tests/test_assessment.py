"""Tests for the assessment registry: patterns, rulesets, hierarchy, specialization."""

from __future__ import annotations

import pytest

from svcv4_model import (
    ASSESSMENT_TYPES,
    RULESETS,
    Method,
    Ruleset,
    Statement,
    children,
    make_ruleset_id,
    parse_ruleset_id,
    resolve,
    roots,
)


def test_every_ruleset_references_a_known_pattern() -> None:
    for r in RULESETS.values():
        assert r.method_type in ASSESSMENT_TYPES


def test_every_ruleset_parent_exists() -> None:
    for r in RULESETS.values():
        if r.parent is not None:
            assert r.parent in RULESETS


def test_svcv4_method_root_composes_the_code_families() -> None:
    assert {r.code for r in roots()} == {"SVCV4"}
    kids = {c.code for c in children("svcv4:SVCV4:1.0")}
    assert kids == {"POP", "CLN", "LOC", "MIS", "NUL", "CDS", "SPL"}


def test_id_round_trips() -> None:
    rid = make_ruleset_id("gene-MYH7", "MIS_PRD_INIT_REVEL", "1.0")
    assert parse_ruleset_id(rid) == ("gene-MYH7", "MIS_PRD_INIT_REVEL", "1.0")


def test_a_pattern_is_reused_across_distinct_rulesets() -> None:
    """methodType (pattern) recurs; ruleset ids do not."""
    mis_fxn = resolve("svcv4:MIS_FXN:1.0")
    nul_fxn = resolve("svcv4:NUL_FXN:1.0")
    assert mis_fxn.method_type == nul_fxn.method_type == "functional-assay-assessment"
    assert mis_fxn.id != nul_fxn.id


def test_hierarchy_is_navigable() -> None:
    mis_prd = "svcv4:MIS_PRD:1.0"
    kids = {c.code for c in children(mis_prd)}
    assert kids == {"MIS_PRD_INIT_REVEL", "MIS_PRD_EXON"}
    assert resolve(mis_prd).parent == "svcv4:MIS:1.0"


def test_specialization_overrides_one_node_by_id() -> None:
    base = resolve("svcv4:MIS_PRD_INIT_REVEL:1.0")
    spec = resolve("svcv4-gene-MYH7:MIS_PRD_INIT_REVEL:1.0")
    assert base.method_type == spec.method_type  # same pattern
    assert base.id != spec.id and base.scope != spec.scope  # distinct ruleset id
    assert spec.params["predictor"] == "REVEL(MYH7-recalibrated)"


def test_bad_id_is_rejected() -> None:
    with pytest.raises(ValueError):
        Ruleset(
            id="not-valid",
            code="POP",
            label="x",
            method_type="population-observation-assessment",
            scope="baseline",
        )


def test_two_statements_same_methodtype_different_specifiedby() -> None:
    """A ruleset drives specifiedBy: same methodType, distinct code-based id."""
    base_id = "svcv4:MIS_PRD_INIT_REVEL:1.0"
    spec_id = "svcv4-gene-MYH7:MIS_PRD_INIT_REVEL:1.0"
    mt = resolve(base_id).method_type
    base = Statement(
        code="MIS_PRD_INIT_REVEL",
        score=3.0,
        direction="supports",
        specified_by=Method(code="svcv4:MIS_PRD_INIT_REVEL", id=base_id, method_type=mt),
    )
    spec = Statement(
        code="MIS_PRD_INIT_REVEL",
        score=4.0,
        direction="supports",
        specified_by=Method(code="svcv4:MIS_PRD_INIT_REVEL", id=spec_id, method_type=mt),
    )
    assert base.specified_by.method_type == spec.specified_by.method_type == mt
    assert base.specified_by.id != spec.specified_by.id
    assert resolve(base.specified_by.id).scope == "baseline"
    assert resolve(spec.specified_by.id).scope == "gene-MYH7"
