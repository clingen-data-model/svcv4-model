# Scoring map — Clinical observations (CLN)

> Part of the **[Workflow scoring map](index.md)**; the shared [reading guide](index.md#how-to-read-this) and the GKS [evidence-line & item structure](index.md#evidence-line-item-structure-gks-va-spec) live on the index page.

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
shown in [Structuring case-count evidence](structuring-case-evidence.md)).

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

