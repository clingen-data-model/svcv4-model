"""Tests for the Case applicability matrix and its loader."""

from __future__ import annotations

import typing

from pydantic import BaseModel

from svcv4_model.case import Case, Workflow
from svcv4_model.case_applicability import (
    VALID_CODES,
    field_paths,
    load_matrix,
    workflow_codes,
)

#: Value types whose internal fields are a single sheet attribute, not matrix paths.
LEAF_VALUE_MODELS = {"Age"}


def test_matrix_loads_and_codes_are_valid() -> None:
    matrix = load_matrix()
    assert "moi" in matrix
    for path, entry in matrix.items():
        codes = entry["applicability"]
        assert set(codes) == {w.value for w in Workflow}, f"{path} missing a workflow"
        for value in codes.values():
            assert value in VALID_CODES, f"{path} has invalid code {value!r}"


def test_every_field_applies_somewhere() -> None:
    # Each attribute must be r/o/c in at least one workflow (never x everywhere).
    for path, entry in load_matrix().items():
        assert set(entry["applicability"].values()) != {"x"}, f"{path} is x everywhere"


def test_workflow_codes_view() -> None:
    aff = workflow_codes(Workflow.CLN_AFF)
    assert aff["pop_frq_points"] == "r"
    assert aff["case_proband_info.pheno_severity"] == "x"
    assert aff["additional_variants"] == "c"


def test_field_paths_are_unique() -> None:
    paths = field_paths()
    assert len(paths) == len(set(paths))


def _nested_model(annotation: object) -> type[BaseModel] | None:
    """Return the BaseModel hiding inside `X | None`, `list[X]`, etc., or None."""
    args = typing.get_args(annotation)
    candidates = list(args) if args else [annotation]
    for candidate in candidates:
        origin = typing.get_origin(candidate)
        if origin in (list, set, tuple):
            for inner in typing.get_args(candidate):
                model = _nested_model(inner)
                if model is not None:
                    return model
        elif isinstance(candidate, type) and issubclass(candidate, BaseModel):
            return candidate
    return None


def _model_field_paths(model: type[BaseModel], prefix: str = "") -> set[str]:
    """Enumerate dotted field paths for a Pydantic model, descending into
    nested models and into list-of-model item types (arrays do not add a
    path segment; their item fields append to the array's path)."""
    paths: set[str] = set()
    for name, field in model.model_fields.items():
        path = f"{prefix}.{name}" if prefix else name
        paths.add(path)
        nested = _nested_model(field.annotation)
        if nested is not None and nested.__name__ not in LEAF_VALUE_MODELS:
            paths |= _model_field_paths(nested, path)
    return paths


def test_matrix_and_model_paths_match_exactly() -> None:
    model_paths = _model_field_paths(Case)
    matrix_paths = set(field_paths())
    assert matrix_paths - model_paths == set(), "matrix has paths the model lacks (orphans)"
    assert model_paths - matrix_paths == set(), "model has fields the matrix lacks (gaps)"
