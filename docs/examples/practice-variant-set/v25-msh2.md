# MSH2 c.630G>A (p.Met210Ile) — Lynch syndrome / hereditary non-polyposis colorectal cancer

!!! info "Practice Variant Set · `PVS-v25-MSH2`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=924699761#gid=924699761) · **Repo entry:** [`examples/practice-variant-set/v25-msh2/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v25-msh2) ·
    **Exercises:** POP_FRQ · FNC · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of MSH2 c.630G>A (p.Met210Ile) against Lynch syndrome / hereditary non-polyposis colorectal cancer, drawn from the
`PVS-v25-MSH2` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    MSH2 c.630G>A (p.Met210Ile) is assessed for whether it **is causal for** Lynch syndrome / hereditary non-polyposis colorectal cancer (`MONDO:0005835`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, functional assay, single-amino-acid change — compose to an illustrative **likely benign**.

=== "Narrative"

    The variant being classified (VBC) is MSH2 c.630G>A (p.Met210Ile); the disease/condition (MDE) is Lynch syndrome / hereditary non-polyposis colorectal cancer. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Functional assay (FNC)** (`FNC_-4`, score -4.0) — Functional assay, benign (PFD, illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_+0`, score 0.0) — Predictive missense evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of -4.0 → *likely benign*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): MSH2 c.630G>A (p.Met210Ile)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0005835 (Lynch syndrome / hereditary non-polyposis colorectal cancer)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - FNC_-4       score -4.0
        - MIS_+0       score  0.0
      final_score:          -4.0
      score_classification: likely_benign
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v25-msh2/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v25-msh2/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v25-msh2/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
