# PVS-v22-F8 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** F8 `c.1420G>C` (p.Gly474Arg), CAID CA414914392 → `Proposition.subject`.
- **MDE:** hemophilia A, MONDO:0010602.
- **MOI:** **X-linked** (`XLR`). LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | The variant has not been identified in a case with the relevant phenotype. | — |

No `case-*.json`. This entry is **evidence-driven** (in-silico + same-residue).

## Evidence → lines (`classification.json`)

- `POP_FRQ` — binning approach (X-linked dominant combined table): prevalence 1/10000,
  penetrance 0.20, absent from gnomAD → `pop_frq_points 0`.
- `MIS` — REVEL 0.972 (Grantham 125); plus **same-amino-acid** LP (`c.1420G>A`,
  p.Gly474Arg — **PS1-type**) and two **same-codon** P/LP variants (p.Gly474Glu P,
  p.Gly474Trp LP — **PM5-type**).

Net: **Likely pathogenic** (illustrative), driven by in-silico + PS1/PM5.

## Open questions

1. Same-amino-acid (PS1) vs. same-codon (PM5): both captured as data on the `MIS` line —
   should they be distinct evidence items/concepts?
2. Confirm `XLR` for hemophilia A even though the POP binning uses an X-linked-dominant table.
