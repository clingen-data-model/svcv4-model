# Missense (`MIS_` / `SPL_`)

**Missense variants** are evaluated on **two** paths of the SVCv4 missense flow
diagram (Supplementary Material 6): an **amino-acid effect** path (the upper,
green path → the `MIS_` parent code) and a **splicing effect** path (the lower
yellow/orange/blue/violet paths → the `SPL_` parent code). The analyst follows
**both**, then applies the higher (more positive) of the two scores.

!!! note "Modeling underway — amino-acid path landed"

    This increment models the **amino-acid (`MIS_`) path** as
    `MissenseAminoAcidAssessment` (inputs captured, scoring documented not
    computed). The splice (`SPL_`) paths and the `MIS_`-vs-`SPL_` comparison are
    later increments.

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

## Splice effect path (`SPL_`)

Modeled in a later increment — the five color sub-paths (yellow/upper-orange/
lower-orange/blue/violet), the `SPL_SPA` splice-assay module, and the
`MIS_`-vs-`SPL_` comparison.
