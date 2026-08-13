# PAH c.865G>A (p.Gly289Arg) — phenylketonuria

!!! info "Practice Variant Set · `PVS-v7-PAH`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=2018479162#gid=2018479162) · **Repo entry:** [`examples/practice-variant-set/v7-pah/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v7-pah) ·
    **Exercises:** POP_FRQ · CLN_AFF · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of PAH c.865G>A (p.Gly289Arg) against phenylketonuria, drawn from the
`PVS-v7-PAH` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    PAH c.865G>A (p.Gly289Arg) is assessed for whether it **is causal for** phenylketonuria (`MONDO:0009861`), under AR inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, clinical observation in affected individual(s), single-amino-acid change — compose to an illustrative **pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is PAH c.865G>A (p.Gly289Arg); the disease/condition (MDE) is phenylketonuria. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+4`, score 4.0) — Affected biallelic probands (illustrative). LOC_PHE also applicable (>82% yield).
    - **Single-amino-acid change (MIS)** (`MIS_+4`, score 4.0) — Predictive missense evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 8.0 → *pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): PAH c.865G>A (p.Gly289Arg)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0009861 (phenylketonuria)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+4   score  4.0
        - MIS_+4       score  4.0
      final_score:          8.0
      score_classification: pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v7-pah/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v7-pah/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA386294434",
    "gene": { "symbol": "PAH", "id": "HGNC:8582", "mde_associated_gene": "PAH", "transcript": "NM_000277.3" }
  },
  "mde": { "curie": "MONDO:0009861", "label": "phenylketonuria" },
  "moi": "AR",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v7-PAH-proband-1",
    "family_id": "PVS-v7-PAH-FAM-1",
    "phenotypes": [ { "name": "Hyperphenylalaninemia", "code": "HP:0004923" } ],
    "pheno_specificity_for_mde": "CONSISTENT",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "PCT_80_100",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "compound_het_variant": {
      "id": "CAID:PAH-Gly272Ter-in-trans",
      "phase_confidence": "HIGH",
      "classification": "P"
    },
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v7-pah/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v7-pah/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
