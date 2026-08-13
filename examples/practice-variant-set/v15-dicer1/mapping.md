# PVS-v15-DICER1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** DICER1 `c.2T>C` (p.Met1Thr, start-loss), CAID CA10583232 → `Proposition.subject`.
- **MDE:** DICER1-related tumor predisposition, MONDO:0100216.
- **MOI:** AD. LoF is an established mechanism. Penetrance is low (0.10).

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | Proband 1 is **unaffected** and DICER1 penetrance is low → no CLN_UAF. Proband 2's breast cancer is **non-specific**, carries a Pathogenic BRCA1 variant, and has high genetic heterogeneity → no CLN_AFF and no CLN_ALT. | — |

No `case-*.json`: both probands are excluded.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/800, penetrance 0.10 → `pop_frq_points 0`.
- `NUL` — **start-loss** (p.Met1Thr), but three in-frame downstream Met codons
  (Met11/17/24) exist, p.M1 is not highly conserved, and loss of the first ~24 aa
  is only ~1.2% of the protein → LoF weight uncertain.

Net: a **VUS** and a clear "why cases don't count" teaching example.

## Open questions

1. Should start-loss with plausible alternate starts have its own concept/flag?
