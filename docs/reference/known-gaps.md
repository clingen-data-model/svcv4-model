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
| No VBC region / molecular-consequence annotation | Case model | The `Vbc` entity carries only an id + gene, with no coding/intronic-region or consequence field. So the SM 4 CLN_DNV `+7.0` reduction (recommended when the VBC is *outside* coding/adjacent-intronic regions, where de novos are more frequent) cannot be computed — the reference scorer awards the faithful `+7.0` and flags the caveat in provenance. |
| Variant `classification` is a placeholder `str` | Case model | `AdditionalVariant.classification` and `CompoundHetVariant.classification` are free-text `str` (e.g. `"P"`/`"LP"`), not the `VariantClassification` enum. The CLN scorers normalize via `_classify`; typing these fields as `VariantClassification` would remove the string handling. |
| No `de_novo` field on `Case` | Case model | CLN_DNV requires a de-novo occurrence, but `Case` has no `de_novo` field (only `confirmed_parental_relationship`, which is parentage confirmation). `reference_score_cln_proband` **infers** de-novo from `relatives` — both parents present (`parent_of_proband=TRUE`) and both VBC-absent (`vbc_exists=FALSE`), with `confirmed_parental_relationship=TRUE`. A curator who doesn't capture the parents-are-VBC-negative relatives will silently under-score CLN_DNV. |
| No explicit affected-status field | Case model | The per-proband CLN combine infers "affected" from `pheno_specificity_for_mde ∈ {SPECIFIC, CONSISTENT}` (else the unaffected/CLN_UAF path). A genuinely affected proband recorded with only `INCONSISTENT`/absent phenotype specificity is routed to CLN_UAF. SM 4 L186's CLN_ALT "multiple genetic contributions" MDE exclusion is likewise not modeled (only the AR exclusion is enforced). |
| Non-segregation not explicitly captured | Case model | SM 5's LOC_PHE (and LOC_SEG) key off **non-segregation** events, but `CaseRelative` has no non-segregation flag. `reference_score_loc_phe` infers it (the two-case rule: affected + VBC-absent; or unaffected VBC-carrier at near-100% penetrance). Rule (b) is **not yet zygosity-gated**, so an unaffected **XLR** het carrier can trip it — the needed fields (`relative.sex`, `relative.vbc_zygosity`) *are* captured ("data available, not gated"); rule-(b) suppression stays `{AR}` per the settled design. Diagnostic yield is also a free-text `str` (`"90%"`) parsed to a percent — a leading `>` is treated as a floor; a bare proportion with no `%` below 1.0 (`"0.9"`) is scaled to a percent, but a `"1 in N"` ratio (parses to `1.0`) still misparses (curators should record a percent). |

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
| SM 4 CLN_CCS benign value | SM 4 | SM 4 assigns a case-control OR `>5.0` the pathogenic value `CLN_CCS_+4.0`, and notes an OR "near to, or less than 1.0 should be evidence of benignity" — but gives **no CLN_CCS benign point value**. The reference scorer records `0.0` for a low OR and flags the benignity direction in provenance. A candidate to confirm with the working group. |
| SM 3 POP_HMZ Autosomal Dominant weight | SM 3 | Prose (L93) says −0.5 pts per homozygous occurrence for AD *or* AR, but **Table 7** assigns Autosomal Dominant **−1.0** (AR/semidominant/X-linked −0.5). The reference scorer follows Table 7 (the explicit point-value table). A good candidate to raise with the working group — same category as the SM 18 Figure-1 open item. |
| SM 5 LOC_PHE Figure-1 `+2.0` band + boundaries | SM 5 | SM 5's text anchors the phenotype-specificity bands `<33→0`, `33-50→+1`, `68-81→+3`, `>82→+4`, but gives **no explicit anchor for the `+2.0` band** (the reference scorer uses `50<pct<68`) and leaves the `(81,82)` sliver undefined (folded **down** to `+3` conservatively; `≥82→+4` slightly over-awards vs the "83%" worked examples). A candidate to confirm with the working group — same category as the SM 18 Figure-1 open item. |
| Global sum clamp unspecified | SM 1 / GA4GH spec | SM 1 defines **Pathogenic** as open-ended (`≥ +10.0`) and **Benign** as `≤ −4.0`, but the GA4GH JSON `scale` (`svc-v4-ga4gh-spec.md`) gives `maximum: 10.0` / `minimum: −8.0`. No supplement states whether the **summed** point total is clamped. `reference_classify` does not clamp (faithful to SM 1), and the cross-code combine (`reference_combine_case`) sums the family totals **unclamped** — the settled reference-scorer choice. A candidate to confirm with the working group. |
| SM 4 Figure 1 (CLN flow) is image-only | SM 4 | SM 4 Figure 1 authoritatively encodes the CLN branch structure — the CLN_CCS-vs-individual-counting decision, the exact **POP_FRQ gate** (award CLN pathogenic codes only when POP_FRQ is 0.0/−1.0), and the "CLN_DNV could still be added" exception. The prose (L10/L25/L27) gives thresholds but not the full branch logic. These are Inc 3c concerns; per-proband routing (Inc 3a) is fully in SM 4 *text*. A candidate to confirm with the working group. |
| SM 5 LOC_PHE non-segregation under AR | SM 5 | SM 5's "Note Regarding Non-segregation in AR" argues an AR non-segregation may reflect *another causative locus* rather than benignity (the BBS example) — so whether a rule-(a) non-segregation should **zero LOC_PHE at all under AR** is under-specified (SM 5's only worked LOC_PHE non-seg example, TSC2, is dominant). The reference scorer zeroes conservatively and flags the caveat in provenance; this may over-negate. A candidate to raise with the working group. |

## How to use this page

When picking up one of these: move the detail into a proper spec (see
`docs/superpowers/specs/` for the convention this project uses) before
implementing, and remove or update the row here once it's underway. This page
should stay short enough to scan, not become its own backlog-management
system.
