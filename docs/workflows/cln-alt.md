# Alternative Cause (CLN_ALT)

**`CLN_ALT`** — *Alternative Cause* — captures evidence that an **alternate
explanation** for the proband's disease exists, which counts **against** the
VBC's causality. It has two subtypes, kept together here:

- **[Alternative Cause-Variant (`CLN_ALTV`)](#alternative-cause-variant-cln_altv)**
  — a *different variant in the same gene* offers the alternate explanation.
- **[Alternative Cause-Gene (`CLN_ALTG`)](#alternative-cause-gene-cln_altg)** — a
  variant in a *different gene* offers the alternate explanation.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../reference/glossary.md)). Both subtypes are distinct workflows in
the [Case model](case-model.md) (separate columns in its applicability matrix),
so use that page for the exact field applicability.

## Alternative Cause-Variant (CLN_ALTV)

The **Alternative Cause-Variant** subtype covers cases where a **different
variant in the same gene** offers an alternate explanation for the proband's
disease.

### What evidence to capture

Required (see the full [applicability table](case-model.md)):

- `moi` — mode of inheritance.
- `case_proband_info` — including **`pheno_severity`** (severity relative to
  expectation).
- `vbc` — the variant being considered.
- `additional_variant_exists` — must indicate the alternate variant is present.
- **`additional_variants`** — the alternate variant(s): `id`, `gene`,
  `zygosity`, and (since it's the same gene as the VBC) **`phase_in_ref_to_vbc`**
  and `phase_confidence`. Each alternate variant's `classification` must be
  **P/LP** to count.

### Scoring

The `CLN_ALTV` points (and how phase and the alternate variant's classification
weigh in) are determined by its workflow in
[ClinGen CSpec](../reference/cspec-interop.md). This model captures the evidence.

## Alternative Cause-Gene (CLN_ALTG)

The **Alternative Cause-Gene** subtype covers cases where a variant in a
**different gene** offers an alternate explanation for the proband's disease.

### What evidence to capture

Required (see the full [applicability table](case-model.md)):

- `moi` — mode of inheritance.
- `case_proband_info` — including:
    - **`pheno_severity`** — *conditional*: the `BIALLELIC_LT_EXPECTED` value is
      **not applicable** to Alternative Cause-Gene (the workflow drops it).
    - **`age_matched_penetrance`** — *conditional*: applicable for Alternative
      Gene among the conditional workflows.
- `vbc` — the variant being considered.
- `additional_variant_exists` — must indicate the alternate-gene variant is present.
- **`additional_variants`** — the alternate variant(s): `id`, `gene` (including
  **`mde_associated_gene`**, since the gene differs from the VBC's), `zygosity`,
  and `classification` (must be **P/LP**).

### Scoring

`CLN_ALTG` points come from its CSpec workflow; phenotype severity and
age-matched penetrance feed that scoring, but the **rules** live in
[ClinGen CSpec](../reference/cspec-interop.md). This model captures the evidence.
