# Structuring case-count evidence — three approaches

> Part of the **[Workflow scoring map](index.md)**; the shared [reading guide](index.md#how-to-read-this) and the GKS [evidence-line & item structure](index.md#evidence-line-item-structure-gks-va-spec) live on the index page.

Several CLN codes **count cases**: each unique case signature is a **cell** with its own
`method.code`, and when **multiple cases share a cell** they **multiply** that cell's per-case
score (`n × per-case`). This *cells × case-count* shape is shared by every per-individual
counting code — **`CLN_AFF`** (affected probands), **`CLN_DNV`** (de-novo probands),
**`CLN_ALTV`/`CLN_ALTG`** (affected individuals with an alternate cause), and **`CLN_UAF`**
(unaffected individuals). *(By contrast `CLN_CCS` is a single per-study assessment — no case
multiplier; `POP`/`LOC` codes count occurrences or segregants, not cases-in-cells.)*

There are **three ways** to structure such cases in the `EvidenceLine` tree; they all produce
the same totals, differing only in where the per-case score and the per-cell subtotal live.
**Approach 1 is the default recommended structure, and every worked example and condensed tree
in the code pages uses it.** The illustration below uses `CLN_AFF` monoallelic cells (defined in
[Clinical → `CLN_AFF`](clinical.md#cln_aff-affected-observations-worked-branch)).

### Illustration — multiple cases per cell (`CLN_AFF` monoallelic, Approach 1)

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

**This document defaults to Approach 1** for every counting code — a case is auditable *data* under one cell leaf; the two alternatives are documented for teams that need each case as an independently scored, citable line.

*Rule of thumb:* **Approach 1** if a case is a data point (audit trail, not a scored claim);
**Approach 2** if every case must be an independently scored, citable `EvidenceLine` *and* you want
the per-cell subtotal as a node; **Approach 3** if every case is its own scored line but the per-cell
grouping doesn't need to be a first-class node.

> **PMIDs are illustrative placeholders** in all three.

