# GP1BA c.334G>A (p.Gly112Arg) — Bernard-Soulier syndrome

!!! info "Practice Variant Set · `PVS-v23-GP1BA`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1698869350#gid=1698869350) · **Repo entry:** [`examples/practice-variant-set/v23-gp1ba/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v23-gp1ba) ·
    **Exercises:** POP_FRQ · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of GP1BA c.334G>A (p.Gly112Arg) against Bernard-Soulier syndrome, drawn from the
`PVS-v23-GP1BA` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    GP1BA c.334G>A (p.Gly112Arg) is assessed for whether it **is causal for** Bernard-Soulier syndrome (`MONDO:0009276`), under AR inheritance, under the baseline SVCv4 specification. 2 lines of evidence — population allele frequency, single-amino-acid change — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is GP1BA c.334G>A (p.Gly112Arg); the disease/condition (MDE) is Bernard-Soulier syndrome. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_+0`, score 0.0) — Predictive missense evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): GP1BA c.334G>A (p.Gly112Arg)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0009276 (Bernard-Soulier syndrome)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - MIS_+0       score  0.0
      final_score:          0.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v23-gp1ba/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v23-gp1ba/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v23-gp1ba/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
