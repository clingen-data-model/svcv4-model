# Specialization & the assessment registry

Every scored branch of a workflow is an **assessment**. Its stable name is the
`methodType` carried on the `specifiedBy` (`Method`) of an evidence-line
`Statement`. The baseline SVCv4 framework registers each assessment once, with a
baseline configuration; a **specialization** (for a gene, VCEP, or disease area)
reuses the *same* `methodType` but registers its own **configuration** under a
distinct, namespaced id.

## The two identifiers

| Field | Purpose | Example |
|---|---|---|
| `specifiedBy.methodType` | *What kind of rule this is* — stable across baseline and every specialization; this is what makes results **comparable**. | `insilico-predictor-assessment` |
| `specifiedBy.id` | *Which configured ruleset actually ran* — namespaced + versioned; this is what makes results **reproducible**. | `svcv4:MIS_PRD_INIT_REVEL:1.0` |

The id scheme is **`svcv4:<CODE>:<version>` (baseline) or `svcv4-<scope>:<CODE>:<version>`**. Scope is `baseline`
or a specialization scope (e.g. `gene-MYH7`, `vcep-cardiomyopathy`). All scopes
live under the `svcv4` registry umbrella.

## Worked example — same evidence, two configurations

A missense VBC in *MYH7* with an in-silico predictor **raw score of 0.91**. The
baseline predictor calibration reaches `+4.0` only at `≥ 0.932`, so 0.91 lands in
the next band down; the *MYH7* specialization was re-calibrated for the gene and
reaches `+4.0` at `≥ 0.90`. Same evidence item, same assessment — different
configured threshold, different score.

=== "Baseline"

    ```jsonc
    {
      "type": "Statement",
      "code": "MIS_PRD_INIT_REVEL",
      "specifiedBy": {
        "id": "svcv4:MIS_PRD_INIT_REVEL:1.0",
        "methodType": "insilico-predictor-assessment",
        "version": "1.0"
      },
      "score": 3.0,
      "direction": "supports",
      "outcome": "MIS_PRD_INIT_REVEL_+3",
      "hasEvidenceItems": [
        { "type": "DataItem", "subtype": "computational_prediction",
          "value": { "predictor": "REVEL", "raw_score": 0.91 } }
      ]
    }
    ```

=== "MYH7 specialization"

    ```jsonc
    {
      "type": "Statement",
      "code": "MIS_PRD_INIT_REVEL",
      "specifiedBy": {
        "id": "svcv4-gene-MYH7:MIS_PRD_INIT_REVEL:1.0",
        "methodType": "insilico-predictor-assessment",
        "version": "1.0"
      },
      "score": 4.0,
      "direction": "supports",
      "outcome": "MIS_PRD_INIT_REVEL_+4",
      "hasEvidenceItems": [
        { "type": "DataItem", "subtype": "computational_prediction",
          "value": { "predictor": "REVEL(MYH7-recalibrated)", "raw_score": 0.91 } }
      ]
    }
    ```

Both lines share `methodType` (a reader can compare them as the same kind of
assessment); their `specifiedBy.id` differs, and each id resolves in the registry
to the exact configuration — including the calibration thresholds — that produced
the score.

## What a specialization may reconfigure

The registry records, per assessment type, which **parameters** a configuration
may set. A specialization overrides those parameters within the compliance limits
of the SVCv4 framework; it does **not** mint new codes. Examples:

| Assessment (`methodType`) | Reconfigurable parameters |
|---|---|
| `insilico-predictor-assessment` | predictor · calibration thresholds |
| `mechanism-exon-relevance-assessment` | matrix fractions · gene-disease-validity gate |
| `informative-variants-assessment` | point values · relatedness rule · added granularity |
| `population-frequency-assessment` | fold thresholds & point tiers |

## In the model

The registry lives in `svcv4_model.assessment`:
`AssessmentType` (the pattern) and `Ruleset` (a pathway node),
with `make_ruleset_id` / `parse_ruleset_id` / `resolve` / `children` helpers. Baseline rulesets are seeded for the whole method tree; specializations override
individual nodes by id.

## Top-level wiring

The whole method is a single root ruleset — `svcv4:SVCV4:1.0` — that composes the seven code families (POP, CLN, LOC, MIS, NUL, CDS, SPL). The **top-level classification `Statement`** carries `specifiedBy.id = svcv4:SVCV4:1.0` (the applied SVCv4 method); each **evidence-line `Statement`** carries `specifiedBy.id` = its own ruleset node (e.g. `svcv4:MIS_PRD_EXON:1.0`). A specialization swaps the method root's version and/or individual node ids without changing any `methodType`.
