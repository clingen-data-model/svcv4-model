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

## 2b. Blocking content task: scrub all v3 / 2015 criteria-code references **[DECIDE: aggressiveness]**

The v4 docs must **stand on their own** — no references to the 2015/v3 guidelines
or their criteria codes (PVS1, PS/PM/PP/BA/BS/BP…). Sweep results (published pages
only; `superpowers/` working notes excluded):

**Scrub (real v3 references):**

| Page | What | Fix |
|---|---|---|
| `overview/svcv4-in-brief.md` | "What changed from v3 to v4" section; `PS4`, `PS4_Moderate`; "succeeding the 2015 Richards et al." | Remove the v3→v4 section; restate points-based framing v4-only; drop code examples |
| `reference/summary-table.md` | "v3 to v4 code shape" section; `PS4`, `PS4_Moderate` | Remove/rewrite as "SVCv4 code shape" — code names type, `_+N` is the point value |
| `reference/glossary.md` | SVCv4 def "replaces v3's strength-categories… (SVCv3)" | Drop the v3 comparison clause; define SVCv4 on its own |
| `workflows/pfd/index.md` | "already capture much of v3's PM1 'critical domain' evidence" | Remove the PM1 reference; state the v4 evidence directly |
| `examples/v19-tp53.md` | "(PM5-type) evidence" | Drop "(PM5-type)" |
| `examples/v22-f8.md` | "same-AA (PS1) + same-codon (PM5)" | Drop the `(PS1)`/`(PM5)` parentheticals |
| `examples/v5-myh7.md` | "PM5-type support" | Reword to the v4 same-residue concept without the code |
| `reference/scoring-map/population.md` | "SVCv4 chose –3, not BS1's –4" | Drop the `BS1` comparison |
| `reference/scoring-map/locus.md` | "(BS4-equivalent)" | Drop the `BS4` parenthetical |

**Preserve (false positives — do NOT scrub):**

- `PVS-v3-FOXG1` / `v3-foxg1` everywhere — that "v3" = **practice variant #3**, not
  ACMG v3 (all example IDs are `v1…v30`).
- `Sue Richards (OHSU)` in `reference/credits.md` — a contributor's name.
- `reference/va-spec-profile.md` line on the 2015 guidelines being an earlier
  VA-Spec profile — factual lineage about VA-Spec, not a criteria-code mapping;
  **[DECIDE]** keep (recommended) or drop for strict v4-only purity.

> **[DECIDE] aggressiveness:** recommend removing the two dedicated "v3 → v4"
> sections outright (a non-VA, v4-first audience doesn't need the contrast) and
> reducing the inline code mentions to the underlying v4 concept. Confirm and I'll
> execute in one pass with `mkdocs build --strict` as the gate.
>
> **Source material** (`source-material/svcv4-supplements/SM02-v3-to-v4-status.txt`,
> and the figures) is *inputs*, not published — leave as-is unless a figure with a
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
