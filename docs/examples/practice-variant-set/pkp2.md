# PKP2 c.1481C>A (p.Ser494Ter, alt transcript NM_004572.4) — arrhythmogenic right ventricular cardiomyopathy

!!! info "Practice Variant Set · `PVS-PKP2`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1335968173#gid=1335968173) · **Repo entry:** [`examples/practice-variant-set/pkp2/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/pkp2) ·
    **Exercises:** POP_FRQ · NUL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of PKP2 c.1481C>A (p.Ser494Ter, alt transcript NM_004572.4) against arrhythmogenic right ventricular cardiomyopathy, drawn from the
`PVS-PKP2` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    PKP2 c.1481C>A (p.Ser494Ter, alt transcript NM_004572.4) is assessed for whether it **is causal for** arrhythmogenic right ventricular cardiomyopathy (`MONDO:0016587`), under AD inheritance, under the baseline SVCv4 specification. 2 lines of evidence — population allele frequency, absent protein / loss of function — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is PKP2 c.1481C>A (p.Ser494Ter, alt transcript NM_004572.4); the disease/condition (MDE) is arrhythmogenic right ventricular cardiomyopathy. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Absent protein / loss of function (NUL)** (`NUL_+0`, score 0.0) — Transcript-context-limited LoF evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): PKP2 c.1481C>A (p.Ser494Ter, alt transcript NM_004572.4)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0016587 (arrhythmogenic right ventricular cardiomyopathy)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - NUL_+0       score  0.0
      final_score:          0.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/pkp2/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/pkp2/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/pkp2/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
