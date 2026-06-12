# Show your work: structured evidence

The cornerstone of SVCv4 — and of this model — is **showing your work with
structured evidence**. A classification isn't just a verdict; it's a verdict
*plus* the evidence and reasoning behind it, captured so others (and machines)
can see, check, and reuse it.

## Why it matters

- **Reproducible.** When the evidence behind a score is captured explicitly,
  another curator or system can follow exactly how the classification was
  reached.
- **Computable.** SVCv4 is points-based; the points come from evidence evaluated
  by workflows. Capturing that evidence in a common structure is what lets the
  scoring be applied consistently.
- **Shareable.** Structured evidence travels between tools and organizations
  without losing meaning — the whole point of a common data model.

## What "structured evidence" means here

Each SVCv4 evidence code (e.g. `CLN_AFF` — affected individuals) has a
**workflow** that needs specific **data points**. In the model, those captured
data points are **Evidence Items**, grouped under the **Evidence Line** that
carries the workflow's score. Capturing the right Evidence Items, in the right
shape, for the workflow you're applying is "showing your work."

This project standardizes *how that evidence is structured*. It does **not**
define the scoring rules themselves — those workflows/methods live in
[ClinGen CSpec](../reference/cspec-interop.md). Your job (as a curator or a
producing system) is to capture the evidence; the workflow turns it into a score.

## How it builds up

Captured evidence rolls up into the final classification record:

- **Evidence Items** — the structured data points you capture.
- **Evidence Lines** — scored roll-ups for a code/concept/category.
- **Statement** — the final causal Variant Pathogenicity Classification over a
  Proposition.

See [The assertion framework](assertion-framework.md) for that backbone, then
[Capture your first case](first-case.md) for a concrete, minimal example.
