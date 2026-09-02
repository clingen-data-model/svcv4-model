# Workflow scoring map

A complete reference of **every place a score is produced** across the SVCv4 workflows and
[Summary Table](../summary-table.md) — one node per unique scoring point, whether or not it has an
explicit evidence code.

The hierarchy follows the Summary Table: **Evidence Category → Evidence Concept → Evidence Code**,
then *inside* each code's workflow down to **every unique case/combination that yields a distinct
score**, its **aggregation** across cases, and the **rolled-up** code total.

> **Status:** the full **HOD** side is worked — **POP** (`POP_FRQ`, `POP_HMZ`), **CLN** (`CLN_AFF`,
> `CLN_DNV`, `CLN_ALTV`/`CLN_ALTG`, `CLN_UAF`, `CLN_CCS`), and **LOC** (`LOC_PHE`, `LOC_SEG`), each
> with a category roll-up, assembled under the `HOD` roll-up. **PFD** and the final (VBC, MDE)
> classification remain.

## Contents

- [How to read this](#how-to-read-this)
- [Evidence-line & item structure (GKS VA-Spec)](#evidence-line-item-structure-gks-va-spec)
- [Structuring case-count evidence — 3 approaches](structuring-case-evidence.md) · *Approach 1 = default*

**POP — Population evidence**

- [POP — category roll-up](population.md#pop-population-evidence-category-roll-up)
- [`POP_FRQ` — Population frequency](population.md#pop_frq-population-frequency-worked-branch)
- [`POP_HMZ` — Homozygous / hemizygous occurrences](population.md#pop_hmz-homozygous-hemizygous-population-occurrences-worked-branch)

**CLN — Clinical observations**

- [CLN — category roll-up](clinical.md#cln-clinical-observations-category-roll-up) · *POP_FRQ gate · CLN_CCS exclusivity · the ripple effect*
- [`CLN_AFF` — Affected observations](clinical.md#cln_aff-affected-observations-worked-branch) — [data items](clinical.md#cln_aff-evidence-data-items) · [biallelic example](clinical.md#cln_aff-biallelic-bial-worked-example)
- [`CLN_DNV` — De novo observations](clinical.md#cln_dnv-de-novo-observations-worked-branch)
- [`CLN_ALTV` / `CLN_ALTG` — Alternative causative variant](clinical.md#cln_altv-cln_altg-alternative-causative-variant-worked-branch)
- [`CLN_UAF` — Unaffected observations](clinical.md#cln_uaf-unaffected-observations-worked-branch)
- [`CLN_CCS` — Case-control](clinical.md#cln_ccs-case-control-worked-branch)

**LOC — Locus specificity**

- [LOC — category roll-up](locus.md#loc-locus-specificity-category-roll-up)
- [`LOC_PHE` — Phenotype specificity](locus.md#loc_phe-phenotype-specificity-worked-branch)
- [`LOC_SEG` — Co-segregation](locus.md#loc_seg-co-segregation-worked-branch)

**PFD — Predictive & Functional Data**

- [PFD — the pipeline (overview)](pfd.md#pfd-the-pipeline-overview) · *`_PRD`/`_SPA`/`_FXN`/`_INF`, held values, take-higher*
- [`NUL` / `CDS` — Loss of function](pfd.md#nul-cds-loss-of-function-worked-branch)
- *`SPL`, `MIS` — in progress*

**HOD & beyond**

- [`HOD` — Human Observational Data (roll-up = POP + CLN + LOC)](#hod-human-observational-data-roll-up)
- [Next: the rest of the tree](#next-the-rest-of-the-tree)

## How to read this

- **Codes are base forms; scores are shown separately.** A code is `CLN_AFF`; a node's final score
  is written **`CLN_AFF (score: +1.0)`** — never the compacted `CLN_AFF_+1`, which fuses the code
  with its outcome. **No code ends in a number.** In tables the score lives in its own column
  (**Per-case** = one proband's score; **Aggregation** = how those roll up).
- **Node type** —
  **branch** (a routing choice, no score) ·
  **combo** (a unique per-case scoring cell) ·
  **aggregation** (a subtotal across cases) ·
  **roll-up** (the final code value).
- **Code?** — ✅ maps to an explicit code · ⬦ computed & recorded but **no** code (the label maps
  it to the SM).
- **One code per cell (scoring opportunity)** — the code-minting rule; see *Evidence-line & item
  structure* below.
- Indentation (`›`) shows depth; `n` = count of unrelated probands of that combo type.

---

## Evidence-line & item structure (GKS VA-Spec)

These structural principles govern **every** code in this reference (`CLN_AFF` below is the fully
worked example).

**1 — Every scored node is a GKS `EvidenceLine`.** Any JSON object carrying a `score` has
`"type": "EvidenceLine"`, a **`method`** `{ "code", "label" }` (`code` = the svcv4 code or a
proposed cell code; `label` = its name), and a **`score`**.

**2 — Non-leaf vs leaf.**

- A **non-leaf** node (a subtotal or roll-up) has an **`evidenceLines`** array — one or more child
  `EvidenceLine`s, whose scores are **summed and capped per the svcv4 rules** for that code.
- A **leaf** node (a cell code) has an **`evidenceItems`** array — each element
  `{ "id", "type", "references" (when available), "data" }`, where `data` holds the attributes
  required for that leaf's `method.code`. **Multiple cases that resolve to the same cell sit in that
  one leaf's `evidenceItems`.**

**3 — Code-minting rule.** A `method.code` is minted **per cell** — one distinct scoring
opportunity: a single point value (or a **range**, for roll-up/parent codes). **A cell, not a point
value, is the unit of a code.** Case signatures that resolve to the same cell share the code (and
its `evidenceItems`); **distinct cells keep distinct codes even when their point values coincide**
(e.g. two `+1.5` biallelic cells stay separate). Cells collapse only when they are literally the
same opportunity or not distinctly reachable from case data.

**4 — Codes vs outcomes.** A code is a base form (`CLN_AFF`); a node's score is written
`CLN_AFF (score: +1.0)`, **never** the compacted `CLN_AFF_+1`. **No code ends in a number.**

**5 — Provenance / audit (reuses existing schema — no new fields).** An `evidenceItems` element is
an `EvidenceItem`: `id` (stable id), `type` (e.g. `clinical_observation`), `references` (PMIDs /
CURIEs / URLs — the source a reviewer reopens), and `data` (a `Case`, holding `id` / `family_id` +
the scoring attributes). `EvidenceItem.description` is available for a free-text source locator. A
reviewer follows `references` + `id` to the source, then re-derives the leaf code from `data`.

**6 — Scores are interdependent; edits ripple downstream.** A `score` is a **computed** value, not a
fixed annotation. Cross-code rules make one `EvidenceLine`'s score depend on *other* lines' values:
the **`POP_FRQ` gate** zeroes `CLN_AFF` / `CLN_DNV` unless the VBC's `pop_frq_vbc_score ∈ {0.0,
−1.0}`; **`CLN_CCS` exclusivity** silences its siblings; **category caps** bound sums; the take-higher
`MIS` vs `SPL` choice picks one path. So when a curator revises **previously collected evidence** —
say a new gnomAD release lifts the VBC's FAF and flips `POP_FRQ` from `−1.0` to `−3.0` — the change
**ripples**: `CLN_AFF` and `CLN_DNV` drop to NA, the `CLN` subtotal shifts, and the (VBC, MDE) total
and classification band can move with it. This is *the* reason to structure evidence as a tree of
typed, referenced `EvidenceLine`s rather than a flat list of points: the dependencies become
**explicit, recomputable, and auditable**. A scoring engine must **re-evaluate every dependent code
whenever any input changes**, and a reviewer can trace exactly *why* a code is NA back to the input
that gated it. To make a dependency visible, the depended-on value travels **on the dependent code's
own evidence items** — e.g. `pop_frq_vbc_score` sits in each `CLN_AFF` / `CLN_DNV` `evidenceItem`, so
the gate's input is auditable right beside the observation it controls. (Worked end-to-end in the
[`CLN` roll-up](clinical.md#cln-clinical-observations-category-roll-up).)

---

## `HOD` — Human Observational Data (roll-up)

**Where it sits:** the top of the **Human Observational Data** hierarchy. `HOD` sums the three
category subtotals — **`POP` + `CLN` + `LOC`** — into the observational contribution to the
(VBC, MDE) total (which also includes the **PFD** predictive/functional total). `HOD` is a grouping
label (⬦), not a scored SVCv4 code.

> **Basis — Manufactured composite.** Category subtotals are the roll-ups above (each from different
> practice variants). Shown together to illustrate the top-level sum; `CLN` uses the *rare-VBC*
> branch (`pop_frq_vbc_score = 0.0`), so its pathogenic counting codes are kept.

```text
EvidenceLine  HOD                         score +7.0   (= POP + CLN + LOC)
└─ evidenceLines:
   ├─ EvidenceLine  POP   score -3.5   → POP roll-up (POP_FRQ + POP_HMZ)
   ├─ EvidenceLine  CLN   score +6.5   → CLN roll-up (rare-VBC branch, after both override rules)
   └─ EvidenceLine  LOC   score +4.0   → LOC roll-up (LOC_PHE + LOC_SEG, capped)
```

`HOD = −3.5 + 6.5 + 4.0 = +7.0`. Two ripples already live inside this number: the **`POP_FRQ` gate**
(which admitted `CLN`'s counting codes) and the potential **non-segregation** zeroing (which `LOC`
survived). Change either input and `HOD` — and the classification band — move with it. The remaining
contribution to the (VBC, MDE) total is **PFD** (predictive & functional), worked separately.

---

## Next: the rest of the tree

The entire **HOD** side is worked — **POP** (`POP_FRQ`, `POP_HMZ`), **CLN** (`CLN_AFF`, `CLN_DNV`,
`CLN_ALTV`/`CLN_ALTG`, `CLN_UAF`, `CLN_CCS`), and **LOC** (`LOC_PHE`, `LOC_SEG`), each with a category
roll-up, assembled under the `HOD` roll-up. The same pattern (cell → multiplier where applicable →
roll-up, with cross-code ripples) expands to what remains:

- **PFD:** for each parent code (`NUL`/`CDS`/`SPL`/`MIS`) the `_PRD`/`_SPA`/`_FXN`/`_INF` codes, the
  held combinations, and the parent total (with the `MIS` vs `SPL` take-higher ripple).
- **The (VBC, MDE) total** → `HOD + PFD` → the **classification band**.

See the [Summary Table](../summary-table.md) for the code / combination / category caps that bound each
branch.
