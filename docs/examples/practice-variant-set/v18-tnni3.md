# TNNI3 c.236G>T (p.Arg79Leu) — hypertrophic cardiomyopathy

!!! info "Practice Variant Set · `PVS-v18-TNNI3`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1710001749#gid=1710001749) · **Repo entry:** [`examples/practice-variant-set/v18-tnni3/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v18-tnni3) ·
    **Exercises:** POP_FRQ · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of TNNI3 c.236G>T (p.Arg79Leu) against hypertrophic cardiomyopathy, drawn from the
`PVS-v18-TNNI3` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    TNNI3 c.236G>T (p.Arg79Leu) is assessed for whether it **is causal for** hypertrophic cardiomyopathy (`MONDO:0005045`), under AD inheritance, under the baseline SVCv4 specification. 2 lines of evidence — population allele frequency, single-amino-acid change — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is TNNI3 c.236G>T (p.Arg79Leu); the disease/condition (MDE) is hypertrophic cardiomyopathy. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_+0`, score 0.0) — Predictive missense evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): TNNI3 c.236G>T (p.Arg79Leu)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0005045 (hypertrophic cardiomyopathy)
        qualifiers:           moi=AD; note=Loss of function is NOT an established mechanism for TNNI3-related HCM.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - MIS_+0       score  0.0
      final_score:          0.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v18-tnni3/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v18-tnni3/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v18-tnni3/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
