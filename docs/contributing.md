# Contributing

This page covers local development for the `svcv4-model` repository.

## Prerequisites

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) for dependency management

## Install

From the repo root:

```sh
uv sync --all-groups
```

This installs the package itself (in editable mode), the dev
dependencies (pytest, ruff, jsonschema), and the docs dependencies
(mkdocs + Material + mkdocstrings).

## Common commands

```sh
# Lint
uv run ruff check .
uv run ruff format --check .

# Tests
uv run pytest

# Regenerate JSON Schemas after a model change
uv run python scripts/export_schemas.py

# Validate every example fixture
uv run python scripts/validate_examples.py

# Serve the docs locally
uv run mkdocs serve
```

## How to add or change a model class

1. Edit the relevant module under `src/svcv4_model/`.
2. Re-export new public names from `src/svcv4_model/__init__.py` if
   you want them in `__all__` (and therefore in the generated
   schemas).
3. Add or update tests under `tests/`.
4. Re-run `uv run python scripts/export_schemas.py`. The committed
   `schemas/json/*.json` must match the freshly generated output, or
   CI will fail.
5. Validate the examples still pass: `uv run python scripts/validate_examples.py`.

## How to add a worked example

1. Create a new `*.json` file under `examples/` whose top-level shape
   conforms to `Statement`.
2. Add a row to `examples/README.md`.
3. Add a paragraph to `docs/examples/index.md` describing what the
   example illustrates.
4. Run `uv run python scripts/validate_examples.py`.

## Style

- Ruff is configured in `pyproject.toml` (line length 100, target
  Python 3.11, selected lint rules `E F I B UP SIM`). Match the
  existing style; format with `uv run ruff format`.
- Pydantic models use `model_config = ConfigDict(extra="forbid")` —
  schema strictness is intentional. Don't relax it without a reason
  documented in the diff.
- Every public field has a `Field(..., description="...")`. That
  description ends up in the JSON Schema and the rendered docs;
  keep it accurate.

## Releasing

Release tooling will land when the first published release is in
sight. Until then, the model is still pre-1.0 and breaking changes
are expected.
