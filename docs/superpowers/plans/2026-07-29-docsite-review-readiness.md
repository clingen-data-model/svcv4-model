# Docsite Review Readiness Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare the existing MkDocs site for review by the named external reviewer group (`docs/Docsite Review Plan.md`) — fix stale Case-field examples, correct two stale maturity annotations (`CLN_CCS` understated as WG-unspecified; `LOC_PHE`/`LOC_SEG` understated as unmodeled), give LOC the same full deep-dive treatment as CLN, add a spec-coverage traceability page, a reviewer front-door page, a core-concepts reference page, and de-duplicate the repeated hierarchy statement — per `docs/superpowers/specs/2026-07-29-docsite-review-readiness-design.md`.

**Architecture:** Almost entirely documentation. One source-file touch: a single docstring line in `src/svcv4_model/case.py` (no logic change). Three new pages and one new nested section added to `mkdocs.yml` nav; several existing pages edited in place; verification is `mkdocs build --strict` + grep audits for the fixed stale strings + the (unaffected) Case schema/docs drift gate.

**Tech Stack:** MkDocs + mkdocs-material, uv.

**Branch:** `docs/review-readiness` (off `main`). Commit per task.

**Cross-cutting content requirements (carry over from the Phase A spec, still binding):**
- **Positioning:** never present the SVCv4 framework as this project's own; attribute framework facts to the SVCv4 Working Group; this project provides the computational data model; CSpec owns methods/rules/scoring.
- **Maturity annotations:** distinguish "not yet specified by the SVCv4 Working Group" from "specified by the SVCv4 Standards but not yet modeled here" — use the existing admonition conventions (`!!! warning "Not yet specified by the SVCv4 Working Group"` vs. `!!! note "Not yet modeled here"`).
- **Terminology:** "the variant" = **VBC** = Proposition `subjectVariant`; "the disease/condition" = **MDE** ("Mendelian Disease Entity") = Proposition `objectCondition`/`objectConditionSet`.
- **Scope boundary:** describe *what evidence a workflow needs*; do not assert scoring rules — point to CSpec.
- **Tone:** understated register, matching the existing site.

**Recommended execution order** (later chunks may link to earlier ones' new pages): **1 → 2 → 3 → 5 → 4 → 6 → 7 → 8 → 9 → 10 → 11.** Chunk 4 (the `CLN_CCS` fix) links to Chunk 5's new Spec coverage page, so Chunk 5 must land first even though it's numbered later, exactly as Chunk 2 (LOC) does not depend on it and can run anytime after Chunk 1.

---

## Chunk 1: Fix stale Case-field examples

### Task 1.1: Fix `docs/getting-started/first-case.md`

**Files:** Modify `docs/getting-started/first-case.md`.

- [ ] **Step 1:** Replace the JSON block (current lines 18–30) with:

```json
{
  "moi": "AD",
  "pop_frq_points": 0,
  "vbc": { "id": "clinvar:VCV000000001" },
  "sex": "F",
  "phenotypes": [{ "code": "HP:0001250", "name": "Seizure" }],
  "pheno_specificity_for_mde": "SPECIFIC",
  "testing": { "covers_all_genes_relevant_to_mde": "TRUE" },
  "vbc_zygosity": "HET"
}
```

- [ ] **Step 2:** Update the prose sentence below it (current lines 32–34) to match the corrected field names (no more "specific to the gene" — it's "specific to the MDE").

- [ ] **Step 3:** Replace the "What each piece is" list (current lines 36–42) with entries for `moi`, `pop_frq_points`, `vbc`, `sex`/`phenotypes`, `pheno_specificity_for_mde`, `testing.covers_all_genes_relevant_to_mde`, `vbc_zygosity` — and add one line noting that `moi`/`pop_frq_points`/`vbc` are `WorkflowParameters` (submitted alongside a `Case`, not fields of it — per `src/svcv4_model/case.py`), while the rest are `Case` fields.

- [ ] **Step 4:** Add a short "Following the hierarchy" section after "What happens next" (current lines 44–52) that labels this same example against all four levels plus the entity chain, e.g.:

  > This one `CLN_AFF` capture threads the whole hierarchy: it's an **Evidence Item** (the `Case` payload above) that feeds the `CLN_AFF` **Evidence Code**'s workflow, producing an **Evidence Line** under the **Clinical Observations (CLN)** Evidence Concept, under the **Human Observations** Evidence Category — whose score ultimately rolls up into a **Statement** about a **Proposition** (`subjectVariant` = the VBC, `objectCondition` = the MDE).

  Link each bolded term to its existing definition page (`workflows/index.md` for Category/Concept/Code/Workflow, `getting-started/assertion-framework.md` for Statement/Proposition, `getting-started/evidence-lines-and-items.md` for Evidence Line/Item).

- [ ] **Step 5:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/getting-started/first-case.md
git commit -m "docs: fix stale Case field names in first-case example; add hierarchy walkthrough"
```

### Task 1.2: Fix `docs/workflows/hod/cln/cln-aff.md`

**Files:** Modify `docs/workflows/hod/cln/cln-aff.md`.

- [ ] **Step 1:** In "What evidence to capture" (current lines 10–19), replace `case_proband_info` including `pheno_specificity_for_gene` and `all_relevant_genes_tested` with: `sex`/`phenotypes` (direct `Case` fields), `pheno_specificity_for_mde`, and `testing.covers_all_genes_relevant_to_mde`.
- [ ] **Step 2:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/workflows/hod/cln/cln-aff.md
git commit -m "docs: fix stale Case field names on CLN_AFF workflow page"
```

### Task 1.3: Audit for any other occurrences of the stale field names

- [ ] **Step 1:** Run the audit:

```bash
grep -rn 'case_proband_info\|pheno_specificity_for_gene\|all_relevant_genes_tested' docs --include='*.md'
```
Expected: no output. If any remain (e.g. in `docs/workflows/case-model.md`'s generated content, or other CLN pages like `cln-dnv.md`/`cln-alt.md`/`cln-uaf.md`), fix them the same way — for the generated `case-model.md`, do **not** hand-edit; instead confirm the generator (`scripts/export_case_views.py`) reads live from `src/svcv4_model/case.py` and doesn't have its own hardcoded stale field list; if it does, that's a separate, out-of-scope code fix (flag it, don't silently expand this doc-only pass).

- [ ] **Step 2:** Commit any additional fixes found.

---

## Chunk 2: Restructure LOC into a full deep-dive (mirrors CLN)

`LOC_PHE`/`LOC_SEG` are already modeled to the same depth as the five CLN workflows — `src/svcv4_model/case.py`'s `Workflow` enum includes them, `schemas/applicability/case_applicability.yaml` has a full `r`/`o`/`c`/`x` entry for every Case field across all seven workflows, and `docs/workflows/case-model.md`'s generator already emits complete tables/JSON examples for both. Several pages currently claim otherwise. This chunk gives LOC the same page structure as CLN, per the user's direction (full deep-dive, not a minimal correction).

### Task 2.1: Move and rewrite the LOC concept overview page

**Files:** `git mv docs/workflows/hod/loc.md docs/workflows/hod/loc/index.md`.

- [ ] **Step 1:** Move the file.

```bash
mkdir -p docs/workflows/hod/loc
git mv docs/workflows/hod/loc.md docs/workflows/hod/loc/index.md
```

- [ ] **Step 2:** Rewrite it mirroring `docs/workflows/hod/cln/index.md`'s structure: intro paragraph (Locus Specificity is the Evidence Concept under Human Observational Data covering how specifically the variant/locus tracks with phenotype and disease — **realized by the same Case model that realizes CLN**, not a separate structure); a codes/workflows table with ✅ for both `LOC_PHE` and `LOC_SEG` (remove the old "Not yet modeled here" admonition entirely — it no longer applies); a short "How to read each workflow page" section matching the CLN page's.
- [ ] **Step 3:** Build-check and commit (link resolution to the not-yet-created deep-dive pages will warn under `--strict` until Task 2.2 lands — do Task 2.1 and 2.2 in the same commit, or accept a transient local warning between them).

```bash
git add docs/workflows/hod/loc/index.md
git commit -m "docs: rewrite LOC concept overview — LOC_PHE/LOC_SEG are already modeled"
```

### Task 2.2: Author `docs/workflows/hod/loc/loc-phe.md`

**Files:** Create `docs/workflows/hod/loc/loc-phe.md`.

- [ ] **Step 1:** Write the page mirroring `cln-aff.md`'s template (intro sentence; "What evidence to capture" required/conditional lists; "Scoring" section pointing to CSpec), populated from the applicability matrix's `LOC_PHE` column:
  - **Required:** `vbc`, `mde`, `pop_frq_points` (workflow parameters — note that `moi` is **not applicable** to `LOC_PHE`, unlike every other workflow); `id`; `gene_specificity_for_phenotypes`; `testing` + `testing.diagnostic_yield_for_phenotypes`; `vbc_exists`; `additional_variant_exists`.
  - **Conditional:** `additional_variants` (populated only when `additional_variant_exists` is `TRUE`; its own sub-fields `id`/`zygosity`/`phase_in_ref_to_vbc`/`classification` are required once present).
  - **Optional:** `sex`, `age`, `phenotypes`, `family_id`, `vbc_zygosity`, `age_matched_penetrance`, `testing.method`, `testing.covers_all_genes_relevant_to_mde`.
- [ ] **Step 2:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/workflows/hod/loc/loc-phe.md
git commit -m "docs: add LOC_PHE deep-dive page"
```

### Task 2.3: Author `docs/workflows/hod/loc/loc-seg.md`

**Files:** Create `docs/workflows/hod/loc/loc-seg.md`.

- [ ] **Step 1:** Same template, populated from the `LOC_SEG` column:
  - **Required:** `vbc`, `mde`, `moi` (required here, unlike `LOC_PHE`), `pop_frq_points`; `id`, `family_id`; `vbc_exists`; `additional_variant_exists`; `relatives`, and within it `relatives.parent_of_proband`, `relatives.affected_w_mde`, `relatives.vbc_exists`, `relatives.vbc_zygosity`, `relatives.cmp_het_variant_exists`.
  - **Conditional:** `compound_het_variant` (per its own rule: only when `vbc_zygosity` is `HET`); `additional_variants`; `relatives.sex` (required if X-linked MOI); `relatives.severe_phenotype` (required if semi-dominant or X-linked and affected).
  - **Optional:** `sex`, `age`, `phenotypes`, `vbc_zygosity`, `age_matched_penetrance`, `confirmed_parental_relationship`, `relatives.age`, `relatives.phenotypes`.
- [ ] **Step 2:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/workflows/hod/loc/loc-seg.md
git commit -m "docs: add LOC_SEG deep-dive page"
```

### Task 2.4: Update `mkdocs.yml` nav for the nested LOC section

**Files:** Modify `mkdocs.yml`.

- [ ] **Step 1:** Replace the current single-entry line `- Population (POP): workflows/hod/pop.md` / `- Locus Specificity (LOC): workflows/hod/loc.md` pairing's LOC half with a nested section matching the CLN pattern:

```yaml
- Locus Specificity (LOC):
    - workflows/hod/loc/index.md
    - Phenotype (LOC_PHE): workflows/hod/loc/loc-phe.md
    - Segregation (LOC_SEG): workflows/hod/loc/loc-seg.md
```

- [ ] **Step 2:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add mkdocs.yml
git commit -m "docs: nest LOC nav section (index + LOC_PHE + LOC_SEG deep-dives)"
```

### Task 2.5: Fix the pages that compound the LOC-as-stub misconception

**Files:** Modify `docs/workflows/hod/index.md`, `docs/workflows/index.md`, `docs/workflows/hod/cln/index.md`.

- [ ] **Step 1:** `docs/workflows/hod/index.md` — stop lumping LOC in with the POP/PFD stubs in its "Where this model goes deep" framing; LOC belongs alongside CLN as "detailed here."
- [ ] **Step 2:** `docs/workflows/index.md` — in the "What this section covers now" paragraph, change "the CLN workflows that the Case model supports" to "the CLN **and LOC** workflows that the Case model supports."
- [ ] **Step 3:** `docs/workflows/hod/cln/index.md` — line 6 currently reads "This is the concept the [Case model] realizes." Change to name both concepts, e.g. "This is one of the two concepts the Case model realizes (together with Locus Specificity, `../loc/index.md`)."
- [ ] **Step 4:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/workflows/hod/index.md docs/workflows/index.md docs/workflows/hod/cln/index.md
git commit -m "docs: stop framing LOC as a stub on the HOD/Workflows/CLN overview pages"
```

### Task 2.6: Link audit for the old `workflows/hod/loc.md` path

- [ ] **Step 1:** Run:

```bash
grep -rn 'workflows/hod/loc\.md\|hod/loc\.md' docs --include='*.md' mkdocs.yml
```
Expected: no output (all references now point at `workflows/hod/loc/index.md` or the two deep-dive pages).

- [ ] **Step 2:** Fix any stragglers found and commit.

---

## Chunk 3: `src/svcv4_model/case.py` docstring fix

The only source-file touch in this pass — a one-line, logic-free correction that is the actual root cause of the LOC-as-stub misconception (Chunk 2).

### Task 3.1: Correct the module docstring

**Files:** Modify `src/svcv4_model/case.py`.

- [ ] **Step 1:** Change the module docstring's opening line (current lines 1–2) from "the case-level clinical-observation (CLN) evidence payload" to reflect both concepts it serves, e.g.:

```python
"""SVCv4 Case model — the case-level clinical-observation and locus-specificity
(CLN/LOC) evidence payload.
```

- [ ] **Step 2:** Confirm no behavior change — the drift gate should report no diff (docstrings don't appear in the generated JSON Schema's `$comment`/`title`):

```bash
uv run python scripts/export_case_views.py >/dev/null
git diff --quiet -- schemas/json docs/workflows/case-model.md && echo "NO DRIFT" || echo "DRIFT"
```
Expected: `NO DRIFT`.

- [ ] **Step 3:** Run the existing test suite as a sanity check (docstring-only change, but confirm nothing imports/asserts on it):

```bash
uv run pytest -q
```

- [ ] **Step 4:** Commit.

```bash
git add src/svcv4_model/case.py
git commit -m "docs: correct Case module docstring — it serves CLN and LOC, not CLN only"
```

---

## Chunk 4: Correct the `CLN_CCS` maturity annotation

**Depends on Chunk 5** (the new Spec coverage page) for its link target — do Chunk 5 first, or land both in the same commit.

### Task 4.1: Update `docs/workflows/hod/cln/index.md`

**Files:** Modify `docs/workflows/hod/cln/index.md`.

- [ ] **Step 1:** Replace the admonition block (current lines 21–29):

Old:
```markdown
!!! warning "Not yet specified by the SVCv4 Working Group"

    **`CLN_CCS` (Case-Control studies)** is shown here for completeness of the
    framework, but it is **out of scope for the first release** of the SVCv4
    Standards — the SVCv4 Working Group has not yet specified it. It is therefore
    not modeled here. (This is different from POP/LOC/PFD, which the Standards
    specify but this model has not yet covered — see
    [Population (POP)](../pop.md), [Locus Specificity (LOC)](../loc.md), and
    [Predictive & Functional Data](../../pfd/index.md).)
```

New:
```markdown
!!! note "Not yet modeled here"

    **`CLN_CCS` (Case-Control studies)** is now specified by the SVCv4 Standards
    (Supplementary Material 4, "Clinical Observations" — odds-ratio/confidence-interval
    based evidence) but is **not yet modeled in this Case**. It joins
    [Population (POP)](../pop.md) and [Predictive & Functional Data](../../pfd/index.md)
    in the same "specified but not yet modeled" bucket — see
    [Spec coverage](../../../reference/spec-alignment.md) for the full picture.
    (Locus Specificity is no longer in that bucket — see
    `Locus Specificity (LOC)` (`../loc/index.md`).)
```

- [ ] **Step 2:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/workflows/hod/cln/index.md
git commit -m "docs: correct CLN_CCS maturity annotation now that Supp Mat 4 specifies it"
```

---

## Chunk 5: New page — Spec coverage (`docs/reference/spec-alignment.md`)

### Task 5.1: Author the page

**Files:** Create `docs/reference/spec-alignment.md`.

- [ ] **Step 1:** Write the page using the coverage table from spec §3.4 (trim the "obtained?" column — that's internal provenance, not useful to an external reader; keep supplement #, title, evidence code(s), and model coverage status). Open with one paragraph: "This page tracks which parts of the SVCv4 Standards this data model currently represents, and which are planned, so you can see exactly where we stand relative to the Standards documents." Link each "Not yet modeled" row to its stub page (`workflows/hod/pop.md`, `workflows/pfd/index.md`); link row 5 (now **Modeled**) to `workflows/hod/loc/index.md`. Flag supplement 17 (Non-Coding Variants) with a note that the manuscript itself describes this section as unwritten — a Working Group gap, not a modeling-project gap (same distinction convention as `CLN_CCS`, inverted).

- [ ] **Step 2:** Add to `mkdocs.yml` nav — insert `Spec coverage: reference/spec-alignment.md` immediately after `Model reference: reference/model.md` in the `Reference` section.

- [ ] **Step 3:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/reference/spec-alignment.md mkdocs.yml
git commit -m "docs: add Spec coverage reference page tracking SVCv4 supplement coverage"
```

---

## Chunk 6: New page — Reviewing this site (`docs/overview/review-guide.md`)

### Task 6.1: Author the page

**Files:** Create `docs/overview/review-guide.md`.

- [ ] **Step 1:** Write the page per spec §5.3: orientation paragraph (what stage the model is at), a curated reading path (Home → SVCv4 Standards in brief → How SVCv4 maps to the model → Getting Started track → Workflows: CLN and LOC deep-dives → Spec coverage → Core concepts), and a "what we'd like feedback on" checklist:
  - Do the CLN_AFF/DNV/ALT/UAF and LOC_PHE/LOC_SEG Case fields look complete and correctly named to a practicing curator? (link `workflows/case-model.md`)
  - `CLN_CCS` has no fields yet — what would you expect to capture? (link the corrected `workflows/hod/cln/index.md` note)
  - Two data points implied by Supplementary Material 4 aren't modeled yet: the gnomAD co-occurrence-likelihood bucket (biallelic `CLN_AFF` scoring) and an explicit "non-genetic etiology excluded" flag — first-class fields, or fine deferred?
  - Is the planned PFD shape (see the pattern note on the PFD page, Chunk 8) the right one?
  - Do the cross-cutting concepts (Core concepts page, Chunk 7) match how you think about Gene/MOI/VBC/MDE day to day?

  Do **not** duplicate `docs/Docsite Review Plan.md`'s reviewer names/meeting logistics — that stays a private planning note, not site content.

- [ ] **Step 2:** Add to `mkdocs.yml` nav — insert `Reviewing this site: overview/review-guide.md` immediately after `Home: index.md` in the `Overview` section.

- [ ] **Step 3:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/overview/review-guide.md mkdocs.yml
git commit -m "docs: add reviewer front-door page with feedback-focused known-gaps checklist"
```

---

## Chunk 7: New page — Core concepts (`docs/reference/concepts.md`)

### Task 7.1: Author the page

**Files:** Create `docs/reference/concepts.md`.

- [ ] **Step 1:** Write the page per spec §3.3/§5.11 — a richer companion to the Glossary (which stays a terse term table), one short explanatory entry per concept (what it is, why it matters, which workflows use it, current representation):
  - **VBC** (Variant Being Classified) — `WorkflowParameters.vbc` → `Vbc`; the Proposition subject; link to `assertion-framework.md` and the Glossary.
  - **MDE** (Mendelian Disease Entity) — `WorkflowParameters.mde` → `Mde`; the Proposition object; call out the gene↔MDE **non-1:1** relationship (a gene may map to more than one MDE), linking to the Spec coverage page's Supplementary Material 21 row.
  - **Gene** — `Gene` (`symbol`/`id`/`transcript`/`mde_associated_gene`); explain that `mde_associated_gene` is only populated when it differs from the VBC's gene (alternate-cause scenarios, `CLN_ALT`/`CLN_ALTG`).
  - **MOI** (Mode of Inheritance) — `WorkflowParameters.moi` (AD/AR/XLD/XLR/SD); explain it as the single shared parameter driving table selection (e.g. `CLN_AFF` monoallelic vs. biallelic) and per-workflow applicability (e.g. not applicable to `LOC_PHE`, required for `LOC_SEG`).
  - **Zygosity & Phase** — `Zygosity`/`Phase`/`PhaseConfidence`; one place explaining where each is used (VBC status, compound-het, additional variants, relatives) instead of leaving it scattered.
  - **Case** — the permissive-superset entity itself, realizing both CLN and LOC; explain the design (every field optional; required/optional/conditional/not-applicable is driven entirely by `schemas/applicability/case_applicability.yaml`, not the type); explain why `vbc`/`mde`/`moi`/`pop_frq_points` live in `WorkflowParameters` instead of `Case`; link to `workflows/case-model.md` for the generated per-workflow views.
  - **Cohort Allele Frequency** *(forward-looking only — not modeled)* — the VA-Spec [Cohort Allele Frequency Study Result](https://va-spec.ga4gh.org/en/1.0/va-standard-profiles/base-profiles/study-result-profiles.html#cohort-allele-frequency-study-result); the natural representation for population-database frequency data once `POP_FRQ`/`POP_HMZ` are built, since VA-Spec is this repo's primary dependency.
  - **Disease Allele Frequency Threshold (DAFT)** *(forward-looking only — not modeled)* — from Supplementary Material 3: the calculated population-frequency ceiling for a pathogenic variant, per-MDE; three derivation methods (Calculator/Binning/Pathogenic-Variants); distinct from, but compared against, Cohort Allele Frequency.
  - **Gene-Disease Validity** *(forward-looking only — not modeled anywhere)* — the ClinGen validity classification (Definitive/Strong/Moderate/Limited/Disputed/Refuted) that gates which classification tiers are reachable at all; cite the main manuscript; flag as a genuine model gap, not just a docs gap.
- [ ] **Step 2:** Add to `mkdocs.yml` nav — insert `Core concepts: reference/concepts.md` immediately before `Glossary: reference/glossary.md` in the `Reference` section.
- [ ] **Step 3:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/reference/concepts.md mkdocs.yml
git commit -m "docs: add Core concepts reference page (VBC, MDE, Gene, MOI, Zygosity/Phase; forward-looking Cohort Allele Frequency, DAFT, Gene-Disease Validity)"
```

---

## Chunk 8: PFD forward-looking pattern note

### Task 8.1: Update `docs/workflows/pfd/index.md`

**Files:** Modify `docs/workflows/pfd/index.md`.

- [ ] **Step 1:** After the "Concepts and codes" table (current line 32), add a short section, still under the page's existing "Not yet modeled here" admonition:

```markdown
## The shape of the remaining work

Every PFD workflow (missense, nonsense, frameshift, canonical splice, exon
deletion, start loss, stop loss, and others) follows the same pipeline:
**predict → adjust for molecular mechanism / exon relevance → functional
evidence → informative variants → capped code total.** Four sub-modules are
shared across all of them: Determining Critical Amino Acids, Molecular
Mechanism and Exon Relevance, Informative Variants, and Functional Assays.
Modeling this pipeline once, as a reusable shape, is the likely starting point
when PFD modeling begins.
```

- [ ] **Step 2:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/workflows/pfd/index.md
git commit -m "docs: note the shared PFD pipeline pattern ahead of future modeling"
```

---

## Chunk 9: Glossary additions

### Task 9.1: Update `docs/reference/glossary.md`

**Files:** Modify `docs/reference/glossary.md`.

- [ ] **Step 1:** Add rows for:
  - **Reclassification / Case Interpretation / Reanalysis / Reinterpretation** — the manuscript's four-way distinction (variant-level update from new evidence/standards vs. whether a variant explains an individual's phenotype vs. re-examining raw sequencing data vs. updating a report due to new phenotype/reanalysis/reclassification).
  - **Diagnostic yield** — referenced by `CaseTesting.diagnostic_yield_for_phenotypes` and `LOC_PHE`.
  - **Filtering Allele Frequency (FAF)** — the gnomAD-derived statistic underlying `POP_FRQ`; cross-link to the new Core concepts page's Cohort Allele Frequency / DAFT entries.
- [ ] **Step 2:** Sharpen the existing **MDE** row with the manuscript's precise phrasing (a gene+phenotype dyad; one gene may map to more than one MDE) and a link to the new Spec coverage page's Supplementary Material 21 row and the Core concepts page's MDE entry.
- [ ] **Step 3:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/reference/glossary.md
git commit -m "docs: add glossary terms surfaced by the SVCv4 manuscript/glossary review"
```

---

## Chunk 10: De-duplicate the hierarchy statement

### Task 10.1: Find and trim restatements

**Files:** Modify `docs/overview/svcv4-in-brief.md`, `docs/overview/alignment.md`, `docs/reference/summary-table.md` (as needed).

- [ ] **Step 1:** Find the duplicated chain:

```bash
grep -rn 'Evidence Category.*Evidence Concept.*Evidence Code' docs --include='*.md'
```

- [ ] **Step 2:** Keep the full statement only on `docs/workflows/index.md` (already there, unchanged). On each other page that restates it in full, replace with one sentence + a link, e.g.: "SVCv4 organizes evidence in a four-level hierarchy — see `Workflows overview` (`../workflows/index.md`) for the full picture." Read each page first to confirm the replacement doesn't strand any content that depended on the full chain being spelled out locally (e.g. `overview/alignment.md`'s mapping table stands on its own and shouldn't need the chain restated above it).

- [ ] **Step 3:** Re-run the Step 1 grep — expected: only `docs/workflows/index.md` remains.

- [ ] **Step 4:** Build-check and commit.

```bash
uv run mkdocs build --strict
git add docs/overview/svcv4-in-brief.md docs/overview/alignment.md docs/reference/summary-table.md
git commit -m "docs: de-duplicate the repeated evidence hierarchy statement"
```

---

## Chunk 11: Final verification

- [ ] **Step 1: Strict docs build**

```bash
uv sync --group docs --group dev
uv run mkdocs build --strict
```
Expected: clean build; new/changed nav entries present (Reviewing this site, Spec coverage, Core concepts, nested Locus Specificity section).

- [ ] **Step 2: Stale-field audit (should already be clean from Chunk 1)**

```bash
grep -rn 'case_proband_info\|pheno_specificity_for_gene\|all_relevant_genes_tested' docs --include='*.md' || echo "CLEAN"
```
Expected: `CLEAN`.

- [ ] **Step 3: Old LOC-path audit (should already be clean from Chunk 2)**

```bash
grep -rn 'workflows/hod/loc\.md' docs --include='*.md' mkdocs.yml || echo "CLEAN"
```
Expected: `CLEAN`.

- [ ] **Step 4: Hierarchy-duplication audit (should already be clean from Chunk 10)**

```bash
grep -rln 'Evidence Category.*Evidence Concept.*Evidence Code' docs --include='*.md'
```
Expected: only `docs/workflows/index.md`.

- [ ] **Step 5: Case schema/docs drift gate**

```bash
uv run python scripts/export_schemas.py >/dev/null
uv run python scripts/export_case_views.py >/dev/null
git diff --quiet -- schemas/json docs/workflows/case-model.md && echo "NO DRIFT" || echo "DRIFT"
```
Expected: `NO DRIFT` (the Chunk 3 docstring edit shouldn't change generated output; this also re-confirms nothing else in this pass touched generated content).

- [ ] **Step 6: Full test suite (Chunk 3 touched a source file)**

```bash
uv run ruff check .
uv run pytest -q
```
Expected: clean lint, all tests pass.

- [ ] **Step 7: Push and summarize**

```bash
git push origin docs/review-readiness
```
Then summarize for the user: what landed, and the follow-up backlog from spec §7 (CLN_CCS/Case-field model gaps, Cohort Allele Frequency + DAFT modeling, the Gene-Disease Validity field gap, the empty Workflow Images Drive folder, the 10 not-yet-obtained supplements, existing Phase B/Case-Phase-2 backlogs) — these are recommended as separate future work, not part of this PR.

---

## Notes & references

- Spec: `docs/superpowers/specs/2026-07-29-docsite-review-readiness-design.md`.
- Builds on Phase A (`docs/superpowers/specs/2026-06-11-docs-restructure-design.md`, PR #18) and the Case model (`docs/superpowers/specs/2026-06-11-case-model-design.md`, PR #17).
- Recommended chunk order: **1 → 2 → 3 → 5 → 4 → 6 → 7 → 8 → 9 → 10 → 11** (see the note at the top of this document).
- Follow-up backlog (not this PR): see spec §7.

## Post-plan additions (beyond the original 11 chunks)

Landed in the same PR (#20), driven by mid-execution user feedback rather than
being in the original chunk list above. Recorded here for an accurate history
— the spec doc's §3.3/§3.4/§5.9-5.11 were updated to match, but this plan's
chunk list above was intentionally left as originally written rather than
renumbered:

- **`getting-started/classification-inputs.md`** — new page; Getting Started
  shouldn't lead with a single-workflow example (`first-case.md`), it should
  ground readers in the classification-level inputs (VBC/MDE/MOI/Gene/
  Transcript) first.
- **`getting-started/capturing-basic-evidence.md`** (new) and
  **`getting-started/rolling-up-scores.md`** (new), plus a worked-example
  extension to `evidence-lines-and-items.md` and a trim of `first-case.md`'s
  hierarchy walkthrough — expands Getting Started into a full arc using
  `POP_FRQ` (the simplest real evidence code) before the more complex,
  branching `CLN_AFF` example. Chosen as the lower-risk, additive alternative
  to fully retiring/merging "The assertion framework" and "Evidence Lines &
  Evidence Items" as standalone pages — that fuller merge remains an option
  if wanted later, but was explicitly deferred ("good enough for now").
- **`docs/reference/known-gaps.md`** (new) — consolidates the follow-up
  backlog (spec §7) into one organized, cross-linked triage page, at the
  user's request to "create placeholders in the docs to figure out how best
  to organize them."
- **`docs/workflows/hod/pop.md`** — expanded with a "shape of the remaining
  work" section (mirroring the PFD stub's pattern), using Supplementary
  Material 3 content already ingested.
- **`docs/workflows/hod/loc/index.md`** — one additional note (allele vs.
  single-variant scope) added after reading the actual SVCv4 text
  (Supplementary Material 5), confirming the Chunk 2 restructuring was
  correct.
- **`docs/overview/review-guide.md`**'s reading path — updated to include the
  new Getting Started pages and Known gaps once they existed.
