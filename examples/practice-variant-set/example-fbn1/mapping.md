# PVS-EXAMPLE-FBN1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.
This is the spreadsheet's **template ("Example: FBN1")** tab.

## Anchor (SPOQ)

- **VBC:** FBN1 `c.7003C>T` (p.Arg2335Trp), CAID CA016924 → `Proposition.subject`.
- **MDE:** Marfan syndrome, MONDO:0007947.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** | Proband 1: TAAD, TAAD panel clear (`CONSISTENT`). Proband 2: ectopia lentis (FBN1 ~60-68% of ectopia lentis), confirmed de novo, exome clear (`SPECIFIC`). | `case-CLN_AFF.json` (proband 2) |
| CLN_DNV | Proband 2 is a **confirmed de novo** (parentage confirmed). | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/5000, penetrance 0.85 → `pop_frq_points 0`.
- `CLN_AFF` — two probands (TAAD; ectopia lentis + de novo).
- `MIS` — REVEL 0.841 (supportive); no splice impact.

Net: **Likely pathogenic** (illustrative). Also exercises CLN_DNV.

## Open questions

1. Encode proband 2's confirmed de novo as `case-CLN_DNV.json` too?
