# Reference scorer — CLN_DNV (SM 4 Table 3) — design

**Date:** 2026-08-23
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-cln-dnv` (off `main`)
**Scope:** the de-novo clinical code (SM 4 Table 3). CLN_CCS and cross-proband aggregation follow.

## Goal

Add `reference_score_cln_dnv` (SM 4 Table 3): the pathogenic de-novo points for one affected
proband, **additive on CLN_AFF** for the same proband. Per-`Case`; `parent_code="CLN"`, single
sub-code `CLN_DNV`. Reuses the phenotype-consistency category. Non-authoritative; CSpec
authoritative.

## Table 3 (SM 4)

Phenotype consistency (the **same** category the proband got in CLN_AFF Table 1/2) × parental
confirmation:

| Phenotype consistency | confirmed parental relationships | unconfirmed |
|---|---|---|
| `SPECIFIC` (mono-allelic only) | `+7.0` `**` | `+2.0` |
| `CONSISTENT` (mono or biallelic) | `+4.0` | `+1.0` |
| NOT consistent (`INCONSISTENT`) | `+0.0` | `+0.0` |

## Design decisions (flagged)

- **DD1 — biallelic folds `SPECIFIC` → `CONSISTENT`.** The `SPECIFIC` `+7.0/+2.0` row is
  **mono-allelic only** (SM 4). A biallelic proband uses the CONSISTENT row (Table 2's singular
  category). The scorer infers biallelic from the Case: `vbc_zygosity == HOM`, or
  `vbc_zygosity == HET and compound_het_variant is not None` (mirrors the AFF split). For a
  biallelic proband with `pheno_specificity_for_mde == SPECIFIC`, score the CONSISTENT row.
- **DD2 — confirmed vs unconfirmed via `confirmed_parental_relationship`.** `TriState.TRUE` →
  confirmed column; `FALSE`/`UNKNOWN`/`None` → unconfirmed (the conservative reading — only an
  affirmative identity/parentage confirmation earns the higher weight; SM 4: "confirmed" requires
  identity/genomic testing, "unconfirmed" is when it "was not performed").
- **DD3 — the `+7.0` `**` caveat is NOT applied.** SM 4 recommends decreasing the `+7.0` if the
  VBC falls outside coding/adjacent-intronic regions (where de novos are more frequent). The
  model has **no VBC-region annotation**, so the scorer awards the faithful `+7.0` and records the
  caveat in `provenance` (a documented non-applied reduction, like the SM 18 / SM 6 / SM 3 flags).
- **DD4 — `_ND` vs `0.0`.** `_ND` only when `pheno_specificity_for_mde is None` (cannot pick the
  row). `INCONSISTENT` → a recorded `+0.0`. (De-novo status itself is the workflow's precondition
  — the caller invokes CLN_DNV on a de-novo proband; there is no separate `de_novo` flag.)
- **DD5 — per-`Case`, additive on CLN_AFF.** CLN_DNV and CLN_AFF both apply to the same de-novo
  proband; the cross-proband sum is aggregation-layer. `moi` accepted for parity (Table 3 has no
  MOI axis).

## `reference_score_cln_dnv(case, *, moi)` — `scoring/hod/clinical.py`

```
pheno = case.pheno_specificity_for_mde
if pheno is None: -> _ND
biallelic = vbc_zygosity == HOM or (vbc_zygosity == HET and compound_het_variant is not None)
row = CONSISTENT if (biallelic and pheno == SPECIFIC) else pheno
confirmed = case.confirmed_parental_relationship == TriState.TRUE
pts = {
  SPECIFIC:    7.0 if confirmed else 2.0,
  CONSISTENT:  4.0 if confirmed else 1.0,
  INCONSISTENT: 0.0,
}[row]
```

`parent_code="CLN"`, `sub_code_points={"CLN_DNV": pts}` (or `{}` when `_ND`), `parent_total=pts`;
provenance records the row, confirmed flag, the biallelic-fold + the `+7.0` `**` caveat notes.

## Tests (TDD) — `tests/test_cln_dnv_scoring.py`

- SPECIFIC (mono, het no compound-het) + confirmed → `+7.0`; + unconfirmed (FALSE) → `+2.0`.
- CONSISTENT + confirmed → `+4.0`; + unconfirmed → `+1.0`.
- INCONSISTENT → `+0.0` (recorded).
- **biallelic fold**: HOM + SPECIFIC + confirmed → `+4.0` (SPECIFIC row is mono-only → CONSISTENT);
  HET + compound-het + SPECIFIC + confirmed → `+4.0`.
- DD2 edges: `confirmed_parental_relationship` `None`/`UNKNOWN` → unconfirmed column
  (SPECIFIC/None → `+2.0`).
- `_ND`: `pheno_specificity_for_mde is None` → `{}`, `parent_total None`.
- provenance carries the `+7.0` `**` caveat note on the SPECIFIC-confirmed mono case.

## Docs

`docs/reference/scoring.md`: extend the CLN line — add CLN_DNV (Table 3, additive on CLN_AFF); note
the biallelic SPECIFIC→CONSISTENT fold and the non-applied `+7.0` region caveat. CLN_CCS + LOC
follow. Optionally a `known-gaps.md` note for the un-annotated VBC-region (the `+7.0` caveat).

## Quality gates

`pytest`, `ruff`, drift gate (no schema), `mkdocs build --strict`, clean tree. All existing
scorers untouched.

## Out of scope

CLN_CCS (case-control + exclusivity), cross-proband aggregation + summing CLN_AFF+CLN_DNV per
proband, the `+7.0` region reduction (needs VBC-region annotation), post-zygotic-mosaic caveats.
LOC; classification band; validate_case.
