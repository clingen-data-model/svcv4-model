# PVS-v19-TP53 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** TP53 `c.641A>T` (p.His214Leu), CAID CA16603036 → `Proposition.subject`.
- **MDE:** Li-Fraumeni syndrome, MONDO:0018875.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | The single proband is **unaffected** (family history of breast cancer only), so contributes no clinical points. | — |

No `case-*.json`. This entry is **evidence-driven** (functional + same-residue).

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/3000, penetrance 0.30, absent from gnomAD → `pop_frq_points 0`.
- `FNC` — yeast + human-cell assays: non-functional transactivation and loss of
  growth suppression; TP53 VCEP combines the three outputs → **+4**.
- `MIS` — a different missense at the **same residue** (`p.His214Arg`, `ClinVar:376615`)
  is **Pathogenic** (PM5-type); the VBC change is less conservative (Grantham 99 vs 29);
  BayesDel 0.32.

Net: **Likely pathogenic** (illustrative), driven by functional + PM5 evidence.

## Open questions

1. Same-residue PM5 with a Pathogenic comparator → confirm the `MIS` weight applied.
2. Should the unaffected proband register as a (0-point) `CLN_UAF` line for provenance?
