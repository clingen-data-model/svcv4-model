# Affected (CLN_AFF)

**CLN_AFF** collects evidence from **affected individuals who carry the VBC** —
the most common source of case-level support for pathogenicity. It is part of the
[Case superset](index.md); this page names the portion of that superset it turns
on.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../reference/glossary.md)).

## What is collected

For each affected proband, the curator captures who the individual is, what they
presented with, how they were tested, and how they carry the VBC:

- **`sex`**, **`phenotypes`**, and **`pheno_specificity_for_mde`** (`C`) — how
  closely the observed phenotype matches what is expected for the MDE.
- **`testing.covers_all_genes_relevant_to_mde`** (`R`) — whether the test that
  found the VBC covered all genes relevant to the MDE — plus, optionally,
  **`testing.non_genetic_etiology_excluded`** (a CLN_AFF refinement factor,
  SM 4).
- **`vbc_exists`** / **`vbc_zygosity`** (`R`) — that the proband carries the VBC,
  and how.
- **Biallelic (AR / compound-het) cases** additionally capture
  **`compound_het_variant`** (with `co_occurrence_likelihood`, SM 4) and
  **`additional_variant_exists`** / **`additional_variants`**.

Parameters: **`moi`** is required (it selects the monoallelic vs. biallelic
scoring path) and **`pop_frq_points`** is required and **gated** — see below.

## The POP_FRQ gate

`CLN_AFF` only awards pathogenic points when the VBC is rare: the
[POP_FRQ gate](../population.md#lead-with-the-gate) makes `CLN_AFF` **not
applicable unless `pop_frq_points ∈ {0.0, −1.0}`** (SM 4). Settle
[Part 2](../population.md) before relying on affected-individual evidence.

## Reference

- Applicability column and per-workflow JSON: [Case model & applicability](../../workflows/case-model.md).
- Full workflow and scoring: [Affected (CLN_AFF)](../../workflows/hod/cln/cln-aff.md).
