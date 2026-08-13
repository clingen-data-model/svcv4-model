# PVS-v23-GP1BA — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** GP1BA `c.334G>A` (p.Gly112Arg), CAID CA8314744 → `Proposition.subject`.
- **MDE:** Bernard-Soulier syndrome, MONDO:0009276.
- **MOI:** AR. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | The variant has not been identified in a case with the relevant phenotype. | — |

No `case-*.json`.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/1,000,000, penetrance 1.00 (biallelic) → `pop_frq_points 0`.
- `MIS` — REVEL 0.322 (low); no predicted splicing impact.

Net: a **VUS** by insufficient evidence — no clinical observation and only a low REVEL.

## Open questions

1. A low REVEL (0.322) alone: neutral (encoded), or does it warrant a small
   benign-leaning contribution?
