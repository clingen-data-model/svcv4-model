# DYSF c.5626G>A (p.Asp1876Asn) — autosomal recessive limb-girdle muscular dystrophy

!!! info "Practice Variant Set · `PVS-v16-DYSF`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=678750638#gid=678750638) · **Repo entry:** [`examples/practice-variant-set/v16-dysf/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v16-dysf) ·
    **Exercises:** POP_FRQ · CLN_AFF · FNC · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

An SVCv4 classification of DYSF c.5626G>A (p.Asp1876Asn) against autosomal recessive limb-girdle muscular dystrophy, drawn from the
`PVS-v16-DYSF` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    DYSF c.5626G>A (p.Asp1876Asn) is assessed for whether it **is causal for** autosomal recessive limb-girdle muscular dystrophy (`MONDO:0015152`), under AR inheritance, under the baseline SVCv4 specification. 4 lines of evidence — population allele frequency, clinical observation in affected individual(s), functional assay, single-amino-acid change — compose to an illustrative **pathogenic**.

=== "Narrative"

    The variant being classified (VBC) is DYSF c.5626G>A (p.Asp1876Asn); the disease/condition (MDE) is autosomal recessive limb-girdle muscular dystrophy. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ_+0`, score 0.0) — Population frequency (illustrative).
    - **Clinical observation in affected individual(s) (CLN_AFF)** (`CLN_AFF_+2`, score 2.0) — Affected homozygous proband (illustrative). LOC_SEG (3 affected sibs) applicable, captured separately.
    - **Functional assay (FNC)** (`FNC_+2`, score 2.0) — Functional assay (PFD, illustrative).
    - **Single-amino-acid change (MIS)** (`MIS_+2`, score 2.0) — Predictive missense + same-residue evidence (PFD, illustrative).

    Each became an Evidence Line; their scores compose to a Statement final score of 8.0 → *pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): DYSF c.5626G>A (p.Asp1876Asn)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0015152 (autosomal recessive limb-girdle muscular dystrophy)
        qualifiers:           moi=AR; note=Loss of function is an established disease mechanism.
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0   score  0.0
        - CLN_AFF_+2   score  2.0
        - FNC_+2       score  2.0
        - MIS_+2       score  2.0
      final_score:          8.0
      score_classification: pathogenic
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v16-dysf/classification.json)

    [Download `case-CLN_AFF.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v16-dysf/case-CLN_AFF.json)

## The case capture (CLN_AFF)

The workflow submission that feeds the `CLN_AFF` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA222190",
    "gene": { "symbol": "DYSF", "id": "HGNC:3097", "mde_associated_gene": "DYSF", "transcript": "NM_001130987.2" }
  },
  "mde": { "curie": "MONDO:0015152", "label": "autosomal recessive limb-girdle muscular dystrophy" },
  "moi": "AR",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v16-DYSF-proband-1",
    "family_id": "PVS-v16-DYSF-FAM-1",
    "phenotypes": [ { "name": "Limb-girdle muscle weakness", "code": "HP:0003325" } ],
    "pheno_specificity_for_mde": "SPECIFIC",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "PCT_80_100",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HOM",
    "additional_variant_exists": "FALSE"
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v16-dysf/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v16-dysf/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
