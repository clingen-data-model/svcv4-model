# Alternative Variant (CLN_ALTV)

**`CLN_ALTV`** is one half of `CLN_ALT` — *affected observations with an
alternate cause of disease*. The **Alternative Variant** workflow covers cases
where a **different variant in the same gene** offers an alternate explanation
for the proband's disease, which counts against the VBC's causality.

## What evidence to capture

Required for an Alternative-Variant case (see the full
[applicability table](case-model.md)):

- `moi` — mode of inheritance.
- `case_proband_info` — including **`pheno_severity`** (severity relative to
  expectation).
- `vbc` — the variant being considered.
- `additional_variant_exists` — must indicate the alternate variant is present.
- **`additional_variants`** — the alternate variant(s): `id`, `gene`,
  `zygosity`, and (since it's the same gene as the VBC) **`phase_in_ref_to_vbc`**
  and `phase_confidence`. Each alternate variant's `classification` must be
  **P/LP** to count for this workflow.

## Scoring

The `CLN_ALTV` points (and how phase and the alternate variant's classification
weigh in) are determined by its workflow in
[ClinGen CSpec](../reference/cspec-interop.md). This model captures the alternate
variant evidence; see [Case model & applicability](case-model.md) for exact
fields. Compare with [Alternative Gene (CLN_ALTG)](cln-altg.md).
