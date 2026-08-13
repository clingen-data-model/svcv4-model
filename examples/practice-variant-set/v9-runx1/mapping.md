# PVS-v9-RUNX1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** RUNX1 `c.1412_1413dup` (p.Leu472AlafsTer123), CAID CA658799413 → `Proposition.subject`.
- **MDE:** hereditary thrombocytopenia and hematologic cancer predisposition syndrome, MONDO:0011071.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **LOC_SEG** | Segregates with FPD/AML in **7 affected relatives**. | `case-LOC_SEG.json` |
| CLN_AFF | Proband with thrombocytopenia + AML; all relevant genes tested → `CONSISTENT`. | (in `classification.json`) |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/40, penetrance 0.85, absent from gnomAD → `pop_frq_points 0`.
- `CLN_AFF` — one consistent proband.
- `LOC_SEG` — 7 affected relatives co-segregate.
- `CDS` — frameshift at Leu472 **escaping NMD** (past the c.917 boundary) that alters
  the **VWRPY motif** (a critical functional domain); elongation >100 codons past native stop.

Net: **Likely pathogenic** (illustrative) — strong segregation + critical-domain alteration.

## Open questions

1. This entry feeds the Workflows page's `LOC_SEG` per-workflow example.
