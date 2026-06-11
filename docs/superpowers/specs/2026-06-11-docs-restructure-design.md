# Docs Site Restructure — Design Spec

**Date:** 2026-06-11
**Status:** Proposed (rev. 2 — incorporates user-supplied decks, graphics, and the workflow↔evidence-item sheet)
**Branch:** `docs/site-restructure` (off `feat/case-model`; PR base = `feat/case-model`, rebase to `main` once PR #17 merges)

## 1. Purpose & goal

Re-center the MkDocs site on **teaching the SVCv4 framework and how it aligns to
this data model**, learner-first, with the computational reference demoted while
the model is in flux.

Cornerstone message: **"show your work with structured evidence."** A reader
lands, learns what SVCv4 is and why it exists, then follows simple steps to
capture the evidence each workflow needs — building up to the evidence-based
assertions (causal Variant Pathogenicity Statements) that are the final,
shareable classification records.

**Primary audience:** curators, VCEP members, researchers/clinicians learning
the framework→model alignment. Engineers/integrators are routed to **Reference**.

## 2. Source material (user-supplied)

Authoring draws on materials the user added under `tmp/` (decks + PNGs) and two
Google Sheets:

- **Decks** (text extracted; not committed to the site): *Overview of SVCv4
  Standards* (points-based rubric, v3→v4, evidence-code naming like `CLN_AFF_+1`),
  *The SVCv4 Standard Data Model* (GKS/VA-Spec alignment, the
  Statement→Proposition→Evidence Line→Evidence Item structure, Standard vs
  Specialized/CSpec), *Summary Table alignment to evidence lines*.
- **Graphics (PNGs)** → become the three primary site images (§7).
- **Workflow↔evidence-item sheet** (`gid=495026972`): the evidence-line/evidence-item
  hierarchy, the inputs each workflow needs (GDM, MOI, MDE, VBC, ZYG, …), and
  scoring methods. **Scoring rules/methods stay pointed at CSpec** per the repo's
  scope boundary; the docs use this to describe *what evidence items a workflow
  needs*, not to implement the rules.
- **Case applicability sheet** (`gid=138412089`): already realized in PR #17.

**The SVCv4 Summary Table hierarchy** (confirmed from the graphics) is the
backbone of the Workflows section:

```
Evidence Category → Evidence Concept → Evidence Code → Code Workflow(s) → Workflow Score   (points roll up)
  Human Observational Data (HOD)
    Population (POP):            POP_FRQ, POP_HMZ
    Clinical (CLN):             CLN_UAF, CLN_ALT (→ Alt Variant / Alt Gene), CLN_AFF, CLN_DNV, CLN_CCS
    Locus Specificity (LOC):    LOC_PHE, LOC_SEG
  Variant Impact
    Single-aa change (MIS):     MIS_PRD, MIS_FXN, MIS_INF
    RNA alteration (CDS):       CDS_PRD, CDS_FXN, CDS_INF
    Absent protein (NUL):       NUL_PRD, NUL_FXN, NUL_INF
    Splicing (SPL):             SPL_PRD, SPL_SPA, SPL_FXN, SPL_INF
```

The **Case model (PR #17) covers the CLN clinical-observation workflows**
`CLN_AFF / CLN_DNV / CLN_ALTV / CLN_ALTG / CLN_UAF` — one Concept's codes within
this larger framework. Those are the deep-dive exemplars in this PR.

> **Authoring caveat:** content authored from the decks/sheets will flag any
> non-obvious inference for user review, and will not assert scoring rules
> (CSpec's domain).

## 3. Scope

**In scope (this PR):** new top-tab IA; rewritten Home; Overview "alignment"
page authored from the decks; Getting Started track; the Workflows section built
on the Summary Table hierarchy (overview + HOD/Variant-Impact category pages +
the five CLN workflow deep-dives + the moved Case model page; POP/LOC/CLN_CCS and
Variant-Impact concepts as brief stubs); Examples reorg with content tabs;
Reference demotion with an in-flux banner; the three graphics placed under
`docs/assets/images/` with a manifest; mkdocs config for tabs, section index
pages, content tabs, and Mermaid; **the Case-exporter/CI path fix** required by
moving `case-model.md` (§8).

**Out of scope / deferred (Phase B):** deep per-data-point workflow nuance and
scoring narrative; full build-out of POP, LOC, CLN_CCS, and the Variant-Impact
concepts; per-workflow worked examples and downloadable JSON beyond the existing
one; committing the source decks; any data-model/schema change.

## 4. Information architecture (top tabs)

`navigation.tabs` is already enabled; top-level nav keys become tabs.
`navigation.indexes` makes section landing pages.

```
Overview
  • Home (index.md) — what SVCv4 is, why we built it, how to apply it; points-based rubric
  • How SVCv4 maps to the model — Summary Table & data model        [img: summary-table]   (core)
  • What's in scope — Classification Model vs Method Model

Getting Started
  • Show your work: structured evidence (the cornerstone)
  • The assertion framework: Propositions → Variant Pathogenicity Statements   [Mermaid diagram]
  • Evidence Lines & Evidence Items, simply
  • Capture your first case — a minimal worked example (uses the Case model)

Workflows
  • Workflows overview — the Summary Table (Category → Concept → Code → Workflow)   [img: summary-table]
  • Human Observational Data                                          [img: hod-workflows]
      – Clinical Observations (CLN) — overview (incl. CLN_CCS note)
      – Affected (CLN_AFF) · De Novo (CLN_DNV) · Alternative Variant (CLN_ALTV)
        · Alternative Gene (CLN_ALTG) · Unaffected (CLN_UAF)        (deep-dives)
      – Population (POP) & Locus Specificity (LOC)                   (stub)
  • Variant Impact — Predictive & Functional (MIS/CDS/NUL/SPL)       [img: variant-impact-workflows]  (stub)
  • Case model & applicability — the structured backbone            (moved from concepts/)

Examples
  • Examples overview — prose · narrative · semi-structured · downloadable JSON

Reference   (banner: "in flux / advisory while the model stabilizes")
  • Model reference · JSON Schemas · Summary Table (vocabulary) · VA-Spec community profile
  • Glossary · Interop: GA4GH GKS · Interop: ClinGen CSpec · Contributing
```

**Out of nav (files kept):** `docs/superpowers/**`, `docs/plans/2026-05-19-initial-scaffold.md`.
These produce mkdocs INFO (not warnings), so `--strict` still passes.

## 5. Page inventory & disposition

Existing concept pages are **reframed and relocated** (via `git mv` to preserve
history), not rewritten from scratch. Internal cross-links are updated; `--strict`
+ a link audit (§9) catch breakage.

| New page | Source | Status |
|----------|--------|--------|
| `index.md` (Home) | rewrite for broad audience; points-based rubric as a table | authored now |
| `overview/alignment.md` | new — Summary Table & data-model alignment | **authored from decks** (+ img) |
| `overview/scope.md` | move `concepts/classification-vs-method-model.md` | authored now |
| `getting-started/show-your-work.md` | new — cornerstone rationale | authored now |
| `getting-started/assertion-framework.md` | reframe `concepts/statement-and-proposition.md`; add Mermaid | authored from decks |
| `getting-started/evidence-lines-and-items.md` | reframe `concepts/evidence-lines-and-items.md` (simple first, deeper links) | authored now |
| `getting-started/first-case.md` | new — minimal CLN_AFF capture using the Case model | authored now |
| `workflows/index.md` | new — Summary Table overview | authored from decks (+ img) |
| `workflows/human-observational-data.md` | new — HOD category overview | authored from decks (+ img) |
| `workflows/clinical-observations.md` | new — CLN concept overview (notes CLN_CCS not yet modeled) | authored now |
| `workflows/cln-aff.md` … `cln-uaf.md` (5) | new deep-dives; each: description + "evidence needed" (from the Case applicability matrix + the sheet) + link to the generated applicability table + example stub | authored now |
| `workflows/pop-loc.md` | new — POP & LOC stub | stub |
| `workflows/variant-impact.md` | new — Variant-Impact overview (MIS/CDS/NUL/SPL) | stub (+ img) |
| `workflows/case-model.md` | move `concepts/case-model.md` | authored (already generated) |
| `examples/index.md` | reorganize with content tabs | authored now |
| `reference/model.md` | move `model/index.md` (+ in-flux banner) | authored now |
| `reference/schemas.md` | move `schemas/index.md` (+ in-flux banner) | authored now |
| `reference/summary-table.md` | move `concepts/summary-table.md` | authored now |
| `reference/va-spec-profile.md` | move `concepts/va-spec-community-profile.md` | authored now |
| `reference/glossary.md` | move `glossary.md` | authored now |
| `reference/gks-interop.md`, `reference/cspec-interop.md` | move interop pages | authored now |
| `reference/contributing.md` | move `contributing.md` | authored now |

The five CLN workflow pages **link to** the generated per-workflow applicability
table on `workflows/case-model.md` (the exporter writes all five tables into that
one page); they do not each carry a generated table, so no exporter change beyond
the path fix in §8.

## 6. Example presentation

Examples use mkdocs-material **content tabs** (`pymdownx.tabbed`, `alternate_style:
true`): one example shows switchable **Prose / Narrative / Semi-structured / JSON**
views. The JSON view references the downloadable file in the repo-root `examples/`
directory via its GitHub URL (its current location; validated by
`scripts/validate_examples.py`) — it is not relocated into `docs/`.

## 7. Graphics: assets & manifest

`docs/assets/images/` holds the three user PNGs (copied from `tmp/`); `tmp/` is
added to `.gitignore` so the source decks/PNGs aren't committed wholesale. Each
embed carries descriptive alt text and a caption. `docs/assets/images/README.md`
documents the manifest.

| File (`docs/assets/images/`) | Source (`tmp/`) | Depicts | Used on |
|---|---|---|---|
| `summary-table.png` | `SVCv4 Summary Table.png` | full SVCv4 Summary Table | `workflows/index.md`, `overview/alignment.md` |
| `hod-workflows.png` | `Human Observational Data w: Workflows.png` | HOD Summary Table w/ workflows | `workflows/human-observational-data.md` |
| `variant-impact-workflows.png` | `Predictive and Functional Data w: Workflows.png` | Variant-Impact Summary Table w/ workflows | `workflows/variant-impact.md` |

Two conceptual diagrams are authored **in-repo as Mermaid** (no image needed,
editable, version-controlled): the **data-model diagram**
(Statement → Proposition / Final Score → Evidence Line(s) → Evidence Item(s)) on
the assertion-framework page, and the **points-based classification rubric**
(score ranges B ≤ −4 / LB −3..−1 / VUS 0..5 [Low/Mid/High] / LP 6..9 / P ≥ 10)
rendered as a table on Home. If the user later wants the decks' polished figures
for these, they drop PNGs into new manifest slots.

## 8. mkdocs config + the Case-exporter/CI path fix

**mkdocs.yml:** add `navigation.indexes` and `navigation.tabs.sticky` to
`theme.features`; add `pymdownx.tabbed` (`alternate_style: true`) and a
`pymdownx.superfences` Mermaid custom fence to `markdown_extensions`; replace
`nav` with §4. No new Python dependency (pymdownx/mermaid ship with the `docs`
group already).

**Case-exporter/CI path fix (required):** moving `concepts/case-model.md` →
`workflows/case-model.md` breaks PR #17's generator and drift gate, which
hardcode the old path. Update:
- `scripts/export_case_views.py`: `DOCS_PAGE` → `docs/workflows/case-model.md`.
- `.github/workflows/ci.yml`: the two `docs/concepts/case-model.md` references in
  the drift step → `docs/workflows/case-model.md`.

After the fix, `uv run python scripts/export_case_views.py` regenerates the moved
page in place and the drift gate stays green.

## 9. Quality gates

- `uv run mkdocs build --strict` passes (only the known out-of-nav internal docs
  emit INFO, not warnings).
- **Link audit:** no references to old paths (`concepts/…`, `model/…`,
  `schemas/…`, root `glossary.md`/`contributing.md`/`*-interop.md`) remain —
  `grep` for them returns nothing.
- `scripts/validate_examples.py` passes.
- The Case schema/docs drift gate passes with the new path: regenerate both
  exporters, `git diff --quiet -- schemas/json docs/workflows/case-model.md` is clean.
- The three image embeds resolve (files present under `docs/assets/images/`).

## 10. Implementation phasing

**This PR (Phase A):** full IA + config + path fix; all "authored now / authored
from decks" pages; the Workflows section (overview + HOD/Variant-Impact category
pages + five CLN deep-dives + moved Case page; POP/LOC + Variant-Impact stubs);
Examples reorg; Reference moves with in-flux banner; the three graphics + manifest;
Mermaid data-model + rubric; strict build green.

**Later (Phase B, separate PR):** deep per-data-point workflow nuance; full
POP/LOC/CLN_CCS and Variant-Impact concept pages; per-workflow examples +
downloadable JSON; optional polished deck figures.

## 11. Delivery

Work on `docs/site-restructure` (off `feat/case-model`). Open a PR with **base
`feat/case-model`** so it stacks on the Case work; retarget to `main` once PR #17
merges. Keep in sync via the PR.
