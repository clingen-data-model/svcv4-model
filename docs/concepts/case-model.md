# Case model

A **Case** is the case-level payload a curator captures from the literature to
represent a single human clinical (CLN) observation supporting (or opposing)
variant pathogenicity. It is the structured `data` behind a
`clinical_observation` Evidence Item.

The model is a permissive **superset**: every attribute is optional on the type.
Which attributes are required (`r`), optional (`o`), conditional (`c`), or not
applicable (`x`) depends on the CLN workflow — `CLN_AFF` (Affected), `CLN_DNV`
(De Novo), `CLN_ALTV` (Alternative Variant), `CLN_ALTG` (Alternative Gene), and
`CLN_UAF` (Unaffected). `CLN_ALTV` + `CLN_ALTG` generalize to `CLN_ALT`.

Applicability and the conditional rules live in a single source of truth,
`schemas/applicability/case_applicability.yaml`. The per-workflow JSON Schemas
under `schemas/json/case/` and the tables below are generated from it; this
phase documents the conditional rules but does not enforce them.

See the [`Case` model reference][svcv4_model.Case] for field types.

## Applicability by workflow

<!-- BEGIN GENERATED: applicability tables -->

#### CLN_AFF

| Attribute | Code | Value | Notes |
|-----------|------|-------|-------|
| `moi` | r | AD, AR, XLD, XLR, SD | ALTV does not yet support AR/XLR |
| `pop_frq_points` | r |  | must be >= -1.0 |
| `case_proband_info` | r |  |  |
| `case_proband_info.sex` | o | M/F/U/T |  |
| `case_proband_info.age` | o |  | age + unit, or an age range; general or disease-specific |
| `case_proband_info.phenotypes` | o | 0..many |  |
| `case_proband_info.phenotypes.name` | o |  |  |
| `case_proband_info.phenotypes.code` | o |  | HPO identifier when possible |
| `case_proband_info.pheno_specificity_for_gene` | r | SPECIFIC, CONSISTENT, INCONSISTENT | curator makes the PHENO SPECIFICITY call; rule coordination is out of scope |
| `case_proband_info.pheno_severity` | x |  | BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG |
| `case_proband_info.age_matched_penetrance` | o | <80%, 80-100%, near 100% | only applicable at all for ALT Gene among the conditional workflows |
| `case_proband_info.confirmed_parental_relationship` | x |  |  |
| `case_proband_info.all_relevant_genes_tested` | r |  |  |
| `vbc` | r |  |  |
| `vbc.id` | r |  |  |
| `vbc.zygosity` | r |  | the only variant_type element needed for case-level VBC assessment |
| `compound_het_variant` | c |  | AFF only; otherwise use additional_variant |
| `compound_het_variant.id` | c |  |  |
| `compound_het_variant.zygosity` | c |  |  |
| `compound_het_variant.phase_in_ref_to_vbc` | c |  |  |
| `compound_het_variant.phase_confidence` | c |  |  |
| `compound_het_variant.classification` | c |  |  |
| `additional_variant_exists` | r |  |  |
| `additional_variants` | c |  | compound-het additional variants are NOT supported |
| `additional_variants.id` | r |  |  |
| `additional_variants.gene` | r |  |  |
| `additional_variants.gene.symbol` | r |  | gene symbol; follows the gene's applicability |
| `additional_variants.gene.mde_associated_gene` | r |  | required if gene is different from VBC gene |
| `additional_variants.zygosity` | r | HOM / HET / HEMI |  |
| `additional_variants.phase_in_ref_to_vbc` | c |  | only if same gene as VBC |
| `additional_variants.phase_confidence` | c |  | only if phase is captured |
| `additional_variants.classification` | r |  | must be P-LP if ALTV or ALTG use case |

#### CLN_DNV

| Attribute | Code | Value | Notes |
|-----------|------|-------|-------|
| `moi` | r | AD, AR, XLD, XLR, SD | ALTV does not yet support AR/XLR |
| `pop_frq_points` | r |  | must be >= -1.0 |
| `case_proband_info` | r |  |  |
| `case_proband_info.sex` | o | M/F/U/T |  |
| `case_proband_info.age` | o |  | age + unit, or an age range; general or disease-specific |
| `case_proband_info.phenotypes` | o | 0..many |  |
| `case_proband_info.phenotypes.name` | o |  |  |
| `case_proband_info.phenotypes.code` | o |  | HPO identifier when possible |
| `case_proband_info.pheno_specificity_for_gene` | r | SPECIFIC, CONSISTENT, INCONSISTENT | curator makes the PHENO SPECIFICITY call; rule coordination is out of scope |
| `case_proband_info.pheno_severity` | x |  | BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG |
| `case_proband_info.age_matched_penetrance` | o | <80%, 80-100%, near 100% | only applicable at all for ALT Gene among the conditional workflows |
| `case_proband_info.confirmed_parental_relationship` | r |  |  |
| `case_proband_info.all_relevant_genes_tested` | r |  |  |
| `vbc` | r |  |  |
| `vbc.id` | r |  |  |
| `vbc.zygosity` | r |  | the only variant_type element needed for case-level VBC assessment |
| `compound_het_variant` | x |  | AFF only; otherwise use additional_variant |
| `compound_het_variant.id` | x |  |  |
| `compound_het_variant.zygosity` | x |  |  |
| `compound_het_variant.phase_in_ref_to_vbc` | x |  |  |
| `compound_het_variant.phase_confidence` | x |  |  |
| `compound_het_variant.classification` | x |  |  |
| `additional_variant_exists` | x |  |  |
| `additional_variants` | x |  | compound-het additional variants are NOT supported |
| `additional_variants.id` | x |  |  |
| `additional_variants.gene` | x |  |  |
| `additional_variants.gene.symbol` | x |  | gene symbol; follows the gene's applicability |
| `additional_variants.gene.mde_associated_gene` | x |  | required if gene is different from VBC gene |
| `additional_variants.zygosity` | x | HOM / HET / HEMI |  |
| `additional_variants.phase_in_ref_to_vbc` | x |  | only if same gene as VBC |
| `additional_variants.phase_confidence` | x |  | only if phase is captured |
| `additional_variants.classification` | x |  | must be P-LP if ALTV or ALTG use case |

#### CLN_ALTV

| Attribute | Code | Value | Notes |
|-----------|------|-------|-------|
| `moi` | r | AD, AR, XLD, XLR, SD | ALTV does not yet support AR/XLR |
| `pop_frq_points` | x |  | must be >= -1.0 |
| `case_proband_info` | r |  |  |
| `case_proband_info.sex` | o | M/F/U/T |  |
| `case_proband_info.age` | o |  | age + unit, or an age range; general or disease-specific |
| `case_proband_info.phenotypes` | o | 0..many |  |
| `case_proband_info.phenotypes.name` | o |  |  |
| `case_proband_info.phenotypes.code` | o |  | HPO identifier when possible |
| `case_proband_info.pheno_specificity_for_gene` | x | SPECIFIC, CONSISTENT, INCONSISTENT | curator makes the PHENO SPECIFICITY call; rule coordination is out of scope |
| `case_proband_info.pheno_severity` | r |  | BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG |
| `case_proband_info.age_matched_penetrance` | x | <80%, 80-100%, near 100% | only applicable at all for ALT Gene among the conditional workflows |
| `case_proband_info.confirmed_parental_relationship` | x |  |  |
| `case_proband_info.all_relevant_genes_tested` | x |  |  |
| `vbc` | r |  |  |
| `vbc.id` | r |  |  |
| `vbc.zygosity` | r |  | the only variant_type element needed for case-level VBC assessment |
| `compound_het_variant` | x |  | AFF only; otherwise use additional_variant |
| `compound_het_variant.id` | x |  |  |
| `compound_het_variant.zygosity` | x |  |  |
| `compound_het_variant.phase_in_ref_to_vbc` | x |  |  |
| `compound_het_variant.phase_confidence` | x |  |  |
| `compound_het_variant.classification` | x |  |  |
| `additional_variant_exists` | r |  |  |
| `additional_variants` | r |  | compound-het additional variants are NOT supported |
| `additional_variants.id` | r |  |  |
| `additional_variants.gene` | r |  |  |
| `additional_variants.gene.symbol` | r |  | gene symbol; follows the gene's applicability |
| `additional_variants.gene.mde_associated_gene` | r |  | required if gene is different from VBC gene |
| `additional_variants.zygosity` | r | HOM / HET / HEMI |  |
| `additional_variants.phase_in_ref_to_vbc` | r |  | only if same gene as VBC |
| `additional_variants.phase_confidence` | r |  | only if phase is captured |
| `additional_variants.classification` | r |  | must be P-LP if ALTV or ALTG use case |

#### CLN_ALTG

| Attribute | Code | Value | Notes |
|-----------|------|-------|-------|
| `moi` | r | AD, AR, XLD, XLR, SD | ALTV does not yet support AR/XLR |
| `pop_frq_points` | x |  | must be >= -1.0 |
| `case_proband_info` | r |  |  |
| `case_proband_info.sex` | o | M/F/U/T |  |
| `case_proband_info.age` | o |  | age + unit, or an age range; general or disease-specific |
| `case_proband_info.phenotypes` | o | 0..many |  |
| `case_proband_info.phenotypes.name` | o |  |  |
| `case_proband_info.phenotypes.code` | o |  | HPO identifier when possible |
| `case_proband_info.pheno_specificity_for_gene` | x | SPECIFIC, CONSISTENT, INCONSISTENT | curator makes the PHENO SPECIFICITY call; rule coordination is out of scope |
| `case_proband_info.pheno_severity` | c |  | BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG |
| `case_proband_info.age_matched_penetrance` | c | <80%, 80-100%, near 100% | only applicable at all for ALT Gene among the conditional workflows |
| `case_proband_info.confirmed_parental_relationship` | x |  |  |
| `case_proband_info.all_relevant_genes_tested` | x |  |  |
| `vbc` | r |  |  |
| `vbc.id` | r |  |  |
| `vbc.zygosity` | r |  | the only variant_type element needed for case-level VBC assessment |
| `compound_het_variant` | x |  | AFF only; otherwise use additional_variant |
| `compound_het_variant.id` | x |  |  |
| `compound_het_variant.zygosity` | x |  |  |
| `compound_het_variant.phase_in_ref_to_vbc` | x |  |  |
| `compound_het_variant.phase_confidence` | x |  |  |
| `compound_het_variant.classification` | x |  |  |
| `additional_variant_exists` | r |  |  |
| `additional_variants` | r |  | compound-het additional variants are NOT supported |
| `additional_variants.id` | r |  |  |
| `additional_variants.gene` | r |  |  |
| `additional_variants.gene.symbol` | r |  | gene symbol; follows the gene's applicability |
| `additional_variants.gene.mde_associated_gene` | r |  | required if gene is different from VBC gene |
| `additional_variants.zygosity` | r | HOM / HET / HEMI |  |
| `additional_variants.phase_in_ref_to_vbc` | x |  | only if same gene as VBC |
| `additional_variants.phase_confidence` | x |  | only if phase is captured |
| `additional_variants.classification` | r |  | must be P-LP if ALTV or ALTG use case |

#### CLN_UAF

| Attribute | Code | Value | Notes |
|-----------|------|-------|-------|
| `moi` | r | AD, AR, XLD, XLR, SD | ALTV does not yet support AR/XLR |
| `pop_frq_points` | x |  | must be >= -1.0 |
| `case_proband_info` | r |  |  |
| `case_proband_info.sex` | o | M/F/U/T |  |
| `case_proband_info.age` | o |  | age + unit, or an age range; general or disease-specific |
| `case_proband_info.phenotypes` | o | 0..many |  |
| `case_proband_info.phenotypes.name` | o |  |  |
| `case_proband_info.phenotypes.code` | o |  | HPO identifier when possible |
| `case_proband_info.pheno_specificity_for_gene` | x | SPECIFIC, CONSISTENT, INCONSISTENT | curator makes the PHENO SPECIFICITY call; rule coordination is out of scope |
| `case_proband_info.pheno_severity` | x |  | BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG |
| `case_proband_info.age_matched_penetrance` | r | <80%, 80-100%, near 100% | only applicable at all for ALT Gene among the conditional workflows |
| `case_proband_info.confirmed_parental_relationship` | x |  |  |
| `case_proband_info.all_relevant_genes_tested` | x |  |  |
| `vbc` | r |  |  |
| `vbc.id` | r |  |  |
| `vbc.zygosity` | r |  | the only variant_type element needed for case-level VBC assessment |
| `compound_het_variant` | x |  | AFF only; otherwise use additional_variant |
| `compound_het_variant.id` | x |  |  |
| `compound_het_variant.zygosity` | x |  |  |
| `compound_het_variant.phase_in_ref_to_vbc` | x |  |  |
| `compound_het_variant.phase_confidence` | x |  |  |
| `compound_het_variant.classification` | x |  |  |
| `additional_variant_exists` | x |  |  |
| `additional_variants` | x |  | compound-het additional variants are NOT supported |
| `additional_variants.id` | x |  |  |
| `additional_variants.gene` | x |  |  |
| `additional_variants.gene.symbol` | x |  | gene symbol; follows the gene's applicability |
| `additional_variants.gene.mde_associated_gene` | x |  | required if gene is different from VBC gene |
| `additional_variants.zygosity` | x | HOM / HET / HEMI |  |
| `additional_variants.phase_in_ref_to_vbc` | x |  | only if same gene as VBC |
| `additional_variants.phase_confidence` | x |  | only if phase is captured |
| `additional_variants.classification` | x |  | must be P-LP if ALTV or ALTG use case |

<!-- END GENERATED: applicability tables -->
