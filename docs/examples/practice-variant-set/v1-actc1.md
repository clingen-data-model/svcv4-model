# ACTC1 c.488dup (p.His163GlnfsTer7) — hypertrophic cardiomyopathy

!!! info "Practice Variant Set · `PVS-v1-ACTC1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=0#gid=0) · **Repo entry:** [`examples/practice-variant-set/v1-actc1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v1-actc1) ·
    **Exercises:** POP_FRQ · CLN_AFF · CLN_UAF · LOC_PHE.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of ACTC1 c.488dup (p.His163GlnfsTer7) against hypertrophic cardiomyopathy, drawn from the
`PVS-v1-ACTC1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    ACTC1 c.488dup (p.His163GlnfsTer7) is assessed for whether it **is causal for** hypertrophic cardiomyopathy (`MONDO:0005045`), under AD inheritance, under the baseline SVCv4 specification. 4 lines of evidence — population allele frequency, clinical observation in affected individual(s), clinical observation in unaffected individual(s), locus specificity — phenotype — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is ACTC1 c.488dup (p.His163GlnfsTer7); the disease/condition (MDE) is hypertrophic cardiomyopathy. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+1`, score 1.0) — Affected proband (illustrative).
    - **Clinical observation in unaffected individual(s) (CLN_UAF)** (`CLN_UAF_+0`, score 0.0) — Unaffected carrier (illustrative).
    - **Locus specificity** (`LOC_PHE_+0`, score 0.0) — Locus specificity for phenotype (illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 1.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): ACTC1 c.488dup (p.His163GlnfsTer7)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0005045 (hypertrophic cardiomyopathy)
        qualifiers:           moi=AD; note=Loss of function is NOT an established mechanism for ACTC1-related HCM.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+1   score  1.0
        - CLN_UAF_+0   score  0.0
        - LOC_PHE_+0   score  0.0
      final_score:          1.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v1-actc1/classification.json)

    [Download `case-CLN_UAF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v1-actc1/case-CLN_UAF.json)

    [Download `case-LOC_PHE.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v1-actc1/case-LOC_PHE.json)

## The case capture (CLN_UAF)

The workflow submission that feeds the `CLN_UAF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA2627662931",
    "gene": { "symbol": "ACTC1", "id": "HGNC:143", "mde_associated_gene": "ACTC1", "transcript": "NM_005159.5" }
  },
  "mde": { "curie": "MONDO:0005045", "label": "hypertrophic cardiomyopathy" },
  "moi": "AD",
  "case": {
    "id": "PVS-v1-ACTC1-proband-2",
    "family_id": "PVS-v1-ACTC1-FAM-2",
    "age_matched_penetrance": "LT_80",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v1-actc1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v1-actc1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
