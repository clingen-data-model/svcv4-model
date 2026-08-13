# RUNX1 c.1412_1413dup (p.Leu472AlafsTer123) — hereditary thrombocytopenia and hematologic cancer predisposition syndrome

!!! info "Practice Variant Set · `PVS-v9-RUNX1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=866552192#gid=866552192) · **Repo entry:** [`examples/practice-variant-set/v9-runx1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v9-runx1) ·
    **Exercises:** POP_FRQ · CLN_AFF · LOC_SEG · CDS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of RUNX1 c.1412_1413dup (p.Leu472AlafsTer123) against hereditary thrombocytopenia and hematologic cancer predisposition syndrome, drawn from the
`PVS-v9-RUNX1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    RUNX1 c.1412_1413dup (p.Leu472AlafsTer123) is assessed for whether it **is causal for** hereditary thrombocytopenia and hematologic cancer predisposition syndrome (`MONDO:0011071`), under AD inheritance, under the baseline SVCv4 specification. 4 lines of evidence — population allele frequency, clinical observation in affected individual(s), locus specificity — segregation, rna / coding alteration — compose to an illustrative **likely pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is RUNX1 c.1412_1413dup (p.Leu472AlafsTer123); the disease/condition (MDE) is hereditary thrombocytopenia and hematologic cancer predisposition syndrome. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+1`, score 1.0) — Affected proband (illustrative).
    - **Locus specificity** (`LOC_SEG_+3`, score 3.0) — Co-segregation (illustrative).
    - **RNA / coding alteration (CDS)** (`CDS_+2`, score 2.0) — Coding-alteration / critical-domain evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 6.0 → *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): RUNX1 c.1412_1413dup (p.Leu472AlafsTer123)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0011071 (hereditary thrombocytopenia and hematologic cancer predisposition syndrome)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+1   score  1.0
        - LOC_SEG_+3   score  3.0
        - CDS_+2       score  2.0
      final_score:          6.0
      score_classification: likely_pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v9-runx1/classification.json)

    [Download `case-LOC_SEG.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v9-runx1/case-LOC_SEG.json)

## The case capture (LOC_SEG)

The workflow submission that feeds the `LOC_SEG` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA658799413",
    "gene": { "symbol": "RUNX1", "id": "HGNC:10471", "mde_associated_gene": "RUNX1", "transcript": "NM_001754.5" }
  },
  "mde": { "curie": "MONDO:0011071", "label": "hereditary thrombocytopenia and hematologic cancer predisposition syndrome" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v9-RUNX1-proband-1",
    "family_id": "PVS-v9-RUNX1-FAM-1",
    "pheno_specificity_for_mde": "CONSISTENT",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "FALSE",
    "relatives": [
      {
        "parent_of_proband": "FALSE",
        "affected_w_mde": "TRUE",
        "vbc_exists": "TRUE",
        "vbc_zygosity": "HET",
        "cmp_het_variant_exists": "FALSE"
      },
      {
        "parent_of_proband": "TRUE",
        "affected_w_mde": "TRUE",
        "vbc_exists": "TRUE",
        "vbc_zygosity": "HET",
        "cmp_het_variant_exists": "FALSE"
      }
    ]
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v9-runx1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v9-runx1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
