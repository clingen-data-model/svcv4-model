# Capture your first case

This page walks through one concrete workflow — **Affected (`CLN_AFF`)** — as a
worked example of a **complex, multi-branch workflow** — contrast with the
simpler [`POP_FRQ` example](capturing-basic-evidence.md) earlier in this
section. (Locus Specificity and, eventually, Population and
Predictive & Functional Data workflows follow the same shape but capture
different evidence; see [Workflows](../workflows/index.md).) If you haven't
already, [The classification inputs](classification-inputs.md) covers the
VBC/MDE/MOI/Gene inputs used below before you dive into workflow-specific
evidence.

A **case** is the case-level evidence a curator captures from the literature to
represent a single human clinical observation supporting (or opposing) variant
pathogenicity — the structured payload behind a `clinical_observation` Evidence
Item.

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
  "vbc": { "id": "clinvar:VCV000000001" },
  "sex": "F",
  "phenotypes": [{ "code": "HP:0001250", "name": "Seizure" }],
  "pheno_specificity_for_mde": "SPECIFIC",
  "testing": { "covers_all_genes_relevant_to_mde": "TRUE" },
  "vbc_zygosity": "HET"
}
```

In prose: *a female proband with a seizure phenotype that is specific to the
MDE; testing covered all genes relevant to the MDE; the variant being
classified (the VBC) is heterozygous, under autosomal-dominant inheritance.*

## What each piece is

- `moi` — the mode of inheritance for the VBC ⇔ MDE pairing.
- `pop_frq_points` — the population-frequency contribution (computed upstream).
- `vbc` — the variant being classified, by id.
- `sex` / `phenotypes` — what's known about the proband (sex, phenotypes).
- `pheno_specificity_for_mde` — how closely the phenotype(s) match what is
  expected for the MDE.
- `testing.covers_all_genes_relevant_to_mde` — whether the test covered all
  genes relevant to the MDE.
- `vbc_zygosity` — the VBC's zygosity in the proband.

`moi`, `pop_frq_points`, and `vbc` are `WorkflowParameters` — submitted
alongside a `Case`, not fields of it (see `src/svcv4_model/case.py`'s own
docstring/design) — while the rest are `Case` fields directly.

## What happens next

This captured case becomes one or more **Evidence Items** under the `CLN_AFF`
**Evidence Line**. The workflow (defined in
[CSpec](../reference/cspec-interop.md)) turns the captured evidence into a
**score**; scores roll up into the **Statement**. See
[Affected (CLN_AFF)](../workflows/hod/cln/cln-aff.md) for the full workflow and
[Case model & applicability](../workflows/case-model.md) for every field and how
its applicability varies by workflow.

## Following the hierarchy

Like every workflow, this `CLN_AFF` capture is an **Evidence Item** that
feeds an **Evidence Line**, which rolls up through the Concept/Category
hierarchy into the **Statement**'s final score — see
[Rolling up Evidence Line scores](rolling-up-scores.md) for exactly how
that works, using a smaller worked example.

!!! note "This is a teaching example"

    Field names follow the current [Case model](../workflows/case-model.md);
    they track the SVCv4 Standards, which have not yet been finalized and are
    still changing to varying degrees.
