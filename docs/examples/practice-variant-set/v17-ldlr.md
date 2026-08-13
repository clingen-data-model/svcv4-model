# LDLR c.1216C>A (p.Arg406=, splice-altering) — familial hypercholesterolemia

!!! info "Practice Variant Set · `PVS-v17-LDLR`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1874520311#gid=1874520311) · **Repo entry:** [`examples/practice-variant-set/v17-ldlr/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v17-ldlr) ·
    **Exercises:** POP_FRQ · CLN_AFF · SPL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of LDLR c.1216C>A (p.Arg406=, splice-altering) against familial hypercholesterolemia, drawn from the
`PVS-v17-LDLR` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    LDLR c.1216C>A (p.Arg406=, splice-altering) is assessed for whether it **is causal for** familial hypercholesterolemia (`MONDO:0005439`), under SD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), splicing — compose to an illustrative **pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is LDLR c.1216C>A (p.Arg406=, splice-altering); the disease/condition (MDE) is familial hypercholesterolemia. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+2`, score 2.0) — Affected probands (illustrative). A biallelic proband also supports LOC_PHE.
    - **Splicing (SPL)** (`SPL_+5`, score 5.0) — Splicing + functional evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 7.0 → *pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): LDLR c.1216C>A (p.Arg406=, splice-altering)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0005439 (familial hypercholesterolemia)
        qualifiers:           moi=SD; note=Semidominant. Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+2   score  2.0
        - SPL_+5       score  5.0
      final_score:          7.0
      score_classification: pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v17-ldlr/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v17-ldlr/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA023436",
    "gene": { "symbol": "LDLR", "id": "HGNC:6547", "mde_associated_gene": "LDLR", "transcript": "NM_000527.5" }
  },
  "mde": { "curie": "MONDO:0005439", "label": "familial hypercholesterolemia" },
  "moi": "SD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v17-LDLR-proband-1",
    "family_id": "PVS-v17-LDLR-FAM-1",
    "phenotypes": [ { "name": "Hypercholesterolemia", "code": "HP:0003124" } ],
    "pheno_specificity_for_mde": "SPECIFIC",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "PCT_80_100",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v17-ldlr/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v17-ldlr/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
