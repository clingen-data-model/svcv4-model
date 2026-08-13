# PVS-v4-HNF4A — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** HNF4A `c.421del` (p.Arg141AspfsTer29), CAID CA2573106197 → `Proposition.subject`.
- **MDE:** monogenic diabetes, MONDO:0015967 → `Proposition.object`.
- **MOI:** AD → `WorkflowParameters.moi`. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** | Proband 1: HNF4A-MODY phenotype, all other MODY genes negative → `CONSISTENT`. | `case-CLN_AFF.json` |
| LOC_SEG | Variant segregated with MODY in **3 additional affected family members**. | applicable, not yet encoded |
| LOC_PHE | Diagnostic yield 33–50%. | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/1000, penetrance 0.50, absent from gnomAD → `pop_frq_points 0`.
- `CLN_AFF` — one proband, phenotype consistent, other MODY genes negative.
- `NUL` — frameshift → PTC in exon 5/10, predicted NMD in a LoF gene; ≥3 other
  NMD-predicted LoF variants in this exon are Pathogenic (Monogenic Diabetes VCEP).

## Open questions

1. `LOC_SEG` is clearly applicable (3 affected relatives) — encode a
   `case-LOC_SEG.json` next to strengthen this entry?
2. Diagnostic-yield 33–50% is low for `LOC_PHE`; worth encoding?
