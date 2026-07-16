# Case model

A **Case** is the case-level payload a curator captures from the literature to
represent a single human clinical (CLN) observation supporting (or opposing)
variant pathogenicity. It is the structured `data` behind a
`clinical_observation` Evidence Item.

The model is a permissive **superset**: every attribute is optional on the type.
Which attributes are required (`R`), optional (`O`), conditional (`C`), or not
applicable (`X`) depends on the CLN workflow — `CLN_AFF` (Affected), `CLN_DNV`
(De novo), `CLN_ALTV` (Alternative Cause-Variant), `CLN_ALTG` (Alternative
Cause-Gene), and `CLN_UAF` (Unaffected). `CLN_ALTV` + `CLN_ALTG` are subtypes of
`CLN_ALT` (Alternative Cause).

Applicability and the conditional rules live in a single source of truth,
`schemas/applicability/case_applicability.yaml`. The per-workflow JSON Schemas
under `schemas/json/case/` and the tables below are generated from it; this
phase documents the conditional rules but does not enforce them.

See the [`Case` model reference][svcv4_model.Case] for field types.

This is the **structured backbone** of the
[Clinical Observations](hod/cln/index.md) workflows: each CLN workflow
page describes *what evidence to capture*, and the per-workflow tables below say
exactly which fields apply. Terminology follows the
[Glossary](../reference/glossary.md) — "the variant" is the **VBC**, "the
disease/condition" is the **MDE**.

## Applicability by workflow

<!-- BEGIN GENERATED: applicability tables -->

**Legend:** <span class="appl-r">required (R)</span> &nbsp;·&nbsp; <span class="appl-c">conditional (C)</span> &nbsp;·&nbsp; <span class="appl-o">optional (O)</span> &nbsp;·&nbsp; <span class="appl-x">not applicable (X)</span>

### Workflow parameters

The shared inputs each workflow takes alongside the `case` — `vbc`, `mde`, `moi`, `pop_frq_points`. Required by the workflows but **not** part of the Case data structure (they feed the workflow matrix that determines applicability and scoring).

<div class="appl-params">
<table class="appl-matrix-table"><thead><tr><th>AFF</th><th>DNV</th><th>ALTV</th><th>ALTG</th><th>UAF</th><th>PHE</th><th>SEG</th><th>Property</th><th>Notes</th></tr></thead><tbody><tr><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><code>vbc</code></td><td class="appl-notes">the Variant Being Considered; a shared parameter for every workflow</td></tr><tr><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<code>id</code></td><td class="appl-notes"></td></tr><tr><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<code>gene</code></td><td class="appl-notes"></td></tr><tr><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>symbol</code></td><td class="appl-notes"></td></tr><tr><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>id</code></td><td class="appl-notes">gene identifier (e.g. HGNC / NCBI id)</td></tr><tr><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>mde_associated_gene</code></td><td class="appl-notes">whether the VBC gene is the MDE-associated gene</td></tr><tr><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>transcript</code></td><td class="appl-notes">transcript reference (e.g. RefSeq accession)</td></tr><tr><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><code>mde</code></td><td class="appl-notes">the Mendelian Disease Entity the VBC is assessed against</td></tr><tr><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<code>curie</code></td><td class="appl-notes">e.g. MONDO:0007254, OMIM:114480</td></tr><tr><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<code>label</code></td><td class="appl-notes"></td></tr><tr><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><code>moi</code></td><td class="appl-notes">AD, AR, XLD, XLR, SD — ALTV does not yet support AR/XLR</td></tr><tr><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><code>pop_frq_points</code></td><td class="appl-notes">must be &gt;= -1.0</td></tr></tbody></table>
</div>

### Case workflow matrix

Every attribute of the Case data structure across the seven workflows (five clinical `CLN_*` and two locus-based `LOC_*`), with the nested structure preserved. Rows with nested attributes can be expanded or collapsed; use the controls above the table to expand/collapse all or show the tree to a given depth. Conditional rules are summarized in **Notes**.

<div class="appl-matrix">
<div class="appl-matrix-controls"><button type="button" data-appl-expand="all">Expand all</button><button type="button" data-appl-collapse="all">Collapse all</button><span class="appl-level-label">Show to depth:</span><button type="button" data-appl-level="1">1</button><button type="button" data-appl-level="2">2</button><button type="button" data-appl-level="3">3</button></div>
<table class="appl-matrix-table"><thead><tr><th>AFF</th><th>DNV</th><th>ALTV</th><th>ALTG</th><th>UAF</th><th>PHE</th><th>SEG</th><th>Property</th><th>Notes</th></tr></thead><tbody><tr class="appl-row" data-path="id" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle id"></button><code>id</code></td><td class="appl-notes">match individuals across workflows (DNV/AFF, PHE/AFF, ALT/AFF, UAF standalone)</td></tr><tr class="appl-row" data-path="family_id" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle family_id"></button><code>family_id</code></td><td class="appl-notes">match individuals in families across UAF/AFF and SEG/AFF</td></tr><tr class="appl-row" data-path="sex" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle sex"></button><code>sex</code></td><td class="appl-notes">M/F/U/T</td></tr><tr class="appl-row" data-path="age" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle age"></button><code>age</code></td><td class="appl-notes">age + unit, or an age range; general or disease-specific</td></tr><tr class="appl-row" data-path="phenotypes" data-depth="0" data-parent="" data-children="2"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle phenotypes"></button><code>phenotypes</code></td><td class="appl-notes">0..many</td></tr><tr class="appl-row" data-path="phenotypes.name" data-depth="1" data-parent="phenotypes" data-children="0"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle name"></button><code>name</code></td><td class="appl-notes"></td></tr><tr class="appl-row" data-path="phenotypes.code" data-depth="1" data-parent="phenotypes" data-children="0"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle code"></button><code>code</code></td><td class="appl-notes">HPO identifier when possible</td></tr><tr class="appl-row" data-path="pheno_specificity_for_mde" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle pheno_specificity_for_mde"></button><code>pheno_specificity_for_mde</code></td><td class="appl-notes">SPECIFIC, CONSISTENT, INCONSISTENT — how closely phenotype matches the MDE; 'SPECIFIC' n/a to biallelic AFF, none apply to biallelic DNV; curator makes the call, rule coordination is out of scope</td></tr><tr class="appl-row" data-path="gene_specificity_for_phenotypes" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle gene_specificity_for_phenotypes"></button><code>gene_specificity_for_phenotypes</code></td><td class="appl-notes">e.g. 100%, 50% — how specific the phenotype(s) are to the gene (roughly the inverse of the number of genes causing them)</td></tr><tr class="appl-row" data-path="testing" data-depth="0" data-parent="" data-children="3"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle testing"></button><code>testing</code></td><td class="appl-notes"></td></tr><tr class="appl-row" data-path="testing.method" data-depth="1" data-parent="testing" data-children="0"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle method"></button><code>method</code></td><td class="appl-notes">e.g. Sanger, Exome, Genome, Cyto — CSV allowed for multiple methods; a single diagnostic yield / covers-all value applies</td></tr><tr class="appl-row" data-path="testing.diagnostic_yield_for_phenotypes" data-depth="1" data-parent="testing" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle diagnostic_yield_for_phenotypes"></button><code>diagnostic_yield_for_phenotypes</code></td><td class="appl-notes">e.g. 100%, 50% — supporting evidence captured as notes only this phase, not structured values</td></tr><tr class="appl-row" data-path="testing.covers_all_genes_relevant_to_mde" data-depth="1" data-parent="testing" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle covers_all_genes_relevant_to_mde"></button><code>covers_all_genes_relevant_to_mde</code></td><td class="appl-notes">true, false — all relevant genes for the disease were covered by the test</td></tr><tr class="appl-row" data-path="pheno_severity" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle pheno_severity"></button><code>pheno_severity</code></td><td class="appl-notes">BIALLELIC&lt;expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG — CLN_ALTG excludes <code>BIALLELIC_LT_EXPECTED</code></td></tr><tr class="appl-row" data-path="age_matched_penetrance" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle age_matched_penetrance"></button><code>age_matched_penetrance</code></td><td class="appl-notes">&lt;80%, 80-100%, near 100%</td></tr><tr class="appl-row" data-path="confirmed_parental_relationship" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle confirmed_parental_relationship"></button><code>confirmed_parental_relationship</code></td><td class="appl-notes">true, false</td></tr><tr class="appl-row" data-path="vbc_exists" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle vbc_exists"></button><code>vbc_exists</code></td><td class="appl-notes">TRUE / FALSE / UNKNOWN — whether the proband carries the VBC</td></tr><tr class="appl-row" data-path="vbc_zygosity" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle vbc_zygosity"></button><code>vbc_zygosity</code></td><td class="appl-notes">HET / HOM / HEMI — zygosity of the VBC in the proband; compound_het_variant applies only when this is HET</td></tr><tr class="appl-row" data-path="compound_het_variant" data-depth="0" data-parent="" data-children="3"><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle compound_het_variant"></button><code>compound_het_variant</code></td><td class="appl-notes">only when vbc_zygosity is HET and there is another same-gene variant that is also HET and in trans; zygosity (HET) and phase (TRANS) are implied, so not captured — requires <code>vbc_zygosity == HET</code></td></tr><tr class="appl-row" data-path="compound_het_variant.id" data-depth="1" data-parent="compound_het_variant" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle id"></button><code>id</code></td><td class="appl-notes"></td></tr><tr class="appl-row" data-path="compound_het_variant.phase_confidence" data-depth="1" data-parent="compound_het_variant" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle phase_confidence"></button><code>phase_confidence</code></td><td class="appl-notes">confidence that the variant is in trans with the VBC</td></tr><tr class="appl-row" data-path="compound_het_variant.classification" data-depth="1" data-parent="compound_het_variant" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle classification"></button><code>classification</code></td><td class="appl-notes"></td></tr><tr class="appl-row" data-path="additional_variant_exists" data-depth="0" data-parent="" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle additional_variant_exists"></button><code>additional_variant_exists</code></td><td class="appl-notes">TRUE / FALSE / UNKNOWN — TriState (Yes/No/Unknown). TRUE asserts an additional variant exists but does NOT itself carry the details — see additional_variants.</td></tr><tr class="appl-row" data-path="additional_variants" data-depth="0" data-parent="" data-children="6"><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle additional_variants"></button><code>additional_variants</code></td><td class="appl-notes">applies only when additional_variant_exists is TRUE; the data layer permits TRUE with an empty array (details omitted) — feasible, but flagged at validate_case time for workflows that require the details. Compound-het additional variants are NOT supported. — requires <code>additional_variant_exists == TRUE</code></td></tr><tr class="appl-row" data-path="additional_variants.id" data-depth="1" data-parent="additional_variants" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle id"></button><code>id</code></td><td class="appl-notes"></td></tr><tr class="appl-row" data-path="additional_variants.gene" data-depth="1" data-parent="additional_variants" data-children="4"><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle gene"></button><code>gene</code></td><td class="appl-notes">required if gene is different from the VBC gene</td></tr><tr class="appl-row" data-path="additional_variants.gene.symbol" data-depth="2" data-parent="additional_variants.gene" data-children="0"><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle symbol"></button><code>symbol</code></td><td class="appl-notes">gene symbol; follows the gene's applicability</td></tr><tr class="appl-row" data-path="additional_variants.gene.id" data-depth="2" data-parent="additional_variants.gene" data-children="0"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle id"></button><code>id</code></td><td class="appl-notes">gene identifier</td></tr><tr class="appl-row" data-path="additional_variants.gene.mde_associated_gene" data-depth="2" data-parent="additional_variants.gene" data-children="0"><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle mde_associated_gene"></button><code>mde_associated_gene</code></td><td class="appl-notes">required if gene is different from VBC gene</td></tr><tr class="appl-row" data-path="additional_variants.gene.transcript" data-depth="2" data-parent="additional_variants.gene" data-children="0"><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle transcript"></button><code>transcript</code></td><td class="appl-notes">transcript reference</td></tr><tr class="appl-row" data-path="additional_variants.zygosity" data-depth="1" data-parent="additional_variants" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle zygosity"></button><code>zygosity</code></td><td class="appl-notes">HOM / HET / HEMI</td></tr><tr class="appl-row" data-path="additional_variants.phase_in_ref_to_vbc" data-depth="1" data-parent="additional_variants" data-children="0"><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle phase_in_ref_to_vbc"></button><code>phase_in_ref_to_vbc</code></td><td class="appl-notes">only if same gene as VBC</td></tr><tr class="appl-row" data-path="additional_variants.phase_confidence" data-depth="1" data-parent="additional_variants" data-children="0"><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle phase_confidence"></button><code>phase_confidence</code></td><td class="appl-notes">only if phase is captured</td></tr><tr class="appl-row" data-path="additional_variants.classification" data-depth="1" data-parent="additional_variants" data-children="0"><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle classification"></button><code>classification</code></td><td class="appl-notes">must be P-LP if ALTV or ALTG; must be VUS/P-LP if AFF or PHE</td></tr><tr class="appl-row" data-path="relatives" data-depth="0" data-parent="" data-children="9"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop"><button class="appl-row-toggle" type="button" aria-label="toggle relatives"></button><code>relatives</code></td><td class="appl-notes">capture multiple relatives, singularly or in bulk</td></tr><tr class="appl-row" data-path="relatives.parent_of_proband" data-depth="1" data-parent="relatives" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle parent_of_proband"></button><code>parent_of_proband</code></td><td class="appl-notes">true, false</td></tr><tr class="appl-row" data-path="relatives.sex" data-depth="1" data-parent="relatives" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle sex"></button><code>sex</code></td><td class="appl-notes">required if X-linked — X-linked MOI</td></tr><tr class="appl-row" data-path="relatives.age" data-depth="1" data-parent="relatives" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle age"></button><code>age</code></td><td class="appl-notes"></td></tr><tr class="appl-row" data-path="relatives.phenotypes" data-depth="1" data-parent="relatives" data-children="2"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle phenotypes"></button><code>phenotypes</code></td><td class="appl-notes">0..many</td></tr><tr class="appl-row" data-path="relatives.phenotypes.name" data-depth="2" data-parent="relatives.phenotypes" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle name"></button><code>name</code></td><td class="appl-notes"></td></tr><tr class="appl-row" data-path="relatives.phenotypes.code" data-depth="2" data-parent="relatives.phenotypes" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-o">O</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle code"></button><code>code</code></td><td class="appl-notes">HPO identifier when possible</td></tr><tr class="appl-row" data-path="relatives.affected_w_mde" data-depth="1" data-parent="relatives" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle affected_w_mde"></button><code>affected_w_mde</code></td><td class="appl-notes">true, false</td></tr><tr class="appl-row" data-path="relatives.severe_phenotype" data-depth="1" data-parent="relatives" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-c">C</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle severe_phenotype"></button><code>severe_phenotype</code></td><td class="appl-notes">true, false — distinct concept from pheno_severity — semi-dominant or X-linked MOI and affected</td></tr><tr class="appl-row" data-path="relatives.vbc_exists" data-depth="1" data-parent="relatives" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle vbc_exists"></button><code>vbc_exists</code></td><td class="appl-notes">true, false</td></tr><tr class="appl-row" data-path="relatives.vbc_zygosity" data-depth="1" data-parent="relatives" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle vbc_zygosity"></button><code>vbc_zygosity</code></td><td class="appl-notes">het / hom / hemi</td></tr><tr class="appl-row" data-path="relatives.cmp_het_variant_exists" data-depth="1" data-parent="relatives" data-children="0"><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-x">X</span></td><td class="appl-w"><span class="appl-r">R</span></td><td class="appl-prop">&nbsp;&nbsp;&nbsp;&nbsp;<button class="appl-row-toggle" type="button" aria-label="toggle cmp_het_variant_exists"></button><code>cmp_het_variant_exists</code></td><td class="appl-notes">true, false</td></tr></tbody></table>
</div>

### Per-workflow structures

Expand a workflow to see its full input as a JSON example with mock data: the workflow parameters that apply (e.g. `moi`, `pop_frq_points`) plus a nested `case` object with only that workflow's applicable Case fields — **bold** = required, <span class="appl-c">underlined</span> = conditional, *italic* = optional; not-applicable fields are omitted. Use the **Hide optional** button (top-right of each example) to collapse the example to just the required and conditional fields.

<details class="appl-detail">
<summary>Affected <code>CLN_AFF</code></summary>
<div class="appl-json-wrap">
<input type="checkbox" class="appl-toggle-cb" id="appl-cb-CLN_AFF">
<label class="appl-toggle" for="appl-cb-CLN_AFF"><span class="t-all">Hide optional</span><span class="t-req">Show optional</span></label>
<pre class="appl-json appl-full">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
      <span class="j-key appl-o">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>,
    <span class="j-key appl-o">"label"</span>: <span class="j-str">"Stargardt disease"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-r">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-c">"pheno_specificity_for_mde"</span>: <span class="j-str">"SPECIFIC"</span>,
    <span class="j-key appl-r">"testing"</span>: {
      <span class="j-key appl-o">"method"</span>: <span class="j-str">"Exome"</span>,
      <span class="j-key appl-r">"covers_all_genes_relevant_to_mde"</span>: <span class="j-str">"TRUE"</span>
    },
    <span class="j-key appl-o">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-c">"compound_het_variant"</span>: {
      <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000002"</span>,
      <span class="j-key appl-r">"phase_confidence"</span>: <span class="j-str">"HIGH"</span>,
      <span class="j-key appl-r">"classification"</span>: <span class="j-str">"P"</span>
    },
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-c">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-c">"gene"</span>: {
          <span class="j-key appl-c">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
          <span class="j-key appl-c">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
        },
        <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-c">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
        <span class="j-key appl-c">"phase_confidence"</span>: <span class="j-str">"LOW"</span>,
        <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ]
  }
}
</pre>
<pre class="appl-json appl-req">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-r">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-c">"pheno_specificity_for_mde"</span>: <span class="j-str">"SPECIFIC"</span>,
    <span class="j-key appl-r">"testing"</span>: {
      <span class="j-key appl-r">"covers_all_genes_relevant_to_mde"</span>: <span class="j-str">"TRUE"</span>
    },
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-c">"compound_het_variant"</span>: {
      <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000002"</span>,
      <span class="j-key appl-r">"phase_confidence"</span>: <span class="j-str">"HIGH"</span>,
      <span class="j-key appl-r">"classification"</span>: <span class="j-str">"P"</span>
    },
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-c">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-c">"gene"</span>: {
          <span class="j-key appl-c">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-c">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>
        },
        <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-c">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
        <span class="j-key appl-c">"phase_confidence"</span>: <span class="j-str">"LOW"</span>,
        <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ]
  }
}
</pre>
</div>
</details>

<details class="appl-detail">
<summary>De novo <code>CLN_DNV</code></summary>
<div class="appl-json-wrap">
<input type="checkbox" class="appl-toggle-cb" id="appl-cb-CLN_DNV">
<label class="appl-toggle" for="appl-cb-CLN_DNV"><span class="t-all">Hide optional</span><span class="t-req">Show optional</span></label>
<pre class="appl-json appl-full">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
      <span class="j-key appl-o">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>,
    <span class="j-key appl-o">"label"</span>: <span class="j-str">"Stargardt disease"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-o">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-c">"pheno_specificity_for_mde"</span>: <span class="j-str">"SPECIFIC"</span>,
    <span class="j-key appl-r">"testing"</span>: {
      <span class="j-key appl-o">"method"</span>: <span class="j-str">"Exome"</span>,
      <span class="j-key appl-r">"covers_all_genes_relevant_to_mde"</span>: <span class="j-str">"TRUE"</span>
    },
    <span class="j-key appl-o">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"confirmed_parental_relationship"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>
  }
}
</pre>
<pre class="appl-json appl-req">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-c">"pheno_specificity_for_mde"</span>: <span class="j-str">"SPECIFIC"</span>,
    <span class="j-key appl-r">"testing"</span>: {
      <span class="j-key appl-r">"covers_all_genes_relevant_to_mde"</span>: <span class="j-str">"TRUE"</span>
    },
    <span class="j-key appl-r">"confirmed_parental_relationship"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>
  }
}
</pre>
</div>
</details>

<details class="appl-detail">
<summary>Alternative Cause-Variant <code>CLN_ALTV</code></summary>
<div class="appl-json-wrap">
<input type="checkbox" class="appl-toggle-cb" id="appl-cb-CLN_ALTV">
<label class="appl-toggle" for="appl-cb-CLN_ALTV"><span class="t-all">Hide optional</span><span class="t-req">Show optional</span></label>
<pre class="appl-json appl-full">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
      <span class="j-key appl-o">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>,
    <span class="j-key appl-o">"label"</span>: <span class="j-str">"Stargardt disease"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-o">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-r">"pheno_severity"</span>: <span class="j-str">"MONO_EQ_EXPECTED"</span>,
    <span class="j-key appl-o">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-r">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-r">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
        <span class="j-key appl-r">"phase_confidence"</span>: <span class="j-str">"LOW"</span>,
        <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ]
  }
}
</pre>
<pre class="appl-json appl-req">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-r">"pheno_severity"</span>: <span class="j-str">"MONO_EQ_EXPECTED"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-r">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-r">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
        <span class="j-key appl-r">"phase_confidence"</span>: <span class="j-str">"LOW"</span>,
        <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ]
  }
}
</pre>
</div>
</details>

<details class="appl-detail">
<summary>Alternative Cause-Gene <code>CLN_ALTG</code></summary>
<div class="appl-json-wrap">
<input type="checkbox" class="appl-toggle-cb" id="appl-cb-CLN_ALTG">
<label class="appl-toggle" for="appl-cb-CLN_ALTG"><span class="t-all">Hide optional</span><span class="t-req">Show optional</span></label>
<pre class="appl-json appl-full">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
      <span class="j-key appl-o">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>,
    <span class="j-key appl-o">"label"</span>: <span class="j-str">"Stargardt disease"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-o">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-c">"pheno_severity"</span>: <span class="j-str">"MONO_EQ_EXPECTED"</span>,
    <span class="j-key appl-o">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-r">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-r">"gene"</span>: {
          <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
          <span class="j-key appl-r">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
        },
        <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ]
  }
}
</pre>
<pre class="appl-json appl-req">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-c">"pheno_severity"</span>: <span class="j-str">"MONO_EQ_EXPECTED"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-r">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-r">"gene"</span>: {
          <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-r">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>
        },
        <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ]
  }
}
</pre>
</div>
</details>

<details class="appl-detail">
<summary>Unaffected <code>CLN_UAF</code></summary>
<div class="appl-json-wrap">
<input type="checkbox" class="appl-toggle-cb" id="appl-cb-CLN_UAF">
<label class="appl-toggle" for="appl-cb-CLN_UAF"><span class="t-all">Hide optional</span><span class="t-req">Show optional</span></label>
<pre class="appl-json appl-full">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
      <span class="j-key appl-o">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>,
    <span class="j-key appl-o">"label"</span>: <span class="j-str">"Stargardt disease"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-r">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-r">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>
  }
}
</pre>
<pre class="appl-json appl-req">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-r">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-r">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>
  }
}
</pre>
</div>
</details>

<details class="appl-detail">
<summary>Locus — Phenotype <code>LOC_PHE</code></summary>
<div class="appl-json-wrap">
<input type="checkbox" class="appl-toggle-cb" id="appl-cb-LOC_PHE">
<label class="appl-toggle" for="appl-cb-LOC_PHE"><span class="t-all">Hide optional</span><span class="t-req">Show optional</span></label>
<pre class="appl-json appl-full">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
      <span class="j-key appl-o">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>,
    <span class="j-key appl-o">"label"</span>: <span class="j-str">"Stargardt disease"</span>
  },
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-o">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-r">"gene_specificity_for_phenotypes"</span>: <span class="j-str">"50%"</span>,
    <span class="j-key appl-r">"testing"</span>: {
      <span class="j-key appl-o">"method"</span>: <span class="j-str">"Exome"</span>,
      <span class="j-key appl-r">"diagnostic_yield_for_phenotypes"</span>: <span class="j-str">"100%"</span>,
      <span class="j-key appl-o">"covers_all_genes_relevant_to_mde"</span>: <span class="j-str">"TRUE"</span>
    },
    <span class="j-key appl-o">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-o">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-c">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-r">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
        <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ]
  }
}
</pre>
<pre class="appl-json appl-req">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>
  },
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-r">"gene_specificity_for_phenotypes"</span>: <span class="j-str">"50%"</span>,
    <span class="j-key appl-r">"testing"</span>: {
      <span class="j-key appl-r">"diagnostic_yield_for_phenotypes"</span>: <span class="j-str">"100%"</span>
    },
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-c">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-r">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
        <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ]
  }
}
</pre>
</div>
</details>

<details class="appl-detail">
<summary>Locus — Segregation <code>LOC_SEG</code></summary>
<div class="appl-json-wrap">
<input type="checkbox" class="appl-toggle-cb" id="appl-cb-LOC_SEG">
<label class="appl-toggle" for="appl-cb-LOC_SEG"><span class="t-all">Hide optional</span><span class="t-req">Show optional</span></label>
<pre class="appl-json appl-full">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
      <span class="j-key appl-o">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
      <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>,
    <span class="j-key appl-o">"label"</span>: <span class="j-str">"Stargardt disease"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-r">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-o">"pheno_specificity_for_mde"</span>: <span class="j-str">"SPECIFIC"</span>,
    <span class="j-key appl-o">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-o">"confirmed_parental_relationship"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-o">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-o">"compound_het_variant"</span>: {
      <span class="j-key appl-o">"id"</span>: <span class="j-str">"clinvar:VCV000000002"</span>,
      <span class="j-key appl-o">"phase_confidence"</span>: <span class="j-str">"HIGH"</span>,
      <span class="j-key appl-o">"classification"</span>: <span class="j-str">"P"</span>
    },
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-c">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-c">"gene"</span>: {
          <span class="j-key appl-c">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-o">"id"</span>: <span class="j-str">"HGNC:34"</span>,
          <span class="j-key appl-c">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-o">"transcript"</span>: <span class="j-str">"NM_000350.3"</span>
        },
        <span class="j-key appl-o">"zygosity"</span>: <span class="j-str">"HOM"</span>,
        <span class="j-key appl-o">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
        <span class="j-key appl-o">"phase_confidence"</span>: <span class="j-str">"LOW"</span>,
        <span class="j-key appl-o">"classification"</span>: <span class="j-str">"LP"</span>
      }
    ],
    <span class="j-key appl-r">"relatives"</span>: [
      {
        <span class="j-key appl-r">"parent_of_proband"</span>: <span class="j-str">"TRUE"</span>,
        <span class="j-key appl-c">"sex"</span>: <span class="j-str">"F"</span>,
        <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">35</span>, <span class="j-key">"unit"</span>: <span class="j-str">"YEAR"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"35 yrs"</span> },
        <span class="j-key appl-o">"phenotypes"</span>: [
          {
            <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
            <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
          }
        ],
        <span class="j-key appl-r">"affected_w_mde"</span>: <span class="j-str">"TRUE"</span>,
        <span class="j-key appl-c">"severe_phenotype"</span>: <span class="j-str">"FALSE"</span>,
        <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
        <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
        <span class="j-key appl-r">"cmp_het_variant_exists"</span>: <span class="j-str">"FALSE"</span>
      }
    ]
  }
}
</pre>
<pre class="appl-json appl-req">
{
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"gene"</span>: {
      <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>
    }
  },
  <span class="j-key appl-r">"mde"</span>: {
    <span class="j-key appl-r">"curie"</span>: <span class="j-str">"MONDO:0007254"</span>
  },
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"PROBAND-1"</span>,
    <span class="j-key appl-r">"family_id"</span>: <span class="j-str">"FAM-1"</span>,
    <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
    <span class="j-key appl-c">"additional_variants"</span>: [
      {
        <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
        <span class="j-key appl-c">"gene"</span>: {
          <span class="j-key appl-c">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
          <span class="j-key appl-c">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>
        }
      }
    ],
    <span class="j-key appl-r">"relatives"</span>: [
      {
        <span class="j-key appl-r">"parent_of_proband"</span>: <span class="j-str">"TRUE"</span>,
        <span class="j-key appl-c">"sex"</span>: <span class="j-str">"F"</span>,
        <span class="j-key appl-r">"affected_w_mde"</span>: <span class="j-str">"TRUE"</span>,
        <span class="j-key appl-c">"severe_phenotype"</span>: <span class="j-str">"FALSE"</span>,
        <span class="j-key appl-r">"vbc_exists"</span>: <span class="j-str">"TRUE"</span>,
        <span class="j-key appl-r">"vbc_zygosity"</span>: <span class="j-str">"HET"</span>,
        <span class="j-key appl-r">"cmp_het_variant_exists"</span>: <span class="j-str">"FALSE"</span>
      }
    ]
  }
}
</pre>
</div>
</details>

<!-- END GENERATED: applicability tables -->
