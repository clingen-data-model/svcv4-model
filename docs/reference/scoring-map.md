# Workflow scoring map

A complete reference of **every place a score is produced** across the SVCv4 workflows and
[Summary Table](summary-table.md) — one node per unique scoring point, whether or not it has an
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

**POP — Population evidence**

- [POP — category roll-up](#pop-population-evidence-category-roll-up)
- [`POP_FRQ` — Population frequency](#pop_frq-population-frequency-worked-branch)
- [`POP_HMZ` — Homozygous / hemizygous occurrences](#pop_hmz-homozygous-hemizygous-population-occurrences-worked-branch)

**CLN — Clinical observations**

- [CLN — category roll-up](#cln-clinical-observations-category-roll-up) · *POP_FRQ gate · CLN_CCS exclusivity · the ripple effect*
- [`CLN_AFF` — Affected observations](#cln_aff-affected-observations-worked-branch) — [data items](#cln_aff-evidence-data-items) · [EvidenceLine tree](#cln_aff-gks-va-spec-evidenceline-tree-auditable-array-approach) · [biallelic example](#cln_aff-biallelic-bial-worked-example)
- [`CLN_DNV` — De novo observations](#cln_dnv-de-novo-observations-worked-branch)
- [`CLN_ALTV` / `CLN_ALTG` — Alternative causative variant](#cln_altv-cln_altg-alternative-causative-variant-worked-branch)
- [`CLN_UAF` — Unaffected observations](#cln_uaf-unaffected-observations-worked-branch)
- [`CLN_CCS` — Case-control](#cln_ccs-case-control-worked-branch)

**LOC — Locus specificity**

- [LOC — category roll-up](#loc-locus-specificity-category-roll-up)
- [`LOC_PHE` — Phenotype specificity](#loc_phe-phenotype-specificity-worked-branch)
- [`LOC_SEG` — Co-segregation](#loc_seg-co-segregation-worked-branch)

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
[`CLN` roll-up](#cln-clinical-observations-category-roll-up).)

---

## `POP` — Population evidence (category roll-up)

**Where it sits:** HOD → **Population (POP)**. `POP` is a **grouping label** (⬦ not an official
SVCv4 code), not a scored cell — it collects two independent, **benignity-only**, **per-variant**
codes: **`POP_FRQ`** (allele frequency vs DAFT) and **`POP_HMZ`** (homozygous / hemizygous
occurrences). The category total is their **sum**; SM 3 sets **no combined POP cap**.

Both children are worked in full below (cells, data items, `EvidenceLine` tree). This roll-up only
**references** their examples:

> **Basis — Manufactured composite.** The two child scores are taken from the worked examples in the
> sub-sections below — `POP_FRQ` from `example-fbn1`, `POP_HMZ` from `v13-aipl1`. They are *different*
> practice variants, shown together only to illustrate the category sum; in a real classification
> both codes apply to the **same** VBC.

```text
EvidenceLine  POP                         score -3.5   (Σ evidenceLines; benignity-only ≤ 0; no combined cap)
└─ evidenceLines:
   ├─ EvidenceLine  POP_FRQ               score -3.0 → see the POP_FRQ example below (FBN1 · FAF ≈ 6.1× DAFT → MOD band)
   └─ EvidenceLine  POP_HMZ               score -0.5 → see the POP_HMZ example below (AIPL1 · 2 homozygotes · n−1 rule)
```

---

## `POP_FRQ` — Population frequency (worked branch)

**Where it sits:** HOD → Population (POP) → `POP_FRQ` · Evidence Code range **0.0 to –6.0** (SM 3,
Figure 1). **Benignity-only** and **per-variant** — computed once for the VBC from an unselected
population database, *not* per proband. There is **no multiplier and no cross-proband summation**:
exactly one band applies to the variant. (This is the first structural contrast with the per-proband
CLN codes — worth seeing early, because most POP/PFD codes score this way.)

**How the band is chosen.** `POP_FRQ` compares the VBC's **FAF** (filtering allele frequency,
gnomAD) to the MDE's **DAFT** (disease allele frequency threshold — computed per gene/MDE by the
calculator / binning / pathogenic-variants methods, SM 3). The **fold** = FAF ÷ DAFT selects the
band.

### The three levels

1. **Band** — the FAF/DAFT fold selects exactly **one** of four bands; each band is a distinct
   scoring opportunity → its own proposed code.
2. **No aggregation** — a single per-variant assessment: no `n × per-case` multiplier, no summation
   across probands.
3. **Roll-up** — `POP_FRQ` = the selected band (0.0 … –6.0); it feeds the **POP** category subtotal
   alongside `POP_HMZ` (SM 3 sets no combined POP cap).

### The bands

Proposed code `POP_FRQ_<STRENGTH>` — **only `POP_FRQ` is an official SVCv4 code**; SVCv4 writes the
band as a point value (`POP_FRQ_-3.0`), which this map avoids (no code ends in a number). The
strength labels are proposed descriptors. Bands are **lower-edge-inclusive** here (SM 3 prose uses
strict `>`/`<` at the exact multiples — a documented boundary assumption).

| Proposed code | FAF vs DAFT (fold) | Points | Official? | SM 3 (Figure 1) |
|---|---|---|---|---|
| `POP_FRQ_NONE` | FAF < 1.5× DAFT       | **0.0**  | ⬦ | below threshold — no benign evidence |
| `POP_FRQ_SUPP` | 1.5× ≤ FAF < 5× DAFT  | **–1.0** | ⬦ | supporting benign |
| `POP_FRQ_MOD`  | 5× ≤ FAF < 15× DAFT   | **–3.0** | ⬦ | moderate benign (SVCv4 chose –3, not BS1's –4) |
| `POP_FRQ_STRG` | FAF ≥ 15× DAFT        | **–6.0** | ⬦ | strong benign |
| `POP_FRQ`      | the selected band     | **0.0 … –6.0** | ✅ | Figure 1 |

Every variant is assessable — **absent-in-database is `faf = 0.0` → `POP_FRQ_NONE` (+0.0)**, not "no
data". `_ND` (no code) is reserved for when FAF or DAFT cannot be computed: a non-robust AF from a
low allele number, or FAF undefined at allele count 1 (SM 3 caveats), or `daft ≤ 0`.

### Evidence data items

| Attribute (real name) | Feeds | Notes |
|---|---|---|
| `evidence.faf`                    | fold numerator   | gnomAD filtering allele frequency; undefined at allele count 1 |
| `evidence.faf_source`             | provenance       | database + version (e.g. gnomAD v4.1.0) |
| `evidence.daft`                   | fold denominator | computed threshold; must be `> 0` |
| `evidence.daft_method`            | provenance       | `calculator` / `binning` / `pathogenic-variants` |
| `evidence.daft_calculator_inputs` | provenance       | prevalence, penetrance, locus/allelic heterogeneity, inheritance |
| *(derived)* `faf / daft`          | band selection   | not stored — computed at scoring time |

### Code ← data-item cross-reference

| Code | fold = `faf / daft` |
|---|---|
| `POP_FRQ_NONE` | < 1.5 |
| `POP_FRQ_SUPP` | 1.5 – < 5 |
| `POP_FRQ_MOD`  | 5 – < 15 |
| `POP_FRQ_STRG` | ≥ 15 |
| *(no code → `_ND`)* | `faf` or `daft` missing, or `daft ≤ 0` |

### `POP_FRQ` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Grounded DAFT inputs + manufactured FAF.** The DAFT inputs (prevalence 1/5000,
> penetrance 0.85, heterogeneity) match SM 3's worked FBN1 example and practice `example-fbn1`
> (DAFT ≈ 0.000118). The VBC's FAF here (0.00072 → `MOD`, −3.0) is invented to illustrate a non-zero
> band; the real `example-fbn1` VBC is below threshold (`POP_FRQ` +0.0).

An FBN1 · Marfan example (SM 3's worked DAFT = 0.000118). The VBC's FAF is 0.00072, so
fold ≈ 6.1 → the `MOD` band → **–3.0**. The tree is shallow — one band, one population-frequency
observation, no multiplier:

```text
EvidenceLine  POP_FRQ                     score -3.0   (single per-variant assessment; range 0.0…-6.0)
└─ evidenceLines:
   └─ EvidenceLine  POP_FRQ_MOD           score -3.0 → evidenceItems: [1 pop-frequency obs]  (FAF ≈ 6.1× DAFT)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "POP_FRQ", "label": "Population frequency (benignity)" }, "score": -3.0,
  "note": "single per-variant assessment; exactly one band applies; range 0.0 to -6.0",
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "POP_FRQ_MOD", "label": "FAF 5-15x DAFT · moderate benign" }, "score": -3.0,
      "evidenceItems": [ { "id": "pop-01", "type": "population_frequency", "references": ["gnomAD:v4.1.0"],
        "data": { "faf": 0.00072, "faf_source": "gnomAD v4.1.0",
          "daft": 0.000118, "daft_method": "calculator",
          "daft_calculator_inputs": { "prevalence_denominator": 5000, "penetrance": 0.85,
            "locus_heterogeneity": 1.0, "allelic_heterogeneity": 0.10, "inheritance": "monoallelic" } } } ] }
  ]
}
```

fold = `0.00072 / 0.000118 ≈ 6.1` → `5× ≤ FAF < 15×` → `POP_FRQ_MOD` = **–3.0**. Because only one
band applies, `POP_FRQ` reports that band directly — no summation node. The single leaf still carries
a full audit trail (the FAF and its source, the DAFT and the method + inputs used to derive it), so a
reviewer can reproduce the fold and the resulting band.

---

## `POP_HMZ` — Homozygous / hemizygous population occurrences (worked branch)

**Where it sits:** HOD → Population (POP) → `POP_HMZ` · **benignity-only (≤ 0)** (SM 3 Table 7).
**Per-variant**, like `POP_FRQ` — read from an unselected population database, not per proband. The
presence of **homozygous** (or, for X-linked, **hemizygous**) individuals in the database is benign
evidence *when the MDE's penetrance and severity would preclude affected individuals from that
database*.

**Eligibility gate.** `hmz_eligible` must hold — the MDE is near-100% penetrant and affected
individuals are not expected in population databases. If the phenotype is mild enough that carriers
could appear (SM 3's F8 example: 89 hemizygotes but only mild factor-VIII reduction → **not**
eligible), no points are awarded.

**The `n − 1` rule.** Points count **only from the 2nd occurrence** — the first homozygote/hemizygote
is free. `score = weight × max(count − 1, 0)`, where `count` = `homozygote_count`
(+ `hemizygote_count` for X-linked).

### The three levels

1. **Cell** — the MDE's inheritance selects one per-occurrence **weight**.
2. **Aggregation** — the **`n − 1` multiplier**: `weight × (count − 1)`; the first occurrence scores 0.
3. **Roll-up** — `POP_HMZ` = the cell (≤ 0); feeds the **POP** category alongside `POP_FRQ`.

### The cells

| Proposed code | inheritance · genotype | per-occurrence (from the 2nd) |
|---|---|---|
| `POP_HMZ_DOM` | Autosomal Dominant · homozygous          | **−1.0** |
| `POP_HMZ_OTH` | Semidominant / AR / X-linked · homo/hemi | **−0.5** |
| `POP_HMZ`     | roll-up = `weight × (count − 1)`         | **≤ 0** |

Only one cell applies per MDE (set by its MOI). SD, AR, and X-linked share the `−0.5` weight → one
collapsed `OTH` cell (point-identical); only Autosomal Dominant homozygous is `−1.0`.

### Evidence data items

| Attribute (real name) | Feeds | Notes |
|---|---|---|
| `evidence.homozygote_count` | count | homozygous occurrences in the database |
| `evidence.hemizygote_count` | count | added only for X-linked MOIs |
| `evidence.hmz_eligible`     | gate  | near-100% penetrance; affecteds not expected in the DB |
| `moi`                       | weight + hemizygote inclusion | AD → `−1.0`; SD/AR/XL → `−0.5` |

### Code ← data-item cross-reference

| Code | `moi` | count = |
|---|---|---|
| `POP_HMZ_DOM` | AD        | `homozygote_count` |
| `POP_HMZ_OTH` | SD / AR   | `homozygote_count` |
| `POP_HMZ_OTH` | XLD / XLR | `homozygote_count + hemizygote_count` |
| *(no code → `_ND`)* | any | `hmz_eligible` not TRUE, or no count |

### `POP_HMZ` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Grounded (practice `v13-aipl1`).** AIPL1 · AR retinopathy: a near-100%-penetrant,
> early-onset recessive disease, so homozygotes are **not** expected in gnomAD → eligible. gnomAD
> shows **2 homozygotes**.

`POP_HMZ_OTH` (AR): `−0.5 × (2 − 1) = −0.5` — the first homozygote is free, the second scores −0.5.
The count lives in one population observation; the multiplier is `count − 1`, not a per-item array.

```text
EvidenceLine  POP_HMZ                     score -0.5   (weight × (count − 1); benignity-only ≤ 0)
└─ evidenceLines:
   └─ EvidenceLine  POP_HMZ_OTH           score -0.5 → evidenceItems: [1 pop obs]  (2 homozygotes → 2−1 counted × −0.5)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "POP_HMZ", "label": "Homozygous/hemizygous occurrences (benignity)" }, "score": -0.5,
  "note": "weight × (count − 1); AR weight −0.5; 2 homozygotes → 1 counted",
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "POP_HMZ_OTH", "label": "SD / AR / X-linked · −0.5 per occurrence" }, "score": -0.5,
      "evidenceItems": [ { "id": "hmz-01", "type": "population_frequency", "references": ["practice-variant-set:v13-aipl1", "gnomAD:v4.1.0"],
        "description": "Grounded — AIPL1 AR retinopathy; 2 homozygotes in gnomAD; near-100% penetrant early-onset → eligible.",
        "data": { "hmz_eligible": "TRUE", "homozygote_count": 2, "hemizygote_count": 0 } } ] }
  ]
}
```

**Reconciliation note.** Practice `v13-aipl1`'s illustrative target is `POP_HMZ_−2`; the Table-7 model
here gives `−0.5` (AR weight × (2 − 1)). The practice-set targets are placeholders and will be
reconciled once the cell weights are finalized.

---

## `CLN` — Clinical observations (category roll-up)

**Where it sits:** HOD → **Clinical Observations (CLN)**. `CLN` is a **grouping label** (⬦ not an
official SVCv4 code) collecting six codes — pathogenic **`CLN_AFF`**, **`CLN_DNV`**, **`CLN_CCS`**
and benign **`CLN_ALTV`**, **`CLN_ALTG`**, **`CLN_UAF`**. The category total is the **sum of the
sub-codes that survive two cross-code override rules**.

### Two cross-code override rules

Both are *removals*, applied to the summed CLN sub-codes (order-independent):

**1 — `CLN_CCS` exclusivity** (SM 4). When a `CLN_CCS` code is present — *regardless of its value,
even 0.0* — mark **`CLN_AFF`, `CLN_ALTV`/`CLN_ALTG`, `CLN_UAF` as NA**; keep only **`CLN_CCS` +
`CLN_DNV`**. A robust case-control study supersedes individual proband counting.

**2 — `POP_FRQ` gate** (SM 4 Fig 1 / L27). The pathogenic **counting** codes **`CLN_AFF` + `CLN_DNV`**
are awarded **only when the VBC is rare** — `pop_frq_vbc_score ∈ {0.0, −1.0}`. If the VBC is common
enough to earn `−3.0` or `−6.0` from `POP_FRQ`, **`CLN_AFF` and `CLN_DNV` are NA (zeroed)**: a common
variant's presence in affected probands is not pathogenic evidence. **Benign codes (`CLN_UAF`,
`CLN_ALTV`/`CLN_ALTG`) are *not* POP-gated.**

> **Why `pop_frq_vbc_score` rides on the evidence item.** The gate needs the VBC's `POP_FRQ` outcome
> at the moment it scores `CLN_AFF` / `CLN_DNV`, so those codes' `evidenceItems` carry a
> **`pop_frq_vbc_score`** attribute — the VBC-level `POP_FRQ` score (`= POP_FRQ.score`, one of
> `0.0 / −1.0 / −3.0 / −6.0`). Each proband's contribution is then self-auditable: a reviewer sees
> the frequency that either admits or zeroes the count, right beside the observation. (The value is
> per-VBC, so it is identical across that code's items.)

```json
{ "type": "EvidenceLine", "method": { "code": "CLN_AFF", "label": "Affected observations" }, "score": 5.5,
  "note": "POP_FRQ-gated: if pop_frq_vbc_score is not 0.0 or -1.0, this whole code is NA (score → 0, dropped)",
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_RARE_CTP", "label": "rare · confirmed-trans P/LP" }, "score": 3.0,
      "evidenceItems": [ { "id": "ush2a-proband-3", "type": "clinical_observation", "references": ["practice-variant-set:v20-ush2a"],
        "data": { "id": "ush2a-proband-3", "pop_frq_vbc_score": 0.0, "vbc_zygosity": "HET",
          "compound_het_variant": { "classification": "P", "phase_confidence": "HIGH", "co_occurrence_likelihood": "LT_0_0001" } } } ] }
  ]
}
```

Flip that `pop_frq_vbc_score` to `−3.0` and the entire `CLN_AFF` `EvidenceLine` is dropped from the
CLN roll-up — no matter how many strong probands it holds.

**This is the ripple effect (principle 6) made concrete.** `pop_frq_vbc_score` is *collected
evidence* — it is the `POP_FRQ` code's own outcome. If a curator later revises the `POP_FRQ` inputs
(a new gnomAD release raises the VBC's FAF, moving `POP_FRQ` from `−1.0` to `−3.0`), that single edit
**cascades**: every `CLN_AFF` / `CLN_DNV` evidence item's `pop_frq_vbc_score` updates → the gate now
fails → both codes flip to NA → the `CLN` subtotal changes → the (VBC, MDE) total and its
classification band can change. A scoring engine must **re-run the gate on every edit**; the tree
records the dependency so nothing silently goes stale. The three roll-ups below show the same cases
landing at `+6.5`, `−11.0`, or `+16.0` depending only on *other* evidence lines.

### Condensed roll-up (references the sub-section examples)

> **Basis — Manufactured composite.** Sub-code scores are the worked examples below (each a
> *different* practice variant), shown together to illustrate the roll-up and the two override rules;
> `pop_frq_vbc_score` is set on the gated codes to make the gate visible.

**(a) VBC rare — `pop_frq_vbc_score = 0.0` — every code kept:**

```text
EvidenceLine  CLN                         score +6.5   (Σ kept sub-codes)
└─ evidenceLines:
   ├─ EvidenceLine  CLN_AFF   score +5.5   [pop_frq_vbc_score 0.0 → kept]   → CLN_AFF example (USH2A biallelic)
   ├─ EvidenceLine  CLN_DNV   score +12.0  [pop_frq_vbc_score 0.0 → kept]   → CLN_DNV example (PTPN11, capped)
   ├─ EvidenceLine  CLN_ALTV  score -0.5   (benign · not POP-gated)         → CLN_ALTV example (ACVRL1)
   ├─ EvidenceLine  CLN_ALTG  score -0.5   (benign · not POP-gated)         → CLN_ALTG example (ACVRL1)
   └─ EvidenceLine  CLN_UAF   score -10.0  (benign · not POP-gated)         → CLN_UAF example
```

**(b) `POP_FRQ` gate — same probands, but `pop_frq_vbc_score = −3.0` (VBC too common):**

```text
EvidenceLine  CLN                         score -11.0   (Σ kept sub-codes)
└─ evidenceLines:
   ├─ (CLN_AFF   NA)   pop_frq_vbc_score −3.0 → too common → zeroed
   ├─ (CLN_DNV   NA)   pop_frq_vbc_score −3.0 → too common → zeroed
   ├─ EvidenceLine  CLN_ALTV  score -0.5    (benign · not gated)
   ├─ EvidenceLine  CLN_ALTG  score -0.5    (benign · not gated)
   └─ EvidenceLine  CLN_UAF   score -10.0   (benign · not gated)
```

The pathogenic proband counting vanished the moment the VBC became too common; only the benign
observations survive.

**(c) `CLN_CCS` exclusivity — a robust case-control study is present:**

```text
EvidenceLine  CLN                         score +16.0   (Σ kept sub-codes)
└─ evidenceLines:
   ├─ EvidenceLine  CLN_CCS   score +4.0    (applied → silences the others)  → CLN_CCS example
   ├─ EvidenceLine  CLN_DNV   score +12.0   (the sole CLN exception, kept)
   ├─ (CLN_AFF            NA)   CLN_CCS exclusivity
   ├─ (CLN_ALTV/CLN_ALTG  NA)  CLN_CCS exclusivity
   └─ (CLN_UAF            NA)   CLN_CCS exclusivity
```

Each child is worked in full (cells, data items, `EvidenceLine` tree) in its section below.

---

## `CLN_AFF` — Affected observations (worked branch)

**Where it sits:** HOD → Clinical Observations (CLN) → `CLN_AFF` · Evidence Code Cap **≥ 0** (SM 4
Tables 1 & 2). A `CLN_AFF` score is built **per unrelated proband**, then **summed** across probands
(SM 4 L29/L80).

**Which table(s) apply is set by the MDE's MOI.** `CLN_AFF` = `CLN_AFF_MONO` + `CLN_AFF_BIAL` —
the **sum of both table subtotals** — where MOI determines which are populated (SM 4 L28/L77/L80):

| MOI | Monoallelic (Table 1) | Biallelic (Table 2) |
|---|---|---|
| AD, XLD | ✔ | — |
| AR | — | ✔ |
| **XLR** | ✔ affected males | ✔ affected females |
| **Semidominant** | ✔ heterozygotes | ✔ biallelic individuals |

For most MOIs exactly one subtotal contributes; for **XLR** and **semidominant** both can, and
their subtotals are summed. **The per-cell scores are identical either way** — only which subtotals
are non-empty changes.

### The three levels

1. **Combo** — each unique (phenotype × testing × second-variant) **cell** yields a per-case score
   and its own proposed code.
2. **Aggregation** — for each cell, `n × per-case` summed across the probands of that cell type,
   rolling into the table **subtotal** (`CLN_AFF_MONO` / `CLN_AFF_BIAL`).
3. **Roll-up** — `CLN_AFF` = `CLN_AFF_MONO` + `CLN_AFF_BIAL` (MOI sets which are populated; XLR/SD
   sum both), range **≥ 0**.

### Proposed code scheme

`CLN_AFF_<TABLE>_<ROW>_<COL>` — **only `CLN_AFF` is an official SVCv4 code**; the suffix is a
proposed identifier so every cell/aggregation line has a stable name (rename freely).
`TABLE` = `MONO`/`BIAL`; biallelic `ROW` = `RARE` (co-occ < 0.0001) / `UNCM` (0.0001–0.01) / `INCP`
(incomplete); `COL` = `CTP` confirmed-trans P/LP · `ATP` assumed-trans P/LP · `CTV` confirmed-trans
VUS · `HOM` homozygous · `NON` none. **Official?** ✅ = official code · ⬦ = proposed sub-cell id.

#### Monoallelic — Table 1 *(when the MDE is monoallelic-inherited)*

| Proposed code | Cell | Per-case | Aggregation | Official? | SM 4 (Table 1) |
|---|---|---|---|---|---|
| `CLN_AFF_MONO_SPEC_THOR` | Specific · thorough | **+1.0** | `n × +1.0` | ⬦ | specific; non-genetic unlikely **and** all relevant genes tested **and** no add'l variant |
| `CLN_AFF_MONO_SPEC_LIM` | Specific · limited | **+0.5** | `n × +0.5` | ⬦ | specific; non-genetic not excluded **or** limited testing **or** add'l VUS |
| `CLN_AFF_MONO_CONS_THOR` | Consistent · thorough | **+0.5** | `n × +0.5` | ⬦ | consistent; thorough |
| `CLN_AFF_MONO_CONS_LIM` | Consistent · limited | **+0.25** | `n × +0.25` | ⬦ | consistent; limited |
| `CLN_AFF_MONO_ALT` | P/LP alt explains phenotype → `CLN_ALT` | **+0.0** | `n × +0.0` | ⬦ | L29: add'l P/LP fully accounts for phenotype |
| `CLN_AFF_MONO_UAF` | Not consistent / unaffected → `CLN_UAF` | **+0.0** | `n × +0.0` | ⬦ | phenotype not consistent |
| `CLN_AFF_MONO` | **Monoallelic subtotal** | — | `Σ (n × per-case)` | ⬦ | L29/L80 |

#### Biallelic — Table 2 *(when the MDE is biallelic-inherited)*

| Proposed code | Cell | Per-case | Aggregation | Official? | SM 4 (Table 2) |
|---|---|---|---|---|---|
| `CLN_AFF_BIAL_RARE_CTP` | Rare co-occ · confirmed-trans P/LP | **+3.0** | `n × +3.0` | ⬦ | co-occ < 0.0001 |
| `CLN_AFF_BIAL_RARE_ATP` | Rare co-occ · assumed-trans P/LP | **+1.5** | `n × +1.5` | ⬦ | co-occ < 0.0001 |
| `CLN_AFF_BIAL_RARE_CTV` | Rare co-occ · confirmed-trans VUS | **+1.5** | `n × +1.5` | ⬦ | co-occ < 0.0001 |
| `CLN_AFF_BIAL_UNCM_CTP` | Uncommon co-occ · confirmed-trans P/LP | **+2.0** | `n × +2.0` | ⬦ | co-occ 0.0001–0.01 |
| `CLN_AFF_BIAL_UNCM_ATP` | Uncommon co-occ · assumed-trans P/LP | **+1.0** | `n × +1.0` | ⬦ | co-occ 0.0001–0.01 |
| `CLN_AFF_BIAL_UNCM_CTV` | Uncommon co-occ · confirmed-trans VUS | **+1.0** | `n × +1.0` | ⬦ | co-occ 0.0001–0.01 |
| `CLN_AFF_BIAL_INCP_CTP` | Incomplete‡ · confirmed-trans P/LP | **+1.0** | `n × +1.0` | ⬦ | incomplete row |
| `CLN_AFF_BIAL_INCP_ATP` | Incomplete‡ · assumed-trans P/LP | **+0.75** | `n × +0.75` | ⬦ | incomplete row |
| `CLN_AFF_BIAL_INCP_CTV` | Incomplete‡ · confirmed-trans VUS | **+0.5** | `n × +0.5` | ⬦ | incomplete row |
| `CLN_AFF_BIAL_THOR_HOM` | Homozygous VBC · thorough | **+1.0** | `n × +1.0` | ⬦ | homozygous; thorough (co-occ N/A) |
| `CLN_AFF_BIAL_INCP_HOM` | Homozygous VBC · incomplete‡ | **+0.5** | `n × +0.5` | ⬦ | homozygous; incomplete (co-occ N/A) |
| `CLN_AFF_BIAL_NON` | Any row · none† (het, no valid in-trans 2nd variant) | **+0.0** | `n × +0.0` | ⬦ | col 5 |
| `CLN_AFF_BIAL_ALT` | P/LP alt (different gene) → `CLN_ALT` | **+0.0** | `n × +0.0` | ⬦ | row C |
| `CLN_AFF_BIAL_UAF` | Not consistent / unaffected → `CLN_UAF` | **+0.0** | `n × +0.0` | ⬦ | last row |
| `CLN_AFF_BIAL` | **Biallelic subtotal** | — | `Σ (n × per-case)` | ⬦ | L80 |

#### Roll-up

| Proposed code | Node | Value | Official? | SM 4 |
|---|---|---|---|---|
| `CLN_AFF` | **Roll-up** = `CLN_AFF_MONO` + `CLN_AFF_BIAL` (MOI sets which contribute; XLR/SD can sum both) | **≥ 0** | ✅ | L28/L77/L80 |

† **none** = heterozygous VBC with no 2nd variant, or 2nd variant in *cis*, or unknown phase.
‡ **incomplete (`INCP`)** = not all relevant genes tested **or** high number of unexplained cases
**or** non-genetic etiology cannot be excluded **or** an additional plausible VUS is present.

### Distinct scores this branch can produce

Per-case: `+3.0, +2.0, +1.5, +1.0, +0.75, +0.5, +0.25, +0.0`. The rolled-up `CLN_AFF` is the sum
over probands (≥ 0, no cap at this layer — the Summary Table shows `≥ 0`).

---

## `CLN_AFF` — evidence data items

The precise set of captured data items every `CLN_AFF` cell reads, and which codes depend on each.

The precise set of captured attributes every `CLN_AFF` cell reads — named as they appear in the
`Case` schema (validated against `schemas/json/case/CLN_AFF.schema.json`). In the schema/examples,
`moi` and `pop_frq_points` are top-level workflow parameters and the proband fields live under
`case.*`.

### Data items (attributes)

| Attribute | Type | Role in `CLN_AFF` | Example value (practice set) |
|---|---|---|---|
| `moi` | `MOI` | Routing: which table(s) apply (AD/XLD → mono; AR → biallelic; XLR/SD → both) | `"AD"` (MYH7), `"AR"` (ATM) |
| `case.sex` | `Sex` | XLR routing: affected M → mono, F → biallelic | *(unset)* |
| `case.vbc_zygosity` | `Zygosity` | SD routing; biallelic column (HOM vs HET) | `"HET"` |
| `case.pheno_specificity_for_mde` | `PhenoSpecificity` | Affected gate; mono row; biallelic gate (not INCONSISTENT) | `"SPECIFIC"`, `"CONSISTENT"` |
| `case.testing.covers_all_genes_relevant_to_mde` | `TriState` | Thoroughness | `"TRUE"` |
| `case.testing.non_genetic_etiology_excluded` | `TriState` | Thoroughness | *(unset in all 3)* |
| `case.additional_variants[].classification` | `str` | P/LP → alt-cause exit; VUS → forces limited/incomplete | *(none; `additional_variant_exists=FALSE`)* |
| `case.compound_het_variant.classification` | `str` | Biallelic column: P/LP vs VUS vs other | `"P"` (ATM) |
| `case.compound_het_variant.phase_confidence` | `PhaseConfidence` | Biallelic column: HIGH = confirmed-trans, else assumed | `"HIGH"` (ATM) |
| `case.compound_het_variant.co_occurrence_likelihood` | `CoOccurrenceLikelihood` | Biallelic row for a compound-het: rare / uncommon | *(unset in ATM)* |
| `case.id` | `str` | Per-proband counting (`n`) | `"PVS-v5-MYH7-proband-2"` |
| `case.family_id` | `str` | Unrelated determination (one index proband per family) | `"PVS-v5-MYH7-FAM-2"` |

**Common to every cell:** `moi` + `case.sex` (routing) and `case.id` + `case.family_id`
(aggregation). The cross-references below list only the **cell-discriminating** attributes.

### Thoroughness — `THOR`, and its counterparts `LIM` / `INCP`

**`THOR` (thorough) is the same composite condition wherever it appears in `CLN_AFF`:**

> `covers_all_genes_relevant_to_mde` = TRUE **and** `non_genetic_etiology_excluded` = TRUE
> **and** no VUS in `additional_variants[].classification`.

(A P/LP additional variant is *not* part of THOR — it routes to the `_ALT` exit. So THOR means
"all relevant genes tested **and** non-genetic cause excluded **and** no competing VUS.")

| | Positive (top tier) | Counterpart | Counterpart condition |
|---|---|---|---|
| **Monoallelic** | `THOR` (best tier) | **`LIM`** (limited) | the **plain negation** of THOR: `covers_all`≠TRUE **or** `non_genetic`≠TRUE **or** a VUS additional variant |
| **Biallelic** | `THOR` → `RARE`/`UNCM`/`THOR_HOM` | **`INCP`** (incomplete) | the **same** negation of THOR, **plus** one biallelic-only trigger: THOR holds but `compound_het_variant.co_occurrence_likelihood` is unestablished (neither `LT_0_0001` nor `BETWEEN_0_0001_0_01`) |

So on the THOR *attributes*, **`LIM` = `INCP`** (both are "not THOR"). They differ only because
biallelic has a **co-occurrence** dimension monoallelic lacks: `INCP` ⊋ `LIM`, additionally
catching "thorough testing but co-occurrence likelihood not established." Hence the different names
— mono's counterpart is about *limited testing*; biallelic's is about *incomplete evidence*
(testing **or** co-occurrence).

### Cross-reference — Monoallelic cells

| Code | Required attributes → values |
|---|---|
| `CLN_AFF_MONO_SPEC_THOR` | `pheno_specificity_for_mde`=SPECIFIC · `covers_all_genes_relevant_to_mde`=TRUE · `non_genetic_etiology_excluded`=TRUE · no P/LP or VUS in `additional_variants[].classification` |
| `CLN_AFF_MONO_SPEC_LIM` | `pheno_specificity_for_mde`=SPECIFIC · *limited*‖ |
| `CLN_AFF_MONO_CONS_THOR` | `pheno_specificity_for_mde`=CONSISTENT · `covers_all_genes_relevant_to_mde`=TRUE · `non_genetic_etiology_excluded`=TRUE · no P/LP or VUS add'l |
| `CLN_AFF_MONO_CONS_LIM` | `pheno_specificity_for_mde`=CONSISTENT · *limited*‖ |
| `CLN_AFF_MONO_ALT` | ≥1 `additional_variants[].classification` ∈ {P, LP} *(pheno irrelevant)* |
| `CLN_AFF_MONO_UAF` | `pheno_specificity_for_mde`=INCONSISTENT |

‖ *limited* = `covers_all_genes_relevant_to_mde`≠TRUE **or** `non_genetic_etiology_excluded`≠TRUE
**or** a VUS in `additional_variants[].classification`.

### Cross-reference — Biallelic cells

*thorough♦* = `covers_all_genes_relevant_to_mde`=TRUE **and** `non_genetic_etiology_excluded`=TRUE
**and** no P/LP or VUS in `additional_variants[].classification`. All rows require
`pheno_specificity_for_mde`≠INCONSISTENT.

| Code | Required attributes → values |
|---|---|
| `CLN_AFF_BIAL_RARE_CTP` | `vbc_zygosity`=HET · `compound_het_variant.classification`∈{P,LP} · `.phase_confidence`=HIGH · `.co_occurrence_likelihood`=`LT_0_0001` · thorough♦ |
| `CLN_AFF_BIAL_RARE_ATP` | `vbc_zygosity`=HET · `ch.classification`∈{P,LP} · `.phase_confidence`≠HIGH · `.co_occurrence_likelihood`=`LT_0_0001` · thorough♦ |
| `CLN_AFF_BIAL_RARE_CTV` | `vbc_zygosity`=HET · `ch.classification`=VUS · `.phase_confidence`=HIGH · `.co_occurrence_likelihood`=`LT_0_0001` · thorough♦ |
| `CLN_AFF_BIAL_UNCM_CTP` | as RARE_CTP but `.co_occurrence_likelihood`=`BETWEEN_0_0001_0_01` |
| `CLN_AFF_BIAL_UNCM_ATP` | as RARE_ATP but `.co_occurrence_likelihood`=`BETWEEN_0_0001_0_01` |
| `CLN_AFF_BIAL_UNCM_CTV` | as RARE_CTV but `.co_occurrence_likelihood`=`BETWEEN_0_0001_0_01` |
| `CLN_AFF_BIAL_INCP_CTP` | `vbc_zygosity`=HET · `ch.classification`∈{P,LP} · `.phase_confidence`=HIGH · **not** thorough♦ *(or co-occ unassessed)* |
| `CLN_AFF_BIAL_INCP_ATP` | `vbc_zygosity`=HET · `ch.classification`∈{P,LP} · `.phase_confidence`≠HIGH · **not** thorough♦ |
| `CLN_AFF_BIAL_INCP_CTV` | `vbc_zygosity`=HET · `ch.classification`=VUS · `.phase_confidence`=HIGH · **not** thorough♦ |
| `CLN_AFF_BIAL_THOR_HOM`§ | `vbc_zygosity`=HOM · thorough♦ *(no `compound_het_variant`; `co_occurrence_likelihood` not read)* |
| `CLN_AFF_BIAL_INCP_HOM`§ | `vbc_zygosity`=HOM · **not** thorough♦ |
| `CLN_AFF_BIAL_NON` | `vbc_zygosity`=HET · no valid in-trans 2nd variant: `compound_het_variant` absent **or** `.classification`∈{B,LB} **or** (`.classification`=VUS **and** `.phase_confidence`≠HIGH) |
| `CLN_AFF_BIAL_ALT` | ≥1 `additional_variants[].classification` ∈ {P, LP} (different gene) |
| `CLN_AFF_BIAL_UAF` | `pheno_specificity_for_mde`=INCONSISTENT |

§ **Refinement applied:** the **homozygous** cells never read
`compound_het_variant.co_occurrence_likelihood` (co-occurrence of two heterozygous variants is
meaningless for a homozygote), so the cell table now carries a single **`CLN_AFF_BIAL_THOR_HOM`**
(homozygous · thorough → `+1.0`) plus **`CLN_AFF_BIAL_INCP_HOM`** (homozygous · incomplete →
`+0.5`), replacing the former co-occurrence-split `BIAL_RARE_HOM` / `BIAL_UNCM_HOM`. Both tables are
now consistent.

### Mapping the practice-variant-set examples

Concrete `case-CLN_AFF.json` inputs from the practice set, the cell each **shown proband** resolves
to (from the attributes present), and the aggregate target in its `classification.json`:

| Example (VBC · MDE · MOI) | Attributes present | Shown-proband cell | `classification.json` target |
|---|---|---|---|
| MYH7 · HCM · **AD** | `pheno`=SPECIFIC · `covers_all`=TRUE · `non_genetic`∅ · `vbc_zygosity`=HET | `CLN_AFF_MONO_SPEC_LIM` (score: +0.5) | `CLN_AFF` (score: +1.0) |
| ATM · ataxia-telangiectasia · **AR** | `pheno`=CONSISTENT · `vbc_zygosity`=HET · `ch.classification`=P · `ch.phase_confidence`=HIGH · `covers_all`=TRUE · `non_genetic`∅ · `co_occurrence`∅ | `CLN_AFF_BIAL_INCP_CTP` (score: +1.0) | `CLN_AFF` (score: +2.0) |
| ATXN7L3 · NDD · **AD** | `pheno`=CONSISTENT · `covers_all`=TRUE · `non_genetic`∅ · `vbc_zygosity`=HET | `CLN_AFF_MONO_CONS_LIM` (score: +0.25) | `CLN_AFF` (score: +2.0) |

*(The `classification.json` files currently encode these targets in the compacted `CLN_AFF_+1` /
`CLN_AFF_+2` form; shown here in the `code (score: …)` convention.)*

**∅ = attribute not populated.** The `classification.json` **target is a cross-proband aggregate,
not the shown-proband cell** — they answer different questions, so they are not expected to match
one-to-one. Three things the mapping surfaces (informational — the examples will be reconciled to
the finalized codes later):

- **The targets aggregate multiple probands.** MYH7's `CLN_AFF` evidence line (target score +1.0)
  has `individuals_observed: 3` (a SPECIFIC + a CONSISTENT + an INCONSISTENT proband) and is
  labelled *"illustrative" / "Placeholder"* — so +1.0 is a hand-picked aggregate, not the +0.5 of
  the one proband detailed in `case-CLN_AFF.json`. (No clean cell combination sums to exactly 1.0.)
  Likewise ATXN7L3's `CLN_AFF` target (+2.0) on an AD-CONSISTENT MDE (per-proband max +0.5) is only
  reachable as a multi-proband sum.
- **The single-proband files omit `non_genetic_etiology_excluded`** (and ATM omits
  `co_occurrence_likelihood`) — exactly the attributes that separate the **top-tier** cells from
  the limited/incomplete ones. As populated, each shown proband lands one tier below thorough; to
  land on the top cell those attributes must be `TRUE`.
- **The two files sit at different granularities** — `case-*.json` details one proband's full
  attributes; `classification.json` summarizes several probands with only phenotype + specificity.
  They do not yet round-trip.

### Worked example — MYH7 · HCM · AD → `CLN_AFF (score: +1.0)`

A self-consistent scenario that rolls up to `+1.0` (the raw practice example's `+1.0` is an
illustrative placeholder; this assigns concrete attributes so the hierarchy genuinely sums).
**MOI = AD ⇒ monoallelic only**, so `CLN_AFF_BIAL` is not populated.

Three **unrelated** index probands (distinct `family_id`), each `moi`=AD, `vbc_zygosity`=HET,
`additional_variant_exists`=FALSE:

| Proband | `pheno_specificity_for_mde` | Testing attributes → thoroughness | Cell (score) | `n` | Contribution |
|---|---|---|---|---|---|
| A | SPECIFIC | `covers_all_genes_relevant_to_mde`=TRUE · `non_genetic_etiology_excluded`∅ → **limited** (`LIM`) | `CLN_AFF_MONO_SPEC_LIM` (score: +0.5) | 1 | +0.5 |
| B | CONSISTENT | `covers_all…`=TRUE · `non_genetic…`=TRUE · no VUS → **thorough** (`THOR`) | `CLN_AFF_MONO_CONS_THOR` (score: +0.5) | 1 | +0.5 |
| C | INCONSISTENT | — (unaffected/inconsistent path) | `CLN_AFF_MONO_UAF` (score: +0.0) | 1 | +0.0 → `CLN_UAF` |

Rolls up as (each cell = `n × per-case`):

```text
CLN_AFF (score: +1.0)
├─ CLN_AFF_MONO (score: +1.0)                 monoallelic subtotal = Σ (n × per-case)
│  ├─ CLN_AFF_MONO_SPEC_LIM (score: +0.5)     ← proband A   (1 × +0.5)
│  ├─ CLN_AFF_MONO_CONS_THOR (score: +0.5)    ← proband B   (1 × +0.5)
│  └─ CLN_AFF_MONO_UAF (score: +0.0)          ← proband C   (1 × +0.0; redirected to CLN_UAF)
└─ CLN_AFF_BIAL (∅ — not populated; MOI is AD → monoallelic only)
```

`CLN_AFF (score: +1.0)` = `CLN_AFF_MONO (score: +1.0)` + `CLN_AFF_BIAL (∅ = 0)`.

**Why each proband lands where it does** (the discriminating data items):

- **A → `CLN_AFF_MONO_SPEC_LIM`:** `pheno_specificity_for_mde`=SPECIFIC picks the SPECIFIC row;
  `non_genetic_etiology_excluded` is not `TRUE` ⇒ **not `THOR`** ⇒ the limited column ⇒ `+0.5`
  (a thorough SPECIFIC proband would instead be `CLN_AFF_MONO_SPEC_THOR`, score +1.0).
- **B → `CLN_AFF_MONO_CONS_THOR`:** CONSISTENT row; both testing flags `TRUE` and no VUS ⇒
  `THOR` ⇒ `+0.5`.
- **C → `CLN_AFF_MONO_UAF`:** `pheno_specificity_for_mde`=INCONSISTENT ⇒ the unaffected path ⇒
  `+0.0`, redirected to the `CLN_UAF` branch.

## `CLN_AFF` — GKS VA-Spec `EvidenceLine` tree (auditable, array approach)

**Alignment baseline (GA4GH GKS VA-Spec).** Every scored node in the hierarchy is a GKS
**`EvidenceLine`** — any JSON object that carries a `score` has `"type": "EvidenceLine"`:

- **`method`** — `{ "code": …, "label": … }`. `code` is the svcv4 code, or one of our proposed
  codes for the cells the svcv4 docs don't name explicitly (`CLN_AFF`, `CLN_AFF_MONO`,
  `CLN_AFF_MONO_SPEC_LIM`, …); `label` is its human name.
- **`score`** — that node's score.
- A **non-leaf** EvidenceLine (a subtotal or the roll-up) has an **`evidenceLines`** array — one or
  more child `EvidenceLine`s, whose scores are **summed and capped per the svcv4 rules** (`CLN_AFF`:
  floor 0, no upper cap).
- A **leaf** EvidenceLine (a cell code, no child EvidenceLines) has instead an **`evidenceItems`**
  array — each item `{ "id", "type", "references" (when available), "data" }`, where `data` carries
  the data elements required for that leaf's `method.code`.

The **array** therefore appears at two levels: `evidenceLines` (child lines) on every non-leaf, and
`evidenceItems` (the cases) on every leaf — **multiple probands that map to the *same* cell code sit
together in that one leaf's `evidenceItems`.**

### Auditability — the `evidenceItems` element

Each `evidenceItems` element is independently auditable and reuses existing schema (an
`EvidenceItem` wrapping a `Case` in `data`); **no new fields required**:

| `evidenceItems[]` field | Schema | Audit role |
|---|---|---|
| `id` | `EvidenceItem.id` | stable id for this observation datum |
| `type` | `EvidenceItem.type` | e.g. `"clinical_observation"` |
| `references` | `EvidenceItem.references` | PMIDs / CURIEs / URLs — the source a reviewer reopens |
| `data` | a `Case` | the attributes required for the leaf `method.code` (incl. `id`, `family_id`) |

*(`EvidenceItem.description` is available for a free-text source locator — e.g. "Table 2, family
F3, individual II-1" — if you want it on each item.)*

### `CLN_AFF` as an `EvidenceLine` tree — multiple probands per code

> **Basis — Manufactured.** Gene/MDE (MYH7 · HCM · AD) matches practice `v5-myh7`, but the
> multi-proband distribution here (3 × `SPEC_LIM`, 2 × `CONS_THOR`, 1 × `UAF`) is invented to
> demonstrate the `n × per-case` multiplier. Practice `v5-myh7`'s real cohort is 3 probands —
> SPECIFIC / CONSISTENT / INCONSISTENT — targeting `CLN_AFF_+1`.

MYH7 · HCM · **AD** with several probands per cell (`AD` ⇒ monoallelic only, so `CLN_AFF_BIAL` is
absent). Each **leaf** `evidenceItems` array holds **every** case that maps to that leaf's code:

- **3** probands → SPECIFIC · limited → leaf `CLN_AFF_MONO_SPEC_LIM`, `score = 3 × +0.5 = +1.5`
- **2** probands → CONSISTENT · thorough → leaf `CLN_AFF_MONO_CONS_THOR`, `score = 2 × +0.5 = +1.0`
- **1** proband → INCONSISTENT → leaf `CLN_AFF_MONO_UAF`, `score = 1 × +0.0 = +0.0`

```text
EvidenceLine  CLN_AFF                       score +2.5   (Σ evidenceLines; cap floor 0)
└─ evidenceLines:
   └─ EvidenceLine  CLN_AFF_MONO            score +2.5   (Σ evidenceLines)
      └─ evidenceLines:
         ├─ EvidenceLine  CLN_AFF_MONO_SPEC_LIM   score +1.5 → evidenceItems: [3 cases]
         ├─ EvidenceLine  CLN_AFF_MONO_CONS_THOR  score +1.0 → evidenceItems: [2 cases]
         └─ EvidenceLine  CLN_AFF_MONO_UAF        score +0.0 → evidenceItems: [1 case]
```

```json
{
  "type": "EvidenceLine",
  "method": { "code": "CLN_AFF", "label": "Clinical observation in affected individual(s)" },
  "score": 2.5,
  "evidenceLines": [
    {
      "type": "EvidenceLine",
      "method": { "code": "CLN_AFF_MONO", "label": "CLN_AFF — monoallelic (Table 1) subtotal" },
      "score": 2.5,
      "evidenceLines": [
        {
          "type": "EvidenceLine",
          "method": { "code": "CLN_AFF_MONO_SPEC_LIM", "label": "Affected · monoallelic · specific · limited testing" },
          "score": 1.5,
          "evidenceItems": [
            { "id": "PVS-v5-MYH7-cln-A1", "type": "clinical_observation", "references": ["PMID:12477932"],
              "data": { "id": "PVS-v5-MYH7-proband-A1", "family_id": "PVS-v5-MYH7-FAM-A1",
                        "pheno_specificity_for_mde": "SPECIFIC",
                        "testing": { "covers_all_genes_relevant_to_mde": "TRUE" },
                        "vbc_zygosity": "HET", "additional_variant_exists": "FALSE" } },
            { "id": "PVS-v5-MYH7-cln-A2", "type": "clinical_observation", "references": ["PMID:23074333"],
              "data": { "id": "PVS-v5-MYH7-proband-A2", "family_id": "PVS-v5-MYH7-FAM-A2",
                        "pheno_specificity_for_mde": "SPECIFIC",
                        "testing": { "covers_all_genes_relevant_to_mde": "TRUE" },
                        "vbc_zygosity": "HET", "additional_variant_exists": "FALSE" } },
            { "id": "PVS-v5-MYH7-cln-A3", "type": "clinical_observation", "references": ["PMID:24558114"],
              "data": { "id": "PVS-v5-MYH7-proband-A3", "family_id": "PVS-v5-MYH7-FAM-A3",
                        "pheno_specificity_for_mde": "SPECIFIC",
                        "testing": { "covers_all_genes_relevant_to_mde": "TRUE" },
                        "vbc_zygosity": "HET", "additional_variant_exists": "FALSE" } }
          ]
        },
        {
          "type": "EvidenceLine",
          "method": { "code": "CLN_AFF_MONO_CONS_THOR", "label": "Affected · monoallelic · consistent · thorough testing" },
          "score": 1.0,
          "evidenceItems": [
            { "id": "PVS-v5-MYH7-cln-B1", "type": "clinical_observation", "references": ["PMID:26332594"],
              "data": { "id": "PVS-v5-MYH7-proband-B1", "family_id": "PVS-v5-MYH7-FAM-B1",
                        "pheno_specificity_for_mde": "CONSISTENT",
                        "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
                        "vbc_zygosity": "HET", "additional_variant_exists": "FALSE" } },
            { "id": "PVS-v5-MYH7-cln-B2", "type": "clinical_observation", "references": ["PMID:28356264"],
              "data": { "id": "PVS-v5-MYH7-proband-B2", "family_id": "PVS-v5-MYH7-FAM-B2",
                        "pheno_specificity_for_mde": "CONSISTENT",
                        "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
                        "vbc_zygosity": "HET", "additional_variant_exists": "FALSE" } }
          ]
        },
        {
          "type": "EvidenceLine",
          "method": { "code": "CLN_AFF_MONO_UAF", "label": "Affected table · inconsistent phenotype (→ CLN_UAF)" },
          "score": 0.0,
          "evidenceItems": [
            { "id": "PVS-v5-MYH7-cln-C1", "type": "clinical_observation", "references": ["PMID:30297972"],
              "data": { "id": "PVS-v5-MYH7-proband-C1", "family_id": "PVS-v5-MYH7-FAM-C1",
                        "pheno_specificity_for_mde": "INCONSISTENT",
                        "vbc_zygosity": "HET", "additional_variant_exists": "FALSE" } }
          ]
        }
      ]
    }
  ]
}
```

**Scoring rule.** A **leaf** `score` = `n × per-case`, where `n = len(evidenceItems)` (all cases in
one leaf share that leaf's code, so all earn the same per-case points). A **non-leaf** `score` =
the **capped** sum of its `evidenceLines` (`CLN_AFF`: floor 0, no upper cap). Here `CLN_AFF_MONO` =
`+1.5 + +1.0 + +0.0 = +2.5`, and `CLN_AFF` = `+2.5`. Every `evidenceItems` element is independently
auditable — follow its `references` + `id` to the source, then re-derive the leaf code from `data`.

> **PMIDs above are illustrative placeholders.** Want me to pull the real MYH7 citations from the
> example's `source.md`?

### Three ways to organize the cases

The tree above is **Approach 1**. Two alternatives make each **case its own scored `EvidenceLine`**
instead of a plain `evidenceItems` datum. All three produce the same `CLN_AFF (score: +2.5)`; they
differ only in **where the per-case score and the per-cell subtotal live**. *(In the two JSON
blocks below, `data` is abbreviated to the discriminating fields — the full `Case` shape is as in
Approach 1.)*

**Approach 1 — cases as `evidenceItems` under one cell-code leaf** *(the tree above).* One leaf per
cell code; every case sits in that leaf's `evidenceItems`; `leaf score = n × per-case`. Fewest
nodes; explicit per-cell subtotal; individual cases are **data**, not scored lines.

**Approach 2 — per-case leaves under a cell-code aggregate.** Each case is a single-case
`EvidenceLine` (`score` = per-case, one `evidenceItems`); siblings of the same cell are grouped
under a cell-code **aggregate** `EvidenceLine` (`score` = their sum) beneath `CLN_AFF_MONO`. Every
case gets its own score node **and** the per-cell subtotal is preserved — deepest tree, and the
cell code appears at two levels. *(Basis — Manufactured: the same invented MYH7 cohort as Approach 1,
restructured to show the shape.)*

```text
EvidenceLine  CLN_AFF                          score +2.5   (Σ evidenceLines; cap floor 0)
└─ evidenceLines:
   └─ EvidenceLine  CLN_AFF_MONO               score +2.5   (Σ evidenceLines)
      └─ evidenceLines:
         ├─ EvidenceLine  CLN_AFF_MONO_SPEC_LIM    score +1.5   (Σ evidenceLines)  ← cell aggregate
         │  └─ evidenceLines:
         │     ├─ EvidenceLine  CLN_AFF_MONO_SPEC_LIM   score +0.5 → evidenceItems: [1 case]
         │     ├─ EvidenceLine  CLN_AFF_MONO_SPEC_LIM   score +0.5 → evidenceItems: [1 case]
         │     └─ EvidenceLine  CLN_AFF_MONO_SPEC_LIM   score +0.5 → evidenceItems: [1 case]
         ├─ EvidenceLine  CLN_AFF_MONO_CONS_THOR   score +1.0   (Σ evidenceLines)  ← cell aggregate
         │  └─ evidenceLines:
         │     ├─ EvidenceLine  CLN_AFF_MONO_CONS_THOR  score +0.5 → evidenceItems: [1 case]
         │     └─ EvidenceLine  CLN_AFF_MONO_CONS_THOR  score +0.5 → evidenceItems: [1 case]
         └─ EvidenceLine  CLN_AFF_MONO_UAF         score +0.0   (Σ evidenceLines)  ← cell aggregate
            └─ evidenceLines:
               └─ EvidenceLine  CLN_AFF_MONO_UAF      score +0.0 → evidenceItems: [1 case]
```

```json
{
  "type": "EvidenceLine", "method": { "code": "CLN_AFF", "label": "Affected observations" }, "score": 2.5,
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO", "label": "Monoallelic subtotal" }, "score": 2.5,
      "evidenceLines": [
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_SPEC_LIM", "label": "specific · limited (aggregate)" }, "score": 1.5,
          "evidenceLines": [
            { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_SPEC_LIM", "label": "specific · limited" }, "score": 0.5,
              "evidenceItems": [ { "id": "cln-A1", "type": "clinical_observation", "references": ["PMID:12477932"], "data": { "id": "proband-A1", "pheno_specificity_for_mde": "SPECIFIC", "testing": { "covers_all_genes_relevant_to_mde": "TRUE" } } } ] },
            { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_SPEC_LIM", "label": "specific · limited" }, "score": 0.5,
              "evidenceItems": [ { "id": "cln-A2", "type": "clinical_observation", "references": ["PMID:23074333"], "data": { "id": "proband-A2", "pheno_specificity_for_mde": "SPECIFIC", "testing": { "covers_all_genes_relevant_to_mde": "TRUE" } } } ] },
            { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_SPEC_LIM", "label": "specific · limited" }, "score": 0.5,
              "evidenceItems": [ { "id": "cln-A3", "type": "clinical_observation", "references": ["PMID:24558114"], "data": { "id": "proband-A3", "pheno_specificity_for_mde": "SPECIFIC", "testing": { "covers_all_genes_relevant_to_mde": "TRUE" } } } ] }
          ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_CONS_THOR", "label": "consistent · thorough (aggregate)" }, "score": 1.0,
          "evidenceLines": [
            { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_CONS_THOR", "label": "consistent · thorough" }, "score": 0.5,
              "evidenceItems": [ { "id": "cln-B1", "type": "clinical_observation", "references": ["PMID:26332594"], "data": { "id": "proband-B1", "pheno_specificity_for_mde": "CONSISTENT", "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" } } } ] },
            { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_CONS_THOR", "label": "consistent · thorough" }, "score": 0.5,
              "evidenceItems": [ { "id": "cln-B2", "type": "clinical_observation", "references": ["PMID:28356264"], "data": { "id": "proband-B2", "pheno_specificity_for_mde": "CONSISTENT", "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" } } } ] }
          ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_UAF", "label": "inconsistent (aggregate)" }, "score": 0.0,
          "evidenceLines": [
            { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_UAF", "label": "inconsistent → CLN_UAF" }, "score": 0.0,
              "evidenceItems": [ { "id": "cln-C1", "type": "clinical_observation", "references": ["PMID:30297972"], "data": { "id": "proband-C1", "pheno_specificity_for_mde": "INCONSISTENT" } } ] }
          ] }
      ] }
  ]
}
```

**Approach 3 — per-case leaves flat under `CLN_AFF_MONO`.** Each case is a single-case
`EvidenceLine` (`score` = per-case, one `evidenceItems`); **all** are siblings directly under
`CLN_AFF_MONO`, which sums them. Every case gets its own score node; flatter than Approach 2, but
there is **no per-cell subtotal node** — a cell's total is the sum of the siblings sharing its code.
*(Basis — Manufactured: the same invented MYH7 cohort as Approach 1, restructured to show the shape.)*

```text
EvidenceLine  CLN_AFF                          score +2.5   (Σ evidenceLines; cap floor 0)
└─ evidenceLines:
   └─ EvidenceLine  CLN_AFF_MONO               score +2.5   (Σ evidenceLines)
      └─ evidenceLines:            (no per-cell subtotal node — cell total = Σ siblings sharing the code)
         ├─ EvidenceLine  CLN_AFF_MONO_SPEC_LIM    score +0.5 → evidenceItems: [1 case]
         ├─ EvidenceLine  CLN_AFF_MONO_SPEC_LIM    score +0.5 → evidenceItems: [1 case]
         ├─ EvidenceLine  CLN_AFF_MONO_SPEC_LIM    score +0.5 → evidenceItems: [1 case]
         ├─ EvidenceLine  CLN_AFF_MONO_CONS_THOR   score +0.5 → evidenceItems: [1 case]
         ├─ EvidenceLine  CLN_AFF_MONO_CONS_THOR   score +0.5 → evidenceItems: [1 case]
         └─ EvidenceLine  CLN_AFF_MONO_UAF         score +0.0 → evidenceItems: [1 case]
```

```json
{
  "type": "EvidenceLine", "method": { "code": "CLN_AFF", "label": "Affected observations" }, "score": 2.5,
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO", "label": "Monoallelic subtotal" }, "score": 2.5,
      "evidenceLines": [
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_SPEC_LIM", "label": "specific · limited" }, "score": 0.5,
          "evidenceItems": [ { "id": "cln-A1", "type": "clinical_observation", "references": ["PMID:12477932"], "data": { "id": "proband-A1", "pheno_specificity_for_mde": "SPECIFIC", "testing": { "covers_all_genes_relevant_to_mde": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_SPEC_LIM", "label": "specific · limited" }, "score": 0.5,
          "evidenceItems": [ { "id": "cln-A2", "type": "clinical_observation", "references": ["PMID:23074333"], "data": { "id": "proband-A2", "pheno_specificity_for_mde": "SPECIFIC", "testing": { "covers_all_genes_relevant_to_mde": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_SPEC_LIM", "label": "specific · limited" }, "score": 0.5,
          "evidenceItems": [ { "id": "cln-A3", "type": "clinical_observation", "references": ["PMID:24558114"], "data": { "id": "proband-A3", "pheno_specificity_for_mde": "SPECIFIC", "testing": { "covers_all_genes_relevant_to_mde": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_CONS_THOR", "label": "consistent · thorough" }, "score": 0.5,
          "evidenceItems": [ { "id": "cln-B1", "type": "clinical_observation", "references": ["PMID:26332594"], "data": { "id": "proband-B1", "pheno_specificity_for_mde": "CONSISTENT", "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_CONS_THOR", "label": "consistent · thorough" }, "score": 0.5,
          "evidenceItems": [ { "id": "cln-B2", "type": "clinical_observation", "references": ["PMID:28356264"], "data": { "id": "proband-B2", "pheno_specificity_for_mde": "CONSISTENT", "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_MONO_UAF", "label": "inconsistent → CLN_UAF" }, "score": 0.0,
          "evidenceItems": [ { "id": "cln-C1", "type": "clinical_observation", "references": ["PMID:30297972"], "data": { "id": "proband-C1", "pheno_specificity_for_mde": "INCONSISTENT" } } ] }
      ] }
  ]
}
```

**Trade-offs**

| | Per-case score node | Per-cell subtotal node | Tree depth | Cell code repeats |
|---|---|---|---|---|
| **1** cases in `evidenceItems` | ✗ (cases are data) | ✓ (the leaf) | shallowest | once per cell |
| **2** per-case + aggregate | ✓ | ✓ (the aggregate) | deepest | aggregate **and** each case |
| **3** per-case flat | ✓ | ✗ (summed on the fly) | middle | each case |

*Rule of thumb:* **Approach 1** if a case is a data point (audit trail, not a scored claim);
**Approach 2** if every case must be an independently scored, citable `EvidenceLine` *and* you want
the per-cell subtotal as a node; **Approach 3** if every case is its own scored line but the per-cell
grouping doesn't need to be a first-class node.

> **PMIDs are illustrative placeholders** in all three.

## `CLN_AFF` — biallelic (`BIAL`) worked example

For a **biallelic** MDE (e.g. USH2A · Usher syndrome · **AR**), `CLN_AFF_MONO` is absent, so
`CLN_AFF = CLN_AFF_BIAL`. The biallelic cells fan across the **second-variant status** (columns:
`CTP`/`ATP`/`CTV`/`HOM`/`NON`) and **co-occurrence × thoroughness** (rows: `RARE`/`UNCM`/`INCP`,
plus the two override rows). This section has two parts: first the **code catalog** — every cell of
Table 2 and the code it mints — then a **realistic worked example** showing how one real variant +
MDE populates only a *few* of those cells.

### Every cell of Table 2 → a code

SM 4 Table 2 is a **5 × 5 grid (25 positions)**, but only the positions with a *distinct case
signature* are separately reachable — several grid positions collapse because the case attributes
that would reach them are identical. The grid below shows the `method.code` (abbreviated
`…` = `CLN_AFF_BIAL_`) and score for every position:

| Row ＼ Col | `CTP` | `ATP` | `CTV` | `HOM` | `NON` |
|---|---|---|---|---|---|
| **RARE** (co-occ <0.0001, thorough) | `…RARE_CTP` +3.0 | `…RARE_ATP` +1.5 | `…RARE_CTV` +1.5 | `…THOR_HOM` +1.0 ¹ | `…NON` 0 ² |
| **UNCM** (co-occ 0.0001–0.01, thorough) | `…UNCM_CTP` +2.0 | `…UNCM_ATP` +1.0 | `…UNCM_CTV` +1.0 | `…THOR_HOM` +1.0 ¹ | `…NON` 0 ² |
| **INCP** (incomplete) | `…INCP_CTP` +1.0 | `…INCP_ATP` +0.75 | `…INCP_CTV` +0.5 | `…INCP_HOM` +0.5 | `…NON` 0 ² |
| **ALT-CAUSE** (P/LP alt, diff gene) | `…ALT` 0 ³ | `…ALT` 0 ³ | `…ALT` 0 ³ | `…ALT` 0 ³ | `…ALT` 0 ³ |
| **NOT-CONSISTENT** (INCONSISTENT) | `…UAF` 0 ⁴ | `…UAF` 0 ⁴ | `…UAF` 0 ⁴ | `…UAF` 0 ⁴ | `…UAF` 0 ⁴ |

Where positions share a code (the collapses):

- ¹ **`HOM` · RARE = UNCM.** Co-occurrence is the likelihood of *two heterozygous* variants — it is
  undefined for a homozygote, so `RARE×HOM` and `UNCM×HOM` have the *same* signature (homozygous ·
  thorough) → one reachable code `…THOR_HOM`. Only thoroughness distinguishes HOM (`THOR_HOM` +1.0
  vs `INCP_HOM` +0.5). A curator can never assign a homozygote to a co-occurrence row.
- ² **`NON` · row-invariant.** A het with no valid in-trans 2nd variant earns 0 biallelic points
  regardless of the co-occurrence row → one code (its several signatures all resolve to the same
  `+0.0` cell — per the code-minting rule below).
- ³ **ALT-CAUSE · column-invariant.** A P/LP alternate cause (different gene) overrides every column
  to 0 → one code (redirect `CLN_ALT`).
- ⁴ **NOT-CONSISTENT · column-invariant.** An inconsistent phenotype overrides every column to 0 →
  one code (redirect `CLN_UAF`).

**⇒ 14 uniquely-reachable codes:** `RARE_{CTP,ATP,CTV}`, `UNCM_{CTP,ATP,CTV}`, `INCP_{CTP,ATP,CTV}`,
`THOR_HOM`, `INCP_HOM`, `NON`, `ALT`, `UAF` (each prefixed `CLN_AFF_BIAL_`).

**Code-minting rule (decided).** A `method.code` is minted **per cell — one distinct scoring
opportunity, i.e. a single point value (or a range, for roll-up/parent codes).** A **cell**, not a
point value, is the unit of a code. Every case signature that resolves to the same cell shares that
code, and its cases group in that code's `evidenceItems`. Consequences:

- **`NON` stays merged** — its several signatures (no 2nd variant, *cis*, unknown phase, assumed
  VUS, benign 2nd) all resolve to the one `+0.0` "none" cell → `CLN_AFF_BIAL_NON`. Likewise
  `THOR_HOM`, `ALT`, and `UAF` are each one cell.
- **Distinct cells keep distinct codes even when their point values coincide** — e.g. `…RARE_ATP`
  and `…RARE_CTV` are both `+1.5` but are different cells (different second-variant status), so they
  stay separate codes.

⇒ `CLN_AFF_BIAL` = **14** codes (the set listed above).

### Which attributes reach each `BIAL` code

`thorough♦` = `covers_all_genes_relevant_to_mde`=TRUE **and** `non_genetic_etiology_excluded`=TRUE
**and** no VUS additional variant. All rows require `pheno_specificity_for_mde`≠INCONSISTENT unless
noted.

| Code | `vbc_zygosity` | `compound_het_variant.classification` | `.phase_confidence` | `.co_occurrence_likelihood` | thorough♦ | per-case |
|---|---|---|---|---|---|---|
| `CLN_AFF_BIAL_RARE_CTP` | HET | P/LP | HIGH | `LT_0_0001` | ✓ | +3.0 |
| `CLN_AFF_BIAL_RARE_ATP` | HET | P/LP | ≠HIGH | `LT_0_0001` | ✓ | +1.5 |
| `CLN_AFF_BIAL_RARE_CTV` | HET | VUS | HIGH | `LT_0_0001` | ✓ | +1.5 |
| `CLN_AFF_BIAL_UNCM_CTP` | HET | P/LP | HIGH | `BETWEEN_0_0001_0_01` | ✓ | +2.0 |
| `CLN_AFF_BIAL_UNCM_ATP` | HET | P/LP | ≠HIGH | `BETWEEN_0_0001_0_01` | ✓ | +1.0 |
| `CLN_AFF_BIAL_UNCM_CTV` | HET | VUS | HIGH | `BETWEEN_0_0001_0_01` | ✓ | +1.0 |
| `CLN_AFF_BIAL_INCP_CTP` | HET | P/LP | HIGH | `NOT_ASSESSED` *(or not thorough)* | ✗ | +1.0 |
| `CLN_AFF_BIAL_INCP_ATP` | HET | P/LP | ≠HIGH | `NOT_ASSESSED` *(or not thorough)* | ✗ | +0.75 |
| `CLN_AFF_BIAL_INCP_CTV` | HET | VUS | HIGH | `NOT_ASSESSED` *(or not thorough)* | ✗ | +0.5 |
| `CLN_AFF_BIAL_THOR_HOM` | HOM | — | — | N/A | ✓ | +1.0 |
| `CLN_AFF_BIAL_INCP_HOM` | HOM | — | — | N/A | ✗ | +0.5 |
| `CLN_AFF_BIAL_NON` | HET | none / *cis* / absent / (VUS·≠HIGH) / B / LB | — | — | — | +0.0 |
| `CLN_AFF_BIAL_ALT` | — | — | — | — | — | +0.0 → `CLN_ALT` *(≥1 P/LP additional variant, different gene)* |
| `CLN_AFF_BIAL_UAF` | — | — | — | — | — | +0.0 → `CLN_UAF` *(`pheno_specificity_for_mde`=INCONSISTENT)* |

### `EvidenceLine` tree — a realistic biallelic classification (USH2A · Usher syndrome type 2 · AR)

> **Basis — Grounded (practice variant `v20-ush2a`).** The gene, MDE, and the three-proband
> second-allele pattern are drawn from a practice variant. Contrast the *catalog* grid above, which
> is **manufactured** to display all 14 codes at once and is not a real classification.

The catalog lists *all 14* codes, but **no single variant + MDE realistically fills every cell** —
cells like `ALT` (an alternate P/LP cause in another gene) or `UAF` (an inconsistent phenotype)
rarely co-occur with strong pathogenic cells for the *same* variant. A real classification populates
only a **few** cells. Here, **three unrelated affected biallelic probands** share one VBC but land in
**three different cells**, because each proband's **second allele differs**:

- **Proband 1** — **homozygous** for the VBC → `CLN_AFF_BIAL_THOR_HOM` (**+1.0**)
- **Proband 2** — heterozygous, second allele a **confirmed-in-trans VUS** → `CLN_AFF_BIAL_RARE_CTV` (**+1.5**)
- **Proband 3** — heterozygous, second allele a **confirmed-in-trans known Pathogenic LoF** → `CLN_AFF_BIAL_RARE_CTP` (**+3.0**)

`Σ = +5.5` → `CLN_AFF (score: +5.5)`. `data` is abbreviated to discriminators.

```text
EvidenceLine  CLN_AFF                          score +5.5   (Σ evidenceLines; cap floor 0)
└─ evidenceLines:
   └─ EvidenceLine  CLN_AFF_BIAL               score +5.5   (Σ evidenceLines)
      └─ evidenceLines:
         ├─ EvidenceLine  CLN_AFF_BIAL_THOR_HOM    score +1.0 → evidenceItems: [1 case]  (proband 1 · homozygous VBC)
         ├─ EvidenceLine  CLN_AFF_BIAL_RARE_CTV    score +1.5 → evidenceItems: [1 case]  (proband 2 · in-trans VUS)
         └─ EvidenceLine  CLN_AFF_BIAL_RARE_CTP    score +3.0 → evidenceItems: [1 case]  (proband 3 · in-trans P)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "CLN_AFF", "label": "Affected observations" }, "score": 5.5,
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL", "label": "Biallelic (Table 2) subtotal" }, "score": 5.5,
      "evidenceLines": [
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_THOR_HOM", "label": "homozygous · thorough" }, "score": 1.0,
          "evidenceItems": [ { "id": "ush2a-proband-1", "type": "clinical_observation", "references": ["practice-variant-set:v20-ush2a"],
            "description": "Illustrative — proband 1 homozygous for the VBC; classic Usher type 2.",
            "data": { "id": "ush2a-proband-1", "family_id": "ush-fam-1", "pop_frq_vbc_score": 0.0, "pheno_specificity_for_mde": "SPECIFIC", "vbc_zygosity": "HOM",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_RARE_CTV", "label": "rare · confirmed-trans VUS" }, "score": 1.5,
          "evidenceItems": [ { "id": "ush2a-proband-2", "type": "clinical_observation", "references": ["practice-variant-set:v20-ush2a"],
            "description": "Illustrative — proband 2 second allele a VUS confirmed in trans.",
            "data": { "id": "ush2a-proband-2", "family_id": "ush-fam-2", "pop_frq_vbc_score": 0.0, "pheno_specificity_for_mde": "SPECIFIC", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "VUS", "phase_confidence": "HIGH", "co_occurrence_likelihood": "LT_0_0001" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_RARE_CTP", "label": "rare · confirmed-trans P/LP" }, "score": 3.0,
          "evidenceItems": [ { "id": "ush2a-proband-3", "type": "clinical_observation", "references": ["practice-variant-set:v20-ush2a"],
            "description": "Illustrative — proband 3 second allele a known Pathogenic LoF confirmed in trans.",
            "data": { "id": "ush2a-proband-3", "family_id": "ush-fam-3", "pop_frq_vbc_score": 0.0, "pheno_specificity_for_mde": "SPECIFIC", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "P", "phase_confidence": "HIGH", "co_occurrence_likelihood": "LT_0_0001" } } } ] }
      ] }
  ]
}
```

**Why three cells, one variant.** The VBC is identical across all three probands; what places each
in a different cell is the **second allele** (homozygous VBC vs in-trans VUS vs in-trans P) — exactly
the axis Table 2's columns encode. This is the biologically natural way a biallelic classification
spans cells: **different probands, different partner alleles**, not one proband in many cells.

**The multiplier still applies.** Each cell here has one proband; had two probands shared the
in-trans-P signature, `CLN_AFF_BIAL_RARE_CTP` would score `2 × +3.0 = +6.0` (the `n × per-case` rule,
shown in the monoallelic tree above).

**The exit cells** (`NON`, `ALT`, `UAF`, all `+0.0`) are omitted here because they rarely belong to
the same strong classification — they live in the **code catalog** above, and each would carry its
own auditable cases recording *why* a proband scored zero (no valid in-trans 2nd variant; an
alternate P/LP cause; or an inconsistent phenotype).

**Reconciliation note.** Practice `v20-ush2a`'s illustrative target is `CLN_AFF_+3`; the cell model
here sums to `+5.5`. The practice-set targets are cross-proband placeholders and will be reconciled
once the cell codes are finalized (see the practice-set caveat).

---

## `CLN_DNV` — De novo observations (worked branch)

**Where it sits:** HOD → CLN → `CLN_DNV` · Evidence Code Cap **0 to +12** (SM 4 Table 3). Scored
**per de-novo proband** and **additive on `CLN_AFF`** — a de-novo affected proband is counted under
*both* codes (SM 4: a PTPN11 de-novo Noonan proband earns `CLN_AFF (+1.0)` **and** `CLN_DNV
(+7.0)`). `CLN_DNV` is its own `EvidenceLine`; the same proband simply appears as a case under a
`CLN_AFF` cell and under a `CLN_DNV` cell. Cross-proband sum, floored at 0 and capped at +12.

**De-novo eligibility (the gate).** A proband is eligible only when **both parents are unaffected
for the MDE and both parental samples tested negative for the VBC** (SM 4: *"No evidence should be
awarded based on phenotypically unaffected parents who have not been genotyped"*). This is read from
`case.relatives[]`, not from a de-novo flag — the Case has none.

**Eligibility (parents genotyped VBC-negative) is separate from parentage confirmation.** The
"confirmed / unconfirmed" column is *not* the eligibility gate — it asks whether identity/genomic
testing proved the samples came from the biological parents. Both columns require genotyped
VBC-negative parents; they differ only in whether parentage was confirmed. (The current reference
scorer's `_is_de_novo` additionally requires `confirmed_parental_relationship == TRUE`, which would
make the *unconfirmed* cells unreachable — a discrepancy to reconcile; this map models the
SM 4-correct structure where both columns are reachable.)

### The three levels

1. **Cell** — each unique (phenotype × parentage-confirmation) **cell** yields a per-case score and
   its own proposed code (the `SPECIFIC` row is monoallelic-only).
2. **Aggregation** — for each cell, `n × per-case` summed across that cell's eligible de-novo
   probands.
3. **Roll-up** — `CLN_DNV` = Σ of the cells across probands, floored at 0 and **capped at +12**
   (Evidence Code Cap); the raw sum is retained alongside the capped score.

### The cells

Table 3 is a single grid: rows = phenotype consistency, columns = parentage confirmation. The
**SPECIFIC row is mono-allelic only** — biallelic disorders fold `SPECIFIC → CONSISTENT` (Table 2
has no SPECIFIC tier), so the `SPEC_*` cells are reachable only for monoallelic MOIs.

| Proposed code | phenotype | parentage | per-case | note |
|---|---|---|---|---|
| `CLN_DNV_SPEC_CONF`   | SPECIFIC *(mono only)*   | confirmed   | **+7.0** ** | ** reduce if the VBC is outside coding / adjacent-intronic regions (no VBC-region annotation → awarded in full + flagged) |
| `CLN_DNV_SPEC_UNCONF` | SPECIFIC *(mono only)*   | unconfirmed | **+2.0** | |
| `CLN_DNV_CONS_CONF`   | CONSISTENT               | confirmed   | **+4.0** | biallelic-SPECIFIC probands land here |
| `CLN_DNV_CONS_UNCONF` | CONSISTENT               | unconfirmed | **+1.0** | |
| `CLN_DNV_INCON`       | not consistent           | *(either)*  | **+0.0** | column-invariant → route to `CLN_UAF` |

Five cells — 6 grid positions (3 rows × 2 columns) collapse to 5 because the **not-consistent row is
column-invariant** (+0 whether or not parentage is confirmed), so it is one merged code (same rule
as `CLN_AFF`'s `NON`/`ALT`/`UAF`). Post-zygotic mosaic events use the **same weights** (SM 4
caveats: exclude CHIP variants, monogenic mosaic entities only, watch revertants) — a mosaic proband
resolves to the same cells, not new codes.

### Evidence data items

| Attribute (real name) | Feeds | Values |
|---|---|---|
| `case.pheno_specificity_for_mde` | row | `SPECIFIC` / `CONSISTENT` / `INCONSISTENT` (folds to `CONSISTENT` for biallelic MOI) |
| `case.confirmed_parental_relationship` | column | `TRUE` → confirmed; anything else → unconfirmed |
| `case.relatives[]` | eligibility gate | ≥2 with `parent_of_proband == TRUE`, each `vbc_exists == FALSE` and `affected_w_mde == FALSE` |
| `moi` | SPEC→CONS fold | mono MOIs keep `SPEC_*`; biallelic MOIs fold to `CONS_*` |
| *(additive)* `case.id` | ties this proband to its `CLN_AFF` case | same proband, two codes |

### Code ← data-item cross-reference

| Code | pheno row | `confirmed_parental_relationship` | `relatives[]` (both parents) | MOI |
|---|---|---|---|---|
| `CLN_DNV_SPEC_CONF`   | `SPECIFIC`     | `TRUE`   | genotyped, VBC-absent, unaffected | mono |
| `CLN_DNV_SPEC_UNCONF` | `SPECIFIC`     | ≠ `TRUE` | genotyped, VBC-absent, unaffected | mono |
| `CLN_DNV_CONS_CONF`   | `CONSISTENT` † | `TRUE`   | genotyped, VBC-absent, unaffected | any |
| `CLN_DNV_CONS_UNCONF` | `CONSISTENT` † | ≠ `TRUE` | genotyped, VBC-absent, unaffected | any |
| `CLN_DNV_INCON`       | `INCONSISTENT` | *(n/a)*  | genotyped, VBC-absent, unaffected | any |

† includes biallelic probands whose `pheno_specificity_for_mde` is `SPECIFIC` (folded).

### `CLN_DNV` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Manufactured (cap demonstration).** PTPN11 · Noonan is SM 4's worked de-novo example;
> the multi-proband set here is invented so the raw Σ (`+17.0`) overflows the `+12` code cap. A
> **real** de-novo instance lives in the practice set — `example-fbn1` proband 2 (ectopia lentis,
> confirmed de novo, SPECIFIC → `CLN_DNV_SPEC_CONF` +7.0).

A demonstration proband set for a monoallelic MDE (e.g. PTPN11 · Noonan · AD). `CONS_CONF` carries
two probands to show the `n × per-case` multiplier; the raw child sum (`+17.0`) exceeds the code cap,
so the roll-up is **capped to +12.0** — the "non-leaf = capped Σ children" rule in action. `data` is
abbreviated to the discriminators + the de-novo gate.

```text
EvidenceLine  CLN_DNV                        score +12.0  (Σ evidenceLines capped 0…+12; raw +17.0)
└─ evidenceLines:
   ├─ EvidenceLine  CLN_DNV_SPEC_CONF          score +7.0 → evidenceItems: [1 case]
   ├─ EvidenceLine  CLN_DNV_SPEC_UNCONF        score +2.0 → evidenceItems: [1 case]
   ├─ EvidenceLine  CLN_DNV_CONS_CONF          score +8.0 → evidenceItems: [2 cases]  (2 × +4.0)
   └─ EvidenceLine  CLN_DNV_INCON              score +0.0 → evidenceItems: [1 case]  (→ CLN_UAF)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "CLN_DNV", "label": "De novo observations" }, "score": 12.0,
  "note": "raw Σ children = +17.0; Evidence Code Cap 0 to +12 → +12.0",
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "CLN_DNV_SPEC_CONF", "label": "specific · confirmed parentage" }, "score": 7.0,
      "evidenceItems": [ { "id": "dnv-01", "type": "clinical_observation", "references": ["PMID:16358218"],
        "data": { "id": "proband-A", "family_id": "fam-A", "pop_frq_vbc_score": 0.0, "pheno_specificity_for_mde": "SPECIFIC",
          "confirmed_parental_relationship": "TRUE",
          "relatives": [ { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" },
                         { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" } ] } } ] },
    { "type": "EvidenceLine", "method": { "code": "CLN_DNV_SPEC_UNCONF", "label": "specific · unconfirmed parentage" }, "score": 2.0,
      "evidenceItems": [ { "id": "dnv-02", "type": "clinical_observation", "references": ["PMID:16358218"],
        "data": { "id": "proband-B", "family_id": "fam-B", "pop_frq_vbc_score": 0.0, "pheno_specificity_for_mde": "SPECIFIC",
          "confirmed_parental_relationship": "FALSE",
          "relatives": [ { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" },
                         { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" } ] } } ] },
    { "type": "EvidenceLine", "method": { "code": "CLN_DNV_CONS_CONF", "label": "consistent · confirmed parentage" }, "score": 8.0,
      "evidenceItems": [
        { "id": "dnv-03a", "type": "clinical_observation", "references": ["PMID:19077116"],
          "data": { "id": "proband-C", "family_id": "fam-C", "pop_frq_vbc_score": 0.0, "pheno_specificity_for_mde": "CONSISTENT",
            "confirmed_parental_relationship": "TRUE",
            "relatives": [ { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" },
                           { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" } ] } },
        { "id": "dnv-03b", "type": "clinical_observation", "references": ["PMID:22585553"],
          "data": { "id": "proband-D", "family_id": "fam-D", "pop_frq_vbc_score": 0.0, "pheno_specificity_for_mde": "CONSISTENT",
            "confirmed_parental_relationship": "TRUE",
            "relatives": [ { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" },
                           { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" } ] } }
      ] },
    { "type": "EvidenceLine", "method": { "code": "CLN_DNV_INCON", "label": "phenotype not consistent" }, "score": 0.0,
      "evidenceItems": [ { "id": "dnv-04", "type": "clinical_observation", "references": ["PMID:20301303"],
        "data": { "id": "proband-E", "family_id": "fam-E", "pheno_specificity_for_mde": "INCONSISTENT",
          "confirmed_parental_relationship": "TRUE",
          "relatives": [ { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" },
                         { "parent_of_proband": "TRUE", "vbc_exists": "FALSE", "affected_w_mde": "FALSE" } ] } } ] }
  ]
}
```

`CONS_CONF` scores `2 × +4.0 = +8.0` (multiplier). Raw child sum `7.0 + 2.0 + 8.0 + 0.0 = +17.0`
exceeds the `0 to +12` code cap, so `CLN_DNV` reports **+12.0** — the first worked cap in this map,
and the reason a non-leaf keeps *both* the raw sum (in `note`) and the capped `score`. The
`INCON` leaf is kept even at `+0.0`: it records *why* an eligible de-novo proband contributed no
points (and routes the individual to `CLN_UAF`). Every proband here is genotype-eligible (both
parents VBC-negative); a proband whose parents were not genotyped never reaches `CLN_DNV` at all.

---

## `CLN_ALTV` / `CLN_ALTG` — Alternative causative variant (worked branch)

**Where it sits:** HOD → Clinical Observations (CLN) → `CLN_ALTV` / `CLN_ALTG` · **benignity-only
(≤ 0)** (SM 4 Table 4). The VBC is seen in an **affected** individual whose phenotype is already
explained by a **P/LP alternate cause**. Scored **per individual**, summed. Two codes by *where* the
alternate variant sits:

- **`CLN_ALTV`** — the alternate P/LP is in the **same gene** as the VBC.
- **`CLN_ALTG`** — the alternate P/LP is in a **different gene** associated with the phenotype.

Not applicable to AR MDEs or MDEs with multiple genetic contributions — except the semidominant
`_REC` case below (SM 4's BRCA2 / Fanconi example: a P variant confirmed in trans that would give a
severe biallelic phenotype, which is *not* observed).

### The three levels

1. **Cell** — the phenotype-severity row selects a per-individual score.
2. **Aggregation** — `n × per-case` summed across the individuals of that cell.
3. **Roll-up** — `CLN_ALTV` / `CLN_ALTG` = Σ their cells, **benignity-only (≤ 0)**.

### The cells

| Proposed code | phenotype severity vs expectation | per-case |
|---|---|---|
| `CLN_ALTV_BOTH` / `CLN_ALTG_BOTH` | more severe than expected, **or** ≥ expected for >1 allele (both alleles contribute) | **0.0** |
| `CLN_ALTV_ONE` / `CLN_ALTG_ONE`   | **not** more severe (only the alternate allele contributes) | **−0.5** |
| `CLN_ALTV_REC`                    | recessive/biallelic phenotype **not** observed despite VBC + alt in trans, penetrance >80% (**same gene only**) | **−1.0** |

`CLN_ALTG` has **no `_REC` cell** — the `−1.0` row is same-gene only (Table 4).

### Evidence data items

| Attribute (real name) | Feeds | Values |
|---|---|---|
| `case.additional_variants[].classification` | gate | at least one `P`/`LP` alternate cause |
| `case.additional_variants[].phase_in_ref_to_vbc` | ALTV vs ALTG | not `None` → same gene → `ALTV`; `None` → different gene → `ALTG` |
| `case.pheno_severity` | severity row | `MONO_GT_OR_BIALLELIC_EQ_EXPECTED` → `BOTH`; `MONO_EQ_EXPECTED` → `ONE`; `BIALLELIC_LT_EXPECTED` → `REC` |
| `case.age_matched_penetrance` | `_REC` gate | must be >80% (`PCT_80_100` / `NEAR_100`) |

### Code ← data-item cross-reference

| Code | alt-variant location | `pheno_severity` | penetrance |
|---|---|---|---|
| `CLN_ALTV_BOTH` / `CLN_ALTG_BOTH` | same / different gene | `MONO_GT_OR_BIALLELIC_EQ_EXPECTED` | — |
| `CLN_ALTV_ONE` / `CLN_ALTG_ONE`   | same / different gene | `MONO_EQ_EXPECTED`                  | — |
| `CLN_ALTV_REC`                    | same gene             | `BIALLELIC_LT_EXPECTED`             | >80% |

### `CLN_ALTV` / `CLN_ALTG` as GKS `EvidenceLine` trees (Approach 1)

> **Basis — Grounded (practice `v11-acvrl1`).** ACVRL1 · hereditary hemorrhagic telangiectasia · AD.
> One VBC, two alternate-cause scenarios: a P LoF in **ACVRL1** (same gene → `CLN_ALTV`) and a P LoF
> in **ENG** (a different HHT gene → `CLN_ALTG`). Both present as **typical HHT** (not more severe →
> the alternate allele explains the phenotype), so each lands in the `ONE` cell → **−0.5**.

`CLN_ALTV` and `CLN_ALTG` are **separate codes** (not summed under one parent). Here each has one
affected individual whose HHT is explained by the alternate P/LP cause:

```text
EvidenceLine  CLN_ALTV                    score -0.5   (Σ evidenceLines; benignity-only ≤ 0)
└─ evidenceLines:
   └─ EvidenceLine  CLN_ALTV_ONE          score -0.5 → evidenceItems: [1 case]  (same-gene ACVRL1 P LoF in trans · typical HHT)

EvidenceLine  CLN_ALTG                    score -0.5   (Σ evidenceLines; benignity-only ≤ 0)
└─ evidenceLines:
   └─ EvidenceLine  CLN_ALTG_ONE          score -0.5 → evidenceItems: [1 case]  (different-gene ENG P LoF · typical HHT)
```

```json
[
  {
    "type": "EvidenceLine", "method": { "code": "CLN_ALTV", "label": "Alternative cause · same gene" }, "score": -0.5,
    "evidenceLines": [
      { "type": "EvidenceLine", "method": { "code": "CLN_ALTV_ONE", "label": "alt explains phenotype · not more severe" }, "score": -0.5,
        "evidenceItems": [ { "id": "altv-01", "type": "clinical_observation", "references": ["practice-variant-set:v11-acvrl1"],
          "description": "Grounded — typical HHT; a Pathogenic LoF ACVRL1 variant confirmed in trans accounts for the phenotype.",
          "data": { "id": "acvrl1-proband-a", "pheno_severity": "MONO_EQ_EXPECTED",
            "additional_variants": [ { "id": "acvrl1-alt", "classification": "P", "phase_in_ref_to_vbc": "TRANS" } ] } } ] }
    ]
  },
  {
    "type": "EvidenceLine", "method": { "code": "CLN_ALTG", "label": "Alternative cause · different gene" }, "score": -0.5,
    "evidenceLines": [
      { "type": "EvidenceLine", "method": { "code": "CLN_ALTG_ONE", "label": "alt explains phenotype · not more severe" }, "score": -0.5,
        "evidenceItems": [ { "id": "altg-01", "type": "clinical_observation", "references": ["practice-variant-set:v11-acvrl1"],
          "description": "Grounded — typical HHT; a Pathogenic LoF in ENG (a different HHT gene) accounts for the phenotype.",
          "data": { "id": "acvrl1-proband-b", "pheno_severity": "MONO_EQ_EXPECTED",
            "additional_variants": [ { "id": "eng-alt", "classification": "P", "phase_in_ref_to_vbc": null } ] } } ] }
    ]
  }
]
```

The `_REC` cell (`CLN_ALTV_REC`, −1.0) is not shown: it is the semidominant case where the VBC + a
P/LP in trans would predict a **severe biallelic** phenotype that is **not** observed (SM 4's BRCA2 /
Fanconi example), with penetrance >80%. Practice `v26-msh6` is another `CLN_ALTV` instance (a
truncating MSH6 variant in trans accounts for the Lynch phenotype).

**Reconciliation note.** Practice `v11-acvrl1` illustratively targets `−1.0` for each of `CLN_ALTV`
and `CLN_ALTG`; the Table-4 cell model gives `−0.5` for `MONO_EQ_EXPECTED`. Reconcile once the cells
are finalized.

---

## `CLN_UAF` — Unaffected observations (worked branch)

**Where it sits:** HOD → Clinical Observations (CLN) → `CLN_UAF` · **benignity-only (≤ 0)** (SM 4
Table 5). Scored **per well-phenotyped unaffected individual**, then **summed** across individuals.
An unaffected individual only counts if they are **within the age range of the penetrance estimate**
(age-matched); if penetrance is unknown, or the individual is younger than the penetrance window, no
points are awarded.

**Age-matched penetrance gate.** SM 4: *"the unaffected individual needs to be in the age range of
the penetrance estimate to be considered … If the penetrance estimates are unknown for the MDE, then
no points should be applied."* So an unaffected carrier who is too young (or an MDE with unknown
penetrance) lands in the zero cell, not a negative one.

### The three levels

1. **Cell** — each (penetrance-band × signature-strength) is a distinct scoring opportunity → its
   own proposed code.
2. **Aggregation** — for each cell, `n × per-case` summed across that cell's well-phenotyped
   unaffected individuals.
3. **Roll-up** — `CLN_UAF` = Σ of the cells, **benignity-only (≤ 0)**; feeds the **CLN** category
   (cross-proband sum; `CLN_CCS` exclusivity is handled at aggregation).

### The cells

Table 5 lists **four columns** — *dominant/SD*, *rec/XL homozygous-or-hemizygous*, *rec/XL
confirmed-trans P*, *rec/XL confirmed-trans LP* — but the **first three are point-identical across
every penetrance row** (`−4 / −2 / 0`), so they collapse to one **`FULL`** signature; only
**confirmed-trans LP** is reduced (`−2 / −1 / 0`) → **`RED`**. Penetrance `<80%` (or unknown) is `0`
for every column → one `LOW` cell; a rec/XL het with **no** confirmed-trans P/LP (or unknown phase)
is `0` → `NON`.

| Proposed code | penetrance (age-matched) | signature | per-case |
|---|---|---|---|
| `CLN_UAF_FULL_NEAR` | near 100%      | dom/SD · **or** rec/XL homo/hemi · **or** rec/XL confirmed-trans P | **−4.0** |
| `CLN_UAF_FULL_HIGH` | 80–100%        | *(same as above)*                                                 | **−2.0** |
| `CLN_UAF_RED_NEAR`  | near 100%      | rec/XL confirmed-trans **LP**                                     | **−2.0** |
| `CLN_UAF_RED_HIGH`  | 80–100%        | rec/XL confirmed-trans **LP**                                     | **−1.0** |
| `CLN_UAF_LOW`       | <80% / unknown | *(any signature)* — column-invariant                             | **0.0** |
| `CLN_UAF_NON`       | *(any)*        | rec/XL het · no confirmed-trans P/LP (or unknown phase)           | **0.0** |
| `CLN_UAF`           | roll-up        | Σ cells                                                           | **≤ 0** |

The `FULL` collapse follows the code-minting rule: dominant carrier, recessive homozygote, and
recessive confirmed-trans-P **never diverge** in score across the penetrance rows, so they are the
*same* scoring opportunity → one code. `RED` (trans-LP) diverges → its own code. (Contrast `CLN_AFF`,
where `RARE_ATP` and `RARE_CTV` share `+1.5` at one row but diverge at another, so they stay
separate.)

### Evidence data items

| Attribute (real name) | Feeds | Values |
|---|---|---|
| `moi` | signature family | dom/SD → `FULL`; rec/XL → by zygosity / trans classification |
| `case.age_matched_penetrance` | penetrance row + age gate | `NEAR_100` / `PCT_80_100` / `LT_80` (or `None` → `LOW`) |
| `case.vbc_zygosity` | rec/XL signature | `HOM`/`HEMI` → `FULL`; `HET` → check the in-trans variant |
| `case.compound_het_variant.classification` | rec/XL het trans | `P` → `FULL`; `LP` → `RED`; none/other → `NON` |
| `case.affected_w_mde` | eligibility | must be `FALSE` (well-phenotyped, unaffected, age-matched) |

### Code ← data-item cross-reference

| Code | `age_matched_penetrance` | signature attributes |
|---|---|---|
| `CLN_UAF_FULL_NEAR` | `NEAR_100`    | dom/SD; **or** `vbc_zygosity` HOM/HEMI; **or** HET + trans `P` |
| `CLN_UAF_FULL_HIGH` | `PCT_80_100`  | *(same as above)* |
| `CLN_UAF_RED_NEAR`  | `NEAR_100`    | `vbc_zygosity` HET + `compound_het_variant.classification` `LP` |
| `CLN_UAF_RED_HIGH`  | `PCT_80_100`  | HET + trans `LP` |
| `CLN_UAF_LOW`       | `LT_80` / `None` | *(any)* |
| `CLN_UAF_NON`       | *(any)*       | rec/XL, HET, no confirmed-trans P/LP (or unknown phase) |

### `CLN_UAF` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Manufactured (negative cells) + grounded zero cells.** No practice variant scores
> `CLN_UAF` negative, so the `−4.0` / `−2.0` cells are invented — a dominant MDE with well-phenotyped
> unaffected adult carriers, which is strong benign evidence. The **zero** cells are grounded:
> `v1-actc1` (unaffected carrier not age-matched → `LOW`) and `v8-trdn` (unaffected het, no
> confirmed-trans P/LP → `NON`).

A dominant MDE with **four well-phenotyped unaffected carriers**. They land in different cells by
their **age-matched penetrance** — an older carrier past the near-100% penetrance age is stronger
benign evidence than a young one below the penetrance window. This is the same *"different
individuals, different cells"* logic as the USH2A biallelic example, here driven by **age-matched
penetrance** rather than the second allele. `Σ = −10.0`.

```text
EvidenceLine  CLN_UAF                       score -10.0  (Σ evidenceLines; benignity-only ≤ 0)
└─ evidenceLines:
   ├─ EvidenceLine  CLN_UAF_FULL_NEAR         score -8.0 → evidenceItems: [2 cases]  (2 × -4.0 · near-100% penetrance)
   ├─ EvidenceLine  CLN_UAF_FULL_HIGH         score -2.0 → evidenceItems: [1 case]   (80-100% penetrance)
   └─ EvidenceLine  CLN_UAF_LOW               score  0.0 → evidenceItems: [1 case]   (young carrier · below penetrance age → 0)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "CLN_UAF", "label": "Unaffected observations (benignity)" }, "score": -10.0,
  "note": "benignity-only; per well-phenotyped unaffected individual; cross-proband sum",
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "CLN_UAF_FULL_NEAR", "label": "full-strength · near-100% penetrance" }, "score": -8.0,
      "evidenceItems": [
        { "id": "uaf-01", "type": "clinical_observation", "references": [],
          "description": "Manufactured — well-phenotyped unaffected adult carrier past the near-100% penetrance age.",
          "data": { "id": "unaff-1", "family_id": "uaf-fam-1", "affected_w_mde": "FALSE", "vbc_zygosity": "HET", "age_matched_penetrance": "NEAR_100" } },
        { "id": "uaf-02", "type": "clinical_observation", "references": [],
          "description": "Manufactured — second unaffected adult carrier, same signature (multiplier).",
          "data": { "id": "unaff-2", "family_id": "uaf-fam-2", "affected_w_mde": "FALSE", "vbc_zygosity": "HET", "age_matched_penetrance": "NEAR_100" } }
      ] },
    { "type": "EvidenceLine", "method": { "code": "CLN_UAF_FULL_HIGH", "label": "full-strength · 80-100% penetrance" }, "score": -2.0,
      "evidenceItems": [ { "id": "uaf-03", "type": "clinical_observation", "references": [],
        "description": "Manufactured — unaffected carrier in the 80-100% age-matched penetrance band.",
        "data": { "id": "unaff-3", "family_id": "uaf-fam-3", "affected_w_mde": "FALSE", "vbc_zygosity": "HET", "age_matched_penetrance": "PCT_80_100" } } ] },
    { "type": "EvidenceLine", "method": { "code": "CLN_UAF_LOW", "label": "age-matched penetrance <80% -> no points" }, "score": 0.0,
      "evidenceItems": [ { "id": "uaf-04", "type": "clinical_observation", "references": ["practice-variant-set:v1-actc1"],
        "description": "Grounded — young unaffected carrier below the penetrance age window (cf. practice v1-actc1 proband 2).",
        "data": { "id": "unaff-4", "family_id": "uaf-fam-4", "affected_w_mde": "FALSE", "vbc_zygosity": "HET", "age_matched_penetrance": "LT_80" } } ] }
  ]
}
```

`CLN_UAF_FULL_NEAR` scores `2 × −4.0 = −8.0` (multiplier). The `LOW` leaf is kept even at `0.0`: it
records an unaffected carrier who is real evidence but below the penetrance age window — exactly the
`v1-actc1` situation. The `NON` cell (not shown) is the `v8-trdn` situation — an unaffected het with
no confirmed-trans P/LP. Both zero cells stay as auditable nodes so a reviewer sees *why* the
individual scored zero.

---

## `CLN_CCS` — Case-control (worked branch)

**Where it sits:** HOD → Clinical Observations (CLN) → `CLN_CCS` · **pathogenic**, `0` or `+4.0`
(SM 4). A robust **variant-specific case-control** study — the VBC's frequency in a cohort of
affected cases vs unaffected controls. Operates on a standalone **case-control study**, not a
per-proband Case (like `POP_FRQ`, one assessment per study).

**Exclusivity.** When `CLN_CCS` is applied — *regardless of the point value* — **all other CLN codes
are marked NA except `CLN_DNV`** (SM 4). That override is an aggregation-layer rule; this map records
the code and applies the exclusivity when the CLN category is combined.

**Robustness gate.** The study must have **≥ 5 case-variant observations**, **≥ 100 unrelated cases**,
and **matched controls**. If not, or if no odds ratio is given → `CLN_CCS_ND` (no code).

### The three levels

1. **Outcome** — the odds ratio + confidence interval (past the robustness gate) select one cell.
2. **No aggregation** — a single per-study assessment; no multiplier.
3. **Roll-up** — `CLN_CCS` = the cell; when applied, it silences the other CLN codes (except
   `CLN_DNV`).

### The cells

| Proposed code | condition | points |
|---|---|---|
| `CLN_CCS_SIG` | robust · **OR > 5.0** · CI **excludes** 1.0 | **+4.0** |
| `CLN_CCS_NS`  | robust · OR ≤ 5.0, **or** CI includes 1.0, **or** OR ≤ 1.0 | **0.0** |
| `CLN_CCS`     | roll-up | **0 or +4.0** |
| *(no code → `_ND`)* | not robust, or no odds ratio | — |

`OR > 5.0` is **strict**. A CI that includes 1.0 vetoes the award even when OR > 5 (SM 4's example:
`OR = 5.5, CI = 0.9–7.4` → `0.0`). `OR ≤ 1.0` indicates *benignity*, but **SM 4 assigns no benign
`CLN_CCS` value** — a documented gap, so it lands in `NS` (`0.0`) with a provenance flag.

### Evidence data items

| Attribute (real name) | Feeds | Threshold |
|---|---|---|
| `evidence.odds_ratio`                    | outcome    | `> 5.0` for `SIG` |
| `evidence.ci_lower`, `evidence.ci_upper` | CI veto    | must **exclude** 1.0 for `SIG` |
| `evidence.case_variant_count`            | robustness | `≥ 5` |
| `evidence.case_cohort_size`              | robustness | `≥ 100` |
| `evidence.controls_matched`              | robustness | `TRUE` |
| `evidence.ascertainment_bias_considered` | caution    | provenance note if not `TRUE` (not gated) |

### `CLN_CCS` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Manufactured (no practice `CLN_CCS` example).** Values follow SM 4's worked case-control
> guidance: a robust study with `OR = 8.0`, `CI = 3.2–19.0` (excludes 1.0), 12 case-variant
> observations across 400 matched cases → the `SIG` cell → **+4.0**. (SM 4's counter-example
> `OR = 5.5, CI = 0.9–7.4` would instead be `CLN_CCS_NS` = 0.0 — the CI includes 1.0.)

```text
EvidenceLine  CLN_CCS                     score +4.0   (single per-study assessment; 0 or +4.0)
└─ evidenceLines:
   └─ EvidenceLine  CLN_CCS_SIG           score +4.0 → evidenceItems: [1 case-control study]  (OR 8.0 · CI 3.2–19.0 · robust)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "CLN_CCS", "label": "Case-control (enrichment)" }, "score": 4.0,
  "note": "single per-study assessment; when applied, other CLN codes NA except CLN_DNV",
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "CLN_CCS_SIG", "label": "OR > 5.0 · CI excludes 1.0 · robust" }, "score": 4.0,
      "evidenceItems": [ { "id": "ccs-01", "type": "case_control_study", "references": ["PMID:38054408"],
        "description": "Manufactured — robust variant-specific case-control study per SM 4 guidance.",
        "data": { "odds_ratio": 8.0, "ci_lower": 3.2, "ci_upper": 19.0,
          "case_variant_count": 12, "case_cohort_size": 400, "controls_matched": true, "ascertainment_bias_considered": true } } ] }
  ]
}
```

The `SIG` leaf carries the full study for audit — the OR, its CI, the cohort sizes, and the
robustness flags — so a reviewer can re-check the gate (≥ 5 / ≥ 100 / matched) and the CI veto.

---

## `LOC` — Locus specificity (category roll-up)

**Where it sits:** HOD → **Locus specificity (LOC)**. `LOC` is a **grouping label** (⬦ not an
official code) collecting two **pathogenic** codes: **`LOC_PHE`** (phenotype specificity / diagnostic
yield) and **`LOC_SEG`** (co-segregation / linkage). `LOC = LOC_PHE + LOC_SEG`, **capped at +4.0**
(SM 5 L5/L38).

**Why the +4.0 cap matters.** `LOC` evidence implicates the **gene / locus**, not the specific
variant — it applies to *every* variant in the gene. The cap keeps locus evidence **below the LP
threshold (+6.0)** on its own, so some variant-specific evidence is always needed to move a variant
past VUS-high (SM 5 L5).

**Another ripple (principle 6): non-segregation zeroes both children.** A single observed
**non-segregation** (an affected relative *without* the VBC, or — at near-100% penetrance — an
unaffected relative *carrying* it) zeroes `LOC_PHE` and `LOC_SEG`, and for AD / AR-homozygous /
X-linked flips `LOC_SEG` to **−4.0**. So editing a relative's phenotype/genotype can collapse the
whole `LOC` subtotal — the dependency runs from `case.relatives` into both codes.

> **Basis — Manufactured composite.** `LOC_PHE` from the FBN1 example below, `LOC_SEG` from
> `v9-runx1` — *different* practice variants, shown together to illustrate the sum and the cap.

```text
EvidenceLine  LOC                         score +4.0   (capped; raw Σ = +7.0; cap 0…+4.0)
└─ evidenceLines:
   ├─ EvidenceLine  LOC_PHE               score +4.0 → see LOC_PHE example (FBN1 · Ghent · 91–93% yield)
   └─ EvidenceLine  LOC_SEG               score +3.0 → see LOC_SEG example (RUNX1 · 7 affected co-segregants)
```

Raw `LOC_PHE (+4.0) + LOC_SEG (+3.0) = +7.0` → capped to **+4.0**.

---

## `LOC_PHE` — Phenotype specificity (worked branch)

**Where it sits:** HOD → LOC → `LOC_PHE` · **pathogenic**, **0.0 to +4.0** (SM 5 Figure 1).
**Per-VBC / locus**, a **single** assessment — based on the **most-specific proband** (not a
per-proband multiplier). The score reflects the **diagnostic yield**: the % of individuals with a
precisely defined phenotype who are found to have a causative genotype.

### The three levels

1. **Band** — the diagnostic yield selects one of five bands (each a proposed code).
2. **No aggregation** — one assessment per locus (the single most-specific proband).
3. **Roll-up** — `LOC_PHE` = the band, unless a **non-segregation** zeroes it; feeds `LOC`.

### The bands

| Proposed code | diagnostic yield | Points |
|---|---|---|
| `LOC_PHE_NONE` | < 33%   | **0.0** |
| `LOC_PHE_LOW`  | 33–50%  | **+1.0** |
| `LOC_PHE_MOD`  | 51–67%  | **+2.0** ‡ |
| `LOC_PHE_HIGH` | 68–81%  | **+3.0** |
| `LOC_PHE_FULL` | ≥ 82%   | **+4.0** |
| `LOC_PHE`      | roll-up | **0.0 … +4.0** |

‡ the `+2.0` band and the `(81, 82)` sliver are inferred — SM 5 gives no explicit anchor (see
known-gaps). For ultra-rare disorders with no yield data, up to **+2.0** may instead come from
phenotype **semantic-similarity** scores (an alternate path to the same cap).

**Non-segregation zeroing.** If a band of `+1.0…+4.0` is awarded, an observed non-segregation
**zeroes it to 0.0** — a non-segregation excludes the locus (log-odds −∞ at Θ=0), far stronger than
any yield. Triggers: a relative **affected but VBC-absent** (MOI-independent), or an **unaffected
VBC-carrier at near-100% penetrance** (not for AR).

### Evidence data items

| Attribute (real name) | Feeds | Notes |
|---|---|---|
| `case.testing.diagnostic_yield_for_phenotypes` | band | e.g. `"91-93%"`, `"2.6%"`, `"<33%"` |
| `case.relatives[]` | non-segregation zeroing | affected + VBC-absent, or unaffected carrier |
| `case.age_matched_penetrance` | non-seg rule (b) | near-100% for the unaffected-carrier trigger |
| `moi` | non-seg rule (b) gate | AR suppresses the unaffected-carrier trigger |

### `LOC_PHE` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Grounded (SM 5 worked example, FBN1 · Marfan).** Two publications show a 91–93%
> diagnostic yield for FBN1 in individuals meeting Ghent criteria → the `FULL` band → **+4.0**.

```text
EvidenceLine  LOC_PHE                     score +4.0   (single assessment; zeroed by a non-segregation)
└─ evidenceLines:
   └─ EvidenceLine  LOC_PHE_FULL          score +4.0 → evidenceItems: [1 locus obs]  (FBN1 · Ghent · 91–93% ≥82%)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "LOC_PHE", "label": "Phenotype specificity (locus)" }, "score": 4.0,
  "note": "per-VBC/locus; single most-specific-proband assessment; zeroed by an observed non-segregation",
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "LOC_PHE_FULL", "label": "diagnostic yield ≥ 82%" }, "score": 4.0,
      "evidenceItems": [ { "id": "locphe-01", "type": "phenotype_specificity", "references": ["PMID:15241795", "PMID:21542060"],
        "description": "Grounded — FBN1 · Marfan; classic case meeting Ghent criteria; 91–93% diagnostic yield (SM 5).",
        "data": { "diagnostic_yield_for_phenotypes": "91-93%", "most_specific_proband": "classic Marfan syndrome, meets Ghent criteria" } } ] }
  ]
}
```

Were a relative later found **affected but VBC-negative**, this `+4.0` would **zero to 0.0** — the
same ripple as the CLN gate, sourced from `case.relatives`.

---

## `LOC_SEG` — Co-segregation (worked branch)

**Where it sits:** HOD → LOC → `LOC_SEG` · **pathogenic**, **0.0 to +4.0** (SM 5 Figure 2). Points
from **informative meiotic segregations** of the VBC through a family, **summed** across observations
and capped at +4.0.

> **Figure-2 gap.** The exact per-affected point tiers (`+1.0` to `+2.0`, by inheritance pattern) live
> in the SM 5 **Figure 2 image**, not the text — so the affected-segregant cell is modeled as a
> **range**, not a fixed per-observation value (see known-gaps).

### The cells

| Proposed code | observation | Points |
|---|---|---|
| `LOC_SEG_AFF`     | per **affected** co-segregant (VBC present) | **+1.0 … +2.0** † (by MOI; Fig-2 image-only) |
| `LOC_SEG_UAF`     | per **unaffected** co-segregant, near-100% penetrance, phase established | **+1.0** |
| `LOC_SEG_UAF_AR`  | per **unaffected** VBC-carrier, **AR** | **+0.4** |
| `LOC_SEG_NONSEG`  | a **non-segregation** is observed | **0.0 + flip −4.0** ‡ |
| `LOC_SEG`         | roll-up = Σ observations | **0.0 … +4.0** |

† summed across affected co-segregants (multiplier), then capped at +4.0.
‡ a non-segregation **zeroes** any co-segregation points **and** assigns **−4.0** (BS4-equivalent) for
**AD / AR-homozygous / X-linked** — but **not plain AR** (an AR non-segregation may just mean another
locus explains that family, not benignity of the VBC).

### Evidence data items

| Attribute (real name) | Feeds | Notes |
|---|---|---|
| `case.relatives[]` | affected / unaffected co-segregants + non-segregation | genotype + phenotype per relative |
| `moi` | affected tier + AR unaffected weight + non-seg flip scope | |
| `case.age_matched_penetrance` | unaffected counting | near-100% required |

### `LOC_SEG` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Grounded (practice `v9-runx1`).** RUNX1 · familial platelet disorder / AML · AD: **7
> affected relatives** segregating the VBC → `LOC_SEG_AFF` summed → **+3.0** (practice target). The
> per-affected value is Fig-2 image-only, so the leaf shows the practice total, not a per-item weight.

```text
EvidenceLine  LOC_SEG                     score +3.0   (Σ observations, capped 0…+4.0)
└─ evidenceLines:
   └─ EvidenceLine  LOC_SEG_AFF           score +3.0 → evidenceItems: [7 affected co-segregants]  (RUNX1 · FPD/AML · AD)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "LOC_SEG", "label": "Co-segregation (locus)" }, "score": 3.0,
  "note": "Σ informative meioses, capped +4.0; per-affected tier is Fig-2 image-only; zeroed + flipped -4.0 by a non-segregation (AD/AR-hom/XL)",
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "LOC_SEG_AFF", "label": "affected co-segregants (AD)" }, "score": 3.0,
      "evidenceItems": [ { "id": "locseg-01", "type": "segregation", "references": ["practice-variant-set:v9-runx1"],
        "description": "Grounded — 7 affected relatives segregating the VBC (FPD/AML). Represents 7 informative meioses; total +3.0.",
        "data": { "affected_relatives_segregating": 7, "moi": "AD", "phenotype": "FPD/AML" } } ] }
  ]
}
```

A single non-segregation here (an affected relative without the VBC) would zero this `+3.0` **and**
add `−4.0` (AD). The whole `LOC` subtotal turns benign from one relative's data.

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

See the [Summary Table](summary-table.md) for the code / combination / category caps that bound each
branch.
