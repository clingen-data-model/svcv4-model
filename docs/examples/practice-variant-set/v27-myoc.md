# MYOC c.719A>G (p.Glu240Gly) — open-angle glaucoma

!!! info "Practice Variant Set · `PVS-v27-MYOC`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=383577094#gid=383577094) · **Repo entry:** [`examples/practice-variant-set/v27-myoc/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v27-myoc) ·
    **Exercises:** POP_FRQ · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in CSpec.

An SVCv4 classification of MYOC c.719A>G (p.Glu240Gly) against open-angle glaucoma, drawn from the
`PVS-v27-MYOC` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    MYOC c.719A>G (p.Glu240Gly) is assessed for whether it **is causal for** open-angle glaucoma (`MONDO:0005338`), under AD inheritance, under the baseline SVCv4 specification. 2 lines of evidence — population allele frequency, single-amino-acid change — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is MYOC c.719A>G (p.Glu240Gly); the disease/condition (MDE) is open-angle glaucoma. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ`, score 0.0) — Population frequency (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS`, score 0.0) — Predictive missense evidence (PFD, illustrative).
      - `MIS_PRD` (score 0.0) — In-silico predictive missense assessment.
        - `MIS_PRD_INIT_REVEL` (score 0.0) · *provisional* — REVEL 0.205 is low; no same-codon informative variants.

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subject (VBC): MYOC c.719A>G (p.Glu240Gly)
        predicate:     is_causal_for
        object (MDE):  MONDO:0005338 (open-angle glaucoma)
        qualifiers:    moi=AD; note=Loss of function is NOT an established mechanism for MYOC-related open-angle glaucoma.
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

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v27-myoc/classification.json)

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v27-myoc/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v27-myoc/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
