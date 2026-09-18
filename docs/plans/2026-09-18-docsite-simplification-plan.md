# Docs-site simplification & reorganization plan

**Date:** 2026-09-18
**Goal:** Reshape the site so it presents **only the most concrete decisions and
results**, ready to share with a **broad standards + informatics audience** for
the first time.
**Audience for this share:** GA4GH / ClinGen-adjacent scientists, standards
people, and system architects evaluating the approach — *not yet the general
public*. We keep a light "feedback welcome" framing but drop the named-reviewer,
internal-logistics posture.
**Status:** Proposal for Larry's sign-off. Decisions that need a human call are
tagged **[DECIDE]**.

---

## 1. The problem we're fixing

The current site was built as a **working review site for a named reviewer
list**. It is thorough and honest about being in-progress — but for a broader
first audience it has three frictions:

1. **Too much surface.** 5 tabs, ~30 narrative pages, a 17-item Reference tab, a
   17-item Workflows tree, and 32 example pages. A new visitor can't tell what's
   load-bearing.
2. **Provisional and settled content sit side-by-side** with no consistent
   signal of which is which. A broad audience will read a draft stub as a claim.
3. **The front door speaks to insiders.** "Reviewing this site" assumes you were
   invited and told what to critique. A broader visitor needs "here's what this
   is, here's what's solid, here's what's still moving."

## 2. Principle: what counts as "concrete"

We keep a page in the shareable core **only if it states a decision we've made or
a result we can stand behind today**. Everything else is either (a) clearly
labeled as draft/placeholder, or (b) moved out of the primary nav.

**Concrete (keep, front-and-center):**

- The **scope boundary** — Classification Model (this repo) vs Method Model
  (CSpec) vs the Standards WG. This is our clearest, most-defensible decision.
- The **VA-Spec community-profile framing** and the **core entity model**
  (Statement / Proposition (SPOQ) / Evidence Line / Evidence Item).
- The **Summary Table → Evidence Code → Workflow** alignment.
- The **Case model + applicability matrix** (a real, tested artifact).
- The **worked examples** (practice variant set — 32 encoded).
- The **JSON Schemas** (generated, real).
- The **reference scorer** and the **scoring map** for the categories that are
  done (POP, CLN, LOC_PHE, PFD) — these are genuine results.

**Provisional (label or demote):**

- PFD per-workflow narrative pages (the model is captured, but the prose reads as
  in-progress).
- `known-gaps`, WG follow-ups, un-resolved figure assumptions (SM18 Fig 1, SM5
  Fig 2 / LOC_SEG).
- Anything that assumes the reader is a pre-briefed reviewer.

## 2a. Blocking content-accuracy item: VA-Spec 1.1.0 reconciliation **[DECIDE]**

VA-Spec **`1.1.0-ballot.2026-09`** (released the week of this plan) **removed the
separate `EvidenceLine` class**: an evidence line is now a **`Statement` nested
under another `Statement`** via `hasEvidenceLines` (with `hasEvidenceItems` →
Study Results / Data Items / other Statements). The site's entity framing
(`Statement → EvidenceLine → EvidenceItem`, e.g. on `reference/concepts.md`,
`getting-started/evidence-lines-and-items.md`, `reference/va-spec-profile.md`,
`reference/model.md`) reflects the **older two-class shape.**

**The audience is NOT VA-Spec-literate.** So this isn't about impressing VA
experts — it's that the site currently *teaches* a class (`EvidenceLine`) that no
longer exists in the base standard, and does so in vocabulary a general
scientific/informatics reader doesn't share. Two problems, one fix.

- **[DECIDE]** Do a **light terminology pass now** (before the share): (a) stop
  asserting a distinct `EvidenceLine` class — frame it as "a classification is a
  scored claim, backed by **lines of evidence**, backed by the **captured facts**;
  the same shape nests at every level"; (b) keep **class/property names
  (`Statement`, `hasEvidenceLines`, SPOQ, VRS) out of the narrative pages** — they
  belong only in `reference/va-spec-profile.md` / `reference/model.md` for readers
  who want them. This is wording, not a remodel — the *concept* (scored directional
  arguments rolling up under caps) is unchanged.
- Full Pydantic/schema remodel to the new base-standard shape can follow
  separately; the **docs** just need to stop teaching the retired class.
- Add a dated "Built on the GA4GH standard (VA-Spec `1.1.0-ballot.2026-09`)" line
  to `reference/va-spec-profile.md` and the Home scope block — reference pages only.

## 2b. Blocking content task: remove v3 criteria-code *mappings* (not principled differences)

**Refined intent (Larry, 2026-09-18):** the scrub is **not** about erasing the
high-level, *principled* differences between v3 and v4 — those are fine to state
(e.g. "v4 is points-based; v3 used strength categories + combining rules"; "a v4
code names the evidence *type*, with the points shown separately"). The scrub
targets any **mapping of a specific v3 criteria code to a v4 process** — anything
that implies a v4 assessment *is / equals / corresponds to* a v3 rule. **We do not
want v4 users to think there's a straightforward path from a v3 rule assessment to
v4, even though many assessments overlap or are similar.** Remove the v3 **code
token** *and* its **association to the v4 process** — wherever it lives: **text,
figures, or the explainer graphics.**

**Keep (principled, no code mapping):**

- "v4 is points-based; v3 used strength categories + combining rules" — the
  conceptual shift (`svcv4-in-brief.md`, `summary-table.md`, `glossary.md`).
- "v4 codes name the evidence type; the points are separate" — the code-shape
  principle (drop only the *v3 code examples* used to illustrate it).
- "SVCv4 succeeds the 2015 guidelines" / predecessor lineage — factual, not a
  per-rule mapping.

**Remove (v3 code ↔ v4-process mappings):**

| Location | Mapping to remove | Result |
|---|---|---|
| `overview/svcv4-in-brief.md` | the `PS4` / `PS4_Moderate` **code examples** in the "codes carry type" point | keep the principle; drop the v3 code tokens |
| `reference/summary-table.md` | the `PS4` / `PS4_Moderate` **code examples** in "code shape" | keep the shape principle; drop the v3 code tokens |
| `workflows/pfd/index.md` | "already capture much of v3's **PM1** 'critical domain' evidence" | state the v4 evidence directly; no PM1 / v3-process claim |
| `examples/v19-tp53.md` | "(**PM5**-type) evidence" | drop the code + "-type" association |
| `examples/v22-f8.md` | "same-AA (**PS1**) + same-codon (**PM5**)" | describe the v4 evidence; drop the `(PS1)`/`(PM5)` mappings |
| `examples/v5-myh7.md` | "**PM5**-type support" | reword to the v4 same-residue concept; no code |
| `reference/scoring-map/population.md` | "SVCv4 chose –3, not **BS1**'s –4" | drop the `BS1` equivalence |
| `reference/scoring-map/locus.md` | "(**BS4**-equivalent)" | drop the `BS4` equivalence |

**Also sweep (not yet audited for v3 codes):**

- **Figures** in `docs/assets/images/` — check any embedded v3 criteria codes /
  v3↔v4 mapping cells; re-export without them if found.
- **Explainer graphics** (the claude.ai artifacts + any exported stills in
  `docs/assets/images/explainers/`) — several predate this rule; audit each for v3
  code tokens or "= v3 X" mappings before use, per the manifest note.

**Preserve (false positives — do NOT scrub):**

- `PVS-v3-FOXG1` / `v3-foxg1` everywhere — that "v3" = **practice variant #3**, not
  ACMG v3 (all example IDs are `v1…v30`).
- `Sue Richards (OHSU)` in `reference/credits.md` — a contributor's name.
- `reference/va-spec-profile.md` line on the 2015 guidelines being an earlier
  VA-Spec profile — VA-Spec lineage, not a criteria-code mapping.

> Ready to execute on your go — text edits in one pass with `mkdocs build --strict`
> as the gate; figures/explainers audited separately (I can't re-export a PNG that
> has a baked-in v3 code without the source). **Source material**
> (`source-material/svcv4-supplements/SM02-v3-to-v4-status.txt` and the SM figures)
> is *inputs*, not published — leave as-is unless a figure with a
> visible v3 code gets embedded in the site.

> Treat this as **Tier A, item 0** — it gates "shareable with a technical
> audience" more than any nav change.

## 3. Cross-cutting simplifications (do these regardless of nav changes)

These three moves deliver most of the "feels shareable" benefit and are low-risk.

### 3a. A single maturity convention on every page

Add a one-line status admonition at the top of each page, drawn from a fixed set:

- **`Stable`** — a decision we stand behind; unlikely to change in shape.
- **`Draft`** — content is real but wording/detail is still settling.
- **`Placeholder`** — scaffold only; here for completeness, not yet a claim.

Implement as a reusable admonition (or a small `attr_list` badge) so it's visually
consistent. This replaces the current scattered, per-page "early development"
prose with **one signal the whole audience learns once.**

### 3b. Rewrite the front door for an outside reader

- **`overview/review-guide.md` → `overview/how-to-read.md`.** Keep the excellent
  "reading path" (it's genuinely good orientation). Drop the "what we'd like
  feedback on" checklist framing; replace with a short "What's solid vs what's
  still moving" section that points at the maturity labels. Move the specific
  feedback asks into `reference/contributing.md`.
- **`index.md`** — tighten to: what this is (one sentence), the scope boundary
  (one graphic/table), the points-based figure, and 3 "start here" links (not 5).
  Keep the "Early development" banner but make it point to the maturity legend.

### 3c. Publish a one-screen "What's in / what's out" status table

A single new page (or a section on Home) that lists each evidence category and
its state: **modeled / scored / documented / open**. This is the fastest way for
an evaluator to calibrate trust, and it's content we already know cold.

## 4. Proposed information architecture (nav)

**Guiding cut:** 5 tabs → 5 tabs, but each is shorter and clearly tiered. The
biggest reductions are in **Getting Started**, **Workflows (PFD)**, and
**Reference**.

### Overview (keep — it's the strongest tab)
- Home *(tighten)*
- How to read this site *(renamed from Reviewing this site)*
- SVCv4 Standards in brief
- How SVCv4 maps to the model
- What this project is — and isn't  ← **elevate; this is our best page**

### Getting Started (consolidate 7 → 4) **[DECIDE]**
Current: show-your-work · classification-inputs · assertion-framework ·
capturing-basic-evidence · evidence-lines-and-items · rolling-up-scores ·
first-case.

Proposed merge (fewer, stronger pages):
1. **Show your work: structured evidence** *(keep — the "why")*
2. **The classification inputs & assertion framework** *(merge inputs +
   assertion-framework)*
3. **Evidence Lines, Items & rolling up scores** *(merge
   evidence-lines-and-items + rolling-up-scores; fold in
   capturing-basic-evidence's essentials)*
4. **Capture your first case** *(keep — the payoff)*

> **[DECIDE]** Larry may prefer to keep all 7 (they build gently) and only
> relabel. The merge halves the click-depth for a first read; the cost is
> longer individual pages. Recommend the merge for the broad-audience share, and
> keep the granular pages in git history if we want them back.

### Workflows (keep HOD in full; tier PFD) **[DECIDE]**
- **HOD** stays as the showcase — POP, CLN (AFF/DNV/ALT/UAF), LOC are modeled and
  scored. This is our strongest "it actually works" evidence. Keep the full tree.
- **PFD**: collapse the **10 individual variant-type pages** behind the
  `pfd/index.md`. Reshape `pfd/index.md` into: the shared pipeline pattern +
  a **status table** (all 10 workflows, each marked `Draft`/`Placeholder` with a
  one-line "what it captures"). Keep the 10 pages reachable (linked from the
  table) but **out of the top-level nav** so the tab isn't 13 items deep.
- **Case model & applicability** stays.

> **[DECIDE]** The PFD workflows are captured in the model and have reference
> scorers, so they're more real than "stub." The question is only nav clutter,
> not deletion. Recommend collapsing into a status table for the first share;
> re-expand once the prose is `Stable`.

### Examples (keep; add a landing filter)
- 32 variant pages is fine **as a library** — but the flat nav list is
  overwhelming. Keep the pages; make `practice-variant-set/index.md` the real
  entry point with a **grouped/tabulated index** (by gene / disease area / what
  each illustrates) and **2–3 "start with these" featured examples**. Consider
  moving the 32 out of the sidebar and driving all navigation from the index page.

### Reference (17 → ~10 in nav; tier the rest) **[DECIDE]**
Keep in nav (the concrete reference set):
- Model reference · JSON Schemas · Summary Table · VA-Spec community profile ·
  Workflow scoring map · Reference scoring · Core concepts · Glossary ·
  Interop: GKS · Interop: CSpec · Credits.

Demote out of primary nav (reachable, not featured):
- **Evidence data structures**, **Spec coverage**, **Known gaps**, **Contributing**
  → group under a single **"Project status & contributing"** sub-section, or link
  from the relevant pages rather than listing each at top level.

> **[DECIDE]** `known-gaps` is valuable and honest — keep it, but reframe its intro
> for outsiders ("here's what we've *chosen* to defer and why") and file it under
> status rather than as a peer of Model reference.

## 5. Page-by-page disposition

| Page | Disposition | Note |
|---|---|---|
| `index.md` | **Simplify** | Tighten to scope + bands figure + 3 links; add maturity legend link |
| `overview/review-guide.md` | **Rename + rewrite** | → `how-to-read.md`; drop reviewer asks |
| `overview/svcv4-in-brief.md` | Keep | Mark `Stable` |
| `overview/alignment.md` | Keep | Mark `Stable` |
| `overview/scope.md` | **Elevate** | Best page; consider linking from Home prominently |
| `getting-started/*` (7) | **Merge → 4** | [DECIDE]; label survivors `Stable`/`Draft` |
| `workflows/index.md` | Keep | Add category status table |
| `workflows/hod/**` | Keep (full) | Showcase; mark `Stable` where scored |
| `workflows/pfd/index.md` | **Reshape** | Pipeline + 10-workflow status table |
| `workflows/pfd/<10 pages>` | **Demote from nav** | Reachable via index; mark `Draft` |
| `workflows/case-model.md` | Keep | Mark `Stable` |
| `examples/index.md` | **Rebuild as filtered index** | Featured + grouped |
| `examples/<32>` | Keep (library) | Drive from index, not sidebar |
| `reference/model.md` | Keep | Provisional banner → `Draft` badge |
| `reference/schemas.md` | Keep | `Stable` |
| `reference/summary-table.md` | Keep | `Stable` |
| `reference/va-spec-profile.md` | Keep | `Stable` |
| `reference/scoring-map/**` | Keep | `Draft`; strongest recent result |
| `reference/scoring.md` | Keep | Already well-scoped as non-authoritative |
| `reference/concepts.md` | Keep | `Stable` |
| `reference/glossary.md` | Keep | `Stable` |
| `reference/gks-interop.md` | Keep | `Stable` |
| `reference/cspec-interop.md` | Keep | `Stable` |
| `reference/credits.md` | Keep | `Stable` |
| `reference/evidence-structures.md` | **Demote** | → status/contributing group |
| `reference/spec-alignment.md` | **Demote** | → status/contributing group |
| `reference/known-gaps.md` | **Reframe + demote** | "what we deferred & why" |
| `reference/contributing.md` | Keep, absorb feedback asks | New home for review-guide's asks |
| `docs/Docsite Review Plan.md` | **Remove from repo** | Internal reviewer names — never ship |
| `docs/superpowers/**` | Leave (not in nav) | Working notes; confirm excluded from build |

## 6. Execution — two tiers for today

### Tier A — Minimum shareable cut (target: today)
The smallest set that makes the site honest and legible for a broad audience.

1. Add the **maturity-label convention** (3a) as a snippet + apply to Overview
   and Reference top pages.
2. **Rewrite Home + rename review-guide → how-to-read** (3b).
3. Add the **category status table** (3c) on `workflows/index.md` or Home.
4. **Reshape `pfd/index.md`** into pipeline + status table; drop the 10 PFD pages
   from the top nav (keep files + links).
5. **Rebuild `examples/index.md`** as a featured/grouped landing; drop the 32
   from the sidebar.
6. **Remove `docs/Docsite Review Plan.md`** from the repo (reviewer names).
7. `mkdocs build --strict` must pass; fix any broken internal links from moves.

### Tier B — Fuller consolidation (follow-on, this week)
8. Merge Getting Started 7 → 4 **[DECIDE]**.
9. Collapse the Reference demotions into a "Project status & contributing" group.
10. Reframe `known-gaps` intro for outsiders.
11. Apply maturity labels to every remaining page.
12. Optional: light visual polish (Home hero, consistent admonition styling).

## 7. Risks & open decisions

- **[DECIDE] Getting Started merge (7→4)** — recommend yes for the share; reversible.
- **[DECIDE] PFD page demotion** — recommend collapse-not-delete; the scorers make
  these real, it's purely a clutter fix.
- **[DECIDE] Reference demotions** — confirm `known-gaps` stays public (recommend
  yes; it signals rigor, not weakness).
- **Link integrity** — every move risks internal links; `--strict` is the gate.
- **Don't over-hide provisional-ness** — the audience is technical and will
  respect "here's what's still moving." The goal is *legibility*, not polish that
  overstates certainty.

## 8. Definition of done (Tier A)

- A first-time visitor can, within one screen, tell **what this project is, what's
  solid, and what's still moving.**
- No page in the primary nav is a bare stub without a `Placeholder`/`Draft` label.
- No internal/reviewer logistics remain in the repo or nav.
- `mkdocs build --strict` is green.
