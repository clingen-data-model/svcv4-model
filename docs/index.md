# SVCv4 Classification Model

> A reference for the **Classification Model** of the forthcoming
> **ACMG/AMP/CAP/ClinGen Sequence Variant Classification v4 (SVCv4)**
> Standards, expressed as a **GA4GH GKS VA-Spec community profile**.

These docs are generated from the [Pydantic data model][src] in this
repository together with hand-written concept pages, exported JSON
Schemas, and worked examples. They are aimed at software engineers,
bioinformaticians, and platform teams who will integrate, automate, or
exchange SVCv4 data.

**Status — early development.** The SVCv4 Standards target publication
in *Genetics in Medicine* in October 2026; these docs evolve alongside
the draft VA-Spec SVCv4 community profile in step with GA4GH review.

## Start here

- [**Classification Model vs Method Model**](concepts/classification-vs-method-model.md) — what this model covers, and what lives in ClinGen CSpec instead.
- [**VA-Spec community profile**](concepts/va-spec-community-profile.md) — how the SVCv4 profile layers on top of GA4GH GKS VA-Spec.
- [**Statement & Proposition**](concepts/statement-and-proposition.md) — the top-level entity and its SPOQ-structured Proposition.
- [**Evidence Lines & Items**](concepts/evidence-lines-and-items.md) — how curator-captured evidence becomes scored Evidence Lines.
- [**Summary Table**](concepts/summary-table.md) — Evidence Category / Concept / Code vocabulary.

## Reference

- [**Model reference**](model/index.md) — every class, every field.
- [**JSON Schemas**](schemas/index.md) — machine-readable schemas exported from the Pydantic model.
- [**Examples**](examples/index.md) — worked classifications with narrative walkthrough.

## Interop

- [**GA4GH GKS**](gks-interop.md) — VA-Spec, VRS, Cat-VRS, gks-core.
- [**ClinGen CSpec**](cspec-interop.md) — where method codes resolve.

## Project context

See the [project README][readme] for the contributor list, FAIR posture,
broader context, and licensing.

[src]: https://github.com/clingen-data-model/svcv4-model/tree/main/src/svcv4_model
[readme]: https://github.com/clingen-data-model/svcv4-model/blob/main/README.md
