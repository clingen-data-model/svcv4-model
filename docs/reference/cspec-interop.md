# ClinGen CSpec interop

ClinGen's **Criteria Specification (CSpec)** system houses the
**Method Model** for SVCv4 — the methods, rules, and workflows that
evaluate evidence and produce scores. CSpec sits **outside** this
repository and **outside** GA4GH GKS VA-Spec.

The Classification Model published here only **names** CSpec methods;
it never defines them. Every place this model carries a method or
evidence code, it is a reference into CSpec.

## Where references appear

| Where | Slot | Purpose |
|---|---|---|
| `Statement` | `method` | Identifies the **applied SVCv4 specification version** — baseline SVCv4 or a VCEP-specialised version selected via gene-disease-MOI scoping. |
| `EvidenceLine` | `method` | Identifies the **specific CSpec method or rule** whose invocation produced the Evidence Line's score. |
| `EvidenceLine` | `code` | Optional Evidence Code or method-code mirror, where useful for disambiguation. |

`Method.code` is an opaque CURIE-style string for now; the precise
scheme that CSpec will issue is TBD.

## Both baseline and specialised versions live in CSpec

- **Baseline SVCv4** methods and rules — authored by the SVCv4 working
  group. The baseline is the operative SVCv4 version from publication
  onward.
- **VCEP specialisations** — gene/disease-scoped customisations
  authored on top of the baseline by ClinGen Variant Curation Expert
  Panels.

Specialisations are applied **only as they become available** for the
gene/disease in scope; otherwise the baseline is used.

## SVCv4 deliverables outside this repo

- The SVCv4 Standards publication (target: October 2026,
  *Genetics in Medicine*).
- The SVCv4 specification model in the **CSpec Registry** — public API
  and documentation.

## See also

- [What this project is — and isn't](../overview/scope.md)
- [GA4GH GKS interop](gks-interop.md)
