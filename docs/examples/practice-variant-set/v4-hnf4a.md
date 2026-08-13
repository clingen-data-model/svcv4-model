# HNF4A c.421del (p.Arg141AspfsTer29) — monogenic diabetes

!!! info "Practice Variant Set · `PVS-v4-HNF4A`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=23733664#gid=23733664) · **Repo entry:** [`examples/practice-variant-set/v4-hnf4a/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v4-hnf4a) ·
    **Exercises:** POP_FRQ · CLN_AFF · NUL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of HNF4A c.421del (p.Arg141AspfsTer29) against monogenic diabetes, drawn from the
`PVS-v4-HNF4A` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    HNF4A c.421del (p.Arg141AspfsTer29) is assessed for whether it **is causal for** monogenic diabetes (`MONDO:0015967`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), absent protein / loss of function — compose to an illustrative **likely pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is HNF4A c.421del (p.Arg141AspfsTer29); the disease/condition (MDE) is monogenic diabetes. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+1`, score 1.0) — Affected proband (illustrative). Note: LOC_SEG also applicable — variant segregated with MODY in 3 affected relatives — but is captured separately.
    - **Absent protein / loss of function (NUL)** (`NUL_+4`, score 4.0) — Predicted null / LoF evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 5.0 → *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): HNF4A c.421del (p.Arg141AspfsTer29)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0015967 (monogenic diabetes)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+1   score  1.0
        - NUL_+4       score  4.0
      final_score:          5.0
      score_classification: likely_pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v4-hnf4a/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v4-hnf4a/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA2573106197",
    "gene": { "symbol": "HNF4A", "id": "HGNC:5024", "mde_associated_gene": "HNF4A", "transcript": "NM_175914.5" }
  },
  "mde": { "curie": "MONDO:0015967", "label": "monogenic diabetes" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v4-HNF4A-proband-1",
    "family_id": "PVS-v4-HNF4A-FAM-1",
    "phenotypes": [ { "name": "Maturity-onset diabetes of the young", "code": "HP:0004904" } ],
    "pheno_specificity_for_mde": "CONSISTENT",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "LT_80",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v4-hnf4a/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v4-hnf4a/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
