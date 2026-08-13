# USH2A del exons 63-64 (c.12295-?_14133+?del) — Usher syndrome

!!! info "Practice Variant Set · `PVS-v20-USH2A`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=558949416#gid=558949416) · **Repo entry:** [`examples/practice-variant-set/v20-ush2a/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v20-ush2a) ·
    **Exercises:** POP_FRQ · CLN_AFF · CDS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of USH2A del exons 63-64 (c.12295-?_14133+?del) against Usher syndrome, drawn from the
`PVS-v20-USH2A` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    USH2A del exons 63-64 (c.12295-?_14133+?del) is assessed for whether it **is causal for** Usher syndrome (`MONDO:0019501`), under AR inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), rna / coding alteration — compose to an illustrative **likely pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is USH2A del exons 63-64 (c.12295-?_14133+?del); the disease/condition (MDE) is Usher syndrome. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+3`, score 3.0) — Affected biallelic probands (illustrative). LOC_PHE (~60% yield) also applicable.
    - **RNA / coding alteration (CDS)** (`CDS_+2`, score 2.0) — Coding-alteration evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 5.0 → *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): USH2A del exons 63-64 (c.12295-?_14133+?del)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0019501 (Usher syndrome)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+3   score  3.0
        - CDS_+2       score  2.0
      final_score:          5.0
      score_classification: likely_pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v20-ush2a/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v20-ush2a/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA3246685756",
    "gene": { "symbol": "USH2A", "id": "HGNC:12601", "mde_associated_gene": "USH2A", "transcript": "NM_206933.3" }
  },
  "mde": { "curie": "MONDO:0019501", "label": "Usher syndrome" },
  "moi": "AR",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v20-USH2A-proband-1",
    "family_id": "PVS-v20-USH2A-FAM-1",
    "phenotypes": [
      { "name": "Sensorineural hearing impairment", "code": "HP:0000407" },
      { "name": "Retinitis pigmentosa", "code": "HP:0000510" }
    ],
    "pheno_specificity_for_mde": "SPECIFIC",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "PCT_80_100",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HOM",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v20-ush2a/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v20-ush2a/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
