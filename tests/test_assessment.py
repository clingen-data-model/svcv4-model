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


def test_svcv4_method_composes_hod_and_prd() -> None:
    assert {r.code for r in roots()} == {"SVCV4"}
    assert {c.code for c in children("svcv4:SVCV4:1.0")} == {"HOD", "PRD"}
    assert {c.code for c in children("svcv4:HOD:1.0")} == {"POP", "CLN", "LOC"}
    assert {c.code for c in children("svcv4:PRD:1.0")} == {"MIS", "NUL", "CDS", "SPL"}


def test_id_round_trips() -> None:
    rid = make_ruleset_id("gene-MYH7", "MIS_PRD_INIT_INSILICO", "1.0")
    assert parse_ruleset_id(rid) == ("gene-MYH7", "MIS_PRD_INIT_INSILICO", "1.0")


def test_a_pattern_is_reused_across_distinct_rulesets() -> None:
    """methodType (pattern) recurs; ruleset ids do not."""
    mis_er = resolve("svcv4:MIS_PRD_EXON_REL:1.0")
    nul_er = resolve("svcv4:NUL_PRD_EXON_REL:1.0")
    assert mis_er.method_type == nul_er.method_type == "exon-relevance-assessment"
    assert mis_er.id != nul_er.id
    # same pattern, different config: missense excludes gene-disease mechanism
    assert mis_er.params["include_mechanism"] is False
    assert nul_er.params["include_mechanism"] is True


def test_hierarchy_is_navigable() -> None:
    mis_prd = "svcv4:MIS_PRD:1.0"
    kids = {c.code for c in children(mis_prd)}
    assert kids == {"MIS_PRD_INIT_INSILICO", "MIS_PRD_EXON_REL"}
    assert resolve(mis_prd).parent == "svcv4:MIS_PRD_FXN:1.0"


def test_insilico_subcode_is_tool_agnostic() -> None:
    """The predictor tool lives in params, not the code."""
    r = resolve("svcv4:MIS_PRD_INIT_INSILICO:1.0")
    assert "REVEL" not in r.code
    assert r.method_type == "insilico-predictor-assessment"
    assert "REVEL" in r.params["selectable_tools"]


def test_prd_init_spectra_are_or_siblings() -> None:
    """NUL predictive-init offers the OR-selected impact spectra + exon-relevance."""
    kids = {c.code for c in children("svcv4:NUL_PRD:1.0")}
    assert kids == {
        "NUL_PRD_INIT_PROT_IMP",
        "NUL_PRD_INIT_ALT_START_IMP",
        "NUL_PRD_INIT_ALT_START_FXN",
        "NUL_PRD_INIT_MECH_IMP",
        "NUL_PRD_EXON_REL",
    }


def test_specialization_overrides_one_node_by_id() -> None:
    base = resolve("svcv4:MIS_PRD_INIT_INSILICO:1.0")
    spec = resolve("svcv4-gene-MYH7:MIS_PRD_INIT_INSILICO:1.0")
    assert base.method_type == spec.method_type  # same pattern
    assert base.id != spec.id and base.scope != spec.scope  # distinct ruleset id
    assert spec.params["selected_tool"] == "REVEL"


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
    base_id = "svcv4:MIS_PRD_INIT_INSILICO:1.0"
    spec_id = "svcv4-gene-MYH7:MIS_PRD_INIT_INSILICO:1.0"
    mt = resolve(base_id).method_type
    base = Statement(
        code="MIS_PRD_INIT_INSILICO",
        score=3.0,
        direction="supports",
        specified_by=Method(code="svcv4:MIS_PRD_INIT_INSILICO", id=base_id, method_type=mt),
    )
    spec = Statement(
        code="MIS_PRD_INIT_INSILICO",
        score=4.0,
        direction="supports",
        specified_by=Method(code="svcv4:MIS_PRD_INIT_INSILICO", id=spec_id, method_type=mt),
    )
    assert base.specified_by.method_type == spec.specified_by.method_type == mt
    assert base.specified_by.id != spec.specified_by.id
    assert resolve(base.specified_by.id).scope == "baseline"
    assert resolve(spec.specified_by.id).scope == "gene-MYH7"


def test_hod_count_grouping_cells() -> None:
    """HOD codes group similar cases into cells (n x per-case) under the code."""
    mono = {c.code for c in children("svcv4:CLN_AFF_MONO:1.0")}
    assert "CLN_AFF_MONO_CONS_THOR" in mono
    assert resolve("svcv4:CLN_AFF_MONO_CONS_THOR:1.0").method_type == (
        "case-count-grouping-assessment"
    )
    assert {c.code for c in children("svcv4:POP_HMZ:1.0")} == {"POP_HMZ_DOM", "POP_HMZ_OTH"}
