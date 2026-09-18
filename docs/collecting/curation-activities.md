# 1 · Starting curation activities

Before any assessment scores anything, a curator does a small amount of setup:
naming what is being classified and gathering the easily-captured evidence that
needs no workflow branching. These are **starting curation activities, not
assessments.** An assessment is a *scored* line of evidence — a rule-level
evaluation. Everything on this page is an **input**: a value that is set once (or
looked up, or calculated) and then steers or feeds the assessments that come
later.

Throughout: **the variant = the VBC** (Variant Being Classified) and **the
disease/condition = the MDE** (Mendelian Disease Entity). See the
[Glossary](../reference/glossary.md) and [Core concepts](../reference/concepts.md)
for full definitions — this page explains *why each input matters* and *where it
is structured*.

## The anchoring inputs

A classification is anchored by a small, fixed set of inputs. They don't change
per evidence code — they're set once per classification and then steer how every
workflow applies and scores evidence.

### VBC — the variant being classified

The single variant under evaluation. It's what every workflow gathers evidence
*about*, and it becomes the Proposition's subject (`subject`) in the final
classification.

### MDE — the disease being assessed

The disease/condition the VBC is classified *against*. An MDE is a **gene +
phenotype pairing**, not just a gene: one gene can be associated with more than
one MDE (different inheritance patterns, mechanisms, or both), so a
classification is always made with respect to one specific MDE. This becomes the
Proposition's object (`object`).

### MOI — mode of inheritance

Whether the VBC ⇔ MDE relationship is monoallelic (AD), biallelic (AR), X-linked
(XLD/XLR), or semi-dominant (SD). MOI is not just descriptive metadata — it
**controls which path a workflow follows**: it selects which scoring table
`CLN_AFF` uses (monoallelic vs. biallelic), is not applicable to `LOC_PHE` but
required for `LOC_SEG`, and steers the POP and PFD workflows too. Get MOI wrong
and every downstream workflow's applicability and scoring can be wrong.

### Gene & transcript

The gene the VBC sits in and — increasingly, as more workflows come online — the
specific transcript the evidence is evaluated against (e.g. MANE Select). Usually
the VBC's gene *is* the MDE-associated gene, but not always: when a curator
weighs an alternate cause of disease, the gene carrying the alternate variant may
differ from the VBC's gene, which is why the model carries an explicit
`mde_associated_gene` distinction rather than assuming a 1:1 gene ↔ variant ↔
disease relationship.

## Evidence that's captured, not branched

Two further inputs are easily captured up front because they need no workflow
branching — a lookup and a calculation:

- **The gnomAD population frequency.** The VBC's **Filtering Allele Frequency
  (FAF)** — the population-max, lower-95%-CI-bound allele frequency — is a
  **lookup** from a population database such as gnomAD. It is the observed value
  that the `POP_FRQ` assessment (covered in
  [Part 2](population.md)) later compares against a threshold.
- **The DAFT.** The **Disease Allele Frequency Threshold** is a **calculation**:
  an estimated ceiling on how common a *truly pathogenic* variant for the MDE
  could plausibly be, derived from disease prevalence, penetrance, and
  locus/allelic heterogeneity. It is computed once and recorded with the method
  used to derive it.

State it plainly: the FAF is a *lookup* and the DAFT is a *calculation* — neither
is an assessment. They become inputs to the POP assessment, not scores in their
own right.

## Gene-disease validity — a classification-level precondition

One more thing a curator records up front is the **ClinGen gene-disease
validity** for the gene ↔ MDE pair (Definitive, Strong, Moderate, Limited,
Disputed, Refuted, or Not Classified). It is not a per-workflow evidence input
like MOI; it is a **precondition** that gates which final tiers are reachable and
whether the PFD molecular-mechanism multiplier may be applied at all. It is
captured here; the gating is documented, not enforced this phase.

## Gates — order your work so you don't collect what gets zeroed

A **gate** is a condition, set by an earlier input or assessment, that makes a
later assessment **not applicable** or forces its score to a fixed value. Knowing
the gates up front lets a curator sequence the work — settle the gating inputs
first, and skip data collection that a gate would discard. None of these are
enforced by the model this phase; they are documented so the ordering is
deliberate.

| Gate | Set by | Effect when it trips | Do this first |
| --- | --- | --- | --- |
| **POP_FRQ gate** | `pop_frq_points` (from the POP assessment) | If `pop_frq_points` is **not** `0.0` or `−1.0` (the variant is too common), `CLN_AFF` and `CLN_DNV` become **NA** — affected/de-novo probands won't be scored. | Do **POP first** (Part 2). If the variant fails the frequency gate, don't collect affected/de-novo case evidence for scoring. |
| **Gene-disease validity gate** | `gene_disease_validity` (recorded above) | Below **Moderate** (or unclassified), the PFD molecular-mechanism multiplier (SM 18) is treated as Uncertain and can zero the mechanism-scaled predictive/functional contribution; it also caps which final tiers are reachable. | Record gene-disease validity **before** investing in predictive/functional (PFD) collection for a weakly-validated gene↔MDE pair. |
| **CLN_CCS exclusivity** | A variant-specific case-control study (`CLN_CCS`) being used | When `CLN_CCS` is applied, all other clinical codes are **NA except `CLN_DNV`** — `CLN_AFF`, `CLN_UAF`, and `CLN_ALT` won't be scored. | Decide whether a case-control study is your clinical evidence **before** compiling individual probands you can't also score. |
| **Non-segregation flip** | An observed non-segregation in a family (`LOC_SEG`) | A non-segregation **zeroes `LOC_PHE`** and **flips `LOC_SEG` to `−4.0`** (benign evidence) for the relevant MOI. | Confirm segregation and parental relationships early; a single non-segregation overrides accumulated locus support. |

The through-line: **frequency and validity are settled first, the clinical
evidence *type* is chosen before probands are compiled, and family relationships
are confirmed before locus evidence is banked.** Gates are cited to their
Supplemental Material (POP_FRQ + CLN_CCS: SM 4; mechanism multiplier: SM 18;
segregation: SM 5); CSpec remains authoritative for the arithmetic.

## Sources & resources the assessments draw on

The Supplemental Materials reference a recurring set of public knowledge sources.
Curators don't need all of them up front, but knowing which source feeds which
assessment helps stage the lookups. This maps each source to the data it provides
and the assessment (or input) it feeds.

| Source / resource | Kind | Provides | Feeds |
| --- | --- | --- | --- |
| **gnomAD** | Population database | Filtering Allele Frequency (population-max, lower-95%-CI-bound) | POP — the FAF lookup |
| **ClinGen gene-disease validity** (with **GenCC**) | Curated registry | Definitive → Refuted classification for a gene ↔ MDE pair | Gene-disease validity precondition; PFD mechanism gate |
| **MANE Select** | Transcript standard | The canonical transcript evidence is evaluated against | Gene & transcript anchoring; all workflows |
| **OMIM / MONDO** | Disease ontologies | Disease/condition identity and curie | MDE definition |
| **HPO** | Phenotype ontology | Phenotype terms (`HP:…`) for probands and relatives | Case phenotypes; LOC_PHE specificity |
| **ClinVar** | Variant archive | Existing classifications of comparator alleles (same-codon / same-residue) | MIS same-residue / same-codon evidence |
| **SpliceAI** | In-silico predictor | Predicted splice-altering effect | SPL (splicing) |
| **REVEL, BayesDel, AlphaMissense, VEST4, VARITY, ESM1b, MutPred2** | In-silico predictors | Missense pathogenicity prediction scores | MIS_PRD predictor initial points |
| **Grantham** | Substitution matrix | Amino-acid physicochemical distance | MIS_INF (same-/distant-AA reasoning) |
| **MaveDB** | Functional-data repository | Multiplexed assay (MAVE) functional readouts | FNC (functional assays) |
| **OddsPath** | Calibration statistic | Strength calibration of a functional assay | FNC (functional assays) |
| **PubMed** | Literature | Source publications for observations | Case-evidence provenance |
| **UniProt / Ensembl** | Sequence & annotation | Protein features, domain / exon context | Predictive & splicing context |

In-silico predictor choice and weighting are **specification decisions**, not
fixed here — a domain specialization may add, limit, or re-weight the predictors
it accepts (each carrying its `MIS_`-scoped code), which is why the predictor row
lists candidates rather than a mandated set. The authoritative per-assessment
source lists live in the Supplemental Materials.

## How it is structured before sharing

Each conceptual input maps to a concrete home in the model:

| Input | Where it lives | Notes |
|---|---|---|
| VBC (id + gene) | `WorkflowParameters.vbc` → `Vbc` | shared across every workflow, not a `Case` field |
| MDE (curie + label) | `WorkflowParameters.mde` → `Mde` | the disease the VBC is assessed against |
| MOI | `WorkflowParameters.moi` | AD / AR / XLD / XLR / SD |
| Gene & transcript | `Gene` (`symbol` / `id` / `transcript` / `mde_associated_gene`) | nested under `Vbc` |
| gnomAD FAF | `PopulationEvidence.faf` (+ `faf_source`) | the observed value behind `POP_FRQ` |
| DAFT | `PopulationEvidence.daft` (+ `daft_method`, `daft_calculator_inputs`) | the calculated threshold |
| Gene-disease validity | `WorkflowParameters.gene_disease_validity` | classification-level precondition |

`VBC`, `MDE`, `MOI`, and `gene_disease_validity` are `WorkflowParameters` —
shared inputs submitted **alongside** a `Case`, deliberately kept out of the
`Case` itself. See [Core concepts](../reference/concepts.md) for the formal
definitions.

## Next

With these inputs set, the first real assessment is population frequency — and it
matters early because it can **gate** several downstream assessments. Continue to
**[2 · Population observations (POP)](population.md)**.
