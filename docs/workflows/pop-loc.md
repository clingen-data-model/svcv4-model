# Population & Locus Specificity

Two more Evidence Concepts sit under
[Human Observational Data](human-observational-data.md) alongside Clinical
Observations. They are part of the SVCv4 Standards; this data model has
not modeled them in detail yet.

!!! note "Not yet modeled here"

    **Population (POP)** and **Locus Specificity (LOC)** are specified by the
    SVCv4 Standards but are **not yet covered by this data model**. This page
    summarizes them; detailed modeling is a later phase. (This is different from
    `CLN_CCS`, which the SVCv4 Working Group has not yet specified — see
    [Clinical Observations](clinical-observations.md).)

## Population (POP)

| Code | Captures |
|---|---|
| `POP_FRQ` | Population (allele) frequency of the variant. |
| `POP_HMZ` | Population observations of homozygotes / hemizygotes. |

## Locus Specificity (LOC)

| Code | Captures |
|---|---|
| `LOC_PHE` | Observation of a specific phenotype. |
| `LOC_SEG` | Segregation of the variant with disease (co-segregation). |

<!-- VERIFY: POP/LOC codes transcribed from the Human Observational Data Summary Table graphic; confirm with the SVCv4 WG. -->

Scoring for these codes is defined in
[ClinGen CSpec](../reference/cspec-interop.md).
