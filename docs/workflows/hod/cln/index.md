# Clinical Observations (CLN)

**Clinical Observations (CLN)** is the Evidence Concept (under
[Human Observational Data](../index.md)) for evidence drawn from observing
individuals — affected and unaffected — and how the variant tracks with disease.
This is one of the two concepts the [Case model](../../case-model.md) realizes
(together with [Locus Specificity](../loc/index.md)).

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../../reference/glossary.md)).

## Codes and their workflows

| Code | Workflow(s) | Detailed here |
|---|---|---|
| [`CLN_AFF`](cln-aff.md) | Affected individuals (AD; AR / X-linked) | ✅ |
| [`CLN_DNV`](cln-dnv.md) | De novo occurrence (AD / X-linked male) | ✅ |
| [`CLN_ALT`](cln-alt.md) | Affected with an alternate cause — [Variant](cln-alt.md#alternative-cause-variant-cln_altv) / [Gene](cln-alt.md#alternative-cause-gene-cln_altg) | ✅ |
| [`CLN_UAF`](cln-uaf.md) | Unaffected individuals (AD; AR / X-linked) | ✅ |
| `CLN_CCS` | Case-control studies | — |

!!! warning "Out of scope for this Classification Model (for now)"

    SVCv4 provides scoring guidance for **`CLN_CCS` (Case-Control studies)** — a
    point scale keyed to an odds ratio and confidence interval — but does not yet
    define decomposed **evidence concepts** for it the way it does for
    `CLN_AFF`/`CLN_DNV`/`CLN_ALT`/`CLN_UAF`. This project models structured,
    verifiable **evidence**, not just derived scores, so there isn't yet a robust
    evidence shape here to capture beyond a single statistic. Subsequent SVCv4
    versions aim to add more evidence-based workflow scoring for `CLN_CCS`; this
    model will cover it once that exists. (This is different from
    [Population (POP)](../pop.md) and
    [Predictive & Functional Data](../../pfd/index.md), which the Standards
    specify with decomposed evidence concepts this project simply hasn't modeled
    yet. Locus Specificity is already covered — see
    [Locus Specificity (LOC)](../loc/index.md).)

## How to read each workflow page

Each CLN workflow page describes **what evidence to capture** (the Evidence
Items), links to the generated **applicability table** on the
[Case model](../../case-model.md) page (which fields are required/optional/
conditional/not-applicable for that workflow), and points to
[CSpec](../../../reference/cspec-interop.md) for the scoring rules.
