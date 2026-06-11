# Docs Site Restructure — Design Spec

**Date:** 2026-06-11
**Status:** Proposed
**Branch:** `docs/site-restructure` (off `feat/case-model`; PR base = `feat/case-model`, rebase to `main` once PR #17 merges)

## 1. Purpose & goal

Re-center the MkDocs site on **teaching the SVCv4 framework and how it aligns to
this data model**, with a learner-first path and the computational reference
demoted while the model is in flux.

The cornerstone message: **"show your work with structured evidence."** A reader
should land, understand what SVCv4 is and why it exists, then follow simple
steps to capture the evidence each SVCv4 workflow needs — building up to the
evidence-based assertions (causal Variant Pathogenicity Statements) that are the
final, shareable classification records.

**Primary audience:** curators, VCEP members, and researchers/clinicians
learning the framework→model alignment. Engineers/integrators are routed to
**Reference**.

## 2. Scope

**In scope (this PR):** new top-tab information architecture; rewritten Home;
new Overview "alignment" page; new Getting Started track; Workflows section
(landing + 5 workflow pages from a shared template); Examples reorganization
with content tabs; demotion of Model reference / JSON Schemas / vocabulary into
a secondary **Reference** tab with an "in-flux" banner; an image **manifest** +
`docs/assets/images/` with labeled placeholders; mkdocs config for tabs, section
index pages, content tabs, and Mermaid.

**Out of scope / deferred (need user content or later phases):**
- The real **SVCv4 rubric→model alignment narrative** and the **graphics**
  (rubric overview, workflow diagrams, alignment figures). Supplied by the user
  against the image manifest (§7); until then those slots are placeholders.
- Deep per-data-point **workflow nuance** (how each point is applied/scored).
- Per-workflow worked **examples** and downloadable JSON beyond the existing one.
- Any change to the data model, schemas, or the Case work from PR #17.

## 3. Information architecture (top tabs)

`navigation.tabs` is already enabled. Top-level nav keys become tabs:

```
Overview
  • Home — what SVCv4 is, why we built it, how to apply it        [img: rubric-overview]
  • How SVCv4 maps to the model — rubric & workflows ↔ model      [img: alignment]   (core objective)
  • What's in scope — Classification Model vs Method Model

Getting Started
  • Show your work: structured evidence (the cornerstone)
  • The assertion framework: Propositions → Variant Pathogenicity Statements
  • Evidence Lines & Evidence Items, simply
  • Capture your first case — a minimal worked example

Workflows                                                          [img: workflows-overview]
  • Workflows overview — the 5 CLN use cases & how the rubric drives them
  • Affected (CLN_AFF)            [img: cln-aff]
  • De Novo (CLN_DNV)             [img: cln-dnv]
  • Alternative Variant (CLN_ALTV)[img: cln-altv]
  • Alternative Gene (CLN_ALTG)   [img: cln-altg]
  • Unaffected (CLN_UAF)          [img: cln-uaf]
  • Case model & applicability — the structured backbone

Examples
  • Examples overview — prose · narrative · semi-structured · downloadable JSON

Reference   (banner: "in flux / advisory while the model stabilizes")
  • Model reference · JSON Schemas · Summary Table · VA-Spec community profile
  • Glossary · Interop: GA4GH GKS · Interop: ClinGen CSpec · Contributing
```

Section landing pages (Workflows, Examples) use `navigation.indexes`. The site
index (`docs/index.md`) is the Overview/Home page.

**Out of nav (files kept):** `docs/superpowers/specs/*`, `docs/superpowers/plans/*`,
`docs/plans/2026-05-19-initial-scaffold.md`. These are internal history.

## 4. Page inventory & disposition

Each existing concept page is **reframed and relocated**, not rewritten from
scratch. "Authored now" = I can write accurate content from existing
pages/README/model. "Placeholder" = needs the user's SVCv4 alignment content.

| New page | Source | Status |
|----------|--------|--------|
| `index.md` (Home) | rewrite of current `index.md` for broad audience | authored now (+ image slot) |
| `overview/alignment.md` | new — rubric & workflows ↔ model | **placeholder** (needs user narrative + image) |
| `overview/scope.md` | move `concepts/classification-vs-method-model.md` | authored now |
| `getting-started/show-your-work.md` | new — cornerstone rationale | authored now |
| `getting-started/assertion-framework.md` | reframe `concepts/statement-and-proposition.md` | authored now |
| `getting-started/evidence-lines-and-items.md` | reframe `concepts/evidence-lines-and-items.md` (simple first, "learn more" links) | authored now |
| `getting-started/first-case.md` | new — minimal capture example using the Case model | authored now |
| `workflows/index.md` | new — workflows overview | partial now + **placeholder** narrative/image |
| `workflows/cln-aff.md` … `cln-uaf.md` (5) | new from shared template | scaffold now (diagram placeholder + evidence-needed + generated applicability table + example stub); **nuance placeholder** |
| `workflows/case-model.md` | move `concepts/case-model.md` | authored now (already generated) |
| `examples/index.md` | reorganize with content tabs | authored now |
| `reference/model.md` | move `model/index.md` (+ in-flux banner) | authored now |
| `reference/schemas.md` | move `schemas/index.md` (+ in-flux banner) | authored now |
| `reference/summary-table.md` | move `concepts/summary-table.md` | authored now |
| `reference/va-spec-profile.md` | move `concepts/va-spec-community-profile.md` | authored now |
| `reference/glossary.md` | move `glossary.md` | authored now |
| `reference/gks-interop.md`, `reference/cspec-interop.md` | move interop pages | authored now |
| `reference/contributing.md` | move `contributing.md` | authored now |

> Moves preserve git history via `git mv`. Internal cross-links are updated to
> the new paths; a build with `--strict` (already configured) catches any
> broken links/anchors.

## 5. Tone & content conventions

- Match the repo's understated register (no puffed-up adjectives).
- Getting Started pages: lead with a plain-language explanation and one concrete
  snippet; push depth behind "Learn more" links so the basics stay light.
- The Workflows applicability tables are **generated** from the Case model's
  per-workflow views (PR #17), not hand-maintained — each workflow page includes
  the relevant generated table (or links to `workflows/case-model.md`).

## 6. Example presentation

Examples use mkdocs-material **content tabs** (`pymdownx.tabbed`, `alternate_style:
true`) so one example shows switchable **Prose / Narrative / Semi-structured /
JSON** views. The JSON tab links to the downloadable file under
`examples/` (e.g. `classification-example-01.json`), which `scripts/validate_examples.py`
already validates.

## 7. Graphics: image manifest

A new `docs/assets/images/` holds graphics. Until the user supplies files, each
page embeds a **labeled placeholder** (a captioned admonition naming the slot)
so the layout is real and the missing asset is obvious. `docs/assets/images/README.md`
documents the manifest. Preferred format: **SVG** for diagrams, PNG acceptable;
each embed carries descriptive alt text and a caption.

| Slot (filename under `docs/assets/images/`) | Depicts | Used on |
|---|---|---|
| `overview/rubric-overview.*` | SVCv4 rubric & general overview | Home hero |
| `overview/alignment.*` | how the rubric & workflows align to the model's structure | `overview/alignment.md` (core) |
| `workflows/workflows-overview.*` | the 5 CLN workflows & how the rubric drives them | `workflows/index.md` |
| `workflows/cln-aff.*` | Affected workflow diagram | `workflows/cln-aff.md` |
| `workflows/cln-dnv.*` | De Novo workflow diagram | `workflows/cln-dnv.md` |
| `workflows/cln-altv.*` | Alternative Variant workflow diagram | `workflows/cln-altv.md` |
| `workflows/cln-altg.*` | Alternative Gene workflow diagram | `workflows/cln-altg.md` |
| `workflows/cln-uaf.*` | Unaffected workflow diagram | `workflows/cln-uaf.md` |

Optional (only if no static graphic is provided): the
**Proposition → Statement → Evidence Line → Evidence Item** concept diagram may
be authored in-repo as **Mermaid** on `getting-started/assertion-framework.md`.

## 8. mkdocs configuration changes

- `theme.features`: add `navigation.indexes` (section index pages) and
  `navigation.tabs.sticky`. Keep existing `navigation.tabs`, `navigation.sections`.
- `markdown_extensions`: add `pymdownx.tabbed` (`alternate_style: true`) for
  content tabs; add a `pymdownx.superfences` custom fence for **Mermaid**
  (mkdocs-material's built-in `mermaid`/`fence_code_format`).
- `nav`: replace with the §3 structure.
- No new Python dependency: content tabs and Mermaid ship with
  pymdownx/mkdocs-material already in the `docs` group.

## 9. Quality gates

- `uv run mkdocs build --strict` passes (no broken links/anchors/nav warnings
  beyond the known internal docs deliberately left out of nav).
- `scripts/validate_examples.py` still passes.
- The Case schema/docs drift gate from PR #17 is unaffected (no schema/model
  changes here); `case-model.md` still regenerates clean from the exporter.
- A link-audit step confirms no references to the old `concepts/…`, `model/…`,
  `schemas/…` paths remain.

## 10. Implementation phasing

**This PR (Phase A):** the full IA + config; all "authored now" pages; the
Workflows scaffold (5 templated pages) and Examples reorg; Reference moves with
in-flux banner; `docs/assets/images/` + manifest + placeholders; strict build
green.

**Later (Phase B, separate PR, needs user input):** real alignment narrative +
graphics dropped into the manifest slots; deep per-workflow nuance; per-workflow
examples and downloadable JSON.

## 11. Delivery

Work on `docs/site-restructure` (branched off `feat/case-model`). Open a PR with
**base `feat/case-model`** so it stacks on the Case work; once PR #17 merges,
retarget the base to `main`. Keep in sync via the PR.
