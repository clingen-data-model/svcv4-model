# Capture your first case

A **case** is the case-level evidence a curator captures from the literature to
represent a single human clinical observation supporting (or opposing) variant
pathogenicity — the structured payload behind a `clinical_observation` Evidence
Item. This page walks through a minimal **Affected (`CLN_AFF`)** case.

Throughout, **"the variant" means the VBC** (Variant Being Classified) and
**"the disease/condition" means the MDE** (Mendelian Disease Entity). See the
[Glossary](../reference/glossary.md).

## The minimal shape

For an Affected case, a handful of fields are required (the rest are optional or
not applicable — see the [per-workflow applicability table](../workflows/case-model.md)).
A minimal capture looks like:

```json
{
  "moi": "AD",
  "pop_frq_points": 0,
  "case_proband_info": {
    "sex": "F",
    "phenotypes": [{ "code": "HP:0001250", "name": "Seizure" }],
    "pheno_specificity_for_gene": "SPECIFIC",
    "all_relevant_genes_tested": "TRUE"
  },
  "vbc": { "id": "clinvar:VCV000000001", "zygosity": "HET" }
}
```

In prose: *a female proband with a seizure phenotype that is specific to the
gene; all relevant genes for the disorder were tested; the variant being
classified (the VBC) is heterozygous, under autosomal-dominant inheritance.*

## What each piece is

- `moi` — the mode of inheritance for the VBC ⇔ MDE pairing.
- `pop_frq_points` — the population-frequency contribution (computed upstream).
- `case_proband_info` — what's known about the proband (sex, age, phenotypes,
  phenotype specificity, …).
- `vbc` — the variant being classified, by id and case-level zygosity.

## What happens next

This captured case becomes one or more **Evidence Items** under the `CLN_AFF`
**Evidence Line**. The workflow (defined in
[CSpec](../reference/cspec-interop.md)) turns the captured evidence into a
**score**; scores roll up into the **Statement**. See
[Affected (CLN_AFF)](../workflows/hod/cln/cln-aff.md) for the full workflow and
[Case model & applicability](../workflows/case-model.md) for every field and how
its applicability varies by workflow.

!!! note "This is a teaching example"

    Field names follow the current [Case model](../workflows/case-model.md);
    they track the SVCv4 Standards, which have not yet been finalized and are
    still changing to varying degrees.
