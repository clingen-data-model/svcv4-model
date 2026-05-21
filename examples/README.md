# Examples

JSON fixtures showing complete SVCv4 `Statement` payloads. Each file
validates against the model in two ways during CI:

- it round-trips through `svcv4_model.Statement.model_validate(...)`, and
- it validates against the generated `schemas/json/Statement.schema.json`.

Run the validation locally:

```sh
uv run python scripts/validate_examples.py
```

## Files

| File | What it illustrates |
|---|---|
| [`classification-example-01.json`](classification-example-01.json) | A minimal, illustrative `Statement` with two `EvidenceLine`s (one clinical observation, one functional assay). All values are **placeholder content** — the shape is real; the data is not. |

These examples will grow and gain fidelity as the SVCv4 Standards and
the GA4GH GKS VA-Spec SVCv4 community profile firm up. Today they
exist primarily to exercise the scaffold and to give downstream
implementers a concrete target to test against.
