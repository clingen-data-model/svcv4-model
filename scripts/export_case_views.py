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
DOCS_PAGE = REPO_ROOT / "docs" / "workflows" / "case-model.md"
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


#: Display labels for each workflow.
WORKFLOW_LABELS = {
    "CLN_AFF": "Affected",
    "CLN_DNV": "De novo",
    "CLN_ALTV": "Alternative Cause-Variant",
    "CLN_ALTG": "Alternative Cause-Gene",
    "CLN_UAF": "Unaffected",
}

#: Applicability code -> CSS class (bold / underline / italic / dim).
APPL_CLASS = {"r": "appl-r", "c": "appl-c", "o": "appl-o", "x": "appl-x"}

#: Array-valued (0..many) fields, by dotted path. Asserted against the matrix.
ARRAYS = {"case_proband_info.phenotypes", "additional_variants"}

#: Mock values for leaf fields, used in the per-workflow JSON examples.
MOCK: dict[str, object] = {
    "moi": "AD",
    "pop_frq_points": 0,
    "case_proband_info.sex": "F",
    "case_proband_info.age": {"value": 7, "unit": "MONTH", "qualifier": "EXACT", "raw": "7 mo"},
    "case_proband_info.phenotypes.code": "HP:0001250",
    "case_proband_info.phenotypes.name": "Seizure",
    "case_proband_info.pheno_specificity_for_gene": "SPECIFIC",
    "case_proband_info.pheno_severity": "MONO_EQ_EXPECTED",
    "case_proband_info.age_matched_penetrance": "NEAR_100",
    "case_proband_info.confirmed_parental_relationship": "TRUE",
    "case_proband_info.all_relevant_genes_tested": "TRUE",
    "vbc.id": "clinvar:VCV000000001",
    "vbc.zygosity": "HET",
    "compound_het_variant.id": "clinvar:VCV000000002",
    "compound_het_variant.zygosity": "HET",
    "compound_het_variant.phase_in_ref_to_vbc": "TRANS",
    "compound_het_variant.phase_confidence": "HIGH",
    "compound_het_variant.classification": "P",
    "additional_variants.id": "clinvar:VCV000000003",
    "additional_variants.gene.symbol": "ABCA4",
    "additional_variants.gene.mde_associated_gene": "ABCA4",
    "additional_variants.zygosity": "HOM",
    "additional_variants.phase_in_ref_to_vbc": "CIS",
    "additional_variants.phase_confidence": "LOW",
    "additional_variants.classification": "LP",
}


def _build_tree() -> dict:
    """Build an ordered nested tree of field nodes from the matrix dotted paths.

    Each node is ``{"name", "path", "children": {name: node, ...}}``; a node with
    children is a container, and a container whose path is in ``ARRAYS`` is a list.
    """
    root: dict = {}
    for path in load_matrix():
        cur, acc = root, ""
        for i, part in enumerate(path.split(".")):
            acc = part if i == 0 else f"{acc}.{part}"
            cur = cur.setdefault(part, {"name": part, "path": acc, "children": {}})["children"]
    return root


def _appl_span(code: str) -> str:
    return f'<span class="{APPL_CLASS[code]}">{code.upper()}</span>'


def _notes_for(entry: dict) -> str:
    bits: list[str] = []
    if entry.get("value"):
        bits.append(str(entry["value"]))
    if entry.get("notes"):
        bits.append(str(entry["notes"]))
    rule = entry.get("rule")
    if rule:
        if rule.get("effect") == "fixed":
            bits.append(f"fixed = `{rule['value']}` ({rule['workflow']})")
        elif rule.get("effect") == "enum_exclude":
            bits.append(f"{rule['workflow']} excludes `{rule['value']}`")
        elif "requires" in rule:
            req = rule["requires"]
            if "field" in req:
                bits.append(f"requires `{req['field']} == {req.get('equals')}`")
            elif "context" in req:
                bits.append(str(req["context"]))
    return " — ".join(bits).replace("|", "\\|")


def _matrix_table() -> str:
    """The superset matrix: every field (hierarchy preserved) × the five workflows."""
    matrix = load_matrix()
    cols = list(Workflow)
    short = [w.value.replace("CLN_", "") for w in cols]
    header = "| " + " | ".join(short) + " | Property | Notes |"
    sep = "|" + "---|" * (len(cols) + 2)
    lines = [header, sep]
    for path, entry in matrix.items():
        depth = path.count(".")
        name = path.split(".")[-1]
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth
        prop = f"{indent}{'↳ ' if depth else ''}`{name}`"
        cells = " | ".join(_appl_span(entry["applicability"][w.value]) for w in cols)
        lines.append(f"| {cells} | {prop} | {_notes_for(entry)} |")
    table = "\n".join(lines)
    return f'<div class="appl-matrix" markdown="1">\n\n{table}\n\n</div>'


def _value_html(path: str) -> str:
    val = MOCK.get(path, "...")
    if isinstance(val, bool):
        return f'<span class="j-num">{str(val).lower()}</span>'
    if isinstance(val, (int, float)):
        return f'<span class="j-num">{val}</span>'
    if isinstance(val, dict):
        parts = []
        for k, v in val.items():
            vv = (
                f'<span class="j-str">"{v}"</span>'
                if isinstance(v, str)
                else f'<span class="j-num">{v}</span>'
            )
            parts.append(f'<span class="j-key">"{k}"</span>: {vv}')
        return "{ " + ", ".join(parts) + " }"
    return f'<span class="j-str">"{val}"</span>'


def _emit_obj(children: dict, codes: dict[str, str], indent: int) -> list[str]:
    pad = "  " * indent
    items = [(n, node) for n, node in children.items() if codes.get(node["path"]) != "x"]
    out: list[str] = []
    for idx, (name, node) in enumerate(items):
        comma = "," if idx < len(items) - 1 else ""
        cls = APPL_CLASS[codes[node["path"]]]
        key = f'<span class="j-key {cls}">"{name}"</span>'
        if node["children"]:
            if node["path"] in ARRAYS:
                out.append(f"{pad}{key}: [")
                out.append(f"{pad}  {{")
                out += _emit_obj(node["children"], codes, indent + 2)
                out.append(f"{pad}  }}")
                out.append(f"{pad}]{comma}")
            else:
                out.append(f"{pad}{key}: {{")
                out += _emit_obj(node["children"], codes, indent + 1)
                out.append(f"{pad}}}{comma}")
        else:
            out.append(f"{pad}{key}: {_value_html(node['path'])}{comma}")
    return out


def _workflow_block(workflow: Workflow, tree: dict) -> str:
    codes = {p: e["applicability"][workflow.value] for p, e in load_matrix().items()}
    body = "\n".join(["{", *_emit_obj(tree, codes, 1), "}"])
    label = WORKFLOW_LABELS[workflow.value]
    return (
        f'<details class="appl-detail">\n'
        f"<summary>{label} <code>{workflow.value}</code></summary>\n"
        f'<pre class="appl-json">\n{body}\n</pre>\n'
        f"</details>"
    )


def write_docs_tables() -> None:
    assert set(load_matrix()) >= ARRAYS, "ARRAYS contains a path missing from the matrix"
    tree = _build_tree()
    legend = (
        "**Legend:** "
        '<span class="appl-r">required (R)</span> &nbsp;·&nbsp; '
        '<span class="appl-c">conditional (C)</span> &nbsp;·&nbsp; '
        '<span class="appl-o">optional (O)</span> &nbsp;·&nbsp; '
        '<span class="appl-x">not applicable (X)</span>'
    )
    blocks = "\n\n".join(_workflow_block(w, tree) for w in Workflow)
    body = "\n\n".join(
        [
            legend,
            "### Superset matrix",
            "Every Case attribute across the five CLN workflows, with the nested "
            "structure preserved. Conditional rules are summarized in **Notes**.",
            _matrix_table(),
            "### Per-workflow structures",
            "Expand a workflow to see only its applicable fields as a JSON example "
            'with mock data — **bold** = required, <span class="appl-c">underlined</span> '
            "= conditional, *italic* = optional; not-applicable fields are omitted.",
            blocks,
        ]
    )
    text = DOCS_PAGE.read_text()
    pre, _, rest = text.partition(GEN_BEGIN)
    _, _, post = rest.partition(GEN_END)
    DOCS_PAGE.write_text(f"{pre}{GEN_BEGIN}\n\n{body}\n\n{GEN_END}{post}")


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
