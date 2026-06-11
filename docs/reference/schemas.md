# JSON Schemas

!!! warning "Advisory — in flux"

    These schemas are generated from the computational data model, which is
    still evolving alongside the SVCv4 Standards. They **track** the (evolving)
    SVCv4 Standards authored by the SVCv4 Working Group — they are not themselves
    the Standard. Treat as advisory while the model stabilizes.

The Pydantic data model emits JSON Schemas via
`pydantic.BaseModel.model_json_schema()`. The committed schemas in
[`schemas/json/`][schemas-src] are the source of truth for downstream
consumers; CI regenerates them on every PR and fails if the committed
copies drift from the model.

Regenerate locally:

```sh
uv run python scripts/export_schemas.py
```

Validate every example under `examples/` against the schemas:

```sh
uv run python scripts/validate_examples.py
```

## Schemas published in this repository

| Class | File | Source |
|---|---|---|
| `Statement` | [`Statement.schema.json`][stmt] | [`statement.py`][src-statement] |
| `Proposition` | [`Proposition.schema.json`][prop] | [`proposition.py`][src-proposition] |
| `EvidenceLine` | [`EvidenceLine.schema.json`][el] | [`evidence_line.py`][src-evidence-line] |
| `EvidenceItem` | [`EvidenceItem.schema.json`][ei] | [`evidence_item.py`][src-evidence-item] |
| `Method` | [`Method.schema.json`][meth] | [`method.py`][src-method] |
| `VBC` | [`VBC.schema.json`][vbc] | [`inputs.py`][src-inputs] |
| `MDE` | [`MDE.schema.json`][mde] | [`inputs.py`][src-inputs] |

The `VariantPathogenicityClassification` enum appears inline within
the schemas that reference it.

[schemas-src]: https://github.com/clingen-data-model/svcv4-model/tree/main/schemas/json
[stmt]: https://github.com/clingen-data-model/svcv4-model/blob/main/schemas/json/Statement.schema.json
[prop]: https://github.com/clingen-data-model/svcv4-model/blob/main/schemas/json/Proposition.schema.json
[el]: https://github.com/clingen-data-model/svcv4-model/blob/main/schemas/json/EvidenceLine.schema.json
[ei]: https://github.com/clingen-data-model/svcv4-model/blob/main/schemas/json/EvidenceItem.schema.json
[meth]: https://github.com/clingen-data-model/svcv4-model/blob/main/schemas/json/Method.schema.json
[vbc]: https://github.com/clingen-data-model/svcv4-model/blob/main/schemas/json/VBC.schema.json
[mde]: https://github.com/clingen-data-model/svcv4-model/blob/main/schemas/json/MDE.schema.json
[src-statement]: https://github.com/clingen-data-model/svcv4-model/blob/main/src/svcv4_model/statement.py
[src-proposition]: https://github.com/clingen-data-model/svcv4-model/blob/main/src/svcv4_model/proposition.py
[src-evidence-line]: https://github.com/clingen-data-model/svcv4-model/blob/main/src/svcv4_model/evidence_line.py
[src-evidence-item]: https://github.com/clingen-data-model/svcv4-model/blob/main/src/svcv4_model/evidence_item.py
[src-method]: https://github.com/clingen-data-model/svcv4-model/blob/main/src/svcv4_model/method.py
[src-inputs]: https://github.com/clingen-data-model/svcv4-model/blob/main/src/svcv4_model/inputs.py
