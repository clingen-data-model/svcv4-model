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
| Rule enforcement (`validate_case`) | Case model | Applicability-matrix rules are stored/documented, not enforced at validation time. Deferred since the Case model's initial design (PR #17). |
| Case aggregation & counting | Case model | Aggregating/counting multiple proband observations within a workflow. Deferred since PR #17. |
| SVCv4 point-mapping | Case model / Statement | Mapping aggregated case evidence to the SVCv4 point system, one workflow at a time. Deferred since PR #17. |

## Documentation / content gaps

| Gap | Area | Notes |
|---|---|---|
| POP scoring computation | POP | POP_FRQ/POP_HMZ evidence *inputs* are now modeled (`PopulationEvidence`); what remains is the point computation (FAF-vs-DAFT fold-change and the POP_HMZ tally — deferred with the other rule/method enforcement) plus the DAFT binning lookup grids and pathogenic-variants list, not yet modeled structurally. See [Population (POP)](../workflows/hod/pop.md). |
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), the **complete Missense workflow** (`MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`, `MissenseAssessment`), the **Nonsense workflow** (`NonsenseAssessment`, three branches), the **Frameshift workflow** (`FrameshiftAssessment`, five branches → `NUL_`/`CDS_`), the **In-Frame InDel workflow** (`InframeIndelAssessment`, two branches → `CDS_`), the **Canonical Splice workflow** (`CanonicalSpliceAssessment`, five color paths → `SPL_`), and the **Intronic & Synonymous workflow** (`IntronicSynonymousAssessment`, five splice paths → `SPL_`, reusing the shared `Splice*` vocabulary) are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
| Workflow decision-tree diagrams | Documentation assets | The official "Workflow Images" Drive folder (linked from the SVCv4 Pilot Launch announcement) is currently empty. Dozens of named figures are referenced throughout the supplements (missense/nonsense/frameshift/splice flow diagrams, the DAFT derivation diagrams, etc.) — need to follow up with the SVCv4 Working Group (Alicia Byrne / Steven Harrison) for official, releasable versions before embedding any. |
| SM 17 (Non-Coding Variants) not yet released | Source material | The 20 currently-available SVCv4 Supplementary Materials (SM 1–16, 18–21) have been read into this project's working understanding and are linked from [Spec coverage](spec-alignment.md). SM 17 (Non-Coding Variants) is the one not yet released — the Working Group has deferred it; the manuscript flags that section as an unwritten placeholder. |

## How to use this page

When picking up one of these: move the detail into a proper spec (see
`docs/superpowers/specs/` for the convention this project uses) before
implementing, and remove or update the row here once it's underway. This page
should stay short enough to scan, not become its own backlog-management
system.
