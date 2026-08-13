# PVS-v13-AIPL1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** AIPL1 `c.150C>T` (p.Asp50=, **synonymous**), CAID CA8328608 → `Proposition.subject`.
- **MDE:** AIPL1-related retinopathy, MONDO:0100438.
- **MOI:** AR. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | No clinical data provided. | — |

No `case-*.json`: no clinical observations.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/6000, penetrance 1.00 (biallelic) → `pop_frq_points 0`.
- `POP_HMZ` — **2 homozygotes in gnomAD**. For a near-100%-penetrant, early-onset
  recessive disease, homozygotes are not expected → **benign-leaning** (count = 2
  minus 1 per the POP_HMZ recommendation).
- `MIS` — **synonymous** change, no predicted splicing impact → benign-leaning.

Net: **Likely benign** (illustrative) — a useful benign counter-example.

## Open questions

1. `POP_HMZ` is a POP concept not yet in the Case workflow enum — modeled here only
   as an evidence line on the `Statement`. Confirm placement.
2. Synonymous/no-impact coded under `MIS`; is a dedicated `BP7`-style concept wanted?
