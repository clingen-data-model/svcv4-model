# Reference scorer — CLN_AFF biallelic (SM 4 Table 2) — design

**Date:** 2026-08-23
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-cln-aff-biallelic` (off `main`)
**Scope:** CLN_AFF for **biallelic** disorders (SM 4 Table 2). Completes CLN_AFF (mono Table 1
already merged). CLN_DNV, CLN_CCS, table selection/routing, cross-proband aggregation are later.

## Goal

Add `reference_score_cln_aff_biallelic` (SM 4 Table 2): the pathogenic CLN_AFF points for one
affected biallelic proband. Per-`Case`; `parent_code="CLN"`, single sub-code `CLN_AFF`. Reuses the
shared `_classify`. Non-authoritative; CSpec authoritative.

## Table 2 (SM 4 L85-140) — 5 columns (2nd-variant status) × row-class

**Columns** (the 2nd-variant status): `conf_plp` (het VBC confirmed-in-trans with a P/LP variant),
`assumed_plp` (assumed-in-trans P/LP), `conf_vus` (confirmed-in-trans VUS), `hom` (homozygous
VBC), `none` (no 2nd variant / in cis / unknown phase).

**Row-classes** and per-column points (verified vs SM 4 L109-140):

| Row-class | `conf_plp` | `assumed_plp` | `conf_vus` | `hom` | `none` |
|---|---|---|---|---|---|
| `A1` — CONSISTENT + thorough + co-occurrence `<0.0001` | `+3.0` | `+1.5` | `+1.5` | `+1.0` | `0.0` |
| `A2` — CONSISTENT + thorough + co-occurrence `0.0001–0.01` | `+2.0` | `+1.0` | `+1.0` | `+1.0` | `0.0` |
| `B` — incomplete testing / non-genetic not excluded / a VUS additional | `+1.0` | `+0.75` | `+0.5` | `+0.5` | `0.0` |
| `zero` — P/LP diff-gene alt (→ CLN_ALT), or phenotype NOT CONSISTENT | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` |

## Column selection (`_biallelic_column`)

- `vbc_zygosity == HOM` → **`hom`**.
- `vbc_zygosity == HET`, `compound_het_variant` present:
  - classifies **P/LP**: `phase_confidence == HIGH` → **`conf_plp`**; else (MED/LOW/None) →
    **`assumed_plp`** (the entity asserts in-trans by construction, so unconfirmed = "assumed").
  - classifies **VUS**: `phase_confidence == HIGH` → **`conf_vus`**; else → **`none`**
    (SM 4 L75: "No evidence points … for a VBC assumed in trans with a VUS").
  - classifies B/LB/other/None → **`none`**.
- `vbc_zygosity == HET`, no `compound_het_variant` → **`none`** (no in-trans 2nd variant).
- `vbc_zygosity is None` → `_ND` (cannot pick a column).

## Row-class selection

- `pheno_specificity_for_mde is None` → `_ND`.
- `INCONSISTENT` → **`zero`** (SM 4 L134: NOT CONSISTENT → 0.0).
- any `additional_variant` classifies **P/LP** (a P/LP alt cause in a different gene) → **`zero`**
  (SM 4 L128 row C → CLN_ALT).
- **thorough** = `case.testing` present **and** `covers_all_genes_relevant_to_mde == TRUE` **and**
  `non_genetic_etiology_excluded == TRUE` **and** no **VUS** `additional_variant`:
  - column `hom` → **`A1`** (co-occurrence is N/A for a single homozygous variant; `A1.hom == A2.hom == +1.0`, so the choice is immaterial).
  - else (het columns / `none`) by `compound_het_variant.co_occurrence_likelihood`:
    `LT_0_0001` → **`A1`**; `BETWEEN_0_0001_0_01` → **`A2`**; `None`/`NOT_ASSESSED` → **`B`**
    (the biallelic rarity is unestablished → fall to the incomplete row).
- otherwise → **`B`**.

`pts = _TABLE2[row_class][column]`.

## Design decisions (flagged)

- **DD1 — SPECIFIC folds into CONSISTENT.** Table 2 has a single phenotype-consistency category
  (SM 4 L74). Both `SPECIFIC` and `CONSISTENT` use the CONSISTENT scoring rows; only `INCONSISTENT`
  → `zero`.
- **DD2 — confirmed vs assumed via `phase_confidence`.** `HIGH` → confirmed; `MED`/`LOW`/`None` →
  assumed (P/LP) or `none` (VUS). `None` defaults to *assumed* for P/LP because the
  `CompoundHetVariant` entity asserts the 2nd variant is in trans by construction.
- **DD3 — co-occurrence `None`/`NOT_ASSESSED` → row `B`** for het columns (rarity unestablished);
  `hom` is unaffected (row `A`). `co_occurrence_likelihood` is read from `compound_het_variant`.
- **DD4 — `_ND` vs `0.0`.** `_ND` only when `pheno_specificity_for_mde is None` or `vbc_zygosity
  is None`; every other outcome (incl. `zero`/`none` → `0.0`) is a recorded computed value.
- **DD5 — per-`Case`, table pre-selected.** The caller invokes the biallelic scorer on a
  biallelic proband; table selection / X-linked routing / semidominant summing are deferred. `moi`
  accepted for parity (Table 2 has no MOI axis).

## `reference_score_cln_aff_biallelic(case, *, moi)` — `scoring/hod/clinical.py`

Module constant `_TABLE2 = {"A1": {...}, "A2": {...}, "B": {...}, "zero": {...}}` (5 keys each) +
a module-private `_biallelic_column(case) -> str | None` (None → `_ND`). `parent_code="CLN"`,
`sub_code_points={"CLN_AFF": pts}` (or `{}` when `_ND`), `parent_total=pts`; provenance records
the column, row-class, and the DD notes.

## Tests (TDD) — `tests/test_cln_aff_biallelic_scoring.py`

- **A1 row** (CONSISTENT, thorough, co `LT_0_0001`): conf-P/LP → `+3.0`; assumed-P/LP → `+1.5`;
  conf-VUS → `+1.5`; HOM → `+1.0`; no-2nd → `0.0`.
- **A2 row** (co `BETWEEN_0_0001_0_01`): conf-P/LP → `+2.0`; HOM → `+1.0`.
- **B row**: incomplete testing (covers_all FALSE) → conf-P/LP `+1.0`, assumed-P/LP `+0.75`,
  conf-VUS `+0.5`, HOM `+0.5`; a VUS additional forces `B`; co-occurrence `None` (het) → `B`.
- **zero**: a P/LP diff-gene additional → `0.0`; INCONSISTENT → `0.0`.
- **column edges**: assumed-P/LP = P/LP + `phase_confidence` MED (and None); assumed-VUS
  (VUS + MED) → `none` → `0.0`; HET + no compound_het → `none`.
- **`_ND`**: `pheno None` → `_ND`; `vbc_zygosity None` → `_ND`.
- HOM + thorough + co `None` → `A1.hom` = `+1.0` (co N/A for HOM).

## Docs

`docs/reference/scoring.md`: extend the CLN line — CLN_AFF is now mono + biallelic;
CLN_DNV/CLN_CCS/LOC follow. Note the DD2/DD3 interpretations.

## Quality gates

`pytest`, `ruff`, drift gate (no schema), `mkdocs build --strict`, clean tree. All existing
scorers (incl. the CLN benign pair + CLN_AFF-mono) untouched.

## Out of scope

CLN_DNV (Table 3), CLN_CCS, table selection / X-linked routing / semidominant summing,
cross-proband aggregation + the AD ceiling-on-sum, typing `classification`. LOC; classification
band; validate_case.
