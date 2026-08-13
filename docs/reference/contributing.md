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

## How to add or encode a worked example

Worked examples are the [Practice Variant Set](../examples/practice-variant-set/index.md) —
one entry per spreadsheet tab under `examples/practice-variant-set/<slug>/`. To
encode a captured entry:

1. Add `mapping.md` (which model fields each source value maps to, plus the
   workflow assignment), a validated `case-<WORKFLOW>.json` for the primary
   workflow, and a rolled-up `classification.json` conforming to `Statement`.
2. Validate: `uv run python scripts/validate_examples.py`.
3. Generate its page: `uv run python scripts/export_example_pages.py` (writes
   `docs/examples/practice-variant-set/<slug>.md` from the fixtures).
4. Add the page to the `Examples` nav in `mkdocs.yml` and refresh the catalog
   status/link in `docs/examples/practice-variant-set/index.md`.

The synthetic `examples/classification-example-01.json` scaffold remains only as
a minimal `Statement` test fixture; new examples come from the pilots.

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
