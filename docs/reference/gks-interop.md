# GA4GH GKS interop

This model is grounded in the **Global Alliance for Genomics and Health
(GA4GH)** [**Genomic Knowledge Standards (GKS)**][gks] workstream.
ClinGen is a GA4GH driver project. The primary GKS dependency for the
Classification Model is **[Variant Annotation Specification
(VA-Spec)][va-spec]**; supporting schemas include VRS, Cat-VRS, and
gks-core.

| GKS schema | Version | Role in this model |
|---|---|---|
| **VA-Spec** | v1.0 | Baseline for the SVCv4 Classification Model — `Statement`, `Proposition`, `EvidenceLine`, `InformationEntity` / `EvidenceData`. |
| **VRS** | v2.0 | Used to represent the **VBC**'s variation. |
| **Cat-VRS** | v1.0 | Used where the variant is described categorically. |
| **gks-core** | — | Shared identifier, CURIE, and provenance constructs. |

## Reference, do not redefine

The Classification Model **references** GKS types by CURIE per GKS
conventions; it does not duplicate or redefine them. Where a slot
expects a VRS Variation, the slot will be typed against
`ga4gh.vrs.models.Variation` in Python and against the VRS schema in
JSON Schema.

The Pydantic GKS packages used as upstream dependencies:

- `ga4gh.vrs` (v2.x) — Pydantic models for VRS, generated upstream
  from LinkML.
- `ga4gh.va-spec` (0.x; pre-1.0) — Pydantic models for VA-Spec,
  generated upstream from LinkML.
- `ga4gh.cat-vrs` — added when the SVCv4 community profile requires
  categorical variation support.

These are wired into the model incrementally as the SVCv4 VA-Spec
community profile stabilises.

## Why VA-Spec is the lead dependency

VA-Spec is the GKS schema that represents *evidence-based assertions
about variants*. Every SVCv4 classification is exactly that. VRS and
Cat-VRS describe the variant itself — they support VA-Spec by giving
it a precise way to identify the subject of an assertion. gks-core
provides the shared building blocks across all of GKS.

For a complete GKS overview, see the [VRS documentation site][vrs].

## Lineage

- The earlier ACMG/AMP 2015 (SVCv3) guidelines were developed into a
  VA-Spec community profile.
- ClinGen's Evidence Repository (ERepo) and its JSON-LD SEPIO
  implementation informed VA-Spec.
- This project further informs the SVCv4 VA-Spec community profile.

[gks]: https://ga4gh-gks.github.io/
[va-spec]: https://va-spec.ga4gh.org/
[vrs]: https://vrs.ga4gh.org/
