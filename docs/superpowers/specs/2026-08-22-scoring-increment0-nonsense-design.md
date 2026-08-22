# Reference scorer — Increment 0 (scaffold + primitives + Nonsense) — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Parent scoping doc:** `2026-08-21-scoring-computation-scoping.md`
**Branch:** `feat/scoring-computation` (off `main`)
**Scope:** the first, pattern-setting slice of the **reference, non-authoritative** scorer.

## Goal

Stand up `src/svcv4_model/scoring/`: the `ScoreResult` contract, the shared `primitives.py`
(SM 18 multiplier, cap, held-combined, informative tally), and `reference_score_nonsense`
end-to-end across all three SM 8 branches. Non-authoritative — CSpec is authoritative; this
mirrors the documented rules for tests and worked examples. Purely additive: no capture
model, schema, applicability matrix, or existing doc rule changes.

## Package layout (this increment)

```
src/svcv4_model/scoring/
    __init__.py            # exports: ScoreResult, reference_score_nonsense
    result.py              # ScoreResult (frozen dataclass)
    primitives.py          # apply_sm18_multiplier, cap, hold_combined, informative_points
    pfd/
        __init__.py
        nonsense.py        # reference_score_nonsense
tests/scoring/
    test_primitives.py
    test_nonsense_scoring.py
docs/reference/scoring.md  # the non-authoritative contract (new nav entry under Reference)
```

**The scoring subpackage is NOT re-exported from `svcv4_model/__init__.py`.** Consumers import
`from svcv4_model.scoring import reference_score_nonsense`. This keeps `scoring` out of the
root `__all__`, so `export_schemas.py` (which emits a schema per BaseModel in the root
`__all__`) does not touch it — the drift gate stays clean and no scoring schema files are
produced. Dependency points one way: `scoring → svcv4_model.*` models, never the reverse.

## `ScoreResult` (frozen dataclass, not Pydantic)

A **compute DTO**, deliberately a `@dataclass(frozen=True)` rather than a Pydantic model —
it is scorer output, not a captured evidence entity, and must never land in `schemas/json`
or the model reference. Fields:

- `parent_code: str | None` — e.g. `"NUL_"` / `"CDS_"`.
- `sub_code_points: dict[str, float]` — coded sub-code values, e.g. `{"PRD": 6.0, "FXN": 2.0,
  "INF": 1.0}`. A step that is un-scoreable / No-Data is **omitted** (not `0.0`), and noted in
  `provenance`.
- `held_combined: dict[str, float]` — e.g. `{"PRD+FXN": 8.0}`.
- `parent_total: float | None`.
- `provenance: list[str]` — one human-readable line per step: the rule applied, the cap, and
  any `_ND`/assumption. This is the audit trail.
- `authoritative: bool` — a field defaulted to `False`; `__post_init__` **raises** if it is
  ever constructed `True`, so the non-authoritative contract cannot be bypassed.

## `primitives.py`

### `cap(value, lo, hi) -> float`
Clamp. `cap(None, ...)` returns `None`.

### `hold_combined(*parts, lo, hi) -> float | None`
Sum the non-`None` parts, then `cap`. If **all** parts are `None`, return `None` (nothing to
hold). Records nothing itself — the caller adds provenance.

### `informative_points(variants) -> float | None`
The shared SM 19 tally over a list of `InformativeVariant` (each has a `classification`):
- Pathogenic side: **+2.0** for the first P, **+1.0** for the first LP, **+1.0** for each
  additional P or LP.
- Benign side (symmetric): **−2.0** first B, **−1.0** first LB, **−1.0** each additional B/LB.
- `VUS` contributes `0.0`. A mix of P/LP and B/LB is summed.
- Empty / all-`None`-classification list → `None` (`_INF_ND`).
- Assumes the captured list is already the *eligible* set (per-branch position eligibility is
  an analyst determination captured upstream, not recomputed here — documented in provenance).

### `apply_sm18_multiplier(points, mechanism, exon_relevance, gene_disease_validity) -> float`
The SM 18 matrix, applied **only to positive `points`** (negatives and `None` pass through
unchanged; `0.0` stays `0.0`):

- **GDV gate:** if `gene_disease_validity` is below **Moderate** (Limited / Disputed /
  Refuted / Not-classified / `None`), the mechanism is treated as Uncertain → **×0.0**
  (documented project gate; provenance records it).
- **Mechanism fraction:** Established → 1.0, Likely → 0.5, Suspected → 0.25, Uncertain →
  0.0. (`None` mechanism → 0.0, with a provenance note.)
- **Exon-relevance fraction:** All → 1.0, Most → 0.5, Few → 0.0. (`None` → treated as All =
  1.0, i.e. no exon reduction, with a provenance note — the conservative default when the
  analyst did not assess exon relevance.)
- **Combine:** `fraction = mechanism_fraction × exon_relevance_fraction` — **except** the one
  cell SM 18 special-cases: **Suspected × Most**, which SM 18 explicitly declined to compound
  to 0.125 ("fractions this small were not useful"). **⚠️ OPEN INPUT:** the actual
  Suspected×Most cell value comes from SM 18 Figure 1 (an image not in the repo). Until
  confirmed, this increment assumes **0.0** (drop — consistent with "not useful") and records
  the assumption in `provenance` with a flag. This is the one fidelity gap in Increment 0 and
  is called out for WG confirmation; it affects only the single Suspected×Most combination.
- Fractional results are allowed and carried forward (e.g. `+3.0 × 0.25 = 0.75`).

## `reference_score_nonsense(assessment, *, gene_disease_validity=None) -> ScoreResult`

`gene_disease_validity` is a keyword argument because a `NonsenseAssessment` does not carry it
(it lives on `WorkflowParameters` / `Case`); the caller supplies it. The pipeline (SM 8):

1. **PRD.** Take `assessment.predictive.initial_points` as the pre-adjustment initial (the
   analyst-captured branch initial: yellow +6.0; orange/violet from the protein-fraction
   table). `prd = cap(apply_sm18_multiplier(initial, mechanism, exon_relevance, gdv), lo, hi)`
   where `(mechanism, exon_relevance)` come from `assessment.mechanism_exon_relevance`, and the
   PRD range is the branch's (`NUL_PRD_ 0.0..+6.0` yellow; `CDS_PRD_ −1.0..+6.0` orange;
   `CDS_PRD_ 0.0..+6.0` violet). If `predictive`/`initial_points` is absent → PRD omitted
   (`_PRD_ND`).
2. **FXN — consumed, not recomputed.** `fxn = assessment.fxn_points` (the analyst's coded
   functional value; OddsPath calibration is expert-input, never invented here). Absent →
   `_FXN_ND`.
3. **Held PRD+FXN.** `held = hold_combined(prd, fxn, lo=−8.0, hi=(+10.0 if yellow else +9.0))`
   — the SM 8 held cap (`+10.0` yellow, `+9.0` orange/violet).
4. **INF.** `inf = informative_points(assessment.informative.variants)` if present, else
   `_INF_ND`, coded within `−8.0..+8.0`.
5. **Parent total.** `parent_total = hold_combined(held, inf, lo=−8.0, hi=+10.0)` — the parent
   cap `NUL_/CDS_ −8.0..+10.0`.
6. Return `ScoreResult(parent_code, sub_code_points, held_combined={"PRD+FXN": held},
   parent_total, provenance, authoritative=False)`. `parent_code` follows the branch
   (`NUL_` yellow; `CDS_` orange/violet), consistent with `assessment.parent_code`; if the
   captured `parent_code` disagrees, that contradiction is noted in `provenance` (the reference
   scorer reports, it does not "fix" captured data).

Cross-check helpers (not enforcement): where the assessment ALSO carries analyst-coded
`prd_points` / `parent_total`, the tests assert the reference computation matches — turning
the scorer into a validator of the documented rules against hand-worked values.

## Tests (TDD)

**`test_primitives.py`:**
- `cap` clamps low/high/inside/`None`.
- `apply_sm18_multiplier`: Established×All = full; Likely×All = ½; Suspected×All = ¼ (0.75
  from +3.0); mechanism `Uncertain`/exon `Few` → 0.0; GDV below Moderate → 0.0; negatives and
  `0.0` pass through unchanged; the flagged Suspected×Most → 0.0 (assumption) with provenance.
- `hold_combined`: sums + caps; all-`None` → `None`.
- `informative_points`: 1 P → +2.0; 1 P + 2 LP → +4.0; 1 LP → +1.0; 2 B → −3.0; P+B mix
  sums; all-VUS → 0.0; empty → `None`.

**`test_nonsense_scoring.py`:**
- Yellow maximal: `initial +6.0`, Established×All, `fxn +2.0`, one P informative →
  `prd +6.0`, `held +8.0`, `inf +2.0`, `parent_total +10.0` (cap), `parent_code "NUL_"`.
- Orange: a `−1.0` initial, `fxn` present, held capped at `+9.0`.
- Violet: reduced mechanism (Likely×Most) reducing a positive PRD; `_FXN_ND` path (fxn
  absent → held = prd alone); benign informative pulling `parent_total` negative.
- `authoritative=True` construction raises.
- A permissive-empty `NonsenseAssessment()` → all sub-codes `_ND`, `parent_total` `None`, no
  crash.

## Docs

- New `docs/reference/scoring.md`: the non-authoritative contract (what it is, that CSpec is
  authoritative, how `ScoreResult`/`provenance` work, the Figure-1 Suspected×Most caveat),
  and a worked Nonsense example. Nav: add under **Reference**.
- No per-workflow page or example-page edits (computed totals stay in tests, per the scoping
  decision).

## Quality gates

`pytest` (incl. the new `tests/scoring/`), `ruff check`, drift gate (`git diff --quiet --
schemas/json docs/workflows/case-model.md` → GATE_CLEAN — no schema produced for scoring),
`mkdocs build --strict`, clean tree.

## Explicitly out of scope (Increment 0)

Other workflow scorers; the `SPL_SPA` primitive and the missense take-higher; POP/LOC/CLN;
case aggregation; classification band; `validate_case`; recomputing FXN OddsPath or any
expert-calibrated value; resolving the SM 18 Figure-1 Suspected×Most cell (flagged, assumed).
