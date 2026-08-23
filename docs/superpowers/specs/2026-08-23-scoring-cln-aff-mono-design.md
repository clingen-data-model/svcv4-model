# Reference scorer — CLN_AFF monoallelic (SM 4 Table 1) — design

**Date:** 2026-08-23
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-cln-aff-mono` (off `main`)
**Scope:** CLN_AFF for **monoallelic** disorders (SM 4 Table 1) — the pathogenic per-proband
clinical code. The biallelic path (Table 2), CLN_DNV, CLN_CCS, table selection/X-linked routing,
and cross-proband aggregation are later increments.

## Goal

Add `reference_score_cln_aff_mono` (SM 4 Table 1): the CLN_AFF benignity→**pathogenic** points
for one affected monoallelic proband. Per-`Case`; `parent_code="CLN"`, single sub-code `CLN_AFF`.
Generalizes the shared classifier (`_classify_plp` → `_classify`, adding VUS) so Table 1's tiers
can distinguish P/LP vs VUS additional variants. Non-authoritative; CSpec authoritative.

## Table 1 (SM 4 L37-71) — phenotype consistency × thoroughness tier

| Phenotype | best tier | middle tier | P/LP-alt tier |
|---|---|---|---|
| `SPECIFIC` | `+1.0` | `+0.5` | `+0.0` |
| `CONSISTENT` | `+0.5` | `+0.25` | `+0.0` |
| `INCONSISTENT` | `+0.0` (→ CLN_UAF) | — | — |

**Tier selection** (SM 4 L45-68), for SPECIFIC/CONSISTENT:

- **P/LP-alt** (`+0.0`, → CLN_ALT): any `additional_variant` classifies **P/LP** ("Additional
  variant of interest — LP/P variant in trans in same gene OR in a different gene that explains
  phenotype").
- **best**: `testing.covers_all_genes_relevant_to_mde == TRUE` **and**
  `testing.non_genetic_etiology_excluded == TRUE` **and** no additional variant of interest (no
  P/LP — already excluded — and no **VUS**). ("All relevant genes tested AND non-genetic etiology
  unlikely AND no additional variant of interest.")
- **middle**: otherwise ("Not all genes tested OR high unexplained OR non-genetic not excludable
  OR an additional plausible VUS").

The `+1.0` SPECIFIC/best cell is already the SM 4 AD `+1.0`/proband ceiling — inherent in
Table 1 (the cross-proband sum + the ceiling-on-sum are aggregation-layer concerns).

## Design decisions (flagged)

**DD1 — TriState thoroughness → tier.** "best" requires both `covers_all_genes_relevant_to_mde`
**and** `non_genetic_etiology_excluded` to be `TriState.TRUE`. `None`/`FALSE`/`UNKNOWN` on either
→ **not** best → middle (the conservative reading; SM 4's best tier requires the affirmative
"tested AND excluded"). **`case.testing` itself defaults to `None`** — guard it: `case.testing is
None` → treat both TriState inputs as unsatisfied → middle (never dereference a `None` testing).

**DD2 — `_ND` vs computed `0.0`.** `_ND` only when `pheno_specificity_for_mde is None` (cannot
place the proband). `INCONSISTENT` → a computed `+0.0` **is** recorded (a real "no CLN_AFF
weight" assessment; the SM 4 redirect to CLN_UAF is the applicability layer's concern).

**DD3 — generalize the classifier.** `_classify_plp(s) → "P"/"LP"/None` becomes
`_classify(s) → "P"/"LP"/"VUS"/"B"/"LB"/None` (case-insensitive; accepts the `VariantClassification`
enum values `PATHOGENIC/LIKELY_PATHOGENIC/VUS/BENIGN/LIKELY_BENIGN` + the `P/LP/VUS/B/LB`
shorthands). The two merged benign callers are updated **differently** (behaviour-preserving —
their tests guard it):
- `reference_score_cln_uaf` — **rename only** (`_classify_plp` → `_classify`). It feeds the result
  into `{"P":"rec_trans_p","LP":"rec_trans_lp"}.get(trans, "no_trans_plp")`, which needs the
  **string**; VUS/B/LB (and None) already fall through to `no_trans_plp` (correct per Table 5).
- `reference_score_cln_alt` — its P/LP **gate must change** from the truthy filter
  `if _classify(v.classification)` to `if _classify(v.classification) in {"P","LP"}`, because
  `_classify` now also returns truthy `VUS`/`B`/`LB`; the truthy filter would wrongly admit
  non-P/LP alternates. (This is the one real regression risk the generalization introduces.)

A B/LB additional variant is **not** "of interest" (does not block the best tier).

**DD4 — per-`Case`, table pre-selected.** The scorer trusts the caller to invoke the *mono*
scorer on a monoallelic proband (het/hemi VBC, monoallelic MDE). The table-selection logic
(mono vs biallelic; X-linked XLD/XLR × sex routing, SM 4 L77; semidominant summing, L80) is
deferred to the aggregation/dispatch layer. `moi` is accepted (signature parity) but not consumed
by Table 1.

## `reference_score_cln_aff_mono(case, *, moi)` — `scoring/hod/clinical.py`

```
pheno = case.pheno_specificity_for_mde
if pheno is None: -> _ND
if pheno == INCONSISTENT: pts = 0.0
else:  # SPECIFIC or CONSISTENT
    if any _classify(v.classification) in {"P","LP"} for v in additional_variants: tier = plp_alt
    elif covers_all_genes == TRUE and non_genetic_excluded == TRUE
         and not any _classify(v.classification) == "VUS": tier = best
    else: tier = middle
    pts = {SPECIFIC: {best:1.0, middle:0.5, plp_alt:0.0},
           CONSISTENT: {best:0.5, middle:0.25, plp_alt:0.0}}[pheno][tier]
```

`parent_code="CLN"`, `sub_code_points={"CLN_AFF": pts}` (or `{}` when `_ND`), `parent_total=pts`.
Provenance records the phenotype, tier, and the DD1/DD2 notes.

## Tests (TDD) — extend `tests/test_cln_aff_mono_scoring.py`

- SPECIFIC + best (all-genes TRUE, non-genetic TRUE, no alts) → `+1.0`; SPECIFIC + middle
  (covers_all_genes FALSE) → `+0.5`; SPECIFIC + a VUS alt → `+0.5` (middle, VUS blocks best);
  SPECIFIC + a P/LP alt → `+0.0`.
- CONSISTENT + best → `+0.5`; CONSISTENT + middle → `+0.25`; CONSISTENT + P/LP alt → `+0.0`.
- INCONSISTENT → `+0.0` (recorded, not `_ND`).
- best-tier TriState edges: `covers_all_genes=None` → middle; `non_genetic_excluded=UNKNOWN` →
  middle; a B/LB alt does **not** block best.
- `pheno_specificity_for_mde=None` → `_ND` (`sub_code_points == {}`, `parent_total is None`).
- `_classify` unit: "VUS"→VUS, "B"→B, "LB"→LB, plus the existing P/LP/None cases; the two benign
  scorers still pass unchanged.

## Docs

- `docs/reference/scoring.md`: extend the CLN line — add CLN_AFF (monoallelic, Table 1); note the
  biallelic Table 2 + CLN_DNV/CLN_CCS follow, and the classifier generalization.

## Quality gates

`pytest`, `ruff`, drift gate (no schema), `mkdocs build --strict`, clean tree. The two benign
CLN scorers keep passing (behaviour-preserving classifier refactor).

## Out of scope

CLN_AFF **biallelic** (Table 2 — 5-column 2nd-variant matrix + co-occurrence rows), CLN_DNV,
CLN_CCS, table selection / X-linked routing / semidominant summing, cross-proband aggregation +
the AD ceiling-on-sum, typing the `classification` fields. LOC; classification band; validate_case.
