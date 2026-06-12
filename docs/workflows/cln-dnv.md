# De Novo (CLN_DNV)

**`CLN_DNV`** captures evidence from **affected individuals in whom the VBC
occurred de novo** (not inherited from either parent) — strong support under
autosomal-dominant / X-linked-male inheritance.

## What evidence to capture

Required for a De Novo case (see the full
[applicability table](case-model.md)):

- `moi` — mode of inheritance.
- `pop_frq_points` — the population-frequency contribution.
- `case_proband_info` — including **`pheno_specificity_for_gene`**,
  **`confirmed_parental_relationship`** (was the parentage confirmed?), and
  **`all_relevant_genes_tested`**.
- `vbc` — the variant being considered (`id`, case-level `zygosity`).

The compound-het and additional-variant fields are **not applicable** to
`CLN_DNV`.

## Scoring

Points for `CLN_DNV` come from its CSpec workflow; the strength of a de novo
observation typically depends on whether the parental relationship was confirmed
and on phenotype specificity — but those **rules** live in
[ClinGen CSpec](../reference/cspec-interop.md). This model captures the evidence;
see [Case model & applicability](case-model.md) for the exact `CLN_DNV` fields.
