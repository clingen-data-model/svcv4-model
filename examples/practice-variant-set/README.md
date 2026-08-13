# Practice Variant Set

The **Practice Variant Set (PVS)** is a small, fixed set of real-world variant
examples used as the shared baseline for every worked example in this project.
Each entry is transcribed from one tab of the source spreadsheet, mapped onto
our Case and classification models, and given a stable `PVS-*` identifier.

Any example that appears in the docs site should trace back to a PVS entry, and
each PVS entry traces back to its source tab. That chain — docs → PVS entry →
spreadsheet — is what keeps the examples honest and reviewable.

Source spreadsheet: **Practice Variant Set**
(<https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit>).
One example per tab; the PVS id preserves the tab name so provenance is lossless.

## How an entry is built

Each entry is produced by one repeatable pass:

1. **Capture** — transcribe the tab verbatim into `source.md` (+ the tab link).
2. **Map** — record, field by field, where each source value lands in the
   model, in `mapping.md`.
3. **Encode** — emit validated model instances (per-workflow `case-*.json`
   payloads and a rolled-up `classification.json` `Statement`). *(Not yet done;
   the entries below are at the mapping stage.)*
4. **Author** — a docs example page that cites the PVS id.

As with everything here: the **shapes are real; the data is placeholder** until
the SVCv4 Standards and the GA4GH GKS VA-Spec SVCv4 community profile firm up.
Scores and classifications shown in mappings are illustrative — the underlying
Bayesian/points arithmetic belongs to the ClinGen CSpec (the Method model),
which is out of scope for this repository.

## Entries

| PVS id | Variant | Condition | Workflows encoded | Source tab | Stage |
|---|---|---|---|---|---|
| [`PVS-v1-ACTC1`](v1-actc1/) | ACTC1 `c.488dup` | Hypertrophic Cardiomyopathy (HCM) (MONDO:0005045) | CLN_UAF · LOC_PHE | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=0#gid=0) | Encoded + page |
| [`PVS-v2-ATM`](v2-atm/) | ATM `c.5005+1G>A` | ataxia telangiectasia (MONDO:0008840) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=174163698#gid=174163698) | Encoded + page |
| [`PVS-v3-FOXG1`](v3-foxg1/) | FOXG1 `c.234_236delGCC` | FOXG1-related disorder (MONDO:0100040) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=692785807#gid=692785807) | Encoded + page |
| [`PVS-v4-HNF4A`](v4-hnf4a/) | HNF4A `c.421del` | monogenic diabetes (MONDO:0015967) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=23733664#gid=23733664) | Encoded + page |
| [`PVS-v5-MYH7`](v5-myh7/) | MYH7 `c.4909G>A` | hypertropic cardiomyopathy (MONDO:0005045) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1923098172#gid=1923098172) | Encoded + page |
| [`PVS-v6-NF1`](v6-nf1/) | NF1 `c.3496G>C` | neurofibromatosis type 1 (MONDO:0018975) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1040336969#gid=1040336969) | Encoded + page |
| [`PVS-v7-PAH`](v7-pah/) | PAH `c.865G>A` | phenylketonuria (MONDO:0009861) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=2018479162#gid=2018479162) | Encoded + page |
| [`PVS-PKP2`](pkp2/) | PKP2 `c.1379-2006C>A` | arrhythmogenic right ventricular cardiomyopathy (MONDO:0016587) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1335968173#gid=1335968173) | Encoded + page |
| [`PVS-v8-TRDN`](v8-trdn/) | TRDN `c.1462A>T` | catecholaminergic polymorphic ventricular tachycardia (MONDO:0017990) | CLN_UAF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=345645658#gid=345645658) | Encoded + page |
| [`PVS-v9-RUNX1`](v9-runx1/) | RUNX1 `c.1412_1413dup` | Hereditary thrombocytopenia and hematologic cancer predisposition syndrome (MONDO:0011071) | LOC_SEG | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=866552192#gid=866552192) | Encoded + page |
| [`PVS-v10-SCN2A`](v10-scn2a/) | SCN2A `c.1108T>C` | complex neurodevelopmental disorder (MONDO:0100038) | CLN_DNV | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=130507855#gid=130507855) | Encoded + page |
| [`PVS-v11-ACVRL1`](v11-acvrl1/) | ACVRL1 `c.88C>T` | hereditary hemorrhagic telangiectasia (MONDO:0019180) | CLN_ALTG · CLN_ALTV | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1656716375#gid=1656716375) | Encoded + page |
| [`PVS-v12-ADA`](v12-ada/) | ADA `c.219-2A>G` | severe combined immunodeficiency, autosomal recessive, T cell-negative, B cell-negative, NK cell-negative, due to adenosine deaminase deficiency (MONDO:0007064) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=125729140#gid=125729140) | Encoded + page |
| [`PVS-v13-AIPL1`](v13-aipl1/) | AIPL1 `c.150C>T` | AIPL1-related retinopathy (MONDO:0100438) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=2040908414#gid=2040908414) | Encoded + page |
| [`PVS-v14-ATXN7L3`](v14-atxn7l3/) | ATXN7L3 `c.332del` | ATXN7L3-related developmental delay, hypotonia and facial dysmorphism (MONDO:0100038) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=306028402#gid=306028402) | Encoded + page |
| [`PVS-v15-DICER1`](v15-dicer1/) | DICER1 `c.2T>C` | DICER1-related tumor predisposition (MONDO:0100216) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1839319038#gid=1839319038) | Encoded + page |
| [`PVS-v16-DYSF`](v16-dysf/) | DYSF `c.5626G>A` | autosomal recessive limb-girdle muscular dystrophy (MONDO:0015152) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=678750638#gid=678750638) | Encoded + page |
| [`PVS-v17-LDLR`](v17-ldlr/) | LDLR `c.1216C>A` | familial hypercholesterolemia (MONDO:0005439) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1874520311#gid=1874520311) | Encoded + page |
| [`PVS-v18-TNNI3`](v18-tnni3/) | TNNI3 `c.236G>T` | hypertrophic cardiomyopathy (MONDO:0005045) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1710001749#gid=1710001749) | Encoded + page |
| [`PVS-v19-TP53`](v19-tp53/) | TP53 `c.641A>T` | Li-Fraumeni syndrome (MONDO:0018875) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=2047952345#gid=2047952345) | Encoded + page |
| [`PVS-v20-USH2A`](v20-ush2a/) | USH2A `c.12295-?_14133+?del` | Usher syndrome (MONDO:0019501) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=558949416#gid=558949416) | Encoded + page |
| [`PVS-v21-ANO5`](v21-ano5/) | ANO5 `c.139-1del` | autosomal recessive limb-girdle muscular dystrophy (MONDO:0015152) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=870504889#gid=870504889) | Encoded + page |
| [`PVS-v22-F8`](v22-f8/) | F8 `c.1420G>C` | hemophilia A (MONDO:0010602) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1776447041#gid=1776447041) | Encoded + page |
| [`PVS-v23-GP1BA`](v23-gp1ba/) | GP1BA `c.334G>A` | Bernard-Soulier syndrome (MONDO:0009276) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1698869350#gid=1698869350) | Encoded + page |
| [`PVS-v24-MECP2`](v24-mecp2/) | MECP2 `c.907_1080del` | Rett syndrome (MONDO:0010726) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1165317085#gid=1165317085) | Encoded + page |
| [`PVS-v25-MSH2`](v25-msh2/) | MSH2 `c.630G>A` | Lynch syndrome/familial non-polyposis colon cancer (MONDO:0005835) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=924699761#gid=924699761) | Encoded + page |
| [`PVS-v26-MSH6`](v26-msh6/) | MSH6 `c.107C>T` | Lynch syndrome/familial non-polyposis colon cancer (MONDO:0005835) | CLN_ALTV | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=65997805#gid=65997805) | Encoded + page |
| [`PVS-v27-MYOC`](v27-myoc/) | MYOC `c.719A>G` | open-angle glaucoma (MONDO:0005338) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=383577094#gid=383577094) | Encoded + page |
| [`PVS-v28-PTEN`](v28-pten/) | PTEN `c.802-3T>A` | PTEN hamartoma tumor syndrome (MONDO:0017623) | — (classification only) | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1850504083#gid=1850504083) | Encoded + page |
| [`PVS-v29-RS1`](v29-rs1/) | RS1 `c.53-713_78+266del` | X-linked retinoschisis (MONDO:0010725) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=616889408#gid=616889408) | Encoded + page |
| [`PVS-v30-RYR1`](v30-ryr1/) | RYR1 `c.12383C>T` | malignant hyperthermia, susceptibility to, 1 (MONDO:0007783) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1866712904#gid=1866712904) | Encoded + page |
| [`PVS-EXAMPLE-FBN1`](example-fbn1/) | FBN1 `c.7003C>T` | Marfan syndrome (MONDO:0007947) | CLN_AFF | [tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1792158038#gid=1792158038) | Encoded + page |
