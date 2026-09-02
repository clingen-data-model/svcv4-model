# Evidence data structures

This page catalogs the **evidence data structures** — the Pydantic models that capture a
curator's inputs for each SVCv4 workflow — and maps each to the workflow(s) it supports, then
describes every attribute.

Every model is a *permissive superset*: all fields are optional (`| None` / empty list) and
`extra="forbid"`. Which fields are required / optional / conditional / not-applicable per
workflow is expressed by the applicability matrix and the SM point rules, not by these types.
The coded-point fields (`*_points`, `*_combined`, `*_total`) are **capture placeholders** — the
[reference scorer](scoring.md) computes them; the models themselves store only the raw inputs.

Two families of workflow exist:

- **PFD — Predictive & Functional Data** (10 variant-type workflows). Each has its own
  *assessment* entity and shares four SM submodules (mechanism/exon-relevance, functional,
  informative, and — for splice paths — the splice vocabulary; plus critical-amino-acid).
- **HOD — Human Observational Data**. Population frequency (POP), Clinical Observations (CLN),
  and Locus/linkage (LOC). These read the standalone `PopulationEvidence` /
  `CaseControlStudyEvidence` payloads or the shared per-proband `Case`.

---

## Which workflows use which structures

### Shared across every workflow

| Structure | Module | Role |
|---|---|---|
| [`WorkflowParameters`](#workflowparameters) | `case.py` | The VBC, MDE, MOI, POP_FRQ points, and gene-disease validity that parameterize any workflow |
| [`Vbc`](#vbc) · [`Mde`](#mde) · [`Gene`](#gene) | `case.py` | Curation-level variant / disease / gene references |
| [`EvidenceItem`](#evidenceitem) | `evidence_item.py` | The generic VA-Spec container each captured datum is wrapped in |

### PFD — shared submodules

| Structure | Module | SM | Used by |
|---|---|---|---|
| [`MechanismExonRelevanceEvidence`](#mechanismexonrelevanceevidence) | `mechanism.py` | SM 18 | **All 10 PFD workflows** (the `_PRD` mechanism × exon-relevance multiplier) |
| [`FunctionalAssayEvidence`](#functionalassayevidence) (+ [`ProteinFunctionalAssay`](#proteinfunctionalassay), [`AnimalModelEvidence`](#animalmodelevidence)) | `functional.py` | SM 20 | **All 10 PFD workflows** (the `_FXN` step) |
| [`InformativeVariantsEvidence`](#informativevariantsevidence) (+ [`InformativeVariant`](#informativevariant)) | `informative.py` | SM 19 | **All 10 PFD workflows** except the Missense amino-acid path (`_INF` step) |
| [`SplicePredictiveEvidence`](#splicepredictiveevidence) · [`SpliceAssayEvidence`](#spliceassayevidence) | `splice.py` | SM 6 | Missense (splice path), Canonical Splice, Intronic & Synonymous (the `SPL_PRD` / `SPL_SPA` steps) |
| [`CriticalAminoAcidEvidence`](#criticalaminoacidevidence) | `critical_amino_acid.py` | SM 7 | Missense (motif / critical-residue points) and the splice orange paths (critical-amino-acid initial-points tables) |

### PFD — per-workflow assessments

| Workflow | Parent code | Assessment structure(s) | Module |
|---|---|---|---|
| *(variant-agnostic scaffold)* | any | [`PfdCodeAssessment`](#pfdcodeassessment) · [`PfdPredictiveEvidence`](#pfdpredictiveevidence) | `pfd.py` |
| Missense | MIS_ / SPL_ | [`MissenseAssessment`](#missenseassessment) → [`MissenseAminoAcidAssessment`](#missenseaminoacidassessment) + [`MissenseSpliceAssessment`](#missensespliceassessment); [`MissensePredictiveEvidence`](#missensepredictiveevidence); [`MissenseInformativeEvidence`](#missenseinformativeevidence) + [`MissenseInformativeVariant`](#missenseinformativevariant) | `missense.py` |
| Nonsense | NUL_ / CDS_ | [`NonsenseAssessment`](#nonsenseassessment) · [`NonsensePredictiveEvidence`](#nonsensepredictiveevidence) | `nonsense.py` |
| Frameshift | NUL_ / CDS_ | `FrameshiftAssessment` · [`FrameshiftPredictiveEvidence`](#frameshiftpredictiveevidence) | `frameshift.py` |
| In-Frame InDel | CDS_ | `InframeIndelAssessment` · [`InframeIndelPredictiveEvidence`](#inframeindelpredictiveevidence) | `inframe_indel.py` |
| Canonical Splice | SPL_ | [`CanonicalSpliceAssessment`](#canonicalspliceassessment) | `canonical_splice.py` |
| Intronic & Synonymous | SPL_ | [`IntronicSynonymousAssessment`](#intronicsynonymousassessment) | `intronic_synonymous.py` |
| Exon Deletion | NUL_ / CDS_ | `ExonDeletionAssessment` · [`ExonDeletionPredictiveEvidence`](#exondeletionpredictiveevidence) | `exon_deletion.py` |
| Exon Duplication | NUL_ / CDS_ | `ExonDuplicationAssessment` · [`ExonDuplicationPredictiveEvidence`](#exonduplicationpredictiveevidence) | `exon_duplication.py` |
| Start Lost | NUL_ / CDS_ | `StartLostAssessment` · [`StartLostPredictiveEvidence`](#startlostpredictiveevidence) | `start_lost.py` |
| Stop Lost | NUL_ / CDS_ | `StopLostAssessment` · [`StopLostPredictiveEvidence`](#stoplostpredictiveevidence) | `stop_lost.py` |

### HOD — per-workflow evidence

| Workflow | Evidence code(s) | Structure(s) | Module |
|---|---|---|---|
| Population | POP_FRQ, POP_HMZ | [`PopulationEvidence`](#populationevidence) (+ [`DaftCalculatorInputs`](#daftcalculatorinputs)) | `population.py` |
| Clinical — Affected | CLN_AFF | [`Case`](#case) (+ [`CaseTesting`](#casetesting), [`CompoundHetVariant`](#compoundhetvariant), [`AdditionalVariant`](#additionalvariant), [`Phenotype`](#phenotype)) | `case.py` |
| Clinical — De novo | CLN_DNV | [`Case`](#case) (`pheno_specificity_for_mde`, `confirmed_parental_relationship`) | `case.py` |
| Clinical — Alternative cause | CLN_ALTV, CLN_ALTG | [`Case`](#case) (`pheno_severity`, `additional_variants`, `age_matched_penetrance`) | `case.py` |
| Clinical — Unaffected | CLN_UAF | [`Case`](#case) (`age_matched_penetrance`, `vbc_zygosity`, `compound_het_variant`) | `case.py` |
| Clinical — Case-control | CLN_CCS | [`CaseControlStudyEvidence`](#casecontrolstudyevidence) *(standalone, like POP)* | `case_control.py` |
| Locus — Phenotype | LOC_PHE | [`Case`](#case) (`gene_specificity_for_phenotypes`, `testing.diagnostic_yield_for_phenotypes`; `relatives` for non-segregation) | `case.py` |
| Locus — Segregation | LOC_SEG | [`Case.relatives`](#caserelative) ([`CaseRelative`](#caserelative)); `confirmed_parental_relationship`, `age_matched_penetrance` | `case.py` |

The `Case` sub-models [`Age`](#age) and [`Phenotype`](#phenotype) are shared by the case and its
relatives.

---

## Attribute reference

### PFD shared submodules

#### `MechanismExonRelevanceEvidence`
*SM 18 mechanism × exon-relevance inputs for a PFD assessment.* Module: `mechanism.py`.

| Field | Type | Description |
|---|---|---|
| `gencc_mechanism` | `GenccMechanism \| None` | GenCC level to which LoF is established as the disease mechanism; gated on Moderate+ validity |
| `exon_relevance` | `ExonRelevance \| None` | Clinical relevance of the VBC's exon across transcripts (All / Most / Few) |
| `mane_status` | `ManeStatus \| None` | MANE membership of the assessed transcript |
| `exon_known_irrelevant` | `bool \| None` | Override: exon known clinically irrelevant, forcing exon relevance to zero |
| `exon_has_established_pathogenic` | `bool \| None` | Override: exon contains established pathogenic variants, so no reduction is applied |

#### `InformativeVariant`
*A single distinct variant (not the VBC) informative for the VBC's classification (SM 19).* Module: `informative.py`.

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Identifier for the informative variant |
| `classification` | `VariantClassification \| None` | The informative variant's own pathogenicity classification |
| `similarity_basis` | `SimilarityBasis \| None` | Why it is informative for the VBC (position / exon / effect / deletion) |
| `distinct_evidence_from_vbc` | `bool \| None` | Whether it reached classification via evidence distinct from the VBC (required to count) |
| `star_rating` | `int \| None` | ClinVar review star rating for external classifications (usable only at 3–4 stars) |
| `circularity_checked` | `bool \| None` | Whether the analyst confirmed the VBC was not used as evidence for this variant |

#### `InformativeVariantsEvidence`
*SM 19 informative-variants inputs for a PFD assessment.* Module: `informative.py`.

| Field | Type | Description |
|---|---|---|
| `variants` | `list[InformativeVariant]` | 0..many distinct informative variants (observation counts do not matter) |

#### `ProteinFunctionalAssay`
*A protein / cellular functional assay, OddsPath-calibrated (SM 20).* Module: `functional.py`.

| Field | Type | Description |
|---|---|---|
| `assay_type` | `ProteinAssayType \| None` | Kind of protein / cellular assay |
| `odds_path` | `float \| None` | OddsPath / likelihood ratio from the calibrated truth set |
| `has_pathogenic_controls` | `bool \| None` | Whether known pathogenic-variant controls were used |
| `has_benign_controls` | `bool \| None` | Whether known benign-variant controls were used |
| `pathogenic_control_count` | `int \| None` | Number of pathogenic controls in the calibration set |
| `benign_control_count` | `int \| None` | Number of benign controls in the calibration set |
| `has_false_positives_or_negatives` | `bool \| None` | Whether the experiment had false positives/negatives (routes calibration beyond lookup tables) |
| `fidelity_to_mechanism` | `bool \| None` | Whether the assay faithfully recapitulates the disease mechanism |

#### `AnimalModelEvidence`
*Whole-animal-model functional evidence (SM 20); range `_FXN_ 0.0 to +4.0`.* Module: `functional.py`.

| Field | Type | Description |
|---|---|---|
| `model_type` | `AnimalModelType \| None` | Engineered / naturally-occurring / complementation |
| `species` | `str \| None` | Model organism, e.g. mouse, zebrafish |
| `ortholog_established` | `bool \| None` | Whether the animal gene is an established ortholog of the human gene |
| `phenotype_replication` | `PhenotypeReplication \| None` | How well the model replicates the human phenotype |
| `inheritance_match` | `bool \| None` | Whether the inheritance pattern matches the human MDE |
| `local_sequence_similarity_high` | `bool \| None` | Whether local sequence similarity around the VBC is high |
| `fidelity_to_mechanism` | `bool \| None` | Whether the model faithfully recapitulates the disease mechanism |

#### `FunctionalAssayEvidence`
*SM 20 functional-assay inputs for a PFD assessment.* Module: `functional.py`.

| Field | Type | Description |
|---|---|---|
| `disease_mechanism` | `MolecularMechanism \| None` | The MDE's molecular mechanism the assays are evaluated against |
| `protein_assays` | `list[ProteinFunctionalAssay]` | 0..many protein / cellular functional assays |
| `animal_models` | `list[AnimalModelEvidence]` | 0..many animal-model functional evidence entries |

#### `CriticalAminoAcidEvidence`
*SM 7 critical-residue / critical-domain inputs for a PFD predictive step.* Module: `critical_amino_acid.py`.

| Field | Type | Description |
|---|---|---|
| `criticality_kind` | `CriticalityKind \| None` | Whether the VBC affects a critical residue or a critical domain |
| `motif_or_domain_name` | `str \| None` | The named motif / domain / residue role (e.g. Gly-X-Y triple-helix glycine) |
| `function_role_established` | `bool \| None` | Whether the residue's/domain's role in protein function is well established |
| `additional_points` | `float \| None` | Additional points on top of the in-silico score (up to +2.0 for a residue) |
| `max_score_not_reached` | `bool \| None` | Whether the `_PRD_ + _INF_` combination has not already reached its cap |
| `observed_in_affected` | `bool \| None` | Whether the variant has been observed in an individual affected with the MDE |
| `double_counting_considered` | `bool \| None` | Whether the analyst confirmed this does not double-count the in-silico predictor |

#### `SplicePredictiveEvidence`
*The splice predictive (`SPL_PRD`) step of a splice path (SM 6; shared by SM 6/11/12).* Module: `splice.py`.

| Field | Type | Description |
|---|---|---|
| `splice_predictor` | `SplicePredictor \| None` | The in-silico splice predictor used (e.g. SpliceAI) |
| `initial_points` | `float \| None` | Initial `SPL_PRD` points before the SM 18 adjustment |
| `protein_fraction_altered` | `float \| None` | Fraction of protein altered (orange paths' initial-points table) |
| `alternative_start_rescue` | `bool \| None` | Whether an alternative start codon rescues the 5′ PTC (the −1.0 case) |
| `adjusted_points` | `float \| None` | Coded `SPL_PRD` points after the SM 18 adjustment |

#### `SpliceAssayEvidence`
*The splice-assay (`SPL_SPA`) step: RNA / minigene evidence for splicing (SM 6).* Module: `splice.py`.

| Field | Type | Description |
|---|---|---|
| `assay_type` | `str \| None` | Assay modality (e.g. RT-PCR, RNAseq, minigene) |
| `result` | `SpliceAssayResult \| None` | Qualitative degree of the aberrant splice product |
| `calibrated` | `bool \| None` | Whether an activity-threshold calibration allows adjusted scoring |

### PFD assessments

#### `PfdPredictiveEvidence`
*The variant-type-agnostic predictive (`_PRD`) step of a PFD assessment.* Module: `pfd.py`.

| Field | Type | Description |
|---|---|---|
| `predictor` | `str \| None` | In-silico predictor or basis used (e.g. REVEL, NMD prediction) |
| `raw_score` | `float \| None` | The predictor's raw score, if applicable |
| `initial_points` | `float \| None` | Initial evidence points before the SM 18 adjustment |
| `path_label` | `str \| None` | Flow-diagram path / color (e.g. GREEN, YELLOW); typed later |
| `transcript_relevance_applied` | `bool \| None` | Whether the SM 18 transcript-relevance step reduced the points |
| `mechanism_applied` | `bool \| None` | Whether the SM 18 mechanism step applied (not for the missense amino-acid path) |
| `adjusted_points` | `float \| None` | Coded `_PRD` points after the SM 18 adjustment |

#### `PfdCodeAssessment`
*One PFD parent-code assessment: the shared pipeline's captured inputs.* Module: `pfd.py`.

| Field | Type | Description |
|---|---|---|
| `parent_code` | `PfdParentCode \| None` | The parent evidence code this assessment resolves to |
| `predictive` | `PfdPredictiveEvidence \| None` | The predictive (`_PRD`) step |
| `mechanism_exon_relevance` | `MechanismExonRelevanceEvidence \| None` | SM 18 molecular-mechanism & exon-relevance inputs |
| `functional` | `FunctionalAssayEvidence \| None` | SM 20 functional-assay evidence (`_FXN`) |
| `informative` | `InformativeVariantsEvidence \| None` | SM 19 informative-variants evidence (`_INF`) |
| `prd_points` | `float \| None` | Coded `_PRD` point value |
| `spa_points` | `float \| None` | Coded `_SPA` (splice-assay) point value; splice paths only |
| `fxn_points` | `float \| None` | Coded `_FXN` point value |
| `inf_points` | `float \| None` | Coded `_INF` point value |
| `parent_total` | `float \| None` | Capped parent-code total for this assessment |

The ten variant-type assessments below all follow this shape — a `prediction_outcome`/`branch`
selector, a `parent_code`, a workflow-specific `*PredictiveEvidence`, the three shared submodules,
the coded `*_points`, a held `prd_fxn_combined` (or the two splice held values), and a
`parent_total`. Only the distinctive fields are highlighted.

#### `NonsensePredictiveEvidence`
*The nonsense predictive (`PRD`) step (SM 8).* Module: `nonsense.py`.

| Field | Type | Description |
|---|---|---|
| `basis` | `str \| None` | Predictive basis (e.g. NMD prediction; PTC position) |
| `initial_points` | `float \| None` | Initial `PRD` points before the SM 18 adjustment |
| `protein_fraction_reduced` | `float \| None` | Fraction of protein lost (the orange/violet initial-points table) |
| `alternative_met_rescue` | `bool \| None` | Evidence an alternative-Met start codon rescues function (orange branch) |
| `adjusted_points` | `float \| None` | Coded `PRD` points after the SM 18 adjustment |

#### `NonsenseAssessment`
*A nonsense variant (NUL_/CDS_) assessment (SM 8).* Module: `nonsense.py`.

| Field | Type | Description |
|---|---|---|
| `prediction_outcome` | `NonsensePredictionOutcome \| None` | Which of the three nonsense branches applies |
| `parent_code` | `PfdParentCode \| None` | Resolved parent code (NUL for yellow; CDS otherwise) |
| `predictive` | `NonsensePredictiveEvidence \| None` | The `PRD` predictive step |
| `mechanism_exon_relevance` | `MechanismExonRelevanceEvidence \| None` | SM 18 inputs |
| `functional` | `FunctionalAssayEvidence \| None` | SM 20 `FXN` evidence |
| `informative` | `InformativeVariantsEvidence \| None` | SM 19 `INF` evidence |
| `prd_points` / `fxn_points` / `inf_points` | `float \| None` | Coded `PRD` / `FXN` / `INF` point values |
| `prd_fxn_combined` | `float \| None` | Held `PRD + FXN` combined value (no distinct code) |
| `parent_total` | `float \| None` | Capped parent-code total (NUL_/CDS_ −8.0 to +10.0) |

#### `FrameshiftPredictiveEvidence`
*The frameshift predictive (`PRD`) step (SM 9).* Module: `frameshift.py`. Adds, beyond the nonsense fields:

| Field | Type | Description |
|---|---|---|
| `non_stop_decay_predicted` | `bool \| None` | ORF runs to the polyA with no in-frame stop, predicting NSD (green) |
| `extension_length_aa` | `int \| None` | Non-native C-terminal amino acids added past the stop (extension branch) |

(`FrameshiftAssessment` mirrors `NonsenseAssessment`, with `prediction_outcome:
FrameshiftPredictionOutcome` — five branches.)

#### `InframeIndelPredictiveEvidence`
*The in-frame InDel predictive (`CDS_PRD`) step (SM 10).* Module: `inframe_indel.py`.

| Field | Type | Description |
|---|---|---|
| `basis` | `str \| None` | Predictive basis (e.g. repeat length; deleted fraction) |
| `initial_points` | `float \| None` | Initial `CDS_PRD` points before the SM 18 adjustment |
| `protein_fraction_reduced` | `float \| None` | Fraction of protein removed (the non-repeat initial-points table) |
| `in_silico_predictor` | `str \| None` | Indel in-silico predictor used (e.g. MutationTaster2021, PROVEAN) |
| `in_silico_calibrated` | `bool \| None` | Whether the indel predictor is calibrated (calibrated reaches +2.0) |
| `repeat_stable_in_controls` | `bool \| None` | SSR branch: the repeat is stable in large control sets (else polymorphic) |
| `adjusted_points` | `float \| None` | Coded `CDS_PRD` points after the SM 18 adjustment |

(`InframeIndelAssessment` mirrors the shape, with `branch: InframeIndelBranch` and
`parent_code` always CDS.)

#### `MissensePredictiveEvidence`
*The amino-acid predictive (`MIS_PRD`) step: one calibrated predictor (SM 6).* Module: `missense.py`.

| Field | Type | Description |
|---|---|---|
| `predictor` | `MissensePredictor \| None` | The single pre-selected calibrated predictor |
| `raw_score` | `float \| None` | The predictor's raw score, if applicable |
| `initial_points` | `float \| None` | Calibrated points before the transcript-relevance step |
| `transcript_relevance` | `ExonRelevance \| None` | Exon presence across disease-relevant transcripts (All / Most / Few) |
| `adjusted_points` | `float \| None` | Coded `MIS_PRD` points after transcript relevance (−4.0 to +4.0) |

#### `MissenseInformativeVariant`
*One `MIS_INF` informative variant in the same codon as the VBC (SM 6).* Module: `missense.py`.

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Variant identifier (e.g. a ClinVar VCV) |
| `category` | `MissenseInfCategory \| None` | Which of the four summable `MIS_INF` categories applies |
| `classification` | `VariantClassification \| None` | The informative variant's classification (P/LP/B/LB) |
| `grantham_wt_to_vbc` | `float \| None` | Grantham distance wild-type → VBC amino acid (categories 2 & 3) |
| `grantham_wt_to_informative` | `float \| None` | Grantham distance wild-type → informative amino acid (categories 2 & 3) |

#### `MissenseInformativeEvidence`
*The `MIS_INF` step: the summable informative variants for the VBC's codon (SM 6).* Module: `missense.py`.

| Field | Type | Description |
|---|---|---|
| `variants` | `list[MissenseInformativeVariant]` | Distinct informative variants; summed, not counted |

#### `MissenseAminoAcidAssessment`
*The missense amino-acid (`MIS_`) path assessment (SM 6).* Module: `missense.py`.

| Field | Type | Description |
|---|---|---|
| `predictive` | `MissensePredictiveEvidence \| None` | The `MIS_PRD` amino-acid predictive step |
| `functional` | `FunctionalAssayEvidence \| None` | SM 20 functional-assay evidence (`MIS_FXN`) |
| `informative` | `MissenseInformativeEvidence \| None` | The four-category Grantham informative evidence (`MIS_INF`) |
| `prd_points` / `fxn_points` / `inf_points` | `float \| None` | Coded `MIS_PRD` / `MIS_FXN` / `MIS_INF` point values |
| `prd_fxn_combined` | `float \| None` | Held `MIS_PRD + MIS_FXN` combined value (−8.0 to +6.0) |
| `mis_total` | `float \| None` | Capped `MIS_` parent-code total (−8.0 to +9.0) |

#### `MissenseSpliceAssessment`
*The missense splice (`SPL_`) path assessment (SM 6).* Module: `missense.py`.

| Field | Type | Description |
|---|---|---|
| `prediction_outcome` | `SplicePredictionOutcome \| None` | Which of the five splice prediction paths applies |
| `predictive` | `SplicePredictiveEvidence \| None` | The `SPL_PRD` splice-prediction step |
| `mechanism_exon_relevance` | `MechanismExonRelevanceEvidence \| None` | SM 18 inputs |
| `splice_assay` | `SpliceAssayEvidence \| None` | `SPL_SPA` splice-assay evidence |
| `functional` | `FunctionalAssayEvidence \| None` | SM 20 `SPL_FXN` evidence |
| `informative` | `InformativeVariantsEvidence \| None` | SM 19 `SPL_INF` evidence |
| `prd_points` / `spa_points` / `fxn_points` / `inf_points` | `float \| None` | Coded `SPL_PRD` / `SPL_SPA` / `SPL_FXN` / `SPL_INF` values |
| `prd_spa_combined` | `float \| None` | Held `SPL_PRD + SPL_SPA` combined value |
| `prd_spa_fxn_combined` | `float \| None` | Held `SPL_PRD + SPL_SPA + SPL_FXN` combined value |
| `spl_total` | `float \| None` | Capped `SPL_` parent-code total for this path |

#### `MissenseAssessment`
*The overall missense workflow assessment; holds both paths plus the applied result (SM 6).* Module: `missense.py`.

| Field | Type | Description |
|---|---|---|
| `amino_acid` | `MissenseAminoAcidAssessment \| None` | The amino-acid (`MIS_`) path assessment |
| `splice` | `MissenseSpliceAssessment \| None` | The splice (`SPL_`) path assessment |
| `selected_path` | `MissenseSelectedPath \| None` | Which path was applied to the VBC after the comparison |
| `applied_total` | `float \| None` | The final points applied to the VBC (the `MIS_` or `SPL_` total) |

#### `CanonicalSpliceAssessment`
*A canonical splice variant (`SPL_`) assessment (SM 11).* Module: `canonical_splice.py`. Field-identical to
[`MissenseSpliceAssessment`](#missensespliceassessment) (same `SPL_PRD → SPL_SPA → SPL_FXN → SPL_INF` pipeline,
two held values, `spl_total`).

#### `IntronicSynonymousAssessment`
*An intronic / synonymous variant (`SPL_`) assessment (SM 12).* Module: `intronic_synonymous.py`. Field-identical
to [`CanonicalSpliceAssessment`](#canonicalspliceassessment); only the point values differ.

#### `ExonDeletionPredictiveEvidence`
*The exon-deletion predictive (`PRD`) step (SM 13).* Module: `exon_deletion.py`.

| Field | Type | Description |
|---|---|---|
| `basis` | `str \| None` | Predictive basis (e.g. whole-gene LoF; NMD; % protein lost) |
| `initial_points` | `float \| None` | Initial `PRD` points before the SM 18 adjustment |
| `protein_fraction_removed` | `float \| None` | Fraction of protein removed (the violet/blue initial-points table) |
| `alternative_start_functional` | `bool \| None` | Demonstrated functional alternative in-frame start (the grey branch) |
| `adjusted_points` | `float \| None` | Coded `PRD` points after the SM 18 adjustment |

(`ExonDeletionAssessment` mirrors the NUL_/CDS_ shape, with `prediction_outcome:
ExonDeletionOutcome` — six branches.)

#### `ExonDuplicationPredictiveEvidence`
*The duplication/gain predictive (`PRD`) step (SM 14).* Module: `exon_duplication.py`.

| Field | Type | Description |
|---|---|---|
| `basis` | `str \| None` | Predictive basis (e.g. tandem NMD; % ORF duplicated; critical domain) |
| `initial_points` | `float \| None` | Initial `PRD` points before the SM 18 adjustment |
| `molecularly_tandem` | `bool \| None` | VBC molecularly proven tandem (vs an unproven copy-number gain) |
| `nmd_predicted` | `bool \| None` | Introduced PTC >50 bp upstream of the last exon-intron boundary predicts NMD |
| `includes_terminal_exon_or_utr` | `bool \| None` | Duplication includes the first exon, last exon, or either UTR |
| `orf_fraction_duplicated` | `float \| None` | Fraction of ORF duplicated / protein disrupted (the >50%..<10% table) |
| `duplicated_domain_critical` | `bool \| None` | Duplicated amino acids alter a proven critical disease-relevant domain |
| `adjusted_points` | `float \| None` | Coded `PRD` points after the SM 18 adjustment |

(`ExonDuplicationAssessment` mirrors the NUL_/CDS_ shape, with `prediction_outcome:
ExonDuplicationOutcome` — six scored branches + whole-gene NA; `functional` is NA on the gain paths.)

#### `StartLostPredictiveEvidence`
*The start-lost predictive (`PRD`) step (SM 15).* Module: `start_lost.py`.

| Field | Type | Description |
|---|---|---|
| `basis` | `str \| None` | Predictive basis (e.g. no alt-start; % protein lost; proven alt-start) |
| `initial_points` | `float \| None` | Initial `PRD` points before the SM 18 adjustment |
| `alternative_start_present` | `bool \| None` | A potential alternate in-frame MET start codon exists |
| `rescue_blocked_by_ptc` | `bool \| None` | P/LP PTC variants between the VBC and the alt-MET make rescue unlikely |
| `protein_fraction_lost` | `float \| None` | Fraction of protein lost if the alternative start is used (orange table) |
| `alternative_start_functional` | `bool \| None` | The alternative start codon is experimentally shown functional (violet) |
| `adjusted_points` | `float \| None` | Coded `PRD` points after the SM 18 adjustment |

(`StartLostAssessment` mirrors the NUL_/CDS_ shape, with `prediction_outcome:
StartLostOutcome` — three branches.)

#### `StopLostPredictiveEvidence`
*The stop-lost predictive (`PRD`) step (SM 16).* Module: `stop_lost.py`.

| Field | Type | Description |
|---|---|---|
| `basis` | `str \| None` | Predictive basis (e.g. NSD predicted; extension length; interference) |
| `initial_points` | `float \| None` | Initial `PRD` points before the SM 18 adjustment |
| `nsd_predicted` | `bool \| None` | No in-frame stop before the polyA site → non-stop decay (the yellow gate) |
| `similar_variant_interference` | `StopLostInterference \| None` | Functional evidence of interference from similar variants (orange tier) |
| `extension_length_aa` | `int \| None` | Predicted extension in amino acids past the native stop (≥30 threshold) |
| `adjusted_points` | `float \| None` | Coded `PRD` points after the SM 18 adjustment |

(`StopLostAssessment` mirrors the NUL_/CDS_ shape, with `prediction_outcome:
StopLostOutcome` — two branches.)

### HOD evidence

#### `DaftCalculatorInputs`
*The four quantitative inputs to the DAFT calculator method (SM 3).* Module: `population.py`.

| Field | Type | Description |
|---|---|---|
| `prevalence_denominator` | `int \| None` | X in a phenotype prevalence of '1 in X'; use the smallest reasonable X |
| `penetrance` | `float \| None` | Expected penetrance (0–1); use the lowest reasonable estimate |
| `locus_heterogeneity` | `float \| None` | Fraction of cases attributable to this locus (0–1) |
| `allelic_heterogeneity` | `float \| None` | Fraction of disease alleles this variant could represent (0–1) |

#### `PopulationEvidence`
*Population-database frequency evidence for the VBC (POP_FRQ + POP_HMZ); benignity-only.* Module: `population.py`.

| Field | Type | Description |
|---|---|---|
| `faf` | `float \| None` | Filtering Allele Frequency (population-max, lower-95%-CI-bound AF), e.g. from gnomAD |
| `faf_source` | `str \| None` | Source / version of the FAF, e.g. 'gnomAD v4.1.1' |
| `daft` | `float \| None` | Disease Allele Frequency Threshold: the MDE-specific ceiling the FAF is compared against |
| `daft_method` | `DaftMethod \| None` | How the DAFT was obtained / derived |
| `daft_calculator_inputs` | `DaftCalculatorInputs \| None` | The calculator method's inputs, when `daft_method` is CALCULATOR (optional) |
| `homozygote_count` | `int \| None` | Number of homozygous occurrences of the VBC in the population database |
| `hemizygote_count` | `int \| None` | Number of hemizygous occurrences (X-linked) of the VBC |
| `hmz_eligible` | `TriState \| None` | Whether MDE penetrance + severity make affected individuals implausible in the database (SM 3 Table 7) |

#### `CaseControlStudyEvidence`
*CLN_CCS case-control study inputs for a VBC (SM 4); standalone, like `PopulationEvidence`.* Module: `case_control.py`.

| Field | Type | Description |
|---|---|---|
| `odds_ratio` | `float \| None` | Odds ratio for the VBC's enrichment in cases vs controls |
| `ci_lower` | `float \| None` | Lower bound of the confidence interval around the OR |
| `ci_upper` | `float \| None` | Upper bound of the confidence interval around the OR |
| `case_cohort_size` | `int \| None` | Number of unrelated cases in the cohort (SM 4 recommends ≥ 100) |
| `case_variant_count` | `int \| None` | Observations of the VBC in the case cohort (SM 4 recommends ≥ 5) |
| `control_cohort_size` | `int \| None` | Number of individuals in the control cohort |
| `controls_matched` | `bool \| None` | Whether cases and controls were matched (ancestry, platform, QC) per SM 4 |
| `ascertainment_bias_considered` | `bool \| None` | Whether ascertainment bias was considered (SM 4) |

#### `Case`
*A reusable, permissive superset of the case-level information for a single human observation (the shared CLN/LOC proband entity).* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Proband identifier, used to match individuals across workflows |
| `family_id` | `str \| None` | Family identifier, used to match relatives across workflows |
| `sex` | `Sex \| None` | Proband sex |
| `age` | `Age \| None` | Proband age |
| `phenotypes` | `list[Phenotype]` | 0..many phenotypes relevant to the case |
| `pheno_specificity_for_mde` | `PhenoSpecificity \| None` | How closely the phenotype(s) match what is expected for the MDE (CLN_AFF/DNV) |
| `gene_specificity_for_phenotypes` | `str \| None` | How specific the phenotype(s) are to the gene, e.g. `100%`, `50%` (LOC_PHE) |
| `testing` | `CaseTesting \| None` | Genetic testing performed |
| `pheno_severity` | `PhenoSeverity \| None` | Phenotype severity relative to expectation (CLN_ALT) |
| `age_matched_penetrance` | `AgeMatchedPenetrance \| None` | Age-matched penetrance band (CLN_UAF / CLN_ALT / LOC) |
| `confirmed_parental_relationship` | `TriState \| None` | Whether the parental relationship was confirmed (CLN_DNV / LOC_SEG) |
| `vbc_exists` | `TriState \| None` | Whether the VBC is present in the proband |
| `vbc_zygosity` | `Zygosity \| None` | Zygosity of the VBC in the proband |
| `compound_het_variant` | `CompoundHetVariant \| None` | The in-trans second variant (biallelic evaluation) |
| `additional_variant_exists` | `TriState \| None` | Whether an additional variant exists in the case |
| `additional_variants` | `list[AdditionalVariant]` | Additional variant(s); populated only if `additional_variant_exists` is TRUE |
| `relatives` | `list[CaseRelative]` | 0..many relatives, for segregation (LOC_SEG) |

> `moi`, `pop_frq_points`, and `gene_disease_validity` are **not** on `Case` — they are on
> [`WorkflowParameters`](#workflowparameters).

#### `CaseTesting`
*Genetic testing performed for the proband/case.* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `method` | `str \| None` | Test method(s), e.g. Sanger, Exome, Genome, Cyto; CSV allowed for multiple |
| `diagnostic_yield_for_phenotypes` | `str \| None` | Diagnostic yield for the phenotype(s), e.g. `100%`, `50%` (LOC_PHE) |
| `covers_all_genes_relevant_to_mde` | `TriState \| None` | Whether the test covered all genes relevant to the MDE (CLN_AFF) |
| `non_genetic_etiology_excluded` | `TriState \| None` | Whether a non-genetic etiology has been excluded (CLN_AFF refinement) |

#### `CompoundHetVariant`
*The second variant in a biallelic evaluation against a het VBC (implied HET + in-trans).* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Identifier for the in-trans second variant |
| `phase_confidence` | `PhaseConfidence \| None` | Confidence that the variant is in trans with the VBC |
| `classification` | `str \| None` | Variant classification (placeholder string this phase) |
| `co_occurrence_likelihood` | `CoOccurrenceLikelihood \| None` | gnomAD co-occurrence likelihood bucket for the VBC + in-trans pairing (biallelic CLN_AFF, SM 4 Table 2) |

#### `AdditionalVariant`
*An additional variant in the case (ALTV/ALTG, or an alternate-cause variant).* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Identifier for the additional variant |
| `gene` | `Gene \| None` | The additional variant's gene (same-gene ALTV vs different-gene ALTG) |
| `zygosity` | `Zygosity \| None` | Zygosity of the additional variant |
| `phase_in_ref_to_vbc` | `Phase \| None` | Captured only if the additional variant shares the VBC gene |
| `phase_confidence` | `PhaseConfidence \| None` | Captured only if phase is captured (HIGH / MED / LOW) |
| `classification` | `str \| None` | Variant classification; must be P/LP for the ALTV and ALTG workflows |

#### `CaseRelative`
*A relative of the proband, captured for segregation (LOC_SEG).* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `parent_of_proband` | `TriState \| None` | Whether this relative is a parent of the proband |
| `sex` | `Sex \| None` | Relative sex; required if X-linked |
| `age` | `Age \| None` | Relative age |
| `phenotypes` | `list[Phenotype]` | 0..many phenotypes for the relative |
| `affected_w_mde` | `TriState \| None` | Whether the relative is affected with the MDE |
| `severe_phenotype` | `TriState \| None` | Whether the relative has a severe phenotype (semi-dominant / X-linked when affected) |
| `vbc_exists` | `TriState \| None` | Whether the VBC is present in the relative |
| `vbc_zygosity` | `Zygosity \| None` | Zygosity of the VBC in the relative |
| `cmp_het_variant_exists` | `TriState \| None` | Whether a compound-het variant exists in the relative |

#### `Age`
*A structured age covering point values, bounds, and ranges.* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `value` | `float \| None` | Point value (with EXACT / GT / LT / APPROX) |
| `min` | `float \| None` | Lower bound (with RANGE) |
| `max` | `float \| None` | Upper bound (with RANGE) |
| `unit` | `AgeUnit \| None` | Unit for value / min / max |
| `qualifier` | `AgeQualifier \| None` | How to interpret the value(s) |
| `raw` | `str \| None` | Original curator text, preserved verbatim |

#### `Phenotype`
*A phenotype as a `{name, code}` pair; either may stand alone.* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `code` | `str \| None` | HPO id / code, preferred (e.g. `HP:0001250`) |
| `name` | `str \| None` | Label of the coded entry, or free-text term not confidently matched to HPO |

### Shared context / container

#### `WorkflowParameters`
*Parameters required by the workflows but not part of the `Case` data structure.* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `vbc` | `Vbc \| None` | The variant being considered |
| `mde` | `Mde \| None` | The disease the VBC is assessed against |
| `moi` | `MOI \| None` | Mode of inheritance |
| `pop_frq_points` | `float \| None` | Population-frequency points (constrained `≥ −1.0`) |
| `gene_disease_validity` | `GeneDiseaseValidity \| None` | ClinGen gene-disease validity for the gene↔MDE pair (a classification-level precondition) |

#### `Vbc`
*Variant Being Considered — the curation-level reference (id + gene). Module: `case.py`.*

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Identifier for the variant being considered |
| `gene` | `Gene \| None` | The gene the VBC is in |

#### `Mde`
*Mendelian Disease Entity — the curation-level disease reference. Module: `case.py`.*

| Field | Type | Description |
|---|---|---|
| `curie` | `str \| None` | Disease CURIE (e.g. `MONDO:0007254`, `OMIM:114480`) |
| `label` | `str \| None` | Human-readable disease label |

#### `Gene`
*A gene reference (symbol / id / transcript).* Module: `case.py`.

| Field | Type | Description |
|---|---|---|
| `symbol` | `str \| None` | Gene symbol |
| `id` | `str \| None` | Gene identifier (e.g. HGNC / NCBI id) |
| `mde_associated_gene` | `str \| None` | MDE-associated gene, required when the gene differs from the VBC gene |
| `transcript` | `str \| None` | Transcript reference (e.g. RefSeq accession) |

#### `EvidenceItem`
*A single structured datum captured for a (VBC, MDE) curation — the generic VA-Spec container each evidence payload is wrapped in (aliased `EvidenceData`).* Module: `evidence_item.py`.

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Stable identifier for the item, when one exists |
| `type` | `str \| None` | Kind of evidence (e.g. `clinical_observation`, `functional_assay`); vocabulary TBD |
| `data` | `dict[str, Any]` | The structured datum itself; open in the scaffold, constrained later per Evidence Code |
| `references` | `list[str]` | CURIEs / URLs sourcing the evidence (e.g. PMIDs) |
| `description` | `str \| None` | Optional prose description |

> A second, *formal* `VBC` / `MDE` pair lives in `inputs.py` (the VA-Spec Proposition
> subject/object — `VBC.variation` will be typed as a GA4GH VRS `Variation`). It reconciles with
> the curation-level `Vbc` / `Mde` above in a later phase.

---

## Enums

The fields above reference these enumerations (module in parentheses):

| Enum | Members |
|---|---|
| `PfdParentCode` (`pfd`) | NUL, CDS, SPL, MIS, NCG, REG |
| `GenccMechanism` (`mechanism`) | ESTABLISHED, LIKELY, SUSPECTED, UNCERTAIN |
| `ExonRelevance` (`mechanism`) | ALL, MOST, FEW |
| `ManeStatus` (`mechanism`) | MANE_SELECT, MANE_PLUS_CLINICAL, NEITHER |
| `VariantClassification` (`informative`) | PATHOGENIC, LIKELY_PATHOGENIC, VUS, LIKELY_BENIGN, BENIGN |
| `SimilarityBasis` (`informative`) | SIMILAR_POSITION, SAME_EXON, SIMILAR_EFFECT, GENE_DELETION |
| `MolecularMechanism` (`functional`) | LOSS_OF_FUNCTION, INCREASED_FUNCTION, TOXIC_GAIN_OF_FUNCTION, DOMINANT_NEGATIVE |
| `ProteinAssayType` (`functional`) | ENZYME_KINETIC, SIGNAL_TRANSDUCTION, MEMBRANE_CONFORMATION, MAVE, OTHER |
| `AnimalModelType` (`functional`) | ENGINEERED, NATURALLY_OCCURRING, COMPLEMENTATION |
| `PhenotypeReplication` (`functional`) | SPECIFIC, KEY_FEATURES, NONE |
| `CriticalityKind` (`critical_amino_acid`) | CRITICAL_RESIDUE, CRITICAL_DOMAIN |
| `SplicePredictionOutcome` (`splice`) | NMD_PREDICTED, FRAMESHIFT_NO_NMD, SPLICE_NO_FRAMESHIFT, UNCERTAIN, UNLIKELY |
| `SplicePredictor` (`splice`) | SPLICEAI, PANGOLIN, OTHER |
| `SpliceAssayResult` (`splice`) | NEAR_COMPLETE_OR_COMPLETE, SUBSTANTIAL, INCOMPLETE_OR_NONE |
| `NonsensePredictionOutcome` (`nonsense`) | NMD_NO_RESCUE, NMD_WITH_RESCUE, NO_NMD |
| `FrameshiftPredictionOutcome` (`frameshift`) | NMD_NO_RESCUE, NMD_WITH_RESCUE, NO_NMD, NON_STOP_DECAY, PROTEIN_EXTENSION |
| `InframeIndelBranch` (`inframe_indel`) | SIMPLE_SEQUENCE_REPEAT, NON_REPEAT |
| `MissensePredictor` (`missense`) | ALPHAMISSENSE, BAYESDEL, ESM1B, MUTPRED2, REVEL, VARITY_R, VEST4, OTHER_CALIBRATED |
| `MissenseInfCategory` (`missense`) | SAME_AA_PATHOGENIC, DISTINCT_AA_PATHOGENIC, DISTINCT_AA_BENIGN, SAME_AA_BENIGN |
| `MissenseSelectedPath` (`missense`) | AMINO_ACID, SPLICE |
| `ExonDeletionOutcome` (`exon_deletion`) | WHOLE_GENE, SUBGENIC_NMD, SUBGENIC_NO_NMD, START_CODON_NO_ALT_START, START_CODON_ALT_START_UNPROVEN, START_CODON_ALT_START_FUNCTIONAL |
| `ExonDuplicationOutcome` (`exon_duplication`) | TANDEM_NMD, TANDEM_NO_NMD, TANDEM_TERMINAL_EXON, GAIN_NMD, GAIN_NO_NMD, GAIN_TERMINAL_EXON, WHOLE_GENE_NA |
| `StartLostOutcome` (`start_lost`) | NO_ALT_START, ALT_START_UNPROVEN, ALT_START_FUNCTIONAL |
| `StopLostOutcome` (`stop_lost`) | NSD_PREDICTED, NO_NSD |
| `StopLostInterference` (`stop_lost`) | LOSS_OF_FUNCTION, SOME_INTERFERENCE, NONE |
| `DaftMethod` (`population`) | VCEP_CURATED, CALCULATOR, BINNING, PATHOGENIC_VARIANTS |
| `Workflow` (`case`) | CLN_AFF, CLN_DNV, CLN_ALTV, CLN_ALTG, CLN_UAF, LOC_PHE, LOC_SEG |
| `MOI` (`case`) | AD, AR, XLD, XLR, SD |
| `GeneDiseaseValidity` (`case`) | DEFINITIVE, STRONG, MODERATE, LIMITED, DISPUTED, REFUTED, NOT_CLASSIFIED |
| `CoOccurrenceLikelihood` (`case`) | LT_0_0001, BETWEEN_0_0001_0_01, NOT_ASSESSED |
| `Sex` (`case`) | M, F, U, T |
| `PhenoSpecificity` (`case`) | SPECIFIC, CONSISTENT, INCONSISTENT |
| `PhenoSeverity` (`case`) | MONO_GT_OR_BIALLELIC_EQ_EXPECTED, MONO_EQ_EXPECTED, BIALLELIC_LT_EXPECTED |
| `AgeMatchedPenetrance` (`case`) | LT_80, PCT_80_100, NEAR_100 |
| `Zygosity` (`case`) | HOM, HET, HEMI |
| `Phase` (`case`) | TRANS, CIS, UNKNOWN |
| `PhaseConfidence` (`case`) | HIGH, MED, LOW |
| `AgeUnit` (`case`) | DAY, WEEK, MONTH, YEAR |
| `AgeQualifier` (`case`) | EXACT, GT, LT, APPROX, RANGE |
| `TriState` (`case`) | TRUE, FALSE, UNKNOWN |
