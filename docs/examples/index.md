# Examples

Worked SVCv4 `Statement` payloads, shown four ways — read them as **prose**, as a
curator's **narrative**, as a **semi-structured** outline, or as downloadable
**JSON**. Each JSON file is validated in CI against both the Pydantic model and
the generated JSON Schema:

```sh
uv run python scripts/validate_examples.py
```

!!! note "Placeholder content"

    The shapes are real; the data is illustrative. Real-world examples — and
    per-Evidence-Code shapes — will be added as the SVCv4 Standards and the
    VA-Spec SVCv4 community profile firm up.

## Example 01 — a Likely Pathogenic classification

=== "Prose"

    A classification that *BRCA1* c.5096G>A (p.Arg1699Gln) **is causal for**
    Hereditary breast and ovarian cancer syndrome (`MONDO:0007254`), evaluated
    under the baseline SVCv4 specification. Two lines of evidence — a clinical
    observation of affected individuals and a functional assay — combine to a
    final score of **4.0**, i.e. **Likely Pathogenic**.

=== "Narrative"

    The variant being considered (VBC) is *BRCA1* c.5096G>A (p.Arg1699Gln); the
    disease/condition (MDE) is Hereditary breast and ovarian cancer syndrome.
    The curator captured two Evidence Items: four affected individuals with a
    consistent phenotype (Evidence Code `CLN_AFF_+2`), and an HDR
    loss-of-function functional result (`FNC_ASY_+2`). Each became an Evidence
    Line; their scores compose to a Statement final score of 4.0 →
    *likely pathogenic*.

=== "Semi-structured"

    ```text
    Statement
      proposition:
        subjectVariant (VBC): BRCA1 c.5096G>A (p.Arg1699Gln)
        predicate:            is_causal_for
        objectCondition (MDE): MONDO:0007254
      method:        svcv4:baseline
      evidence_lines:
        - CLN_AFF_+2  (4 affected, consistent phenotype)   score +2
        - FNC_ASY_+2  (HDR loss-of-function assay)          score +2
      final_score:          4.0
      score_classification: likely_pathogenic
    ```

=== "JSON"

    A minimal, illustrative `Statement` with two `EvidenceLine`s.

    [Download `classification-example-01.json` →][example-01-src]

    See [all example files][examples-src] in the repository.

[examples-src]: https://github.com/clingen-data-model/svcv4-model/tree/main/examples
[example-01-src]: https://github.com/clingen-data-model/svcv4-model/blob/main/examples/classification-example-01.json
