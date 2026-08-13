# PVS-v3-FOXG1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** FOXG1 `c.234_236delGCC` (p.Pro79del), CAID CA258396552 → `Proposition.subject`.
- **MDE:** FOXG1-related disorder, MONDO:0100040 → `Proposition.object`.
- **MOI:** AD → `WorkflowParameters.moi`. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** | Proband 1: severe intellectual disability + microcephaly → `pheno_specificity_for_mde = CONSISTENT`. | `case-CLN_AFF.json` |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/40000, penetrance 0.50 → `pop_frq_points 0`.
- `CLN_AFF` — one proband, phenotype consistent.
- `MIS` (repeat context, **benign-leaning**) — the variant deletes one of six GCC
  repeats in a region gnomAD suggests is **polymorphic**; no splicing impact.

## Why this entry is a deliberate VUS

The clinical support is offset by the polymorphic-repeat context, so the rolled-up
`score_classification` is `variant_of_uncertain_significance`. It's a useful
counter-example to the "everything is pathogenic" pattern.

## Open questions

1. Is a `p.Pro79del` in-frame repeat deletion best represented under `MIS`, or a
   dedicated repeat/`CDS` concept?
2. Should the polymorphic-region signal instead raise `pop_frq_points`?
