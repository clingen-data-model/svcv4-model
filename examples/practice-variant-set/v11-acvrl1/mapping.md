# PVS-v11-ACVRL1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** ACVRL1 `c.88C>T` (p.Pro30Ser), CAID CA211326 → `Proposition.subject`.
- **MDE:** hereditary hemorrhagic telangiectasia, MONDO:0019180.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_ALTV** | Case 1: typical HHT, but a Pathogenic LoF ACVRL1 variant (`c.191delA`) is confirmed **in trans** → alternate cause (variant). | `case-CLN_ALTV.json` |
| **CLN_ALTG** | Case 2: typical HHT, but a Pathogenic LoF variant in **ENG** (a different HHT gene) accounts for the phenotype → alternate cause (gene). | `case-CLN_ALTG.json` |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/4000, penetrance 0.80 → `pop_frq_points 0`.
- `CLN_ALTV` / `CLN_ALTG` — both observed cases are explained by other pathogenic
  variants, so neither credits the VBC.
- `MIS` — REVEL 0.499 (intermediate); no other variants in this codon.

Net: a **VUS** — the alternate causes remove clinical support and in-silico is intermediate.

## Open questions

1. This entry feeds the Workflows page's `CLN_ALTV` **and** `CLN_ALTG` per-workflow examples.
