# ATM c.5005+1G>A — ataxia telangiectasia

!!! info "Practice Variant Set · `PVS-v2-ATM`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=174163698#gid=174163698) · **Repo entry:** [`examples/practice-variant-set/v2-atm/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v2-atm) ·
    **Exercises:** POP_FRQ · CLN_AFF · SPL.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of ATM c.5005+1G>A against ataxia telangiectasia, drawn from the
`PVS-v2-ATM` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    ATM c.5005+1G>A is assessed for whether it **is causal for** ataxia telangiectasia (`MONDO:0008840`), under AR inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), splicing — compose to an illustrative **likely pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is ATM c.5005+1G>A; the disease/condition (MDE) is ataxia telangiectasia. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+2`, score 2.0) — Affected biallelic proband (illustrative).
    - **Splicing (SPL)** (`SPL_+3`, score 3.0) — Splicing/critical-domain evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 5.0 → *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): ATM c.5005+1G>A
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0008840 (ataxia telangiectasia)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+2   score  2.0
        - SPL_+3       score  3.0
      final_score:          5.0
      score_classification: likely_pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v2-atm/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v2-atm/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA382538604",
    "gene": { "symbol": "ATM", "id": "HGNC:795", "mde_associated_gene": "ATM", "transcript": "NM_000051.4" }
  },
  "mde": { "curie": "MONDO:0008840", "label": "ataxia telangiectasia" },
  "moi": "AR",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v2-ATM-proband-1",
    "family_id": "PVS-v2-ATM-FAM-1",
    "phenotypes": [ { "name": "Ataxia", "code": "HP:0001251" } ],
    "pheno_specificity_for_mde": "CONSISTENT",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "PCT_80_100",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "compound_het_variant": {
      "id": "CAID:ATM-second-LoF-in-trans",
      "phase_confidence": "HIGH",
      "classification": "P"
    },
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v2-atm/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v2-atm/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
