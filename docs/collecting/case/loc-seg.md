# Segregation (LOC_SEG)

!!! info "Maturity: Draft"

    Fields and applicability track the [Case model](../../workflows/case-model.md);
    scoring is documented elsewhere, not computed here.

**LOC_SEG** collects evidence that the VBC **co-segregates with disease across a
family** — affected relatives carry it, unaffected relatives don't. It is the
assessment that most exercises the Case superset's family structure. It uses the
[Case superset](index.md); this page names the portion it turns on.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../reference/glossary.md)).

## What is collected

The distinguishing evidence is the **`relatives[]`** list — each a
[`CaseRelative`](../../reference/evidence-structures.md#caserelative) capturing:

- **`parent_of_proband`** (`R`), **`sex`** (`C`, required if X-linked),
  **`affected_w_mde`** (`R`), **`severe_phenotype`** (`C`, for semi-dominant /
  X-linked when affected), **`age`**, and **`phenotypes`**.
- How the relative carries the VBC: **`vbc_exists`** (`R`), **`vbc_zygosity`**
  (`R`), and **`cmp_het_variant_exists`** (`R`).

Alongside the relatives, the proband-level fields that tie the family together:
**`family_id`** (`R`), **`confirmed_parental_relationship`**, and
**`age_matched_penetrance`**.

Parameters: **`moi`** is required (it changes which relatives count and how) and
**`pop_frq_points`** is required.

## Reference

- Applicability column and per-workflow JSON: [Case model & applicability](../../workflows/case-model.md).
- Full workflow and scoring: [Segregation (LOC_SEG)](../../workflows/hod/loc/loc-seg.md).
