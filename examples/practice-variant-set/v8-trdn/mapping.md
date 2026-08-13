# PVS-v8-TRDN — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** TRDN `c.1462A>T` (p.Lys488Ter), CAID CA365563886 → `Proposition.subject`.
- **MDE:** catecholaminergic polymorphic ventricular tachycardia, MONDO:0017990.
- **MOI:** AR. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_UAF** | An **unaffected** individual (family history of sudden cardiac death) carries the variant heterozygous; no second TRDN variant found. | `case-CLN_UAF.json` |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/7000, penetrance 0.75 (biallelic threshold) → `pop_frq_points 0`.
- `CLN_UAF` — one unaffected het carrier (expected for a recessive condition → uninformative).
- `NUL` — nonsense `p.Lys488Ter` in **exon 23 of MANE Select**, outside the
  cardiac-predominant transcript (exons 1-8); LoF variants after exon 8 are not
  P/LP, so LoF weight is uncertain.

Net: a **VUS** — no informative clinical data and transcript-limited LoF.

## Open questions

1. Does an unaffected het carrier for an AR condition warrant a `CLN_UAF` line at
   all, or is it purely context? (Encoded as 0-point.)
