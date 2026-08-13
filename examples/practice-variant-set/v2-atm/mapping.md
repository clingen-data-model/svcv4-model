# PVS-v2-ATM — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** ATM `c.5005+1G>A` (CAID CA382538604) → `Proposition.subject`.
- **MDE:** ataxia telangiectasia, MONDO:0008840 → `Proposition.object`.
- **MOI:** AR (biallelic) → `WorkflowParameters.moi`. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** (biallelic) | Proband 1 meets classic A-T criteria; a second ATM LoF is confirmed in trans → captured as `compound_het_variant` (classification `P`, `phase_confidence HIGH`). `pheno_specificity_for_mde = CONSISTENT` (SPECIFIC is n/a to biallelic AFF). | `case-CLN_AFF.json` |
| LOC_PHE | Diagnostic yield >90% for classic A-T. | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/40000, penetrance 0.90 (biallelic threshold) → `pop_frq_points 0`.
- `CLN_AFF` — one biallelic proband, classic A-T + elevated AFP.
- `SPL` — `+1G>A` → in-frame skip of exon 33, removing part of the HEAT-repeat
  critical domain; same-position LP comparator `ClinVar:371636` (`c.5005+1G>T`).

## Open questions

1. Biallelic AFF specificity — `CONSISTENT` used (SPECIFIC disallowed for biallelic); confirm.
2. Is the in-frame exon-skip best coded as `SPL`, or a `CDS`/`NUL` critical-domain line?
