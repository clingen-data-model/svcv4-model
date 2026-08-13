# MYH7 — hypertrophic cardiomyopathy

!!! info "Practice Variant Set · `PVS-v5-MYH7`"

    **Source:** the *v5: MYH7* tab of the Practice Variant Set spreadsheet ·
    **Repo entry:** [`examples/practice-variant-set/v5-myh7/`][entry] ·
    **Exercises:** POP · CLN_AFF · LOC_PHE · PFD (MIS/SPL).

    This example traces back to a [Practice Variant Set](index.md) entry; the
    entry traces back to the source tab. Values are illustrative — scoring lives
    in [CSpec](../../reference/cspec-interop.md).

A classification of MYH7 `c.4909G>A` (p.Ala1637Thr) against hypertrophic
cardiomyopathy. It draws on four kinds of evidence — population frequency, three
affected probands, and predictive missense/splicing data — which compose to an
illustrative **variant of uncertain significance**.

## The classification, four ways

=== "Prose"

    MYH7 `c.4909G>A` (p.Ala1637Thr) is assessed for whether it **is causal for**
    hypertrophic cardiomyopathy (`MONDO:0005045`), under autosomal-dominant
    inheritance and the baseline SVCv4 specification. Population frequency offers
    no push either way; three affected probands (weighted by how specifically
    their phenotype matches the disease) lend supporting weight; the predictive
    missense signal (REVEL 0.577, plus a different variant at the same codon
    classified VUS) and the absence of a splicing effect are uninformative. The
    lines compose to an illustrative **VUS**.

=== "Narrative"

    The variant being classified (VBC) is MYH7 `c.4909G>A` (p.Ala1637Thr),
    ClinGen Allele ID `CA015454`; the disease/condition (MDE) is hypertrophic
    cardiomyopathy. The curator captured:

    - **Population (POP_FRQ):** prevalence 1 in 200, allelic heterogeneity 0.05,
      genetic heterogeneity 0.40, penetrance 0.40 → `pop_frq_points = 0`.
    - **Affected individuals (CLN_AFF):** three probands — hypertrophic
      cardiomyopathy (`SPECIFIC`), unspecified cardiomyopathy (`CONSISTENT`), and
      dilated cardiomyopathy (`INCONSISTENT`). `pop_frq_points` is carried in as
      an input to this method.
    - **Single-amino-acid change (MIS):** REVEL 0.577, and a same-residue
      comparator variant (ClinVar 525029) classified VUS.
    - **Splicing (SPL):** no predicted impact.

    Each became an Evidence Line; their scores compose to a Statement final score
    → *variant of uncertain significance*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): MYH7 c.4909G>A (p.Ala1637Thr) [CAID:CA015454]
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0005045 (hypertrophic cardiomyopathy)
        qualifiers:           MOI=AD; LoF not an established mechanism
      method:        svcv4:baseline
      evidence_lines:
        - POP_FRQ_+0  (prevalence 1/200; penetrance 0.40; pop_frq_points 0)  score  0
        - CLN_AFF_+1  (3 probands: SPECIFIC / CONSISTENT / INCONSISTENT)     score +1
        - MIS_+0      (REVEL 0.577; same-codon VUS ClinVar:525029)           score  0
        - SPL_+0      (no predicted splicing impact)                         score  0
      final_score:          1.0
      score_classification: variant_of_uncertain_significance
    ```

=== "JSON"

    The rolled-up `Statement`, validated in CI against the Pydantic model and the
    generated JSON Schema:

    [Download `classification.json` →][classification-src]

    The Affected-workflow submission that feeds the `CLN_AFF` line:

    [Download `case-CLN_AFF.json` →][case-src]

## The case capture (CLN_AFF)

Before scoring, the affected proband is captured as a workflow submission —
`WorkflowParameters` (`vbc`/`mde`/`moi`/`pop_frq_points`) plus a nested `case`
holding only the fields the [Affected workflow](../../workflows/hod/cln/cln-aff.md)
applies. This is the hypertrophic-cardiomyopathy proband (the `SPECIFIC` one);
the other two probands follow the same shape and are summarized inside the
`CLN_AFF` evidence line.

```json
{
  "vbc": { "id": "CAID:CA015454",
           "gene": { "symbol": "MYH7", "id": "HGNC:7577", "transcript": "NM_000257.4" } },
  "mde": { "curie": "MONDO:0005045", "label": "hypertrophic cardiomyopathy" },
  "moi": "AD",
  "pop_frq_points": 0,
  "case": {
    "id": "PVS-v5-MYH7-proband-2",
    "family_id": "PVS-v5-MYH7-FAM-2",
    "phenotypes": [ { "name": "Hypertrophic cardiomyopathy", "code": "HP:0001639" } ],
    "pheno_specificity_for_mde": "SPECIFIC",
    "testing": { "method": "Panel", "covers_all_genes_relevant_to_mde": "TRUE" },
    "age_matched_penetrance": "LT_80",
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET",
    "additional_variant_exists": "FALSE"
  }
}
```

## What is illustrative vs. representative

- **POP** has no Case-model workflow of its own, so its inputs live as evidence
  data on the `POP_FRQ` line rather than a `case-*.json` submission. Only the
  capped `pop_frq_points` is carried today; the raw POP_FRQ score (which the
  affecteds/de-novo `≤ -3.0` gate uses) and the DAF Threshold are modeled later,
  with the POP_FRQ method.
- **LOC_PHE** is applicable (probands are counted) but is not scored here — the
  tab lacks the gene-specificity and diagnostic-yield inputs the method needs.
- **PM5-type support** is not a clinical line: it is a single-amino-acid-change
  (`MIS`) datum, and the non-VBC comparator allele rides along as one of that
  workflow's evidence items. Because the comparator is a VUS, it carries little
  or no positive weight.

[entry]: https://github.com/clingen-data-model/svcv4-model/tree/main/examples/practice-variant-set/v5-myh7
[classification-src]: https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v5-myh7/classification.json
[case-src]: https://github.com/clingen-data-model/svcv4-model/blob/main/examples/practice-variant-set/v5-myh7/case-CLN_AFF.json
