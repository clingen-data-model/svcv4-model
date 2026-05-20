# svcv4-model

> Computational reference data model for the **Sequence Variant Classification v4 (SVCv4)** community guidelines.

**Status: early development.** The SVCv4 guidelines are being drafted and piloted by the genomic-medicine community; this repository will publish the engineering-facing data-model documentation that accompanies the guidelines' eventual release.

---

## What this repository will be

A single integrated reference site that documents how to represent, exchange, and reason about **SVCv4 classifications** in software. It will combine:

- **Pydantic data models** — the Python source of truth for SVCv4 classifications, evidence lines, workflows, evidence items, and Bayesian scoring.
- **JSON Schemas** — emitted automatically from the Pydantic models so any language or toolchain can validate and exchange SVCv4 data.
- **Worked examples** — concrete classifications of representative `(VBC, MDE)` pairs that downstream implementers can test against.
- **Narrative documentation** — concept guides explaining the evidence hierarchy, score composition, and where SVCv4 builds on the GA4GH GKS foundation.

The site will be published to the public web alongside (or before) the SVCv4 guideline release later in 2026.

## What SVCv4 is

The **Sequence Variant Classification, version 4** guidelines are the next-generation, expert-authored standard for evaluating whether a germline **Variant Being Considered (VBC)** is causal for a specified **Mendelian Disease Entity (MDE)**. SVCv4 organises the available evidence into a hierarchy of **Evidence Lines → Workflows → Evidence Items**, scores each evidence item, rolls those scores into a final **Bayesian score**, and maps that score to a position on the **Benign ↔ Pathogenic** classification spectrum. The guidelines are being designed and piloted by the international clinical-genomics community and target publication later in 2026.

This repository does not author the SVCv4 guidelines themselves — it provides the **computational representation** of them, so the standard can be implemented, exchanged, and automated by the community.

## Foundation: GA4GH GKS

All structural choices in this repository are grounded in the **Global Alliance for Genomics and Health (GA4GH) Genomic Knowledge Standards (GKS)** workstream. SVCv4 data references — rather than redefines — existing GKS schemas:

- [**VRS** (Variation Representation Specification)](https://vrs.ga4gh.org/) — used to describe the VBC.
- [**Cat-VRS** (Categorical Variation Representation)](https://cat-vrs.ga4gh.org/) — used where the variant is described categorically.
- [**VA-Spec** (Variant Annotation Specification)](https://va-spec.ga4gh.org/) — used for related annotations.
- **gks-core** — common identifier, CURIE, and provenance constructs shared across GKS.

By layering on top of GKS rather than around it, SVCv4 data produced from these models is interoperable with the broader genomic-knowledge ecosystem out of the box.

## FAIR posture

This project prioritises the **Interoperability** and **Reusability** dimensions of the [FAIR data principles](https://www.go-fair.org/fair-principles/):

- **Interoperability** — shared GKS-grounded schemas, machine-readable JSON Schemas, stable identifiers.
- **Reusability** — open licence, versioned models, worked examples, clear documentation aimed at implementers.

## Audience

Software engineers, bioinformaticians, and platform teams in:

- Clinical diagnostic laboratories implementing SVCv4 in production pipelines.
- Translational genomics research groups and consortia.
- Knowledge-base curators exchanging variant classifications.
- Tool builders producing user interfaces, decision support, or automated curation systems.

This is engineering reference documentation. For *clinical* guidance on applying SVCv4, refer to the forthcoming SVCv4 guideline publication itself.

## Status & roadmap

**Now (this initial PR, May 2026):**

- This README.
- The first design document at [`docs/plans/2026-05-19-initial-scaffold.md`](docs/plans/2026-05-19-initial-scaffold.md) — the intended repository structure, tooling choices, GKS interop strategy, and verification approach.

**Next:**

- Python package skeleton (`src/svcv4_model/`) with placeholder Pydantic classes for `Classification`, `EvidenceLine`, `Workflow`, `EvidenceItem`, `BayesianScore`, `VBC`, and `MDE`.
- JSON Schema export pipeline.
- MkDocs Material site with auto-generated model reference.
- First worked example validated in CI.

**Later:**

- Fill in real SVCv4 evidence-line, workflow, and evidence-item definitions as the guidelines stabilise.
- Score-composition / Bayesian-rollup logic.
- Cat-VRS and VA-Spec integration where the model requires them.

See the [initial scaffold design](docs/plans/2026-05-19-initial-scaffold.md) for the planned directory layout and tooling rationale.

## Glossary

| Term | Meaning |
|---|---|
| **SVCv4** | Sequence Variant Classification, version 4 (forthcoming community guidelines). |
| **VBC** | Variant Being Considered — the specific germline variant under evaluation. |
| **MDE** | Mendelian Disease Entity — the disease the VBC is being assessed against. |
| **Evidence Line** | A top-level category of evidence (e.g. population, functional, computational). |
| **Workflow** | A leaf-level procedure that gathers evidence items using a defined method. |
| **Evidence Item** | A single structured datum contributing a score under a workflow. |
| **Bayesian score** | The composed numeric score produced by rolling up evidence-item scores. |
| **GA4GH** | Global Alliance for Genomics and Health. |
| **GKS** | Genomic Knowledge Standards (a GA4GH workstream). |
| **FAIR** | Findable, Accessible, Interoperable, Reusable. |

## Contributing

Contribution guidelines will land alongside the first scaffolded code drop. Until then, please open an issue to discuss any proposed direction.

## Licence

Code is licensed under the terms in [`LICENSE`](LICENSE). Documentation content is intended to be published under a permissive open licence; final licence terms for narrative content will be confirmed before the first published release of the site.
