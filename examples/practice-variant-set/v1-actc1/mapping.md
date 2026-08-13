# PVS-v1-ACTC1 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** ACTC1 `c.488dup` (p.His163GlnfsTer7), CAID CA2627662931 → `Proposition.subject`.
- **MDE:** hypertrophic cardiomyopathy, MONDO:0005045.
- **MOI:** AD. LoF is **NOT** an established mechanism for ACTC1-related HCM.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| **CLN_AFF** | Proband 1: clinical HCM, all HCM genes tested → `CONSISTENT`. | (in `classification.json`) |
| **CLN_UAF** | Proband 2: currently unaffected, family history of DCM. | `case-CLN_UAF.json` |
| **LOC_PHE** | ACTC1 accounts for **<3%** of HCM → low locus specificity for the phenotype. | `case-LOC_PHE.json` |

A third proband (HCM + a MYBPC3 LoF variant) is an **alternate cause** and is not counted.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/200, penetrance 0.40 → `pop_frq_points 0`.
- `CLN_AFF` — proband 1 (CONSISTENT).
- `CLN_UAF` — proband 2 (unaffected carrier).
- `LOC_PHE` — gene specificity ~3%.

Net: a **VUS** — a minor HCM gene where LoF is not the mechanism, with mixed observations.

## Open questions

1. This entry feeds the Workflows page's `CLN_UAF` and `LOC_PHE` per-workflow examples
   (`WORKFLOW_SOURCE` in `export_case_views.py`).
