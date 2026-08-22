# Reference scorer — Intronic & Synonymous (SM 12) — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-intronic-synonymous` (off `main`)
**Scope:** Increment B of the splice family — a new branch table on the Inc-A `SPL_` machinery.

## Goal

Add `reference_score_intronic_synonymous` (SM 12, five paths). `IntronicSynonymousAssessment`
is **field-identical** to `CanonicalSpliceAssessment` (same `SplicePredictionOutcome` enum, same
submodules, same `spa_points`/`fxn_points`/`informative`), so this increment reuses the existing
`score_spl_workflow` + `SplBranchSpec` **unchanged** — only a new `_BRANCH` table + a one-line
delegation + tests + a docs line. Non-authoritative; CSpec authoritative. SPA consumed raw.

## Branch table (verified vs SM 12 + `pfd/intronic-synonymous.md`)

| Path | PRD range | held prd_spa | held prd_spa_fxn | INF | parent |
|---|---|---|---|---|---|
| `NMD_PREDICTED` (yellow) | `0.0 .. +3.0` | (parent range) | `−8 .. +9` | `−8 .. +8` | `−8 .. +10` |
| `FRAMESHIFT_NO_NMD` (upper orange) | `−1.0 .. +3.0` | **`−1.0 .. +6.0`** | `−8 .. +9` | `−8 .. +8` | `−8 .. +10` |
| `SPLICE_NO_FRAMESHIFT` (lower orange) | `−1.0 .. +3.0` | **`−1.0 .. +6.0`** | `−8 .. +9` | `−8 .. +8` | `−8 .. +10` |
| `UNCERTAIN` (blue) | `0.0 .. 0.0` | (parent range) | `−8 .. +9` | `−8 .. +8` | `−8 .. +8` |
| `UNLIKELY` (lilac) | `−1.0 .. 0.0` | **`−3.0 .. 0.0`** | **`−8 .. 0.0`** | **`−8 .. 0.0`** | **`−8 .. 0.0`** |

### The three deltas from Canonical Splice (SM 11) — the fidelity points

1. **PRD tops out at +3, not +6** (yellow fixed +3; orange `−1..+3`). SM 12 awards a lower fixed
   yellow value than a nonsense/canonical variant, reflecting splice-prediction uncertainty
   (SM 12 / docs line 68).
2. **Orange has an explicit first held `prd_spa` cap `−1.0 .. +6.0`** (SM 12 line 51: SPA is
   `0.0..+3.0` and *doubles* the PRD; "(SPL_PRD_ and SPL_SPA_) … capped at −1.0 to +6.0"). On
   Canonical this held value defaulted to the parent range; here it is explicit.
3. **Blue's second held `prd_spa_fxn` caps at +9** (SM 12 line 110: "capped at −8.0 to +9.0"),
   i.e. the `prd_spa_fxn_hi` **default** — *unlike* Canonical Splice, where blue was carved down
   to +8. Blue's parent (`spl_total`) is still `−8..+8`, so the parent is blue's binding cap.

Everything else matches the Inc-A pattern: SM 18 reduces positive yellow/orange PRD (blue/lilac
skip it); SPA consumed raw as the coded delta (here it *scales up* rather than reduces — but the
scorer just sums, unchanged); lilac is benignity-only (INF B/LB only → `inf_hi=0`).

## `_BRANCH` — `scoring/pfd/intronic_synonymous.py`

```python
_BRANCH = {
    NMD_PREDICTED: SplBranchSpec(0.0, 3.0),
    FRAMESHIFT_NO_NMD: SplBranchSpec(-1.0, 3.0, prd_spa_lo=-1.0, prd_spa_hi=6.0),
    SPLICE_NO_FRAMESHIFT: SplBranchSpec(-1.0, 3.0, prd_spa_lo=-1.0, prd_spa_hi=6.0),
    UNCERTAIN: SplBranchSpec(0.0, 0.0, parent_hi=8.0),           # prd_spa_fxn_hi=9 (default)
    UNLIKELY: SplBranchSpec(-1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0,
                            prd_spa_fxn_hi=0.0, inf_hi=0.0, parent_hi=0.0),
}
```

`reference_score_intronic_synonymous(assessment, *, gene_disease_validity)` → one-line delegation
to `score_spl_workflow`. Exported from `svcv4_model.scoring` (sorted `__all__`:
`intronic_synonymous` sorts after `frameshift`, before `nonsense`).

## Tests (TDD) — `tests/test_intronic_synonymous_scoring.py`

- Yellow maximal: PRD +3 (Established×All), `spa_points=+3.0` (near-complete doubles) → held
  `PRD+SPA`=+6; `fxn_points=+8` → held `PRD+SPA+FXN`=cap(6+8, +9)=**+9**; one P INF (+2) →
  parent cap(9+2, +10)=**+10**; `parent_code "SPL"`.
- Orange held-prd_spa +6 cap: `FRAMESHIFT_NO_NMD`, PRD +3, `spa_points=+5.0` → held
  `PRD+SPA`=cap(3+5, [−1,+6])=**+6** (proves the orange −1..+6 first-held cap, distinct from
  canonical).
- Blue second-held +9 (the SM 12-vs-SM 11 difference): `UNCERTAIN`, PRD 0, `spa_points=+2`,
  `fxn_points=+8` → held `PRD+SPA+FXN`=cap(2+8, +9)=**+9** (canonical would clamp to +8); parent
  cap(9+INF, +8) with no INF → **+8**.
- Lilac benignity: `UNLIKELY`, PRD −1, `spa_points=-2` → held `PRD+SPA`=cap(−3, [−3,0])=−3; a P
  INF clamped to 0 by `inf_hi=0`; parent in `[−8, 0]`.
- Orange PRD floor: `SPLICE_NO_FRAMESHIFT`, `initial_points=-5` → PRD cap(−5, [−1,+3])=−1.
- SPA `_ND` records `SPL_SPA: _ND`; all-five-outcomes loop (`parent_code == "SPL"`); empty → all
  `_ND`, `parent_total` None.

## Docs

`docs/reference/scoring.md`: add an Intronic & Synonymous line under Canonical Splice (same
`score_spl_workflow`; note the +3 PRD ceiling, the explicit orange held prd_spa −1..+6, and the
blue +9 second-held).

## Quality gates

`pytest`, `ruff`, drift gate (no schema — scoring stays out of root `__all__`),
`mkdocs build --strict`, clean tree. `score_spl_workflow`/`SplBranchSpec` and the Canonical
scorer are untouched.

## Out of scope

Missense (Increment C — the MIS_ amino-acid path scorer + SPL_ path + MIS_-vs-SPL_ take-higher).
POP/LOC/CLN; aggregation; classification band; validate_case.
