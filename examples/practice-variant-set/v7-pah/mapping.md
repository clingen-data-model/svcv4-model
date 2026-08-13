# PVS-v7-PAH — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** PAH `c.865G>A` (p.Gly289Arg), CAID CA386294434 → `Proposition.subject`.
- **MDE:** phenylketonuria, MONDO:0009861 → `Proposition.object`.
- **MOI:** AR (biallelic) → `WorkflowParameters.moi`. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** (biallelic) | Two probands with classic PKU, each with a second P/LP variant confirmed in trans (Gly272Ter; Arg155Cys) → `compound_het_variant`. `pheno_specificity_for_mde = CONSISTENT`. | `case-CLN_AFF.json` (proband 1) |
| LOC_PHE | Phe >120 μM with BH4 deficiency excluded is in the >82% diagnostic-yield bucket. | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/5000, penetrance 0.80 (biallelic threshold) → `pop_frq_points 0`.
- `CLN_AFF` — two biallelic probands, classic PKU.
- `MIS` — REVEL 0.98, BayesDel 0.58 (strong), no splicing impact.

## Open questions

1. Only proband 1 is encoded in `case-CLN_AFF.json`; proband 2 is summarized in the
   evidence line. Encode proband 2 as a second submission if aggregation is wanted.
2. Informative same-codon variants (tab references "see right") weren't transcribed
   in the source grid — confirm whether a `MIS` same-residue datum should be added.
