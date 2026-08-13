# PVS-v26-MSH6 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** MSH6 `c.107C>T` (p.Ala36Val), CAID CA007963 → `Proposition.subject`.
- **MDE:** Lynch syndrome / HNPCC, MONDO:0005835.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_ALTV** | The proband's colorectal cancer is explained by a **Pathogenic truncating MSH6 variant in trans** (`c.3202C>T`, p.Arg1068*); no CMMRD/biallelic features → alternate cause (variant). `pheno_severity = MONO_EQ_EXPECTED`. | `case-CLN_ALTV.json` |

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/14, penetrance 0.16 → `pop_frq_points 0`.
- `CLN_ALTV` — the affected phenotype is attributable to the in-trans Pathogenic
  variant, so the VBC receives **no positive clinical credit**.
- `MIS` — BayesDel −0.20 (mildly benign-leaning).

Net: a **VUS** leaning benign — the second-hit Pathogenic variant removes clinical support.

## Open questions

1. `CLN_ALTV` for a dominant-cancer gene where a second in-trans P would give a
   severe biallelic (CMMRD) phenotype — confirm this is the intended alt-cause use.
