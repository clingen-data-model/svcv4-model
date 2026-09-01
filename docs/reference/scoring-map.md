# Workflow scoring map

A complete reference of **every place a score is produced** across the SVCv4 workflows and
[Summary Table](summary-table.md) — one node per unique scoring point, whether or not it has an
explicit evidence code.

The hierarchy follows the Summary Table: **Evidence Category → Evidence Concept → Evidence Code**,
then *inside* each code's workflow down to **every unique case/combination that yields a distinct
score**, its **aggregation** across cases, and the **rolled-up** code total.

> **Status:** developing one branch at a time. **`CLN_AFF` is worked in full below** as the
> pattern; the remaining branches will be expanded the same way and assembled into one tree.

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
cell code appears at two levels.

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

For a **biallelic** MDE (e.g. ATM · ataxia-telangiectasia · **AR**), `CLN_AFF_MONO` is absent, so
`CLN_AFF = CLN_AFF_BIAL`. The biallelic cells fan across the **second-variant status** (columns:
`CTP`/`ATP`/`CTV`/`HOM`/`NON`) and **co-occurrence × thoroughness** (rows: `RARE`/`UNCM`/`INCP`,
plus the two override rows).

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

### `EvidenceLine` tree — every `BIAL` code (one proband each)

A demonstration case (not a realistic single classification) with one representative proband per
`BIAL` leaf; `Σ = +13.75` → `CLN_AFF (score: +13.75)`. `data` is abbreviated to discriminators.

```json
{
  "type": "EvidenceLine", "method": { "code": "CLN_AFF", "label": "Affected observations" }, "score": 13.75,
  "evidenceLines": [
    { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL", "label": "Biallelic (Table 2) subtotal" }, "score": 13.75,
      "evidenceLines": [
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_RARE_CTP", "label": "rare · confirmed-trans P/LP" }, "score": 3.0,
          "evidenceItems": [ { "id": "cln-01", "type": "clinical_observation", "references": ["PMID:15241795"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "P", "phase_confidence": "HIGH", "co_occurrence_likelihood": "LT_0_0001" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_RARE_ATP", "label": "rare · assumed-trans P/LP" }, "score": 1.5,
          "evidenceItems": [ { "id": "cln-02", "type": "clinical_observation", "references": ["PMID:21542060"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "LP", "phase_confidence": "LOW", "co_occurrence_likelihood": "LT_0_0001" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_RARE_CTV", "label": "rare · confirmed-trans VUS" }, "score": 1.5,
          "evidenceItems": [ { "id": "cln-03", "type": "clinical_observation", "references": ["PMID:30093976"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "VUS", "phase_confidence": "HIGH", "co_occurrence_likelihood": "LT_0_0001" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_UNCM_CTP", "label": "uncommon · confirmed-trans P/LP" }, "score": 2.0,
          "evidenceItems": [ { "id": "cln-04", "type": "clinical_observation", "references": ["PMID:26896183"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "P", "phase_confidence": "HIGH", "co_occurrence_likelihood": "BETWEEN_0_0001_0_01" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_UNCM_ATP", "label": "uncommon · assumed-trans P/LP" }, "score": 1.0,
          "evidenceItems": [ { "id": "cln-05", "type": "clinical_observation", "references": ["PMID:27884173"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "P", "phase_confidence": "MED", "co_occurrence_likelihood": "BETWEEN_0_0001_0_01" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_UNCM_CTV", "label": "uncommon · confirmed-trans VUS" }, "score": 1.0,
          "evidenceItems": [ { "id": "cln-06", "type": "clinical_observation", "references": ["PMID:28492532"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "VUS", "phase_confidence": "HIGH", "co_occurrence_likelihood": "BETWEEN_0_0001_0_01" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_INCP_CTP", "label": "incomplete · confirmed-trans P/LP" }, "score": 1.0,
          "evidenceItems": [ { "id": "cln-07", "type": "clinical_observation", "references": ["PMID:29625052"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "P", "phase_confidence": "HIGH", "co_occurrence_likelihood": "NOT_ASSESSED" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_INCP_ATP", "label": "incomplete · assumed-trans P/LP" }, "score": 0.75,
          "evidenceItems": [ { "id": "cln-08", "type": "clinical_observation", "references": ["PMID:30675029"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "P", "phase_confidence": "LOW", "co_occurrence_likelihood": "NOT_ASSESSED" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_INCP_CTV", "label": "incomplete · confirmed-trans VUS" }, "score": 0.5,
          "evidenceItems": [ { "id": "cln-09", "type": "clinical_observation", "references": ["PMID:31447099"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" },
              "compound_het_variant": { "classification": "VUS", "phase_confidence": "HIGH", "co_occurrence_likelihood": "NOT_ASSESSED" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_THOR_HOM", "label": "homozygous · thorough" }, "score": 1.0,
          "evidenceItems": [ { "id": "cln-10", "type": "clinical_observation", "references": ["PMID:32341571"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HOM",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_INCP_HOM", "label": "homozygous · incomplete" }, "score": 0.5,
          "evidenceItems": [ { "id": "cln-11", "type": "clinical_observation", "references": ["PMID:33083013"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HOM",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_NON", "label": "het · no valid in-trans 2nd variant" }, "score": 0.0,
          "evidenceItems": [ { "id": "cln-12", "type": "clinical_observation", "references": ["PMID:34426522"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET", "additional_variant_exists": "FALSE",
              "testing": { "covers_all_genes_relevant_to_mde": "TRUE", "non_genetic_etiology_excluded": "TRUE" } } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_ALT", "label": "P/LP alt (different gene) → CLN_ALT" }, "score": 0.0,
          "evidenceItems": [ { "id": "cln-13", "type": "clinical_observation", "references": ["PMID:35529060"],
            "data": { "pheno_specificity_for_mde": "CONSISTENT", "vbc_zygosity": "HET", "additional_variant_exists": "TRUE",
              "additional_variants": [ { "id": "alt-1", "classification": "P" } ] } } ] },
        { "type": "EvidenceLine", "method": { "code": "CLN_AFF_BIAL_UAF", "label": "inconsistent phenotype → CLN_UAF" }, "score": 0.0,
          "evidenceItems": [ { "id": "cln-14", "type": "clinical_observation", "references": ["PMID:36646002"],
            "data": { "pheno_specificity_for_mde": "INCONSISTENT", "vbc_zygosity": "HET" } } ] }
      ] }
  ]
}
```

The `NON`, `ALT`, and `UAF` leaves score `+0.0` but are kept as nodes — each carries its own
auditable cases and records *why* a proband contributed no points (no valid in-trans variant; an
alternate P/LP cause; or an inconsistent phenotype).

---

## Next: the rest of the tree

Once the `CLN_AFF` shape is agreed, the same three-level pattern (combo → aggregation → roll-up)
expands to every other branch:

- **CLN:** `CLN_DNV` (Table 3 × parental confirmation, additive on AFF), `CLN_ALTV`/`CLN_ALTG`
  (Table 4), `CLN_UAF` (Table 5), `CLN_CCS` (case-control), then the CLN cross-code overrides.
- **POP:** `POP_FRQ` (FAF/DAFT bands), `POP_HMZ` (per-occurrence), POP combination.
- **LOC:** `LOC_PHE` (yield bands), `LOC_SEG`, the `LOC` combined code.
- **PFD:** for each parent code (`NUL`/`CDS`/`SPL`/`MIS`) the `_PRD`/`_SPA`/`_FXN`/`_INF` codes,
  the held combinations, and the parent total.
- **Roll-up across categories** → the (VBC, MDE) total → classification band.

See the [Summary Table](summary-table.md) for the code/combination/category caps that bound each
branch.
