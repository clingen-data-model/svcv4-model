# PVS-v27-MYOC — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** MYOC `c.719A>G` (p.Glu240Gly), CAID CA343726916 → `Proposition.subject`.
- **MDE:** open-angle glaucoma, MONDO:0005338.
- **MOI:** AD. LoF is **NOT** an established mechanism for MYOC-related OAG.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | Not yet identified in a proband with juvenile/primary open-angle glaucoma. | — |

No `case-*.json`.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/24, penetrance 0.56 → `pop_frq_points 0`.
- `MIS` — REVEL 0.205 (low); no informative same-codon variants; no splice impact.

Net: a **VUS** by insufficient evidence.

## Open questions

1. Low REVEL alone: neutral (encoded) vs. a small benign-leaning contribution?
