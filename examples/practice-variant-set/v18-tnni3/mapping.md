# PVS-v18-TNNI3 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** TNNI3 `c.236G>T` (p.Arg79Leu), CAID CA021404 → `Proposition.subject`.
- **MDE:** hypertrophic cardiomyopathy, MONDO:0005045.
- **MOI:** AD. LoF is **NOT** an established mechanism for TNNI3-related HCM.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | The only proband was ascertained in population cohorts (Framingham / Jackson Heart Study) with **no clinical phenotype details**, so no CLN_AFF or CLN_UAF points. | — |

No `case-*.json`.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/200, penetrance 0.30 → `pop_frq_points 0`.
- `MIS` — REVEL 0.542 (intermediate); no predicted splicing impact.

Net: a **VUS** — no usable clinical data and only intermediate in-silico support.

## Open questions

1. LoF-not-a-mechanism plus an intermediate REVEL: is there any positive line here,
   or is VUS-by-insufficient-evidence the right resting state? (Encoded as VUS.)
