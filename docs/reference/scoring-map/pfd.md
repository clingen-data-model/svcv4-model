# Scoring map — Predictive & Functional Data (PFD)

> Part of the **[Workflow scoring map](index.md)**; the shared [reading guide](index.md#how-to-read-this)
> and the GKS [evidence-line & item structure](index.md#evidence-line-item-structure-gks-va-spec)
> live on the index page.

**PFD** is the *variant-level* evidence half of the classification — predictive (in-silico) and
functional data about the VBC itself, in contrast to the observational **[HOD](index.md#hod-human-observational-data-roll-up)**
side (POP / CLN / LOC). Each variant resolves to **one PFD parent code**, and its total combines with
the `HOD` total to make the (VBC, MDE) score.

## PFD — the pipeline (overview)

**Parent codes** (SM 1). A variant-type workflow resolves to exactly one:

| Parent | Meaning | Parent total range |
|---|---|---|
| **`NUL`** | Null / loss-of-function with NMD | −8.0 … +10.0 |
| **`CDS`** | Coding-sequence LoF that escapes NMD (rescue / no-NMD) | −8.0 … +10.0 |
| **`SPL`** | Splice effect | −8.0 … +10.0 |
| **`MIS`** | Missense (amino-acid effect) | −8.0 … +9.0 |
| `NCG` / `REG` | Non-coding / regulatory | *(not yet modeled)* |

**A pipeline, not cells × a multiplier.** Where the CLN counting codes multiply cases across cells,
a PFD parent code is built by a **fixed sequence of sub-code steps**, each **capped**, then combined:

```
PRD  →  (SPA, splice only)  →  FXN  →  [held]  →  INF  →  parent total
```

**Sub-codes.** Each is its own `EvidenceLine` (`method.code` = `<PARENT>_PRD` / `_SPA` / `_FXN` /
`_INF`):

| Sub-code | Source | Computed or analyst-coded? |
|---|---|---|
| **`_PRD`** | in-silico prediction, reduced by **SM 18** (mechanism × exon relevance × GDV gate) | **computed** |
| **`_SPA`** | splice assay (SPL path only) | analyst-coded (consumed raw) |
| **`_FXN`** | functional assay, calibrated to points (**SM 20** / Brnich OddsPath) | analyst-coded (consumed raw) |
| **`_INF`** | informative variants at the locus (**SM 19**) | **computed** tally |

**Held combined values — the one *codeless* scored node.** Between steps the running subtotal is
**held and capped** but has **no `method.code`** — SVCv4 is explicit (SM 8 L15): *"there is not a
distinct evidence code for the combination … it is just held until the next step … the VCI will
record the separate values."* So a scoring engine records **both** the separate sub-codes **and** the
held combined value. In the trees below a held node is drawn with `"held": true` and **no `method`** —
the deliberate exception to *"every scored node is an `EvidenceLine` with a code"* (index principle 1).
The LoF path holds `PRD+FXN`; the splice path holds `PRD+SPA` then `PRD+SPA+FXN`.

**Ripple (principle 6) is everywhere here.** Every step feeds the next through a cap, and the SM 18
reduction depends on `gene_disease_validity`, `gencc_mechanism`, and `exon_relevance`. Revise the
gene–disease validity and `_PRD` (and therefore the parent total, and the class) can move — the same
recompute-on-edit dependency as the CLN `POP_FRQ` gate.

**Missense is dual-path (take-higher).** A missense VBC is scored **twice** — an amino-acid path
(`MIS_`) and a splice path (`SPL_`) — and the **higher (more pathogenic)** applies (SM 6 L157). A
negative/absent splice total, or a positive tie, keeps the amino-acid path. This is another ripple:
editing splice inputs can flip *which parent code* the variant reports.

## Shared mechanics

### `SM 18` — the `_PRD` multiplier (mechanism × exon relevance)

Applied to **positive** initial points only (`≤ 0` passes through unchanged):

- **GDV gate:** if `gene_disease_validity` is below **Moderate** (or unknown), the mechanism is
  treated as *Uncertain* → **× 0** (a below-Moderate MDE earns no predictive points).
- Otherwise the fraction carried forward is **mechanism × exon**:

| `gencc_mechanism` | fraction | | `exon_relevance` | fraction |
|---|---|---|---|---|
| Established | 1.0 | | All relevant | 1.0 |
| Likely | 0.5 | | Most | 0.5 |
| Suspected | 0.25 | | Few | 0.0 |
| Uncertain / none | 0.0 | | *(none given)* | 1.0 (generous default) |

- **Special case:** `Suspected × Most` is set to **0.25** (a Figure-1-pending assumption), not the
  `0.125` product. Whole-gene deletions (SM 13) use **mechanism only** (no exon axis).

The missense amino-acid path is the exception: `MIS_PRD` uses **transcript relevance only** (the exon
fraction), **no** mechanism axis and **no** GDV gate — predictors already capture LoF + GoF.

### `SM 19` — the `_INF` informative tally

Distinct classified variants at the locus (same-consequence, same MDE): **+2** first P, **+1** first
LP, **+1** each additional P/LP; symmetric negatives for B/LB; VUS → 0; repeats of the same variant
don't re-count. `_ND` when nothing is classified. (Missense uses a richer **four-category** tally —
see the `MIS` section.)

### Caps at each step

| Step | LoF (`NUL`/`CDS`) | Splice (`SPL`) | Missense (`MIS`) |
|---|---|---|---|
| `_PRD` | branch `[0/−1, +6]` | branch | `[−4, +4]` |
| held `PRD+SPA` | — | branch `[−8, +10]` | — |
| held `PRD(+SPA)+FXN` | `[−8, +9/+10]` | `[−8, +9]` | `[−8, +6]` |
| `_INF` | `[−8, +8]` | `[−8, +8]` | `[−8, +8]` |
| **parent total** | `[−8, +10]` | `[−8, +10]` | `[−8, +9]` |

---

## `NUL` / `CDS` — Loss of function (worked branch)

**Where it sits:** PFD → `NUL` (NMD) / `CDS` (LoF escaping NMD). The **Nonsense** workflow (SM 8) is
the canonical LoF pipeline; Frameshift, Exon-Deletion/Duplication, Start-Lost and Stop-Lost share it.
The **NMD prediction routes the parent code**:

| Prediction outcome | Parent | `_PRD` initial | `_PRD` cap |
|---|---|---|---|
| NMD predicted, **no** rescue *(yellow)* | **`NUL`** | +6.0 | `[0, +6]` |
| NMD predicted, **rescue** by alt-Met *(orange)* | **`CDS`** | −1.0 … +6.0 | `[−1, +6]` |
| **No** NMD *(escapes; downstream loss)* | **`CDS`** | +6.0 | `[0, +6]` |

### The pipeline

1. **`_PRD`** — initial points (from the NMD prediction) **× SM 18**, capped to the branch range.
2. **`_FXN`** — a calibrated functional assay confirming loss of transcript/protein (SM 20), raw;
   `_ND` if none. *(NA on gain paths.)*
3. **held `PRD+FXN`** — `cap(PRD + FXN, [−8, +9/+10])`; **recorded, no code.**
4. **`_INF`** — informative NMD variants in the same exon (SM 19), capped `[−8, +8]`.
5. **parent** — `cap(held + INF, [−8, +10])`.

### Evidence data items

| Attribute (real name) | Feeds | Notes |
|---|---|---|
| `assessment.prediction_outcome` | parent + branch | NMD / rescue / no-NMD |
| `predictive.initial_points` | `_PRD` | +6.0 (NMD) etc. |
| `mechanism_exon_relevance.gencc_mechanism` | `_PRD` (SM 18) | Established/Likely/Suspected/Uncertain |
| `mechanism_exon_relevance.exon_relevance` | `_PRD` (SM 18) | All/Most/Few |
| `gene_disease_validity` | `_PRD` (SM 18 gate) | below Moderate → × 0 |
| `fxn_points` | `_FXN` | coded SM 20 value (raw) |
| `informative.variants[].classification` | `_INF` | P/LP/B/LB/VUS at the locus |

### `NUL` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Manufactured (pipeline breakdown).** Real `NUL` parent totals are grounded in the
> practice set — `v4-hnf4a` (`NUL_+4`, NMD predicted), `v29-rs1` (`NUL_+4`), `v20-ush2a` (`CDS_+2`),
> `v24-mecp2` (`CDS_+4`) — but the per-step `_PRD`/`_FXN`/`_INF` breakdown is not in that data, so
> the decomposition here is illustrative. Nonsense · NMD · no rescue → `NUL`.

```text
EvidenceLine  NUL                          score +7.0   (= cap(held[PRD+FXN] + INF, [-8,+10]))
└─ evidenceLines:
   ├─ (held) PRD+FXN                        score +5.0   (cap(PRD+FXN, [-8,+10]); recorded · NO method.code)
   │  ├─ EvidenceLine  NUL_PRD              score +3.0 → evidenceItems: [1]  (initial +6.0 × SM18 0.5 [Likely×All]; cap [0,+6])
   │  └─ EvidenceLine  NUL_FXN              score +2.0 → evidenceItems: [1]  (calibrated LoF assay · SM20 · raw)
   └─ EvidenceLine  NUL_INF                 score +2.0 → evidenceItems: [1]  (1 P informative NMD variant, same exon; cap [-8,+8])
```

```json
{
  "type": "EvidenceLine", "method": { "code": "NUL", "label": "Nonsense · NMD, no rescue (LoF)" }, "score": 7.0,
  "note": "parent = cap(held[PRD+FXN] + INF, [-8,+10]); held and sub-codes both recorded",
  "evidenceLines": [
    { "held": true, "label": "PRD + FXN (held — recorded, no method.code)", "score": 5.0,
      "note": "cap(PRD + FXN, [-8,+10]); SM 8 L15 — no distinct code, VCI records the separate values",
      "evidenceLines": [
        { "type": "EvidenceLine", "method": { "code": "NUL_PRD", "label": "in-silico · NMD prediction × SM 18" }, "score": 3.0,
          "evidenceItems": [ { "id": "nul-prd-01", "type": "computational_prediction", "references": ["practice-variant-set:v4-hnf4a"],
            "description": "Manufactured — NMD predicted (+6.0 initial) reduced by SM 18 (Likely × All = 0.5).",
            "data": { "prediction_outcome": "NMD_NO_RESCUE", "initial_points": 6.0,
              "gencc_mechanism": "LIKELY", "exon_relevance": "ALL", "gene_disease_validity": "STRONG", "sm18_fraction": 0.5 } } ] },
        { "type": "EvidenceLine", "method": { "code": "NUL_FXN", "label": "functional assay (SM 20)" }, "score": 2.0,
          "evidenceItems": [ { "id": "nul-fxn-01", "type": "functional_assay", "references": [],
            "description": "Manufactured — calibrated assay confirming loss of transcript/protein.",
            "data": { "fxn_points": 2.0, "assay": "RNA/protein loss; OddsPath-calibrated" } } ] }
      ] },
    { "type": "EvidenceLine", "method": { "code": "NUL_INF", "label": "informative variants (SM 19)" }, "score": 2.0,
      "evidenceItems": [ { "id": "nul-inf-01", "type": "informative_variant", "references": [],
        "description": "Manufactured — one Pathogenic NMD variant in the same exon, classified for the same MDE.",
        "data": { "variants": [ { "classification": "P", "same_exon": true, "nmd_predicted": true } ] } } ] }
  ]
}
```

`NUL_PRD` = `cap(6.0 × 0.5, [0,+6]) = +3.0`; held `PRD+FXN` = `cap(3.0 + 2.0, [−8,+10]) = +5.0`;
`NUL_INF` = `+2.0` (first P); parent `NUL` = `cap(5.0 + 2.0, [−8,+10]) = +7.0`. The **held node
carries a score but no `method.code`** — record it *and* the separate `_PRD` / `_FXN`. The `CDS`
branches (rescue / no-NMD) run the identical pipeline with a `−1.0`-floored `_PRD` and a `+9.0` held
cap.

---

## `SPL` — Splice (worked branch)

**Where it sits:** PFD → `SPL`. **Canonical-Splice** (SM 11) and **Intronic / Synonymous** (SM 12)
share this pipeline (the missense splice path reuses it too). Unlike LoF, it inserts a **splice-assay
(`_SPA`)** step, so it holds **two** intermediate values.

### The pipeline

`PRD → SPA → [held PRD+SPA] → FXN → [held PRD+SPA+FXN] → INF → parent`

1. **`SPL_PRD`** — initial points (from the splice prediction) **× SM 18**, capped to the branch.
2. **`SPL_SPA`** — RNA splice-assay result, coded to points (raw); `_ND` if none. *(On canonical
   splice the assay usually **reduces** the PRD; on the missense splice path it scales it up.)*
3. **held `PRD+SPA`** — `cap(PRD + SPA, branch)`; recorded, no code.
4. **`SPL_FXN`** — protein/functional assay (SM 20), raw.
5. **held `PRD+SPA+FXN`** — `cap(…, [−8, +9])`; recorded, no code.
6. **`SPL_INF`** — informative splice variants (SM 19), capped `[−8, +8]`.
7. **parent** — `cap(held + INF, [−8, +10])`.

### The branches (Canonical splice, SM 11)

The splice **prediction outcome** sets the caps:

| Prediction outcome | `_PRD` cap | notes |
|---|---|---|
| NMD predicted | `[0, +6]` | strongest LoF splice |
| Frameshift, no NMD | `[−1, +6]` | |
| Splice change, no frameshift (in-frame) | `[−1, +6]` | |
| Uncertain | `[0, 0]` | PRD 0; parent capped `+8` |
| Unlikely *(violet)* | `[−1, 0]` | **benignity-only** — every cap `≤ 0` |

*(Intronic/Synonymous, SM 12, runs the same pipeline with its own path set. The missense splice path,
SM 6, inverts the blue/violet parent caps — a suspected SM 6 inconsistency, reproduced and flagged.)*

### Evidence data items

| Attribute (real name) | Feeds |
|---|---|
| `assessment.prediction_outcome` | branch caps |
| `predictive.initial_points` | `_PRD` |
| `mechanism_exon_relevance.*` + `gene_disease_validity` | `_PRD` (SM 18) |
| `spa_points` | `_SPA` (raw) |
| `fxn_points` | `_FXN` (raw) |
| `informative.variants[].classification` | `_INF` |

### `SPL` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Manufactured (breakdown).** Real `SPL` totals are grounded — `v12-ada` (`SPL_+6`,
> in-frame exon skip of a critical region), `v17-ldlr` (`SPL_+5`), `v6-nf1` (`SPL_+4`), `v28-pten`
> (`SPL_−3`) — but the per-step decomposition is illustrative. In-frame exon skip, no frameshift.

```text
EvidenceLine  SPL                          score +7.0   (= cap(held[PRD+SPA+FXN] + INF, [-8,+10]))
└─ evidenceLines:
   ├─ (held) PRD+SPA+FXN                    score +6.0   (cap(held[PRD+SPA] + FXN, [-8,+9]); recorded · no code)
   │  ├─ (held) PRD+SPA                     score +5.0   (cap(PRD + SPA, [-8,+10]); recorded · no code)
   │  │  ├─ EvidenceLine  SPL_PRD           score +3.0 → evidenceItems:[1]  (initial +6.0 × SM18 0.5 [Likely×All]; cap [-1,+6])
   │  │  └─ EvidenceLine  SPL_SPA           score +2.0 → evidenceItems:[1]  (RNA splice assay confirms; raw)
   │  └─ EvidenceLine  SPL_FXN              score +1.0 → evidenceItems:[1]  (protein assay · SM20 · raw)
   └─ EvidenceLine  SPL_INF                 score +1.0 → evidenceItems:[1]  (1 LP informative splice variant; cap [-8,+8])
```

```json
{
  "type": "EvidenceLine", "method": { "code": "SPL", "label": "Splice · in-frame exon skip" }, "score": 7.0,
  "note": "two held values; parent = cap(held[PRD+SPA+FXN] + INF, [-8,+10])",
  "evidenceLines": [
    { "held": true, "label": "PRD + SPA + FXN (held — recorded, no method.code)", "score": 6.0,
      "note": "cap(held[PRD+SPA] + FXN, [-8,+9])",
      "evidenceLines": [
        { "held": true, "label": "PRD + SPA (held — recorded, no method.code)", "score": 5.0,
          "note": "cap(PRD + SPA, [-8,+10])",
          "evidenceLines": [
            { "type": "EvidenceLine", "method": { "code": "SPL_PRD", "label": "splice prediction × SM 18" }, "score": 3.0,
              "evidenceItems": [ { "id": "spl-prd-01", "type": "computational_prediction", "references": ["practice-variant-set:v12-ada"],
                "description": "Manufactured — in-frame exon skip (+6.0 initial) × SM 18 (Likely × All = 0.5).",
                "data": { "prediction_outcome": "SPLICE_NO_FRAMESHIFT", "initial_points": 6.0,
                  "gencc_mechanism": "LIKELY", "exon_relevance": "ALL", "gene_disease_validity": "STRONG", "sm18_fraction": 0.5 } } ] },
            { "type": "EvidenceLine", "method": { "code": "SPL_SPA", "label": "RNA splice assay" }, "score": 2.0,
              "evidenceItems": [ { "id": "spl-spa-01", "type": "splice_assay", "references": [],
                "description": "Manufactured — minigene/RNA assay confirms aberrant splicing.",
                "data": { "spa_points": 2.0, "assay": "minigene / RNA-seq" } } ] }
          ] },
        { "type": "EvidenceLine", "method": { "code": "SPL_FXN", "label": "functional assay (SM 20)" }, "score": 1.0,
          "evidenceItems": [ { "id": "spl-fxn-01", "type": "functional_assay", "references": [],
            "description": "Manufactured — protein-level assay.", "data": { "fxn_points": 1.0 } } ] }
      ] },
    { "type": "EvidenceLine", "method": { "code": "SPL_INF", "label": "informative variants (SM 19)" }, "score": 1.0,
      "evidenceItems": [ { "id": "spl-inf-01", "type": "informative_variant", "references": [],
        "description": "Manufactured — one LP splice variant at the locus.",
        "data": { "variants": [ { "classification": "LP", "same_splice_consequence": true } ] } } ] }
  ]
}
```

held `PRD+SPA` = `cap(3.0 + 2.0, [−8,+10]) = +5.0`; held `PRD+SPA+FXN` = `cap(5.0 + 1.0, [−8,+9]) =
+6.0`; parent `SPL` = `cap(6.0 + 1.0, [−8,+10]) = +7.0`. **Both** held values are recorded, neither has
a `method.code`.

---

## `MIS` — Missense (worked branch · dual-path take-higher)

**Where it sits:** PFD → `MIS` (SM 6). A missense VBC is scored on **two paths** and the **higher
applies**: an **amino-acid** path (`MIS_`) and a **splice** path (`SPL_`, the pipeline above). SM 6
L157: a negative/absent splice total → amino-acid; a positive splice total → the higher; a **positive
tie → amino-acid** (the amino-acid effect has the higher prior). Editing splice inputs can therefore
flip *which parent code the variant reports* — another ripple (principle 6).

### The amino-acid pipeline (`MIS_`)

`MIS_PRD → [held PRD+FXN] → MIS_INF → mis_total`

- **`MIS_PRD`** — one **pre-selected calibrated predictor** (AlphaMissense / BayesDel / ESM1b /
  MutPred2 / REVEL / VARITY_R / VEST4), initial **+4** (pathogenic) down to **−3…−4** (benign),
  **× transcript relevance** (exon fraction only — **no** mechanism axis and **no** GDV gate, since
  predictors already capture LoF + GoF). Cap **[−4, +4]**.
- **`MIS_FXN`** — functional assay (SM 20), raw. held `PRD+FXN` cap **[−8, +6]**.
- **`MIS_INF`** — the **four-category** tally (below), cap **[−8, +8]**.
- **mis_total** — `cap(held + INF, [−8, +9])`.

### `MIS_INF` — four categories (SM 6)

| Category | meaning | tally |
|---|---|---|
| `SAME_AA_PATHOGENIC` | different variant, **same** amino-acid change, P/LP | **doubled**: +4 first P / +2 first LP, +2 each more |
| `DISTINCT_AA_PATHOGENIC` | **different** AA change at the residue, P/LP | standard: +2 / +1 / +1 |
| `DISTINCT_AA_BENIGN` | different AA change, B/LB | standard *(negative)* |
| `SAME_AA_BENIGN` | same AA change, B/LB | **doubled** *(negative)* |

A VUS or off-polarity class scores 0. (The SM 7 motif-variant special case is deferred.)

### Take-higher

| splice total `SPL_` | result |
|---|---|
| negative or absent | amino-acid `MIS_` applies |
| positive, `> MIS_` | splice `SPL_` applies (parent code becomes `SPL`) |
| positive, `≤ MIS_` (incl. tie) | amino-acid `MIS_` applies |

### `MIS` as a GKS `EvidenceLine` tree (Approach 1)

> **Basis — Manufactured (breakdown).** Real `MIS` totals are grounded — `v22-f8` (`MIS_+5`),
> `v10-scn2a` / `v7-pah` (`MIS_+4`), `v19-tp53` (`MIS_+1`), `v3-foxg1` (`MIS_−1`), `v13-aipl1`
> (`MIS_−2`) — but the per-step decomposition is illustrative. Here the amino-acid path wins.

```text
take-higher:  MIS_ +7.0   vs   SPL_ +2.0   →   MIS_   (applied parent = MIS, score +7.0)
EvidenceLine  MIS                          score +7.0   (amino-acid path — SELECTED)
└─ evidenceLines:
   ├─ (held) PRD+FXN                        score +5.0   (cap(PRD + FXN, [-8,+6]); recorded · no code)
   │  ├─ EvidenceLine  MIS_PRD              score +4.0 → evidenceItems:[1]  (REVEL 0.92 → +4.0 × transcript All; cap [-4,+4])
   │  └─ EvidenceLine  MIS_FXN              score +1.0 → evidenceItems:[1]  (functional assay · SM20 · raw)
   └─ EvidenceLine  MIS_INF                 score +2.0 → evidenceItems:[1]  (1 distinct-AA P; four-category tally; cap [-8,+8])
   ·  (SPL_ path scored separately = +2.0 — not selected; shown for the comparison)
```

```json
{
  "type": "EvidenceLine", "method": { "code": "MIS", "label": "Missense · amino-acid (selected by take-higher)" }, "score": 7.0,
  "note": "take-higher: MIS_ +7.0 vs SPL_ +2.0 -> MIS_ applies; mis_total = cap(held[PRD+FXN] + INF, [-8,+9])",
  "evidenceLines": [
    { "held": true, "label": "PRD + FXN (held — recorded, no method.code)", "score": 5.0,
      "note": "cap(PRD + FXN, [-8,+6])",
      "evidenceLines": [
        { "type": "EvidenceLine", "method": { "code": "MIS_PRD", "label": "in-silico (calibrated) × transcript relevance" }, "score": 4.0,
          "evidenceItems": [ { "id": "mis-prd-01", "type": "computational_prediction", "references": ["practice-variant-set:v10-scn2a"],
            "description": "Manufactured — REVEL 0.92 -> +4.0, transcript relevance All (x1.0); no mechanism/GDV axis.",
            "data": { "predictor": "REVEL", "raw_score": 0.92, "initial_points": 4.0, "transcript_relevance": "ALL" } } ] },
        { "type": "EvidenceLine", "method": { "code": "MIS_FXN", "label": "functional assay (SM 20)" }, "score": 1.0,
          "evidenceItems": [ { "id": "mis-fxn-01", "type": "functional_assay", "references": [],
            "description": "Manufactured — calibrated missense functional assay.", "data": { "fxn_points": 1.0 } } ] }
      ] },
    { "type": "EvidenceLine", "method": { "code": "MIS_INF", "label": "informative variants · four-category (SM 6)" }, "score": 2.0,
      "evidenceItems": [ { "id": "mis-inf-01", "type": "informative_variant", "references": [],
        "description": "Manufactured — one Pathogenic variant, distinct amino-acid change at the residue (category 2).",
        "data": { "variants": [ { "category": "DISTINCT_AA_PATHOGENIC", "classification": "P" } ] } } ] }
  ]
}
```

`MIS_PRD` = `cap(4.0 × 1.0, [−4,+4]) = +4.0`; held `PRD+FXN` = `cap(4.0 + 1.0, [−8,+6]) = +5.0`;
`MIS_INF` = `+2.0` (category 2, first P); mis_total = `cap(5.0 + 2.0, [−8,+9]) = +7.0`. The splice
path scores `SPL_ +2.0` on its own pipeline, so the take-higher keeps **`MIS_` (+7.0)**. Had the
splice path exceeded `+7.0`, the variant would report parent code **`SPL`** instead.

---

## Next: the (VBC, MDE) total → classification

Every PFD parent code and the `HOD` total now feed the top of the tree:

- **(VBC, MDE) total** = `HOD` + the applied `PFD` parent total (the take-higher result for missense).
- **Classification band** (SM 1): `≥ +10` P · `+6 … <+10` LP · VUS bands · `≤ −7` / `≤ −1` benign
  tiers — the final `EvidenceLine` roll-up.

This is the last roll-up; with it the scoring map spans every scored node from the leaf cases to the
classification band.
