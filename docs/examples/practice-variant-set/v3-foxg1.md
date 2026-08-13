# FOXG1 c.234_236delGCC (p.Pro79del) — FOXG1-related disorder

!!! info "Practice Variant Set · `PVS-v3-FOXG1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=692785807#gid=692785807) · **Repo entry:** [`examples/practice-variant-set/v3-foxg1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v3-foxg1) ·
    **Exercises:** POP_FRQ · CLN_AFF · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of FOXG1 c.234_236delGCC (p.Pro79del) against FOXG1-related disorder, drawn from the
`PVS-v3-FOXG1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    FOXG1 c.234_236delGCC (p.Pro79del) is assessed for whether it **is causal for** FOXG1-related disorder (`MONDO:0100040`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), single-amino-acid change — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is FOXG1 c.234_236delGCC (p.Pro79del); the disease/condition (MDE) is FOXG1-related disorder. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+1`, score 1.0) — Affected proband (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_-1`, score -1.0) — Polymorphic-repeat context (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): FOXG1 c.234_236delGCC (p.Pro79del)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0100040 (FOXG1-related disorder)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+1   score  1.0
        - MIS_-1       score -1.0
      final_score:          0.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v3-foxg1/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v3-foxg1/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA258396552",
    "gene": { "symbol": "FOXG1", "id": "HGNC:3811", "mde_associated_gene": "FOXG1", "transcript": "NM_005249.5" }
  },
  "mde": { "curie": "MONDO:0100040", "label": "FOXG1-related disorder" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v3-FOXG1-proband-1",
    "family_id": "PVS-v3-FOXG1-FAM-1",
    "phenotypes": [
      { "name": "Severe global developmental delay", "code": "HP:0011344" },
      { "name": "Microcephaly", "code": "HP:0000252" }
    ],
    "pheno_specificity_for_mde": "CONSISTENT",
    "testing": { "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "LT_80",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v3-foxg1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v3-foxg1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
