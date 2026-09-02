# Scoring map — Population (POP)

> Part of the **[Workflow scoring map](index.md)**; the shared [reading guide](index.md#how-to-read-this) and the GKS [evidence-line & item structure](index.md#evidence-line-item-structure-gks-va-spec) live on the index page.

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

