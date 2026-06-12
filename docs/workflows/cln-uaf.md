# Unaffected (CLN_UAF)

**`CLN_UAF`** captures evidence from **unaffected individuals** carrying the VBC
— observations that count against the variant's causality (someone has the
variant but not the disease). Workflows exist for autosomal-dominant and for
autosomal-recessive / X-linked inheritance.

## What evidence to capture

Required for an Unaffected case (see the full
[applicability table](case-model.md)):

- `moi` — mode of inheritance.
- `case_proband_info` — including **`age_matched_penetrance`** (how penetrant the
  condition is by the individual's age — central to interpreting an unaffected
  carrier).
- `vbc` — the variant being considered.

Population-frequency, phenotype-specificity, compound-het, and additional-variant
fields are **not applicable** to `CLN_UAF`.

## Scoring

The weight of an unaffected observation depends heavily on age-matched
penetrance, but the scoring **rules** are defined in
[ClinGen CSpec](../reference/cspec-interop.md). This model captures the evidence;
see [Case model & applicability](case-model.md) for the exact `CLN_UAF` fields.
