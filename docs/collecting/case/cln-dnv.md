# De novo (CLN_DNV)

!!! info "Maturity: Draft"

    Fields and applicability track the [Case model](../../workflows/case-model.md);
    scoring is documented elsewhere, not computed here.

**CLN_DNV** collects evidence that the VBC arose **de novo** in an affected
proband — a strong signal for pathogenicity when parentage is confirmed. It uses
the [Case superset](index.md); this page names the portion it turns on.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../reference/glossary.md)).

## What is collected

- **`confirmed_parental_relationship`** (`R`) — the crux: whether the biological
  parent-child relationship was confirmed, which separates a scored de-novo
  observation from an assumed one.
- **`pheno_specificity_for_mde`** (`C`) — how closely the proband's phenotype
  matches the MDE.
- **`testing.covers_all_genes_relevant_to_mde`** (`R`) — whether the test covered
  all genes relevant to the MDE.

Parameters: **`moi`** is required and **`pop_frq_points`** is required and
**gated** — like `CLN_AFF`, `CLN_DNV` is a pathogenic counting code, so the
[POP_FRQ gate](../population.md#lead-with-the-gate) makes it not applicable unless
`pop_frq_points ∈ {0.0, −1.0}` (SM 4).

## Reference

- Applicability column and per-workflow JSON: [Case model & applicability](../../workflows/case-model.md).
- Full workflow and scoring: [De novo (CLN_DNV)](../../workflows/hod/cln/cln-dnv.md).
