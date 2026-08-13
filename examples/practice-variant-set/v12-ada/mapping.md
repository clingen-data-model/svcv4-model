# PVS-v12-ADA — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** ADA `c.219-2A>G` (canonical splice acceptor), CAID CA252010 → `Proposition.subject`.
- **MDE:** SCID due to adenosine deaminase deficiency (T-B-NK-), MONDO:0007064.
- **MOI:** AR. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** (homozygous) | One proband, T-B-NK- SCID profile, large SCID panel tested → `pheno_specificity_for_mde = SPECIFIC`, `vbc_zygosity = HOM`. | `case-CLN_AFF.json` |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/5000, penetrance 0.50 (biallelic) → `pop_frq_points 0`.
- `CLN_AFF` — one homozygous proband, SPECIFIC phenotype.
- `SPL` — canonical splice acceptor (-2) → skipping of exon 4 → in-frame deletion
  of aa 74-121 (>10% of protein; critical region, PMID 3182793). **RT-PCR
  confirmed** the exon-4 skip; splicing and PRD are concordant.

Net: **Pathogenic** (illustrative).

## Open questions

1. `SPECIFIC` on a **homozygous** (biallelic) AFF case: the matrix note flags
   SPECIFIC as n/a to biallelic AFF, but says the curator makes the call — and the
   tab curator chose SPECIFIC. Confirm this reconciliation.
2. Splicing-assay concordance ("does not add or subtract points") — captured as a
   data field on the `SPL` line; is a dedicated assay concept wanted?
