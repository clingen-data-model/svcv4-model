# DICER1 c.2T>C (p.Met1Thr, start-loss) — DICER1-related tumor predisposition

!!! info "Practice Variant Set · `PVS-v15-DICER1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1839319038#gid=1839319038) · **Repo entry:** [`examples/practice-variant-set/v15-dicer1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v15-dicer1) ·
    **Exercises:** POP_FRQ · NUL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of DICER1 c.2T>C (p.Met1Thr, start-loss) against DICER1-related tumor predisposition, drawn from the
`PVS-v15-DICER1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    DICER1 c.2T>C (p.Met1Thr, start-loss) is assessed for whether it **is causal for** DICER1-related tumor predisposition (`MONDO:0100216`), under AD inheritance, under the baseline SVCv4 specification. 2 lines of evidence — population allele frequency, absent protein / loss of function — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is DICER1 c.2T>C (p.Met1Thr, start-loss); the disease/condition (MDE) is DICER1-related tumor predisposition. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Absent protein / loss of function (NUL)** (`NUL_+0`, score 0.0) — Start-loss with uncertain LoF (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): DICER1 c.2T>C (p.Met1Thr, start-loss)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0100216 (DICER1-related tumor predisposition)
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

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v15-dicer1/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v15-dicer1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v15-dicer1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
