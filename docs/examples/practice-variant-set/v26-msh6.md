# MSH6 c.107C>T (p.Ala36Val) — Lynch syndrome / hereditary non-polyposis colorectal cancer

!!! info "Practice Variant Set · `PVS-v26-MSH6`"

    **Source:** [source tab ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=65997805#gid=65997805) · **Repo entry:** [`examples/practice-variant-set/v26-msh6/`](https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v26-msh6) ·
    **Exercises:** POP_FRQ · CLN_ALTV · MIS.

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in CSpec.

An SVCv4 classification of MSH6 c.107C>T (p.Ala36Val) against Lynch syndrome / hereditary non-polyposis colorectal cancer, drawn from the
`PVS-v26-MSH6` Practice Variant Set entry.

## The classification, four ways

=== "Prose"

    MSH6 c.107C>T (p.Ala36Val) is assessed for whether it **is causal for** Lynch syndrome / hereditary non-polyposis colorectal cancer (`MONDO:0005835`), under AD inheritance, under the baseline SVCv4 specification. 3 lines of evidence — population allele frequency, affected with an alternate cause — variant, single-amino-acid change — compose to an illustrative **variant of uncertain significance**.

=== "Narrative"

    The variant being classified (VBC) is MSH6 c.107C>T (p.Ala36Val); the disease/condition (MDE) is Lynch syndrome / hereditary non-polyposis colorectal cancer. The curator captured:

    - **Population allele frequency (POP_FRQ)** (`POP_FRQ`, score 0.0) — Population frequency (illustrative).
    - **Affected with an alternate cause** (`CLN_ALTV`, score -1.0) — Alternate cause — variant (illustrative).
    - **Single-amino-acid change (MIS)** (`MIS`, score 0.0) — Predictive missense evidence (PFD, illustrative).
      - `MIS_PRD` (score 0.0) — In-silico predictive missense assessment.
        - `MIS_PRD_INIT_BAYESDEL` (score 0.0) · *provisional* — BayesDel -0.20 is mildly benign-leaning; no same-codon informative variants.

    Each became an Evidence Line; their scores compose to a Statement final score of 0.0 → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subject (VBC): MSH6 c.107C>T (p.Ala36Val)
        predicate:     is_causal_for
        object (MDE):  MONDO:0005835 (Lynch syndrome / hereditary non-polyposis colorectal cancer)
        qualifiers:    moi=AD; note=Loss of function is an established disease mechanism.
      specifiedBy:   svcv4:baseline
      hasEvidenceLines:
        - POP_FRQ                  score   0.0
        - CLN_ALTV                 score  -1.0
        - MIS                      score   0.0
          - MIS_PRD                  score   0.0
            - MIS_PRD_INIT_BAYESDEL (prov) score   0.0
      score:         0.0
      outcome:       variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI:

    [Download `classification.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v26-msh6/classification.json)

    [Download `case-CLN_ALTV.json` →](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v26-msh6/case-CLN_ALTV.json)

## The case capture (CLN_ALTV)

The workflow submission that feeds the `CLN_ALTV` line — `WorkflowParameters`
(`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`:

```json
{
  "vbc": {
    "id": "CAID:CA007963",
    "gene": { "symbol": "MSH6", "id": "HGNC:7329", "mde_associated_gene": "MSH6", "transcript": "NM_000179.3" }
  },
  "mde": { "curie": "MONDO:0005835", "label": "Lynch syndrome / hereditary non-polyposis colorectal cancer" },
  "moi": "AD",
  "case": {
    "id": "PVS-v26-MSH6-case-1",
    "pheno_severity": "MONO_EQ_EXPECTED",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "TRUE",
    "additional_variants": [
      {
        "id": "CAID:MSH6-c.3202C>T-p.Arg1068Ter",
        "zygosity": "HET",
        "phase_in_ref_to_vbc": "TRANS",
        "phase_confidence": "HIGH",
        "classification": "P"
      }
    ]
  }
}
```

## Provenance & caveats

- Capture and the field-by-field mapping (including open questions) live in the
  repo entry: [`source.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v26-msh6/source.md), [`mapping.md`](https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v26-msh6/mapping.md).
- Scores and the classification are **illustrative** — the arithmetic is CSpec's.
- Only the primary workflow is encoded so far; other applicable workflows are
  noted in `mapping.md` and will be added as those workflows are developed.
