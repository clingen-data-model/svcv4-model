# PVS-v30-RYR1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** RYR1 `c.12383C>T` (p.Ala4128Val), CAID CA405668522 → `Proposition.subject`.
- **MDE:** malignant hyperthermia, susceptibility to, 1, MONDO:0007783.
- **MOI:** AD. LoF is **NOT** an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** | One proband with an MH episode + positive IVCT; CACNA1S ruled out → `CONSISTENT` (a substantial fraction of MHS has no identified genetic cause). | `case-CLN_AFF.json` |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/10000, penetrance **0.01** (very low) → `pop_frq_points 0`.
- `CLN_AFF` — one consistent clinical case (MH + IVCT).
- `MIS` — REVEL 0.248 (low); no informative same-codon variants; no splice impact.

Net: a **VUS** — one clinical case is offset by low REVEL and LoF not being the mechanism.

## Open questions

1. Very low penetrance (0.01) for a susceptibility trait — does it change POP handling?
