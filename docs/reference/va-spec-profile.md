# The VA-Spec SVCv4 community profile

The **GA4GH GKS [Variant Annotation Specification (VA-Spec)][va-spec]**
provides a baseline set of classes for representing evidence-based
scientific assertions about genomic variants:

- `Statement`
- `Proposition`
- `EvidenceLine`
- `InformationEntity` / `EvidenceData`

A **community profile** layers additional constraints on top of those
baseline classes to enforce alignment with the terminology and shape
conventions of a specific community guideline.

This repository authors the **VA-Spec SVCv4 Community Profile** — the
SVCv4-specific constraints on top of the VA-Spec baseline. The profile
is what enables consistent representation, comparison, and processing
of SVCv4 classifications with standardised tooling across
organisations.

## Two layerings stacked

It helps to keep two different layerings distinct:

1. **Interoperability layering** — VA-Spec baseline classes → SVCv4
   community profile (authored *here*).
2. **Domain layering** — SVCv4 Standard baseline → VCEP specialisations
   (authored *in CSpec*).

The first determines the *shape* of an SVCv4 classification across the
genomics ecosystem. The second determines *which methods and rules*
produce its scores for a given (VBC, MDE) curation. Both inform what
this model has to express; only the first is what this repo publishes.

## Lineage

The ACMG 2015 (SVCv3) guidelines were earlier developed into a VA-Spec
community profile, and ClinGen's Evidence Repository (ERepo)
JSON-LD/SEPIO implementation informed the design of VA-Spec itself.
This project further informs the SVCv4 community profile being
authored on top of VA-Spec.

[va-spec]: https://va-spec.ga4gh.org/

## See also

- [The assertion framework](../getting-started/assertion-framework.md)
- [Evidence Lines & Evidence Items](../getting-started/evidence-lines-and-items.md)
- [GA4GH GKS interop](gks-interop.md)
