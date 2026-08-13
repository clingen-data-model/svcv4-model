# ATXN7L3 c.332del (p.Asn111ThrfsTer16) — complex neurodevelopmental disorder (ATXN7L3-related; MONDO pending)

!!! info "Practice Variant Set · `PVS-v14-ATXN7L3`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=306028402#gid=306028402) · **Repo entry:** [`examples/practice-variant-set/v14-atxn7l3/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v14-atxn7l3) ·
    **Exercises:** POP_FRQ · CLN_AFF · NUL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of ATXN7L3 c.332del (p.Asn111ThrfsTer16) against complex neurodevelopmental disorder (ATXN7L3-related; MONDO pending), drawn from the
`PVS-v14-ATXN7L3` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    ATXN7L3 c.332del (p.Asn111ThrfsTer16) is assessed for whether it **is causal for** complex neurodevelopmental disorder (ATXN7L3-related; MONDO pending) (`MONDO:0100038`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), absent protein / loss of function — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is ATXN7L3 c.332del (p.Asn111ThrfsTer16); the disease/condition (MDE) is complex neurodevelopmental disorder (ATXN7L3-related; MONDO pending). The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+2`, score 2.0) — Affected proband + confirmed de novo (illustrative). CLN_DNV also applicable.
    - **Absent protein / loss of function (NUL)** (`NUL_+0`, score 0.0) — Predicted null, mechanism-tempered (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 2.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): ATXN7L3 c.332del (p.Asn111ThrfsTer16)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0100038 (complex neurodevelopmental disorder (ATXN7L3-related; MONDO pending))
        qualifiers:           moi=AD; note=Loss of function is the SUSPECTED (not established) mechanism (GenCC LoF framework).
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+2   score  2.0
        - NUL_+0       score  0.0
      final_score:          2.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v14-atxn7l3/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v14-atxn7l3/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA3246641821",
    "gene": { "symbol": "ATXN7L3", "id": "HGNC:28758", "mde_associated_gene": "ATXN7L3", "transcript": "NM_001382309.1" }
  },
  "mde": { "curie": "MONDO:0100038", "label": "complex neurodevelopmental disorder (ATXN7L3-related; MONDO pending)" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v14-ATXN7L3-proband-1",
    "family_id": "PVS-v14-ATXN7L3-FAM-1",
    "phenotypes": [
      { "name": "Global developmental delay", "code": "HP:0001263" },
      { "name": "Hypotonia", "code": "HP:0001252" }
    ],
    "pheno_specificity_for_mde": "CONSISTENT",
    "testing": { "method": "Exome", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "LT_80",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v14-atxn7l3/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v14-atxn7l3/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
