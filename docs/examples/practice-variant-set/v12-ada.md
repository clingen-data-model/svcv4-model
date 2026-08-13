# ADA c.219-2A>G — severe combined immunodeficiency due to adenosine deaminase deficiency

!!! info "Practice Variant Set · `PVS-v12-ADA`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=125729140#gid=125729140) · **Repo entry:** [`examples/practice-variant-set/v12-ada/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v12-ada) ·
    **Exercises:** POP_FRQ · CLN_AFF · SPL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of ADA c.219-2A>G against severe combined immunodeficiency due to adenosine deaminase deficiency, drawn from the
`PVS-v12-ADA` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    ADA c.219-2A>G is assessed for whether it **is causal for** severe combined immunodeficiency due to adenosine deaminase deficiency (`MONDO:0007064`), under AR inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), splicing — compose to an illustrative **pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is ADA c.219-2A>G; the disease/condition (MDE) is severe combined immunodeficiency due to adenosine deaminase deficiency. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+2`, score 2.0) — Affected homozygous proband (illustrative). No LOC_PHE points (only the subset profile was provided).
    - **Splicing (SPL)** (`SPL_+6`, score 6.0) — Splicing + functional evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 8.0 → *pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): ADA c.219-2A>G
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0007064 (severe combined immunodeficiency due to adenosine deaminase deficiency)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+2   score  2.0
        - SPL_+6       score  6.0
      final_score:          8.0
      score_classification: pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v12-ada/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v12-ada/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA252010",
    "gene": { "symbol": "ADA", "id": "HGNC:186", "mde_associated_gene": "ADA", "transcript": "NM_000022.4" }
  },
  "mde": { "curie": "MONDO:0007064", "label": "severe combined immunodeficiency due to adenosine deaminase deficiency" },
  "moi": "AR",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v12-ADA-proband-1",
    "family_id": "PVS-v12-ADA-FAM-1",
    "phenotypes": [ { "name": "Severe combined immunodeficiency", "code": "HP:0004430" } ],
    "pheno_specificity_for_mde": "SPECIFIC",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "LT_80",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HOM",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v12-ada/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v12-ada/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
