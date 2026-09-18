# 1 · Starting curation activities

!!! info "Maturity: Draft"

    The inputs and their model homes are real; wording and the finer conditional
    detail are still settling.

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
*about*, and it becomes the Proposition's subject (`subjectVariant`) in the final
classification.

### MDE — the disease being assessed

The disease/condition the VBC is classified *against*. An MDE is a **gene +
phenotype pairing**, not just a gene: one gene can be associated with more than
one MDE (different inheritance patterns, mechanisms, or both), so a
classification is always made with respect to one specific MDE. This becomes the
Proposition's object (`objectCondition` / `objectConditionSet`).

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

## How it is structured before sharing

Each conceptual input maps to a concrete home in the model:

| Input | Where it lives | Notes |
|---|---|---|
| VBC (id + gene) | `WorkflowParameters.vbc` → [`Vbc`](../reference/evidence-structures.md#vbc) | shared across every workflow, not a `Case` field |
| MDE (curie + label) | `WorkflowParameters.mde` → [`Mde`](../reference/evidence-structures.md#mde) | the disease the VBC is assessed against |
| MOI | `WorkflowParameters.moi` | AD / AR / XLD / XLR / SD |
| Gene & transcript | [`Gene`](../reference/evidence-structures.md#gene) (`symbol` / `id` / `transcript` / `mde_associated_gene`) | nested under `Vbc` |
| gnomAD FAF | `PopulationEvidence.faf` (+ `faf_source`) | the observed value behind `POP_FRQ` |
| DAFT | `PopulationEvidence.daft` (+ `daft_method`, `daft_calculator_inputs`) | the calculated threshold |
| Gene-disease validity | `WorkflowParameters.gene_disease_validity` | classification-level precondition |

`VBC`, `MDE`, `MOI`, and `gene_disease_validity` are `WorkflowParameters` —
shared inputs submitted **alongside** a `Case`, deliberately kept out of the
`Case` itself. See the
[evidence data structures catalog](../reference/evidence-structures.md) for every
field, and [Core concepts](../reference/concepts.md) for the formal definitions.

## Next

With these inputs set, the first real assessment is population frequency — and it
matters early because it can **gate** several downstream assessments. Continue to
**[2 · Population observations (POP)](population.md)**.
