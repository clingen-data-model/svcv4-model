# Locus — Segregation (LOC_SEG)

**`LOC_SEG`** captures evidence that the VBC **co-segregates** with the disease
(MDE) across a family — i.e., whether relatives who are affected carry the VBC
and relatives who are unaffected do not, consistent with the family's mode of
inheritance.

## What evidence to capture

Required for a `LOC_SEG` case (see the full
[applicability table](../../case-model.md)):

- `vbc`, `mde`, `moi`, `pop_frq_points` — shared `WorkflowParameters` inputs
  alongside the Case. Unlike `LOC_PHE`, **`moi`** (mode of inheritance) **is**
  required here.
- `id`, `family_id` — identify the proband and the family.
- `vbc_exists` — whether the proband carries the VBC.
- `additional_variant_exists` — whether another relevant variant is present.
- `relatives` — the segregation data for the family, and within it:
    - **`relatives.parent_of_proband`**
    - **`relatives.affected_w_mde`**
    - **`relatives.vbc_exists`**
    - **`relatives.vbc_zygosity`**
    - **`relatives.cmp_het_variant_exists`**

Conditional:

- **`compound_het_variant`** — only when `vbc_zygosity` is `HET`.
- **`additional_variants`** — populated only when `additional_variant_exists`
  is `TRUE`.
- **`relatives.sex`** — required if the mode of inheritance is X-linked.
- **`relatives.severe_phenotype`** — required if the mode of inheritance is
  semi-dominant or X-linked and the relative is affected.

Optional: `sex`, `age`, `phenotypes`, `vbc_zygosity`, `age_matched_penetrance`,
`confirmed_parental_relationship`, `relatives.age`, `relatives.phenotypes`.

## Scoring

The points for `LOC_SEG` are produced by its workflow in
[ClinGen CSpec](../../../reference/cspec-interop.md); this model captures the
evidence the workflow consumes. See [Case model & applicability](../../case-model.md)
for the exact `LOC_SEG` field applicability.
