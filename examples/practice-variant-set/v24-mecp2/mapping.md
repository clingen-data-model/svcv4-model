# PVS-v24-MECP2 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** MECP2 `c.907_1080del` (p.Ser303_Glu360del, in-frame), CAID CA274615 → `Proposition.subject`.
- **MDE:** Rett syndrome, MONDO:0010726.
- **MOI:** **X-linked dominant** (`XLD`). LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** | Two affected **females (XX)** with Rett / atypical-Rett features (exome; other genes cleared) → `CONSISTENT`. For X-linked-dominant MDEs, affected XX and XY count under the monoallelic section. | `case-CLN_AFF.json` (case 1) |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — binning (X-linked dominant combined table): prevalence 1/10000,
  penetrance 0.80, absent from gnomAD → `pop_frq_points 0`.
- `CLN_AFF` — two affected females, phenotype consistent.
- `CDS` — in-frame deletion of 58 aa (~11% of protein) in the last exon,
  **overlapping the Transcriptional Repression Domain** (285-313) including the VCEP
  critical minimal region; two smaller Pathogenic deletions are fully contained.

Net: **Likely pathogenic** (illustrative) — an X-linked-dominant, critical-domain example.

## Open questions

1. X-linked counting: `sex = F` recorded on the case; confirm the monoallelic-section
   handling for affected XX under an XLD MDE.
2. In-frame deletion overlapping a critical domain: coded `CDS`; dedicated concept wanted?
