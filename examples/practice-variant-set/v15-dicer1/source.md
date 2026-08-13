# V15: DICER1 — source capture

Verbatim transcription of the **v15-dicer1** tab of the Practice Variant Set
spreadsheet. Nothing here is interpreted; interpretation lives in a `mapping.md`
(added when the entry is encoded).

- Source tab: [v15-dicer1 ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1839319038#gid=1839319038)
- PVS id: `PVS-V15-DICER1`


## Variant Data
- **Gene:** DICER1
- **Variant:** NM_177438.3:c.2T>C
- NP_803187.1:p.Met1Thr
- **CAID:** CA10583232
- **gnomAD:** https://gnomad.broadinstitute.org/variant/chr14-95133457-A-G?dataset=gnomad_r4

## Disease Data
- DICER1-related tumor predisposition
- MONDO:0100216
- LoF is an established mechanism of disease for DICER1-related tumor predisposition
- MOI: Autosomal Dominant

## Pop Frequency Data
- https://www.cardiodb.org/allelefrequencyapp/
- **Prevalence Estimate:** 1 in 800
- **Allelic Heterogeneity:** 0.07
- **Genetic (Locus) Heterogeneity:** 1.00
- **Penetrance:** 0.10

## Variant Impact Data
- Variant occurs in a Met1 start loss (Met1 at far right in screenshot above - gene on antisense); exon is present in all clinically relevant transcripts
- p.M1 is not highly conserved and there are three in-frame possible alternate start codons in the first coding exon (p.Met11, p.Met17, p.Met24)
- There are two ClinVar P/LP LoF variants between Met1 and Met11 (above) however it is unknown if these were classified as P/LP simply based on the LoF prediction and if alternative Met usage was considered
- Otherwise there no P/LP variants between Met1 and furthest potential downstream Met24
- This region is not known to encode a critical domain and loss of first 24AAs would only remove ~1.2% of the gene
- There are no other P/LP changes in Met1 observed in ClinVar

## Clinical Data
- **Proband Data:**  Additional Notes for Curation
- **Proband 1: Variant identified in individual with family history of nonspecific cancer:**  Case would not count towards CLN_AFF since unaffected.

Additionally, individual would not contribute to CLN_UAF as penetrance for DICER1-related tumor predisposition is low
- **Proband 2: Variant identified in 40y Female with breast cancer; individual also carried Pathogenic BRCA1 variant:**  Case would not count towards CLN_AFF as breast cancer is not specific for DICER1 and there is an alternative variant that could account for the phenotype in this proband.

Additionally, this case would not contribute towards CLN_ALT (gene) as breast cancer has high genetic heterogeneity and an individual could have two genetic causes without presenting with a more severe phenotype.
