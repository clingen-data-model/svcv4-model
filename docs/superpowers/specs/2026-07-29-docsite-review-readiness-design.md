# Docsite Review Readiness — Design Spec

**Date:** 2026-07-29
**Status:** Proposed
**Builds on:** `docs/superpowers/specs/2026-06-11-docs-restructure-design.md` (Phase A, PR #18, merged) and `docs/superpowers/specs/2026-06-11-case-model-design.md` (PR #17, merged)

## 1. Purpose & goal

A named group of external reviewers (`docs/Docsite Review Plan.md`: Bradford Powell, Tristan Nelson, Liam Mulhall, Kyle Ferriter, Alan Rubin, Kori Kuzma/Alex Wagner, a new Baylor dev, Hana Snow, Ryan Whaley, a CPG MS/Australia contact, and optionally Dave Lawrence/Shariant) is about to review this docsite, ahead of two review meetings. The model is **not finished** — PFD workflows are stubs, Experimental Variant Impact work is in progress, and several Phase A/B backlog items remain open. The goal of this pass is **not** to finish the model; it's to make the site trustworthy and legible to reviewers *as it stands*:

1. **Make the hierarchy legible end-to-end.** A reader should be able to follow one worked example from a Classification Statement down through Evidence Lines to the Evidence Items/Case data that back it, with the four hierarchy levels (Evidence Category → Evidence Concept → Evidence Code → Workflow) labeled at each step — not assembled by the reader from four separate pages.
2. **Prove the model has actually read the spec.** A new spec-coverage reference page tables every SVCv4 supplement against what's modeled/stubbed/not-yet-modeled here, so reviewers can see precisely where the data model stands relative to their own document set.
3. **Turn known incompleteness into directed feedback.** A short reviewer front-door page reframes the stubs and gaps as "here's where your feedback matters most," tied to the real deferred-work list — not left for reviewers to discover and wonder if something is broken.
4. **Fix correctness bugs that would undermine trust.** Two pages currently show Case JSON examples with field names that don't exist in the actual Pydantic model — a credibility risk if a technical reviewer tries to validate the example.

This is documentation-only work. No changes to `src/svcv4_model/*` or the applicability matrix are in scope (see §7 for what's deferred instead).

## 2. Source material (this pass)

Ingested to ground this spec, via the Google Drive/Gmail connectors:

- **Presentation:** `ACMGv4_CGLC_July2026` (Drive id `1Ja0vegwITIBRhgIFB13oc8fG3X1bRinvona989cY5Uw`), 60 slides, presented to the GA4GH Clinical Genomics Laboratory Community 2026-07-20. Gives the full evidence-code inventory, the Category/Concept/Code hierarchy, and the Classification-Model-vs-Method-Model split (slide 43) that matches this repo's existing scope boundary almost exactly.
- **Main manuscript draft:** `NewerestMainManuscript01122026` (Drive id `1qAHkdOjuqGuOtlZBjg4cuzZKXPbC5LPvzHIVlBFiH_4`, owned by L. Biesecker's account, modified 2026-07-29). Gives the 7-tier classification boundaries, the applicability scope (rare variants, Mendelian MDEs only; excludes multi-gene CNVs, somatic cancer, most PGx), and the four-way Reclassification/Case-Interpretation/Reanalysis/Reinterpretation terminology.
- **SVCv4 Pilot Launch email** (Alicia Byrne, 2026-07-22, Gmail thread `19f87a897a6cb0c2`): confirms the two Drive folders already linked into this project (`19RF57OC1mR-954nC9iuiOX0_cVR7suOf` "Code-specific workflow usage descriptions" and `1dMjLBmXo4dtIZA2PItWNvnAHiRyfvapG` "High-res images of variant-type-specific workflows") are the **official** pilot-documentation links — both are currently sparsely populated (2 supplements; the images folder is empty).
- **11 of the 21 Supplementary Materials**, read in full or in large part: **1** (Glossary), **3** (Population Database Frequency), **4** (Clinical Observations), **6** (Missense), **8** (Nonsense), **9** (Frameshift), **11** (Canonical Splice), **13** (Exon Deletion), **15** (Start Loss), **16** (Stop Loss), **21** (Multiple Disorders). Sourced from a mix of the official folder and a working-group copies folder ("SVCv4 Supplemental Doc COPIES for ClinGen WG", owned by abyrne@broadinstitute.org).
- **10 of the 21 Supplementary Materials not yet obtained**: 2 (SVCv3→v4 code status), 5 (Specific Phenotype and Segregation), 7 (Determining Critical Amino Acids), 10 (In-Frame InDel), 12 (Intronic & Synonymous), 14 (Exon Dup/Insertion), 17 (Non-Coding — flagged as an unfinished placeholder in the manuscript itself), 18 (Molecular Mechanism and Exon Relevance), 19 (Informative Variants), 20 (Functional Assays). Titles are known (deck slide 5's release list); content is not.
- **Existing docsite audit** (this project's own `docs/` tree) and four saved project-memory records (docs-restructure spec/plan, case-model spec/plan, scope-boundary note).

## 3. Key findings driving this work

### 3.1 The hierarchy, fully inventoried

Confirms and fills in what `overview/alignment.md` and `workflows/index.md` already state:

```
Evidence Category (2)         Human Observations          Predictive & Functional Data
Evidence Concept (7)          POP · CLN · LOC              MIS · CDS · NUL · SPL
Evidence Code (17)            POP_FRQ, POP_HMZ,             MIS_PRD/FXN/INF
                               CLN_AFF/UAF/DNV/ALT/CCS,      SPL_PRD/SPA/FXN/INF
                               LOC_PHE, LOC_SEG              NUL_PRD/FXN/INF
                                                             CDS_PRD/FXN/INF
Workflow (per variant type)   decision trees that produce each code's score
```

Every PFD workflow (missense, nonsense, frameshift, canonical splice, exon deletion, start loss, stop loss, and — per titles only — in-frame indel, intronic/synonymous, exon dup/insertion) follows the **same reusable pipeline shape**: predict → adjust for molecular-mechanism/exon-relevance → functional evidence → informative variants → capped code total, with four shared sub-modules referenced by every one of them (Supplementary Materials 7, 18, 19, 20). This is worth documenting as a pattern even before PFD is modeled — it tells reviewers we understand the shape of the remaining work.

### 3.2 Correctness bugs (fix regardless of any reorg decision)

1. **Stale Case field names.** `docs/getting-started/first-case.md` and `docs/workflows/hod/cln/cln-aff.md` show a JSON example using a `case_proband_info` wrapper with `pheno_specificity_for_gene` and `all_relevant_genes_tested` fields, and a nested `vbc.zygosity`. None of these exist in `src/svcv4_model/case.py`. The actual model is flat: `pheno_specificity_for_mde` (not `_for_gene`), `testing.covers_all_genes_relevant_to_mde` (not `all_relevant_genes_tested`), `vbc_zygosity` as a top-level `Case` field (not nested under `vbc`), and `sex`/`phenotypes` directly on `Case` (no `case_proband_info` wrapper). `vbc`/`moi`/`pop_frq_points` are `WorkflowParameters`, not `Case` fields — the docs conflate the two into one submission payload, which is a reasonable presentation choice, but should say so.
2. **`CLN_CCS` maturity annotation is now stale — and neither of the site's two existing categories fits.** `docs/workflows/hod/cln/index.md` currently states `CLN_CCS` is "**not yet specified by the SVCv4 Working Group**" — true when PR #18 was authored (2026-06-11), but Supplementary Material 4 (Clinical Observations), now in hand, does provide **scoring guidance** for `CLN_CCS` (an odds-ratio/confidence-interval point scale). It would be equally wrong, though, to simply reclassify it as "specified but not yet modeled here" alongside POP/LOC/PFD — **per user clarification (2026-07-29)**, the SVCv4 Standards give CLN_CCS a scoring formula but not decomposed **evidence concepts** the way `CLN_AFF`/`CLN_DNV`/`CLN_ALT`/`CLN_UAF` have. This project's Classification Model captures structured, verifiable evidence — not just derived scores — so there is genuinely nothing robust to model for `CLN_CCS` yet, independent of this project's own backlog. Subsequent SVCv4 versions aim to add more evidence-based workflow scoring here; this repo will model it once that exists. This is a third, distinct annotation category — not a mechanical swap between the site's existing two.
3. **`LOC_PHE`/`LOC_SEG` are understated as unmodeled — the mirror-image bug.** `docs/workflows/hod/loc.md` currently claims LOC "is not yet covered by this data model." This is **wrong**: `src/svcv4_model/case.py`'s `Workflow` enum already includes `LOC_PHE`/`LOC_SEG` alongside the five CLN workflows, `schemas/applicability/case_applicability.yaml` has a full `r`/`o`/`c`/`x` entry for **every** Case field across all seven workflows (not five), and `docs/workflows/case-model.md`'s generator (`scripts/export_case_views.py`) already emits complete generated tables and JSON examples for `LOC_PHE` ("Locus — Phenotype") and `LOC_SEG` ("Locus — Segregation"). The whole `relatives` sub-structure exists specifically to serve `LOC_SEG`; `gene_specificity_for_phenotypes` and `testing.diagnostic_yield_for_phenotypes` are required specifically for `LOC_PHE`. Three more pages compound this: `docs/workflows/hod/index.md` and `docs/workflows/index.md` both lump LOC in with the genuinely-unmodeled POP/PFD stubs; `docs/workflows/hod/cln/index.md` states "This is the concept the Case model realizes" (singular, CLN-only) when the Case model actually realizes CLN **and** LOC together, sharing one entity. The root cause is in the code itself: `src/svcv4_model/case.py`'s module docstring calls `Case` "the case-level **clinical-observation (CLN)** evidence payload," which is the CLN-only framing that leaked into every downstream doc page. This is the single most important finding of this pass, precisely because it demonstrates the exact failure mode the review is meant to catch: a page confidently telling a reviewer "not built yet" about something that is, in fact, already built and generated two clicks away.
4. **Duplicated hierarchy statement.** The exact "Evidence Category → Evidence Concept → Evidence Code → Code Workflow(s) → Workflow Score" chain is restated near-verbatim on at least four pages (`overview/svcv4-in-brief.md`, `overview/alignment.md`, `workflows/index.md`, `reference/summary-table.md`). Not a bug, but worth consolidating to one canonical statement + links, both for maintainability and so the "spine" reads as one story rather than four copies.

### 3.3 Core cross-cutting concepts (no home currently)

The site documents *workflows* (CLN and — after this pass — LOC deep-dives) and the VA-Spec *entity* layer (Statement/Proposition/Evidence Line/Evidence Item, in Getting Started), but nothing currently explains the handful of domain concepts that recur across **every** workflow as reusable building blocks — a reader has to reconstruct them from the mkdocstrings-generated `reference/model.md` dump, the Glossary's one-liners, and scattered field descriptions. Found while auditing the Case/`WorkflowParameters` split:

| Concept | Current state |
|---|---|
| **VBC** (Variant Being Classified) | Modeled (`WorkflowParameters.vbc` → `Vbc`); documented in Glossary + `assertion-framework.md` as the Proposition subject, but never as a standalone concept with its own page |
| **MDE** (Mendelian Disease Entity) | Modeled (`WorkflowParameters.mde` → `Mde`); same gap — and the gene↔MDE **non-1:1** relationship (Supplementary Material 21) isn't surfaced anywhere prominent, despite affecting `Gene`, DAFT (below), and classification scope decisions across the board |
| **Gene** | Modeled (`Gene`: `symbol`/`id`/`transcript`/`mde_associated_gene`); no page explains *why* `mde_associated_gene` exists (it only differs from the VBC's gene for `CLN_ALT`/`CLN_ALTG`-style alternate-cause scenarios) |
| **MOI** (Mode of Inheritance) | Modeled (`WorkflowParameters.moi`; AD/AR/XLD/XLR/SD); a single shared parameter that drives table selection (e.g. `CLN_AFF` monoallelic vs. biallelic) and applicability differences across all seven CLN+LOC workflows (e.g. `LOC_PHE` doesn't need it, `LOC_SEG` requires it) — never explained as the cross-cutting driver it is |
| **Zygosity & Phase** | Modeled (`Zygosity`, `Phase`, `PhaseConfidence`); scattered across VBC status, compound-het, additional variants, and relatives with no single explanatory page |
| **Case** | Modeled (`Case` — the permissive superset entity itself, realizing both CLN and LOC); explained today only implicitly, split across `getting-started/first-case.md` (one worked example), `workflows/case-model.md` (the generated applicability tables), and the mkdocstrings dump — no page explains the *design* (every field optional; required/optional/conditional/not-applicable is entirely driven by the external applicability matrix, not the type; `WorkflowParameters` — `vbc`/`mde`/`moi`/`pop_frq_points` — are deliberately kept out of `Case` itself) |
| **Cohort Allele Frequency** | **Not modeled** — POP is a genuine stub (zero applicability-matrix entries). This is a **VA-Spec Study Result profile** — the [Cohort Allele Frequency Study Result](https://va-spec.ga4gh.org/en/1.0/va-standard-profiles/base-profiles/study-result-profiles.html#cohort-allele-frequency-study-result) under VA-Spec's base Study Result Profiles — representing population-database frequency (gnomAD-style) as a first-class VA-Spec entity. Since VA-Spec is this repo's primary dependency (not an "added when needed" one like Cat-VRS), this is the natural, already-standardized shape to adopt once `POP_FRQ`/`POP_HMZ` are built |
| **Disease Allele Frequency Threshold (DAFT)** | **Not modeled** — from Supplementary Material 3: the calculated ceiling for a pathogenic variant's population frequency for a given MDE, derived via one of three methods (Calculator / Binning / Pathogenic-Variants); central to how `POP_FRQ` evidence will eventually be captured, and distinct from (but compared against) the Cohort Allele Frequency Study Result above |
| **Gene-Disease Validity** | **Not modeled anywhere** — a new finding, not previously flagged. The manuscript gates which classification tiers are even reachable by ClinGen's gene-disease validity classification (Definitive/Strong/Moderate/Limited/Disputed/Refuted) — e.g. "Limited" validity blocks P/LP outright, "Disputed/Refuted" blocks reporting entirely. No field in `Case`, `WorkflowParameters`, or anywhere in the docs represents this precondition today |

The three "not modeled" rows (Cohort Allele Frequency, DAFT, Gene-Disease Validity) get forward-looking treatment only — same pattern as the PFD pipeline note (§5.6): name the concept, explain why it matters, do not build it.

### 3.4 Spec-coverage inventory (feeds the new Reference page, §5.2)

| # | Supplementary Material | Evidence code(s) | Obtained? | Model coverage |
|---|---|---|---|---|
| — | Main manuscript | hierarchy, 7-tier classification, applicability scope | Yes | Partial — hierarchy/tiers reflected in Overview; applicability scope (rare/Mendelian-only, CNV/somatic/PGx exclusions) not yet stated anywhere in the docs |
| 1 | Glossary of Terms | — | Yes | Partial — `reference/glossary.md` exists; missing several terms now known (see §5.4) |
| 2 | SVCv3 codes → v4 status | — | No | Not modeled (historical mapping; informational only, low priority) |
| 3 | Population Database Frequency | `POP_FRQ`, `POP_HMZ` | Yes | Not yet modeled (`workflows/hod/pop.md` stub — Phase B); introduces the Cohort Allele Frequency / DAFT concepts (§3.3) |
| 4 | Clinical Observations | `CLN_CCS/AFF/DNV/ALT/UAF` | Yes | **Modeled** for AFF/DNV/ALT/UAF via the Case model (PR #17); `CLN_CCS` has zero representation (see §7) |
| 5 | Specific Phenotype and Segregation | `LOC_PHE`, `LOC_SEG` | No | **Modeled** — `Workflow` enum + full applicability-matrix entries + generated tables already exist (§3.2 item 3); the docs wrongly call it a stub |
| 6 | Missense Variants | `MIS_*`, `SPL_*` (missense path) | Yes | Not yet modeled (`workflows/pfd/index.md` stub) |
| 7 | Determining Critical Amino Acids | (shared sub-module) | No | Not yet modeled |
| 8 | Nonsense Variants | `NUL_*`, `CDS_*` | Yes | Not yet modeled |
| 9 | Frameshift Variants | `NUL_*`, `CDS_*` | Yes | Not yet modeled |
| 10 | In-Frame InDel Variants | `CDS_*` (assumed) | No | Not yet modeled |
| 11 | Canonical Splice Variants | `SPL_*` | Yes | Not yet modeled |
| 12 | Intronic & Synonymous Variants | `SPL_*`/`NCG_*` (assumed) | No | Not yet modeled |
| 13 | Exon Deletion Variants | `NUL_*`, `CDS_*` | Yes | Not yet modeled |
| 14 | Exon Dup/Insertion Variants | `NUL_*`, `CDS_*` (assumed) | No | Not yet modeled |
| 15 | Start Loss Variants | `NUL_*`, `CDS_*` | Yes | Not yet modeled |
| 16 | Stop Loss Variants | `NUL_*`, `CDS_*` | Yes | Not yet modeled |
| 17 | Non-Coding Variants | TBD | No | Not yet modeled — **the SVCv4 manuscript itself flags this section as an unwritten placeholder**, i.e. this is a WG gap, not (yet) a modeling-project gap |
| 18 | Molecular Mechanism and Exon Relevance | (shared sub-module) | No | Not yet modeled |
| 19 | Informative Variants | (shared sub-module) | No | Not yet modeled |
| 20 | Functional Assays | (shared sub-module) | No | Not yet modeled |
| 21 | Multiple Disorders Guidance | — (design constraint) | Yes | Partial — informs the `Mde`/`Gene` model's gene↔MDE-is-not-1:1 design; not itself a discrete workflow page |

## 4. Scope

**In scope (this pass):**
- Fix the two stale-field-name pages (§3.2 item 1).
- Correct the `CLN_CCS` maturity annotation (§3.2 item 2).
- Correct the `LOC_PHE`/`LOC_SEG` understated-as-unmodeled bug, restructuring `workflows/hod/loc.md` into a nested concept page + two deep-dive pages mirroring the CLN pattern (§3.2 item 3, §5.9).
- One-line docstring fix in `src/svcv4_model/case.py` — the root cause of the LOC bug (§5.10). The only source-file touch in this pass; no logic change.
- Consolidate the duplicated hierarchy statement to one canonical location + links (§3.2 item 4).
- New capstone content on `getting-started/first-case.md`: carry the corrected worked example through all four hierarchy levels plus Statement/Proposition/Evidence Line/Evidence Item/Case, explicitly labeled.
- New page `reference/spec-alignment.md`: the §3.4 coverage table, presented for readers (not just this spec).
- New page `overview/review-guide.md`: reviewer front door + feedback-focused known-gaps checklist.
- New page `reference/concepts.md`: the §3.3 cross-cutting concepts table, written up as explanatory content (VBC, MDE, Gene, MOI, Zygosity & Phase now; Cohort Allele Frequency, DAFT, Gene-Disease Validity as forward-looking-only).
- Light forward-looking content on `workflows/pfd/index.md`: name the shared PRD→Mechanism/Exon-Relevance→FXN→INF pipeline pattern and the four shared sub-modules, without building out PFD itself.
- Glossary additions for terms now known and referenced by in-scope pages (§5.4).
- `mkdocs.yml` nav entries for the three new pages.

**Out of scope / deferred (see §7 for the full follow-up list):** any change to `src/svcv4_model/*` beyond the single docstring line in §5.10; any change to `schemas/applicability/*`; full POP/LOC-deep-nuance/PFD build-out (existing Phase B backlog, unchanged); rule enforcement, case aggregation, SVCv4 point-mapping (existing Case-model Phase 2 backlog, unchanged); obtaining/reading the 10 not-yet-obtained supplements; sourcing the workflow diagrams (Drive images folder is currently empty); modeling Cohort Allele Frequency, DAFT, or Gene-Disease Validity (documented as concepts only, not built); any bigger nav restructuring beyond what's listed above.

## 5. Content changes, page by page

### 5.1 Fix stale Case examples

**`docs/getting-started/first-case.md`** — replace the JSON block (lines 18–30) and the "What each piece is" list (lines 36–42):

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

Add a one-line note that `moi`, `pop_frq_points`, and `vbc` are `WorkflowParameters` (submitted alongside a `Case`, not part of it — per `src/svcv4_model/case.py`'s own docstring), so the distinction is documented rather than silently blurred.

**`docs/workflows/hod/cln/cln-aff.md`** — same field-name fixes in the "What evidence to capture" list (lines 15–17): `pheno_specificity_for_mde` and `testing.covers_all_genes_relevant_to_mde`, not `pheno_specificity_for_gene`/`all_relevant_genes_tested`.

### 5.2 New page: `reference/spec-alignment.md`

Nav label "Spec coverage", inserted right after "Model reference" in the Reference tab. Content: the §3.4 table (trimmed of internal-only "obtained?" caveats not useful to an external reader — keep coverage status, drop the sourcing-folder trivia), framed with one paragraph explaining why it exists ("so you can see exactly which parts of the SVCv4 Standards this model currently represents, and which are planned"). Link each "Not yet modeled" row to the relevant stub page (`hod/pop.md`, `pfd/index.md`); link the now-corrected row 5 (LOC) to the new `hod/loc/index.md`.

### 5.3 New page: `overview/review-guide.md`

Nav label "Reviewing this site", inserted as the second Overview entry (right after Home, before "SVCv4 Standards in brief"). Content:
- One-paragraph orientation: what stage the model is at, and what kind of feedback is most useful right now.
- A curated reading path (Home → SVCv4 Standards in brief → How SVCv4 maps to the model → Getting Started track → Workflows: CLN deep-dives → Spec coverage).
- A "what we'd like feedback on" checklist mirroring real, current gaps:
  - Do the CLN_AFF/DNV/ALT/UAF Case fields (`workflows/case-model.md`) look complete and correctly named to a practicing curator?
  - `CLN_CCS` (case-control evidence) has no fields yet — what would you expect to capture?
  - Two data points implied by Supplementary Material 4 aren't in the Case model yet: the gnomAD co-occurrence-likelihood bucket used in biallelic scoring, and an explicit "non-genetic etiology excluded" flag — do these need to be first-class fields, or are they fine deferred?
  - POP/LOC/PFD are intentionally unmodeled stubs — is the shape we're planning (per the new Spec coverage page) the right one?
- Explicitly **not** a copy of `docs/Docsite Review Plan.md` (that file stays a private planning note — reviewer names/logistics don't belong on the public site).

### 5.4 Glossary additions (`reference/glossary.md`)

Add rows for terms surfaced by the manuscript/glossary read that are referenced by in-scope pages, and no others (don't pre-load PFD-specific jargon before PFD is modeled):
- **Reclassification vs. Case Interpretation vs. Reanalysis vs. Reinterpretation** — the manuscript's precise four-way distinction (variant-level update vs. does-this-variant-explain-this-phenotype vs. re-examining raw data vs. updating a report).
- **Diagnostic yield** — referenced by `CaseTesting.diagnostic_yield_for_phenotypes` and by `LOC_PHE`.
- **Filtering Allele Frequency (FAF)** — the gnomAD-derived statistic underlying `POP_FRQ`.
- Sharpen the existing **MDE** entry with the manuscript's precise phrasing (gene + phenotype dyad; a gene may map to more than one MDE — link to the new Spec coverage row for Supplementary Material 21).

### 5.5 `CLN_CCS` maturity annotation fix (`docs/workflows/hod/cln/index.md`)

Replace the `!!! warning "Not yet specified by the SVCv4 Working Group"` block (lines 21–29) with the site's other standard admonition, `!!! note "Not yet modeled here"`, stating that Supplementary Material 4 now specifies `CLN_CCS` and it joins POP/LOC/PFD in the "specified but not yet modeled" bucket — not a Working Group gap.

### 5.6 PFD forward-looking pattern note (`docs/workflows/pfd/index.md`)

Add one short section after "Concepts and codes" naming the shared four-step pipeline (predict → molecular-mechanism/exon-relevance adjustment → functional evidence → informative variants) that every PFD workflow follows, and the four shared sub-modules it depends on (Determining Critical Amino Acids; Molecular Mechanism and Exon Relevance; Informative Variants; Functional Assays) — framed as "the shape of the work," still under the existing "Not yet modeled here" admonition.

### 5.7 De-duplicate the hierarchy statement

Keep `workflows/index.md` as the canonical, full statement. On `overview/svcv4-in-brief.md`, `overview/alignment.md` (if it restates the full chain beyond its existing table), and `reference/summary-table.md`, replace a repeated full restatement with one sentence + a link to `workflows/index.md`. (`overview/alignment.md`'s own table, read in full above, already adds value beyond the bare chain — keep its table, just check for redundant restatement elsewhere on the page.)

### 5.8 `mkdocs.yml` nav

Add `Spec coverage: reference/spec-alignment.md` after `Model reference: reference/model.md` in the Reference tab; add `Reviewing this site: overview/review-guide.md` after `Home: index.md` in the Overview tab; add `Core concepts: reference/concepts.md` right before `Glossary: reference/glossary.md` in the Reference tab (§5.11); restructure the `Locus Specificity (LOC)` nav entry to a nested section (§5.9).

### 5.9 Restructure LOC into a full deep-dive (mirrors CLN)

Per the user's direction, LOC gets the same full treatment as CLN rather than a minimal correction, since it's already modeled to the same depth:

- `git mv docs/workflows/hod/loc.md docs/workflows/hod/loc/index.md`, then rewrite as a concept overview page (mirrors `docs/workflows/hod/cln/index.md`): lists `LOC_PHE`/`LOC_SEG` with ✅, corrects the "not yet modeled" claim, states plainly that the Case model realizes **both** CLN and LOC.
- New `docs/workflows/hod/loc/loc-phe.md` — deep-dive mirroring `cln-aff.md`'s template (What evidence to capture / Scoring), populated from the applicability matrix's `LOC_PHE` column: required — `vbc`, `mde`, `pop_frq_points` (workflow params; note `moi` is **not applicable** here, unlike every other workflow), `id`, `gene_specificity_for_phenotypes`, `testing` + `testing.diagnostic_yield_for_phenotypes`, `vbc_exists`, `additional_variant_exists`; conditional — `additional_variants` (when `additional_variant_exists` is `TRUE`); optional — `sex`, `age`, `phenotypes`, `family_id`, `vbc_zygosity`, `age_matched_penetrance`, `testing.method`, `testing.covers_all_genes_relevant_to_mde`.
- New `docs/workflows/hod/loc/loc-seg.md` — same template, populated from the `LOC_SEG` column: required — `vbc`, `mde`, `moi` (required here, unlike `LOC_PHE`), `pop_frq_points`, `id`, `family_id`, `vbc_exists`, `additional_variant_exists`, `relatives` + its required sub-fields (`parent_of_proband`, `affected_w_mde`, `vbc_exists`, `vbc_zygosity`, `cmp_het_variant_exists`); conditional — `compound_het_variant`, `additional_variants`, `relatives.sex` (required if X-linked), `relatives.severe_phenotype` (required if semi-dominant/X-linked and affected); optional — `sex`, `age`, `phenotypes`, `vbc_zygosity`, `age_matched_penetrance`, `confirmed_parental_relationship`, `relatives.age`, `relatives.phenotypes`.
- Update `mkdocs.yml`'s `Locus Specificity (LOC)` entry to a nested section matching the CLN pattern:
  ```yaml
  - Locus Specificity (LOC):
      - workflows/hod/loc/index.md
      - Phenotype (LOC_PHE): workflows/hod/loc/loc-phe.md
      - Segregation (LOC_SEG): workflows/hod/loc/loc-seg.md
  ```
- Fix the compounding pages: `docs/workflows/hod/index.md` (stop lumping LOC with the POP/PFD stubs — it belongs with CLN as "detailed here"); `docs/workflows/index.md`'s "What this section covers now" paragraph (currently says "the CLN workflows the Case model supports" — change to "the CLN **and LOC** workflows"); `docs/workflows/hod/cln/index.md` line 6 ("This is the concept the Case model realizes" → "...the concepts the Case model realizes" or similar, naming both CLN and LOC).
- Update any internal links pointing at the old `workflows/hod/loc.md` path (grep for it).

### 5.10 `src/svcv4_model/case.py` docstring fix (the only source-file touch)

The module docstring (lines 1–13) currently reads "the case-level **clinical-observation (CLN)** evidence payload." Change to reflect both concepts it actually serves, e.g. "the case-level clinical-observation and locus-specificity (**CLN**/**LOC**) evidence payload." Docstring-only; no logic, schema, or behavior change; re-run `uv run python scripts/export_case_views.py` afterward purely to confirm the drift gate still reports no diff (docstrings aren't part of the generated JSON Schema `$comment`/`title`, so none is expected — this is a sanity check, not an expected change).

### 5.11 New page: `reference/concepts.md`

Nav label "Core concepts", inserted right before "Glossary" in the Reference tab (richer companion to the Glossary's one-liners, not a replacement). Content: the §3.3 table, written as short explanatory entries (what it is, why it matters, which workflows use it, current representation) for VBC, MDE (with the gene↔MDE non-1:1 callout, linking to the Spec coverage row for Supplementary Material 21), Gene (explaining `mde_associated_gene`), MOI (the cross-workflow table-selection driver), Zygosity & Phase, and **Case** itself (the permissive-superset design; applicability driven entirely by the external matrix, not the type; its deliberate split from `WorkflowParameters`). Three entries — Cohort Allele Frequency, Disease Allele Frequency Threshold, Gene-Disease Validity — are written as clearly-flagged forward-looking-only content (not yet modeled), matching the PFD pattern note's treatment: name it, cite the source (VA-Spec Study Result Profiles for Cohort Allele Frequency; Supplementary Material 3 for DAFT; the main manuscript for Gene-Disease Validity), explain why it will matter, and stop there.

## 6. Quality gates

- `uv run mkdocs build --strict` passes.
- `grep -rn 'case_proband_info\|pheno_specificity_for_gene\|all_relevant_genes_tested' docs` returns nothing.
- The Case schema/docs drift gate is unaffected (no exporter/schema changes in this pass) — confirm with `uv run python scripts/export_case_views.py && git diff --quiet -- docs/workflows/case-model.md`.
- Manual read-through: the corrected `first-case.md` JSON actually round-trips against `Case`/`WorkflowParameters` (spot check field names against `src/svcv4_model/case.py`).

## 7. Follow-up backlog (explicitly not this pass)

Recommend opening as separate, later work — do not fold into this docs pass:

1. **Model completeness gaps surfaced by Supplementary Material 4:** add a gnomAD co-occurrence-likelihood-bucket field and a "non-genetic etiology excluded" field to `Case`/`CaseTesting`. (`CLN_CCS` is explicitly **not** on this list — per §3.2 item 2, SVCv4 hasn't yet defined decomposed evidence concepts for it, so there's nothing robust to model until a subsequent SVCv4 version does. Revisit once it does, not before.)
2. **Model Cohort Allele Frequency + DAFT once POP is built:** adopt the VA-Spec [Cohort Allele Frequency Study Result](https://va-spec.ga4gh.org/en/1.0/va-standard-profiles/base-profiles/study-result-profiles.html#cohort-allele-frequency-study-result) profile for population-frequency data rather than inventing bespoke fields; model DAFT (and its three derivation methods) per Supplementary Material 3.
3. **Add a Gene-Disease Validity field somewhere in the model** (`WorkflowParameters` is the likely home, alongside `mde`) — currently nothing represents the ClinGen validity classification that gates which classification tiers (P/LP/etc.) are reachable at all.
4. **Chase the empty Workflow Images Drive folder** (`1dMjLBmXo4dtIZA2PItWNvnAHiRyfvapG`) with Alicia Byrne / Steven Harrison — the dozens of named decision-tree figures referenced throughout the supplements (Cherry-, Orange-, Grapefruit-, Tangerine-, Tangelo-, Mandarin-, Dragonfruit-, Boysenberry-series) aren't available yet, and would materially help both this reorg and the eventual PFD build-out.
5. **Obtain the 10 not-yet-read Supplementary Materials** (2, 5, 7, 10, 12, 14, 17, 18, 19, 20) — neither official Drive folder currently has the complete set of 21.
6. Full POP-modeling, LOC deep-per-data-point nuance, and PFD modeling (existing Phase B backlog).
7. Rule enforcement, case aggregation, SVCv4 point-mapping (existing Case-model Phase 2 backlog).

## 8. Delivery

Suggest a new branch (e.g. `docs/review-readiness`) off `main`, single PR. No code changes, so no CI beyond the docs build/link-audit/drift gates in §6.
