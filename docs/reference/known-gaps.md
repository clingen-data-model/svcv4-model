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
| Variant `classification` is a placeholder `str` | Case model | `AdditionalVariant.classification` and `CompoundHetVariant.classification` are free-text `str` (e.g. `"P"`/`"LP"`), not the `VariantClassification` enum. The CLN scorers normalize via `_classify_plp`; typing these fields as `VariantClassification` would remove the string handling. |

## Documentation / content gaps

| Gap | Area | Notes |
|---|---|---|
| POP scoring computation | POP | POP_FRQ/POP_HMZ evidence *inputs* are now modeled (`PopulationEvidence`); what remains is the point computation (FAF-vs-DAFT fold-change and the POP_HMZ tally — deferred with the other rule/method enforcement) plus the DAFT binning lookup grids and pathogenic-variants list, not yet modeled structurally. See [Population (POP)](../workflows/hod/pop.md). |
| Full PFD modeling | PFD | The four shared sub-modules (SM 7/18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), the **complete Missense workflow** (`MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`, `MissenseAssessment`), the **Nonsense workflow** (`NonsenseAssessment`, three branches), the **Frameshift workflow** (`FrameshiftAssessment`, five branches → `NUL_`/`CDS_`), the **In-Frame InDel workflow** (`InframeIndelAssessment`, two branches → `CDS_`), the **Canonical Splice workflow** (`CanonicalSpliceAssessment`, five color paths → `SPL_`), the **Intronic & Synonymous workflow** (`IntronicSynonymousAssessment`, five splice paths → `SPL_`, reusing the shared `Splice*` vocabulary), the **Exon Deletion workflow** (`ExonDeletionAssessment`, six branches → `NUL_`/`CDS_`), the **Exon Duplication/Gain workflow** (`ExonDuplicationAssessment`, six scored branches + whole-gene NA → `NUL_`/`CDS_`), the **Start-Lost workflow** (`StartLostAssessment`, three branches → `NUL_`/`CDS_`), and the **Stop-Lost workflow** (`StopLostAssessment`, two branches → `NUL_`/`CDS_`) are now modeled (inputs only). This completes every variant-type workflow the Working Group has released (Non-Coding, SM 17, is not yet released). What remains: the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
| Workflow decision-tree diagrams | Documentation assets | The official "Workflow Images" Drive folder (linked from the SVCv4 Pilot Launch announcement) is currently empty. Dozens of named figures are referenced throughout the supplements (missense/nonsense/frameshift/splice flow diagrams, the DAFT derivation diagrams, etc.) — need to follow up with the SVCv4 Working Group (Alicia Byrne / Steven Harrison) for official, releasable versions before embedding any. |
| SM 17 (Non-Coding Variants) not yet released | Source material | The 20 currently-available SVCv4 Supplementary Materials (SM 1–16, 18–21) have been read into this project's working understanding and are linked from [Spec coverage](spec-alignment.md). SM 17 (Non-Coding Variants) is the one not yet released — the Working Group has deferred it; the manuscript flags that section as an unwritten placeholder. |

## Working Group follow-ups (suspected source issues)

Open questions surfaced while building the reference scorer where the Supplementary
Material is ambiguous or appears internally inconsistent. The reference scorer encodes
each **faithfully to the documented rule** and flags the assumption in its `provenance`;
these are candidates to raise with the SVCv4 Working Group for confirmation.

| Item | Source | Notes |
|---|---|---|
| SM 18 Figure-1 `Suspected × Most` matrix cell | SM 18 | The `Suspected × Most` mechanism/exon cell lives in SM 18 Figure 1 (an image, absent from the text extracts). The reference scorer **assumes `0.25`** (keep the Suspected fraction; do not further halve). This is a good candidate to raise with the working group. |
| SM 6 missense-splice blue/violet parent caps | SM 6 | SM 6's missense-splice **blue (`UNCERTAIN`) → `−8..0`** and **violet (`UNLIKELY`) → `−8..+8`** parent caps are inverted vs Canonical (SM 11) / Intronic (SM 12), and read backwards (uncertain capped at 0; unlikely allowed positive). Encoded faithfully to SM 6 + `missense.md`. This is a good candidate to raise with the working group — same category as the SM 18 Figure-1 open item. |
| SM 3 POP_HMZ Autosomal Dominant weight | SM 3 | Prose (L93) says −0.5 pts per homozygous occurrence for AD *or* AR, but **Table 7** assigns Autosomal Dominant **−1.0** (AR/semidominant/X-linked −0.5). The reference scorer follows Table 7 (the explicit point-value table). A good candidate to raise with the working group — same category as the SM 18 Figure-1 open item. |

## How to use this page

When picking up one of these: move the detail into a proper spec (see
`docs/superpowers/specs/` for the convention this project uses) before
implementing, and remove or update the row here once it's underway. This page
should stay short enough to scan, not become its own backlog-management
system.
