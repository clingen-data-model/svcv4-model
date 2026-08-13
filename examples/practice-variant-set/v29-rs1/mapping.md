# PVS-v29-RS1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** RS1 deletion of exon 2 (`c.53-713_78+266del`), CAID CA2499226544 → `Proposition.subject`.
- **MDE:** X-linked retinoschisis, MONDO:0010725.
- **MOI:** **X-linked** (`XLR`). LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** (hemizygous) | A **hemizygous male** proband with retinoschisis by age 13 (visual-acuity impairment, schisis, retinal detachment); exome, no other candidate → `SPECIFIC`, `sex = M`, `vbc_zygosity = HEMI`. | `case-CLN_AFF.json` |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — binning (X-linked, male sex-specific table): prevalence 1/5000,
  penetrance 0.80, absent from gnomAD → `pop_frq_points 0`.
- `CLN_AFF` — hemizygous male proband, RS1-specific phenotype.
- `NUL` — deletion of **out-of-frame exon 2** → p.(Ala18GlyfsTer2) (also removes the
  exon-2 splice sites); 2 Pathogenic + 1 LP LoF variants in this exon (VCEP).

Net: **Pathogenic** (illustrative) — the X-linked hemizygous example of the set.

## Open questions

1. Hemizygous X-linked encoding: `sex = M`, `vbc_zygosity = HEMI` on CLN_AFF — confirm.
