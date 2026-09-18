# PTEN c.802-3T>A (intronic, splice region) — PTEN hamartoma tumor syndrome

!!! info "Practice Variant Set · `PVS-v28-PTEN`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1850504083#gid=1850504083) · **Repo entry:** [`examples/practice-variant-set/v28-pten/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v28-pten) ·
    **Exercises:** POP_FRQ · SPL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in CSpec.

An SVCv4 classification of PTEN c.802-3T>A (intronic, splice region) against PTEN hamartoma tumor syndrome, drawn from the
`PVS-v28-PTEN` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    PTEN c.802-3T>A (intronic, splice region) is assessed for whether it **is causal for** PTEN hamartoma tumor syndrome (`MONDO:0017623`), under AD inheritance, under the baseline SVCv4 specification. 2 lines of evidence — population allele frequency, splicing — compose to an illustrative **likely benign**.

=== "Narrative"

    The variant being classified (VBC) is PTEN c.802-3T>A (intronic, splice region); the disease/condition (MDE) is PTEN hamartoma tumor syndrome. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ`, score 0.0) — Population frequency (illustrative).
    - **Splicing (SPL)** (`SPL`, score -3.0) — Splicing assay, benign (PFD, illustrative).
      - `SPL_SPA` (score -3.0) — RNA / splicing functional assay.

    Each became an Evidence Line; their scores compose to a Statement final score of -3.0 → *likely benign*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subject (VBC): PTEN c.802-3T>A (intronic, splice region)
        predicate:     is_causal_for
        object (MDE):  MONDO:0017623 (PTEN hamartoma tumor syndrome)
        qualifiers:    moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ                  score   0.0
        - SPL                      score  -3.0
          - SPL_SPA                  score  -3.0
      score:         -3.0
      outcome:       likely_benign
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v28-pten/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v28-pten/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v28-pten/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
