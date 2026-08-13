# PVS-v16-DYSF — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** DYSF `c.5626G>A` (p.Asp1876Asn), CAID CA222190 → `Proposition.subject`.
- **MDE:** autosomal recessive limb-girdle muscular dystrophy, MONDO:0015152.
- **MOI:** AR. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** (homozygous) | Proband: progressive LGMD with absent dysferlin; homozygous for the VBC → `SPECIFIC`, `vbc_zygosity = HOM`. | `case-CLN_AFF.json` |
| LOC_SEG | **Three affected siblings** are also homozygous → co-segregation (AR). | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/50000, penetrance 0.85 (biallelic) → `pop_frq_points 0`.
- `CLN_AFF` — homozygous proband, DYSF-specific phenotype.
- `FNC` — dysferlin membrane-localization assay: p.Asp1876Asn fails to reach the
  membrane; VCEP-calibrated to **+2** (3 P / 9 B controls).
- `MIS` — REVEL 0.819 and a **same-residue LP** comparator (`ClinVar:2885593`,
  p.Asp1876His); the VBC Asp→Asn is more conservative (Grantham 23 vs 81).

Net: **Pathogenic** (illustrative).

## Open questions

1. Encode `case-LOC_SEG.json` for the 3 affected homozygous sibs to complete the entry?
2. Functional weight (+2) is VCEP-calibrated — captured as data on the `FNC` line.
