# ACVRL1 c.88C>T (p.Pro30Ser) — hereditary hemorrhagic telangiectasia

!!! info "Practice Variant Set · `PVS-v11-ACVRL1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1656716375#gid=1656716375) · **Repo entry:** [`examples/practice-variant-set/v11-acvrl1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v11-acvrl1) ·
    **Exercises:** POP_FRQ · CLN_ALTV · CLN_ALTG · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of ACVRL1 c.88C>T (p.Pro30Ser) against hereditary hemorrhagic telangiectasia, drawn from the
`PVS-v11-ACVRL1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    ACVRL1 c.88C>T (p.Pro30Ser) is assessed for whether it **is causal for** hereditary hemorrhagic telangiectasia (`MONDO:0019180`), under AD inheritance, under the baseline SVCv4 specification. 4 lines of evidence — population allele frequency, affected with an alternate cause — variant, affected with an alternate cause — gene, single-amino-acid change — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is ACVRL1 c.88C>T (p.Pro30Ser); the disease/condition (MDE) is hereditary hemorrhagic telangiectasia. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Affected with an alternate cause** (`CLN_ALTV_-1`, score -1.0) — Alternate cause — variant (illustrative).
    - **Affected with an alternate cause** (`CLN_ALTG_-1`, score -1.0) — Alternate cause — gene (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_+0`, score 0.0) — Predictive missense evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): ACVRL1 c.88C>T (p.Pro30Ser)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0019180 (hereditary hemorrhagic telangiectasia)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_ALTV_-1  score -1.0
        - CLN_ALTG_-1  score -1.0
        - MIS_+0       score  0.0
      final_score:          0.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v11-acvrl1/classification.json)

    [Download `case-CLN_ALTG.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v11-acvrl1/case-CLN_ALTG.json)

    [Download `case-CLN_ALTV.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v11-acvrl1/case-CLN_ALTV.json)

## The case capture (CLN_ALTG)

The workflow submission that feeds the `CLN_ALTG` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA211326",
    "gene": { "symbol": "ACVRL1", "id": "HGNC:175", "mde_associated_gene": "ACVRL1", "transcript": "NM_000020.3" }
  },
  "mde": { "curie": "MONDO:0019180", "label": "hereditary hemorrhagic telangiectasia" },
  "moi": "AD",
  "case": {
    "id": "PVS-v11-ACVRL1-case-2",
    "pheno_severity": "MONO_EQ_EXPECTED",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "TRUE",
    "additional_variants": [
      {
        "id": "CAID:ENG-pathogenic-LoF",
        "gene": { "symbol": "ENG", "id": "HGNC:3349", "mde_associated_gene": "ENG" },
        "zygosity": "HET",
        "classification": "P"
      }
    ]
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v11-acvrl1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v11-acvrl1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
