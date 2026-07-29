# Spec coverage

This page tracks which parts of the SVCv4 Standards this data model currently
represents, and which are planned, so you can see exactly where we stand
relative to the Standards documents.

| # | Supplementary Material | Evidence code(s) | Model coverage |
|---|---|---|---|
| — | Main manuscript | hierarchy, 7-tier classification, applicability scope | Partial — hierarchy/tiers reflected in Overview; the applicability scope (rare variants, Mendelian MDEs only; excludes multi-gene CNVs, somatic cancer, most pharmacogenomics) isn't yet stated anywhere in these docs |
| 1 | Glossary of Terms | — | Partial — see [Glossary](glossary.md) |
| 2 | SVCv3 codes → v4 status | — | Not modeled (historical mapping; informational only, low priority) |
| 3 | Population Database Frequency | `POP_FRQ`, `POP_HMZ` | Not yet modeled — see [Population (POP)](../workflows/hod/pop.md). Introduces the Cohort Allele Frequency and Disease Allele Frequency Threshold concepts — see [Core concepts](concepts.md) |
| 4 | Clinical Observations | `CLN_CCS`/`CLN_AFF`/`CLN_DNV`/`CLN_ALT`/`CLN_UAF` | **Modeled** for AFF/DNV/ALT/UAF via the Case model — see [Clinical Observations (CLN)](../workflows/hod/cln/index.md). `CLN_CCS` is a special case: SVCv4 provides scoring guidance for it but not decomposed evidence concepts, so it's out of scope for this Classification Model until a future SVCv4 version adds those (see the note on the CLN page) — not a simple backlog item |
| 5 | Specific Phenotype and Segregation | `LOC_PHE`, `LOC_SEG` | **Modeled** — see [Locus Specificity (LOC)](../workflows/hod/loc/index.md) |
| 6 | Missense Variants | `MIS_*`, `SPL_*` (missense path) | Not yet modeled — see [Predictive & Functional Data](../workflows/pfd/index.md) |
| 7 | Determining Critical Amino Acids | (shared sub-module) | Not yet modeled |
| 8 | Nonsense Variants | `NUL_*`, `CDS_*` | Not yet modeled |
| 9 | Frameshift Variants | `NUL_*`, `CDS_*` | Not yet modeled |
| 10 | In-Frame InDel Variants | `CDS_*` (assumed) | Not yet modeled |
| 11 | Canonical Splice Variants | `SPL_*` | Not yet modeled |
| 12 | Intronic & Synonymous Variants | `SPL_*`/`NCG_*` (assumed) | Not yet modeled |
| 13 | Exon Deletion Variants | `NUL_*`, `CDS_*` | Not yet modeled |
| 14 | Exon Dup/Insertion Variants | `NUL_*`, `CDS_*` (assumed) | Not yet modeled |
| 15 | Start Loss Variants | `NUL_*`, `CDS_*` | Not yet modeled |
| 16 | Stop Loss Variants | `NUL_*`, `CDS_*` | Not yet modeled |
| 17 | Non-Coding Variants | TBD | Not yet modeled — the SVCv4 manuscript itself flags this section as an unwritten placeholder, i.e. this is currently a Working Group gap, not (yet) a modeling-project gap |
| 18 | Molecular Mechanism and Exon Relevance | (shared sub-module) | Not yet modeled |
| 19 | Informative Variants | (shared sub-module) | Not yet modeled |
| 20 | Functional Assays | (shared sub-module) | Not yet modeled |
| 21 | Multiple Disorders Guidance | — (design constraint) | Partial — informs the `Mde`/`Gene` model's gene↔MDE-is-not-1:1 design (see [Core concepts](concepts.md)); not itself a discrete workflow page |

!!! note "Rows 6–20 share one pipeline"

    Rows 6–20 are the Predictive & Functional Data (PFD) supplements. They all
    follow the same shared pipeline pattern — predict → adjust for molecular
    mechanism / exon relevance → functional evidence → informative variants →
    capped code total — described once on
    [Predictive & Functional Data](../workflows/pfd/index.md) rather than
    repeated per row here.
