# 2 · Population observations (POP)

!!! info "Maturity: Draft"

    Inputs are modeled; the gating behaviour and point tables are documented from
    the SVCv4 Standards, not computed here.

**Population (POP)** is the first assessment family a curator meets, and it earns
its place early: `POP_FRQ` can **gate several downstream assessments**. Getting
it settled before the CLN and LOC codes it gates keeps the rest of the arc from
surprising you.

POP has two evidence codes, both **benignity-only** — they can argue *against*
pathogenicity, never for it:

| Code | Captures |
|---|---|
| `POP_FRQ` | Population (allele) frequency of the VBC, compared against a disease-specific threshold. |
| `POP_HMZ` | Population observations of homozygotes / hemizygotes. |

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../reference/glossary.md)).

## Lead with the gate

`POP_FRQ`'s result is carried as a single value, `WorkflowParameters.pop_frq_points`,
and that value does two jobs:

1. **It contributes its own benignity points** to the classification.
2. **It gates the pathogenic case-counting codes.** In the reference scoring map,
   the **POP_FRQ gate** makes `CLN_AFF` and `CLN_DNV` **not applicable unless the
   VBC is rare** — specifically unless `pop_frq_points ∈ {0.0, −1.0}` (SM 4). A
   variant common enough to earn stronger benignity points is too common for its
   affected-individual and de-novo observations to count *for* pathogenicity.

`pop_frq_points` is a **required input** to `CLN_AFF`, `CLN_DNV`, `LOC_PHE`, and
`LOC_SEG`, and is **not applicable** to `CLN_ALTV`, `CLN_ALTG`, and `CLN_UAF` in
the current applicability matrix. Because it gates the codes in
[Part 3](case/index.md), it is worth settling first — this is the forward
reference the gate depends on.

## What `POP_FRQ` captures

The question is: *is the VBC's population frequency implausibly high for the MDE?*
An implausibly high frequency is evidence of **benignity** — a variant too common
to cause a rare, highly penetrant disease. Answering it needs two values, both of
which are the **starting curation activities** from
[Part 1](curation-activities.md):

- the VBC's **FAF** (the gnomAD lookup), and
- the MDE's **DAFT** (the calculated threshold).

Everything else is comparing the first to the second. A VCEP/community-curated
DAFT is preferred when available; otherwise SVCv4 defines derivation methods,
recorded in `daft_method` (`VCEP_CURATED`, `CALCULATOR`, `BINNING`,
`PATHOGENIC_VARIANTS`).

## What `POP_HMZ` captures

`POP_HMZ` counts homozygote/hemizygote occurrences of the VBC in the population
database — benignity evidence, **counted only from the 2nd occurrence**, and only
when `hmz_eligible` holds (i.e. the MDE's penetrance and severity make affected
individuals implausible among those population samples). It is distinct from
`CLN_UAF`, which requires explicit clinical details.

## How it is structured before sharing

POP's inputs are modeled as [`PopulationEvidence`][svcv4_model.PopulationEvidence]
(the payload behind a `population_frequency` Evidence Item), a permissive entity
where every field is optional:

- **`POP_FRQ`** — `faf`, `faf_source`, `daft`, `daft_method`, and optional
  `daft_calculator_inputs` (`prevalence_denominator`, `penetrance`,
  `locus_heterogeneity`, `allelic_heterogeneity`) for reproducibility. The fifth
  DAFT-calculator input, inheritance, is not re-captured here — it is the shared
  `WorkflowParameters.moi`.
- **`POP_HMZ`** — `homozygote_count`, `hemizygote_count`, and `hmz_eligible`.

Unlike CLN and LOC, POP has **no `Workflow` enum entry and no applicability-matrix
rows**: it is a standalone Evidence Item payload, not a Case workflow.

!!! note "Scoring lives elsewhere"

    The FAF-vs-DAFT fold-change point bands and the `POP_HMZ` per-occurrence
    weights (including the SM 3 prose-vs-Table-7 caveat) are the **reference**,
    not repeated here. See [Population (POP)](../workflows/hod/pop.md) for the
    point tables and [Core concepts](../reference/concepts.md) for Cohort Allele
    Frequency and DAFT in depth. This model captures the inputs; the point
    computation is out of scope.

## Next

The gate is set. Continue to
**[3 · Case & segregation data collection](case/index.md)**, where the codes
`POP_FRQ` gates are collected against the Case superset.
