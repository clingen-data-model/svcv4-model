"""Validate the JSON examples against the model and generated schemas.

Two sets of files are checked:

**Top-level ``examples/*.json``** — complete SVCv4 ``Statement`` payloads. Each
file:

1. Loads the JSON.
2. Round-trips through ``svcv4_model.Statement.model_validate(...)``.
3. Validates against ``schemas/json/Statement.schema.json``.

**The Practice Variant Set (``examples/practice-variant-set/``)** — per-entry
fixtures, recursively:

- ``classification.json`` — validated as a ``Statement`` (as above).
- ``case-<WORKFLOW>.json`` — the workflow submission: its nested ``case`` object
  is validated against ``schemas/json/case/<WORKFLOW>.schema.json`` and the
  Pydantic ``Case`` model; the surrounding ``vbc``/``mde``/``moi``/
  ``pop_frq_points`` are validated against ``WorkflowParameters``.

Exits non-zero on any failure. Run from the repo root:

    uv run python scripts/validate_examples.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

from svcv4_model import Case, Statement, WorkflowParameters

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
PVS_DIR = EXAMPLES_DIR / "practice-variant-set"
SCHEMA_DIR = REPO_ROOT / "schemas" / "json"
STATEMENT_SCHEMA_PATH = SCHEMA_DIR / "Statement.schema.json"
WORKFLOW_PARAMS_SCHEMA_PATH = SCHEMA_DIR / "WorkflowParameters.schema.json"
CASE_SCHEMA_DIR = SCHEMA_DIR / "case"


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _validate_statement(path: Path, validator: jsonschema.Draft202012Validator) -> int:
    """Validate one file as a ``Statement``. Returns the failure count (0 = OK)."""
    rel = _rel(path)
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"FAIL {rel}: invalid JSON — {exc}", file=sys.stderr)
        return 1

    try:
        Statement.model_validate(payload)
    except Exception as exc:  # noqa: BLE001 — surface any model error
        print(f"FAIL {rel}: Pydantic validation — {exc}", file=sys.stderr)
        return 1

    schema_errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    if schema_errors:
        for err in schema_errors:
            loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
            print(f"FAIL {rel}: JSON Schema [{loc}] — {err.message}", file=sys.stderr)
        return len(schema_errors)

    print(f"OK   {rel}")
    return 0


def _validate_case_submission(path: Path) -> int:
    """Validate one ``case-<WORKFLOW>.json`` submission. Returns the failure count."""
    rel = _rel(path)
    workflow = path.stem.removeprefix("case-")
    case_schema_path = CASE_SCHEMA_DIR / f"{workflow}.schema.json"
    if not case_schema_path.exists():
        print(
            f"FAIL {rel}: no case schema for workflow '{workflow}' "
            f"({_rel(case_schema_path)} not found)",
            file=sys.stderr,
        )
        return 1

    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"FAIL {rel}: invalid JSON — {exc}", file=sys.stderr)
        return 1
    if "case" not in payload:
        print(f"FAIL {rel}: missing top-level 'case' object", file=sys.stderr)
        return 1

    case_obj = payload["case"]
    wf_params = {k: v for k, v in payload.items() if k != "case"}

    failures = 0
    try:
        Case.model_validate(case_obj)
        WorkflowParameters.model_validate(wf_params)
    except Exception as exc:  # noqa: BLE001 — surface any model error
        print(f"FAIL {rel}: Pydantic validation — {exc}", file=sys.stderr)
        failures += 1

    case_schema = json.loads(case_schema_path.read_text())
    for err in sorted(
        jsonschema.Draft202012Validator(case_schema).iter_errors(case_obj),
        key=lambda e: list(e.path),
    ):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        print(f"FAIL {rel}: case schema [{loc}] — {err.message}", file=sys.stderr)
        failures += 1

    params_schema = json.loads(WORKFLOW_PARAMS_SCHEMA_PATH.read_text())
    for err in sorted(
        jsonschema.Draft202012Validator(params_schema).iter_errors(wf_params),
        key=lambda e: list(e.path),
    ):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        print(f"FAIL {rel}: workflow-params schema [{loc}] — {err.message}", file=sys.stderr)
        failures += 1

    if not failures:
        print(f"OK   {rel} (case:{workflow})")
    return failures


def main() -> int:
    if not STATEMENT_SCHEMA_PATH.exists():
        print(
            f"ERROR: {_rel(STATEMENT_SCHEMA_PATH)} not found. "
            f"Run `uv run python scripts/export_schemas.py` first.",
            file=sys.stderr,
        )
        return 2

    statement_validator = jsonschema.Draft202012Validator(
        json.loads(STATEMENT_SCHEMA_PATH.read_text())
    )

    # 1) Top-level Statement examples (non-recursive).
    statement_files = sorted(EXAMPLES_DIR.glob("*.json"))
    # 2) Practice Variant Set fixtures (recursive).
    pvs_statements = sorted(PVS_DIR.rglob("classification.json"))
    pvs_cases = sorted(PVS_DIR.rglob("case-*.json"))

    checked = 0
    failures = 0

    for path in statement_files:
        failures += _validate_statement(path, statement_validator)
        checked += 1
    for path in pvs_statements:
        failures += _validate_statement(path, statement_validator)
        checked += 1
    for path in pvs_cases:
        failures += _validate_case_submission(path)
        checked += 1

    if checked == 0:
        print(f"No example files found under {_rel(EXAMPLES_DIR)}/.")
        return 0
    if failures:
        print(
            f"\n{failures} validation failure(s) across {checked} example file(s).",
            file=sys.stderr,
        )
        return 1
    print(f"\nAll {checked} example file(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
