# Known gaps

This page is a single, organized place to track what this project knows is
missing — separate from [Spec coverage](spec-alignment.md), which tracks
coverage against the SVCv4 *source documents*. This page tracks concrete,
actionable gaps: specific fields, specific pages, specific follow-ups. It
exists to help decide **how** and **where** each gap gets addressed, not to
track SVCv4's own document-by-document completeness.

Nothing on this page is scheduled — it's a staging area for triage, not a
roadmap with dates.

## Model gaps

| Gap | Area | Notes |
|---|---|---|
| `CLN_CCS` has no `Workflow` entry or fields | Case model (CLN) | SVCv4 gives scoring guidance for it (Supplementary Material 4) but not decomposed evidence concepts the way it has for `CLN_AFF`/`CLN_DNV`/`CLN_ALT`/`CLN_UAF` — blocked on a future SVCv4 version defining those, not simply unstarted. See [Clinical Observations (CLN)](../workflows/hod/cln/index.md). |
| gnomAD co-occurrence-likelihood bucket | Case model (`CLN_AFF`, biallelic) | Used to select the correct scoring-table row for biallelic `CLN_AFF` per Supplementary Material 4; not yet a field on `CompoundHetVariant` or elsewhere on `Case`. |
| "Non-genetic etiology excluded" flag | Case model (`CLN_AFF`) | A sibling condition to the existing `testing.covers_all_genes_relevant_to_mde` — both are AND-conditions in the SVCv4 flow diagram, but only one is modeled. |
| Cohort Allele Frequency representation | POP | The VA-Spec [Cohort Allele Frequency Study Result](https://va-spec.ga4gh.org/en/1.0/va-standard-profiles/base-profiles/study-result-profiles.html#cohort-allele-frequency-study-result) is the likely shape once `POP_FRQ`/`POP_HMZ` are built. See [Core concepts](concepts.md) and [Population (POP)](../workflows/hod/pop.md#the-shape-of-the-remaining-work). |
| Disease Allele Frequency Threshold (DAFT) | POP | Three derivation methods per Supplementary Material 3 (calculator / binning / pathogenic-variants). See [Population (POP)](../workflows/hod/pop.md#the-shape-of-the-remaining-work). |
| Gene-Disease Validity field | Cross-cutting (every workflow) | Gates which classification tiers are reachable at all (e.g. ClinGen "Limited" validity blocks P/LP outright) — nothing in the model represents this precondition today. Likely home: `WorkflowParameters`, alongside `mde`. See [Core concepts](concepts.md). |
| Rule enforcement (`validate_case`) | Case model | Applicability-matrix rules are stored/documented, not enforced at validation time. Deferred since the Case model's initial design (PR #17). |
| Case aggregation & counting | Case model | Aggregating/counting multiple proband observations within a workflow. Deferred since PR #17. |
| SVCv4 point-mapping | Case model / Statement | Mapping aggregated case evidence to the SVCv4 point system, one workflow at a time. Deferred since PR #17. |

## Documentation / content gaps

| Gap | Area | Notes |
|---|---|---|
| Full POP modeling | POP | Currently a stub with a "shape of the remaining work" outline — see [Population (POP)](../workflows/hod/pop.md). |
| Full PFD modeling | PFD | Currently a stub with a shared-pipeline outline — see [Predictive & Functional Data](../workflows/pfd/index.md). |
| Workflow decision-tree diagrams | Documentation assets | The official "Workflow Images" Drive folder (linked from the SVCv4 Pilot Launch announcement) is currently empty. Dozens of named figures are referenced throughout the supplements (missense/nonsense/frameshift/splice flow diagrams, the DAFT derivation diagrams, etc.) — need to follow up with the SVCv4 Working Group (Alicia Byrne / Steven Harrison) for official, releasable versions before embedding any. |
| Remaining Supplementary Materials | Source material | Of the 21 SVCv4 Supplementary Materials, a varying subset has been read into this project's working understanding at any given time (the Drive folder holding them has had inconsistent search-index visibility). See [Spec coverage](spec-alignment.md) for the current per-supplement status. |

## How to use this page

When picking up one of these: move the detail into a proper spec (see
`docs/superpowers/specs/` for the convention this project uses) before
implementing, and remove or update the row here once it's underway. This page
should stay short enough to scan, not become its own backlog-management
system.
