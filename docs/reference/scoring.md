# Reference scoring (non-authoritative)

!!! warning "Non-authoritative"

    The `svcv4_model.scoring` layer is a **reference** implementation of the documented
    Supplementary-Material point rules — for tests, worked examples, and the
    practice-variant-set. **ClinGen CSpec is the authoritative scorer.** Any divergence from
    CSpec is a bug in *this* layer, never in CSpec. Every result is a `ScoreResult` with
    `authoritative = False` (constructing it `True` raises).

`reference_score_*` functions are pure: they take a captured assessment/evidence entity and
return a `ScoreResult` — the coded sub-code points, any held-combined intermediates, the
capped parent-code total, and a `provenance` trail. A step that is un-scoreable / No-Data is
**omitted** (never recorded as `0.0`). Expert-calibrated inputs (functional OddsPath) are
**consumed** from the analyst's coded value, not recomputed.

```python
from svcv4_model.scoring import reference_score_nonsense

result = reference_score_nonsense(assessment, gene_disease_validity=gdv)
result.parent_total      # e.g. 10.0
result.provenance        # the audit trail, step by step
```

## What is modeled so far

- **Shared primitives** — the SM 18 mechanism/exon multiplier, caps, held-combined, and the
  informative-variant tally (`svcv4_model.scoring.primitives`).
- **Nonsense** (SM 8) — `reference_score_nonsense`, all three branches.
- **Frameshift** (SM 9) — `reference_score_frameshift`, all five branches (shares the
  `score_nul_cds_workflow` pipeline with Nonsense).
- **Start-Lost** (SM 15) — `reference_score_start_lost`, three branches (yellow/orange floor
  the parent total at −4.0; violet is benignity-only).
- **Stop-Lost** (SM 16) — `reference_score_stop_lost`, two branches.
- **Exon Deletion** (SM 13) — `reference_score_exon_deletion`, six branches (the whole-gene
  branch applies SM 18 mechanism-only; the grey functional-alt-start branch is benignity-only).
- **Exon Duplication** (SM 14) — `reference_score_exon_duplication`, six scored branches + a
  whole-gene-NA outcome (the gain paths code functional data as NA; the shared helper skips
  FXN on those branches via `BranchSpec.fxn_na`). **All six NUL_/CDS_ scorers are now modeled.**
- **Canonical Splice** (SM 11) — `reference_score_canonical_splice`, five paths. The first
  `SPL_` scorer: it uses a separate `score_spl_workflow` helper whose pipeline adds an
  **SPL_SPA** (splice-assay) step and records **two** held values (`PRD+SPA`, `PRD+SPA+FXN`);
  the parent code is always `SPL`. SPA is consumed raw — `spa_points` is the analyst's coded
  delta (on the canonical paths the assay *reduces* the PRD). Per-path caps live in a
  `SplBranchSpec` (the yellow/orange second held value caps at +9, the violet path is
  benignity-only).
- **Intronic & Synonymous** (SM 12) — `reference_score_intronic_synonymous`, five paths (the
  same `score_spl_workflow`, a new `SplBranchSpec` table). Field-identical to Canonical Splice;
  the point values differ — PRD tops at +3, the orange paths carry an explicit held `PRD+SPA`
  cap (`−1..+6`, since SPA scales the PRD *up* here), and blue's second held caps at +9.
- **Missense — amino-acid path** (SM 6) — `reference_score_missense_amino_acid`, the first
  `MIS_` scorer. A standalone single-path pipeline: MIS_PRD is reduced by **transcript relevance
  only** (no molecular mechanism, **no GDV gate** — so this scorer takes no
  `gene_disease_validity`), and MIS_INF is a computed **4-category Grantham tally**
  (`missense_informative_points`). The `SPL_` splice path and the `MIS_`-vs-`SPL_` take-higher
  comparison are below.
- **Missense — splice path + comparison** (SM 6) — `reference_score_missense_splice` (a
  `score_spl_workflow` branch table) and `reference_score_missense`, the `MIS_`-vs-`SPL_`
  **take-higher** (negative/absent splice or a positive tie → the amino-acid path; else the
  higher), returning a `MissenseScoreResult` that saves both sub-path scores. **Note:** SM 6's
  splice blue/violet parent caps are inverted vs SM 11/12 (blue `−8..0`, violet `−8..+8`) —
  encoded faithfully and flagged as a suspected SM 6 inconsistency. This completes the splice
  family (Canonical, Intronic, Missense).
- **Population** (SM 3) — `reference_score_population`, the first **HOD** scorer (lives in
  `scoring/hod/`). Two benignity-only codes: **POP_FRQ** (FAF/DAFT fold bands `<1.5×`/`5×`/`15×`
  → `0/−1/−3/−6`, each band's lower edge inclusive — a flagged SM 3 boundary gap) and **POP_HMZ**
  (`−0.5`/observation from the 2nd, **`−1.0` for AD** per SM 3 Table 7; X-linked counts
  hemizygotes — needs the `moi`). `parent_code="POP"` is a grouping label (not an SVCv4 parent
  code); `parent_total` sums the two.
- **Clinical Observations** (SM 4) — `reference_score_cln_uaf` (Table 5) + `reference_score_cln_alt`
  (Table 4) benign codes, and the pathogenic **CLN_AFF**: `reference_score_cln_aff_mono` (Table 1,
  monoallelic — phenotype consistency × testing-thoroughness tier) + `reference_score_cln_aff_biallelic`
  (Table 2, biallelic — the 5-column 2nd-variant-status × co-occurrence-likelihood matrix). Per-`Case`
  (`parent_code="CLN"`); the cross-proband sum, the CLN_CCS exclusivity rule, the AD `+1.0`/proband
  ceiling-on-sum, table selection / X-linked routing, and semidominant summing are deferred to case
  aggregation. Shared `_classify` normalizes the placeholder variant `classification` (see
  known-gaps). **CLN_DNV** (`reference_score_cln_dnv`, Table 3) is the de-novo code — additive on
  CLN_AFF, by phenotype consistency × parental confirmation; biallelic disorders (`moi ∈ {AR, XLR}`)
  fold `SPECIFIC`→`CONSISTENT`, and the `+7.0` region caveat is un-applied (no VBC-region field,
  see known-gaps). **CLN_CCS** (`reference_score_cln_ccs`) is the case-control code — a standalone
  `CaseControlStudyEvidence` (like POP, not a `Case`): `OR>5.0` + a robust study (`≥5`
  case-variant obs, `≥100` cases, matched controls) → `+4.0`; a CI including 1.0 vetoes it; a
  failing gate → `_ND`; a low OR indicates benignity but SM 4 assigns no CLN_CCS benign value
  (see known-gaps); the exclusivity rule (other CLN NA except CLN_DNV) is deferred to aggregation.
  **This completes the CLN codes** (UAF, ALT, AFF, DNV, CCS).
- **Locus specificity — phenotype** (SM 5) — `reference_score_loc_phe`, the first **LOC** code.
  `parent_code="LOC"` is a grouping label; the single sub-code **LOC_PHE** bands
  `testing.diagnostic_yield_for_phenotypes` (`<33→0 / 33-50→+1 / 51-67→+2 / 68-81→+3 / ≥82→+4`; the
  `+2` band and the `(81,82)` boundary are inferred — see known-gaps). An observed
  **non-segregation** zeroes the points (the two-case rule: an affected VBC-absent relative, or —
  except under AR — an unaffected VBC-carrier at near-100% penetrance); under AR a rule-(a)
  non-segregation zeroes with a caveat. Absent/unparseable yield → `_ND`. **LOC_SEG**
  (co-segregation) and the combined **LOC** `+4.0` cap are deferred to LOC-2 / case aggregation
  (LOC_SEG's per-MOI segregant point values live only in the SM 5 Figure 2 image).

The shared `score_nul_cds_workflow` carries per-branch caps via a `BranchSpec` (parent
floor/ceiling, held ceiling, INF ceiling), so each LoF scorer is just its branch table; the
`SPL_` workflows use the parallel `score_spl_workflow` / `SplBranchSpec` pair.

## Classification band

`reference_classify(points)` maps a **summed** Bayesian point total to the SM 1 pathogenicity
descriptor plus the VUS subclass — the capstone the aggregation increments feed:

| Points | Category |
|---|---|
| `≤ −4.0` | Benign |
| `> −4.0` and `≤ −1.0` | Likely Benign |
| `> −1.0` and `< +2.0` | VUS-low |
| `≥ +2.0` and `< +4.0` | VUS-mid |
| `≥ +4.0` and `< +6.0` | VUS-high |
| `≥ +6.0` and `< +10.0` | Likely Pathogenic |
| `≥ +10.0` | Pathogenic |

It returns a `Classification` NamedTuple (`category` + `vus_subclass`, the latter set only for
VUS). The band is **not clamped** (SM 1 makes Pathogenic open-ended `≥ +10.0`); whether the summed
total is globally clamped is a separate open question deferred to the cross-code-combination
increment (see [known gaps](known-gaps.md)). The summing that produces `points` — POP/LOC
subtotals, CLN cross-proband aggregation, and cross-code combination — and `validate_case`
applicability enforcement follow in later increments (see the scoping doc).

## Family subtotals (aggregation)

`reference_aggregate_pop` and `reference_aggregate_loc` collapse a family's per-code
`ScoreResult`(s) into one subtotal `ScoreResult` (consuming and producing `ScoreResult`s keeps the
pipeline uniform). **POP** (`reference_aggregate_pop`) sums POP_FRQ + POP_HMZ with **no cap** (SM 3
— independent case-level codes); it is a pass-through today since the POP scorer already subtotals.
**LOC** (`reference_aggregate_loc`) is the positive LOC_PHE + LOC_SEG combine **capped at `+4.0`**
(SM 5); the uncapped sum is preserved in `held_combined` when the cap binds. The LOC cap is inert
until `LOC_SEG` lands (LOC_PHE alone is `0..+4`), and the `−4.0` non-segregation benign flip is a
separate LOC-2 signal, not summed here. A duplicate sub-code across inputs raises (these codes are
singletons per (VBC, MDE)); CLN cross-proband aggregation (same code, many probands) and the
cross-code combination into one final total follow in later increments.

## Per-proband CLN combine (aggregation)

`reference_score_cln_proband` is the per-proband CLN combiner (aggregation Inc 3a). It **routes**
the affected-counting table — mono (Table 1) vs biallelic (Table 2) — by MOI, then sex (X-linked:
XLR male→mono, female→biallelic) and zygosity (semidominant), then imposes the SM 4
affected-vs-unaffected split the per-code scorers do **not** perform themselves: an affected
proband (`pheno_specificity_for_mde ∈ {SPECIFIC, CONSISTENT}`) is scored under CLN_AFF (routed) +
CLN_ALT (unless AR — SM 4 L186) + CLN_DNV (only when de-novo is *inferred* — both parents present
as relatives and VBC-absent, with confirmed parentage — and CLN_AFF scored); otherwise the proband
takes the CLN_UAF (unaffected) path. This fixes two latent issues: CLN_UAF could previously
co-fire with CLN_AFF, and CLN_DNV's mono/biallelic fold now follows the routing decision (correct
for XLR-by-sex and semidominant). AFF + DNV are additive per proband (SM 4 L147; the AD `+1.0` is
already in Table 1 — no extra ceiling). The scored CLN_* sub-codes merge into one per-proband
`ScoreResult`. Cross-proband summation (3b) and CLN_CCS exclusivity + POP_FRQ gating (3c) follow.

`reference_aggregate_cln_cases` then **sums** each CLN sub-code across the per-proband results —
one *unrelated* index proband per family (SM 4 L27; related individuals are LOC segregation, not
CLN counts) — into one CLN subtotal, with **no cross-proband cap** (the SM 1 band is the only
ceiling). Unlike the POP/LOC family subtotals (which raise on a repeated code), summing a repeated
sub-code across probands is the intended axis here, so semidominant mono+biallelic summing falls
out. CLN_CCS exclusivity + POP_FRQ gating (Inc 3c) apply on top.

Finally, `reference_finalize_cln` applies the two CLN cross-code overrides to that subtotal:
**CLN_CCS exclusivity** (when a CLN_CCS sub-code is present, NA CLN_AFF/CLN_ALT/CLN_UAF and keep
CLN_CCS + CLN_DNV — SM 4 L25) and the **POP_FRQ gate** (award the pathogenic counting codes
CLN_AFF/CLN_DNV only when `pop_frq_points ∈ {0.0, −1.0}`, else NA them — SM 4 L27; the DNV branch
is a flagged faithful default behind the image-only SM 4 Figure 1). Both are removals, unioned and
applied once, yielding the CLN family's contribution to the cross-code combine. **The CLN family
is now complete through aggregation** (per-code → per-proband combine → cross-proband sum →
finalize).

## Cross-code combine

`reference_combine_case` is where all evidence families meet: it sums the one PFD parent-code total
(`NUL`/`CDS`/`SPL`/`MIS` — missense uses its take-higher `applied_total`) with the POP, CLN, and
LOC subtotals into one **(VBC, MDE) total**. An `_ND` family contributes `0`; the per-family
breakdown is kept in `sub_code_points`. The sum is **unclamped** — faithful to SM 1's open-ended
Pathogenic (`≥ +10`) / Benign (`≤ −4`); the GA4GH JSON `scale` cap of `[−8, +10]` is a display
concern (flagged in [known gaps](known-gaps.md)). `reference_classify` then bands that total — but
an all-`_ND` case (no evidence in any family) yields `parent_total=None` (not classifiable, and
distinct from a scored `0.0`), so guard first: `t = reference_combine_case([...]).parent_total`;
`reference_classify(t)` only when `t is not None`.

The remaining PFD workflow scoring and `validate_case` (Inc 5) follow in later increments (see the
scoping doc).

## Known assumption (flagged for WG confirmation)

The SM 18 matrix's **Suspected mechanism × Most exon-relevance** cell was deliberately not
compounded to 12.5% by the Working Group; the authoritative value is in SM 18 Figure 1 (not
in this repo's text extracts). The reference scorer assumes **0.25** (keep the Suspected
fraction, drop the further Most halving) and records the assumption in `provenance`. This
affects only that single matrix cell.
