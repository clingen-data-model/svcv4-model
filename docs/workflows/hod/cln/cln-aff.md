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
- `case_proband_info` — including **`pheno_specificity_for_gene`** and
  **`all_relevant_genes_tested`** (sex, age, phenotypes are optional but
  encouraged).
- `vbc` — the variant being considered (`id`, case-level `zygosity`).
- `additional_variant_exists` — whether another relevant variant is present.

Conditional:

- **`compound_het_variant`** — only for a biallelic evaluation where the VBC is
  heterozygous; its zygosity is fixed to `HET` and phase to `TRANS`.
- **`additional_variants`** — captured when `additional_variant_exists` is `TRUE`.

## Scoring

The points for `CLN_AFF` are produced by its workflow in
[ClinGen CSpec](../../../reference/cspec-interop.md); this model captures the evidence
the workflow consumes. See [Case model & applicability](../../case-model.md) for the
exact `CLN_AFF` field applicability and [Capture your first case](../../../getting-started/first-case.md)
for a worked example.
