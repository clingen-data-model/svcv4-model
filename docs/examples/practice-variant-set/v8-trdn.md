# TRDN c.1462A>T (p.Lys488Ter) — catecholaminergic polymorphic ventricular tachycardia

!!! info "Practice Variant Set · `PVS-v8-TRDN`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=345645658#gid=345645658) · **Repo entry:** [`examples/practice-variant-set/v8-trdn/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v8-trdn) ·
    **Exercises:** POP_FRQ · CLN_UAF · NUL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of TRDN c.1462A>T (p.Lys488Ter) against catecholaminergic polymorphic ventricular tachycardia, drawn from the
`PVS-v8-TRDN` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    TRDN c.1462A>T (p.Lys488Ter) is assessed for whether it **is causal for** catecholaminergic polymorphic ventricular tachycardia (`MONDO:0017990`), under AR inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in unaffected individual(s), absent protein / loss of function — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is TRDN c.1462A>T (p.Lys488Ter); the disease/condition (MDE) is catecholaminergic polymorphic ventricular tachycardia. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in unaffected individual(s) (CLN_UAF)** (`CLN_UAF_+0`, score 0.0) — Unaffected heterozygous carrier (illustrative).
    - **Absent protein / loss of function (NUL)** (`NUL_+0`, score 0.0) — Transcript-context-limited LoF evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): TRDN c.1462A>T (p.Lys488Ter)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0017990 (catecholaminergic polymorphic ventricular tachycardia)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_UAF_+0   score  0.0
        - NUL_+0       score  0.0
      final_score:          0.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v8-trdn/classification.json)

    [Download `case-CLN_UAF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v8-trdn/case-CLN_UAF.json)

## The case capture (CLN_UAF)

The workflow submission that feeds the `CLN_UAF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA365563886",
    "gene": { "symbol": "TRDN", "id": "HGNC:12261", "mde_associated_gene": "TRDN", "transcript": "NM_006073.4" }
  },
  "mde": { "curie": "MONDO:0017990", "label": "catecholaminergic polymorphic ventricular tachycardia" },
  "moi": "AR",
  "case": {
    "id": "PVS-v8-TRDN-relative-1",
    "family_id": "PVS-v8-TRDN-FAM-1",
    "age_matched_penetrance": "LT_80",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v8-trdn/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v8-trdn/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
