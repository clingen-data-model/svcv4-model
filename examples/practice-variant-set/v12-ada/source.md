# V12: ADA — source capture

Verbatim transcription of the **v12-ada** tab of the Practice Variant Set
spreadsheet. Nothing here is interpreted; interpretation lives in a `mapping.md`
(added when the entry is encoded).

- Source tab: [v12-ada ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=125729140#gid=125729140)
- PVS id: `PVS-V12-ADA`


## Variant Data
- **Gene:** ADA
- **Variant:** NM_000022.4:c.219-2A>G
- **CAID:** CA252010
- **gnomAD:** https://gnomad.broadinstitute.org/variant/chr20-44626601-T-C?dataset=gnomad_r4

## Disease Data
- severe combined immunodeficiency, autosomal recessive, T cell-negative, B cell-negative, NK cell-negative, due to adenosine deaminase deficiency
- MONDO:0007064
- LoF is an established mechanism of disease for severe combined immunodeficiency, autosomal recessive, T cell-negative, B cell-negative, NK cell-negative, due to adenosine deaminase deficiency
- MOI: Autosomal Recessive

## Pop Frequency Data
- https://www.cardiodb.org/allelefrequencyapp/
- **Prevalence Estimate:** 1 in 5000 (Remember to use AR)
- **Allelic Heterogeneity:** 0.20
- **Genetic (Locus) Heterogeneity:** 0.13
- **Penetrance:** 0.50

## Variant Impact Data
- Exon present in clinically relevant transcripts
- SpliceAI predictions
- The NM_000022.4:c.219-2A>G variant in ADA occurs within the canonical splice acceptor site (-2) of intron 3. It is predicted to cause skipping of biologically relevant exon 4, resulting in an in-frame deletion (removes amino acids 74-121). The variant removes >10% of the protein (48/363 amino acids). Prior studies have shown that deletion of 4 results in decrease in ADA enzymatic activity. and the truncated region is critical to protein function (PMID 3182793).

With this data, curators can select "Removes/alters >50% of protein OR Removes/alters entire critical functional domain that has been experimentally implicated in the Molecular Mechanism"
- Informative Variants
There is another LP variant at this splice site (c.219-1G>A), but since no details are provided such as clinical data or explanation for the LP classification, out of caution no informative variant should be given for the 219-1G>A variant.
- Splicing assay data
Follow up RT-PCR studies in the proband confirmed that exon 4 was skipped as a result of this variant.
For canonical splice site variants, the PRD weight is the same weight as other LoF types of the same impact (for example for ADA, the PRD weight for a deletion of exon 4 is the same weight as PRD for a canonical splice site that results in skipping of exon 4).
Because of the high weight for canonical splice sites, splicing data does not add points (as then this exon 4 skipping event would be "more Pathogenic" than an actual deletion of exon 4) however incomplete splicing from a splicing assay would deduct points. (Comparatively, splicing assay data for non-canonical AG,GT variants does add weight - for example see LDLR variant in this pilot set).
Since the RT-PCR data confirmed the prediction of exon 4 splicing, curators can select "Splicing data and PRD are concordant with regards to impact" and "Proportion of Alternative Transcripts (Inferred to Be) Produced by VBC is near to complete" - which does not add or subtract points from the SPL_PRD score

## Clinical Data
- **Case Data:**   Curation Notes
- **Variant detected in 1 proband with severe combined immunodeficiency disorder with T-B-NK- lymphocyte subset profile. Case tested on large SCID panel

Variant identified in the homozygous state in this proband:**   Given the T-B-NK- lymphocyte subset profile, proband can be counted under "Phenotype SPECIFIC for gene AND all relevant genes for disorder tested AND with no other variant of interest"
While ADA-SCID is eligible for LOC_PHE points when additional phenotypic details for a proband are provided (see VCEP specifications for PP4: https://cspec.genome.network/cspec/ui/svi/doc/GN114?version=1.0.0), since only T-B-NK- lymphocyte subset profile was provided for the single proband, no LOC_PHE points should be awarded
