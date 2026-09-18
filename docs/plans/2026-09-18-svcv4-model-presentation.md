# SVCv4 Data Model & Computational Design — 20-minute presentation

**Date:** 2026-09-18
**Audience:** Scientific & technical — **system developers and their curator
users.** People who will *build software against* the model or *produce/consume*
classifications with it.
**Goal:** Convey the computational modeling and coding design we're crafting for
release alongside the SVCv4 classification specification, and what a developer can
build against today.
**Length:** 20 minutes. ~19 slides. Budget ≈ 1 min/slide, with 3 min held for the
worked example and 2 min for Q&A. Keep to **one idea per slide.**

> **⚠️ VA-Spec dependency — updated this week.** This deck builds on **GA4GH
> VA-Spec `1.1.0-ballot.2026-09`**
> (<https://va-spec.ga4gh.org/en/1.1.0-ballot.2026-09/>). The ballot **removes the
> separate `EvidenceLine` class**: an evidence line is now a **`Statement` nested
> under another `Statement`** via `hasEvidenceLines`. Slides 5–7 and 12–13 reflect
> the new Statement-centric shape. (Reconcile the repo's model wording to this
> before presenting — see slide 6 notes.)

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

**Speaker notes (~1m):** The v3→v4 shift: strength categories + combining rules →
granular points that can mix positive and negative evidence. That granularity is
powerful but fragile without a shared data structure. If every lab records the
underlying evidence differently, the points aren't comparable and can't be
recomputed or audited. The model is the substrate that makes points portable.

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
- **Classification Model** *(this repo)* — Statements, Propositions, Evidence
  Lines, Evidence Items. *What a classification is.*
- **Method Model** *(CSpec, outside this repo & outside VA-Spec)* — the
  methods/rules that evaluate evidence and produce workflow scores.
- They meet through **method codes & evidence codes** the Evidence Lines carry.
- **Baseline vs specializations:** the SVCv4 Standard is a baseline; VCEP
  specializations live in CSpec. We publish only the baseline profile.

**Speaker notes (~1m):** The junction is the key engineering idea: our Evidence
Lines *name* a method/evidence code; CSpec *defines* what that code does. That
clean seam is what lets the same classification record survive baseline today and
a VCEP-specialized method later without changing shape.

*Visual: redraw the scope.md data-flow: curator captures Evidence Items → CSpec
methods evaluate → Evidence Line (method code + items used + score).*

---

## Slide 5 — Our foundation: GA4GH GKS / VA-Spec *(the high-level entry point)*

**On slide:**
- **VA-Spec (Variant Annotation Specification)** — the GKS standard for
  computer-to-computer exchange of variant annotations. We build **on** it, not
  beside it.
- **Community Profiles** layer additional constraints on VA-Spec core classes to
  align with a specific guideline's terminology.
- **SVCv4 = a VA-Spec community profile** — the same pattern ACMG-2015 used. We
  inherit VA-Spec's classes and *constrain* them; we don't invent a serialization.
- Supported by **VRS 2.0 / Cat-VRS** for variant representation; lineage from
  ClinGen ERepo's SEPIO/JSON-LD.
- **Tracking `1.1.0-ballot.2026-09`** — the ballot that unifies the model around
  `Statement` (next slide).

**Speaker notes (~1m — this is the high-level "how we build on VA-Spec" beat):**
Start here conceptually. The whole project is "take a released GA4GH interoperability
standard and profile it for SVCv4." For developers that's the reassurance: if you
already speak VA-Spec, SVCv4 is a *profile you validate against*, not a new world —
and you inherit VRS for variant identity. Note that we track the spec closely: the
1.1.0 ballot dropped last week and simplified the core model, which we've already
absorbed. That responsiveness is part of the value — the profile moves with the
base standard.

---

## Slide 6 — What a classification *is*: the core entities *(VA-Spec 1.1.0)*

**On slide:**
- **`Statement`** — the one core class. A claim, made by an agent, about a
  Proposition — with a **`direction`** (supports / disputes / neutral),
  **`strength`**, and/or a numeric **`score`** (and an **`outcome`** summary).
- **`Proposition`** — the possible fact being assessed, structured as **SPOQ**
  (Subject, Predicate, Object, Qualifier(s)). e.g. *this variant is pathogenic
  for this condition.*
- **Evidence attaches two ways:**
  - **`hasEvidenceItems`** → captured evidence: **Study Results, Data Items, or
    other Statements.**
  - **`hasEvidenceLines`** → **nested `Statement`s**, each a discrete, scored,
    directional *argument* from evidence.
- **`specifiedBy`** → the **Method** (the code that resolves into CSpec).

**Speaker notes (~1.5m — the conceptual keystone, and what changed this week):**
Be explicit that VA-Spec `1.1.0-ballot` **removed the separate `EvidenceLine`
class.** An "evidence line" is now simply a **Statement nested under another
Statement** via `hasEvidenceLines` — with the child's proposition omittable when
it's the same as the parent's. So the model is *recursive*: a Statement can both
**aggregate** evidence lines and **be** an evidence line for a higher Statement.
This is cleaner than the old two-class split and it maps beautifully onto SVCv4:
the top Statement is the Variant Pathogenicity Classification; each scored node in
the Summary Table is a nested Statement (evidence-line role) carrying its code,
direction, and score. **Unifying rule (restated for 1.1.0): every scored node in
SVCv4 is a Statement in an evidence-line role.**

> **Repo reconciliation note:** our current model/docs still use the older
> distinct-`EvidenceLine` framing (Statement → EvidenceLine → EvidenceItem).
> Update wording to the nested-Statement shape before presenting; the *concept*
> (scored directional arguments rolling up) is unchanged, only the class structure.

*Visual: a small recursive diagram — Statement ▸ hasEvidenceLines ▸ Statement ▸ …
▸ hasEvidenceItems ▸ Study Result / Data Item. Replace the old two-box entity
slide from the deck.*

---

## Slide 7 — The Summary Table is the map

**On slide:**
- Four levels: **Evidence Category → Evidence Concept → Evidence Code → Workflow.**
- **Evidence Codes are the entry points** — each is where a workflow starts.
- A workflow produces a score that **bubbles up** to its parent code (with
  min/max caps).
- WG rule: *"any process, rule, or method that produces a score maps to a VA-Spec
  scored node"* — i.e. a **Statement in an evidence-line role** (1.1.0).

**Speaker notes (~1m):** This is how the Standard's picture becomes our object
graph. Pink boxes = workflow entry points; green boxes = capped roll-ups. Every
one of those maps 1:1 to a nested Statement (evidence-line role). So the Summary
Table isn't decoration — it's the schema of the evidence hierarchy, and its
nesting is literally the `hasEvidenceLines` recursion from the previous slide.

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
LOC_SEG (blocked on an image-only figure) and `validate_case` applicability
enforcement.

*Visual: a clean left-to-right pipeline diagram.*

---

## Slide 13 — Worked example (the 3-minute payoff)

**On slide:**
- One practice-set variant, end to end: captured Case → evidence codes fired →
  nested **Statements** (evidence-line role) carrying codes + scores → combined
  total → band.
- Show the **provenance trail** for one code.

**Speaker notes (~3m — the anchor of the talk):** Pick one clean example from the
practice variant set (32 encoded). Show the actual captured fields, then the scored
nodes it produces — each a Statement with its method code, direction, and score —
then the roll-up to a (VBC, MDE) total and the band. Emphasize: **code = identity,
score = outcome, shown separately** (`CLN_AFF (score: +1.0)`, never `CLN_AFF_+1`) —
and that the same nested-Statement structure is what another system would consume.
This is where the abstract model becomes concrete for a developer.

> Prep: choose the example before the talk; a monoallelic CLN_AFF or a Nonsense
> PFD case reads most cleanly. Have the JSON on the slide, trimmed. If the chosen
> example has a matching **`[EXPLAINER: <that workflow>]`** graphic, show it beside
> the JSON so the audience sees the human view and the computed record together.

---

## Slide 14 — Where the model meets CSpec

**On slide:**
- Evidence Lines carry **method codes + evidence codes** as references.
- CSpec resolves those codes into **definitions** (baseline + VCEP specializations).
- The same classification record is **version-aware**: baseline today, specialized
  method later — **no shape change.**

**Speaker notes (~45s):** Reinforce the seam from slide 4 now that they've seen a
real record. For an implementer: you store the code; you resolve it against the
CSpec registry at evaluation time. The model doesn't hard-code any scoring rule.

---

## Slide 15 — Honest about the edges

**On slide:**
- **Stable:** scope boundary, VA-Spec profile framing, Case model, schemas,
  capture across all categories.
- **Draft / in-flight:** reconciling the repo model to **VA-Spec 1.1.0's
  Statement-centric shape** (evidence lines as nested Statements); scoring map;
  PFD workflow prose; reference-scorer aggregation.
- **Open / flagged for the WG:** two image-only figures (SM18 Fig 1
  mechanism×exon cell; SM5 Fig 2 LOC_SEG point values); a few SM boundary/typo
  questions — all recorded in provenance and `known-gaps`.

**Speaker notes (~45s):** Credibility with a technical audience comes from naming
the gaps precisely. Every assumption we made where the source was an un-extractable
figure is flagged in the code's provenance *and* in the docs. We're not hiding
approximations; we're logging them for WG confirmation.

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
you're building a consumer, read Statements/Evidence Lines. If you're building a
scorer, diff against our reference results (remembering CSpec is the authority).

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
  shape — a VA-Spec profile that makes SVCv4 classifications computable,
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
*"How do VCEP specializations fit?"* (Same record shape; method code resolves
differently in CSpec.) *"Why VA-Spec and not a bespoke schema?"* (Interop +
inherited tooling.) *"When can I depend on it?"* (Draft now, aligned to the ~Oct
2026 GIM publication.)

---

## Delivery notes

- **Cut lever if you run long:** compress slides 5 and 14 (both are "trust the
  seam" points) and hold the time for the worked example (13) — that's what sells
  it.
- **Density:** on-slide bullets are prompts, not scripts. Keep ≤ 5 lines/slide.
- **Tone:** confident about the model and the design discipline; precise and
  un-defensive about what's still provisional. This audience rewards both.
