# SVCv4 Data Model & Computational Design — presentation + learning tool

**Date:** 2026-09-18
**Audience:** **Software developers who need to generate, share, and consume v4
classifications — and their underlying evidence and assessments — across external
groups and knowledgebases (ClinVar being the flagship example).** Plus the curator
users those systems serve, and the scientific/technical people who evaluate the
approach. Assume **no prior GA4GH VA-Spec knowledge** — we *teach* the few entities
we rely on, we don't assume them.
**Goal:** Convey the computational modeling and coding design we're crafting for
release alongside the SVCv4 classification specification, and what a developer can
build against today.
**Dual use:** this file is the source for both the **~20-minute talk** (show the
**★ core** slides) and the **doc-native "Learn the model" learning tool** (all
slides, expanded — see the docsite plan). Slides without ★ are learning-tool depth /
compress-if-short.

## The spine: three principles the talk must land

1. **Show your work — the evidence travels with the verdict.** A v4 classification
   is the call *plus* the evidence and assessments that produced it, in one shared
   shape — so external groups and knowledgebases (ClinVar-style) can consume the
   *reasoning*, not just a label.
2. **One baseline, tuned — not forked.** Expert panels turn a v4 general version
   into a domain-specialized version by changing the **configuration behind workflow
   decision points** — re-weighting points, adding/limiting in-silico tools, and
   shifting the ranges for categorical (nominal) and ranked (ordinal) spectrums —
   never by rewriting the workflow or the record shape, and only **within limits
   that keep it SVCv4-compliant.**
3. **Every assessment travels with the identity of the ruleset that made it.**
   General vs specialized: the record names the exact version and per-line rules, so
   a result is never **opaque** about which rules linked its evidence to its
   assessments — it stays comparable, reproducible, and auditable.

**Five supporting concepts that set up and deepen the spine** (new, per Larry
2026-09-18): the **curator's real workflow** (slide 3); the **VA-Spec entities**
that hold a classification together (slide 6); the **SVCv4 profile that validates**
+ the open-data payoff (slide 8); **applied evidence** (slide 10) and **granularity
→ verifiability** (slide 11).

## Key takeaways (what the audience leaves with)

The whole deck **builds toward these four** — each segment adds one piece, and the
close (slide 23) restates them:

1. **A v4 classification is a computable record, not just a verdict** — the call
   *plus* the evidence and assessments behind it, in one shared, validatable shape.
2. **Standardizing the structure early lets tool-builders (a) assess consistently to
   the specification and (b) produce and consume results *with* their evidence** — so
   no one is inventing a private format, and we can trust results are made the same way.
3. **Granular applied evidence makes results verifiable and reusable** — precise
   data-points-bound-to-rules beat "a few PMIDs and a description," and scale as
   submissions grow.
4. **Every result carries the identity of the ruleset — baseline or specialized —
   that produced it** — comparable, reproducible, auditable across the community.

## Coverage & depth guidance

- Land the three principles + the worked example. Those are the talk.
- Keep the computing internals shallow (slides 16–17) — evidence the model works,
  not a code walkthrough.
- The talk shows the ★ slides (~20 min). The learning tool carries every slide and
  expands the curator-workflow, applied-evidence, and granularity material — that's
  where depth belongs, not the podium.

> **Two hard constraints on every slide:**
>
> 1. **Teach the VA-Spec entities plainly — don't hide them, don't drown in them.**
>    The audience doesn't know VA-Spec, so *introduce and define* the core entities
>    on first use — **Statement, Proposition, Evidence, Method, Contribution/Agent**
>    (slide 6) — in plain words. Keep property-name soup (`hasEvidenceLines`, SPOQ,
>    VRS) in speaker notes. Say "expert panels," not "VCEPs"; show codes as
>    `CLN_AFF (score +1.0)`, never `CLN_AFF_+1`.
> 2. **v4-only — no v3, and never the word "chaos."** Don't reference the 2015/v3
>    guidelines or old criteria codes (PVS1, PS/PM/PP/BA/BS/BP…). When motivating the
>    need for clear rules, frame it as **opacity / hard-to-verify results** when
>    evidence isn't clearly linked to the precise assessments — not "chaos."

> **Terminology — "assessment" (declared up front, then used consistently):** a
> **scored line of evidence is an assessment** — the evaluation a rule makes. Most
> assessments determine **points**; some determine an **intermediate factor** instead
> (e.g. the exon-relevance multiplier applied to positive initial predictive points).
> We use *assessment* for any such rule-level evaluation — a scored line of evidence —
> whether its output is points or a factor that feeds points.

> **Author note — VA-Spec version (do not present as version chatter):** the model
> shape tracks **GA4GH VA-Spec `1.1.0-ballot.2026-09`**
> (<https://va-spec.ga4gh.org/en/1.1.0-ballot.2026-09/>), which folds the old
> separate "EvidenceLine" class into a single recursive `Statement`. Reconcile the
> repo model/docs wording before presenting.

**Reusable visuals in the repo:** points-bands.png · summary-table.png ·
hod-workflows.png · variant-impact-workflows.png · the scope.md data-flow (redraw).
**Explainer graphics** (manifest at `docs/assets/images/explainers/README.md`):
slots marked `[EXPLAINER: …]`; several source artifacts still lead with old
`EvidenceLine`/v3 framing — apply the two constraints before use.

---

## Timing budget (★ core = the ~20-min talk)

| Segment | Slides | Time |
|---|---|---|
| Frame + how classification actually happens | 1–4 | 4 min |
| What a classification *is* (model + VA-Spec entities) | 5–7 | 3.5 min |
| Standards, sharing & applied evidence | 8–11 | 4 min |
| **Principle 2 — one baseline, tuned** | 12–13 | 2.5 min |
| **Principle 3 — identity of the ruleset** | 14–15 | 2.5 min |
| Computing layer (shallow) + worked example | 16–19 | 3 min |
| Build against today · status · close · Q&A | 20–24 | 2.5 min |

---

## ★ Slide 1 — Title

**On slide:**
- **A Data Model & Reference Computation for SVCv4 Variant Classification**
- Built on a shared GA4GH standard, for release alongside the ACMG/AMP/CAP/ClinGen
  SVCv4 Standards
- Presenter · SVCv4 Standards data-modeling team (ClinGen Data Platform WG)

**Speaker notes (~30s):** Who you are and the one promise: "By the end you'll know
how a v4 classification is made, how it's structured so it can be shared and
verified, and what you can build against today." This is the *data model and
reference code* — not the Standard itself and not the scoring authority.

---

## ★ Slide 2 — Why we're standardizing this *now*

**On slide:**
- Today a shared classification often doesn't show **how it was reached** — a few
  PMIDs and a description, and you're left guessing at the author's reasoning.
- SVCv4 is far more **granular** about *how each assessment is made* — but that only
  helps if the evidence is **captured and shared** in a common structure.
- Submissions to ClinVar and other tools are **growing fast**; visibility into the
  evidence and assessments is what lets the community reuse them **at scale.**
- So we're building the shared structure **early**, alongside the spec, so app
  builders can **(A) assess consistently to the specification** and **(B) produce and
  consume results *with* the evidence behind them.**

**Speaker notes (~1.5m — the motivation for the whole talk):** Be concrete about the
status quo: classifications get shared, but *how* the author got there is often
opaque — a handful of PMIDs and, if you're lucky, a prose description, with no
consistent, community-wide way to see which assessments were met or not and how the
evidence was actually applied. The earlier generation of guidelines was also less
granular about how the lower-level assessments in a workflow were performed, and it
built default strengths into the criteria codes themselves, which quickly obscured
how they were meant to be used. SVCv4 is much more granular and specific — but
granularity only pays off if the structure to carry it exists and everyone uses it.
Timing matters: variant-classification submissions to ClinVar and other resources are
growing enormously, so visibility into the evidence and the assessments at each level
is what will let others actually reuse shared data — for better care and faster
discovery. That's why we standardize the structure and coding *early*, before tools
proliferate: everyone assessing to the spec does it consistently (A), and results
*and their evidence* can be produced and consumed across the community (B).
*(Principled framing only — no old criteria codes, no "chaos.")*

*Visual: points-bands.png, or a "PMIDs + a shrug" vs "structured, applied evidence"
contrast.*

---

## ★ Slide 3 — How a variant actually gets classified today *(the curator's workflow)*

*Lead here to hook a developer audience: the real, manual work comes before any
model or score.*

**On slide:**
- A variant (in a gene) needs a classification. In practice the curator:
  1. **Sets the context** — disease, inheritance, canonical transcript — refined as
     they go (sources like GenCC for gene–disease validity & inheritance).
  2. **Gathers evidence** from knowledge sources — gnomAD (frequency), ClinVar
     (prior calls), VEP (consequence/transcript), PubMed & literature (cases,
     functional studies).
  3. **Manually curates case-level data** — judging which cases are *relevant* to
     each assessment.
- Reality today: **no structured case registries** — it's search, read, and
  hand-curate from papers (open + paywalled), plus deidentified clinical cases where
  a site has them.

**Speaker notes (~1.5m — grounds the whole talk):** Open on the real, manual, expert
process before any model or score appears — that's what hooks builders. Two things to
land: (1) context is established up front and *revised along the way* — the disease/
inheritance/transcript you assume can change as evidence comes in. (2) A lot of the
work is deciding **relevance** — which observations actually bear on the assessment.
Note the honest gap: curated case data in a structured, reusable form basically
doesn't exist yet, so everyone re-does the reading. And curators often find data
that's *interesting but out of scope* for the current assessment; today it's
discarded, but captured well it could save others the same effort or resurface later
if the scope shifts. That waste is exactly what structure + sharing can fix
(slides 10–11).

*Visual: a simple 3-step flow with the source logos/names (GenCC, gnomAD, ClinVar,
VEP, PubMed) feeding "curated cases."*

---

## ★ Slide 4 — Three groups, three jobs (and the seam between them)

**On slide:** (table)

| Owns | Who | What |
|---|---|---|
| The **framework** | ACMG/AMP/CAP/ClinGen SVCv4 WG | Summary Table, codes, workflows, scoring approach |
| The **data model** | *This project* (ClinGen Data Platform WG offshoot) | The **shape** of a classification — for interoperability |
| The **methods/rules** | A **method/ruleset model** (not yet built) + registries/tools | **Evaluate** evidence and produce the scores |

- They meet through **codes**: our record *names* a rule/version code; the
  method/ruleset side *defines* what it does. **ClinGen CSpec is one early
  implementer** of such a registry — not the standard, not the only tool.

**Speaker notes (~1m):** Now that they've seen the real work, place the players:
what our artifact is authoritative for and what it isn't. We don't author the
Standard and don't own the scoring rules. The "methods/rules" side is itself a
**model that doesn't exist yet** — how workflow configuration and rulesets are
structured so experts can build specialized versions and register them. CSpec is one
early implementer; not a de-facto standard. We model *what a classification is* so it
can link, by code, to whichever implementation produced it. That code seam is the
hinge for slides 12–15.

---

## ★ Slide 5 — What a classification *is*: evidence that nests

**On slide:**
- A **classification** is a **claim about a variant and a condition** — with a
  **direction** (for / against) and a **score**.
- That top claim is backed by **lines of evidence**.
- Each line of evidence is itself a **small scored claim**, backed by more evidence
  lines or by the **captured facts** underneath.
- So the record **nests** — same shape at every level. That uniformity makes it
  computable and auditable.

**Speaker notes (~1m):** Draw nesting boxes, no jargon yet (the next slide names the
pieces). The whole model is one recursive shape: a scored, directional claim,
supported by smaller scored claims, down to the raw captured data. Every scored box
in SVCv4 is one of these.

*Visual: nesting boxes — Classification ⊃ evidence line ⊃ captured facts.*

---

## ★ Slide 6 — What holds it together: the VA-Spec entities *(plain-language)*

**On slide:**
- **Statement ⇄ Proposition** — a **Statement** makes a claim about a
  **Proposition** (the possible fact: *"this variant is pathogenic for this
  condition"*), with a direction and a score.
- **Statement ⇄ Evidence** — the Statement is **backed by evidence**: the lines of
  evidence and the captured items/data beneath them (the nesting from slide 5).
- **Method** — every Statement names the **method/ruleset** that produced it (the
  *how*).
- **Contribution + Agents** — it also records **who did what, when** — the
  contributing agents (curator, expert panel, software) and their roles.

**Speaker notes (~1.5m — teach these; they recur all talk):** These four ideas come
from GA4GH VA-Spec, and they're worth naming because the rest of the talk uses them.
A **Statement** is the unit — it *asserts or assesses* a **Proposition**, the claim
being evaluated. It's held up by **Evidence** — and because an evidence line is
itself a Statement, evidence and claim share one shape. Two more make a result
trustworthy: the **Method** (which ruleset produced this — the pointer that carries
version identity, slides 14–15) and **Contributions by Agents** (who curated,
reviewed, approved, and when). So a classification isn't a bare verdict — it's a
claim, its evidence, the method behind it, and the people/agents who made it. *For
the technically curious: these are VA-Spec's `Statement` / `Proposition` /
`hasEvidenceLines` / `specifiedBy` (Method) / `contributions` (Agents).*

*Visual: the nesting diagram from slide 5, now labeled Statement / Proposition /
Evidence, with side tags for Method and Contribution-Agents.*

---

## Slide 7 — The Summary Table is the map

**On slide:**
- The SVCv4 **Summary Table** organizes all the evidence: **categories → concepts →
  codes**, and each **code opens a workflow** (a guided set of steps).
- Each workflow produces a **score** that **rolls up** to its code — with **caps.**
- Every scored box becomes **one line of evidence** in the record.

**Speaker notes (~1m):** How the Standard's own picture becomes our data structure —
nothing new to learn, it's the table curators already use. Pink = where a workflow
starts; green = capped roll-ups. It lines up one-to-one with the nesting claims from
slides 5–6, and each decision point inside a workflow is where the "dials" of
slide 13 live.

*Visual: summary-table.png.*

---

## ★ Slide 8 — Build on GA4GH — and a SVCv4 profile that *validates*

**On slide:**
- To share and compare classifications, they need a **common, computer-readable
  shape** — GA4GH already publishes one for variant knowledge; we **build on it.**
- We add a **SVCv4 profile**: SVCv4-specific constraints on top, so a classification
  can be **validated for conformance** — a machine can confirm it *is* a well-formed
  SVCv4 result, not just plausible-looking.
- **Why common standards help open data sharing:** validate once and anywhere ·
  exchange without re-negotiating formats · aggregate across labs · **reuse
  evidence** · far less manual reconciliation · build tooling once, use everywhere.

**Speaker notes (~1m — Principle-3 setup + concept #3):** Two moves. First, we don't
invent a serialization — we constrain GA4GH's shared shape. Second, and important for
a producer/consumer: the **profile is a validation contract**. A profile spells out
what an SVCv4 classification must contain and how it must be structured, so any tool
can *check* a record before trusting or ingesting it — the difference between "looks
right" and "provably conformant." Then the general payoff of common standards: open
data sharing stops being a series of one-off format negotiations. You validate once,
exchange freely, aggregate across sources, and — the theme of the next two slides —
**reuse the evidence** instead of re-curating it. *For the curious: this is a
VA-Spec community profile.*

---

## ★ Slide 9 — Principle 1: a record you can inspect, not a label you must trust

**On slide:**
- A v4 classification carries the **evidence and assessments** that produced it —
  not just the verdict. "Show your work" is built in.
- The captured facts live **under the line that scored them**; when the record is
  shared, that reasoning travels with it.
- One **shared, validatable shape** → a lab's record and a knowledgebase's record
  are the same shape; the same tooling processes either.
- A **ClinVar-style consumer** gets the *reasoning* and can re-derive, compare, or
  challenge the call — not just trust it.

**Speaker notes (~1m — Principle 1):** The interoperability payoff and the
developer's plug-in point. When a lab generates a classification, the structured
evidence lives inside the record under the line that scored it; sharing it sends
"why," not just "Likely Pathogenic." **Honest on ClinVar:** it's the flagship
*example* of a consuming knowledgebase, not a shipped integration — today it appears
in the model as a variant-id namespace and a source of external evidence. Say "the
kind of knowledgebase that would consume these records."

*Visual: `[EXPLAINER: a representative workflow]` beside a trimmed record.*

---

## ★ Slide 10 — Applied evidence: evidence bound to a precise rule

**On slide:**
- Curated evidence becomes **applied evidence** when it's attached to a **specific
  rule** inside a method — a subcode / subrule, the exact scoring opportunity it
  feeds.
- Applied evidence = the **minimal data points** that rule needs **+ enough
  provenance** to know where they came from.
- Because it's unambiguous, the rule can be evaluated **manually or
  computationally** — no guesswork about *how* it applies.
- This is the **best data to share** in the result: others see exactly how the
  outcome was reached.

**Speaker notes (~1.5m — concept #6, the heart of the applied story):** Distinguish
*collected* evidence (a paper, a cohort, a prediction) from **applied** evidence — the
specific data points, pinned to the specific rule they satisfy, with their
provenance. A rule (a subcode/submethod) asks a precise question; applied evidence is
the minimal, provenanced answer to *that* question. When evidence is applied at that
level, there's no ambiguity in how the rule was satisfied — a human or a machine can
evaluate it the same way. And it's exactly what you want to publish in the final
result: a consumer doesn't just see the score, they see the precise data-to-rule
links behind it. This is what makes "show your work" verifiable rather than
narrative.

*Visual: one captured source → several extracted data points → each pinned to a named
subrule with a score; provenance tags on the data points.*

---

## ★ Slide 11 — Granularity determines verifiability (and reuse)

**On slide:**
- The same evidence can be applied **coarsely** ("this paper supports pathogenicity")
  or **granularly** (this data point → this rule → this score).
- **Coarse** → the result can't be re-verified without **manual re-reading**; the
  evidence barely reuses.
- **Granular applied evidence** → results are **computationally verifiable**, and the
  evidence is **reusable** by others with far less manual review.
- The goal — **verifiable results** — depends on *how precisely* evidence is applied.

**Speaker notes (~1m — concept #4):** This is the argument for the whole design. If a
classification just cites sources at a coarse level, anyone who wants to verify it has
to re-read those sources and re-derive the judgment — expensive, manual, and not
reusable. If instead the evidence is applied granularly — specific data points bound
to specific rules — a machine can check the result, and the next curator can reuse
those applied data points instead of starting over. Granularity is the lever between
"trust me, I read the papers" and "here is the checkable, reusable chain." It's also
where the manual-effort-today vs computational-efficiency-tomorrow contrast lands:
same evidence, radically different verifiability depending on how precisely it's
applied and shared.

*Visual: a split — left "coarse: cite paper → manual re-read to verify"; right
"granular: data point → rule → score → machine-verify + reuse."*

---

## ★ Slide 12 — Principle 2: one baseline, tuned — not forked

**On slide:**
- SVCv4 ships **one baseline** set of workflows — same steps, weights, thresholds
  for every gene.
- Biology isn't uniform, so it's built to be **tuned, not rewritten**: expert panels
  author **specialized versions** by changing the **configuration behind decision
  points** — never the workflow structure.
- The **record keeps the same shape** either way; only the *rule behind a named code*
  changes.
- Baseline is the **operative default** wherever no specialization applies.
- **Within limits:** a specialization can tune only so far and still be
  **SVCv4-compliant** — the bounds keep "specialized" from meaning "a different
  standard."

**Speaker notes (~1.5m — Principle 2, part 1):** SVCv4 is designed to be *tuned, not
rewritten*. Everyone starts from the same baseline workflows and data shape; a panel
encodes disease-specific knowledge by adjusting the configuration at decision points,
and neither the workflow nor the record shape changes. For a developer that's the
guarantee: build one pipeline, it works whether a result came from the baseline or a
specialization — the only difference is which rule a code resolves to. And there are
**reasonable limits** to how far a specialization can alter the rulesets and still
claim to be SVCv4 — that compliance boundary keeps the ecosystem coherent. The
baseline is always the fallback, so labs aren't blocked waiting.

---

## ★ Slide 13 — Principle 2: three dials a specialization can turn

**On slide:**
- **Re-weight the points** at a decision point — e.g. how much a predicted
  loss-of-function counts, given the gene's mechanism and which exons matter.
- **Add or limit predictive tools** — mandate a gene-calibrated in-silico predictor;
  add an in-house one; down-weight or disallow one that misbehaves.
- **Shift thresholds/ranges** — categorical buckets *and* ranked bands — e.g. move a
  frequency band edge, or set a disease-specific diagnostic-yield cutoff.
- Same workflow, same codes, same record — **only the numbers and tool lists behind a
  step change.**

**Speaker notes (~1m — Principle 2, part 2):** One real example per dial.
**Weights:** the baseline scales predicted-impact points by mechanism and exon
relevance; a panel can override per gene. **Tools:** the missense workflow lists
several calibrated predictors and makes you pick one; a panel can require a gene-tuned
one or down-weight an over-caller. **Thresholds:** frequency bands and yield cutoffs
are exactly what a panel calibrates to its disease. In every case the decision point,
code, and record shape are untouched — only the configuration moves. Keep it
principle-level.

*Visual: the workflow with three callouts (a weight, a tool list, a threshold band).*

---

## ★ Slide 14 — Principle 3: a namespaced, versioned identity for every ruleset

**On slide:**
- Every classification and scored line **names the exact rule + version** that
  produced it — a stable id, not just a number.
- The **baseline is a namespace** (e.g. `SVC.v4`), and its individual coded rulesets
  are **versioned too** — e.g. `CLN_AFF.v4`, stamped to the baseline that defined or
  last changed it.
- A **specialization registers its own id** off the baseline — e.g. a Hearing Loss
  panel's `HL.v1` (based on `SVC.v4`).
- **Reference or replace:** use a baseline rule unchanged → **reference** it
  (`CLN_AFF.v4`); deviate → **define a replacement rule with its own id.**

**Speaker notes (~1.5m — Principle 3, part 1):** The mechanism that makes "bind the
result to its version" real. Picture a namespaced, versioned registry. The baseline
is a namespace, `SVC.v4`; even individual coded rulesets carry versions —
`CLN_AFF.v4` — stamped to the baseline where that rule was first defined or last
updated. A panel — say Hearing Loss — registers its own id, `HL.v1`, based on
`SVC.v4`. If `HL.v1` uses a baseline rule exactly, it just **references**
`CLN_AFF.v4`; the moment it deviates, it **defines a replacement rule with its own
id**. So a consumer reading any assessment can trace the precise rule — baseline or
specialized, referenced or replaced — that produced it. *(Syntax illustrative, not
finalized.)* In plain terms: **every assessment travels with the identity of the
ruleset that made it.**

---

## ★ Slide 15 — Principle 3: verifiable, comparable, auditable (and where we stand)

**On slide:**
- **Comparable** — two scores mean the same thing only when they cite the same rule
  ids; the record lets you check.
- **Reproducible** — re-resolve the named versions and rules, recompute.
- **Auditable** — the record shows the exact rule id behind each piece of evidence.
- **Versions move independently:** a specialization can fix itself without a baseline
  change; a baseline bump (`SVC.v4` → `v4.1` / `v5`) makes specializations revise and
  **re-register.**
- **Honest status:** the fields exist **today**; stamping isn't yet mandatory and the
  method/ruleset model + registry are **still to be built** (CSpec an early
  implementer); no "who/when" stamp yet.

**Speaker notes (~1m — Principle 3, part 2):** The payoff for a producer/consumer —
decide whether two results are comparable, recompute from the same named rules, audit
how each point was earned. Stress independence and the cascade: `HL.v1` can be
corrected on its own schedule; when the committee changes the baseline, every
specialization revises and re-registers, so a consumer is never guessing which
baseline a specialization sat on. Be straight about current state: the slots are in
the model, but version-stamping is optional, the code scheme isn't finalized, and the
method/ruleset model itself isn't built yet — plus no who/when stamp. The principle is
settled; building the method side is the work ahead.

---

## ★ Slide 16 — The reference computation layer (why it exists)

**On slide:**
- We built a **reference, non-authoritative scorer** in the repo.
- Purpose: **tests, worked examples, and the practice variant set** — proving the
  captured (and applied) evidence is sufficient to compute the documented points.
- **We are not the authority** — every result is non-authoritative by construction;
  the registered ruleset implementation governs.

**Speaker notes (~1m):** We're not the scorer of record. We wrote a mirror of the
documented point rules to prove — mechanically — that the data model captures
everything a scorer needs, *and* that granular applied evidence (slides 10–11) is
enough to compute a result without ambiguity. It's the first layer in the repo that
*computes* anything, and a handy **oracle** to diff your own scorer against. Don't
call CSpec "the authority" — it's one early implementer.

---

## Slide 17 — Engineering discipline (kept shallow)

**On slide:**
- Scoring is a **side-effect-free layer on top of** the data model — never woven in —
  so published schemas stay clean and the non-authoritative boundary is enforced by
  structure.
- **One shared pipeline, parameterized per workflow** — a new scorer is often *a
  small config table + one line*, not a rewrite.
- Every result carries a **step-by-step audit trail.**

**Speaker notes (~1m — brief):** The design *enforces* the boundaries the talk
claimed: scoring depends on the models, never the reverse, so nothing leaks into the
published schemas. We parameterized the shared shape of the ten variant-impact
workflows — differences (a point floor, a mechanism-only multiplier) are data, not
branches. This slide is *evidence of rigor*; don't walk the code.

*Visual: `[EXPLAINER: a NUL_/CDS_ or splice workflow]` — human tree, then "one small
config table."*

---

## Slide 18 — End-to-end: capture → apply → score → aggregate → classify

**On slide:**
- **Per-code scorers:** all 10 variant-impact workflows · population · all clinical
  codes · locus.
- **Aggregation:** family subtotals → per-proband clinical combine → cross-proband
  sum → one **(variant, disease) total.**
- **Classification band:** Benign / Likely Benign / VUS (low/mid/high) / Likely
  Pathogenic / Pathogenic.

**Speaker notes (~1m):** The reference layer runs the whole way — from captured and
applied evidence, through each code, up through aggregation, to a banded
classification — *real and tested*. Remaining pieces: the co-segregation locus code
(values now in hand) and applicability enforcement.

*Visual: clean left-to-right pipeline.*

---

## ★ Slide 19 — Worked example (the anchor)

**On slide:**
- One practice-set variant, end to end: captured facts → **applied** to codes →
  scored lines of evidence (each with its code + score) → combined total → band.
- Show the **audit trail** for one code.

**Speaker notes (~2.5–3m — the anchor):** Pick one clean example from the practice
set (32 encoded, CI-validated). Show captured fields, then the applied evidence and
the scored lines it produces — each with its code, direction, and score — then the
roll-up and band. Emphasize **code = identity, score = outcome, shown separately**
(`CLN_AFF (score +1.0)`), and that the same nested, applied structure is what another
system consumes. This is where the whole talk becomes concrete.

> Prep: choose beforehand; a monoallelic affected-clinical or a nonsense case reads
> cleanest. Trim the JSON. Pair with a matching `[EXPLAINER: …]` graphic if one
> exists.

---

## ★ Slide 20 — What you can build against today

**On slide:**
- **JSON Schemas** for every entity — generated from the model, CI-enforced.
- Two record shapes: the **inputs** you submit (evidence going in) and the
  **rolled-up classification** (scored, coming back).
- **32 validated worked examples** as ready-made fixtures — traceable to source.
- The **reference scorer** as an oracle for your implementation's expected points.

**Speaker notes (~45s):** You don't wait for the guideline to start — the contract is
JSON Schema generated from the model, CI-enforced. Two shapes: the case record you
submit, the rolled-up classification that comes back. Test against 32 real curated
pilot variants. Caveat: the Standard isn't finalized — shapes are stable enough to
build against; illustrative scores aren't spec-locked.

---

## Slide 21 — Honest about the edges

**On slide:**
- **Solid:** the shared-standard foundation, the scope boundary, the Case model, the
  schemas, evidence capture across all categories, the end-to-end reference scorer.
- **In progress:** aligning record wording to the base standard's latest
  simplification; the scoring map; workflow write-ups; the method/ruleset model.
- **Open questions for the Working Group:** a few Supplementary-Material
  boundary/typo points — all in the code's audit trail and `known-gaps`.

**Speaker notes (~45s):** Credibility from naming gaps precisely. Recent win: two
figure-only rules we'd had to assume are now resolved against the source figures — one
corrected an assumption. We log approximations for confirmation rather than hide them.

---

## Slide 22 — Timeline & deliverables

**On slide:**
- **~October 2026** — SVCv4 Standards published in *Genetics in Medicine*; the model
  release aligns to it.
- Draft access before publication: the **data model** (JSON Schema + docs) and
  learning examples/use cases.
- Specialized methods via a forthcoming **method/ruleset registry** (public API +
  docs) — CSpec is one early implementer.

**Speaker notes (~30s):** Set the clock; draft artifacts are available ahead of the
GIM publication for developers who want to start.

---

## ★ Slide 23 — Key takeaways

**On slide:**
- **A v4 classification is a computable record, not just a verdict** — the call
  *plus* the evidence and assessments behind it, in one shared, validatable shape.
- **Standardizing early lets tool-builders (a) assess consistently to the spec and
  (b) produce and consume results *with* their evidence** — no private formats.
- **Granular applied evidence makes results verifiable and reusable** — precise
  data-points-to-rules beat "a few PMIDs and a description," and scale as submissions grow.
- **Every result carries the identity of the ruleset — baseline or specialized —
  that produced it** — comparable, reproducible, auditable.
- *One line:* **the Standard defines the framework; a method/ruleset layer (yet to
  be built) defines the methods; we define the shape — so SVCv4 classifications and
  their evidence are computable, shareable, and verifiable.**

**Speaker notes (~45s):** The four things to leave with — recap each in a sentence,
tying back to the worked example they just saw. Then the one-liner as the capstone.
Invite engagement: repo, docs, feedback. *(These match the "Key takeaways" anchor at
the top of this deck — the whole talk built toward them.)*

---

## Slide 24 — Credits & Q&A

**On slide:**
- Key contributors: Alicia Byrne, Larry Babb, Christine Preston, Neethu Shah
  *(+ the wider data-modeling team)*
- Repo + docs links · contact · **Questions**

**Speaker notes:** Keep 2 min. Pre-load: *"Is this the scorer of record?"* (No — the
registered ruleset implementation is; ours is a reference oracle. CSpec is one early
implementer.) *"How do specializations fit?"* (Same record shape; the code resolves to
a different rule/version — slides 12–15, within compliance limits.) *"How do I know
which version produced a result?"* (Named on the record; resolution via the
forthcoming registry.) *"Can ClinVar consume this today?"* (Motivating use-case, not a
shipped integration.) *"Why build on an outside standard?"* (Interoperability +
inherited tooling + validation.) *"When can I depend on it?"* (Draft now, aligned to
~Oct 2026.)

---

## Delivery notes

- **Protect the spine + the new supporting concepts.** The curator workflow (4), the
  VA-Spec entities (6), applied evidence + granularity (10–11), and the worked example
  (19) are what make the talk land — don't cut into them for time.
- **Cut levers if long:** slide 7 (summary table) and slide 17 (engineering) compress
  first; slides without ★ are learning-tool depth.
- **Density:** on-slide bullets are prompts, not scripts. ≤ 5 lines/slide.
- **Tone:** confident about the model and design discipline; precise and un-defensive
  about what's provisional. Never say "chaos" — say opaque / hard to verify.

---

## Appendix — Embedding this as a docsite learning tool (feasibility)

**Question:** can this live in the docs site under **Getting Started** as a learning
tool? **Yes — best as a doc-native "Learn the model" learning path, not embedded
slides.**

**Recommendation (Option A — doc-native path):** rebuild the talk as a short
**numbered sub-series** under Getting Started, using only extensions the site already
enables (admonitions, `pymdownx.tabbed`, tables, `mermaid` superfences, existing
PNGs). Single source of truth (prose native to docs, not duplicated into a deck),
inherits light/dark + search, self-contained/offline, passes the `strict` build with
**no new dependencies**. For a *developer* learning tool a scannable, deep-linkable
lesson beats a projector deck; the live talk stays a separate artifact. **Effort ≈
0.5–1 day** for the core; the new supporting concepts (curator workflow, applied
evidence, granularity) are where the learning tool goes *deeper* than the talk.

**Suggested page split:**

1. **Why & how classifications are made** — slides 1–4 (scope; the curator's real
   workflow, expanded with the knowledge-source detail and the out-of-scope-data /
   reuse point).
2. **What a classification is & how it's shared** — slides 5–9 (nesting diagram in
   **mermaid**; the VA-Spec entities; the profile-that-validates + open-data benefits;
   show-your-work).
3. **Applied evidence, versions & building** — slides 10–20 condensed (applied
   evidence + granularity as the centerpiece; Principles 2–3; a **mermaid** pipeline;
   a `tabbed` "human view / record" worked example; "build against today").

**Not embedded slides** — reasons (dual maintenance, light/dark mismatch, vendoring)
in the docsite simplification plan.

> **[DECIDE]** Larry: finalize the live-talk deck (this file), then decide whether to
> invest ~1 day to also publish the doc-native learning path (they share content).
