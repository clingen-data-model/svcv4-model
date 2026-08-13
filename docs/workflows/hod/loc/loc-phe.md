# Locus — Phenotype (LOC_PHE)

**`LOC_PHE`** captures evidence that the phenotype(s) observed with the VBC are
specific to the gene — i.e., how narrowly the set of genes known to cause those
phenotypes is confined to the VBC's gene, and how well genetic testing around
the locus supports that specificity.

## What evidence to capture

Required for a `LOC_PHE` case (see the full
[applicability table](../../case-model.md)):

- `vbc`, `mde`, `pop_frq_points` — shared `WorkflowParameters` inputs alongside
  the Case. **Note:** unlike every other workflow, `moi` (mode of inheritance)
  is **not applicable** to `LOC_PHE` — this is unusual and worth calling out
  explicitly.
- `id` — identifies the individual/case.
- `gene_specificity_for_phenotypes` — how specific the observed phenotype(s)
  are to the gene (roughly the inverse of the number of genes known to cause
  them).
- `testing` — and its sub-field **`testing.diagnostic_yield_for_phenotypes`**
  (the diagnostic yield of testing for these phenotypes).
- `vbc_exists` — whether the proband carries the VBC.
- `additional_variant_exists` — whether another relevant variant is present.

Conditional:

- **`additional_variants`** — populated only when `additional_variant_exists`
  is `TRUE`; once present, its sub-fields `id`, `zygosity`,
  `phase_in_ref_to_vbc`, and `classification` are required.

Optional: `sex`, `age`, `phenotypes`, `family_id`, `vbc_zygosity`,
`age_matched_penetrance`, `testing.method`,
`testing.covers_all_genes_relevant_to_mde`.

## Scoring

The points for `LOC_PHE` are produced by its workflow in
[ClinGen CSpec](../../../reference/cspec-interop.md); this model captures the
evidence the workflow consumes. See [Case model & applicability](../../case-model.md)
for the exact `LOC_PHE` field applicability.
