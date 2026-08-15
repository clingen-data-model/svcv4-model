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

!!! note "Not yet modeled here"

    SVCv4 **does** define a `CLN_CCS` (Case-Control studies) process
    ([Supplementary Material 4](https://docs.google.com/document/d/17XnPmgTpzgQ8hfzOZNCcXIBwnNwbVkP0KIv3Dw5Bz_M/edit)):
    a variant-specific case-control analysis, restricted to moderate-frequency
    variants with a sufficient case cohort (≥5 observations of the variant in
    cases, ≥100 unrelated cases, matched controls), measured by an **odds ratio
    (OR)** with its **confidence interval** — `OR > 5.0` awards `CLN_CCS_+4.0`,
    a CI including 1.0 awards no points, and an OR near or below 1.0 is evidence
    of benignity. When `CLN_CCS` is applied, all other CLN codes become **NA
    except `CLN_DNV`**.

    This is a real, addressable evidence shape (a case-control study result: the
    OR and CI, the case/control cohort sizes, and the variant counts) — it is
    simply **not yet modeled** here, alongside [Population (POP)](../pop.md) and
    [Predictive & Functional Data](../../pfd/index.md). Only *finer* case-control
    guidance is anticipated in future SVCv4 iterations; the core process above is
    usable now. Locus Specificity is already covered — see
    [Locus Specificity (LOC)](../loc/index.md).

## How to read each workflow page

Each CLN workflow page describes **what evidence to capture** (the Evidence
Items), links to the generated **applicability table** on the
[Case model](../../case-model.md) page (which fields are required/optional/
conditional/not-applicable for that workflow), and points to
[CSpec](../../../reference/cspec-interop.md) for the scoring rules.
