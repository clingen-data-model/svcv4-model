# SCN2A c.1108T>C (p.Phe370Leu) — complex neurodevelopmental disorder

!!! info "Practice Variant Set · `PVS-v10-SCN2A`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=130507855#gid=130507855) · **Repo entry:** [`examples/practice-variant-set/v10-scn2a/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v10-scn2a) ·
    **Exercises:** POP_FRQ · CLN_DNV · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of SCN2A c.1108T>C (p.Phe370Leu) against complex neurodevelopmental disorder, drawn from the
`PVS-v10-SCN2A` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    SCN2A c.1108T>C (p.Phe370Leu) is assessed for whether it **is causal for** complex neurodevelopmental disorder (`MONDO:0100038`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, de novo occurrence, single-amino-acid change — compose to an illustrative **likely pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is SCN2A c.1108T>C (p.Phe370Leu); the disease/condition (MDE) is complex neurodevelopmental disorder. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **De novo occurrence (CLN_DNV)** (`CLN_DNV_+2`, score 2.0) — De novo occurrence (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_+4`, score 4.0) — Predictive missense evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 6.0 → *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): SCN2A c.1108T>C (p.Phe370Leu)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0100038 (complex neurodevelopmental disorder)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_DNV_+2   score  2.0
        - MIS_+4       score  4.0
      final_score:          6.0
      score_classification: likely_pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v10-scn2a/classification.json)

    [Download `case-CLN_DNV.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v10-scn2a/case-CLN_DNV.json)

## The case capture (CLN_DNV)

The workflow submission that feeds the `CLN_DNV` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA349020765",
    "gene": { "symbol": "SCN2A", "id": "HGNC:10588", "mde_associated_gene": "SCN2A", "transcript": "NM_001040142.2" }
  },
  "mde": { "curie": "MONDO:0100038", "label": "complex neurodevelopmental disorder" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v10-SCN2A-proband-1",
    "family_id": "PVS-v10-SCN2A-FAM-1",
    "phenotypes": [ { "name": "Epileptic encephalopathy", "code": "HP:0200134" } ],
    "pheno_specificity_for_mde": "CONSISTENT",
    "testing": { "method": "Exome", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "LT_80",
    "confirmed_parental_relationship": "FALSE",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v10-scn2a/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v10-scn2a/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
