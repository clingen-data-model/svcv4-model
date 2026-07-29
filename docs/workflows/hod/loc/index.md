# Locus Specificity (LOC)

**Locus Specificity (LOC)** is the Evidence Concept (under
[Human Observational Data](../index.md)) for evidence about how specifically
the variant/locus tracks with phenotype and disease. This is one of the two
concepts the [Case model](../../case-model.md) realizes (together with
[Clinical Observations](../cln/index.md)) — LOC is captured by the **same Case
model** that realizes CLN, not a separate structure.

!!! note "Locus evidence implicates the allele, not necessarily a single variant"

    `LOC_PHE` and `LOC_SEG` evidence implicates a **locus/allele** — via a
    phenotype-to-gene match or via genetic linkage — not a specific variant.
    When an allele carries a single clinically relevant variant (the common
    case, and the only one this model currently represents), that distinction
    doesn't change anything in practice. When an allele carries more than one
    clinically relevant variant, the evidence must be apportioned across them
    rather than applied to just one — a case this model doesn't yet handle.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../../reference/glossary.md)).

## Codes and their workflows

| Code | Workflow(s) | Detailed here |
|---|---|---|
| [`LOC_PHE`](loc-phe.md) | Observation of a specific phenotype | ✅ |
| [`LOC_SEG`](loc-seg.md) | Segregation of the variant with disease (co-segregation) | ✅ |

## How to read each workflow page

Each LOC workflow page describes **what evidence to capture** (the Evidence
Items), links to the generated **applicability table** on the
[Case model](../../case-model.md) page (which fields are required/optional/
conditional/not-applicable for that workflow), and points to
[CSpec](../../../reference/cspec-interop.md) for the scoring rules.
