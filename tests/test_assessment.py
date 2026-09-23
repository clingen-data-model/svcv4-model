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
    assert {c.code for c in children("svc:SVCV4:4.0")} == {"HOD", "PFD"}
    assert {c.code for c in children("svc:HOD:4.0")} == {"POP", "CLN", "LOC"}
    assert {c.code for c in children("svc:PFD:4.0")} == {"PFD_ROUTER"}
    assert {c.code for c in children("svc:PFD_ROUTER:4.0")} == {"MIS", "NUL", "CDS", "SPL"}


def test_id_round_trips() -> None:
    rid = make_ruleset_id("gene-MYH7", "MIS_PRD_INIT_INSILICO", "4.0")
    assert parse_ruleset_id(rid) == ("gene-MYH7", "MIS_PRD_INIT_INSILICO", "4.0")


def test_a_pattern_is_reused_across_distinct_rulesets() -> None:
    """methodType (pattern) recurs; ruleset ids do not."""
    mis_er = resolve("svc:MIS_PRD_EXON_REL:4.0")
    nul_er = resolve("svc:NUL_PRD_EXON_REL:4.0")
    assert mis_er.method_type == nul_er.method_type == "exon-relevance-assessment"
    assert mis_er.id != nul_er.id
    # same pattern, different config: missense configures no mechanism type;
    # the null family configures a "LOF" mechanism-classification type
    assert mis_er.params["mechanism_bands"] == []
    assert [b["mechanism_type"] for b in nul_er.params["mechanism_bands"]] == ["LOF"]


def test_hierarchy_is_navigable() -> None:
    mis_prd = "svc:MIS_PRD:4.0"
    kids = {c.code for c in children(mis_prd)}
    assert kids == {"MIS_PRD_INIT_INSILICO", "MIS_PRD_EXON_REL"}
    assert resolve(mis_prd).parent == "svc:MIS_PRD_FXN:4.0"


def test_insilico_subcode_is_tool_agnostic() -> None:
    """The predictor tool lives in params, not the code."""
    r = resolve("svc:MIS_PRD_INIT_INSILICO:4.0")
    assert "REVEL" not in r.code
    assert r.method_type == "insilico-predictor-assessment"
    assert "REVEL" in r.params["selectable_tools"]


def test_prd_init_spectra_are_or_siblings() -> None:
    """NUL predictive-init offers the OR-selected impact spectra + exon-relevance."""
    kids = {c.code for c in children("svc:NUL_PRD:4.0")}
    assert kids == {
        "NUL_PRD_INIT_PROT_IMP",
        "NUL_PRD_INIT_ALT_START_IMP",
        "NUL_PRD_INIT_ALT_START_FXN",
        "NUL_PRD_INIT_MECH_IMP",
        "NUL_PRD_EXON_REL",
    }


def test_specialization_overrides_one_node_by_id() -> None:
    base = resolve("svc:MIS_PRD_INIT_INSILICO:4.0")
    spec = resolve("svc-gene-MYH7:MIS_PRD_INIT_INSILICO:4.0")
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
    base_id = "svc:MIS_PRD_INIT_INSILICO:4.0"
    spec_id = "svc-gene-MYH7:MIS_PRD_INIT_INSILICO:4.0"
    mt = resolve(base_id).method_type
    base = Statement(
        code="MIS_PRD_INIT_INSILICO",
        score=3.0,
        direction="supports",
        specified_by=Method(code="svc:MIS_PRD_INIT_INSILICO", id=base_id, method_type=mt),
    )
    spec = Statement(
        code="MIS_PRD_INIT_INSILICO",
        score=4.0,
        direction="supports",
        specified_by=Method(code="svc:MIS_PRD_INIT_INSILICO", id=spec_id, method_type=mt),
    )
    assert base.specified_by.method_type == spec.specified_by.method_type == mt
    assert base.specified_by.id != spec.specified_by.id
    assert resolve(base.specified_by.id).scope == "baseline"
    assert resolve(spec.specified_by.id).scope == "gene-MYH7"


def test_hod_count_grouping_cells() -> None:
    """HOD codes group similar cases into cells (n x per-case) under the code."""
    mono = {c.code for c in children("svc:CLN_AFF_MONO:4.0")}
    assert "CLN_AFF_MONO_CONS_THOR" in mono
    assert resolve("svc:CLN_AFF_MONO_CONS_THOR:4.0").method_type == (
        "case-count-grouping-assessment"
    )
    assert {c.code for c in children("svc:POP_HMZ:4.0")} == {"POP_HMZ_DOM", "POP_HMZ_OTH"}


def test_pfd_router_selects_family_from_consequence() -> None:
    """The PFD variant-impact router carries the consequence→family route map."""
    from svcv4_model.assessment import ASSESSMENT_TYPES
    from svcv4_model.inputs import VBC, MolecularConsequence

    r = resolve("svc:PFD_ROUTER:4.0")
    pat = ASSESSMENT_TYPES[r.method_type]
    assert pat.group == "router" and pat.output_kind == "route"
    assert [di.role for di in pat.data_items] == ["router"]

    route = r.params["route_map"]
    assert route["MISSENSE"] == ["MIS"]  # unambiguous
    assert route["SPLICE"] == ["SPL"]
    assert route["INFRAME_INDEL"] == ["CDS"]
    assert set(route["FRAMESHIFT"]) == {"NUL", "CDS"}  # resolved by a within-workflow branch

    # every routed family is a real child of the router
    router_kids = {c.code for c in children("svc:PFD_ROUTER:4.0")}
    for fams in route.values():
        assert set(fams) <= router_kids

    # the VBC carries the routing evidence
    vbc = VBC(variation={}, molecular_consequence=MolecularConsequence.MISSENSE)
    assert vbc.molecular_consequence == "MISSENSE"
    assert route[vbc.molecular_consequence] == ["MIS"]
