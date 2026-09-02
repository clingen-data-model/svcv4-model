# Scoring map — Locus specificity (LOC)

> Part of the **[Workflow scoring map](index.md)**; the shared [reading guide](index.md#how-to-read-this) and the GKS [evidence-line & item structure](index.md#evidence-line-item-structure-gks-va-spec) live on the index page.

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

