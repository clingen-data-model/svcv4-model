"""Verify every fixture under examples/ validates against the model and schema."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from svcv4_model import Statement

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
SCHEMA_PATH = REPO_ROOT / "schemas" / "json" / "Statement.schema.json"

EXAMPLES = sorted(EXAMPLES_DIR.glob("*.json"))


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_loads_as_statement(path: Path) -> None:
    payload = json.loads(path.read_text())
    Statement.model_validate(payload)


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_validates_against_generated_schema(path: Path) -> None:
    if not SCHEMA_PATH.exists():
        pytest.skip("Run `uv run python scripts/export_schemas.py` first.")
    schema = json.loads(SCHEMA_PATH.read_text())
    payload = json.loads(path.read_text())
    jsonschema.Draft202012Validator(schema).validate(payload)
