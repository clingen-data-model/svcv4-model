# Glossary

| Term | Meaning |
|---|---|
| **SVCv4** | Sequence Variant Classification v4 — the ACMG/AMP/CAP/ClinGen joint Technical Standard, succeeding the 2015 Richards et al. guidelines (SVCv3). Points-based; replaces v3's strength-categories + combining-rules approach. |
| **VBC → `CanonicalAllele` / `Allele`** | The Variant Being Classified — the variant under evaluation — is **represented in the model as a GA4GH `CanonicalAllele` (or `Allele`)**. "The variant," "variation," and "VBC" are synonyms for it; it is the Proposition subject (`subjectVariant`). *Additional variant* and *compound-het variant* are other, distinctly-named variants — not the VBC. |
| **MDE → `Condition` / `ConditionSet`** | The Mendelian Disease Entity — a **gene + phenotype dyad** — is the disease/condition the VBC is assessed against, and is **represented as a `Condition` (or `ConditionSet` when more than one)**. **One gene may map to more than one MDE** (e.g., a single gene can underlie multiple distinct disease entities with different modes of inheritance or mechanisms). "The disease," "the condition," and "MDE" are synonyms for it; it is the Proposition object (`objectCondition` / `objectConditionSet`). |
| **Classification Model** | The shape of a classification (Statements, Propositions, Evidence Lines, Evidence Items). Authored by this repo as a VA-Spec community profile. |
| **Method Model** | The definitions of methods, workflows, criteria, and scoring rules — *and* their evaluation logic. Not in this repo, not yet a VA-Spec community profile. |
| **Statement / Proposition / Evidence Line / Evidence Item** | VA-Spec core entities. See [The assertion framework](../getting-started/assertion-framework.md) and [Evidence Lines & Evidence Items](../getting-started/evidence-lines-and-items.md). |
| **SPOQ** | Subject / Predicate / Object / Qualifier — the structure of a VA-Spec Proposition. |
| **Evidence Category / Concept / Code** | Canonical SVCv4 vocabulary for the user-facing Summary Table; the Evidence Code is the jumping-off point for a workflow in CSpec. |
| **Filtering Allele Frequency (FAF)** | A gnomAD-derived population-frequency statistic that accounts for the maximum minor allele frequency observed across population groups and for sample size, yielding a conservative frequency estimate suitable for filtering. Underlies the `POP_FRQ` evidence code. |
| **Workflow** | A prescriptive procedure (defined and applied in CSpec) for evaluating the evidence captured under an Evidence Code and producing a score for the version of SVCv4 being applied. Each workflow's result surfaces in the Classification Model as an Evidence Line. |
| **Diagnostic yield** | The percentage of phenotype-matched patients for whom a causative genotype is found by a given test or method. Captured by the Case model's `testing.diagnostic_yield_for_phenotypes` field; required input for the `LOC_PHE` (Locus — Phenotype) workflow. |
| **CSpec** | ClinGen Criteria Specification system — registry and APIs where SVCv4 methods, workflows, and VCEP specialisations are published. |
| **VCEP** | ClinGen Variant Curation Expert Panel. Authors specialised SVCv4 method definitions in CSpec. |
| **Community Profile (VA-Spec)** | A layer of additional constraints on top of VA-Spec's baseline classes to enforce a community's terminology and conventions. |
| **VA-Spec / VRS / Cat-VRS / gks-core** | GA4GH GKS sub-schemas. VA-Spec is this repo's primary dependency. |
| **CSpec / ERepo / SEPIO** | ClinGen Criteria Specification; ClinGen Evidence Repository; Scientific Evidence and Provenance Information Ontology. SEPIO informed VA-Spec. |
| **GA4GH** | Global Alliance for Genomics and Health. |
| **GKS** | Genomic Knowledge Standards — a GA4GH workstream. |
| **GIM** | *Genetics in Medicine*, the journal where SVCv4 will be published. |
| **Reclassification** | A **variant-level** classification update, driven by new evidence, new standards, or new professional judgment. Contrast with Case Interpretation, Reanalysis, and Reinterpretation, below. |
| **Case Interpretation** | Assessing whether the variant(s) identified in a genetic/genomic analysis play a role in an individual's phenotype or indication for testing. Contrast with Reclassification, Reanalysis, and Reinterpretation. |
| **Reanalysis** | Re-examining an individual's raw sequencing data (BAM/CRAM/FASTQ/VCF) — distinct from reclassifying a variant or reinterpreting a report. Contrast with Reclassification, Case Interpretation, and Reinterpretation. |
| **Reinterpretation** | Updating a **test report** in light of new phenotype information, reanalysis, or reclassification. Contrast with Reclassification, Case Interpretation, and Reanalysis. |
| **FAIR** | Findable, Accessible, Interoperable, Reusable. |
