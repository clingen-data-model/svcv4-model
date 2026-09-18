# SVCv4 Data Model & Computational Design — 20-minute presentation

**Date:** 2026-09-18
**Audience:** Scientific & technical — **system developers and their curator
users.** People who will *build software against* the model or *produce/consume*
classifications with it. **They are NOT VA-Spec-literate** — assume no prior
knowledge of GA4GH GKS, VA-Spec, VRS, or its class/property vocabulary.
**Goal:** Convey the computational modeling and coding design we're crafting for
release alongside the SVCv4 classification specification, and what a developer can
build against today.
**Length:** 20 minutes. ~19 slides. Budget ≈ 1 min/slide, with 3 min held for the
worked example and 2 min for Q&A. Keep to **one idea per slide.**

> **Two hard constraints on every slide:**
>
> 1. **Plain language, not VA-Spec jargon.** The audience doesn't know VA-Spec.
>    Keep class/property names (`Statement`, `hasEvidenceLines`, `Proposition`,
>    SPOQ, VRS) **out of on-slide text** — say "the record," "a scored line of
>    evidence," "the captured facts." Technical names live in speaker notes as
>    *"for the technically curious,"* surfaced only if asked.
> 2. **v4-only — no v3.** Do **not** reference the 2015/v3 guidelines or any old
>    criteria codes (PVS1, PS/PM/PP/BA/BS/BP…). SVCv4 stands on its own. (Same
>    scrub is being applied to the docsite — see the simplification plan.)

> **Author note — VA-Spec version (do not present):** the deck's model shape tracks
> **GA4GH VA-Spec `1.1.0-ballot.2026-09`**
> (<https://va-spec.ga4gh.org/en/1.1.0-ballot.2026-09/>), which folds the old
> separate "EvidenceLine" class into a single recursive `Statement`. Slides 5–7 and
> 12–13 already use the plain-language nested-claim framing this implies; reconcile
> the repo model/docs wording before presenting.

**Reusable visuals already in the repo** (don't rebuild — pull these):
- Points bands — `docs/assets/images/points-bands.png`
- Summary Table — `docs/assets/images/summary-table.png`
- HOD workflows — `docs/assets/images/hod-workflows.png`
- Variant-impact (PFD) workflows — `docs/assets/images/variant-impact-workflows.png`
- Scope/data-flow diagram — the ASCII flow in `docs/overview/scope.md` (redraw clean)
- Entity model & Summary-Table-alignment slides — `tmp/extracted/The_SVCv4_Standard_Data_Model/`
  and `tmp/extracted/TheSummaryTable_alignment_to_evidence_lines.ppt/`

**Workflow explainer graphics (Larry's — location TBD):** the recently-created
per-workflow explainer graphics are the intended visuals for **slides 8, 11, and
13**. Drop the source files into `docs/assets/images/explainers/` (or tell me
where they live) and I'll reference them by exact filename. Slots are marked
`[EXPLAINER: <workflow>]` below.

---

## Timing budget

| Segment | Slides | Time |
|---|---|---|
| Frame the problem & scope | 1–4 | 4 min |
| The model (what a classification *is*) | 5–8 | 5 min |
| From capture to a score (the computing layer) | 9–13 | 6 min |
| Interop, status, and what to build against | 14–17 | 3 min |
| Close + credits + Q&A | 18–19 | 2 min |

---

## Slide 1 — Title

**On slide:**
- **A Data Model & Reference Computation for SVCv4 Variant Classification**
- Built as a GA4GH GKS VA-Spec community profile, for release alongside the
  ACMG/AMP/CAP/ClinGen SVCv4 Standards
- Presenter · SVCv4 Standards data-modeling team (ClinGen Data Platform WG)
- Date

**Speaker notes (~30s):** One line on who you are and the one promise of the talk:
"By the end you'll know what we're publishing, how it's structured, and what you
can build against today." Set expectations: this is the *data model and reference
code*, not the Standard itself and not the scoring authority.

---

## Slide 2 — Why this exists

**On slide:**
- SVCv4 moves variant classification to a **points-based** framework — evidence
  carries a code and a point value; points combine into a final classification.
- Points only interoperate if the **evidence behind them is captured in a common,
  computable form** — "show your work."
- Goal: **standard semantic interoperability** for producing, exchanging, and
  consuming SVCv4-compliant classifications across labs and systems.

**Speaker notes (~1m):** SVCv4 scores evidence as **points** that combine — and
can mix positive and negative evidence — into a final call. That granularity is
powerful but fragile without a shared data structure. If every lab records the
underlying evidence differently, the points aren't comparable and can't be
recomputed or audited. The model is the substrate that makes points portable.
*(Do not frame this as "v3 vs v4" or cite old criteria codes — SVCv4 stands on its
own; keep the talk v4-only.)*

*Visual: points-bands.png.*

---

## Slide 3 — Three groups, three jobs (the scope boundary)

**On slide:** (table)
| Owns | Who | What |
|---|---|---|
| The **framework** | ACMG/AMP/CAP/ClinGen SVCv4 WG | Summary Table, codes, workflows, scoring approach |
| The **data model** | *This project* (ClinGen Data Platform WG offshoot) | The shape of a classification — for interoperability |
| The **methods/rules** | ClinGen **CSpec** | Evaluates evidence, produces the scores |

**Speaker notes (~1m):** This is the single most important slide for a technical
audience — it tells them what our artifact is authoritative for and what it isn't.
We do **not** author the Standard, and we do **not** own the scoring rules. We
model *what a classification is* so that the WG's framework and CSpec's methods
have a common carrier. Everything downstream in the talk lives inside the middle
row.

---

## Slide 4 — Classification Model vs Method Model

**On slide:**
- **The classification** *(this project)* — the **shape** of a classification: the
  claim, its evidence lines, and the captured facts. *What a classification is.*
- **The methods/rules** *(ClinGen CSpec)* — the logic that **evaluates** the
  evidence and produces the workflow scores.
- They meet through **codes**: our record *names* a method/evidence code; CSpec
  *defines* what it does.
- **Baseline vs specializations:** SVCv4 ships a baseline; expert panels (VCEPs)
  add specialized rules later — in CSpec. Same record shape either way.

**Speaker notes (~1m):** The junction is the key idea, in plain terms: we carry the
**code**, CSpec carries the **rule behind the code**. That clean seam is what lets
the very same classification record work with today's baseline and a
panel-specialized rule later **without changing shape**. Keep "Statements /
Evidence Lines" as internal vocabulary — say "the record" and "lines of evidence"
out loud.

*Visual: redraw the scope.md data-flow: curator captures facts → CSpec methods
evaluate → a scored line of evidence (its code + the facts used + the score).*

---

## Slide 5 — Why we build on a shared standard (GA4GH) *(plain-language foundation)*

> **Audience is NOT VA-Spec-literate.** On-slide text stays plain; keep class
> names and version numbers OUT of the bullets and in speaker notes only.

**On slide:**
- For classifications to be **shared and compared** across labs and software, they
  need a **common, computer-readable shape** — not just a PDF or a spreadsheet.
- **GA4GH** already publishes that shape for variant knowledge. We **build on it**
  instead of inventing our own.
- Our job: **add the SVCv4-specific rules on top** of that shared foundation, so
  an SVCv4 classification is understood the same way everywhere.
- Payoff: **produce once, consume anywhere** — and we inherit GA4GH's existing
  tools for naming variants precisely.

**Speaker notes (~1m — the high-level "how we build on GA4GH" beat):** Keep this
conceptual. The one idea: interoperability needs a shared structure, and GA4GH's
VA-Spec (Variant Annotation Specification) is that structure for variant knowledge
— computer-to-computer exchange. We publish a **community profile**: SVCv4-specific
constraints layered on the shared classes (the same pattern the 2015 guidelines
used). *For the technically curious only (don't put on the slide):* we track VA-Spec
closely — the base standard just simplified its model this month and we've already
absorbed it; we lean on VRS for variant identity. Don't say "VA-Spec / VRS /
community profile" from the podium unless someone asks — say "the GA4GH standard."

---

## Slide 6 — What a classification *is*: evidence that nests *(plain language)*

**On slide:**
- A **classification** is a **claim about a variant and a condition** — e.g.
  *"this variant is pathogenic for this condition"* — with a **direction**
  (for / against) and a **score**.
- That top claim is backed by **lines of evidence**.
- Here's the key idea: **each line of evidence is itself a small scored claim**,
  backed either by more evidence lines or by the **captured facts** underneath.
- So the record **nests**: claim → evidence lines → the facts. Same shape at every
  level. That uniformity is what makes it computable and auditable.

**Speaker notes (~1.5m — the conceptual keystone):** Draw it as nesting boxes, no
jargon. The whole model is one recursive shape: a scored, directional claim,
supported by smaller scored, directional claims, all the way down to the raw
captured data (a study result, a data point). Every scored box in SVCv4 is one of
these. *For the technically curious only (keep off the slide):* GA4GH calls this
box a **Statement**; an "evidence line" is just a Statement nested under another
one. The base standard recently collapsed a separate "EvidenceLine" class into this
single recursive Statement — which actually makes the plain-language story *truer*:
it really is the same thing at every level. Don't lead with class names; lead with
"scored claims that nest."

> **Repo reconciliation note (for us, not the audience):** the site + model still
> show the older three-box framing (Statement → EvidenceLine → EvidenceItem).
> Update the wording/diagram to the single nested-claim shape before presenting.
> The *concept* is unchanged; only the class structure simplified.

*Visual: nesting boxes — "Classification (scored claim)" containing "Evidence line
(scored claim)" containing "Captured facts." Reuse for the whole talk.*

---

## Slide 7 — The Summary Table is the map

**On slide:**
- The SVCv4 **Summary Table** organizes all the evidence: **categories →
  concepts → codes**, and each **code opens a workflow** (a guided set of steps).
- Each workflow produces a **score**, which **rolls up** to its code — with
  **caps** (a category can't exceed its ceiling).
- Every one of those scored boxes becomes **one line of evidence** in the record
  (the nesting from the previous slide).

**Speaker notes (~1m):** This is how the Standard's own picture becomes our data
structure — nothing new to learn, it's the table they already use. Pink boxes =
where a workflow starts; green boxes = capped roll-ups. The point for this
audience: the Summary Table isn't a diagram off to the side — it *is* the shape of
the evidence, and it lines up one-to-one with the nesting claims from slide 6.

*Visual: summary-table.png.*

---

## Slide 8 — "Show your work": the Case & evidence capture

**On slide:**
- The curator captures **Evidence Items / data points** — the inputs a method
  needs — in a structured **Case** entity.
- A **Case model + applicability matrix** governs which fields are
  required/optional/conditional/excluded per workflow.
- Capture is **modeled and tested** across all evidence categories.

**Speaker notes (~1m):** This is where a developer's system actually plugs in: you
collect structured evidence into Cases. The applicability matrix (r/o/c/x per
workflow) is the contract for a capture UI — it tells the curator's tool what to
ask for and when. Capture came first in our build precisely because it's the
interoperability payload.

*Visual: `[EXPLAINER: a representative workflow]` — lead with one of Larry's
workflow explainer graphics here to make "structured capture" concrete; fall back
to hod-workflows.png or a Case-fields snippet.*

---

## Slide 9 — The reference computation layer (why it exists)

**On slide:**
- We built a **reference, non-authoritative scorer** in the repo —
  `svcv4_model.scoring`.
- Purpose: **tests, worked examples, and the practice variant set** — proving the
  captured data is sufficient to compute the documented points.
- **CSpec remains authoritative.** Every result carries `authoritative = False`
  (constructing it `True` raises). Any divergence from CSpec is a bug *here*.

**Speaker notes (~1m):** Important framing for this audience: we are *not*
competing with CSpec. We wrote a mirror of the Supplementary-Material point rules
so we can prove — mechanically — that our data model captures everything a scorer
needs. It's the first layer in the repo that *computes* anything; everything
before it was capture + documentation.

---

## Slide 10 — Coding design: pure functions, one-way dependencies

**On slide:**
- `reference_score_*(assessment, *, gene_disease_validity=…)` → a **`ScoreResult`**
  (sub-code points, held-combined intermediates, capped parent total, provenance).
- **Pure functions**; one-way dependency `scoring → models` (capture models never
  import scoring).
- **Kept out of the schema surface** — `ScoreResult` is a compute DTO, not
  Pydantic; no scoring types leak into published JSON Schemas.
- Un-scoreable / No-Data steps are **omitted**, never recorded as `0.0`.

**Speaker notes (~1m):** The design discipline is the point. Scoring is a
side-effect-free layer bolted *on top of* the data model, never woven into it — so
the published schemas stay clean and CSpec-authority is structurally protected,
not just documented. Provenance on every result gives an auditable step-by-step
trail. This is how we keep "reference, non-authoritative" from being a slogan and
make it a property of the code.

---

## Slide 11 — One pattern, every workflow: the BranchSpec pipeline

**On slide:**
- LoF workflows (NUL_/CDS_) share **`score_nul_cds_workflow`**; each workflow is
  just a **`BranchSpec` table** (parent/held/INF caps per outcome branch).
- Splice (SPL_) shares a parallel `score_spl_workflow` (adds a splice-assay step +
  a second held value).
- Shared **primitives**: the SM18 mechanism × exon-relevance multiplier, caps, the
  informative-variant tally, held-combined.
- Result: a new workflow scorer is often **a table + one line of delegation.**

**Speaker notes (~1m):** This is the software story a technical audience
appreciates: we found the shared shape of ten variant workflows and parameterized
it. Adding Frameshift after Nonsense was a branch table, not a rewrite. The per-
workflow differences (a −4 parent floor, a mechanism-only multiplier, a functional-
NA branch) are declared as data in the spec, not branched in code.

*Visual: `[EXPLAINER: a NUL_/CDS_ or splice workflow]` — one of Larry's workflow
explainer graphics pairs naturally here: show the human decision tree, then land
"this whole tree is one BranchSpec table."*

---

## Slide 12 — End-to-end: capture → score → aggregate → classify

**On slide:** (pipeline)
- **Per-code scorers:** all 10 PFD workflows · POP · all CLN codes (AFF/DNV/ALT/
  UAF/CCS) · LOC_PHE.
- **Aggregation:** POP/LOC family subtotals → per-proband CLN combine →
  cross-proband sum → **cross-code combine** into one **(VBC, MDE) total**.
- **Classification band:** `reference_classify(points)` → Benign / Likely Benign /
  VUS (low/mid/high) / Likely Pathogenic / Pathogenic (SM1 bands).

**Speaker notes (~1.5m):** Walk the arrow. The reference layer now runs the whole
way: from a captured Case, through each evidence code, up through aggregation, to a
banded classification. Call out that this end-to-end path is *real and tested* —
it's the strongest evidence that the data model is sufficient. Remaining pieces:
LOC_SEG (point values now in hand from SM5 Fig 2 — implementation pending) and
`validate_case` applicability enforcement.

*Visual: a clean left-to-right pipeline diagram.*

---

## Slide 13 — Worked example (the 3-minute payoff)

**On slide:**
- One practice-set variant, end to end: captured facts → evidence codes fired →
  **scored lines of evidence** (each with its code + score) → combined total → band.
- Show the **provenance trail** for one code.

**Speaker notes (~3m — the anchor of the talk):** Pick one clean example from the
practice variant set (32 encoded). Show the actual captured fields, then the scored
lines of evidence it produces — each with its code, direction, and score — then the
roll-up to a total and the band. Emphasize: **code = identity, score = outcome,
shown separately** (`CLN_AFF (score: +1.0)`, never `CLN_AFF_+1`) — and that the same
nested structure is what another system would consume. This is where the abstract
model becomes concrete for a developer.

> Prep: choose the example before the talk; a monoallelic CLN_AFF or a Nonsense
> PFD case reads most cleanly. Have the JSON on the slide, trimmed. If the chosen
> example has a matching **`[EXPLAINER: <that workflow>]`** graphic, show it beside
> the JSON so the audience sees the human view and the computed record together.

---

## Slide 14 — Where the model meets CSpec

**On slide:**
- Each scored **line of evidence** carries a **code** (a method/evidence reference).
- CSpec resolves those codes into **definitions** (baseline + expert-panel
  specializations).
- The same classification record works with **today's baseline and a specialized
  rule later — no shape change.**

**Speaker notes (~45s):** Reinforce the seam from slide 4 now that they've seen a
real record. For an implementer: you store the code; you resolve it against the
CSpec registry at evaluation time. The model doesn't hard-code any scoring rule.

---

## Slide 15 — Honest about the edges

**On slide:**
- **Solid:** the shared-standard foundation, the scope boundary, the Case model,
  the schemas, evidence capture across all categories.
- **In progress:** aligning our record wording to the base standard's latest
  simplification; the scoring map; workflow write-ups; scorer aggregation.
- **Open questions for the Working Group:** a few Supplementary-Material
  boundary/typo points — all recorded in the code's audit trail and `known-gaps`.

**Speaker notes (~45s):** Credibility comes from naming the gaps precisely. Note
the recent win: two figure-only rules we'd had to *assume* (the mechanism×exon
multiplier's edge cell, and the co-segregation point values) are now resolved
against the source figures — one of them corrected an assumption we'd made. Every
place we still infer is flagged in the code's audit trail *and* the docs. We're not
hiding approximations; we log them for WG confirmation. *(Keep "VA-Spec / Statement"
off the slide — say "the shared GA4GH standard" and "our record.")*

---

## Slide 16 — What you can build against today

**On slide:**
- **JSON Schemas** for every entity (generated from the model).
- The **documentation site** (model reference, workflows, scoring map, glossary,
  interop).
- **32 worked practice examples** as learning/test fixtures.
- The **reference scorer** as an oracle for your own implementation's expected
  points.

**Speaker notes (~45s):** Concrete takeaways. If you're building a capture tool,
target the Case model + applicability matrix and validate against the schemas. If
you're building a consumer, read the classification record and its lines of
evidence. If you're building a scorer, diff against our reference results
(remembering CSpec is the authority).

---

## Slide 17 — Timeline & deliverables

**On slide:**
- **~October 2026** — SVCv4 Standards published in *Genetics in Medicine*; the
  model release aligns to it.
- Draft access before publication: **GA4GH VA community profile** (JSON Schema +
  docs), learning examples/use cases.
- Specialized methods via the **CSpec Registry** (public API + docs).

**Speaker notes (~30s):** Set the clock. We're building toward the GIM publication;
draft artifacts are available ahead of it for developers who want to start.

---

## Slide 18 — Close: one sentence to remember

**On slide:**
- **The Standard defines the framework; CSpec defines the methods; we define the
  shape — built on a shared GA4GH standard so SVCv4 classifications are computable,
  exchangeable, and auditable.**

**Speaker notes (~30s):** Land the single-sentence takeaway. Invite engagement:
here's the repo, here's the docs, here's how to give feedback.

---

## Slide 19 — Credits & Q&A

**On slide:**
- Key contributors: Alicia Byrne, Larry Babb, Christine Preston, Neethu Shah
  *(+ the wider data-modeling team & VA-Spec profile authors)*
- Repo + docs links · contact
- **Questions**

**Speaker notes:** Keep 2 min for Q&A. Likely questions to pre-load:
*"Is this the scorer of record?"* (No — CSpec is; ours is a reference oracle.)
*"How do expert-panel specializations fit?"* (Same record shape; the code resolves
to a different rule in CSpec.) *"Why build on an outside standard instead of your
own format?"* (Interoperability + we inherit existing tooling.) *"When can I depend
on it?"* (Draft now, aligned to the ~Oct 2026 GIM publication.)

---

## Delivery notes

- **Cut lever if you run long:** compress slides 5 and 14 (both are "trust the
  seam" points) and hold the time for the worked example (13) — that's what sells
  it.
- **Density:** on-slide bullets are prompts, not scripts. Keep ≤ 5 lines/slide.
- **Tone:** confident about the model and the design discipline; precise and
  un-defensive about what's still provisional. This audience rewards both.
