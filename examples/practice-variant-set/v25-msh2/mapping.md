# PVS-v25-MSH2 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** MSH2 `c.630G>A` (p.Met210Ile), CAID CA039549 → `Proposition.subject`.
- **MDE:** Lynch syndrome / HNPCC, MONDO:0005835.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | No clinical data provided. | — |

No `case-*.json`. This entry is **evidence-driven** (functional MAVE assay).

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/14, penetrance 0.40 → `pop_frq_points 0`.
- `FNC` — **MAVE** (massively parallel functional testing; Jia et al.); functional
  score −3.662 → calibrated OddsPath **0.04** → −4 points (**benign**).
- `MIS` — REVEL 0.40 (low).

Net: **Likely benign** — driven by the calibrated MAVE functional assay.

## Open questions

1. MAVE/OddsPath calibration is a functional-assay concept; captured as data on the
   `FNC` line. Is a dedicated calibrated-assay representation wanted?
