# PVS-v10-SCN2A — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** SCN2A `c.1108T>C` (p.Phe370Leu), CAID CA349020765 → `Proposition.subject`.
- **MDE:** complex neurodevelopmental disorder, MONDO:0100038.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_DNV** | De novo occurrence in one individual (**parental relationships unconfirmed**) → `confirmed_parental_relationship = FALSE`; phenotype consistent; exome, no other variants. | `case-CLN_DNV.json` |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/200, penetrance 0.50, absent from gnomAD → `pop_frq_points 0`.
- `CLN_DNV` — de novo (unconfirmed parentage), phenotype consistent.
- `MIS` — REVEL 0.977, BayesDel 0.52 (strong); no splice impact.

Net: **Likely pathogenic** (illustrative).

## Open questions

1. This entry feeds the Workflows page's `CLN_DNV` per-workflow example. A *confirmed*
   de novo alternative exists (NF1, ATXN7L3) if a stronger DNV exemplar is preferred.
