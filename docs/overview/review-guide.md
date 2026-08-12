# Reviewing this site

This model is being built **alongside** the SVCv4 Standards themselves, not
after them — see [What this project is — and isn't](scope.md). That means
parts of it are genuinely unfinished: some workflows aren't modeled yet
(Predictive & Functional Data), some fields are still being worded, and some
design choices haven't been tested against a real curation yet. The most
useful feedback right now isn't "is this finished" — it's whether the
**shape** of the evidence and data capture matches how a practicing curator
actually thinks about a case. If a field is named oddly, missing, redundant,
or scoped wrong, that's exactly what this review is for.

## A reading path

If you're reviewing this for the first time, this order builds up the model
piece by piece rather than dropping you into the middle of it:

1. [Home](../index.md)
2. [SVCv4 Standards in brief](svcv4-in-brief.md)
3. [How SVCv4 maps to the model](alignment.md)
4. [Show your work: structured evidence](../getting-started/show-your-work.md)
5. [The classification inputs](../getting-started/classification-inputs.md)
6. [The assertion framework](../getting-started/assertion-framework.md)
7. [Evidence Lines & Evidence Items](../getting-started/evidence-lines-and-items.md)
8. [Capture your first case](../getting-started/first-case.md)
9. [Clinical Observations (CLN)](../workflows/hod/cln/index.md) and [Locus Specificity (LOC)](../workflows/hod/loc/index.md)
10. [Spec coverage](../reference/spec-alignment.md)
11. [Core concepts](../reference/concepts.md)

## What we'd like feedback on

- Do the `CLN_AFF`/`CLN_DNV`/`CLN_ALT`/`CLN_UAF` and `LOC_PHE`/`LOC_SEG` Case
  fields (see [Case model & applicability](../workflows/case-model.md)) look
  complete and correctly named to a practicing curator?
- `CLN_CCS` (case-control evidence): SVCv4 gives scoring guidance for it but
  hasn't yet defined decomposed evidence concepts the way it has for the
  other CLN codes, so this project hasn't modeled it either (see the note on
  the [Clinical Observations](../workflows/hod/cln/index.md) page) — does
  that deferral make sense, or is there something worth capturing now
  regardless?
- Two data points implied by the SVCv4 Clinical Observations material aren't
  modeled yet: a gnomAD co-occurrence-likelihood bucket used in biallelic
  scoring, and an explicit "non-genetic etiology excluded" flag — should
  these be first-class fields, or are they fine left as curator notes for
  now?
- Predictive & Functional Data (PFD — missense/nonsense/splice/etc.
  workflows) is a deliberate stub; does the shared pipeline pattern described
  on that page (predict → mechanism/exon-relevance → functional evidence →
  informative variants) match how you'd expect this to eventually be
  modeled?
- Do the cross-cutting concepts on the [Core concepts](../reference/concepts.md)
  page (VBC, MDE, Gene, MOI, Zygosity & Phase, Case) match how you think
  about these day to day as a curator?
- The items above, plus a few more (Gene-Disease Validity, DAFT, rule
  enforcement, case aggregation), are tracked in one place on
  [Known gaps](../reference/known-gaps.md) — does the way they're grouped
  there make sense, or would you organize this differently?

## What's not here

This page is orientation for the model itself. It intentionally does not
list reviewer names or meeting logistics — that lives in an internal
planning note, not the public site.
