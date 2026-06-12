# Clinical Observations (CLN)

**Clinical Observations (CLN)** is the Evidence Concept (under
[Human Observational Data](human-observational-data.md)) for evidence drawn from
observing individuals — affected and unaffected — and how the variant tracks with
disease. This is the concept the [Case model](case-model.md) realizes.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../reference/glossary.md)).

## Codes and their workflows

| Code | Workflow(s) | Detailed here |
|---|---|---|
| [`CLN_AFF`](cln-aff.md) | Affected individuals (AD; AR / X-linked) | ✅ |
| [`CLN_DNV`](cln-dnv.md) | De novo occurrence (AD / X-linked male) | ✅ |
| [`CLN_ALT`](cln-alt.md) | Affected with an alternate cause — [Variant](cln-alt.md#alternative-variant-cln_altv) / [Gene](cln-alt.md#alternative-gene-cln_altg) | ✅ |
| [`CLN_UAF`](cln-uaf.md) | Unaffected individuals (AD; AR / X-linked) | ✅ |
| `CLN_CCS` | Case-control studies | — |

!!! warning "Not yet specified by the SVCv4 Working Group"

    **`CLN_CCS` (Case-Control studies)** is shown here for completeness of the
    framework, but it is **out of scope for the first release** of the SVCv4
    Standards — the SVCv4 Working Group has not yet specified it. It is therefore
    not modeled here. (This is different from POP/LOC/Variant-Impact, which the
    Standards specify but this model has not yet covered — see
    [Population & Locus Specificity](pop-loc.md) and [Variant Impact](variant-impact.md).)

## How to read each workflow page

Each CLN workflow page describes **what evidence to capture** (the Evidence
Items), links to the generated **applicability table** on the
[Case model](case-model.md) page (which fields are required/optional/conditional/
not-applicable for that workflow), and points to
[CSpec](../reference/cspec-interop.md) for the scoring rules.
