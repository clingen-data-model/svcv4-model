# Examples — the Practice Variant Set

The examples on this site **are** the **Practice Variant Set (PVS)**: the
real-world variants curated for the **three pilots** held to test, validate, and
improve the SVCv4 specification. Between them they cover most of the SVCv4
workflows and use cases, so they double as the on-ramp for new users getting a
feel for real data — no separate or synthetic example set is needed.

Each variant is one tab of the source spreadsheet, transcribed and mapped onto the
[Case model](../../workflows/case-model.md) and the
[classification structures](../../getting-started/evidence-lines-and-items.md),
and given a stable `PVS-*` id that preserves the tab name. Everything stays
**traceable** rather than invented:

**this catalog → a worked-example page → the encoded fixtures → the source tab.**

Each encoded entry has a worked-example page that shows the classification four
ways — as **prose**, a curator's **narrative**, a **semi-structured** outline, and
downloadable **JSON**. Fixtures are validated in CI:

```sh
uv run python scripts/validate_examples.py
```

!!! note "Placeholder content"

    The **shapes are real; the data is illustrative.** Scores and classifications
    shown here are not spec-locked — the scoring arithmetic lives in
    [ClinGen CSpec](../../reference/cspec-interop.md), not in this model.

## Entries

**All 32 of 32 entries are encoded** — each with validated `case-*.json` and/or `classification.json` and a linked worked-example page. The
`case-*.json` fixtures also feed the
[per-workflow examples](../../workflows/case-model.md) on the Workflows page.

| PVS id | Variant | Condition | Workflows encoded | Status |
|---|---|---|---|---|
| [`PVS-v1-ACTC1`](v1-actc1.md) | ACTC1 `c.488dup` | Hypertrophic Cardiomyopathy (HCM) (MONDO:0005045) | CLN_UAF · LOC_PHE | Encoded + page |
| [`PVS-v2-ATM`](v2-atm.md) | ATM `c.5005+1G>A` | ataxia telangiectasia (MONDO:0008840) | CLN_AFF | Encoded + page |
| [`PVS-v3-FOXG1`](v3-foxg1.md) | FOXG1 `c.234_236delGCC` | FOXG1-related disorder (MONDO:0100040) | CLN_AFF | Encoded + page |
| [`PVS-v4-HNF4A`](v4-hnf4a.md) | HNF4A `c.421del` | monogenic diabetes (MONDO:0015967) | CLN_AFF | Encoded + page |
| [`PVS-v5-MYH7`](v5-myh7.md) | MYH7 `c.4909G>A` | hypertropic cardiomyopathy (MONDO:0005045) | CLN_AFF | Encoded + page |
| [`PVS-v6-NF1`](v6-nf1.md) | NF1 `c.3496G>C` | neurofibromatosis type 1 (MONDO:0018975) | CLN_AFF | Encoded + page |
| [`PVS-v7-PAH`](v7-pah.md) | PAH `c.865G>A` | phenylketonuria (MONDO:0009861) | CLN_AFF | Encoded + page |
| [`PVS-PKP2`](pkp2.md) | PKP2 `c.1379-2006C>A` | arrhythmogenic right ventricular cardiomyopathy (MONDO:0016587) | — (classification only) | Encoded + page |
| [`PVS-v8-TRDN`](v8-trdn.md) | TRDN `c.1462A>T` | catecholaminergic polymorphic ventricular tachycardia (MONDO:0017990) | CLN_UAF | Encoded + page |
| [`PVS-v9-RUNX1`](v9-runx1.md) | RUNX1 `c.1412_1413dup` | Hereditary thrombocytopenia and hematologic cancer predisposition syndrome (MONDO:0011071) | LOC_SEG | Encoded + page |
| [`PVS-v10-SCN2A`](v10-scn2a.md) | SCN2A `c.1108T>C` | complex neurodevelopmental disorder (MONDO:0100038) | CLN_DNV | Encoded + page |
| [`PVS-v11-ACVRL1`](v11-acvrl1.md) | ACVRL1 `c.88C>T` | hereditary hemorrhagic telangiectasia (MONDO:0019180) | CLN_ALTG · CLN_ALTV | Encoded + page |
| [`PVS-v12-ADA`](v12-ada.md) | ADA `c.219-2A>G` | severe combined immunodeficiency, autosomal recessive, T cell-negative, B cell-negative, NK cell-negative, due to adenosine deaminase deficiency (MONDO:0007064) | CLN_AFF | Encoded + page |
| [`PVS-v13-AIPL1`](v13-aipl1.md) | AIPL1 `c.150C>T` | AIPL1-related retinopathy (MONDO:0100438) | — (classification only) | Encoded + page |
| [`PVS-v14-ATXN7L3`](v14-atxn7l3.md) | ATXN7L3 `c.332del` | ATXN7L3-related developmental delay, hypotonia and facial dysmorphism (MONDO:0100038) | CLN_AFF | Encoded + page |
| [`PVS-v15-DICER1`](v15-dicer1.md) | DICER1 `c.2T>C` | DICER1-related tumor predisposition (MONDO:0100216) | — (classification only) | Encoded + page |
| [`PVS-v16-DYSF`](v16-dysf.md) | DYSF `c.5626G>A` | autosomal recessive limb-girdle muscular dystrophy (MONDO:0015152) | CLN_AFF | Encoded + page |
| [`PVS-v17-LDLR`](v17-ldlr.md) | LDLR `c.1216C>A` | familial hypercholesterolemia (MONDO:0005439) | CLN_AFF | Encoded + page |
| [`PVS-v18-TNNI3`](v18-tnni3.md) | TNNI3 `c.236G>T` | hypertrophic cardiomyopathy (MONDO:0005045) | — (classification only) | Encoded + page |
| [`PVS-v19-TP53`](v19-tp53.md) | TP53 `c.641A>T` | Li-Fraumeni syndrome (MONDO:0018875) | — (classification only) | Encoded + page |
| [`PVS-v20-USH2A`](v20-ush2a.md) | USH2A `c.12295-?_14133+?del` | Usher syndrome (MONDO:0019501) | CLN_AFF | Encoded + page |
| [`PVS-v21-ANO5`](v21-ano5.md) | ANO5 `c.139-1del` | autosomal recessive limb-girdle muscular dystrophy (MONDO:0015152) | — (classification only) | Encoded + page |
| [`PVS-v22-F8`](v22-f8.md) | F8 `c.1420G>C` | hemophilia A (MONDO:0010602) | — (classification only) | Encoded + page |
| [`PVS-v23-GP1BA`](v23-gp1ba.md) | GP1BA `c.334G>A` | Bernard-Soulier syndrome (MONDO:0009276) | — (classification only) | Encoded + page |
| [`PVS-v24-MECP2`](v24-mecp2.md) | MECP2 `c.907_1080del` | Rett syndrome (MONDO:0010726) | CLN_AFF | Encoded + page |
| [`PVS-v25-MSH2`](v25-msh2.md) | MSH2 `c.630G>A` | Lynch syndrome/familial non-polyposis colon cancer (MONDO:0005835) | — (classification only) | Encoded + page |
| [`PVS-v26-MSH6`](v26-msh6.md) | MSH6 `c.107C>T` | Lynch syndrome/familial non-polyposis colon cancer (MONDO:0005835) | CLN_ALTV | Encoded + page |
| [`PVS-v27-MYOC`](v27-myoc.md) | MYOC `c.719A>G` | open-angle glaucoma (MONDO:0005338) | — (classification only) | Encoded + page |
| [`PVS-v28-PTEN`](v28-pten.md) | PTEN `c.802-3T>A` | PTEN hamartoma tumor syndrome (MONDO:0017623) | — (classification only) | Encoded + page |
| [`PVS-v29-RS1`](v29-rs1.md) | RS1 `c.53-713_78+266del` | X-linked retinoschisis (MONDO:0010725) | CLN_AFF | Encoded + page |
| [`PVS-v30-RYR1`](v30-ryr1.md) | RYR1 `c.12383C>T` | malignant hyperthermia, susceptibility to, 1 (MONDO:0007783) | CLN_AFF | Encoded + page |
| [`PVS-EXAMPLE-FBN1`](example-fbn1.md) | FBN1 `c.7003C>T` | Marfan syndrome (MONDO:0007947) | CLN_AFF | Encoded + page |

## How each entry is built

Every entry is produced by the same repeatable pass:

1. **Capture** — transcribe the tab verbatim (`source.md`).
2. **Map** — record where each source value lands in the model (`mapping.md`).
3. **Encode** — emit validated instances: a per-workflow `case-<WORKFLOW>.json`
   submission and a rolled-up `classification.json` `Statement`.
4. **Author** — a worked-example page (like [MYH7](v5-myh7.md)) that cites the
   PVS id and links back to the tab.

The encoded fixtures and the capture/mapping notes live in the repository under
[`examples/practice-variant-set/`][pvs-repo]. They are
validated in CI by `scripts/validate_examples.py`.

Source spreadsheet: **Practice Variant Set** — one example per tab.

[pvs-repo]: https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set
