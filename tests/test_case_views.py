"""Tests for the per-workflow Case schema views."""

from __future__ import annotations

import json
from pathlib import Path

import scripts.export_case_views as exporter
from svcv4_model.case import Workflow
from svcv4_model.case_applicability import load_matrix

REPO_ROOT = Path(__file__).resolve().parent.parent
CASE_SCHEMA_DIR = REPO_ROOT / "schemas" / "json" / "case"


def test_each_workflow_schema_exists() -> None:
    for workflow in Workflow:
        assert (CASE_SCHEMA_DIR / f"{workflow.value}.schema.json").exists()


def test_committed_schemas_match_generated() -> None:
    """Mirrors CI: regenerating must not change the committed per-workflow schemas."""
    for workflow in Workflow:
        committed = json.loads((CASE_SCHEMA_DIR / f"{workflow.value}.schema.json").read_text())
        generated = exporter.build_workflow_schema(workflow)
        assert committed == generated, f"{workflow.value} schema is stale; re-run the exporter"


def test_not_applicable_fields_are_removed() -> None:
    dnv = json.loads((CASE_SCHEMA_DIR / "CLN_DNV.schema.json").read_text())
    assert "compound_het_variant" not in dnv["properties"]
    assert "additional_variants" not in dnv["properties"]


def test_required_matches_matrix_top_level() -> None:
    matrix = load_matrix()
    for workflow in Workflow:
        schema = json.loads((CASE_SCHEMA_DIR / f"{workflow.value}.schema.json").read_text())
        expected = {
            path
            for path, entry in matrix.items()
            if "." not in path and entry["applicability"][workflow.value] == "r"
        }
        assert set(schema.get("required", [])) == expected, workflow.value


def test_fixed_rule_becomes_const() -> None:
    aff = json.loads((CASE_SCHEMA_DIR / "CLN_AFF.schema.json").read_text())
    che = aff["properties"]["compound_het_variant"]["properties"]
    assert che["zygosity"]["const"] == "HET"
    assert che["phase_in_ref_to_vbc"]["const"] == "TRANS"


def test_enum_exclude_drops_token_for_altg() -> None:
    altg = json.loads((CASE_SCHEMA_DIR / "CLN_ALTG.schema.json").read_text())
    severity = altg["properties"]["case_proband_info"]["properties"]["pheno_severity"]
    assert "BIALLELIC_LT_EXPECTED" not in severity["enum"]
