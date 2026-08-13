# RYR1 c.12383C>T (p.Ala4128Val) — malignant hyperthermia, susceptibility to, 1

!!! info "Practice Variant Set · `PVS-v30-RYR1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1866712904#gid=1866712904) · **Repo entry:** [`examples/practice-variant-set/v30-ryr1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v30-ryr1) ·
    **Exercises:** POP_FRQ · CLN_AFF · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of RYR1 c.12383C>T (p.Ala4128Val) against malignant hyperthermia, susceptibility to, 1, drawn from the
`PVS-v30-RYR1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    RYR1 c.12383C>T (p.Ala4128Val) is assessed for whether it **is causal for** malignant hyperthermia, susceptibility to, 1 (`MONDO:0007783`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), single-amino-acid change — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is RYR1 c.12383C>T (p.Ala4128Val); the disease/condition (MDE) is malignant hyperthermia, susceptibility to, 1. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+2`, score 2.0) — Affected proband (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_+0`, score 0.0) — Predictive missense evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 2.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): RYR1 c.12383C>T (p.Ala4128Val)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0007783 (malignant hyperthermia, susceptibility to, 1)
        qualifiers:           moi=AD; note=Loss of function is NOT an established mechanism for RYR1-related malignant hyperthermia susceptibility.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+2   score  2.0
        - MIS_+0       score  0.0
      final_score:          2.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v30-ryr1/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v30-ryr1/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA405668522",
    "gene": { "symbol": "RYR1", "id": "HGNC:10483", "mde_associated_gene": "RYR1", "transcript": "NM_000540.3" }
  },
  "mde": { "curie": "MONDO:0007783", "label": "malignant hyperthermia, susceptibility to, 1" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v30-RYR1-proband-1",
    "family_id": "PVS-v30-RYR1-FAM-1",
    "phenotypes": [ { "name": "Malignant hyperthermia", "code": "HP:0002047" } ],
    "pheno_specificity_for_mde": "CONSISTENT",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "LT_80",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v30-ryr1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v30-ryr1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
