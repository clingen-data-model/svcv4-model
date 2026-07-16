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
import re
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
    matrix = _case_matrix()
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
    "LOC_PHE": "Locus — Phenotype",
    "LOC_SEG": "Locus — Segregation",
}

#: Applicability code -> CSS class (bold / underline / italic / dim).
APPL_CLASS = {"r": "appl-r", "c": "appl-c", "o": "appl-o", "x": "appl-x"}

#: Array-valued (0..many) fields, by dotted path. Asserted against the matrix.
ARRAYS = {
    "phenotypes",
    "relatives",
    "relatives.phenotypes",
    "additional_variants",
}


def _case_matrix() -> dict[str, dict]:
    """Matrix entries for the Case data structure (excludes workflow parameters)."""
    return {
        p: e for p, e in load_matrix().items() if e.get("model") != "workflow_parameters"
    }


def _param_matrix() -> dict[str, dict]:
    """Matrix entries for the WorkflowParameters model."""
    return {
        p: e for p, e in load_matrix().items() if e.get("model") == "workflow_parameters"
    }


#: Mock values for leaf fields, used in the per-workflow JSON examples. Keyed by
#: dotted path — workflow-parameter paths (moi, pop_frq_points) plus Case paths.
MOCK: dict[str, object] = {
    "moi": "AD",
    "pop_frq_points": 0,
    "id": "PROBAND-1",
    "family_id": "FAM-1",
    "sex": "F",
    "age": {"value": 7, "unit": "MONTH", "qualifier": "EXACT", "raw": "7 mo"},
    "phenotypes.code": "HP:0001250",
    "phenotypes.name": "Seizure",
    "pheno_specificity_for_mde": "SPECIFIC",
    "gene_specificity_for_phenotypes": "50%",
    "testing.method": "Exome",
    "testing.diagnostic_yield_for_phenotypes": "100%",
    "testing.covers_all_genes_relevant_to_mde": "TRUE",
    "pheno_severity": "MONO_EQ_EXPECTED",
    "age_matched_penetrance": "NEAR_100",
    "confirmed_parental_relationship": "TRUE",
    "relatives.parent_of_proband": "TRUE",
    "relatives.sex": "F",
    "relatives.age": {
        "value": 35,
        "unit": "YEAR",
        "qualifier": "EXACT",
        "raw": "35 yrs",
    },
    "relatives.phenotypes.code": "HP:0001250",
    "relatives.phenotypes.name": "Seizure",
    "relatives.affected_w_mde": "TRUE",
    "relatives.severe_phenotype": "FALSE",
    "relatives.vbc_exists": "TRUE",
    "relatives.vbc_zygosity": "HET",
    "relatives.cmp_het_variant_exists": "FALSE",
    # workflow parameters (vbc / mde structures)
    "vbc.id": "clinvar:VCV000000001",
    "vbc.gene.symbol": "ABCA4",
    "vbc.gene.id": "HGNC:34",
    "vbc.gene.mde_associated_gene": "ABCA4",
    "vbc.gene.transcript": "NM_000350.3",
    "mde.curie": "MONDO:0007254",
    "mde.label": "Stargardt disease",
    # case-level VBC status
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "compound_het_variant.id": "clinvar:VCV000000002",
    "compound_het_variant.phase_confidence": "HIGH",
    "compound_het_variant.classification": "P",
    "additional_variants.id": "clinvar:VCV000000003",
    "additional_variants.gene.symbol": "ABCA4",
    "additional_variants.gene.id": "HGNC:34",
    "additional_variants.gene.mde_associated_gene": "ABCA4",
    "additional_variants.gene.transcript": "NM_000350.3",
    "additional_variants.zygosity": "HOM",
    "additional_variants.phase_in_ref_to_vbc": "CIS",
    "additional_variants.phase_confidence": "LOW",
    "additional_variants.classification": "LP",
}


def _build_tree(matrix: dict | None = None) -> dict:
    """Build an ordered nested tree of field nodes from the matrix dotted paths.

    Each node is ``{"name", "path", "children": {name: node, ...}}``; a node with
    children is a container, and a container whose path is in ``ARRAYS`` is a list.
    Defaults to the Case matrix; pass ``_param_matrix()`` for the parameter tree.
    """
    root: dict = {}
    for path in matrix if matrix is not None else _case_matrix():
        cur, acc = root, ""
        for i, part in enumerate(path.split(".")):
            acc = part if i == 0 else f"{acc}.{part}"
            cur = cur.setdefault(part, {"name": part, "path": acc, "children": {}})["children"]
    return root


def _appl_span(code: str) -> str:
    return f'<span class="{APPL_CLASS[code]}">{code.upper()}</span>'


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _notes_html(entry: dict) -> str:
    """Build the Notes cell as HTML, rendering ``\\`code\\``` spans as <code>."""
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
    joined = _esc(" — ".join(bits))
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", joined)


def _row_html(path: str, entry: dict, cols: list[Workflow], child_count: dict[str, int]) -> str:
    """One tree-table row (<tr>) carrying data-* attrs for the JS collapse logic."""
    depth = path.count(".")
    name = path.split(".")[-1]
    parent = path.rsplit(".", 1)[0] if depth else ""
    n_children = child_count.get(path, 0)
    cells = "".join(
        f'<td class="appl-w">{_appl_span(entry["applicability"][w.value])}</td>' for w in cols
    )
    indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth
    toggle = f'<button class="appl-row-toggle" type="button" aria-label="toggle {name}"></button>'
    prop = f'<td class="appl-prop">{indent}{toggle}<code>{name}</code></td>'
    notes = f'<td class="appl-notes">{_notes_html(entry)}</td>'
    return (
        f'<tr class="appl-row" data-path="{path}" data-depth="{depth}" '
        f'data-parent="{parent}" data-children="{n_children}">'
        f"{cells}{prop}{notes}</tr>"
    )


def _header_html(cols: list[Workflow]) -> str:
    short = "".join(f"<th>{w.value.split('_', 1)[1]}</th>" for w in cols)
    return f"<thead><tr>{short}<th>Property</th><th>Notes</th></tr></thead>"


def _matrix_table() -> str:
    """The Case superset matrix as a collapsible tree table (raw HTML)."""
    matrix = _case_matrix()
    cols = list(Workflow)
    child_count: dict[str, int] = {}
    for path in matrix:
        if "." in path:
            child_count[path.rsplit(".", 1)[0]] = child_count.get(path.rsplit(".", 1)[0], 0) + 1
    max_depth = max((p.count(".") for p in matrix), default=0)
    level_btns = "".join(
        f'<button type="button" data-appl-level="{n}">{n}</button>'
        for n in range(1, max_depth + 2)
    )
    controls = (
        '<div class="appl-matrix-controls">'
        '<button type="button" data-appl-expand="all">Expand all</button>'
        '<button type="button" data-appl-collapse="all">Collapse all</button>'
        f'<span class="appl-level-label">Show to depth:</span>{level_btns}'
        "</div>"
    )
    rows = "".join(_row_html(p, e, cols, child_count) for p, e in matrix.items())
    table = (
        f'<table class="appl-matrix-table">{_header_html(cols)}<tbody>{rows}</tbody></table>'
    )
    return f'<div class="appl-matrix">\n{controls}\n{table}\n</div>'


def _params_table() -> str:
    """Static table for the workflow parameters (vbc, mde, moi, pop_frq_points),
    with nested structure preserved (indented by depth)."""
    cols = list(Workflow)
    rows = ""
    for path, entry in _param_matrix().items():
        depth = path.count(".")
        name = path.split(".")[-1]
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth
        cells = "".join(
            f'<td class="appl-w">{_appl_span(entry["applicability"][w.value])}</td>' for w in cols
        )
        prop = f'<td class="appl-prop">{indent}<code>{name}</code></td>'
        rows += f'<tr>{cells}{prop}<td class="appl-notes">{_notes_html(entry)}</td></tr>'
    table = (
        f'<table class="appl-matrix-table">{_header_html(cols)}<tbody>{rows}</tbody></table>'
    )
    return f'<div class="appl-params">\n{table}\n</div>'


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


def _emit_obj(
    children: dict, codes: dict[str, str], indent: int, drop: frozenset[str] = frozenset({"x"})
) -> list[str]:
    """Emit JSON-example lines for one object.

    ``drop`` is the set of applicability codes to omit: ``{"x"}`` for the full
    view, ``{"x", "o"}`` for the required-and-conditional-only view. Commas are
    computed over the *kept* items, so each rendering is independently valid.
    """
    pad = "  " * indent
    items = [(n, node) for n, node in children.items() if codes.get(node["path"]) not in drop]
    out: list[str] = []
    for idx, (name, node) in enumerate(items):
        comma = "," if idx < len(items) - 1 else ""
        cls = APPL_CLASS[codes[node["path"]]]
        key = f'<span class="j-key {cls}">"{name}"</span>'
        if node["children"]:
            if node["path"] in ARRAYS:
                out.append(f"{pad}{key}: [")
                out.append(f"{pad}  {{")
                out += _emit_obj(node["children"], codes, indent + 2, drop)
                out.append(f"{pad}  }}")
                out.append(f"{pad}]{comma}")
            else:
                out.append(f"{pad}{key}: {{")
                out += _emit_obj(node["children"], codes, indent + 1, drop)
                out.append(f"{pad}}}{comma}")
        else:
            out.append(f"{pad}{key}: {_value_html(node['path'])}{comma}")
    return out


def _workflow_block(workflow: Workflow, tree: dict) -> str:
    # The example is the full workflow input: the workflow parameters that apply
    # (moi, pop_frq_points) plus a nested `case` object holding the pruned Case
    # tree. Build a synthetic root so `_emit_obj` renders params + case together.
    case_codes = {p: e["applicability"][workflow.value] for p, e in _case_matrix().items()}
    param_codes = {p: e["applicability"][workflow.value] for p, e in _param_matrix().items()}
    codes = {**case_codes, **param_codes, "case": "r"}
    root: dict = dict(_build_tree(_param_matrix()))
    root["case"] = {"name": "case", "path": "case", "children": tree}
    full = "\n".join(["{", *_emit_obj(root, codes, 1), "}"])
    req = "\n".join(["{", *_emit_obj(root, codes, 1, frozenset({"x", "o"})), "}"])
    label = WORKFLOW_LABELS[workflow.value]
    cb = f"appl-cb-{workflow.value}"
    # Pure-CSS toggle: a hidden checkbox swaps which of two independently
    # rendered <pre> blocks is shown, so commas/delimiters are always correct.
    return (
        f'<details class="appl-detail">\n'
        f"<summary>{label} <code>{workflow.value}</code></summary>\n"
        f'<div class="appl-json-wrap">\n'
        f'<input type="checkbox" class="appl-toggle-cb" id="{cb}">\n'
        f'<label class="appl-toggle" for="{cb}">'
        f'<span class="t-all">Hide optional</span>'
        f'<span class="t-req">Show optional</span></label>\n'
        f'<pre class="appl-json appl-full">\n{full}\n</pre>\n'
        f'<pre class="appl-json appl-req">\n{req}\n</pre>\n'
        f"</div>\n"
        f"</details>"
    )


def write_docs_tables() -> None:
    assert set(_case_matrix()) >= ARRAYS, "ARRAYS contains a path missing from the matrix"
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
            "### Workflow parameters",
            "The shared inputs each workflow takes alongside the `case` — `vbc`, "
            "`mde`, `moi`, `pop_frq_points`. Required by the workflows but **not** "
            "part of the Case data structure (they feed the workflow matrix that "
            "determines applicability and scoring).",
            _params_table(),
            "### Case workflow matrix",
            "Every attribute of the Case data structure across the seven workflows "
            "(five clinical `CLN_*` and two locus-based `LOC_*`), with the nested "
            "structure preserved. Rows with nested attributes can be expanded or "
            "collapsed; use the controls above the table to expand/collapse all or "
            "show the tree to a given depth. Conditional rules are summarized in **Notes**.",
            _matrix_table(),
            "### Per-workflow structures",
            "Expand a workflow to see its full input as a JSON example with mock "
            "data: the workflow parameters that apply (e.g. `moi`, `pop_frq_points`) "
            "plus a nested `case` object with only that workflow's applicable Case "
            'fields — **bold** = required, <span class="appl-c">underlined</span> = '
            "conditional, *italic* = optional; not-applicable fields are omitted. "
            "Use the **Hide optional** button (top-right of each example) "
            "to collapse the example to just the required and conditional fields.",
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
