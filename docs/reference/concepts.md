# Core concepts

This page is the complete reference companion to
[The classification inputs](../getting-started/classification-inputs.md): one
full entry per cross-cutting concept used across the SVCv4 workflows — what it
is, why it matters, which workflows use it, and how it's represented in the
model today. For one-line definitions, see the [Glossary](glossary.md)
instead; this page goes deeper and includes concepts the Glossary doesn't
cover (Zygosity/Phase, the Case model itself, and forward-looking concepts
that aren't modeled yet).

## VBC (Variant Being Classified)

**What it is.** The single variant under evaluation — the thing every
workflow gathers evidence *about*.

**Why it matters.** The VBC is the Proposition's subject (`subjectVariant`)
in the final Statement: every Evidence Line a workflow produces is, in the
end, evidence about this one variant. See
[The assertion framework](../getting-started/assertion-framework.md) for how
the VBC becomes the subject of a Proposition.

**Which workflows use it.** All of them — VBC is a `WorkflowParameters` value
supplied alongside every `Case`, not a per-workflow field.

**Current representation.** `WorkflowParameters.vbc` → `Vbc`, a curation-level
reference with `id` (identifier for the variant being considered) and `gene`
(a `Gene`, described below). Its docstring notes it is the "curation-level
counterpart to the formal VA-Spec `inputs.VBC`" — the two are expected to
reconcile once the curation-level Case model and the formal VA-Spec
Classification Model are unified in a later phase.

## MDE (Mendelian Disease Entity)

**What it is.** The disease/condition the VBC is classified *against* — a
gene + phenotype pairing, not just a gene name.

**Why it matters.** The MDE is the Proposition's object (`objectCondition` /
`objectConditionSet`). Critically, **the gene ↔ MDE relationship is not
1:1**: a single gene may map to more than one MDE, with different modes of
inheritance, different mechanisms, or both (for example, one gene causing a
dominant, gain-of-function disorder and a separate, recessive, loss-of-function
disorder). Because of this, a classification is always made with respect to
one specific MDE — never "the gene" in general. This design constraint traces
back to the SVCv4 Standards' Multiple Disorders Guidance ([Supplementary
Material 21](https://docs.google.com/document/d/1_qkcglOow-l6hLKNH2QipxAJDOn3XZEmoC8Koq9EB6o/edit));
see the corresponding row on the
[Spec coverage](../reference/spec-alignment.md) page.

**Which workflows use it.** All of them — like VBC, MDE is a
`WorkflowParameters` value shared across every workflow a classification
touches.

**Current representation.** `WorkflowParameters.mde` → `Mde`, with `curie`
(disease CURIE, e.g. `MONDO:0007254` or `OMIM:114480`) and `label`
(human-readable disease label). Its docstring likewise notes it is the
curation-level counterpart to the formal VA-Spec `inputs.MDE`.

## Gene

**What it is.** The gene the VBC sits in, plus — as more workflows come
online — the specific transcript being evaluated against (e.g. MANE Select).

**Why it matters.** Usually the VBC's own gene *is* the MDE-associated gene.
But the model doesn't assume that 1:1 relationship: `Gene.mde_associated_gene`
exists specifically for the cases where it isn't true. It is populated **only
when the gene differs from the VBC's own gene** — the relevant scenario is a
curator weighing an *alternate cause* of disease, where the alternate variant
sits in a different gene than the VBC. This is exactly the `CLN_ALT` pair of
workflows: `CLN_ALTV` (Alternative Cause — Variant) and `CLN_ALTG`
(Alternative Cause — Gene).

**Which workflows use it.** Every workflow references the VBC's gene via
`Vbc.gene`; `mde_associated_gene` is specifically relevant to `CLN_ALTG` (and
`CLN_ALTV`, where an alternate-cause variant may also sit in another gene).

**Current representation.** The `Gene` model: `symbol` (gene symbol), `id`
(gene identifier, e.g. HGNC/NCBI id), `transcript` (transcript reference, e.g.
RefSeq accession), and `mde_associated_gene` (string, "required when the gene
differs from the VBC gene," per its field description).

## MOI (Mode of Inheritance)

**What it is.** Whether the VBC's relationship to the MDE is monoallelic
(AD), biallelic (AR), X-linked (XLD/XLR), or semi-dominant (SD).

**Why it matters.** MOI is the single shared parameter with the broadest
downstream effect: it isn't descriptive metadata, it actively **drives
which path a workflow follows**. Concretely, it selects which scoring table
`CLN_AFF` uses (monoallelic vs. biallelic evaluation), and it changes which
fields a workflow even considers applicable — MOI is not applicable at all to
`LOC_PHE` (Locus — Phenotype) but is required for `LOC_SEG` (Locus —
Segregation). The same gating logic is expected to extend to POP and PFD
workflows once those are modeled. Because so much downstream applicability
and scoring hinges on it, an incorrect MOI can silently send a classification
down the wrong evaluation path.

**Which workflows use it.** Shared across all workflows as a
`WorkflowParameters` value, with per-workflow applicability that varies (see
above): required by some (`LOC_SEG`), not applicable to others (`LOC_PHE`),
and table-selecting for others (`CLN_AFF`).

**Current representation.** `WorkflowParameters.moi` → `MOI` enum: `AD`,
`AR`, `XLD`, `XLR`, `SD`. Note the model's `MOI` docstring flags that `ALTV`
does not yet support `AR`/`XLR`.

## Zygosity & Phase

**What they are.** Three related enums describing how a variant sits in an
individual and, when relevant, how it relates to another variant:

- **`Zygosity`** — `HOM` (homozygous), `HET` (heterozygous), `HEMI`
  (hemizygous).
- **`Phase`** — `TRANS`, `CIS`, `UNKNOWN` — the phase of a variant relative to
  the VBC.
- **`PhaseConfidence`** — `HIGH`, `MED`, `LOW` — confidence in a phase
  determination.

**Why they matter.** These three values thread through several distinct
places in the Case model, each with slightly different rules:

- **VBC status in the proband.** `Case.vbc_exists` (whether the VBC is
  present) and `Case.vbc_zygosity` (its `Zygosity`).
- **Compound-het variants.** `Case.compound_het_variant` → `CompoundHetVariant`
  is included *only* when `vbc_zygosity` is `HET` and a second variant in the
  same gene is also `HET` and in *trans* — because those are exactly the
  inclusion criteria, zygosity (`HET`) and phase (`TRANS`) are implied and not
  re-captured on `CompoundHetVariant` itself; only `phase_confidence` is.
- **Additional variants.** `AdditionalVariant` (used by `CLN_ALTV`/`CLN_ALTG`,
  and by `CLN_AFF` when present) carries its own `zygosity`, and
  `phase_in_ref_to_vbc` — captured only if the additional variant shares the
  VBC's gene — plus a `phase_confidence` for that phase determination.
- **Relatives (segregation).** `CaseRelative` (used for `LOC_SEG`) carries
  `vbc_exists` and `vbc_zygosity` for the relative, plus
  `cmp_het_variant_exists`, to determine how the VBC (and any compound-het
  partner) segregates through a family.

**Which workflows use them.** `CLN_AFF`, `CLN_ALTV`, `CLN_ALTG` (via
`AdditionalVariant` and `compound_het_variant`), and `LOC_SEG` (via
`relatives`).

**Current representation.** `Zygosity`, `Phase`, and `PhaseConfidence` enums,
consumed by `Case.vbc_zygosity`, `CompoundHetVariant.phase_confidence`,
`AdditionalVariant.{zygosity, phase_in_ref_to_vbc, phase_confidence}`, and
`CaseRelative.{vbc_exists, vbc_zygosity, cmp_het_variant_exists}`.

## Case

**What it is.** The permissive superset entity that realizes both the CLN
(Clinical Observations) and LOC (Locus Specificity) evidence concepts — the
structured `data` behind a single `clinical_observation` Evidence Item.

**Why it matters — the applicability-driven design.** Every field on `Case`
is optional *on the Pydantic type itself*. Nothing in `case.py` says "this
field is required for `CLN_AFF`" or "not applicable to `LOC_PHE`." That
decision lives entirely outside the type, in the declarative applicability
matrix, `schemas/applicability/case_applicability.yaml`. The matrix — not the
Python class — is the single source of truth for which fields are required
(R), optional (O), conditional (C), or not applicable (X) per workflow; the
per-workflow JSON Schemas and the generated tables on
[Case model](../workflows/case-model.md) are both derived from it. This
separation is deliberate: it lets one reusable `Case` shape serve seven
different workflows (five `CLN_*` plus `LOC_PHE`/`LOC_SEG`) without needing
seven near-duplicate Pydantic models, at the cost of applicability rules not
yet being enforced by the type system itself (this phase documents the rules;
a later phase enforces them).

**Why `vbc`/`mde`/`moi`/`pop_frq_points` live outside `Case`.** These four
values are deliberately modeled as `WorkflowParameters`, not `Case` fields.
The distinction is about what's *shared* versus what's *per-case evidence*:
`vbc`, `mde`, and `moi` are set once per classification and carried into every
workflow that classification touches — they identify *what* is being
classified and *how* its inheritance works, not evidence *for or against* it.
`pop_frq_points` is likewise a cross-cutting workflow input rather than
something a curator observes about a specific clinical case. Folding them
into `Case` would misrepresent them as case-specific observations when
they're actually constants of the classification as a whole.

**Which workflows use it.** All five `CLN_*` workflows and both `LOC_*`
workflows consume `Case` (with workflow-specific applicability); see
[Case model](../workflows/case-model.md) for the full generated
per-workflow applicability tables.

**Current representation.** The `Case` model, with fields spanning proband
identity (`id`, `family_id`, `sex`, `age`), phenotype capture (`phenotypes`,
`pheno_specificity_for_mde`, `gene_specificity_for_phenotypes`,
`pheno_severity`), testing (`testing` → `CaseTesting`), penetrance
(`age_matched_penetrance`), parentage (`confirmed_parental_relationship`),
VBC/variant status (`vbc_exists`, `vbc_zygosity`, `compound_het_variant`,
`additional_variant_exists`, `additional_variants`), and family structure
(`relatives`).

## Cohort Allele Frequency

**What it is.** Population-database allele-frequency data (gnomAD-style) for
the VBC, expressed by the VA-Spec [Cohort Allele Frequency Study
Result](https://va-spec.ga4gh.org/en/1.0/va-standard-profiles/base-profiles/study-result-profiles.html#cohort-allele-frequency-study-result)
profile, one of VA-Spec's base Study Result Profiles.

**Why it matters.** It is *what was observed* for the VBC in a population
database — the raw evidence that `POP_FRQ` weighs against the DAFT (below). In
SVCv4 the specific statistic compared is the **Filtering Allele Frequency
(FAF)**: the population-max, lower-95%-CI-bound allele frequency, a derived
value rather than the raw cohort frequency.

**Which workflows use it.** `POP_FRQ` (population/allele frequency) and
`POP_HMZ` (population observations of homozygotes/hemizygotes) — see
[Population (POP)](../workflows/hod/pop.md).

**Current representation.** `PopulationEvidence.faf` / `faf_source` (and the
homozygote/hemizygote occurrence fields for `POP_HMZ`) — a **curation-level
counterpart** to the formal VA-Spec Cohort Allele Frequency Study Result, the
two reconciled in a later phase. Inputs are captured; scoring is documented on
[Population (POP)](../workflows/hod/pop.md), not computed.

## Disease Allele Frequency Threshold (DAFT)

**What it is.** The calculated ceiling on how frequent a *pathogenic* variant
for a given MDE is expected to be in the population — the threshold the FAF is
compared against. A VCEP/community-curated threshold is preferred; otherwise the
SVCv4 Standards' Population Database Frequency material ([Supplementary
Material 3](https://docs.google.com/document/d/1XON2eq4HSM-guWlqitEnb8PghY0quNbA7_1WmmxvLj8/edit))
defines three derivation methods: a calculator method, a binning method, and a
pathogenic-variants method.

**Why it matters.** DAFT is distinct from, but always compared against, Cohort
Allele Frequency above: Cohort Allele Frequency is *what was observed* for the
VBC; DAFT is *the MDE-specific ceiling* that observed frequency is judged
against to drive the `POP_FRQ` evaluation.

**Which workflows use it.** `POP_FRQ` — see
[Population (POP)](../workflows/hod/pop.md).

**Current representation.** `PopulationEvidence.daft`, `daft_method`
(`VCEP_CURATED` / `CALCULATOR` / `BINNING` / `PATHOGENIC_VARIANTS`), and the
optional `daft_calculator_inputs` (prevalence, penetrance, locus/allelic
heterogeneity). The fold-change scoring against the FAF is documented on
[Population (POP)](../workflows/hod/pop.md), not computed. The binning lookup
grids and pathogenic-variants list are not modeled structurally this phase.

## Gene-Disease Validity

**What it is.** The ClinGen Gene-Disease Validity classification for the
gene↔MDE pair under evaluation: `Definitive`, `Strong`, `Moderate`,
`Limited`, `Disputed`, or `Refuted`.

**Why it matters.** Gene-Disease Validity is a *precondition* that gates
scoring and outcomes in two distinct places, independent of how much
variant-level evidence is accumulated:

- **Downstream — which classification tiers are reachable.** A `Limited`
  validity classification blocks a `Pathogenic`/`Likely Pathogenic` outcome
  outright, no matter the evidence score; a `Disputed` or `Refuted`
  classification blocks reporting entirely. This is a gate evaluated *after*
  the points-based scoring, bounding what the score is allowed to conclude.
- **Upstream — whether molecular-mechanism evidence counts at all.** Per the
  SVCv4 Standards' [Supplementary Material 18 (Molecular Mechanism and Exon
  Relevance)](https://docs.google.com/document/d/1BLnsgxLY0TibwylFWz0SeGGeCusWwSokrgU4qsmBiaw/edit),
  the molecular-mechanism multiplier that scales predictive points in the PFD
  (Predictive & Functional Data) workflows may only be applied for MDEs at
  **Moderate or higher** validity. For MDEs at **Limited or below**, the
  mechanism is treated as `Uncertain`, which zeroes the mechanism multiplier
  (and hence the mechanism-scaled predictive points). So validity feeds the
  PFD scoring pipeline upstream, before any final-tier gate.

**Captured, but not enforced this phase.** This model *captures* Gene-Disease
Validity so a curation records it, and documents both gates above — but it does
**not** enforce either one (no tier-blocking, no mechanism-zeroing). Enforcement
is consistent with, and deferred alongside, the rest of the applicability-rule
enforcement this model documents rather than executes (see the
[Case](#case) note on applicability being documented, not yet type-enforced).
The upstream SM 18 mechanism multiplier itself is not modeled yet either — it
arrives with the PFD workflows (see [Spec coverage](spec-alignment.md)).

**Not classified vs. not captured.** The enum includes a distinct
`NOT_CLASSIFIED` value for a gene↔MDE pair ClinGen has not assessed — which is
*not* the same as leaving the field absent. An absent (`None`) value means the
curator did not capture validity at all; `NOT_CLASSIFIED` means they looked and
ClinGen has no classification for this pair (SM 18 notes such an MDE must then
be assessed manually). This mirrors the model's `TriState` `null`-vs-`UNKNOWN`
distinction elsewhere.

**Which workflows use it.** Potentially all of them, as a classification-level
precondition rather than a per-workflow evidence input — every CLN/LOC/POP/PFD
workflow's scoring or output can ultimately be constrained by it. In the
applicability matrix it is marked optional across all seven current CLN/LOC
workflows, since it drives none of *their* field applicability today (unlike
MOI); its effect lands in PFD scoring and final-tier gating.

**Current representation.** `WorkflowParameters.gene_disease_validity` →
`GeneDiseaseValidity`, a `StrEnum` with the six ClinGen tiers plus
`NOT_CLASSIFIED`.

## See also

- [The classification inputs](../getting-started/classification-inputs.md) —
  the shorter narrative introduction to VBC/MDE/MOI/Gene.
- [Glossary](glossary.md) — one-line definitions for these and other terms.
- [The assertion framework](../getting-started/assertion-framework.md) — how
  VBC/MDE become a Proposition and Statement.
- [Case model](../workflows/case-model.md) — the generated per-workflow
  applicability views for `Case` and `WorkflowParameters`.
- [Spec coverage](../reference/spec-alignment.md) — full SVCv4 Standards
  coverage tracking, including the Multiple Disorders Guidance and Population
  Database Frequency rows referenced above.
- [Known gaps](known-gaps.md) — the organized backlog for the three
  not-yet-modeled concepts above, plus other concrete model/documentation gaps.
