# V24: MECP2 — source capture

Verbatim transcription of the **v24-mecp2** tab of the Practice Variant Set
spreadsheet. Nothing here is interpreted; interpretation lives in a `mapping.md`
(added when the entry is encoded).

- Source tab: [v24-mecp2 ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1165317085#gid=1165317085)
- PVS id: `PVS-V24-MECP2`


## Variant Data
- **Gene:** MECP2   MECP2 has MANE Select and MANE Plus Clinical and this variant is present in both - either can be selected for curation
- **Variant:** NM_001110792.2:c.907_1080del
- NP_001104262.1:p.Ser303_Glu360del
- **CAID:** CA274615
- **gnomAD:** absent

## Disease Data
- Rett syndrome
- MONDO:0010726
- LoF is an established mechanism of disease for MECP2-related Rett Syndrome
- MOI: X-linked

## Pop Frequency Data
- The "Disease Allele Frequency Threshold - Binning Approach" can be used for this variant - click "Use Binning Approach" in the "Workflow for Population Frequency" section
- Using table "X-LINKED DOMINANT - COMBINED (combined male and female prevalence)", you can assume 1/10,000 prevalence and 80% penetrance

## Variant Impact Data
- This variant is an in-frame deletion of 58 amino acids in a non-repeat region within the last exon MECP2; removing ~11% of the protein
- The Transcriptional Repression Domain (TRD) occurs from residues 285-313; with the Rett-Angelman VCEP specifically calling out NM_004992 residues 302-306 (or NM_001110792 residues 314-318) as the critical minimal region and note that loss of this region can result in Rett syndrome
- This variant and region is present in both MANE Select and MANE Plus Clinical
- There are two Pathogenic deletion variants in ClinVar that are completely contained with the VBC - NM_001110792.2:c.907_1080del
- NM_001110792.2(MECP2):c.954_962del (p.Lys319_Arg321del)
- NM_001110792.2(MECP2):c.933_968del (p.Leu313_Val324del)

## Clinical Data
- **Case1: Variant identified via whole exome sequencing in the heterozygous state in an affected female with features of seizures, left hemisphere atrophy on brain MRI, intellectual disability, dysmorphic features:**    Please note - For genes on the X chromosome, our recommendations for counting probands using the CLN_AFF_ tables depend on the inheritance pattern of the Monogenic Disease Entity (MDE). For MDEs presenting with an X-linked dominant pattern, both affected XY and XX individuals should be counted under the Monoallelic Disorder section

Given partial overlap for the first case and limited details provided for the second, erroring on the cautious side both could be scored under "Phenotype CONSISTENT with gene AND all relevant genes for disorder tested AND no other variant of interest"
- Case2: Variant identified via whole exome sequencing in the heterozygous state in an affected female noted to have atypical Rett syndrome - no additional features provided
