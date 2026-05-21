"""Validate every JSON file in ``examples/`` against the model.

For each example file the script:

1. Loads the JSON.
2. Round-trips it through `svcv4_model.Statement.model_validate(...)`
   (i.e. asserts it conforms to the Pydantic model).
3. Validates it against the generated `schemas/json/Statement.schema.json`
   using ``jsonschema`` (i.e. asserts schema and model agree).

Exits non-zero on any failure. Run from the repo root:

    uv run python scripts/validate_examples.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

from svcv4_model import Statement

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
SCHEMA_PATH = REPO_ROOT / "schemas" / "json" / "Statement.schema.json"


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(
            f"ERROR: {SCHEMA_PATH.relative_to(REPO_ROOT)} not found. "
            f"Run `uv run python scripts/export_schemas.py` first.",
            file=sys.stderr,
        )
        return 2

    schema = json.loads(SCHEMA_PATH.read_text())
    validator = jsonschema.Draft202012Validator(schema)

    example_files = sorted(EXAMPLES_DIR.glob("*.json"))
    if not example_files:
        print(f"No example files found under {EXAMPLES_DIR.relative_to(REPO_ROOT)}/.")
        return 0

    failures = 0
    for path in example_files:
        rel = path.relative_to(REPO_ROOT).as_posix()
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            print(f"FAIL {rel}: invalid JSON — {exc}", file=sys.stderr)
            failures += 1
            continue

        try:
            Statement.model_validate(payload)
        except Exception as exc:  # noqa: BLE001 — surface any model error
            print(f"FAIL {rel}: Pydantic validation — {exc}", file=sys.stderr)
            failures += 1
            continue

        schema_errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
        if schema_errors:
            for err in schema_errors:
                loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
                print(f"FAIL {rel}: JSON Schema [{loc}] — {err.message}", file=sys.stderr)
            failures += len(schema_errors)
            continue

        print(f"OK   {rel}")

    if failures:
        print(f"\n{failures} validation failure(s) across examples.", file=sys.stderr)
        return 1
    print(f"\nAll {len(example_files)} example(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
