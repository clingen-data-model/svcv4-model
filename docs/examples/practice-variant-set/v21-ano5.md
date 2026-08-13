# ANO5 c.139-1del (splice acceptor) — autosomal recessive limb-girdle muscular dystrophy

!!! info "Practice Variant Set · `PVS-v21-ANO5`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=870504889#gid=870504889) · **Repo entry:** [`examples/practice-variant-set/v21-ano5/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v21-ano5) ·
    **Exercises:** POP_FRQ · SPL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of ANO5 c.139-1del (splice acceptor) against autosomal recessive limb-girdle muscular dystrophy, drawn from the
`PVS-v21-ANO5` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    ANO5 c.139-1del (splice acceptor) is assessed for whether it **is causal for** autosomal recessive limb-girdle muscular dystrophy (`MONDO:0015152`), under AR inheritance, under the baseline SVCv4 specification. 2 lines of evidence — population allele frequency, splicing — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is ANO5 c.139-1del (splice acceptor); the disease/condition (MDE) is autosomal recessive limb-girdle muscular dystrophy. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Splicing (SPL)** (`SPL_+2`, score 2.0) — Splicing / domain evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 2.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): ANO5 c.139-1del (splice acceptor)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0015152 (autosomal recessive limb-girdle muscular dystrophy)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - SPL_+2       score  2.0
      final_score:          2.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v21-ano5/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v21-ano5/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v21-ano5/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
