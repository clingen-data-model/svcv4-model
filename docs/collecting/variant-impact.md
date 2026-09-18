# 4 · Variant Impact data collection

The final family is **Variant Impact** — the **Predictive & Functional Data
(PFD)** evidence about the variant's molecular effect. Where the case families ask
*what was seen in people*, this one asks *what the variant does to the protein or
transcript*, and it collects four kinds of evidence into **one shared pipeline**
that every variant-type workflow runs.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../reference/glossary.md)).

## The four data types

Each maps to a sub-code and a captured structure:

- **Prediction — `_PRD`.** In-silico predictor output plus initial points,
  captured as `PfdPredictiveEvidence` and the per-variant-type predictive
  entities. Critical-residue/domain determinations (SM 7,
  `CriticalAminoAcidEvidence`) can add points on top of the `_PRD` step.
- **Functional — `_FXN`.** Experimental assays, captured as
  `FunctionalAssayEvidence`: `protein_assays` (`ProteinFunctionalAssay`,
  OddsPath-calibrated) and `animal_models` (`AnimalModelEvidence`).
- **Alteration / splicing — `_SPA`.** RNA/splice assays, captured as
  `SpliceAssayEvidence`, plus the CDS alteration paths. Note the **carve-out**:
  RNA splicing assays are `SPL_SPA`, **not** `_FXN`.
- **Informative variants — `_INF`.** Variants *other than the VBC* that inform its
  classification, captured as `InformativeVariantsEvidence` /
  `InformativeVariant` — distinct-only, with star-rating and circularity gates.

The parent-code pattern is uniform: `_PRD` (prediction), `_FXN` (functional),
`_INF` (informative), plus `_SPA` (splice assay) for splicing — across the MIS,
CDS, NUL, and SPL concepts.

## The one shared pipeline

Every PFD workflow — missense, nonsense, frameshift, canonical splice, exon
deletion/duplication, start/stop lost, and the rest — runs the **same pipeline**:

**predict → adjust for molecular mechanism / exon relevance (SM 18) → (splice
paths: splice assay) → functional → informative → capped code total.**

It is composed by the variant-agnostic `PfdCodeAssessment` scaffold and four
shared submodules: Molecular Mechanism & Exon Relevance (SM 18), Functional
Assays (SM 20), Informative Variants (SM 19), and Determining Critical Amino Acids
(SM 7).

Where the assessment sits here matters for the arc's framing: the scored `_PRD` /
`_FXN` / `_INF` lines and the SM 18 mechanism/exon multiplier (**a factor, not
points**) are the **assessments**. This page is about the **evidence collected to
feed them** — the capture side, consistent with the rest of the arc.

## How it is structured before sharing

- The shared submodules and per-variant-type assessment entities
  (`MissenseAssessment`, `NonsenseAssessment`, …) are catalogued in the
  evidence data structures reference.
- The [PFD workflows overview](../workflows/pfd/index.md) and its ten
  per-variant-type pages hold the branch-by-branch detail — kept out of this arc
  so the pipeline is narrated once here and specified there.
- The [reference scoring map — PFD](../reference/scoring-map/pfd.md) shows how the
  pipeline's pieces combine.

## End of the arc

That completes the four families of collected evidence — curation activities,
population, case & segregation, and variant impact — each captured in a structure
ready to share. From here, the [Workflows](../workflows/index.md) tab specifies
each code and the Reference tab catalogs every structure.
