# Evidence Lines & Items

The Classification Model carries two related but distinct entities:

- **[`EvidenceItem`][svcv4_model.EvidenceItem]** — a single structured
  datum captured by the curator. Evidence Items are **inputs** that
  the Classification Model provides to CSpec methods/rules under the
  chosen specification version.
- **[`EvidenceLine`][svcv4_model.EvidenceLine]** — the **result** of
  invoking a CSpec method/rule on those Evidence Items. It records the
  method code that was invoked, the Evidence Items used, and the score
  (and optional strength) that was produced.

> *Any process, rule, or method that produces a score maps to an
> Evidence Line.* The method's **definition** lives in CSpec; only the
> invocation **result** lives here.

## Shape

```text
EvidenceLine                           EvidenceItem
 ├── method: Method (→ CSpec)           ├── id?: str
 ├── code?: str                         ├── type?: str
 ├── evidence: list[EvidenceItem]       ├── data: dict[str, Any]
 ├── score: float                       ├── references: list[str]
 ├── strength_direction?: str           └── description?: str
 ├── score_classification?: VPC
 ├── contribution?: float
 └── description?: str
```

(`VPC` = [`VariantPathogenicityClassification`][svcv4_model.VariantPathogenicityClassification].)

## How they relate to CSpec

```
EvidenceItem(s)        ──▶  CSpec method/rule  ──▶  EvidenceLine
(curator-captured inputs)   (defined+applied in       (records method,
                             CSpec for the chosen      evidence used,
                             specification version)    and score produced)
```

The same Evidence Item can be used as input to more than one CSpec
method/rule, producing more than one Evidence Line. Each Evidence Line
records the subset of items it actually consumed.

## VA-Spec alias

VA-Spec also uses the umbrella name **`EvidenceData`** for what this
model calls `EvidenceItem`. The two are the same class in the Python
package:

```python
from svcv4_model import EvidenceItem, EvidenceData
assert EvidenceData is EvidenceItem
```

## See also

- [Statement & Proposition](statement-and-proposition.md)
- [Summary Table](summary-table.md) — how Evidence Codes (which CSpec
  workflows reference) organise into Categories and Concepts.
- Model reference: [`EvidenceLine`][svcv4_model.EvidenceLine],
  [`EvidenceItem`][svcv4_model.EvidenceItem].
