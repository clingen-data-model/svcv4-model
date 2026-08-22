# Reference scorer — Frameshift (SM 9) + shared NUL_/CDS_ helper — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Parent scoping doc:** `2026-08-21-scoring-computation-scoping.md`
**Branch:** `feat/scoring-frameshift` (off `main`)
**Scope:** the second PFD workflow scorer, and the extraction of the shared NUL_/CDS_ pipeline
that the remaining LoF scorers reuse.

## Goal

Add `reference_score_frameshift` (SM 9, five branches) and, in the same increment, **extract
the shared NUL_/CDS_ scoring pipeline** — currently inlined in `reference_score_nonsense` —
into a single `score_nul_cds_workflow` helper driven by a per-workflow branch table. Nonsense
is refactored to call it (behaviour-preserving; its existing tests are the guard). This is the
DRY move justified by concrete upcoming reuse: Frameshift, Exon Deletion, Exon Duplication,
Start-Lost, and Stop-Lost are all the same PRD → SM 18 → FXN → held PRD+FXN → INF → capped
parent pipeline, differing only in their branch table. Non-authoritative; CSpec is
authoritative.

## Why generalize now (not speculatively)

The rule of two: Nonsense established the pattern, Frameshift is the second identical instance,
and four more NUL_/CDS_ workflows are known to follow. Extracting on the second instance (with
a behaviour-preserving refactor of the first, verified by the first's tests) avoids six
copy-paste bodies and gives the code-review "reuse/simplification" angle nothing to flag on
every subsequent scorer.

## The shared helper — `scoring/pfd/_common.py`

```python
def score_nul_cds_workflow(
    assessment: NulCdsAssessment,
    branch_table: Mapping[object, tuple[str, float, float, float]],
    *,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> ScoreResult
```

- `branch_table` maps each workflow's `prediction_outcome` enum value → `(parent_code,
  prd_lo, prd_hi, held_hi)`. The parent cap is a shared constant (`−8.0 .. +10.0`), the FXN
  cap is shared (`−8.0 .. +8.0`), and the INF cap is shared (`−8.0 .. +8.0`); only the PRD
  range and the held-PRD+FXN ceiling vary per branch, so those live in the table.
- The body is exactly today's `reference_score_nonsense` logic (PRD initial → SM 18 multiplier
  → cap to `[prd_lo, prd_hi]`; FXN consumed from `fxn_points`; held = `hold_combined(prd, fxn,
  lo=−8, hi=held_hi)`; INF = `cap(informative_points(...), −8, 8)`; parent = `hold_combined(
  held, inf, lo=−8, hi=10)`; captured-vs-derived `parent_code` reported in provenance).
- **`NulCdsAssessment`** is a small `typing.Protocol` capturing the fields the helper reads
  (`prediction_outcome`, `parent_code`, `predictive.initial_points`,
  `mechanism_exon_relevance.gencc_mechanism`/`.exon_relevance`, `fxn_points`,
  `informative.variants`). `NonsenseAssessment` and `FrameshiftAssessment` both satisfy it
  structurally. (The repo runs ruff, not mypy, so the Protocol is documentation + light
  static hint, not enforced.)
- `gene_disease_validity` stays a **required keyword** (the Increment-0 code-review decision).

## `reference_score_frameshift` — `scoring/pfd/frameshift.py`

A thin wrapper: its `_BRANCH` table + a one-line delegation to `score_nul_cds_workflow`. The
SM 9 branch table (verified against `pfd/frameshift.md`):

| `prediction_outcome` | parent | PRD range | held cap |
|---|---|---|---|
| `NMD_NO_RESCUE` (yellow) | `NUL` | `0.0 .. +6.0` (initial +6.0) | `+10.0` |
| `NMD_WITH_RESCUE` (orange) | `CDS` | `−1.0 .. +6.0` | `+9.0` |
| `NO_NMD` (violet) | `CDS` | `0.0 .. +6.0` | `+9.0` |
| `NON_STOP_DECAY` (green) | `NUL` | `0.0 .. +4.0` (initial +4.0) | `+9.0` |
| `PROTEIN_EXTENSION` (green) | `CDS` | `0.0 .. +4.0` | `+9.0` |

All five parent totals cap at `−8.0 .. +10.0`. The held-PRD+FXN ceiling is `+10.0` only for
yellow, `+9.0` for the other four (per SM 9 / `frameshift.md`). FXN is consumed, not
recomputed (as with Nonsense). The two green branches (NSD / protein-extension) are a
non-additive analyst choice upstream — the scorer scores whichever single `prediction_outcome`
was captured; it does not combine them.

`reference_score_frameshift(assessment, *, gene_disease_validity)` is exported from
`svcv4_model.scoring` alongside `reference_score_nonsense`.

## Refactor of `reference_score_nonsense`

`scoring/pfd/nonsense.py` keeps its `_BRANCH` table and becomes a one-line delegation to
`score_nul_cds_workflow`. **No behaviour change** — `tests/test_nonsense_scoring.py` (unchanged)
is the regression guard. The Nonsense branch table is unchanged: yellow `NUL 0..+6 held+10`,
orange `CDS −1..+6 held+9`, violet `CDS 0..+6 held+9`.

## Tests (TDD)

`tests/test_frameshift_scoring.py`, mirroring the nonsense scorer tests:
- Yellow maximal: initial +6.0, Established×All, fxn +2.0, one P informative → PRD +6.0, held
  +8.0, INF +2.0, parent_total +10.0 (cap), `parent_code == "NUL"`.
- Green NSD: `NON_STOP_DECAY`, initial +4.0, Established×All, fxn absent → PRD +4.0,
  held +4.0 (prd alone), `parent_code == "NUL"`, held cap is +9 (assert e.g. initial+4, fxn+8
  → held 9.0).
- Green extension: `PROTEIN_EXTENSION`, `parent_code == "CDS"`, PRD capped to `[0, 4]`.
- Orange held cap +9 (initial +6, fxn +8 → held 9.0).
- Violet reduced mechanism (Likely×Most halving) + benign informative pulling parent negative.
- Empty `FrameshiftAssessment()` → all `_ND`, `parent_total` None.

No new primitive tests (primitives unchanged). The refactor is covered by the existing
nonsense tests staying green.

## Docs

- `docs/reference/scoring.md`: update the "What is modeled so far" list to add **Frameshift
  (SM 9)** alongside Nonsense.
- No new page, no nav change.

## Quality gates

`pytest` (full suite, incl. unchanged nonsense tests), `ruff check`, drift gate (**no schema
produced** — scoring still absent from the root `__all__`), `mkdocs build --strict`, clean
tree.

## Out of scope

The splice family (needs the SPL_SPA primitive + take-higher) and POP/LOC/CLN; case
aggregation; `validate_case`. The SM 18 Figure-1 Suspected×Most cell stays the flagged 0.25
assumption (unchanged from Increment 0).
