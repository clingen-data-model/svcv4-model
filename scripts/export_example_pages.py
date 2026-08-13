"""Generate a worked-example docs page for each encoded Practice Variant Set entry.

For every ``examples/practice-variant-set/<slug>/classification.json`` this emits
``docs/examples/practice-variant-set/<slug>.md`` — a provenance banner plus the
classification shown four ways (Prose / Narrative / Semi-structured / JSON) and,
when present, the primary ``case-<WF>.json`` capture. Pages are data-driven so
they stay in sync with the fixtures; regenerate after editing any fixture.

The hand-authored ``v5-myh7.md`` exemplar is left untouched (listed in SKIP).

Run from the repo root:  uv run python scripts/export_example_pages.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PVS_DIR = REPO_ROOT / "examples" / "practice-variant-set"
DOCS_DIR = REPO_ROOT / "docs" / "examples" / "practice-variant-set"
REPO_BLOB = "https://github.com/clingen-data-model/svcv4-model/blob/main"
REPO_TREE = "https://github.com/clingen-data-model/svcv4-model/tree/main"
SHEET = "https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit"

#: Slugs with a hand-authored page that the generator must not overwrite.
SKIP = {"v5-myh7"}

CLASS_LABEL = {
    "benign": "benign",
    "likely_benign": "likely benign",
    "variant_of_uncertain_significance": "variant of uncertain significance",
    "likely_pathogenic": "likely pathogenic",
    "pathogenic": "pathogenic",
}


def _gid(slug: str) -> str | None:
    src = PVS_DIR / slug / "source.md"
    if not src.exists():
        return None
    m = re.search(r"gid=(\d+)", src.read_text())
    return m.group(1) if m else None


def _short_code(method_code: str) -> str:
    return method_code.split(":", 1)[-1]


def _pretty_data(data: dict) -> str:
    """One-line summary of an evidence item's data dict."""
    bits = []
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            continue
        bits.append(f"{k.replace('_', ' ')} {v}")
    return "; ".join(bits)


def _banner_workflows(clf: dict, case_files: list[Path]) -> str:
    codes: list[str] = []
    for line in clf.get("evidence_lines", []):
        code = _short_code(line["method"]["code"])
        if code not in codes:
            codes.append(code)
    for cf in case_files:
        wf = cf.stem.removeprefix("case-")
        if wf not in codes:
            codes.append(wf)
    return " · ".join(codes)


def _prose(clf: dict) -> str:
    prop = clf["proposition"]
    subj = prop["subject"]["label"].split(" — ", 1)[0]
    obj = prop["object"]
    quals = prop.get("qualifiers") or [{}]
    moi = quals[0].get("moi")
    moi_phrase = f", under {moi} inheritance" if moi else ""
    n = len(clf["evidence_lines"])
    concepts = ", ".join(
        line["method"]["label"].split(" (")[0].lower() for line in clf["evidence_lines"]
    )
    cls = CLASS_LABEL.get(clf["score_classification"], clf["score_classification"])
    return (
        f"{subj} is assessed for whether it **is causal for** {obj['label']} "
        f"(`{obj['curie']}`){moi_phrase}, under the baseline SVCv4 specification. "
        f"{n} lines of evidence — {concepts} — compose to an illustrative "
        f"**{cls}**."
    )


def _narrative(clf: dict) -> str:
    prop = clf["proposition"]
    subj = prop["subject"]["label"].split(" — ", 1)[0]
    lines = [
        f"    The variant being classified (VBC) is {subj}; "
        f"the disease/condition (MDE) is {prop['object']['label']}. The curator captured:",
        "",
    ]
    for line in clf["evidence_lines"]:
        label = line["method"]["label"].split(" — ")[0]
        desc = line.get("description") or ""
        lines.append(f"    - **{label}** (`{line['code']}`, score {line['score']}) — {desc}")
    cls = CLASS_LABEL.get(clf["score_classification"], clf["score_classification"])
    lines += [
        "",
        f"    Each became an Evidence Line; their scores compose to a Statement final "
        f"score of {clf['final_score']} → *{cls}*.",
    ]
    return "\n".join(lines)


def _semi(clf: dict) -> list[str]:
    prop = clf["proposition"]
    quals = prop.get("qualifiers") or [{}]
    qual_bits = "; ".join(f"{k}={v}" for k, v in quals[0].items() if k in ("moi", "note"))
    out = [
        "    ```text",
        "    Statement",
        "      proposition:",
        f"        subjectVariant (VBC): {prop['subject']['label'].split(' — ', 1)[0]}",
        f"        predicate:            {prop['predicate']}",
        f"        objectCondition (MDE): {prop['object']['curie']} ({prop['object']['label']})",
    ]
    if qual_bits:
        out.append(f"        qualifiers:           {qual_bits}")
    out.append(f"      method:        {clf['method']['code']}")
    out.append("      evidence_lines:")
    for line in clf["evidence_lines"]:
        out.append(f"        - {line['code']:<12} score {line['score']:>4}")
    out.append(f"      final_score:          {clf['final_score']}")
    out.append(f"      score_classification: {clf['score_classification']}")
    out.append("    ```")
    return out


def _page(slug: str, pvs_id: str) -> str:
    entry = PVS_DIR / slug
    clf = json.loads((entry / "classification.json").read_text())
    case_files = sorted(entry.glob("case-*.json"))
    gid = _gid(slug)
    prop = clf["proposition"]
    gene_variant = prop["subject"]["label"].split(" — ", 1)[0]
    condition = prop["object"]["label"]
    blob = f"{REPO_BLOB}/examples/practice-variant-set/{slug}"
    tree = f"{REPO_TREE}/examples/practice-variant-set/{slug}"

    tab_link = f"[source tab ↗]({SHEET}?gid={gid}#gid={gid})" if gid else "source tab"
    entry_link = f"[`examples/practice-variant-set/{slug}/`]({tree})"
    banner_wf = _banner_workflows(clf, case_files)

    lines = [
        f"# {gene_variant} — {condition}",
        "",
        f'!!! info "Practice Variant Set · `{pvs_id}`"',
        "",
        f"    **Source:** {tab_link} · **Repo entry:** {entry_link} ·",
        f"    **Exercises:** {banner_wf}.",
        "",
        "    This example traces back to a [Practice Variant Set](index.md) entry; the",
        "    entry traces back to the source tab. Values are illustrative — scoring lives",
        "    in [CSpec](../../reference/cspec-interop.md).",
        "",
        f"An SVCv4 classification of {gene_variant} against {condition}, drawn from the",
        f"`{pvs_id}` Practice Variant Set entry.",
        "",
        "## The classification, four ways",
        "",
        '=== "Prose"',
        "",
        f"    {_prose(clf)}",
        "",
        '=== "Narrative"',
        "",
        _narrative(clf),
        "",
        '=== "Semi-structured"',
        "",
        *_semi(clf),
        "",
        '=== "JSON"',
        "",
        "    The rolled-up `Statement`, validated in CI:",
        "",
        f"    [Download `classification.json` →]({blob}/classification.json)",
    ]
    for cf in case_files:
        lines.append("")
        lines.append(f"    [Download `{cf.name}` →]({blob}/{cf.name})")

    if case_files:
        primary = next((c for c in case_files if "CLN_AFF" in c.name), case_files[0])
        wf = primary.stem.removeprefix("case-")
        lines += [
            "",
            f"## The case capture ({wf})",
            "",
            f"The workflow submission that feeds the `{wf}` line — `WorkflowParameters`",
            "(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:",
            "",
            "```json",
            primary.read_text().rstrip(),
            "```",
        ]

    lines += [
        "",
        "## Provenance & caveats",
        "",
        "- Capture and the field-by-field mapping (including open questions) live in the",
        f"  repo entry: [`source.md`]({blob}/source.md), [`mapping.md`]({blob}/mapping.md).",
        "- Scores and the classification are **illustrative** — the arithmetic is CSpec's.",
        "- Only the primary workflow is encoded so far; other applicable workflows are",
        "  noted in `mapping.md` and will be added as those workflows are developed.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    slugs = sorted(
        p.parent.name for p in PVS_DIR.glob("*/classification.json") if p.parent.name not in SKIP
    )
    for slug in slugs:
        parts = slug.split("-")
        pid = (
            "PVS-" + parts[0] + "-" + "-".join(parts[1:]).upper()
            if re.match(r"v\d+$", parts[0])
            else "PVS-" + slug.upper()
        )
        (DOCS_DIR / f"{slug}.md").write_text(_page(slug, pid))
        print(f"  - docs/examples/practice-variant-set/{slug}.md ({pid})")
    print(f"generated {len(slugs)} example page(s)")


if __name__ == "__main__":
    main()
