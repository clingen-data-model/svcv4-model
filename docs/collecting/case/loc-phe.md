# Phenotype specificity (LOC_PHE)

!!! info "Maturity: Draft"

    Fields and applicability track the [Case model](../../workflows/case-model.md);
    scoring is documented elsewhere, not computed here.

**LOC_PHE** collects evidence about **how specifically the locus tracks with a
phenotype** — whether the proband's phenotype points to this gene in particular
rather than to many genes. It uses the [Case superset](index.md); this page names
the portion it turns on.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../reference/glossary.md)).

## What is collected

- **`gene_specificity_for_phenotypes`** (`R`) — how specific the phenotype(s) are
  to the gene (roughly the inverse of the number of genes that cause them).
- **`testing.diagnostic_yield_for_phenotypes`** (`R`) — the diagnostic yield of
  testing for those phenotypes.
- **`additional_variants`** (`C`) — other clinically relevant variants that bear
  on how the locus is interpreted.

Parameters: **`moi`** is **not applicable** (`X`) — phenotype specificity does not
depend on the inheritance path — while **`pop_frq_points`** is required.

## Reference

- Applicability column and per-workflow JSON: [Case model & applicability](../../workflows/case-model.md).
- Full workflow and scoring: [Phenotype (LOC_PHE)](../../workflows/hod/loc/loc-phe.md).
