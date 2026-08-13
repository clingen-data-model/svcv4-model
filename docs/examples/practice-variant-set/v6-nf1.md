# NF1 c.3496G>C (p.Gly1166Arg) — neurofibromatosis type 1

!!! info "Practice Variant Set · `PVS-v6-NF1`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1040336969#gid=1040336969) · **Repo entry:** [`examples/practice-variant-set/v6-nf1/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v6-nf1) ·
    **Exercises:** POP_FRQ · CLN_AFF · SPL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of NF1 c.3496G>C (p.Gly1166Arg) against neurofibromatosis type 1, drawn from the
`PVS-v6-NF1` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    NF1 c.3496G>C (p.Gly1166Arg) is assessed for whether it **is causal for** neurofibromatosis type 1 (`MONDO:0018975`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), splicing — compose to an illustrative **likely pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is NF1 c.3496G>C (p.Gly1166Arg); the disease/condition (MDE) is neurofibromatosis type 1. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+2`, score 2.0) — Affected probands (illustrative). Proband 1's confirmed de novo is captured separately under CLN_DNV; LOC_PHE also applicable (>82% yield).
    - **Splicing (SPL)** (`SPL_+4`, score 4.0) — Splicing evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 6.0 → *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): NF1 c.3496G>C (p.Gly1166Arg)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0018975 (neurofibromatosis type 1)
        qualifiers:           moi=AD; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+2   score  2.0
        - SPL_+4       score  4.0
      final_score:          6.0
      score_classification: likely_pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v6-nf1/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v6-nf1/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA398989536",
    "gene": { "symbol": "NF1", "id": "HGNC:7765", "mde_associated_gene": "NF1", "transcript": "NM_001042492.3" }
  },
  "mde": { "curie": "MONDO:0018975", "label": "neurofibromatosis type 1" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v6-NF1-proband-1",
    "family_id": "PVS-v6-NF1-FAM-1",
    "phenotypes": [
      { "name": "Neurofibroma", "code": "HP:0001067" },
      { "name": "Cafe-au-lait spot", "code": "HP:0000957" },
      { "name": "Axillary freckling", "code": "HP:0000997" }
    ],
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
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v6-nf1/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v6-nf1/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
