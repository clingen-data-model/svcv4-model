# PVS-v6-NF1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** NF1 `c.3496G>C` (p.Gly1166Arg), CAID CA398989536 → `Proposition.subject`.
- **MDE:** neurofibromatosis type 1, MONDO:0018975 → `Proposition.object`.
- **MOI:** AD → `WorkflowParameters.moi`. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** | Three probands: P1 clinical NF1 dx (`SPECIFIC`), P2 multiple neurofibromas (`CONSISTENT`), P3 CALMs/freckling/Lisch (`SPECIFIC`). | `case-CLN_AFF.json` (P1) |
| CLN_DNV | Proband 1 is a **confirmed de novo** (parental relationships confirmed). | applicable, not yet encoded |
| LOC_PHE | Clinical NF1 diagnosis is in the >82% diagnostic-yield bucket. | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/2600, penetrance 0.80, absent from gnomAD → `pop_frq_points 0`.
- `CLN_AFF` — three probands (specificity as above).
- `SPL` — variant at the **last base of exon 26/57**; SpliceAI donor loss (0.76)
  → out-of-frame exon skip → LoF; informative variants share the prediction.
  Missense predictors (REVEL 0.51, BayesDel 0.05) are intermediate — the splice
  effect drives the line, not the amino-acid change.

## Open questions

1. Proband 1's confirmed de novo is a strong `CLN_DNV` — encode `case-CLN_DNV.json`?
   (The generator currently sources CLN_DNV from SCN2A; NF1 is a *confirmed* de novo.)
2. Splice vs. missense: confirmed the line is coded `SPL`, not `MIS`.
