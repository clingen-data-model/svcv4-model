# SVCv4 Standards in brief

!!! note "About this page"

    A high-level primer on the **SVCv4 Standards/framework**, provided to ground
    the modeling documentation. The SVCv4 Standards are authored by the
    **ACMG/AMP/CAP/ClinGen SVCv4 Working Group**; this page is a summary, not the
    Standard. The Working Group's forthcoming publication and specifications are
    the authoritative source. See [Credits](../reference/credits.md).

## What SVCv4 is

**Sequence Variant Classification v4 (SVCv4)** is the next iteration of the
ACMG/AMP variant-classification guidelines, succeeding the 2015 Richards et al.
guidelines (v3). It is being developed by the ACMG/AMP/CAP/ClinGen SVCv4 Working
Group, with publication targeted in *Genetics in Medicine*.

## What changed from v3 to v4

- **Points-based, not strength-categories.** v3 combined strength categories
  (Strong, Moderate, …) via combining rules that didn't cover every scenario.
  v4 assigns **points** to each line of evidence and sums them, which is more
  granular, improves calibration, and lets positive and negative evidence
  combine on one scale.
- **Codes carry type, not strength.** In v3 the strength was baked into the code
  (e.g. `PS4`, `PS4_Moderate`). In v4 a code names the *type* of evidence
  (e.g. `CLN_AFF` — Clinical observation of an Affected individual) and a
  **point value** gives it weight (e.g. `CLN_AFF_+1`, `CLN_AFF_+2`).
- **Decision-tree "curation SOP."** v4 evidence types are framed as detailed
  decision trees that mimic the steps a curator follows, rather than simple
  Met / Not-Met criteria.

<!-- VERIFY: v3→v4 summary and code-naming examples drawn from the "Overview of SVCv4 Standards" deck (slides 4–9); confirm wording with the SVCv4 WG. -->

## The Summary Table

SVCv4 organizes evidence in a **Summary Table** with a top-down hierarchy:

**Evidence Category → Evidence Concept → Evidence Code → Code Workflow(s) → Workflow Score**

Scores roll up the hierarchy. The two top-level categories are **Human
Observational Data** (population, clinical, and locus-specificity evidence) and
**Variant Impact** (predictive and functional evidence). See
[How SVCv4 maps to the model](alignment.md) and the
[Workflows](../workflows/index.md) section for the full picture.

## How the model relates

This documentation and data model provide a **computational representation** of
the above so that systems can capture and exchange the evidence and the
resulting classifications. The Standards define *what* the evidence and codes
are; this project defines *how the data is structured*; and
[ClinGen CSpec](../reference/cspec-interop.md) owns the *methods/rules* that turn
captured evidence into scores. See
[What this project is — and isn't](scope.md).
