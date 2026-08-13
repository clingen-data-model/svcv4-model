# PVS-v28-PTEN — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** PTEN `c.802-3T>A` (intronic, splice region), CAID CA000593 → `Proposition.subject`.
- **MDE:** PTEN hamartoma tumor syndrome, MONDO:0017623.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | The single proband is an **unaffected** 24-yo with a non-specific family cancer history; disease penetrance is low (0.10). | — |

No `case-*.json`.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/9000, penetrance 0.10 → `pop_frq_points 0`.
- `SPL` — splicing predictions show no impact **and** a follow-up **RNA assay** from a
  case found **no abnormal splicing** → benign-leaning for this splice-region variant.

Net: **Likely benign** — an RNA assay directly refutes a splicing effect.

## Open questions

1. A splice assay showing *no* effect is benign evidence; captured as data on the
   `SPL` line — confirm the sign/strength convention.
