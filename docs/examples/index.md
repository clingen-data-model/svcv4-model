# Examples

Worked SVCv4 `Statement` payloads in [`examples/`][examples-src].
Each file is validated in CI against both the Pydantic model and the
generated JSON Schema.

Run locally:

```sh
uv run python scripts/validate_examples.py
```

## `classification-example-01.json`

A minimal, illustrative `Statement` with two `EvidenceLine`s.

**All values are placeholder content.** The shape is real; the data
is not. Real-world examples — and per-Evidence-Code shapes — will be
added as the SVCv4 Standards and the GA4GH GKS VA-Spec SVCv4
community profile firm up.

The example is structured as follows:

- A **Proposition** with:
    - Subject — a placeholder `VBC` for *BRCA1 c.5096G>A (p.Arg1699Gln)*.
    - Predicate — `is_causal_for`.
    - Object — an `MDE` referencing `MONDO:0007254` (Hereditary breast and ovarian cancer syndrome).
- A `Statement`-level **method** referencing the baseline SVCv4 specification version (placeholder code `svcv4:baseline`).
- Two **Evidence Lines**:
    1. A clinical-observation line referencing four affected individuals with consistent phenotype (placeholder Evidence Code `CLN_AFF_+2`).
    2. A functional-assay line referencing an HDR loss-of-function result (placeholder Evidence Code `FNC_ASY_+2`).
- A final composite score of `4.0` mapping to `likely_pathogenic`.

[See the raw JSON →][example-01-src]

[examples-src]: https://github.com/clingen-data-model/svcv4-model/tree/main/examples
[example-01-src]: https://github.com/clingen-data-model/svcv4-model/blob/main/examples/classification-example-01.json
