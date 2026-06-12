# Docs Site Restructure Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-organize the MkDocs site into a learner-first, audience-progressive structure (Overview → Getting Started → Workflows → Examples → Reference) that teaches the SVCv4 framework→model alignment, per `docs/superpowers/specs/2026-06-11-docs-restructure-design.md`.

**Architecture:** Top-tab IA via mkdocs-material; existing concept pages relocated with `git mv` and re-linked; new authored pages (Overview/Getting Started/Workflows) drawn from the SVCv4 decks; the Case model's per-workflow tables stay generated (with the exporter/CI path updated for the page move); three user PNGs embedded via an image manifest; verification is `mkdocs build --strict` + a link audit + the schema/docs drift gate + example validation.

**Tech Stack:** MkDocs + mkdocs-material, mkdocstrings (Python), pymdownx (tabbed, superfences/Mermaid), uv.

**Branch:** `docs/site-restructure` (PR #18, base `main`). Commit per task; push per chunk to keep the PR in sync.

**Cross-cutting content requirements (apply to EVERY authored page — from spec §1.1–§1.4):**
- **Positioning (§1.1):** never present the SVCv4 framework as this project's own. The **SVCv4 Working Group** owns the Standards; **this project** provides the computational model; **CSpec** owns methods/rules/scoring. Attribute framework facts to the WG.
- **Accreditation (§1.2):** separate credit for the WG vs the modeling team; rosters flagged "verify before publishing."
- **Maturity annotations (§1.3):** distinguish "not yet specified by the SVCv4 WG (first release)" (e.g. `CLN_CCS`, shown-but-flagged) from "specified but not yet modeled here" (POP/LOC/Variant-Impact stubs). Use a consistent admonition style for each.
- **Terminology (§1.4):** "the variant" = **VBC** = variation = Proposition `subjectVariant` (reserve "additional variant"/"compound-het variant"); "the disease/condition" = **MDE** = "**Mendelian** Disease Entity" = Proposition `objectCondition`/`objectConditionSet`.
- **Scope boundary (§2):** describe *what evidence a workflow needs*; do **not** assert scoring rules — point to CSpec.
- **Tone:** understated register; lead simple, push depth behind "Learn more" links.

**Admonition conventions (define once, reuse):**
- Not-yet-specified-by-WG: `!!! warning "Not yet specified by the SVCv4 Working Group"` … "Shown for completeness; the committee has not specified this for the first release."
- Specified-but-not-modeled-here: `!!! note "Not yet modeled here"` … "Specified by the SVCv4 Standards; this computational model will cover it in a later phase."
- In-flux reference: `!!! warning "Advisory — in flux"` … on Reference pages.
- Image placeholder (until a PNG is present): `!!! info "Figure: <slot>"` naming the manifest slot.

---

## Chunk 1: Config, assets, and the Case-exporter/CI path fix

**File structure:**
- Modify `mkdocs.yml` (nav, features, extensions).
- Create `docs/assets/images/` + `README.md` (manifest) + copy 3 PNGs.
- Modify `.gitignore` (ignore `tmp/`).
- Modify `scripts/export_case_views.py` (`DOCS_PAGE` path) and `.github/workflows/ci.yml` (drift paths).
- `git mv docs/concepts/case-model.md docs/workflows/case-model.md` (the move that necessitates the path fix; page re-link happens in Chunk 2/4).

### Task 1.1: Create asset dir, manifest, and copy graphics; ignore tmp/

**Files:** Create `docs/assets/images/README.md`, `docs/assets/images/summary-table.png`, `…/hod-workflows.png`, `…/variant-impact-workflows.png`; Modify `.gitignore`.

- [ ] **Step 1: Copy the three PNGs from `tmp/` to manifest filenames**

```bash
mkdir -p docs/assets/images
cp "tmp/SVCv4 Summary Table.png"                       docs/assets/images/summary-table.png
cp "tmp/Human Observational Data w: Workflows.png"     docs/assets/images/hod-workflows.png
cp "tmp/Predictive and Functional Data w: Workflows.png" docs/assets/images/variant-impact-workflows.png
ls -1 docs/assets/images/
```
Expected: the three `.png` files listed.

- [ ] **Step 2: Write the manifest** `docs/assets/images/README.md`

Document each slot: filename, what it depicts, page(s) it anchors, and "replace this file to update the figure" (table mirrors spec §7). Include a row noting two diagrams are authored as Mermaid (data-model, points rubric) rather than images.

- [ ] **Step 3: Ignore `tmp/` so source decks/PNGs aren't committed**

Append to `.gitignore`:
```
# Local source material (decks, raw graphics) — not published
tmp/
```
Run: `git status --porcelain tmp/` → Expected: no output (tmp/ now ignored).

- [ ] **Step 4: Commit**

```bash
git add docs/assets/images .gitignore
git commit -m "docs: add image assets dir + manifest; ignore tmp/ source material"
```

### Task 1.2: Move `case-model.md` and fix the exporter + CI paths

**Files:** `git mv docs/concepts/case-model.md docs/workflows/case-model.md`; Modify `scripts/export_case_views.py`; Modify `.github/workflows/ci.yml`.

- [ ] **Step 1: Move the page**

```bash
mkdir -p docs/workflows
git mv docs/concepts/case-model.md docs/workflows/case-model.md
```

- [ ] **Step 2: Update the exporter's output path**

In `scripts/export_case_views.py`, change:
```python
DOCS_PAGE = REPO_ROOT / "docs" / "concepts" / "case-model.md"
```
to:
```python
DOCS_PAGE = REPO_ROOT / "docs" / "workflows" / "case-model.md"
```

- [ ] **Step 3: Update the CI drift paths**

In `.github/workflows/ci.yml`, in the "Export schemas and check no drift" step, change both `docs/concepts/case-model.md` references to `docs/workflows/case-model.md` (the `git diff --quiet -- …` line and the `git diff -- …` echo line).

- [ ] **Step 4: Regenerate and verify no drift at the new path**

```bash
uv run python scripts/export_schemas.py >/dev/null
uv run python scripts/export_case_views.py
git diff --quiet -- schemas/json docs/workflows/case-model.md && echo "NO DRIFT" || echo "DRIFT"
```
Expected: exporter lists `docs/workflows/case-model.md` updated; `NO DRIFT`.

- [ ] **Step 5: Commit**

```bash
git add scripts/export_case_views.py .github/workflows/ci.yml docs/workflows/case-model.md
git commit -m "docs: move case-model page to workflows/; update exporter + CI drift paths"
```

### Task 1.3: Rewrite `mkdocs.yml` nav + features + extensions

**Files:** Modify `mkdocs.yml`.

- [ ] **Step 1: Add theme features**

Under `theme.features`, add `navigation.indexes` and `navigation.tabs.sticky` (keep existing `navigation.tabs`, `navigation.sections`, etc.).

- [ ] **Step 2: Add markdown extensions**

Under `markdown_extensions`, add:
```yaml
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```
> Note: a bare `pymdownx.superfences` is already present — replace it with the block above (don't list it twice).

- [ ] **Step 3: Replace `nav`** with the spec §4 structure (final page paths):

```yaml
nav:
  - Overview:
      - Home: index.md
      - SVCv4 Standards in brief: overview/svcv4-in-brief.md
      - How SVCv4 maps to the model: overview/alignment.md
      - What this project is — and isn't: overview/scope.md
  - Getting Started:
      - "Show your work: structured evidence": getting-started/show-your-work.md
      - The assertion framework: getting-started/assertion-framework.md
      - Evidence Lines & Evidence Items: getting-started/evidence-lines-and-items.md
      - Capture your first case: getting-started/first-case.md
  - Workflows:
      - Workflows overview: workflows/index.md
      - Human Observational Data: workflows/human-observational-data.md
      - Clinical Observations (CLN): workflows/clinical-observations.md
      - Affected (CLN_AFF): workflows/cln-aff.md
      - De Novo (CLN_DNV): workflows/cln-dnv.md
      - Alternative Variant (CLN_ALTV): workflows/cln-altv.md
      - Alternative Gene (CLN_ALTG): workflows/cln-altg.md
      - Unaffected (CLN_UAF): workflows/cln-uaf.md
      - Population & Locus Specificity: workflows/pop-loc.md
      - Variant Impact: workflows/variant-impact.md
      - Case model & applicability: workflows/case-model.md
  - Examples:
      - Examples overview: examples/index.md
  - Reference:
      - Model reference: reference/model.md
      - JSON Schemas: reference/schemas.md
      - Summary Table: reference/summary-table.md
      - VA-Spec community profile: reference/va-spec-profile.md
      - Glossary: reference/glossary.md
      - "Interop: GA4GH GKS": reference/gks-interop.md
      - "Interop: ClinGen CSpec": reference/cspec-interop.md
      - Contributing: reference/contributing.md
      - Credits & acknowledgements: reference/credits.md
```
> The old `Plans` nav entry is intentionally dropped (file kept, out of nav).

- [ ] **Step 4: Verify YAML parses** (pages not created yet → build will warn; that's expected until later chunks)

Run: `uv run python -c "import yaml; yaml.unsafe_load(open('mkdocs.yml'))" && echo OK`
Expected: `OK` (the Mermaid `!!python/name:` tag requires `unsafe_load` here; mkdocs itself handles it natively).

- [ ] **Step 5: Commit**

```bash
git add mkdocs.yml
git commit -m "docs: new top-tab nav, section indexes, content tabs + Mermaid"
```

---

## Chunk 2: Relocate existing pages + Reference banner + link audit

All moves use `git mv` to preserve history. After moving, fix internal links and verify with a strict build + link audit. Pages are authored/expanded in later chunks; this chunk only relocates and re-links.

### Task 2.1: Move pages to their new homes

**Files:** `git mv` operations.

- [ ] **Step 1: Move the pages**

```bash
mkdir -p overview getting-started reference 2>/dev/null; cd docs
mkdir -p overview getting-started reference
git mv concepts/classification-vs-method-model.md overview/scope.md
git mv concepts/statement-and-proposition.md      getting-started/assertion-framework.md
git mv concepts/evidence-lines-and-items.md        getting-started/evidence-lines-and-items.md
git mv concepts/summary-table.md                   reference/summary-table.md
git mv concepts/va-spec-community-profile.md        reference/va-spec-profile.md
git mv glossary.md                                  reference/glossary.md
git mv contributing.md                             reference/contributing.md
git mv gks-interop.md                              reference/gks-interop.md
git mv cspec-interop.md                            reference/cspec-interop.md
git mv model/index.md                              reference/model.md
git mv schemas/index.md                            reference/schemas.md
cd ..
# remove now-empty dirs
rmdir docs/concepts docs/model docs/schemas 2>/dev/null || true
```
Expected: `git status` shows the renames; `docs/concepts`, `docs/model`, `docs/schemas` gone (note `docs/workflows/case-model.md` already created in Chunk 1).

- [ ] **Step 2: Commit the moves (before edits, so history is clean)**

```bash
git add -A
git commit -m "docs: relocate concept/reference pages into new IA (git mv, no content change yet)"
```

### Task 2.2: Fix internal links to moved pages

**Files:** Modify any `.md` referencing the old paths.

- [ ] **Step 1: Find residual references to old paths**

```bash
grep -rnE 'concepts/|model/index|schemas/index|va-spec-community-profile|\((\.\./)?(glossary|contributing|gks-interop|cspec-interop)\.md' docs --include='*.md' | grep -vE 'superpowers/|plans/'
```
This lists every link to fix (notably `docs/index.md` "Start here"/"Reference" lists, and cross-links inside the moved pages). The `plans/` and `superpowers/` dirs are kept out of nav and contain old-path-like strings in prose/tree illustrations, so they're excluded from the audit.

- [ ] **Step 2: Update each link to the new path**

Rewrite links per the move map (e.g. `concepts/classification-vs-method-model.md` → `overview/scope.md`; `model/index.md` → `reference/model.md`; `concepts/summary-table.md` → `reference/summary-table.md`; etc.). For mkdocstrings cross-refs prefer the autorefs form (e.g. `[`Case`][svcv4_model.Case]`).

- [ ] **Step 3: Re-run the audit until clean**

Run the Step 1 grep again → Expected: no output (outside `superpowers/`).

- [ ] **Step 4: Commit**

```bash
git add docs
git commit -m "docs: update internal links to relocated pages"
```

### Task 2.3: Add the "in-flux / advisory" banner to Reference pages

**Files:** Modify `reference/model.md`, `reference/schemas.md` (and optionally the section landing behavior).

- [ ] **Step 1:** Prepend the in-flux admonition (see conventions) to `reference/model.md` and `reference/schemas.md`, with one line noting codes/structure track the **evolving** SVCv4 Standards and are not themselves the Standard (spec §1.1 render target 4).

- [ ] **Step 2: Commit**

```bash
git add docs/reference
git commit -m "docs: in-flux advisory banner on Reference model/schemas pages"
```

---

## Chunk 3: Overview + Getting Started (authored)

Each page below: create the file, author the content to the outline (drawing facts from the decks; applying the cross-cutting requirements), then build-check. Commit per page or per small group. Flag any non-obvious inference inline with `<!-- VERIFY: … -->` for user review.

### Task 3.1: Home (`docs/index.md`)
- [ ] Rewrite for the broad audience. Outline: one-line what SVCv4 is (attributed to the WG) → why this project exists (computational model for producers/consumers, common semantics; §1.1) → "how to apply it" (pointer into Getting Started) → the **points-based rubric** as a small table (B ≤ −4 / LB −3..−1 / VUS 0..5 with Low 0-1·Mid 2-3·High 4-5 / LP 6..9 / P ≥ 10) → "Start here" links (Getting Started) and "Switch to Reference" link. Include a one-line credit to the modeling team + link to Credits. Build-check, commit.

### Task 3.2: SVCv4 Standards in brief (`docs/overview/svcv4-in-brief.md`)
- [ ] New primer. Outline (attributed to the SVCv4 WG throughout): what the SVCv4 Standard is (points-based successor to ACMG/AMP 2015; v3→v4 shift: codes + point values, decision-tree "curation SOP"); the Summary Table idea (Category→Concept→Code→Workflow→Score); evidence-code naming (e.g. `CLN_AFF_+1`); pointer to the WG's forthcoming publication/specs as authoritative. Keep high-level. Build-check, commit.

### Task 3.3: How SVCv4 maps to the model (`docs/overview/alignment.md`) — core
- [ ] New, authored from *The SVCv4 Standard Data Model* deck. Outline: embed `summary-table.png`; explain how Summary-Table levels map to the model — every scored cell = an **Evidence Line**; Category/Concept/Code = nested Evidence Lines; Workflows produce the scores; data points = **Evidence Items**; the whole rolls up into a **Statement** (Variant Pathogenicity Classification) over a **Proposition**. Link to the assertion-framework page for the entity detail. Note Standard vs Specialized (CSpec) at a high level. Build-check, commit.

### Task 3.4: What this project is — and isn't (`docs/overview/scope.md`)
- [ ] Expand the moved `classification-vs-method-model` content to frame **all three roles** (spec §1.1): SVCv4 WG → framework; this project → computational data model; CSpec → methods/rules/scoring. Keep the existing Classification-vs-Method detail as the CSpec half. Build-check, commit.

### Task 3.5: Show your work: structured evidence (`docs/getting-started/show-your-work.md`)
- [ ] New cornerstone page. Outline: why structured evidence matters (reproducible, shareable, computable classifications); "show your work" = capture the evidence each workflow needs in a common structure; how this enables producing/consuming SVCv4 classifications across systems. Link forward to assertion-framework and first-case. Build-check, commit.

### Task 3.6: The assertion framework (`docs/getting-started/assertion-framework.md`)
- [ ] Reframe the moved `statement-and-proposition` content, simple-first. Outline: start with the **Proposition** (where SVCv4 work starts) — SPOQ with **subject = `subjectVariant`** (the VBC) and **object = `objectCondition`/`objectConditionSet`** (the MDE); then the **Statement** (causal Variant Pathogenicity Classification) that asserts the Proposition with a final score, made by a group/individual. Add a **Mermaid** diagram: `Statement → Proposition (SPOQ) / Final Score → Evidence Line(s) → Evidence Item(s)`. Apply §1.4 terminology. "Learn more" → Reference/VA-Spec profile. Build-check, commit.

### Task 3.7: Evidence Lines & Evidence Items, simply (`docs/getting-started/evidence-lines-and-items.md`)
- [ ] Reframe the moved page: lead with a plain explanation (Evidence Item = a captured data point / Information Entity; Evidence Line = a scored roll-up of items for a code/concept, contributing up the hierarchy). Keep the deeper detail lower on the page behind a "Learn more" heading. Build-check, commit.

### Task 3.8: Capture your first case (`docs/getting-started/first-case.md`)
- [ ] New minimal worked example using the **Case model**: a simple `CLN_AFF` case — show the few required fields (moi, pop_frq_points, case_proband_info, vbc) as a small JSON snippet, in prose, then point to the workflow page + the Case model page. Use VBC/MDE terminology per §1.4. Build-check, commit.

**Chunk 3 verification:** `uv sync --group docs --group dev && uv run mkdocs build --strict` → builds with no warnings for these pages.

---

## Chunk 4: Workflows section (authored + scaffold)

### Task 4.1: Workflows overview (`docs/workflows/index.md`)
- [ ] New section index. Embed `summary-table.png`; explain the Summary Table hierarchy (Category → Concept → Code → Workflow → Score; points roll up). Two category links: Human Observational Data, Variant Impact. Attribute the framework to the WG. Build-check, commit.

### Task 4.2: Human Observational Data (`docs/workflows/human-observational-data.md`)
- [ ] New category page. Embed `hod-workflows.png`. List Concepts: POP (POP_FRQ, POP_HMZ), CLN (codes), LOC (LOC_PHE, LOC_SEG). Link to the CLN page and the POP/LOC stub. Build-check, commit.

### Task 4.3: Clinical Observations overview (`docs/workflows/clinical-observations.md`)
- [ ] New CLN concept page. List the codes and their workflows: `CLN_UAF`, `CLN_ALT` (→ Alt Variant / Alt Gene), `CLN_AFF`, `CLN_DNV`, and **`CLN_CCS`** — the latter wrapped in the **not-yet-specified-by-WG** admonition (§1.3). Link to the five deep-dive pages. Build-check, commit.

### Task 4.4: Five CLN workflow deep-dives (`cln-aff.md`, `cln-dnv.md`, `cln-altv.md`, `cln-altg.md`, `cln-uaf.md`)
- [ ] For each, a consistent template: 1-line purpose; "What evidence is needed" (authored from the Case applicability matrix + the workflow↔evidence-item sheet, describing the **evidence items**, not scoring rules — point scoring to CSpec); a link to the generated per-workflow applicability table on `workflows/case-model.md`; a short example excerpt; VBC/MDE terminology per §1.4. Build-check, commit (may group the five into 1–2 commits).

### Task 4.5: POP & Locus Specificity stub (`docs/workflows/pop-loc.md`)
- [ ] Brief stub: name POP (POP_FRQ, POP_HMZ) and LOC (LOC_PHE, LOC_SEG) concepts/codes from the Summary Table, each under the **specified-but-not-modeled-here** admonition (§1.3). Build-check, commit.

### Task 4.6: Variant Impact stub (`docs/workflows/variant-impact.md`)
- [ ] Brief stub: embed `variant-impact-workflows.png`; name the concepts MIS/CDS/NUL/SPL and the `_PRD`/`_FXN`/`_INF`(/`_SPA`) code pattern, gated by variant type; under the **specified-but-not-modeled-here** admonition. Build-check, commit.

### Task 4.7: Case model & applicability (`docs/workflows/case-model.md`)
- [ ] Already moved (Chunk 1) and regenerated. Add a short intro paragraph above the generated tables framing it as the structured backbone of CLN evidence capture; ensure the generated BEGIN/END block is intact and re-run the exporter to confirm no drift. Build-check, commit.

**Chunk 4 verification:** strict build clean; `uv run python scripts/export_case_views.py && git diff --quiet -- docs/workflows/case-model.md && echo NO-DRIFT`.

---

## Chunk 5: Examples, Credits, Glossary, and final verification

### Task 5.1: Examples overview (`docs/examples/index.md`)
- [ ] Reorganize using **content tabs**: a single worked example shown as `=== "Prose"` / `=== "Narrative"` / `=== "Semi-structured"` / `=== "JSON"`. The JSON tab links to `examples/classification-example-01.json` via its GitHub URL (repo-root file, unchanged). Build-check, commit.

### Task 5.2: Credits & acknowledgements (`docs/reference/credits.md`)
- [ ] New page. **Two separate sections:** "SVCv4 Working Group" (Standards authors — co-chairs Biesecker & Harrison, AMP rep Gastier-Foster, CAP rep Moyer, members + past members from the deck) and "SVCv4 Standards data-modeling team" (this project — Babb, Preston, Wright, Cheung, Wulf, Mandell, Shah, Dziadzio, Mulhall, Byrne; ClinGen Data Platform WG offshoot). Wrap rosters in the **verify-before-publishing** admonition (§1.2) and link to the WG's authoritative roster where available. Build-check, commit.

### Task 5.3: Glossary terminology (`docs/reference/glossary.md`)
- [ ] Add/confirm entries for the §1.4 equivalences: **VBC** (= the variant = variation = Proposition `subjectVariant`; vs additional/compound-het variant); **MDE** = **Mendelian Disease Entity** (= the disease/condition = Proposition `objectCondition`/`objectConditionSet`); plus Statement/Proposition/Evidence Line/Evidence Item one-liners. Build-check, commit.

### Task 5.4: Final full verification

- [ ] **Step 1: Strict docs build**

```bash
uv sync --group docs --group dev
uv run mkdocs build --strict
```
Expected: builds clean; the only "not in nav" INFO lines are `superpowers/**` and `plans/2026-05-19-initial-scaffold.md`.

- [ ] **Step 2: Link audit** — no references to old paths remain

```bash
grep -rnE 'concepts/|model/index|schemas/index|va-spec-community-profile|\((\.\./)?(glossary|contributing|gks-interop|cspec-interop)\.md' docs --include='*.md' | grep -vE 'superpowers/|plans/' || echo "CLEAN"
```
Expected: `CLEAN` (same pattern as the Task 2.2 audit).

- [ ] **Step 3: Schema/docs drift gate (with the new case-model path)**

```bash
uv run python scripts/export_schemas.py >/dev/null
uv run python scripts/export_case_views.py >/dev/null
git diff --quiet -- schemas/json docs/workflows/case-model.md && echo "NO DRIFT" || echo "DRIFT"
```
Expected: `NO DRIFT`.

- [ ] **Step 4: Examples still validate + lint/tests unaffected**

```bash
uv run python scripts/validate_examples.py
uv run ruff check . && uv run pytest -q
```
Expected: examples OK; ruff clean; tests pass (no code touched beyond the exporter path).

- [ ] **Step 5: Push and confirm PR #18 is green; surface VERIFY markers**

```bash
git push origin docs/site-restructure
grep -rn 'VERIFY:' docs --include='*.md' || echo "no open VERIFY markers"
gh pr checks 18 --watch
```
Then summarize for the user: what landed, the list of `<!-- VERIFY: -->` inferences to confirm, and the deferred Phase B items.

---

## Notes & references
- Spec: `docs/superpowers/specs/2026-06-11-docs-restructure-design.md`.
- Source facts come from the decks under `tmp/` (now gitignored) and the two Google Sheets; attribute framework facts to the SVCv4 WG and keep scoring rules pointed at CSpec.
- Deferred (Phase B): deep per-data-point workflow nuance; full POP/LOC/Variant-Impact pages (and CLN_CCS once the WG specifies it); per-workflow examples + downloadable JSON; optional polished deck figures.
- @superpowers:verification-before-completion — Task 5.4 must show green output before claiming done.
