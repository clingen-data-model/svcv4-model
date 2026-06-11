"""Generate per-workflow Case schema views and docs tables from the matrix.

For each CLN workflow this prunes the superset ``Case`` JSON Schema:
  * fields marked ``x`` (not applicable) are removed,
  * fields marked ``r`` (required) are added to the object's ``required`` list,
  * ``enum_exclude`` rules drop a token from a field's enum,
  * ``fixed`` rules pin a field to a ``const``,
  * ``requires`` rules are recorded as an informational ``x-svcv4-conditional``
    annotation (NOT enforced this phase).

Outputs:
  * schemas/json/case/CLN_*.schema.json
  * the applicability tables inside docs/concepts/case-model.md (between the
    GENERATED markers)

Run from the repo root:  uv run python scripts/export_case_views.py
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from svcv4_model.case import Case, Workflow
from svcv4_model.case_applicability import load_matrix

REPO_ROOT = Path(__file__).resolve().parent.parent
CASE_SCHEMA_DIR = REPO_ROOT / "schemas" / "json" / "case"
DOCS_PAGE = REPO_ROOT / "docs" / "concepts" / "case-model.md"
GEN_BEGIN = "<!-- BEGIN GENERATED: applicability tables -->"
GEN_END = "<!-- END GENERATED: applicability tables -->"


def _flatten(node: Any) -> Any:
    """Collapse Pydantic v2 wrappers so leaf/object schemas are exposed directly.

    Pydantic v2 emits ``X | None`` as ``{"anyOf": [<X>, {"type": "null"}], ...}``
    and sometimes a single-``$ref`` field as ``{"allOf": [<X>], ...}``. We rewrite
    both to ``<X>`` (carrying over sibling keys like ``default``/``description``)
    so that nested objects expose ``properties`` and enum fields expose ``enum``
    at the top level — which is what ``_object_at``/``_apply_rule`` expect. Must
    run AFTER ``$ref`` inlining so the branch contents are concrete.
    """
    if isinstance(node, dict):
        for key in ("anyOf", "oneOf", "allOf"):
            if key in node and isinstance(node[key], list):
                branches = node[key]
                non_null = [
                    b for b in branches if not (isinstance(b, dict) and b.get("type") == "null")
                ]
                # Collapse {<X>, null} unions and single-branch allOf/anyOf wrappers,
                # but leave genuine multi-member unions (2+ non-null branches) intact.
                if len(non_null) == 1:
                    merged = dict(non_null[0])
                    for k, v in node.items():
                        if k != key:
                            merged.setdefault(k, v)
                    return _flatten(merged)
        return {k: _flatten(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_flatten(item) for item in node]
    return node


def _deref(schema: dict[str, Any]) -> dict[str, Any]:
    """Inline all ``$ref`` references, drop ``$defs``, then flatten wrappers.

    The Case models form a finite (non-recursive) tree, so naive inlining
    terminates.
    """
    defs = schema.get("$defs", {})

    def resolve(node: Any) -> Any:
        if isinstance(node, dict):
            if "$ref" in node:
                ref = node["$ref"].rsplit("/", 1)[-1]
                merged = {k: v for k, v in node.items() if k != "$ref"}
                target = copy.deepcopy(defs[ref])
                target.update(merged)
                return resolve(target)
            return {k: resolve(v) for k, v in node.items()}
        if isinstance(node, list):
            return [resolve(item) for item in node]
        return node

    root = {k: v for k, v in schema.items() if k != "$defs"}
    return _flatten(resolve(root))


def _object_at(node: dict[str, Any]) -> dict[str, Any] | None:
    """Return the object-with-properties node, descending through array ``items``."""
    if node.get("type") == "array" and isinstance(node.get("items"), dict):
        return _object_at(node["items"])
    if "properties" in node:
        return node
    return None


def _prune(node: dict[str, Any], path: str, codes: dict[str, str], rules: dict[str, dict]) -> None:
    """Recursively prune one object node in place for a single workflow."""
    obj = _object_at(node)
    if obj is None:
        return
    required: list[str] = []
    for name in list(obj["properties"].keys()):
        child_path = f"{path}.{name}" if path else name
        code = codes.get(child_path)
        prop = obj["properties"][name]
        if code == "x":
            del obj["properties"][name]
            continue
        _apply_rule(prop, child_path, rules)
        if code == "r":
            required.append(name)
        _prune(prop, child_path, codes, rules)
    if required:
        obj["required"] = required
    else:
        obj.pop("required", None)


def _apply_rule(prop: dict[str, Any], path: str, rules: dict[str, dict]) -> None:
    rule = rules.get(path)
    if not rule:
        return
    effect = rule.get("effect")
    target = _object_at(prop) or prop
    if effect == "enum_exclude" and "enum" in target:
        target["enum"] = [v for v in target["enum"] if v != rule["value"]]
    elif effect == "fixed":
        target.pop("enum", None)
        target["const"] = rule["value"]
    elif "requires" in rule:
        prop["x-svcv4-conditional"] = rule["requires"]


def build_workflow_schema(workflow: Workflow) -> dict[str, Any]:
    base = _deref(Case.model_json_schema())
    matrix = load_matrix()
    codes = {p: e["applicability"][workflow.value] for p, e in matrix.items()}
    rules = {p: e["rule"] for p, e in matrix.items() if "rule" in e}
    _prune(base, "", codes, rules)
    base["title"] = f"Case ({workflow.value})"
    base["$comment"] = (
        f"Derived view of the Case superset for the {workflow.value} workflow. "
        "Generated by scripts/export_case_views.py; do not edit by hand."
    )
    return base


def _table(workflow: Workflow) -> str:
    matrix = load_matrix()
    lines = [
        f"#### {workflow.value}",
        "",
        "| Attribute | Code | Value | Notes |",
        "|-----------|------|-------|-------|",
    ]
    for path, entry in matrix.items():
        code = entry["applicability"][workflow.value]
        value = str(entry.get("value", "")).replace("|", "\\|")
        notes = str(entry.get("notes", "")).replace("|", "\\|")
        lines.append(f"| `{path}` | {code} | {value} | {notes} |")
    return "\n".join(lines)


def write_docs_tables() -> None:
    body = "\n\n".join(_table(w) for w in Workflow)
    text = DOCS_PAGE.read_text()
    pre, _, rest = text.partition(GEN_BEGIN)
    _, _, post = rest.partition(GEN_END)
    new = f"{pre}{GEN_BEGIN}\n\n{body}\n\n{GEN_END}{post}"
    DOCS_PAGE.write_text(new)


def main() -> None:
    CASE_SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for workflow in Workflow:
        schema = build_workflow_schema(workflow)
        path = CASE_SCHEMA_DIR / f"{workflow.value}.schema.json"
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
        print(f"  - {path.relative_to(REPO_ROOT).as_posix()}")
    if DOCS_PAGE.exists():
        write_docs_tables()
        print(f"  - updated {DOCS_PAGE.relative_to(REPO_ROOT).as_posix()} (generated tables)")


if __name__ == "__main__":
    main()
