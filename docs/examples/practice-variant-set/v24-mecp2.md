# MECP2 c.907_1080del (p.Ser303_Glu360del) — Rett syndrome

!!! info "Practice Variant Set · `PVS-v24-MECP2`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1165317085#gid=1165317085) · **Repo entry:** [`examples/practice-variant-set/v24-mecp2/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v24-mecp2) ·
    **Exercises:** POP_FRQ · CLN_AFF · CDS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in CSpec.

An SVCv4 classification of MECP2 c.907_1080del (p.Ser303_Glu360del) against Rett syndrome, drawn from the
`PVS-v24-MECP2` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    MECP2 c.907_1080del (p.Ser303_Glu360del) is assessed for whether it **is causal for** Rett syndrome (`MONDO:0010726`), under XLD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), rna / coding alteration — compose to an illustrative **likely pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is MECP2 c.907_1080del (p.Ser303_Glu360del); the disease/condition (MDE) is Rett syndrome. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF`, score 2.0) — Affected XX probands (illustrative).
    - **RNA / coding alteration (CDS)** (`CDS`, score 4.0) — Coding-alteration / critical-domain evidence (PFD, illustrative).
      - `CDS_PRD` (score 4.0) — Structural coding-sequence assessment.

    Each became an Evidence Line; their scores compose to a Statement final score of 6.0 → *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subject (VBC): MECP2 c.907_1080del (p.Ser303_Glu360del)
        predicate:     is_causal_for
        object (MDE):  MONDO:0010726 (Rett syndrome)
        qualifiers:    moi=XLD; note=X-linked; affected XX and XY count under the monoallelic section. Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ                  score   0.0
        - CLN_AFF                  score   2.0
        - CDS                      score   4.0
          - CDS_PRD                  score   4.0
      score:         6.0
      outcome:       likely_pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v24-mecp2/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v24-mecp2/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA274615",
    "gene": { "symbol": "MECP2", "id": "HGNC:6990", "mde_associated_gene": "MECP2", "transcript": "NM_001110792.2" }
  },
  "mde": { "curie": "MONDO:0010726", "label": "Rett syndrome" },
  "moi": "XLD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v24-MECP2-case-1",
    "family_id": "PVS-v24-MECP2-FAM-1",
    "sex": "F",
    "phenotypes": [
      { "name": "Seizure", "code": "HP:0001250" },
      { "name": "Intellectual disability", "code": "HP:0001249" }
    ],
    "pheno_specificity_for_mde": "CONSISTENT",
    "testing": { "method": "Exome", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "PCT_80_100",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v24-mecp2/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v24-mecp2/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
