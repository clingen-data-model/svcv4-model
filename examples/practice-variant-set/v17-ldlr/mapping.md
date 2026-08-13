# PVS-v17-LDLR — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** LDLR `c.1216C>A` (p.Arg406=, splice-altering), CAID CA023436 → `Proposition.subject`.
- **MDE:** familial hypercholesterolemia, MONDO:0005439.
- **MOI:** **Semidominant** (`SD`). LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** (AD) | Probands 1 & 2 meet FH clinical criteria; FH panel negative for other genes → `SPECIFIC`. | `case-CLN_AFF.json` (proband 1) |
| CLN_AFF (biallelic) / LOC_PHE | Proband 3 is homozygous/AR FH (LDLc 704) with `p.Gln254Ter` (P) in trans; biallelic FH diagnostic yield ~60%. | applicable, not yet encoded |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/200, penetrance 0.80 → `pop_frq_points 0`.
- `CLN_AFF` — two AD probands meeting FH criteria (all FH genes tested).
- `SPL` — the synonymous-looking change **creates a new splice acceptor** in exon 9
  → frameshift (`p.Ser397ThrfsTer6`); **minigene + RT-PCR confirmed** (PMID 19371225,
  17335829); splicing/PRD concordant.

Net: **Pathogenic** (illustrative). A good "silent ≠ benign" splicing example.

## Open questions

1. `MOI = SD` (semidominant): confirm the CLN_AFF handling for a semidominant gene.
2. Encode the biallelic proband 3 (+ LOC_PHE) as a second submission?
