# PVS-v21-ANO5 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** ANO5 `c.139-1del` (splice acceptor), CAID CA10605474 → `Proposition.subject`.
- **MDE:** autosomal recessive limb-girdle muscular dystrophy, MONDO:0015152.
- **MOI:** AR. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | Both probands carry only a **single heterozygous** ANO5 variant (no second allele identified) for a **recessive** disease, so neither is a countable biallelic case. | — |

No `case-*.json`.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/50000, penetrance 0.85 (biallelic) → `pop_frq_points 0`.
- `SPL` — loss of the exon-4 acceptor (SpliceAI just above 0.20) → predicted skip of
  in-frame exon 4 (p.Pro47_Met60del, ~1.5% of protein, cytoplasmic region). A
  same-exon P/LP missense with clinical support (`ClinVar:197402`) suggests the exon
  contributes to function.

Net: a **VUS** — predictive evidence only; no countable biallelic case.

## Open questions

1. For an AR disease, how should single-heterozygous-observation probands be
   represented (context vs. a 0-point line)? (Encoded as no case.)
