# Population (POP)

**Population (POP)** is an Evidence Concept under
[Human Observational Data](index.md), covering population-level evidence about the
variant. Its two evidence codes are both **benignity-only** — they can argue
against pathogenicity, never for it.

| Code | Captures |
|---|---|
| `POP_FRQ` | Population (allele) frequency of the variant, compared against a disease-specific threshold. |
| `POP_HMZ` | Population observations of homozygotes / hemizygotes. |

!!! note "Modeled here — inputs captured, scoring documented not computed"

    POP's structured evidence inputs are modeled as
    [`PopulationEvidence`](../../reference/model.md) (the payload behind a
    `population_frequency` Evidence Item). This model **captures** the inputs a
    curator records; it does **not** compute the points — the scoring tables
    below are reproduced from the SVCv4 Standards for reference. Point
    computation is deferred with the rest of the model's rule/method
    enforcement. Unlike the CLN and LOC workflows, POP has no `Workflow` enum
    entry and no applicability-matrix entries: it is a standalone Evidence Item
    payload, not a Case workflow.

## What to capture

`PopulationEvidence` is a permissive entity (every field optional):

- **`POP_FRQ`** — `faf` (the variant's **Filtering Allele Frequency**: the
  population-max, lower-95%-CI-bound allele frequency, typically from gnomAD),
  `faf_source` (e.g. `gnomAD v4.1.1`), `daft` (the **Disease Allele Frequency
  Threshold**), `daft_method` (how the DAFT was obtained), and optional
  `daft_calculator_inputs` (`prevalence_denominator`, `penetrance`,
  `locus_heterogeneity`, `allelic_heterogeneity`) for reproducibility.
- **`POP_HMZ`** — `homozygote_count`, `hemizygote_count`, and `hmz_eligible`
  (whether the MDE's penetrance + severity make affected individuals
  implausible in the population database, so occurrences count as benignity
  evidence).

The **inheritance pattern** — a fifth DAFT-calculator input — is not
re-captured here; it is the shared `WorkflowParameters.moi`.

## DAFT: the threshold the FAF is compared against

The DAFT is an estimated ceiling for how common a truly pathogenic variant for
the specific MDE could plausibly be. A VCEP/community-curated threshold is
preferred when available; otherwise SVCv4
([Supplementary Material 3](https://docs.google.com/document/d/1XON2eq4HSM-guWlqitEnb8PghY0quNbA7_1WmmxvLj8/edit))
defines three derivation methods, recorded in `daft_method`:

| `daft_method` | When |
|---|---|
| `VCEP_CURATED` | An expert-consensus threshold exists (preferred). |
| `CALCULATOR` | Data support prevalence, penetrance, and locus/allelic heterogeneity estimates. |
| `BINNING` | Sparse data or X-linked inheritance — DAFT read from lookup tables by inheritance. |
| `PATHOGENIC_VARIANTS` | ≥ 10 known P/LP variants; also a cross-check on the other methods. |

## Scoring (documented from SM 3 — not computed here)

`POP_FRQ` awards benignity points by the fold-difference between the variant's
FAF and the DAFT:

| FAF vs DAFT | `POP_FRQ` points |
|---|---|
| < 1.5× | 0.0 |
| > 1.5× and < 5× | −1.0 |
| > 5× and < 15× | −3.0 |
| ≥ 15× | −6.0 |

These inequalities are reproduced from SM 3, which does not crisply assign the
exact boundary values; its worked example (FBN1-related Marfan, DAFT 0.000118)
treats the top band as inclusive (FAF ≥ 0.001770 → −6.0).

`POP_HMZ` awards **−0.5 points per eligible occurrence, counted only from the
2nd** eligible occurrence — homozygous occurrences for AD/AR MDEs, homozygous
*or* hemizygous for X-linked — and only when `hmz_eligible` holds. Example:
three homozygous occurrences for an AR MDE → `POP_HMZ_-1.0` (1st free; 2nd and
3rd −0.5 each). This is distinct from `CLN_UAF`, which requires explicit
clinical details.

## See also

- [Core concepts](../../reference/concepts.md) — Cohort Allele Frequency and
  DAFT in more depth.
- [Capturing basic evidence](../../getting-started/capturing-basic-evidence.md)
  — a narrative walkthrough of `POP_FRQ` evidence.
- [ClinGen CSpec](../../reference/cspec-interop.md) — where the scoring
  methods/rules that consume this evidence are defined.
