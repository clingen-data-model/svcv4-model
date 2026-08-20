# Spec coverage

This page tracks which parts of the SVCv4 Standards this data model currently
represents, and which are planned, so you can see exactly where we stand
relative to the Standards documents.

| # | Supplementary Material | Evidence code(s) | Model coverage |
|---|---|---|---|
| — | Main manuscript | hierarchy, 7-tier classification, applicability scope | Partial — hierarchy/tiers reflected in Overview; the applicability scope (rare variants, Mendelian MDEs only; excludes multi-gene CNVs, somatic cancer, most pharmacogenomics) isn't yet stated anywhere in these docs |
| 1 | [Glossary of Terms](https://docs.google.com/document/d/1CZBvar2it9Biq7tIf8UPa7caQV6Luo8eTScQD1ar5XM/edit) | — | Partial — see [Glossary](glossary.md) |
| 2 | [SVCv3 codes → v4 status](https://docs.google.com/document/d/1arjMP34ylJY7xoaT2Hblqhzmnr7iBlLXlxgJgh2-URY/edit) | — | Not modeled (historical mapping; informational only, low priority) |
| 3 | [Population Database Frequency](https://docs.google.com/document/d/1XON2eq4HSM-guWlqitEnb8PghY0quNbA7_1WmmxvLj8/edit) | `POP_FRQ`, `POP_HMZ` | **Modeled (inputs)** — `PopulationEvidence` captures FAF, DAFT + derivation method, and homozygote/hemizygote occurrences; scoring is documented, not computed. See [Population (POP)](../workflows/hod/pop.md) and the Cohort Allele Frequency / DAFT entries in [Core concepts](concepts.md) |
| 4 | [Clinical Observations](https://docs.google.com/document/d/17XnPmgTpzgQ8hfzOZNCcXIBwnNwbVkP0KIv3Dw5Bz_M/edit) | `CLN_CCS`/`CLN_AFF`/`CLN_DNV`/`CLN_ALT`/`CLN_UAF` | **Modeled** for AFF/DNV/ALT/UAF via the Case model — see [Clinical Observations (CLN)](../workflows/hod/cln/index.md), including the two remaining `CLN_AFF` completeness factors now captured (the gnomAD co-occurrence-likelihood bucket and the non-genetic-etiology flag). `CLN_CCS` (case-control studies) is **now captured** as `CaseControlStudyEvidence` (OR, CI bounds, case/control cohort sizes, case-variant count, robustness flags); its scoring (OR > 5.0 → +4.0; CI including 1.0 → no points) and the exclusivity rule (other CLN codes NA except `CLN_DNV`) are documented, not computed (see the note on the CLN page) |
| 5 | [Specific Phenotype and Segregation](https://docs.google.com/document/d/15arEcguLCzjiKKjibE3U0SNdrUjbKjpPoDoBPi2o40Y/edit) | `LOC_PHE`, `LOC_SEG` | **Modeled** — see [Locus Specificity (LOC)](../workflows/hod/loc/index.md) |
| 6 | [Missense Variants](https://docs.google.com/document/d/1eerqnL0kRq1se341-pxHxNI7HrPP9_kDlLL4eDvt-Gk/edit) | `MIS_*`, `SPL_*` (missense path) | **Modeled (inputs)** — the full Missense workflow: the amino-acid (`MIS_`) path (`MissenseAminoAcidAssessment`), the splice (`SPL_`) paths (`MissenseSpliceAssessment`, five prediction outcomes reusing SM 18/19/20), and the `MIS_`-vs-`SPL_` comparison (`MissenseAssessment`). Only the SM 7 motif-variant special case remains. See [Missense](../workflows/pfd/missense.md) |
| 7 | [Determining Critical Amino Acids](https://docs.google.com/document/d/1a64UTev9P35YGStF7YjaprB8znWS5OC5qbBZBMMLA_s/edit) | (shared sub-module) | Not yet modeled |
| 8 | [Nonsense Variants](https://docs.google.com/document/d/1LFqIBpmw_plE8CFmRLbS2aeUYMibpVpxDjkbzJPHQsA/edit) | `NUL_*`, `CDS_*` | **Modeled (inputs)** — `NonsenseAssessment` captures the three branches (NMD+no-rescue → `NUL_`; NMD+rescue → `CDS_`; no-NMD → `CDS_`), reusing SM 18/19/20; the criticality axis (SM 7) is deferred. See [Nonsense](../workflows/pfd/nonsense.md) |
| 9 | [Frameshift Variants](https://docs.google.com/document/d/1s-0OfNWc5h3pHiJFsFjmrdoEmitbJfXzkA29WQisaXo/edit) | `NUL_*`, `CDS_*` | **Modeled (inputs)** — `FrameshiftAssessment` captures the five branches (NMD+no-rescue → `NUL_`; NMD+rescue → `CDS_`; no-NMD → `CDS_`; non-stop decay → `NUL_`; protein extension → `CDS_`), reusing SM 18/19/20; the criticality axis (SM 7) is deferred. See [Frameshift](../workflows/pfd/frameshift.md) |
| 10 | [In-Frame InDel Variants](https://docs.google.com/document/d/1278qhDIDX94nlTUzwl7oIgZDLPc8YgEoFSVHXTHgRKk/edit) | `CDS_*` (assumed) | Not yet modeled |
| 11 | [Canonical Splice Variants](https://docs.google.com/document/d/1LGSPW90-n0EbqGjfLKQ2MpTHPK8Ai-hUuMAkqqhyi80/edit) | `SPL_*` | Not yet modeled |
| 12 | [Intronic & Synonymous Variants](https://docs.google.com/document/d/1mqZnp72N3IC3adenRrVVufOuqkgPAgkD_D5vNmb32gc/edit) | `SPL_*`/`NCG_*` (assumed) | Not yet modeled |
| 13 | [Exon Deletion Variants](https://docs.google.com/document/d/1354VHASLCzQ-73Ha1-TdVL5t7RsVzq-Hgl1tqmuLQlk/edit) | `NUL_*`, `CDS_*` | Not yet modeled |
| 14 | [Exon Dup/Insertion Variants](https://docs.google.com/document/d/1yMgN3Y54V3fnaV_4zjVas1aoOtwfNNyL7hziZA3EdvQ/edit) | `NUL_*`, `CDS_*` (assumed) | Not yet modeled |
| 15 | [Start Loss Variants](https://docs.google.com/document/d/1mn-IsUQSzV5traLH5G8KDa3DE1Q3OueTPfsDV9qBRvA/edit) | `NUL_*`, `CDS_*` | Not yet modeled |
| 16 | [Stop Loss Variants](https://docs.google.com/document/d/1OqEbx2FtQ2mL-7y3n6mpmQwCWuFIysFT_Vyo5lw3kWA/edit) | `NUL_*`, `CDS_*` | Not yet modeled |
| 17 | Non-Coding Variants | TBD | Not yet modeled — not yet released by the Working Group; the SVCv4 manuscript flags this section as an unwritten placeholder, i.e. this is currently a Working Group gap, not (yet) a modeling-project gap |
| 18 | [Molecular Mechanism and Exon Relevance](https://docs.google.com/document/d/1BLnsgxLY0TibwylFWz0SeGGeCusWwSokrgU4qsmBiaw/edit) | (shared sub-module) | **Modeled (inputs)** — `MechanismExonRelevanceEvidence` captures the mechanism level + exon-relevance category + MANE status + two override flags; the multiplier is documented, not computed, and is gated on the `WorkflowParameters.gene_disease_validity` (Moderate+) field. See [Predictive & Functional Data](../workflows/pfd/index.md) |
| 19 | [Informative Variants](https://docs.google.com/document/d/1hNfdtdvDT4dob9oDBrL_UzVV_MYiWnwERfli76EAbyQ/edit) | (shared sub-module) | **Modeled (inputs)** — `InformativeVariantsEvidence` captures the distinct informative variants (classification, similarity basis, eligibility flags); the scoring is documented, not computed. See [Predictive & Functional Data](../workflows/pfd/index.md) |
| 20 | [Functional Assays](https://docs.google.com/document/d/1X68otBl4YvdXlP1bOD83JO4kIod0Ol5BoLB4CLxqijA/edit) | (shared sub-module) | **Modeled (inputs)** — `FunctionalAssayEvidence` captures protein/cellular assays (OddsPath, pathogenic + benign controls) and animal-model evidence; the scoring is documented, not computed. See [Predictive & Functional Data](../workflows/pfd/index.md) |
| 21 | [Multiple Disorders Guidance](https://docs.google.com/document/d/1_qkcglOow-l6hLKNH2QipxAJDOn3XZEmoC8Koq9EB6o/edit) | — (design constraint) | Partial — informs the `Mde`/`Gene` model's gene↔MDE-is-not-1:1 design (see [Core concepts](concepts.md)); not itself a discrete workflow page |

!!! note "Rows 6–20 share one pipeline"

    Rows 6–20 are the Predictive & Functional Data (PFD) supplements. They all
    follow the same shared pipeline pattern — predict → adjust for molecular
    mechanism / exon relevance → functional evidence → informative variants →
    capped code total — described once on
    [Predictive & Functional Data](../workflows/pfd/index.md) rather than
    repeated per row here.
