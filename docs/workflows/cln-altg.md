# Alternative Gene (CLN_ALTG)

**`CLN_ALTG`** is the other half of `CLN_ALT` — *affected observations with an
alternate cause of disease*. The **Alternative Gene** workflow covers cases where
a variant in a **different gene** offers an alternate explanation for the
proband's disease.

## What evidence to capture

Required for an Alternative-Gene case (see the full
[applicability table](case-model.md)):

- `moi` — mode of inheritance.
- `case_proband_info` — including:
    - **`pheno_severity`** — *conditional*: the `BIALLELIC_LT_EXPECTED` value is
      **not applicable** to Alternative Gene (the workflow drops it).
    - **`age_matched_penetrance`** — *conditional*: applicable for Alternative
      Gene among the conditional workflows.
- `vbc` — the variant being considered.
- `additional_variant_exists` — must indicate the alternate-gene variant is present.
- **`additional_variants`** — the alternate variant(s): `id`, `gene` (including
  **`mde_associated_gene`**, since the gene differs from the VBC's), `zygosity`,
  and `classification` (must be **P/LP**).

## Scoring

`CLN_ALTG` points come from its CSpec workflow; phenotype severity and
age-matched penetrance feed that scoring, but the **rules** live in
[ClinGen CSpec](../reference/cspec-interop.md). This model captures the evidence;
see [Case model & applicability](case-model.md). Compare with
[Alternative Variant (CLN_ALTV)](cln-altv.md).
