# GP1BA c.334G>A (p.Gly112Arg) — Bernard-Soulier syndrome

!!! info "Practice Variant Set · `PVS-v23-GP1BA`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1698869350#gid=1698869350) · **Repo entry:** [`examples/practice-variant-set/v23-gp1ba/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v23-gp1ba) ·
    **Exercises:** POP_FRQ · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in CSpec.

An SVCv4 classification of GP1BA c.334G>A (p.Gly112Arg) against Bernard-Soulier syndrome, drawn from the
`PVS-v23-GP1BA` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    GP1BA c.334G>A (p.Gly112Arg) is assessed for whether it **is causal for** Bernard-Soulier syndrome (`MONDO:0009276`), under AR inheritance, under the baseline SVCv4 specification. 2 lines of evidence — population allele frequency, single-amino-acid change — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is GP1BA c.334G>A (p.Gly112Arg); the disease/condition (MDE) is Bernard-Soulier syndrome. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ`, score 0.0) — Population frequency (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS`, score 0.0) — Predictive missense evidence (PFD, illustrative).
      - `MIS_PRD` (score 0.0) — In-silico predictive missense assessment.
        - `MIS_PRD_INIT_REVEL` (score 0.0) · *provisional* — REVEL 0.322 is low — mildly benign-leaning, but not decisive.

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subject (VBC): GP1BA c.334G>A (p.Gly112Arg)
        predicate:     is_causal_for
        object (MDE):  MONDO:0009276 (Bernard-Soulier syndrome)
        qualifiers:    moi=AR; note=Loss of function is an established disease mechanism.
      specifiedBy:   svcv4:baseline
      hasEvidenceLines:
        - POP_FRQ                  score   0.0
        - MIS                      score   0.0
          - MIS_PRD                  score   0.0
            - MIS_PRD_INIT_REVEL (prov) score   0.0
      score:         0.0
      outcome:       variant_of_uncertain_significance
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
