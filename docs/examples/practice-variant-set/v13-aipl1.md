# AIPL1 c.150C>T (p.Asp50=) — AIPL1-related retinopathy

!!! info "Practice Variant Set · `PVS-v13-AIPL1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=2040908414#gid=2040908414) · **Repo entry:** [`examples/practice-variant-set/v13-aipl1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v13-aipl1) ·
    **Exercises:** POP_FRQ · POP_HMZ · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of AIPL1 c.150C>T (p.Asp50=) against AIPL1-related retinopathy, drawn from the
`PVS-v13-AIPL1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    AIPL1 c.150C>T (p.Asp50=) is assessed for whether it **is causal for** AIPL1-related retinopathy (`MONDO:0100438`), under AR inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, population homozygotes/hemizygotes, single-amino-acid change — compose to an illustrative **likely benign**.

=== "Narrative"

    The variant being classified (VBC) is AIPL1 c.150C>T (p.Asp50=); the disease/condition (MDE) is AIPL1-related retinopathy. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Population homozygotes/hemizygotes (POP_HMZ)** (`POP_HMZ_-2`, score -2.0) — Population homozygotes (benign, illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_-2`, score -2.0) — Synonymous / no-impact evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of -4.0 → *likely benign*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): AIPL1 c.150C>T (p.Asp50=)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0100438 (AIPL1-related retinopathy)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - POP_HMZ_-2   score -2.0
        - MIS_-2       score -2.0
      final_score:          -4.0
      score_classification: likely_benign
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v13-aipl1/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v13-aipl1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v13-aipl1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
