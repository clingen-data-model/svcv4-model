# Reference scorer — CLN benign pair (CLN_UAF + CLN_ALT, SM 4) — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-cln-benign` (off `main`)
**Scope:** the first Clinical-Observations (CLN, SM 4) scorers — the two **benign** per-proband
codes. Establishes the CLN harness in `scoring/hod/`. CLN_AFF / CLN_DNV / CLN_CCS and cross-
proband aggregation are later increments.

## Goal

Add `reference_score_cln_uaf` (Table 5) and `reference_score_cln_alt` (Table 4). Both are
**per-`Case`** (one proband); the cross-proband sum, the CLN_CCS exclusivity rule, and the
CLN_AFF `+1.0`/proband ceiling live in the later case-aggregation increment. Non-authoritative;
CSpec authoritative.

CLN codes are **mutually exclusive per Case** (UAF = an *unaffected* carrier; ALT = an *affected*
individual whose phenotype is explained by a P/LP alternate). So these are **two separate
per-code functions**, each returning a `ScoreResult` for its single code — not one combined
scorer (unlike POP, whose two codes co-occur on one variant). Each: `parent_code="CLN"` (the HOD
grouping label), `sub_code_points = {<code>: pts}` (or `{}` when `_ND`), `parent_total = pts`
(or `None`).

## Design decisions (flagged)

**DD1 — the placeholder `classification` string.** `AdditionalVariant.classification` and
`CompoundHetVariant.classification` are `str | None` placeholders (not the `VariantClassification`
enum). Both CLN codes need P-vs-LP detection. A shared `_classify_plp(s)` normalizes
case-insensitively: `{"P","PATHOGENIC"} → "P"`, `{"LP","LIKELY_PATHOGENIC"} → "LP"`, else `None`.
**Model gap flagged** (these fields should become `VariantClassification`) → `known-gaps.md`.

**DD2 — `_ND` vs computed `0.0`.** Consistent with POP: a code is `_ND` (omitted) only when the
inputs to place it in its table are **absent**; a computed `0.0` (in-table but zero — e.g. low
penetrance, or `pheno_severity` = more-severe) **is** recorded (a real "no benignity" assessment).

**DD3 — per-`Case` unit.** The scorers trust the workflow context (the caller invokes `cln_uaf`
on an unaffected Case, `cln_alt` on an affected one) — there is no explicit affected flag; the
applicability matrix governs which code applies. `moi` is a required keyword (as for POP).

## `reference_score_cln_uaf(case, *, moi)` — Table 5 (SM 4 L208-239)

Four columns × three penetrance rows. Column by MOI + zygosity + in-trans classification:

| Column | Selected when | NEAR_100 | PCT_80_100 | LT_80 / None |
|---|---|---|---|---|
| Dominant / Semidominant | `moi ∈ {AD, SD}` | `−4.0` | `−2.0` | `0.0` |
| Recessive/X-linked, homozygous/hemizygous | `moi ∈ {AR, XLD, XLR}` and `vbc_zygosity ∈ {HOM, HEMI}` | `−4.0` | `−2.0` | `0.0` |
| Recessive/X-linked, VBC in *trans* with a **P** variant | recessive/XL, `vbc_zygosity=HET`, `compound_het_variant` classifies **P** | `−4.0` | `−2.0` | `0.0` |
| Recessive/X-linked, VBC in *trans* with an **LP** variant | recessive/XL, `HET`, `compound_het_variant` classifies **LP** | `−2.0` | `−1.0` | `0.0` |

Rules: `_ND` when `moi is None` (cannot pick a column) or recessive/XL with `vbc_zygosity is
None`. A recessive/XL `HET` VBC with **no** confirmed-trans P/LP (no `compound_het_variant`, or it
classifies neither P nor LP) → **`0.0`** (SM 4 L203: "If there is no P or LP variant confirmed in
trans, or if phasing … unknown, then no points"). `age_matched_penetrance` `None`/`LT_80` → `0.0`
(SM 4 L203: unknown/low penetrance → no points).

## `reference_score_cln_alt(case, *, moi)` — Table 4 (SM 4 L188-200)

**Gate:** requires ≥1 **P/LP** `additional_variant` (the alternate cause). No P/LP alternate →
`_ND`. Then by `pheno_severity`:

| `pheno_severity` | CLN_ALT |
|---|---|
| `MONO_GT_OR_BIALLELIC_EQ_EXPECTED` (more severe, or same severity expected for >1 allele) | `0.0` |
| `MONO_EQ_EXPECTED` (not more severe; only one allele contributing) | `−0.5` |
| `BIALLELIC_LT_EXPECTED` (not consistent with recessive entity, penetrance >80%) | `−1.0` — **only** if same-gene (ALTV) and penetrance >80%; else `0.0` |

Rules: `_ND` when `pheno_severity is None` (or no P/LP alternate). The `−1.0` row's preconditions:
**same-gene (ALTV)** = a P/LP alternate with `phase_in_ref_to_vbc` captured (its field doc:
"captured only if the additional variant shares the VBC gene"); **penetrance >80%** =
`age_matched_penetrance ∈ {PCT_80_100, NEAR_100}`. If `BIALLELIC_LT_EXPECTED` but a precondition
is unmet → `0.0` (the SM 4 row does not apply). `MONO_*` never depends on penetrance/gene.

## Shared helper — `scoring/hod/clinical.py`

Both functions live in `scoring/hod/clinical.py`. `_classify_plp(s: str | None) -> str | None`
(module-private) and `_X_LINKED_OR_RECESSIVE = frozenset({MOI.AR, MOI.XLD, MOI.XLR})`. Reuses
`ScoreResult`. Provenance records the selected column/row and the DD1/DD2 notes.

## Tests (TDD) — `tests/test_cln_benign_scoring.py`

**CLN_UAF:** AD near-100 → `−4.0`; AD 80-100 → `−2.0`; AD <80 → `0.0`; AR HOM near-100 → `−4.0`;
XLR HEMI near-100 → `−4.0`; AR HET trans-P near-100 → `−4.0`; AR HET trans-LP near-100 → `−2.0`
(the LP column); AR HET trans-LP 80-100 → `−1.0`; AR HET no-trans-P/LP → `0.0`; penetrance None →
`0.0`; `moi None` → `_ND`; AR HET `vbc_zygosity None` → `_ND`; `parent_code "CLN"`,
`parent_total` mirrors the code.

**CLN_ALT:** a P/LP alternate + `MONO_GT_OR_BIALLELIC_EQ_EXPECTED` → `0.0`; `MONO_EQ_EXPECTED` →
`−0.5`; `BIALLELIC_LT_EXPECTED` + same-gene (phase captured) + NEAR_100 → `−1.0`;
`BIALLELIC_LT_EXPECTED` + different-gene (no phase) → `0.0`; `BIALLELIC_LT_EXPECTED` + LT_80 →
`0.0`; no P/LP alternate (empty, or only a VUS) → `_ND`; `pheno_severity None` → `_ND`.
`_classify_plp` unit cases ("P"/"pathogenic"/"LP"/"likely_pathogenic"/"VUS"/None).

## Docs

- `docs/reference/scoring.md`: a CLN (benign) line — the two per-proband benign codes, the
  Table 4/5 mappings, the per-`Case` unit (aggregation later), and the DD1 classification-string
  normalization.
- `docs/reference/known-gaps.md`: a model-gap row — `AdditionalVariant.classification` /
  `CompoundHetVariant.classification` are placeholder `str`; should become `VariantClassification`
  so scorers need no string normalization.

## Quality gates

`pytest`, `ruff`, drift gate (no schema — scoring out of root `__all__`), `mkdocs build
--strict`, clean tree. All existing scorers untouched.

## Out of scope

CLN_AFF (Tables 1/2), CLN_DNV (Table 3), CLN_CCS (case-control + exclusivity), cross-proband
aggregation + the AD `+1.0`/proband ceiling, and typing the `classification` fields. LOC (SM 5);
the classification band; `validate_case`.
