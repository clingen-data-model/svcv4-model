# PVS-v14-ATXN7L3 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** ATXN7L3 `c.332del` (p.Asn111ThrfsTer16), CAID CA3246641821 → `Proposition.subject`.
- **MDE:** ATXN7L3-related developmental delay (MONDO pending; using
  `MONDO:0100038` "complex neurodevelopmental disorder").
- **MOI:** AD. LoF is only the **SUSPECTED** mechanism (GenCC LoF framework).

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** | Exome case: global DD, language disorder, hypotonia; all genes tested → `CONSISTENT`. | `case-CLN_AFF.json` |
| CLN_DNV | Neither parent carries the variant; parental relationships **confirmed** → confirmed de novo. | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — new gene-disease; heterogeneity estimates unavailable, so a binning
  approach is used (prevalence 1/1000, penetrance 0.50 → threshold 0.001) → `pop_frq_points 0`.
- `CLN_AFF` — one exome proband, CONSISTENT; also a confirmed de novo (CLN_DNV).
- `NUL` — frameshift → predicted NMD, **but** LoF is only *Suspected* (GenCC), and
  two other LoF variants in this exon are VUS → reduced weight.

Net: a **VUS** — the Suspected mechanism and new gene-disease temper the evidence.

## Open questions

1. Confirmed de novo → encode `case-CLN_DNV.json` to strengthen this entry?
2. How should a *Suspected* (vs. established) LoF mechanism scale the `NUL` weight?
