# V17: LDLR — source capture

Verbatim transcription of the **v17-ldlr** tab of the Practice Variant Set
spreadsheet. Nothing here is interpreted; interpretation lives in a `mapping.md`
(added when the entry is encoded).

- Source tab: [v17-ldlr ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1874520311#gid=1874520311)
- PVS id: `PVS-V17-LDLR`


## Variant Data
- **Gene:** LDLR
- **Variant:** NM_000527.5:c.1216C>A
- NP_000518.1:p.Arg406=
- **CAID:** CA023436
- **gnomAD:** https://gnomad.broadinstitute.org/variant/chr19-11113307-C-A?dataset=gnomad_r4

## Disease Data
- familial hypercholesterolemia
- MONDO:0005439
- LoF is an established mechanism of disease for familial hypercholesterolemia
- MOI: Semidominant

## Pop Frequency Data
- https://www.cardiodb.org/allelefrequencyapp/
- **Prevalence Estimate:** 1 in 200
- **Allelic Heterogeneity:** 0.05
- **Genetic (Locus) Heterogeneity:** 0.80
- **Penetrance:** 0.8

## Variant Impact Data
- Variant is predicted to impact splicing
- These data suggest that the natural acceptor at the beginning of exon 9 will not be used (REF score 1.0 - ALT score 0.57) and instead a new acceptor in exon 9 will be used instead (REF score 0.00 - ALT score 1.00), removing the first 31nt of exon 9 (predicted r.1189_1219del - p.(Ser397ThrfsTer6)

## Splicing Data
- Both minigene and RT-PCR (PMID:19371225; PMID:17335829) have shown that this variant results in an acceptor gain r.1189_1219del - p.(Ser397ThrfsTer6)
- Curators can follow workflow for "Splicing data and PRD are concordant with regards to impact"
- Followed by "Proportion of Alternative Transcripts (Inferred to Be) Produced by VBC is near to complete"
- Informative Variants
- There are P/LP variants in this codon
- However all have high missense prediction scores
- All are thought to disrupt LDLR function via the missense variant and not via splicing

## Clinical Data
- **Proband Data:**  Additional Notes for Curation
- **Proband 1: Variant identified in proband who met clinical diagnostic criteria for FH; proband testing on FH panel and no other variants identified in other FH genes including LDLR:**  Case can be counted in Autosomal Dominant CLN_AFF, using "Phenotype SPECIFIC for gene AND all relevant genes for disorder tested AND with no other variant of interest"
- **Proband 2: Variant identified in proband who met clinical diagnostic criteria for FH; proband testing on FH panel and no other variants identified in other FH genes including LDLR:**  Case can be counted in Autosomal Dominant CLN_AFF, using "Phenotype SPECIFIC for gene AND all relevant genes for disorder tested AND with no other variant of interest"
- **Proband 3: Variant identified in proband who met clinical diagnostic criteria for homozygous/AR FH with LDLc: 704 mg/dl; proband also has NM_000527.5(LDLR):c.760C>T (p.Gln254Ter) variant confirmed in trans (variant classified as Path by VCEP):**  Using Autosomal Recessive CLN_AFF, case can be counted in "Phenotype SPECIFIC for gene AND all relevant genes for disorder tested AND with no other variant of interest"

**Additionally, case can be given weight using LOC_PHE. Diagnostic yield for biallelic FH phenotype for LDLR testing is estimated to be ~60% (PMID: 40908092)
