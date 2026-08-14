# Affected (CLN_AFF)

**`CLN_AFF`** captures evidence from **affected individuals** carrying the VBC —
observations that the variant is seen in people who have the disease/condition
(MDE). Workflows exist for autosomal-dominant and for autosomal-recessive /
X-linked inheritance.

## What evidence to capture

Required for an Affected case (see the full
[applicability table](../../case-model.md)):

- `moi` — mode of inheritance.
- `pop_frq_points` — the population-frequency contribution.
- `sex` / `phenotypes` — proband sex and phenotypes (optional but encouraged).
- **`pheno_specificity_for_mde`** — how closely the phenotype(s) match what is
  expected for the MDE.
- **`testing.covers_all_genes_relevant_to_mde`** — whether the test covered all
  genes relevant to the MDE.
- `vbc` — the variant being classified (`id`, case-level `zygosity`).
- `additional_variant_exists` — whether another relevant variant is present.

Optional refinement factors ([Supplementary Material 4](https://docs.google.com/document/d/17XnPmgTpzgQ8hfzOZNCcXIBwnNwbVkP0KIv3Dw5Bz_M/edit)),
which downgrade a proband's category alongside testing thoroughness:

- `testing.non_genetic_etiology_excluded` — whether a non-genetic etiology for
  the proband's phenotype has been excluded (`TriState`; a sibling to
  `covers_all_genes_relevant_to_mde`).

Conditional:

- **`compound_het_variant`** — only for a biallelic evaluation where the VBC is
  heterozygous; its zygosity is fixed to `HET` and phase to `TRANS`. For
  biallelic scoring it also carries `co_occurrence_likelihood` — the gnomAD
  co-occurrence bucket (`<0.0001` / `>0.0001–0.01`, or `NOT_ASSESSED`) that
  SM 4's Table 2 uses to select a row, computed as
  (in-trans + unphased counts) / gnomAD v2 exome total.
- **`additional_variants`** — captured when `additional_variant_exists` is `TRUE`.

## Scoring

The points for `CLN_AFF` are produced by its workflow in
[ClinGen CSpec](../../../reference/cspec-interop.md); this model captures the evidence
the workflow consumes — including the two SM 4 factors above (the
co-occurrence bucket and the non-genetic-etiology flag), which are **captured,
not computed** here. See [Case model & applicability](../../case-model.md) for the
exact `CLN_AFF` field applicability and [Capture your first case](../../../getting-started/first-case.md)
for a worked example.
