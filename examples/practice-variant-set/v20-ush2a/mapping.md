# PVS-v20-USH2A — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** USH2A deletion of exons 63-64 (`c.12295-?_14133+?del`; breakpoints
  unknown), CAID CA3246685756 → `Proposition.subject`.
- **MDE:** Usher syndrome, MONDO:0019501.
- **MOI:** AR. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** (homozygous) | Proband 1 is homozygous with congenital SNHL + RP → `SPECIFIC`, `vbc_zygosity = HOM`. (Probands 2-3 are in trans with a VUS / known Pathogenic LoF.) | `case-CLN_AFF.json` (proband 1) |
| LOC_PHE | Usher-syndrome phenotype with other genes ruled out → ~60% diagnostic yield. | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/30000, penetrance 0.80 (biallelic; inverse-AF ≈ 0.0001388) → `pop_frq_points 0`.
- `CLN_AFF` — three biallelic probands, USH2A-specific dual sensory phenotype.
- `CDS` — in-frame deletion of exons 63-64 (aa 4099-4711) removing **11.7%** of the
  protein, but outside a known critical domain.

Net: **Likely pathogenic** (illustrative) — a structural (multi-exon deletion) example.

## Open questions

1. Multi-exon in-frame deletion: coded here as `CDS`; is a dedicated structural concept wanted?
2. Encode probands 2-3 (comp-het) as additional submissions?
