# What this project is — and isn't

Three distinct groups make SVCv4 real. Keeping their roles clear is essential to
understanding what this documentation does and does not own.

| Role | Who | What they own |
|---|---|---|
| **The Standards / framework** | **ACMG/AMP/CAP/ClinGen SVCv4 Working Group** | The SVCv4 Summary Table, evidence concepts/codes, workflows, and scoring approach. The framework itself — authoritative, though not yet finalized and still changing to varying degrees. |
| **The data model** | **SVCv4 Standards data-modeling team** (this project; a ClinGen Data Platform WG offshoot) | A standard data model for the SVCv4 data — its structure, codes, and uses — providing semantic interoperability for producing, exchanging, and consuming evidence-based SVCv4-compliant classifications. **Not the author of the Standards.** |
| **The methods / rules** | **ClinGen CSpec** | The workflows/methods that evaluate captured evidence and produce scores (baseline + specialized versions). |

This project works **in coordination with** the SVCv4 Working Group's
developments; it does not define the framework, and it does not implement the
scoring rules. See [Credits](../reference/credits.md) for the people in each
group.

## Classification Model vs Method Model

Within the software, SVCv4 is realised through **two complementary models**. This
repository publishes one of them (the Classification Model); the other (the
Method Model) lives in **ClinGen CSpec**.

| Model | What it represents | Where it is published |
|---|---|---|
| **Classification Model** | The shape of a Variant Pathogenicity Classification — Statements, Propositions, Evidence Lines, and the Evidence Items that support them. *What* a classification is. | **This repository** (as a VA-Spec community profile). |
| **Method Model** | The methods and rules that **evaluate** the evidence items and data points carried by the Classification Model and **produce workflow-specific scores** for the version of SVCv4 being applied (baseline or specialised) to a given (VBC, MDE) curation. | **ClinGen Criteria Specification (CSpec)** — outside this repo and outside GA4GH GKS VA-Spec. |

## What this means in practice

This repository covers **only the Classification Model**. The Method
Model — the methods and rules that evaluate evidence and produce
workflow-specific scores under the chosen SVCv4 specification version
(baseline or VCEP-specialised), plus the gene-disease-MOI scoping that
determines which specialised version applies — is the concern of
**ClinGen CSpec**, where SVCv4 specification documents and APIs will be
published. Both the baseline SVCv4 methods/rules and the forthcoming
VCEP specialisations live in CSpec, not in this repository.

The two models meet through **method codes and evidence codes** that
this repo's Evidence Lines carry as references. The Classification
Model *names* methods and evidence codes; the Method Model in CSpec
*defines* what they do.

## The data flow

```
                                  Classification Model
                                  ┌─────────────────────────────┐
  curator captures ──evidence──▶  │  Evidence Items / data      │
  evidence items                  │  points (inputs to CSpec)   │
                                  └────────────┬────────────────┘
                                               │  provided to
                                               ▼
                                          CSpec methods/rules
                                          (chosen SVCv4 spec. version)
                                               │
                                  ┌────────────▼────────────────┐
                                  │  Evidence Line (result)     │
                                  │   - method/rule code        │
                                  │   - evidence items used     │
                                  │   - score / strength        │
                                  └─────────────────────────────┘
                                  Classification Model
```

The Classification Model is both the **carrier of the inputs**
(Evidence Items) and the **carrier of the outputs** (Evidence Lines
recording method code, evidence used, and the score produced). CSpec is
the **evaluator** in between.

## The baseline is the operative version

The SVCv4 Standard authored by the SVCv4 working group is a
**baseline**. It is designed so that VCEPs and other disease-domain
experts can author **specialised versions** on top of it, in CSpec.

In practice, the community will use the baseline version to define
their VBC-MDE classification processes from the SVCv4 publication
onward, and apply specialised versions only as they become available
for specific gene/disease scopes. The baseline is the operative SVCv4
version until — and wherever — no specialised version applies.

## See also

- [VA-Spec community profile](../reference/va-spec-profile.md) — the
  interoperability layering between VA-Spec and SVCv4.
- [ClinGen CSpec interop](../reference/cspec-interop.md) — how method codes
  resolve into CSpec definitions.
