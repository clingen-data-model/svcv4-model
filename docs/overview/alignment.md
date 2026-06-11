# How SVCv4 maps to the model

This is the heart of the project: showing how the **SVCv4 Standards**
(authored by the SVCv4 Working Group) line up with the **computational data
model** documented here, so the two stay in lock-step as the framework evolves.

## The Summary Table is the anchor

SVCv4 presents evidence in a **Summary Table** organized top-down:

**Evidence Category → Evidence Concept → Evidence Code → Code Workflow(s) → Workflow Score**

![The SVCv4 Summary Table](../assets/images/summary-table.png){ loading=lazy }

*The SVCv4 Summary Table — every scored cell is a line of evidence. (Figure
provided by the SVCv4 Standards group.)*

## Summary-Table levels ↔ model entities

The model expresses the Summary Table as a hierarchy of **Evidence Lines** that
roll their scores up into a single **Statement** about a Proposition:

| SVCv4 Summary Table | In the data model |
|---|---|
| A scored cell (at any level) | an **Evidence Line** (carries a score) |
| Evidence Category / Concept / Code | nested **Evidence Lines** (scores roll up) |
| Code **Workflow** | the procedure that produces an Evidence Line's score (defined/applied in **CSpec**) |
| The data points a workflow consumes | **Evidence Items** (the captured structured evidence) |
| The variant ⇔ disease question + final score | a **Statement** (Variant Pathogenicity Classification) over a **Proposition** |

So: **Evidence Items** (captured data) feed **workflows**, which produce
**Evidence Lines** (scores), which roll up the Category/Concept/Code hierarchy
into the **Statement's** final score. The entity detail is in
[The assertion framework](../getting-started/assertion-framework.md) and
[Evidence Lines & Evidence Items](../getting-started/evidence-lines-and-items.md).

<!-- VERIFY: the level↔entity mapping is drawn from "The SVCv4 Standard Data Model" deck (slides 6, 11, 13); confirm the mapping wording with the SVCv4 WG / modeling team. -->

## Standard vs. specialized versions

The SVCv4 **Standard** is the baseline hierarchy, workflows, and default
configuration. **Specialized** versions (e.g. gene-disease-MoI scoping, workflow
modifications, domain-specific thresholds) layer on top. The Summary Table's
evidence definitions are fixed; **workflows** carry the customization. Method
specifications — including specialized versions — are published through
[ClinGen CSpec](../reference/cspec-interop.md); this model links to them rather
than implementing the scoring itself.

## Where to go next

- [Workflows](../workflows/index.md) — the Summary Table in depth, with the
  clinical-observation workflows worked through.
- [What this project is — and isn't](scope.md) — the three-way split between the
  Standards, this model, and CSpec.
