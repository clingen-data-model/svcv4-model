# Capturing basic evidence: a first look with `POP_FRQ`

Before working through a full clinical-observation workflow, it's worth seeing
the whole "capture → score → Evidence Line" mechanic once, somewhere it can't
get lost in branching logic. **`POP_FRQ`** (population database frequency) is
the simplest evidence code SVCv4 defines: one observed value, compared against
one calculated threshold, producing one point value — no proband bookkeeping,
no conditional branches, no multiple-workflow paths to track. That simplicity
makes it a good place to see the mechanic clearly before
[Capture your first case](first-case.md) applies it to something busier
(`CLN_AFF`).

Throughout: **the variant = the VBC** (Variant Being Classified) and **the
disease/condition = the MDE** (Mendelian Disease Entity). See the
[Glossary](../reference/glossary.md).

## What gets captured (conceptually)

The question `POP_FRQ` asks is: *is the VBC's population frequency implausibly
high for the MDE being considered?* An implausibly high frequency is evidence
of **benignity** — a variant that's too common in the general population to be
the cause of a rare, highly penetrant disease.

To answer it, a curator captures two things:

- The VBC's **Filtering Allele Frequency (FAF)** — the population-max,
  lower-95%-CI-bound allele frequency, drawn from a population database such as
  gnomAD.
- A **Disease Allele Frequency Threshold (DAFT)** for the MDE in question — a
  calculated ceiling on how common a *truly pathogenic* variant for that MDE
  could plausibly be, derived from disease prevalence, penetrance, and
  genetic/allelic heterogeneity. SVCv4 defines three ways to derive it (a
  calculator method, a binning method for sparse-data situations, and a
  pathogenic-variants method used as a cross-check).

Everything else in the evaluation is just comparing the first value to the
second.

## What it produces

That comparison lands on a **benignity-only point scale**: FAF at or modestly
above DAFT contributes nothing, and increasingly implausible multiples of DAFT
push the score further negative — roughly 0 near the threshold, down to around
-6 at the extreme end. Treat that shape (four bands, increasingly negative) as
illustrative rather than exact: the precise multiples and point values are
CSpec's to define and may be refined before publication. See
[ClinGen CSpec interop](../reference/cspec-interop.md) for where the actual
scoring rules live — this project describes what evidence is captured, not the
scoring math itself.

## What this project models today

Here's the honest state of things: `POP_FRQ` itself — the raw evidence capture
described above (FAF as a first-class value, DAFT, the comparison between
them) — is **not yet modeled** in this repo. Population (POP) is a genuine
stub: there's no `Workflow` enum entry for it and no applicability-matrix
entries, unlike the CLN and LOC workflows this model already covers in detail.
See [Population (POP)](../workflows/hod/pop.md) for that stub page, and
[Core concepts](../reference/concepts.md) for Cohort Allele Frequency and DAFT,
both documented there as forward-looking concepts only.

What the model *does* carry today is the **result** of a `POP_FRQ` assessment:
a single float field, `pop_frq_points`, on `WorkflowParameters`. It's supplied
alongside a `Case`, not computed by anything in this model, and it's required
input to `CLN_AFF`, `CLN_DNV`, `LOC_PHE`, and `LOC_SEG` (it's marked not
applicable to `CLN_ALTV`, `CLN_ALTG`, and `CLN_UAF` in the current
applicability matrix — see [Case model & applicability](../workflows/case-model.md)).
In other words: this model consumes the *outcome* of a `POP_FRQ` evaluation
everywhere it's needed, without yet modeling the evaluation itself.

## What happens next

Once you have a `pop_frq_points` value, it becomes one of the required inputs
you supply alongside a `Case` — [Capture your first case](first-case.md) uses
this exact field in its minimal `CLN_AFF` example. From there, that single
value joins the rest of the workflow's captured evidence to produce an
**Evidence Line** score, as described in
[Evidence Lines & Evidence Items](evidence-lines-and-items.md). The next page
in this sequence, on rolling up Evidence Line scores, picks up right where
this one leaves off — showing how individual Evidence Line scores combine on
the way to a Statement.

## See also

- [Population (POP)](../workflows/hod/pop.md) — the stub page for the wider
  Population Evidence Concept.
- [Core concepts](../reference/concepts.md) — Cohort Allele Frequency and DAFT,
  documented as forward-looking-only.
- [Capture your first case](first-case.md) — a full worked example that uses
  `pop_frq_points` as one of its inputs.
- [Evidence Lines & Evidence Items](evidence-lines-and-items.md) — what happens
  to a captured value once a workflow scores it.
