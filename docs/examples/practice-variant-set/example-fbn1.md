# FBN1 c.7003C>T (p.Arg2335Trp) — Marfan syndrome

!!! info "Practice Variant Set · `PVS-EXAMPLE-FBN1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1792158038#gid=1792158038) · **Repo entry:** [`examples/practice-variant-set/example-fbn1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/example-fbn1) ·
    **Exercises:** POP_FRQ · CLN_AFF · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of FBN1 c.7003C>T (p.Arg2335Trp) against Marfan syndrome, drawn from the
`PVS-EXAMPLE-FBN1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    FBN1 c.7003C>T (p.Arg2335Trp) is assessed for whether it **is causal for** Marfan syndrome (`MONDO:0007947`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), single-amino-acid change — compose to an illustrative **likely pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is FBN1 c.7003C>T (p.Arg2335Trp); the disease/condition (MDE) is Marfan syndrome. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+3`, score 3.0) — Affected probands (illustrative). Proband 2's confirmed de novo is captured separately under CLN_DNV.
    - **Single-amino-acid change (MIS)** (`MIS_+2`, score 2.0) — Predictive missense evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 5.0 → *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): FBN1 c.7003C>T (p.Arg2335Trp)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0007947 (Marfan syndrome)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+3   score  3.0
        - MIS_+2       score  2.0
      final_score:          5.0
      score_classification: likely_pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/example-fbn1/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/example-fbn1/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA016924",
    "gene": { "symbol": "FBN1", "id": "HGNC:3603", "mde_associated_gene": "FBN1", "transcript": "NM_000138.5" }
  },
  "mde": { "curie": "MONDO:0007947", "label": "Marfan syndrome" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-EXAMPLE-FBN1-proband-2",
    "family_id": "PVS-EXAMPLE-FBN1-FAM-2",
    "phenotypes": [ { "name": "Ectopia lentis", "code": "HP:0001083" } ],
    "pheno_specificity_for_mde": "SPECIFIC",
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
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/example-fbn1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/example-fbn1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
