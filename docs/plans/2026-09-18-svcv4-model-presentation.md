# SVCv4 Data Model & Computational Design — 20-minute presentation

**Date:** 2026-09-18
**Audience:** **Software developers who need to generate, share, and consume v4
classifications — and their underlying evidence and assessments — across external
groups and knowledgebases (ClinVar being the flagship example).** Plus the curator
users those systems serve. **They are NOT VA-Spec-literate** — assume no prior
knowledge of GA4GH GKS, VA-Spec, VRS, or its class/property vocabulary.
**Goal:** Convey the computational modeling and coding design we're crafting for
release alongside the SVCv4 classification specification, and what a developer can
build against today.
**Length:** 20 minutes, ~20 slides. Budget ≈ 1 min/slide, 3 min held for the worked
example, 2 min for Q&A. **One idea per slide.**

## The spine: three principles the talk must land

The deck is built around three developer-facing principles (the through-line, not
just topics):

1. **Show your work — the evidence travels with the verdict.** A v4 classification
   is the call *plus* the evidence and assessments that produced it, in one shared
   shape — so external groups and knowledgebases (ClinVar-style) can consume the
   *reasoning*, not just a label. (Slides 4–7.)
2. **One baseline, tuned — not forked.** Expert panels turn a v4 general version
   into a domain-specialized version by changing the **configuration behind
   workflow decision points** — re-weighting points, adding/limiting in-silico
   tools, and shifting the ranges for categorical (nominal) and ranked (ordinal)
   spectrums — never by rewriting the workflow or the record shape, and only
   **within limits that keep it SVCv4-compliant.** (Slides 8–9.)
3. **Every assessment travels with the identity of the ruleset that made it.**
   General vs specialized: the record names the exact version and the per-line
   rules, so community data stays comparable, reproducible, and auditable — no
   chaos. The *method/ruleset model* those codes resolve into is a **separate
   model, not yet built**; the classification links to it. (Slides 10–11.)

## Coverage & depth guidance (per Larry — build it to see how far it can go)

- **Land the three principles above + the worked example.** Those are the talk.
- **Keep the computing internals shallow.** The scorer architecture (slides 12–13)
  is *evidence that the model works*, not a code walkthrough — one or two slides,
  not a deep dive. Depth lives in the docs, not the podium.
- **Cuttable if long:** slide 5 (build-on-GA4GH) and slide 13 (engineering
  discipline) compress first; protect the pillar slides (7–11) and the worked
  example (15).

> **Two hard constraints on every slide:**
>
> 1. **Plain language, not VA-Spec jargon.** The audience doesn't know VA-Spec.
>    Keep class/property names (`Statement`, `hasEvidenceLines`, `Proposition`,
>    SPOQ, VRS) **out of on-slide text** — say "the record," "a scored line of
>    evidence," "the captured facts." Technical names live in speaker notes as
>    *"for the technically curious,"* surfaced only if asked. Say "expert panels,"
>    not "VCEPs"; show codes as `CLN_AFF (score +1.0)`, never `CLN_AFF_+1`.
> 2. **v4-only — no v3.** Do **not** reference the 2015/v3 guidelines or any old
>    criteria codes (PVS1, PS/PM/PP/BA/BS/BP…). SVCv4 stands on its own. (Same
>    scrub is being applied to the docsite — see the simplification plan.)

> **Author note — VA-Spec version (do not present):** the deck's model shape tracks
> **GA4GH VA-Spec `1.1.0-ballot.2026-09`**
> (<https://va-spec.ga4gh.org/en/1.1.0-ballot.2026-09/>), which folds the old
> separate "EvidenceLine" class into a single recursive `Statement`. The slides use
> the plain-language nested-claim framing this implies; reconcile the repo
> model/docs wording before presenting.

**Reusable visuals already in the repo** (don't rebuild — pull these):

- Points bands — `docs/assets/images/points-bands.png`
- Summary Table — `docs/assets/images/summary-table.png`
- HOD workflows — `docs/assets/images/hod-workflows.png`
- Variant-impact (PFD) workflows — `docs/assets/images/variant-impact-workflows.png`
- Scope/data-flow diagram — the ASCII flow in `docs/overview/scope.md` (redraw clean)
- Entity/summary-table slides — `tmp/extracted/The_SVCv4_Standard_Data_Model/` and
  `tmp/extracted/TheSummaryTable_alignment_to_evidence_lines.ppt/`

**Workflow explainer graphics** (Larry's — manifest at
`docs/assets/images/explainers/README.md`): intended for **slides 7, 13, and 15**.
Slots marked `[EXPLAINER: <workflow>]`. Several source artifacts still lead with
old `EvidenceLine`/v3 framing — apply the two constraints above before use.

---

## Timing budget

| Segment | Slides | Time |
|---|---|---|
| Frame the problem & scope | 1–3 | 3 min |
| What a classification *is* (the model) | 4–6 | 4 min |
| **Principle 1 — show your work / share with ClinVar** | 7 | 1.5 min |
| **Principle 2 — one baseline, tuned not forked** | 8–9 | 2.5 min |
| **Principle 3 — bind results to their version** | 10–11 | 2.5 min |
| The computing layer (kept shallow) + worked example | 12–15 | 4 min |
| Build against today · status · close · Q&A | 16–20 | 2.5 min |

---

## Slide 1 — Title

**On slide:**
- **A Data Model & Reference Computation for SVCv4 Variant Classification**
- Built on a shared GA4GH standard, for release alongside the ACMG/AMP/CAP/ClinGen
  SVCv4 Standards
- Presenter · SVCv4 Standards data-modeling team (ClinGen Data Platform WG)
- Date

**Speaker notes (~30s):** Who you are and the one promise: "By the end you'll know
what we're publishing, how it's structured, and what you can build against today."
Set expectations — this is the *data model and reference code*, not the Standard
itself and not the scoring authority.

---

## Slide 2 — Why this exists

**On slide:**
- SVCv4 scores variant classification as **points** — each line of evidence carries
  a code and a point value; the points combine into a final call.
- Points only travel if the **evidence behind them is captured in a common,
  computable form** — "show your work."
- Goal: **produce, exchange, and consume** SVCv4 classifications across labs,
  systems, and knowledgebases — with the same meaning everywhere.

**Speaker notes (~1m):** Points can mix positive and negative evidence and sum to a
call. That granularity is powerful but fragile without a shared data structure: if
every lab records the underlying evidence differently, the points aren't
comparable, recomputable, or auditable. The model is the substrate that makes
points portable. *(Keep it v4-only — no "v3 vs v4," no old criteria codes.)*

*Visual: points-bands.png.*

---

## Slide 3 — Three groups, three jobs (and the seam between them)

**On slide:** (table)

| Owns | Who | What |
|---|---|---|
| The **framework** | ACMG/AMP/CAP/ClinGen SVCv4 WG | Summary Table, codes, workflows, scoring approach |
| The **data model** | *This project* (ClinGen Data Platform WG offshoot) | The **shape** of a classification — for interoperability |
| The **methods/rules** | A **method/ruleset model** (not yet built) + registries/tools | **Evaluate** evidence and produce the scores |

- They meet through **codes**: our record *names* a rule/version code; the
  method/ruleset side *defines* what it does.
- **ClinGen CSpec is one early implementer** of such a registry — not the
  standard, and not the only possible tool.

**Speaker notes (~1m):** The most important framing slide — what our artifact is
authoritative for and what it isn't. We do **not** author the Standard and we do
**not** own the scoring rules. Be precise about the third row: the "methods/rules"
side is itself a **model that doesn't exist yet** — how a workflow's configuration
and rulesets are structured so experts can build specialized versions and register
them for tools that curators use. **CSpec is one early implementer** of such a
registry; it is *not* a de-facto standard and *not* the only tool. We model *what a
classification is* so it can link, by code, to whichever method/ruleset
implementation produced it. That code seam is the hinge for the whole talk: it lets
the same record work under the baseline today and a specialized rule later (slides
8–11).

---

## Slide 4 — Build on a shared standard (GA4GH) *(plain-language foundation)*

**On slide:**
- To be **shared and compared** across labs and software, classifications need a
  **common, computer-readable shape** — not a PDF or a spreadsheet.
- **GA4GH** already publishes that shape for variant knowledge. We **build on it**
  instead of inventing our own.
- Our job: **add the SVCv4-specific rules on top**, so an SVCv4 classification is
  understood the same way everywhere.
- Payoff: **produce once, consume anywhere** — and we inherit GA4GH's tools for
  naming variants precisely.

**Speaker notes (~1m):** One idea: interoperability needs a shared structure, and
GA4GH already has one for variant knowledge (computer-to-computer exchange). We
publish SVCv4-specific constraints layered on top. *For the technically curious
only (off the slide):* this is a GA4GH VA-Spec community profile; we track it
closely — the base standard just simplified its model this month and we've absorbed
it; we lean on VRS for variant identity. From the podium say "the GA4GH standard,"
not "VA-Spec / VRS / community profile," unless asked.

---

## Slide 5 — What a classification *is*: evidence that nests

**On slide:**
- A **classification** is a **claim about a variant and a condition** — e.g. *"this
  variant is pathogenic for this condition"* — with a **direction** (for / against)
  and a **score**.
- That top claim is backed by **lines of evidence**.
- The key idea: **each line of evidence is itself a small scored claim**, backed
  either by more evidence lines or by the **captured facts** underneath.
- So the record **nests** — same shape at every level. That uniformity is what
  makes it computable and auditable.

**Speaker notes (~1.5m — the conceptual keystone):** Draw nesting boxes, no jargon.
The whole model is one recursive shape: a scored, directional claim, supported by
smaller scored, directional claims, down to the raw captured data. Every scored box
in SVCv4 is one of these. *For the technically curious (off the slide):* GA4GH calls
the box a `Statement`; an "evidence line" is just a Statement nested under another.
The base standard recently collapsed a separate "EvidenceLine" class into this
single recursive shape — which makes the plain-language story *truer*: it really is
the same thing at every level. Lead with "scored claims that nest," never class
names.

> **Repo reconciliation note (for us, not the audience):** the site + model still
> show the older three-box framing (Statement → EvidenceLine → EvidenceItem). Adopt
> the single nested-claim wording before presenting; the concept is unchanged.

*Visual: nesting boxes — "Classification (scored claim)" ⊃ "Evidence line (scored
claim)" ⊃ "Captured facts." Reuse this diagram all talk.*

---

## Slide 6 — The Summary Table is the map

**On slide:**
- The SVCv4 **Summary Table** organizes all the evidence: **categories → concepts →
  codes**, and each **code opens a workflow** (a guided set of steps).
- Each workflow produces a **score** that **rolls up** to its code — with **caps**
  (a category can't exceed its ceiling).
- Every one of those scored boxes becomes **one line of evidence** in the record
  (the nesting from the previous slide).

**Speaker notes (~1m):** How the Standard's own picture becomes our data structure —
nothing new to learn, it's the table curators already use. Pink boxes = where a
workflow starts; green boxes = capped roll-ups. The Summary Table isn't a diagram
off to the side — it *is* the shape of the evidence, one-to-one with the nesting
claims from slide 5. *(This is also the map onto which slide 8's "dials" sit — each
decision point lives inside one of these workflows.)*

*Visual: summary-table.png.*

---

## Slide 7 — Principle 1: a record you can inspect, not a label you must trust

**On slide:**
- A v4 classification carries the **evidence and assessments** that produced it —
  not just the verdict. "Show your work" is built in.
- Curators capture the inputs as **structured evidence** (population data, affected-
  proband observations, an in-silico score) — each under the line that scored it.
- One **shared shape** → a lab's record and a knowledgebase's record are the same
  shape; the same tooling validates and processes either.
- A **ClinVar-style consumer** gets the *reasoning* — observations, references,
  codes — and can re-derive, compare, or challenge the call, not just trust it.

**Speaker notes (~1.5m — Principle 1):** This is the interoperability payoff and the
developer's plug-in point. When a lab generates a classification, the structured
evidence lives *inside* the record under the line that scored it; when it's shared,
that evidence travels with it — so a partner or knowledgebase receives "why," not
just "Likely Pathogenic." The capture side is governed by a **Case model +
applicability matrix** (which fields are required/optional/conditional/excluded per
workflow) — that's the contract a capture UI builds to. **Honest framing on
ClinVar:** it's the flagship *example* of a consuming knowledgebase, not a shipped
integration — today it appears in the model as a variant-id namespace and as a
source of external evidence (a review star-rating), and as the motivating use-case.
Say "the kind of knowledgebase that would consume these records."

*Visual: `[EXPLAINER: a representative workflow]` beside a trimmed record showing
evidence items under an evidence line; fall back to hod-workflows.png.*

---

## Slide 8 — Principle 2: one baseline, tuned — not forked

**On slide:**
- SVCv4 ships **one baseline** set of workflows — same steps, weights, and
  thresholds for every gene.
- Biology isn't uniform, so the standard is built to be **tuned, not rewritten**:
  expert panels author **specialized versions** by changing the **configuration
  behind decision points** — never the workflow structure.
- The **record keeps the same shape** either way; only the *rule behind a named
  code* changes.
- Baseline is the **operative default** wherever no specialization yet applies —
  works on day one, sharpens over time.
- **Within limits:** a specialization can tune only so far — re-weight, restrict
  tools, shift thresholds — and still be **SVCv4-compliant**. The bounds keep
  "specialized" from meaning "a different standard."
- Why it matters: expert knowledge **without a hundred private forks.**

**Speaker notes (~1.5m — Principle 2, part 1):** The headline: SVCv4 is designed to
be *tuned, not rewritten*. Everyone starts from the same baseline workflows and the
same data shape; an expert panel encodes disease-specific knowledge by adjusting the
configuration at particular decision points, and neither the workflow structure nor
the record shape changes. For a developer that's the load-bearing guarantee: you
build one capture-and-consume pipeline and it keeps working whether a classification
came from the baseline or a specialization — the only difference is which rule a
code resolves to. Crucially there are **reasonable limits** to how far a
specialization can alter the rulesets and still *claim to be SVCv4* — that
compliance boundary is what keeps the ecosystem coherent. Those rulesets live in a
method/ruleset layer that is still to be built (CSpec is an early implementer of a
registry for them), which is why our model stays stable while the science evolves.
And the baseline is always the fallback, so labs aren't blocked waiting for a
specialization to exist.

---

## Slide 9 — Principle 2: three dials a specialization can turn

**On slide:**
- **Re-weight the points** at a decision point — e.g. how much a predicted
  loss-of-function counts, given the gene's mechanism and which exons matter.
- **Add or limit the predictive tools** — mandate a gene-calibrated in-silico
  predictor; add an in-house one; down-weight or disallow one that misbehaves for a
  gene.
- **Shift the thresholds/ranges** — both categorical buckets and ranked bands —
  e.g. move a frequency band edge, or set a disease-specific diagnostic-yield cutoff.
- Same workflow, same codes, same record — **only the numbers and tool lists behind
  a step change.**

**Speaker notes (~1m — Principle 2, part 2):** Make it concrete with three real
examples from the guidelines. **Weights:** the baseline scales a variant's
predicted-impact points by how firmly the disease acts through loss-of-function and
how relevant the exon is; a panel can override that per gene — force a
known-irrelevant exon to zero, or waive the reduction where an exon already holds
well-established pathogenic variants. **Tools:** the missense workflow lists several
calibrated in-silico predictors and requires you pick one up front; a panel can
require a specific gene-tuned one, add its own, or down-weight one that over-calls.
**Thresholds:** the population-frequency bands and the diagnostic-yield cutoffs are
exactly the kind of numbers a panel calibrates to its disease — even nudging where a
band boundary sits. In every case the decision point, the code, and the record shape
are untouched; only the configuration moves. *(Keep this at principle level — one
example per dial, not a rules deep-dive.)*

*Visual: the summary-table workflow with three callouts (a weight, a tool list, a
threshold band) — or a simple "3 dials" graphic.*

---

## Slide 10 — Principle 3: a namespaced, versioned identity for every ruleset

**On slide:**
- Every classification and every scored line **names the exact rule + version** that
  produced it — a stable id, not just a number.
- The **baseline is a namespace** (e.g. `SVC.v4`), and its individual coded rulesets
  are **versioned too** — e.g. `CLN_AFF.v4`, stamped to the baseline that defined or
  last changed it.
- A **specialization registers its own id** off the baseline — e.g. a Hearing Loss
  panel's `HL.v1` (based on `SVC.v4`).
- **Reference or replace:** use a baseline rule unchanged → just **reference** it
  (`CLN_AFF.v4`); deviate → **define a replacement rule with its own id**, so a
  consumer sees exactly which rule was used.

**Speaker notes (~1.5m — Principle 3, part 1):** This is the mechanism that makes
"bind the result to its version" real — worth being concrete. Picture a namespaced,
versioned registry. The baseline is a namespace, `SVC.v4`, and even the individual
coded rulesets inside it carry versions — `CLN_AFF.v4` — stamped to the baseline
where that rule was first defined or last updated. A domain-expert panel, say Hearing
Loss, registers its *own* identifier, `HL.v1`, declared as based on `SVC.v4`. The
elegant part: if `HL.v1` uses a baseline rule exactly, it simply **references**
`CLN_AFF.v4`; the moment it deviates, it **defines a replacement rule with its own
id**, and assessments scored by it point at that id. So a consumer reading any
assessment can trace the precise rule — baseline or specialized, referenced or
replaced — that produced it. *(Syntax like `SVC.v4` / `HL.v1` / `CLN_AFF.v4` is
illustrative of the scheme, not a finalized format.)* In plain terms: **every
assessment travels with the identity of the ruleset that made it.**

---

## Slide 11 — Principle 3: comparable, reproducible, auditable (and where we honestly stand)

**On slide:**
- **Comparable** — two scores mean the same thing only when they cite the same rule
  ids; the record lets you check.
- **Reproducible** — re-resolve the named versions and rules, recompute.
- **Auditable** — the record shows the exact rule id behind each piece of evidence.
- **Versions move independently:** a specialization can fix itself without a baseline
  change; when the committee bumps the baseline (`SVC.v4` → `v4.1` / `v5`),
  specializations revise and **re-register** off the new baseline.
- **Honest status:** the fields exist **today**, but stamping isn't yet mandatory and
  the method/ruleset model + registry are **still to be built** (CSpec an early
  implementer); no "who/when" stamp yet.

**Speaker notes (~1m — Principle 3, part 2):** This is the payoff for a developer
producing or consuming records — decide whether two classifications are even
comparable, recompute from the same named rules, audit how each point was earned.
Stress the independence: a specialization like `HL.v1` can be corrected on its own
schedule, and when the committee changes the baseline — `SVC.v4` to `v4.1` or `v5` —
every specialization revises and **re-registers** against the new baseline, so a
consumer is never guessing which baseline a specialization sat on. The resolution
target is a forthcoming method/ruleset registry — CSpec one early implementer, not
the standard. Be straight about current state: the slots are in the model, but
version-stamping is optional not enforced, the code scheme isn't finalized, and the
method/ruleset model itself isn't built yet — plus no who-ran-it/when stamp. The
principle is settled; building the method side is the work ahead. This candor is what
a technical audience trusts.

---

## Slide 12 — The reference computation layer (why it exists)

**On slide:**
- We built a **reference, non-authoritative scorer** in the repo.
- Purpose: **tests, worked examples, and the practice variant set** — proving the
  captured data is sufficient to compute the documented points.
- **We are not the authority.** Every result is marked non-authoritative by
  construction; the official registered ruleset implementation is what governs.

**Speaker notes (~1m):** We're *not* competing to be the scorer of record. We wrote a
mirror of the documented point rules so we can prove — mechanically — that the data
model captures everything a scorer needs. It's the first layer in the repo that
*computes* anything; everything before it was capture + documentation. It's also a
handy **oracle**: build your own scorer, diff against ours. Be careful not to call
CSpec "the authority" from the podium — it's one early implementer of the
method/ruleset registry; the authority is the registered SVCv4 ruleset, whoever
implements it.

---

## Slide 13 — Engineering discipline (kept shallow)

**On slide:**
- Scoring is a **side-effect-free layer bolted *on top of* the data model** — never
  woven in — so the published schemas stay clean and the non-authoritative boundary
  is protected by the code's structure, not just by documentation.
- **One shared pipeline, parameterized per workflow** — a new workflow scorer is
  often *a small table of caps + one line of delegation*, not a rewrite.
- Every result carries a **step-by-step audit trail** (what rule/cap was applied).

**Speaker notes (~1m — keep it brief per the depth guidance):** The one thing to
convey: the design *enforces* the boundaries the earlier slides claimed. Scoring
depends on the models, never the reverse, so no scoring detail leaks into the
published schemas. We found the shared shape of the ten variant-impact workflows and
parameterized it — differences like a point floor or a mechanism-only multiplier are
declared as data, not branched in code. Don't walk the code; this slide is
*evidence of rigor*, then move on. *For the curious:* pure `reference_score_*`
functions returning a `ScoreResult` with a `provenance` trail.

*Visual: `[EXPLAINER: a NUL_/CDS_ or splice workflow]` — show the human decision
tree, then "this whole tree is one small config table."*

---

## Slide 14 — End-to-end: capture → score → aggregate → classify

**On slide:** (pipeline)
- **Per-code scorers:** all 10 variant-impact workflows · population · all clinical
  codes · the first locus code.
- **Aggregation:** family subtotals → per-proband clinical combine → cross-proband
  sum → **one (variant, disease) total.**
- **Classification band:** the total maps to Benign / Likely Benign / VUS
  (low/mid/high) / Likely Pathogenic / Pathogenic.

**Speaker notes (~1m):** The reference layer now runs the whole way: from a captured
case, through each evidence code, up through aggregation, to a banded classification
— *real and tested*, the strongest evidence that the data model is sufficient.
Remaining pieces: the co-segregation locus code (point values now in hand from the
source figure — implementation pending) and applicability enforcement.

*Visual: a clean left-to-right pipeline diagram.*

---

## Slide 15 — Worked example (the 3-minute payoff)

**On slide:**
- One practice-set variant, end to end: captured facts → evidence codes fired →
  **scored lines of evidence** (each with its code + score) → combined total → band.
- Show the **audit trail** for one code.

**Speaker notes (~3m — the anchor of the talk):** Pick one clean example from the
practice variant set (32 encoded, all CI-validated). Show the actual captured
fields, then the scored lines of evidence — each with its code, direction, and score
— then the roll-up to a total and the band. Emphasize **code = identity, score =
outcome, shown separately** (`CLN_AFF (score +1.0)`, never `CLN_AFF_+1`), and that
the same nested structure is what another system consumes. This is where the
abstract model becomes concrete.

> Prep: choose the example beforehand; a monoallelic affected-clinical case or a
> nonsense variant-impact case reads most cleanly. Trim the JSON on the slide. If a
> matching `[EXPLAINER: <that workflow>]` graphic exists, show it beside the record
> so the human view and the computed record sit together.

---

## Slide 16 — What you can build against today

**On slide:**
- **JSON Schemas** for every entity — generated from the model, CI-enforced source
  of truth for any language.
- Two record shapes: the **inputs** you submit (evidence going in) and the
  **rolled-up classification** (scored, coming back).
- **32 validated worked examples** (the practice variant set) as ready-made
  fixtures — traceable to source.
- The **reference scorer** as an oracle for your implementation's expected points.

**Speaker notes (~45s):** You don't wait for the guideline to start building — the
contract exists as JSON Schema generated from the model, and CI fails if the
committed schemas drift, so what's published is what the model enforces. Two shapes
to know: the case record you submit with evidence going in, and the rolled-up
classification that comes back with scores attached. Test against 32 real curated
pilot variants, not synthetic stubs. One caveat: the Standard isn't finalized —
treat schemas as advisory and expect field-level change; the *shapes* are stable
enough to build against, the illustrative *scores* are not spec-locked.

---

## Slide 17 — Honest about the edges

**On slide:**
- **Solid:** the shared-standard foundation, the scope boundary, the Case model, the
  schemas, evidence capture across all categories, the end-to-end reference scorer.
- **In progress:** aligning our record wording to the base standard's latest
  simplification; the scoring map; workflow write-ups.
- **Open questions for the Working Group:** a few Supplementary-Material
  boundary/typo points — all recorded in the code's audit trail and `known-gaps`.

**Speaker notes (~45s):** Credibility comes from naming gaps precisely. Recent win:
two figure-only rules we'd had to *assume* (a mechanism×exon edge cell, and the
co-segregation point values) are now resolved against the source figures — one of
them corrected an assumption we'd made. Every place we still infer is flagged in the
code's audit trail *and* the docs. We log approximations for WG confirmation rather
than hide them.

---

## Slide 18 — Timeline & deliverables

**On slide:**
- **~October 2026** — SVCv4 Standards published in *Genetics in Medicine*; the model
  release aligns to it.
- Draft access before publication: the **data model** (JSON Schema + docs) and
  learning examples/use cases.
- Specialized methods via a forthcoming **method/ruleset registry** (public API +
  docs) — CSpec is one early implementer.

**Speaker notes (~30s):** Set the clock. We're building toward the GIM publication;
draft artifacts are available ahead of it for developers who want to start.

---

## Slide 19 — Close: one sentence to remember

**On slide:**
- **The Standard defines the framework; a method/ruleset layer (yet to be built)
  defines the methods; we define the shape — built on a shared GA4GH standard so
  SVCv4 classifications, and the evidence behind them, are computable, exchangeable,
  and auditable.**

**Speaker notes (~30s):** Land the takeaway. Invite engagement: here's the repo,
here's the docs, here's how to give feedback.

---

## Slide 20 — Credits & Q&A

**On slide:**
- Key contributors: Alicia Byrne, Larry Babb, Christine Preston, Neethu Shah
  *(+ the wider data-modeling team)*
- Repo + docs links · contact
- **Questions**

**Speaker notes:** Keep 2 min for Q&A. Pre-load likely questions:
*"Is this the scorer of record?"* (No — the registered ruleset implementation is;
ours is a reference oracle. CSpec is one early implementer, not the standard.)
*"How do expert-panel specializations fit?"* (Same record shape; the code resolves to
a different rule/version in the method/ruleset registry — slides 8–11, within
compliance limits.) *"How do I know which version produced a result?"* (It's named on
the record; resolution via the forthcoming registry.) *"Can ClinVar consume this
today?"* (It's the motivating use-case, not a shipped integration; the shared shape
is what makes it possible.) *"Why build on an outside standard?"* (Interoperability +
inherited tooling.) *"When can I depend on it?"* (Draft now, aligned to the ~Oct 2026
GIM publication.)

---

## Delivery notes

- **Protect the spine.** The three principle pairs (slides 7, 8–9, 10–11) and the
  worked example (15) are the talk — never cut into them for time.
- **Cut levers if long:** compress slide 4 (build-on-GA4GH) and slide 13
  (engineering discipline) first.
- **Density:** on-slide bullets are prompts, not scripts. ≤ 5 lines/slide.
- **Tone:** confident about the model and the design discipline; precise and
  un-defensive about what's still provisional. This audience rewards both.

---

## Appendix — Embedding this as a docsite learning tool (feasibility)

**Question:** can this presentation live in the docs site under **Getting Started**
as a learning tool? **Yes — best as a doc-native "Learn the model" learning path,
not embedded slides.**

**Recommendation (Option A — doc-native path):** rebuild the talk as a short
**numbered sub-series (3 pages)** under Getting Started, using only extensions the
site already enables (admonitions, `pymdownx.tabbed`, tables, `mermaid`
superfences, existing PNGs). This keeps a **single source of truth** (prose lives
natively in docs, not duplicated into a deck), inherits light/dark + search for
free, is fully self-contained/offline, and passes the `strict` build with **no new
dependencies or CI changes**. For a *developer* learning tool, a scannable,
deep-linkable lesson beats a projector deck; the live talk stays a separate artifact.
**Effort ≈ 0.5–1 day.**

**Why not the alternatives:** a reveal.js deck embedded via iframe means dual
maintenance (slides drift from docs), a light/dark mismatch with the Material theme,
and vendoring ~1–2 MB of JS to stay offline; a CDN version fails the self-contained
requirement; a dedicated slides plugin isn't worth editing the pinned dependency set
for a single deck.

**Suggested page split** (maps the deck's segments):

1. **Learn the model · why & scope** — slides 1–4 (scope table; the code seam;
   build-on-GA4GH). Reuse points-bands.png; a `tabbed` "for the technically curious"
   aside for the scope boundary.
2. **Learn the model · what a classification is & how it's shared** — slides 5–7
   (nesting diagram in **mermaid**; summary-table.png; Principle 1 / show-your-work).
3. **Learn the model · versions, scoring & what you build against** — slides 8–16
   condensed (Principles 2–3; a **mermaid** end-to-end pipeline; a `tabbed` "human
   view / record" worked example; a compact "build against today" admonition).

**Nav placement:** append after `getting-started/first-case.md`, e.g.
`getting-started/learn/why-and-scope.md`, `.../what-a-classification-is.md`,
`.../versions-scoring-and-building.md`.

**Two caveats:** (1) the learning path must adopt the reconciled single
nested-claim wording, not re-import the older three-box framing still present in
`getting-started/show-your-work.md`; (2) the slide-7/13/15 explainer graphics don't
exist as stills yet (`explainers/` is a stub) — fall back to the existing
hod-workflows.png / variant-impact-workflows.png until they land.

> **[DECIDE]** Larry: build the live-talk deck first (this file), then decide
> whether to invest the ~1 day to also publish the doc-native learning path. The two
> share all their content, so the deck is the prerequisite either way.
