# Population (POP)

**Population (POP)** is an Evidence Concept under
[Human Observational Data](index.md), covering population-level evidence about the
variant.

!!! note "Not yet modeled here"

    POP is specified by the SVCv4 Standards but is **not yet covered by this data
    model**. This page summarizes it; detailed modeling is a later phase.

| Code | Captures |
|---|---|
| `POP_FRQ` | Population (allele) frequency of the variant. |
| `POP_HMZ` | Population observations of homozygotes / hemizygotes. |

Scoring for these codes is defined in
[ClinGen CSpec](../../reference/cspec-interop.md).

## The shape of the remaining work

`POP_FRQ` compares the VBC's observed population frequency — a **Filtering
Allele Frequency (FAF)**, the population-max, lower-95%-CI-bound allele
frequency, typically sourced from gnomAD — against a **Disease Allele
Frequency Threshold (DAFT)**: an estimated ceiling for how common a truly
pathogenic variant for the specific MDE could plausibly be, given disease
prevalence, penetrance, and genetic/allelic heterogeneity. SVCv4 defines three
ways to derive a DAFT (a calculator method, a binning method for sparse-data
situations, and a pathogenic-variants method usable as a cross-check); this is
benignity-only evidence — a high FAF relative to DAFT argues against
pathogenicity, but a low FAF earns no positive points on its own. `POP_HMZ`
similarly weighs population-database observations of homozygotes/hemizygotes
against the disease's expected inheritance pattern; its detailed source
material hasn't been read into this project yet (see
[Known gaps](../../reference/known-gaps.md)).

The likely modeling approach: adopt the VA-Spec [Cohort Allele Frequency Study
Result](https://va-spec.ga4gh.org/en/1.0/va-standard-profiles/base-profiles/study-result-profiles.html#cohort-allele-frequency-study-result)
profile for the observed population-frequency data itself (VA-Spec is this
repo's primary dependency, so this is the natural, already-standardized
shape), plus new fields for the DAFT value and which derivation method
produced it. See [Core concepts](../../reference/concepts.md) for these two
concepts in more depth, and [Capturing basic evidence](../../getting-started/capturing-basic-evidence.md)
for a narrative walkthrough of what `POP_FRQ` evidence looks like today (this
model currently only carries the *result*, `pop_frq_points`, not the raw
evidence above).
