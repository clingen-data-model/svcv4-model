# Reference scorer — Canonical Splice (SM 11) + the SPL_ pipeline helper — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Parent scoping doc:** `2026-08-21-scoring-computation-scoping.md`
**Branch:** `feat/scoring-canonical-splice` (off `main`)
**Scope:** the first splice-family scorer, and the new `score_spl_workflow` helper it establishes.

## Goal

Add `reference_score_canonical_splice` (SM 11, five paths) and the shared `score_spl_workflow`
helper for the SPL_ pipeline, which differs from the NUL_/CDS_ one by an extra **SPL_SPA**
(splice-assay) step and a **second held value**. This is Increment A of the 3-increment splice
family (Canonical → Intronic → Missense). Non-authoritative; CSpec authoritative.

## The SPL_ pipeline

```
SPL_PRD  ->  SPL_SPA  ->  held prd_spa  ->  SPL_FXN  ->  held prd_spa_fxn  ->  SPL_INF  ->  spl_total
```

- **SPL_PRD** — computed: `predictive.initial_points` × the SM 18 matrix (positive-only; full
  mode), capped to the per-path PRD range. (SM 11: yellow/orange reduce positive PRD by SM 18;
  blue/violet skip it, but their PRD is 0/−1 so the positive-only multiplier no-ops anyway.)
- **SPL_SPA — consumed raw** (the scoping decision). `spa_points` is the analyst's *coded* SPA
  delta (per SM 11: for canonical, the assay reduces PRD — near-complete → 0, substantial →
  −25%·PRD, incomplete → −100%·PRD; blue additive `−2..+2`; violet benignity `−2..0` — the
  analyst applies that and codes the delta). The scorer consumes it, does not recompute it from
  the raw `SpliceAssayResult`.
- **held prd_spa** = `hold_combined(prd, spa)` — SM 11 gives an explicit cap only for violet
  (`−3.0 .. 0.0`); other paths default to the parent range.
- **SPL_FXN — consumed raw** (like every FXN; violet's benignity is enforced by the held/parent
  caps, not recomputed).
- **held prd_spa_fxn** = `hold_combined(prd_spa, fxn)` — SM 11 gives no explicit per-path cap;
  default to the parent range.
- **SPL_INF** — computed tally (the shared `informative_points`), capped per path.
- **spl_total** = `hold_combined(prd_spa_fxn, inf)`, capped to the parent range. Parent code is
  **always `SPL`**.

**Held-cap assumption (flagged):** SM 11 documents an explicit intermediate held cap only for
the violet path (`prd_spa −3..0`). For the other paths and for `prd_spa_fxn`, the reference
scorer caps the held value to the **parent range** (the natural bound — an intermediate cannot
exceed the parent total's cap). This is recorded in `provenance` and noted on the docs page.

## `score_spl_workflow` + `SplBranchSpec` — `scoring/pfd/_spl_common.py`

A new frozen `SplBranchSpec` (parent code is constant `SPL`, so it is not a field):

```python
@dataclass(frozen=True)
class SplBranchSpec:
    prd_lo: float
    prd_hi: float
    prd_spa_lo: float = -8.0      # held prd_spa floor (violet -3.0)
    prd_spa_hi: float = 10.0      # held prd_spa ceiling (violet 0.0)
    inf_lo: float = -8.0
    inf_hi: float = 8.0
    parent_lo: float = -8.0
    parent_hi: float = 10.0
```

`score_spl_workflow(assessment, branch_table, *, gene_disease_validity) -> ScoreResult`:
PRD (compute) → SPA (consume `spa_points`) → held `prd_spa` (cap `[prd_spa_lo, prd_spa_hi]`) →
FXN (consume `fxn_points`) → held `prd_spa_fxn` (cap `[parent_lo, parent_hi]`) → INF (tally, cap
`[inf_lo, inf_hi]`) → `spl_total` (cap `[parent_lo, parent_hi]`); `parent_code = "SPL"`. Each
sub-code (`PRD`/`SPA`/`FXN`/`INF`) is omitted when its input is absent (`_ND`). The
`held_combined` dict carries `PRD+SPA` and `PRD+SPA+FXN` keys. A `NulCdsAssessment`-style
Protocol (`SplAssessment`) captures the fields read (`prediction_outcome`, `predictive`,
`mechanism_exon_relevance`, `spa_points`, `fxn_points`, `informative`).

(Reuses `apply_sm18_multiplier`, `cap`, `hold_combined`, `informative_points`, `ScoreResult`
from the existing modules.)

## `reference_score_canonical_splice` — `scoring/pfd/canonical_splice.py`

`SplicePredictionOutcome`: `NMD_PREDICTED`, `FRAMESHIFT_NO_NMD`, `SPLICE_NO_FRAMESHIFT`,
`UNCERTAIN`, `UNLIKELY`. Branch table (verified vs `pfd/canonical-splice.md`):

| Path | PRD range | held prd_spa | INF | parent |
|---|---|---|---|---|
| `NMD_PREDICTED` (yellow) | `0.0 .. +6.0` | (parent range) | `−8 .. +8` | `−8 .. +10` |
| `FRAMESHIFT_NO_NMD` (upper orange) | `−1.0 .. +6.0` | (parent range) | `−8 .. +8` | `−8 .. +10` |
| `SPLICE_NO_FRAMESHIFT` (lower orange) | `−1.0 .. +6.0` | (parent range) | `−8 .. +8` | `−8 .. +10` |
| `UNCERTAIN` (blue) | `0.0 .. 0.0` | (parent range) | `−8 .. +8` | `−8 .. +8` |
| `UNLIKELY` (violet) | `−1.0 .. 0.0` | **`−3.0 .. 0.0`** | **`−8 .. 0.0`** | **`−8 .. 0.0`** |

As `SplBranchSpec` (only overrides shown):

```python
_BRANCH = {
    NMD_PREDICTED: SplBranchSpec(0.0, 6.0),
    FRAMESHIFT_NO_NMD: SplBranchSpec(-1.0, 6.0),
    SPLICE_NO_FRAMESHIFT: SplBranchSpec(-1.0, 6.0),
    UNCERTAIN: SplBranchSpec(0.0, 0.0, parent_hi=8.0),
    UNLIKELY: SplBranchSpec(-1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0, inf_hi=0.0, parent_hi=0.0),
}
```

`reference_score_canonical_splice(assessment, *, gene_disease_validity)`, exported from
`svcv4_model.scoring` (sorted `__all__`).

## Tests (TDD)

`tests/test_canonical_splice_scoring.py`:
- Yellow maximal: PRD +6 (Established×All), SPA `spa_points=0.0` (near-complete → no reduction),
  FXN +2, one P INF → held `PRD+SPA`=+6, held `PRD+SPA+FXN`=+8, parent capped +10, `parent_code
  "SPL"`.
- SPA consumed as a reduction: yellow PRD +6, `spa_points=-1.5` (substantial −25%) → held
  `PRD+SPA`=+4.5.
- Blue additive: `UNCERTAIN`, PRD 0, `spa_points=+2.0` → held `PRD+SPA`=+2.0; parent capped +8.
- Violet benignity: `UNLIKELY`, PRD −1.0, `spa_points=-2.0` → held `PRD+SPA`=cap(−3, [−3,0])=−3.0;
  a P informative clamped to 0 by `inf_hi=0`; parent in `[−8, 0]`.
- FXN consumed raw; a `spa_points`-absent path records `SPA: _ND`.
- All-five-outcomes loop (`parent_code == "SPL"`).
- Empty → all `_ND`, `parent_total` None.

## Docs

`docs/reference/scoring.md`: add Canonical Splice (SM 11), noting the SPL_ pipeline (extra
SPL_SPA step, two held values, SPA consumed raw) and the held-cap-to-parent-range assumption.

## Quality gates

`pytest`, `ruff`, drift gate (no schema), `mkdocs build --strict`, clean tree. The existing
NUL_/CDS_ scorers are untouched (the SPL_ helper is separate).

## Out of scope

Intronic/Synonymous (Increment B — same SPL_ helper, different point values) and Missense
(Increment C — MIS_ path + take-higher). POP/LOC/CLN; aggregation; validate_case.
