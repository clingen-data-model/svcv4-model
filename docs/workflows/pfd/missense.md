# Missense (`MIS_` / `SPL_`)

**Missense variants** are evaluated on **two** paths of the SVCv4 missense flow
diagram (Supplementary Material 6): an **amino-acid effect** path (the upper,
green path → the `MIS_` parent code) and a **splicing effect** path (the lower
yellow/orange/blue/violet paths → the `SPL_` parent code). The analyst follows
**both**, then applies the higher (more positive) of the two scores.

!!! note "Modeling underway — both paths landed"

    Both the **amino-acid (`MIS_`) path** (`MissenseAminoAcidAssessment`) and the
    **splice (`SPL_`) paths** (`MissenseSpliceAssessment`) are modeled (inputs
    captured, scoring documented not computed). The `MIS_`-vs-`SPL_` comparison
    ("take the higher") is a later increment.

## Amino-acid effect path (`MIS_`) ✅ modeled (inputs)

The amino-acid path runs the shared PFD pipeline for the `MIS_` parent code. Each
step below is **documented, not computed**.

### Predictive evidence (`MIS_PRD_`)

The analyst selects **one** calibrated in-silico predictor **in advance** from the
seven approved by ClinGen — AlphaMissense, BayesDel, ESM1b, MutPred2, REVEL,
VARITY_R, VEST4 — or an in-house-calibrated alternative (`MissensePredictor`, with
`OTHER_CALIBRATED` for the latter). Each can reach **+4.0** for pathogenicity;
three reach −4.0 and four reach −3.0 for benignity. Positive points are then
adjusted for **transcript relevance** (`ExonRelevance`): the exon is present in
**All** disease-relevant transcripts (full points), **Most** (half), or **Few**
(zero). Unlike other variant types, the **molecular-mechanism** axis is *not*
applied here — missense predictors already capture both loss- and gain-of-function
effects. The result is coded and capped `MIS_PRD_ −4.0 to +4.0`.

### Functional evidence (`MIS_FXN_`)

The generic [Functional Assays](index.md#functional-assays-modeled-inputs) module
(`FunctionalAssayEvidence`), coded `MIS_FXN_ −8.0 to +8.0`. The `MIS_PRD_` and
`MIS_FXN_` points are combined and **held** (no distinct code) capped `−8.0 to
+6.0`; per SM 6, the model records **both** the separate values and the combined
value (`prd_fxn_combined`).

### Informative variants (`MIS_INF_`)

The missense informative-variants module is **distinct** from the general
[Informative Variants](index.md#informative-variants-modeled-inputs) module: it has
**four** categories (`MissenseInfCategory`), any combination of which may be
**summed**, coded `MIS_INF_ −8.0 to +8.0`. All concern nucleotide changes in the
**same codon** as the VBC (the same nucleotide change as the VBC is excluded — that
is `CLN_AFF` evidence):

| Category | Description | Points |
|---|---|---|
| `SAME_AA_PATHOGENIC` | Distinct nucleotide, **same** predicted amino acid, P/LP | +4.0 first P; +2.0 each LP; +2.0 each additional |
| `DISTINCT_AA_PATHOGENIC` | Distinct amino acid, P/LP, Grantham(wt→inf) ≤ Grantham(wt→VBC) | +2.0 first P; +1.0 first LP; +1.0 each additional |
| `DISTINCT_AA_BENIGN` | Distinct amino acid, B/LB, Grantham(wt→inf) ≥ Grantham(wt→VBC) | −2.0 first B; −1.0 first LB; −1.0 each additional |
| `SAME_AA_BENIGN` | Distinct nucleotide, **same** predicted amino acid, B/LB | −4.0 first B; −2.0 each LB; −2.0 each additional |

Points are awarded for **distinct variants**, regardless of how many times each is
observed. The two Grantham distances (`grantham_wt_to_vbc`,
`grantham_wt_to_informative`) gate categories 2 and 3 only. The categories key on
P/LP/B/LB; a `VUS` informative variant is out-of-band for `MIS_INF_` scoring (the
reused `VariantClassification` enum permits it, but it maps to no category). The
**motif-variant** special case (category 2, +2.0 once) leans on
[Determining Critical Amino Acids (SM 7)](../../reference/spec-alignment.md) and is
deferred to that increment.

### Amino-acid total (`MIS_`)

The `MIS_INF_` points are combined with the prior steps and coded with the parent
code `MIS_ −8.0 to +9.0` (`mis_total`). This value is later compared with the
splice path's `SPL_` total (a future increment) to decide which applies.

## Splice effect path (`SPL_`) ✅ modeled (inputs)

The splice path evaluates the nucleotide change's effect on splicing. The in-silico
splice prediction (SpliceAI / Pangolin — `SplicePredictor`) selects **one** of five
paths (`SplicePredictionOutcome`), and all five run the same pipeline: **SPL_PRD**
(prediction) → **SPL_SPA** (splice assay) → **SPL_FXN** (functional, SM 20) →
**SPL_INF** (informative, SM 19) → the capped **SPL_** total. Modeled as one
`MissenseSpliceAssessment`; each step is **documented, not computed**.

| Path (`prediction_outcome`) | Splice prediction | SPL_PRD initial | SPL_ total |
|---|---|---|---|
| `NMD_PREDICTED` (yellow) | frameshift + NMD | `+3.0` | `−8.0 to +10.0` |
| `FRAMESHIFT_NO_NMD` (upper orange) | frameshift, no NMD | `−1.0 to +3.0` | `−8.0 to +10.0` |
| `SPLICE_NO_FRAMESHIFT` (lower orange) | splice, no frameshift/NMD | `−1.0 to +3.0` | `−8.0 to +10.0` |
| `UNCERTAIN` (blue) | uncertain | `0.0` | `−8.0 to 0.0` |
| `UNLIKELY` (violet) | unlikely | `−1.0` | `−8.0 to +8.0` |

### Splice prediction (`SPL_PRD_`)

Positive initial points (yellow/orange) are reduced by the
[Molecular Mechanism & Exon Relevance](index.md#molecular-mechanism-exon-relevance-modeled-inputs)
matrix (SM 18) — unlike the amino-acid path, the splice paths **do** apply it. The
orange paths derive their initial points from a critical-amino-acid table (the
fraction of protein altered; an alternative start codon that rescues a 5′ PTC gives
`−1.0`). The lower-orange path may also fold in a protein-deletion in-silico tool
(MutationTaster / Provean, not yet calibrated). Captured on `SplicePredictiveEvidence`.

### Splice assay (`SPL_SPA_`)

`SpliceAssayEvidence` captures RNA / minigene / RT-PCR evidence for the aberrant
splice product (`SpliceAssayResult`: near-complete / substantial / incomplete-or-none;
absent = `SPL_SPA_ND`). Its semantics differ by path: for yellow/orange it **scales**
SPL_PRD (near-complete → full/double, substantial → half, incomplete/none → zero);
for blue it is **additive** (`−2.0 to +2.0`); for violet it adds **benignity**
(`−2.0 to 0.0`). This is distinct from SPL_FXN, to avoid double-counting.

### Functional (`SPL_FXN_`) and informative (`SPL_INF_`)

`SPL_FXN` reuses the generic [Functional Assays](index.md#functional-assays-modeled-inputs)
module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0`. `SPL_INF` reuses the
generic [Informative Variants](index.md#informative-variants-modeled-inputs) module
(`InformativeVariantsEvidence`, SM 19): a P/LP/B/LB variant in the **same exon** with
the **same predicted splice impact** (+2.0 first P / +1.0 first LP / +1.0 each
additional; negatives for B/LB), coded `−8.0 to +8.0`; the violet path restricts it
to B/LB only. (`similarity_basis` is single-valued, so the compound same-exon-and-
same-impact eligibility is a documented rule rather than fully typed.)

### Held combined values and the `SPL_` total

Per SM 6, the model records **both** the separate coded values and the two held
combined values (`prd_spa_combined` = SPL_PRD + SPL_SPA; `prd_spa_fxn_combined` =
SPL_PRD + SPL_SPA + SPL_FXN), then the capped parent `SPL_` total (`spl_total`),
whose range depends on the path (table above). The `SPL_` total is later compared
with the amino-acid `MIS_` total (increment 2c) to decide which applies.
