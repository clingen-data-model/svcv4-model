# svcv4-model

> A reference for the **Classification Model** of the forthcoming **ACMG/AMP/CAP/ClinGen Sequence Variant Classification v4 (SVCv4) Standards**, expressed as a **GA4GH GKS VA-Spec community profile**.

**Status: early development.** The SVCv4 Standards (jointly sponsored by ACMG, AMP, CAP, and ClinGen) are being drafted and piloted by the genomic-medicine community, with publication targeted for **October 2026 in *Genetics in Medicine* (GIM)**. This repository will publish the engineering-facing data-model documentation that accompanies the guidelines' release.

---

## Scope: the Classification Model only

SVCv4 is realised in software through **two complementary models**:

| Model | What it represents | Where it is published |
|---|---|---|
| **Classification Model** | The shape of a Variant Pathogenicity Classification — Statements, Propositions, Evidence Lines, and the Evidence Items that support them. *What* a classification is. | **This repository** (as a VA-Spec community profile). |
| **Method Model** | The methods and rules that **evaluate** the evidence supplied by a curator and **produce workflow-specific scores** for the version of SVCv4 being applied to a given (VBC, MDE) curation. Encompasses both the baseline SVCv4 methods/rules and the forthcoming domain-specific specialised versions. | **ClinGen Criteria Specification (CSpec)** — outside this repo and outside GA4GH GKS VA-Spec. |

This repository covers **only the Classification Model**. The Method Model — the methods and rules that evaluate the evidence captured during a curation and produce workflow-specific scores for the version of SVCv4 being applied (baseline or VCEP-specialised), along with the gene-disease-MOI scoping that determines which specialised version applies — is the concern of **ClinGen CSpec**, where SVCv4 specification documents and APIs will be published. Both the baseline SVCv4 methods/rules and the forthcoming VCEP specialisations live in CSpec, not in this repository.

The two models meet through **method codes and evidence codes** that this repo's Evidence Lines carry as references. The Classification Model *names* methods and evidence codes; the Method Model in CSpec *defines* what they do.

## Foundation: GA4GH GKS VA-Spec

All structural choices in this repository are grounded in the **Global Alliance for Genomics and Health (GA4GH) Genomic Knowledge Standards (GKS)** workstream. ClinGen is a GA4GH driver project.

The primary GKS dependency for this repo is the **Variant Annotation Specification (VA-Spec)** (released v1.0). VA-Spec provides a baseline set of classes — `Statement`, `Proposition`, `EvidenceLine`, `InformationEntity`, `EvidenceData` — for representing evidence-based scientific assertions about genomic variants. **Community profiles** layer additional constraints on top of those baseline classes to enforce alignment with the terminology conventions of a specific community guideline.

This repository authors the **VA-Spec SVCv4 Community Profile**: the SVCv4-specific shape on top of the VA-Spec baseline. That profile is what enables consistent representation, comparison, and processing of SVCv4 classifications with standardised tooling across organisations.

Supporting GKS schemas:

- [**VRS** (Variation Representation Specification)](https://vrs.ga4gh.org/) — v2.0. Used to describe the VBC (the variant under consideration).
- [**Cat-VRS** (Categorical Variation Representation)](https://cat-vrs.ga4gh.org/) — v1.0. Used where the variant is described categorically.
- **gks-core** — common identifier, CURIE, and provenance constructs shared across GKS.

ClinGen's Evidence Repository (ERepo) and its JSON-LD SEPIO implementation informed VA-Spec; this project further informs the SVCv4 community profile being layered on top of VA-Spec.

## The SVCv4 Standard is a baseline by design

The SVCv4 Standard authored by the SVCv4 working group is intentionally a **baseline**. It is designed so that disease-domain experts — including **ClinGen Variant Curation Expert Panels (VCEPs)** — can author **specialised versions** on top of it:

- Customised **methods and scoring rules** within workflows.
- **Gene/disease scope** (gene-disease-MOI) for which a specialisation is applicable.

These specialisations do not exist yet — the baseline itself is still being finalised — but the design accounts for them. **Both the baseline SVCv4 methods/rules and the forthcoming VCEP specialisations live in ClinGen CSpec** (the Method Model side), not in this repository.

So there are two distinct layerings at play; do not confuse them:

1. **Interoperability layering** — VA-Spec baseline classes → **SVCv4 community profile** (authored here).
2. **Domain layering** — SVCv4 Standard baseline → **VCEP specialisations** (authored in CSpec).

## Conceptual model (VA-Spec terminology)

The Classification Model is expressed using VA-Spec's canonical entity names:

- A **Statement** carries a **Proposition** and a final score, plus attributes for strength-direction, score-classification, method (reference), contribution, and a collection of Evidence Lines.
- A **Proposition** is structured as **SPOQ**: **S**ubject (the **VBC** — Variant Being Considered, expressed as a VRS Variation), **P**redicate (the asserted relationship), **O**bject (the **MDE** — Mendelian Disease Entity), and **Q**ualifier(s).
- A **Variant Pathogenicity Classification** is the categorical classification (a position on the Benign ↔ Pathogenic spectrum) produced by the Statement's score.
- An **Evidence Line** carries its score, the evidence items that support it, optional evidence/method code references, an optional strength-direction, the method (reference), and contribution. Each Evidence Line groups one or more Evidence Items.
- An **Evidence Item / Evidence Data** is a single structured datum captured to support a score.

> *Any process, rule, or method that produces a score maps to a VA-Spec Evidence Line.* When a CSpec workflow evaluates evidence and produces a score for the SVCv4 version being applied, that result surfaces in the Classification Model as an Evidence Line. The workflow itself — its rules, scoring logic, and version selection — lives in CSpec; only the resulting Evidence Line (with its score and supporting evidence) lives here.

### The user-facing summary table

Curators and scientists engage with SVCv4 through a **Summary Table** that organises evidence lines top-down as:

- **Evidence Categories** (e.g., Human Observational Data, Variant Impact Data)
- **Evidence Concepts**
- **Evidence Codes** — each Evidence Code is the **jumping-off point** for a workflow (in CSpec) that walks a curator through gathering evidence and computing the score for a specific (VBC, MDE) classification.

These terms are canonical SVCv4 vocabulary and appear throughout the guidelines. This repository's data model represents the classifications and evidence lines produced via that summary table; the CSpec system will represent the workflows themselves.

## What this repository will be

A single integrated reference site that combines:

- **Pydantic data models** — the Python source of truth for the SVCv4 Classification Model as a VA-Spec community profile.
- **JSON Schemas** — emitted automatically from the Pydantic models so any language or toolchain can validate and exchange SVCv4 classifications.
- **Worked examples** — concrete classifications of representative (VBC, MDE) pairs that downstream implementers can test against.
- **Narrative documentation** — concept guides explaining the model, the VA-Spec layering, the Classification ↔ Method-Model boundary, and the SVCv4 baseline + specialisation design.

The site will be published to the public web alongside (or before) the SVCv4 guideline release in October 2026, and tracks the draft **GA4GH VA Community Profile** for SVCv4 (JSON Schema and documentation, expected after GA4GH review in 2026).

## FAIR posture

This project prioritises the **Interoperability** and **Reusability** dimensions of the [FAIR data principles](https://www.go-fair.org/fair-principles/):

- **Interoperability** — VA-Spec-grounded schemas, machine-readable JSON Schemas, stable identifiers.
- **Reusability** — open licence, versioned models, worked examples, clear documentation aimed at implementers.

## Audience

Software engineers, bioinformaticians, and platform teams in:

- Clinical diagnostic laboratories implementing SVCv4 in production pipelines.
- Translational genomics research groups and consortia.
- Knowledge-base curators exchanging variant classifications.
- Tool builders producing user interfaces, decision support, or automated curation systems.

This is engineering reference documentation. For *clinical* guidance on applying SVCv4, refer to the forthcoming SVCv4 guideline publication itself. For the **method definitions and workflows** that compute SVCv4 scores, refer to **ClinGen CSpec**.

## Status & roadmap

**Now (May 2026):**

- This README.
- The scaffold design document at [`docs/plans/2026-05-19-initial-scaffold.md`](docs/plans/2026-05-19-initial-scaffold.md) — repository structure, tooling choices, VA-Spec interop strategy, and verification approach.

**Next:**

- Python package skeleton (`src/svcv4_model/`) with VA-Spec-aligned Pydantic classes (`Statement`, `Proposition`, `EvidenceLine`, `EvidenceItem`, `VariantPathogenicityClassification`, `VBC`, `MDE`).
- JSON Schema export pipeline.
- MkDocs Material site with auto-generated model reference.
- First worked example validated in CI.

**Later (tracking the SVCv4 publication trajectory):**

- Fill in real SVCv4 Evidence Category / Concept / Code references as the Summary Table stabilises.
- Publish drafts of the VA-Spec SVCv4 community profile in step with GA4GH review.
- Synchronise with the SVCv4 publication (~October 2026, *Genetics in Medicine*).

## Contributors

This work is produced by the **SVCv4 Standards data modeling team**, a task force offshoot of the ClinGen Data Platform Working Group, meeting weekly since July 2024.

**Key contributors:**

- Alicia Byrne, PhD — Broad Institute
- Larry Babb — Broad Institute
- Christine Preston, PhD
- Neethu Shah — ClinGen

**Contributors:**

- Matt Wright, PhD
- Gloria Cheung
- Bryan Wulf
- Mark Mandell
- Hannah Dziadzio
- Liam Mulhall

The VA-Spec SVCv4 community profile work is conducted in collaboration with the GA4GH GKS VA-Spec authors (Matt Brush, Alex Wagner, Larry Babb).

## Glossary

| Term | Meaning |
|---|---|
| **SVCv4** | Sequence Variant Classification v4 — the ACMG/AMP/CAP/ClinGen joint Technical Standard, succeeding the 2015 Richards et al. guidelines (SVCv3). Points-based; replaces v3's strength-categories + combining-rules approach. |
| **VBC** | Variant Being Considered — the specific germline variant under evaluation; expressed as a VRS Variation. |
| **MDE** | Mendelian Disease Entity — the disease the VBC is being assessed against. |
| **Classification Model** | The shape of a classification (Statements, Propositions, Evidence Lines, Evidence Items). Authored by this repo as a VA-Spec community profile. |
| **Method Model** | The definitions of methods, workflows, criteria, scoring rules. Authored in ClinGen CSpec; not in this repo, not in VA-Spec. |
| **Statement / Proposition / Evidence Line / Evidence Item** | VA-Spec core entities; see the conceptual-model section above. |
| **SPOQ** | Subject / Predicate / Object / Qualifier — the structure of a VA-Spec Proposition. |
| **Evidence Category / Concept / Code** | Canonical SVCv4 vocabulary for the user-facing Summary Table; the Evidence Code is the jumping-off point for a workflow. |
| **Workflow** | A prescriptive procedure (defined and applied in CSpec) for evaluating the evidence captured under an Evidence Code and producing a score for the version of SVCv4 being applied. Each workflow's result surfaces in the Classification Model as an Evidence Line. |
| **CSpec** | ClinGen Criteria Specification system — registry and APIs where SVCv4 methods, workflows, and VCEP specialisations are published. |
| **VCEP** | Variant Curation Expert Panel (ClinGen). Authors specialised SVCv4 method definitions in CSpec. |
| **Community Profile (VA-Spec)** | A layer of additional constraints on top of VA-Spec's baseline classes to enforce a community's terminology and conventions. |
| **VA-Spec / VRS / Cat-VRS / gks-core** | GA4GH GKS sub-schemas. VA-Spec is this repo's primary dependency. |
| **CSpec / ERepo / SEPIO** | ClinGen Criteria Specification; ClinGen Evidence Repository; Scientific Evidence and Provenance Information Ontology. SEPIO informed VA-Spec. |
| **GA4GH** | Global Alliance for Genomics and Health. |
| **GKS** | Genomic Knowledge Standards — a GA4GH workstream. |
| **GIM** | *Genetics in Medicine*, the journal where SVCv4 will publish. |
| **FAIR** | Findable, Accessible, Interoperable, Reusable. |

## Contributing

Contribution guidelines will land alongside the first scaffolded code drop. Until then, please open an issue to discuss any proposed direction.

## Licence

Code is licensed under the terms in [`LICENSE`](LICENSE). Documentation content is intended to be published under a permissive open licence; final licence terms for narrative content will be confirmed before the first published release of the site.
