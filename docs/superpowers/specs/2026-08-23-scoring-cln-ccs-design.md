# Reference scorer — CLN_CCS case-control (SM 4) — design

**Date:** 2026-08-23
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-cln-ccs` (off `main`)
**Scope:** the case-control clinical code (SM 4) — the **last** CLN code. Completes CLN.

## Goal

Add `reference_score_cln_ccs` (SM 4): the study-level case-control code. Operates on the
standalone `CaseControlStudyEvidence` (like POP's `PopulationEvidence`, **not** the per-proband
`Case`). `parent_code="CLN"`, single sub-code `CLN_CCS`. Non-authoritative; CSpec authoritative.

## Scoring (SM 4 L25 + the L15 footnote)

- **`OR > 5.0`** (and the CI does **not** include 1.0) → **`CLN_CCS_+4.0`**.
- **CI includes 1.0** (e.g. OR 5.5, CI 0.9–7.4) → **no points** (`0.0`) — the association is not
  significant, vetoing the `+4.0`.
- **`OR` near/`≤ 1.0`** → **benignity** — but **SM 4 assigns no CLN_CCS benign point value**
  (only "should be evidence of benignity"). See DD3.
- otherwise (`1.0 < OR ≤ 5.0`) → `0.0` (insufficient enrichment).

**Robustness gate (SM 4 L19/L24):** use is *restricted* to `case_variant_count ≥ 5` **and**
`case_cohort_size ≥ 100` **and** `controls_matched is True`. A study that fails any gate is
**not robust** → `CLN_CCS_ND` (SM 4: "robust case-control studies… unavailable… coded as
CLN_CCS_ND").

## Design decisions (flagged)

- **DD1 — robustness gate → `_ND`.** `_ND` when `odds_ratio is None`, or when the study is not
  robust (any of: `case_variant_count` missing/`< 5`; `case_cohort_size` missing/`< 100`;
  `controls_matched` not `True`). `ascertainment_bias_considered` is a "must be considered"
  judgement (SM 4 L23), **noted in provenance but not gated** (a `False`/`None` doesn't block).
- **DD2 — CI veto.** `ci_includes_1 = ci_lower is not None and ci_upper is not None and
  ci_lower <= 1.0 <= ci_upper`. When the CI includes 1.0 the `+4.0` is withheld → `0.0`. A `None`
  CI does **not** veto (SM 4 frames the CI as a "should also consider" check, not a hard input) —
  flagged.
- **DD3 — `OR ≤ 1.0` benignity has NO SM 4 point value.** SM 4 says a low OR "should be evidence
  of benignity" but assigns **no CLN_CCS benign number** (benignity flows through POP_FRQ etc.).
  The scorer records `CLN_CCS 0.0` with a `provenance` flag that benignity is *indicated* but
  unquantified — a documented source gap (like the SM 18 / SM 6 / SM 3 flags), logged in
  `known-gaps.md`.
- **DD4 — exclusivity deferred.** SM 4: when CLN_CCS is applied, **all other CLN codes become NA
  except CLN_DNV**. This cross-code suppression is an **aggregation-layer** rule — this scorer
  produces only CLN_CCS; the exclusivity is deferred (noted in provenance), consistent with the
  per-`Case`/per-evidence scoring throughout CLN.
- **DD5 — standalone evidence.** `reference_score_cln_ccs(evidence)` takes
  `CaseControlStudyEvidence` only — no `Case`, no `moi` (case-control is variant/study-level).

## `reference_score_cln_ccs(evidence)` — `scoring/hod/clinical.py`

```python
or_ = evidence.odds_ratio
if or_ is None: -> _ND
robust = (
    evidence.case_variant_count is not None and evidence.case_variant_count >= 5
    and evidence.case_cohort_size is not None and evidence.case_cohort_size >= 100
    and evidence.controls_matched is True
)
if not robust: -> _ND (flag which gate)
ci_includes_1 = (evidence.ci_lower is not None and evidence.ci_upper is not None
                 and evidence.ci_lower <= 1.0 <= evidence.ci_upper)
if or_ > 5.0 and not ci_includes_1: pts = 4.0
else: pts = 0.0   # CI veto, 1<OR<=5, or OR<=1 (benignity indicated, no SM 4 CLN_CCS value)
```

`parent_code="CLN"`, `sub_code_points={"CLN_CCS": pts}` (or `{}` when `_ND`), `parent_total=pts`;
provenance records OR/CI, the gate result, the CI-veto / benign-unquantified / exclusivity notes.

## Tests (TDD) — `tests/test_cln_ccs_scoring.py`

- robust + OR 6.0, CI 2.0–9.0 (excludes 1) → `+4.0`.
- robust + OR 5.5, CI 0.9–7.4 (includes 1) → `0.0` (CI veto); OR 6.0, CI None → `+4.0` (no veto).
- robust + OR 3.0 → `0.0` (1<OR≤5); OR 0.5 → `0.0` (benignity indicated — provenance flag).
- gate fails → `_ND`: `case_variant_count=4`; `case_cohort_size=50`; `controls_matched=False`;
  `controls_matched=None`; each with an otherwise-passing OR.
- `odds_ratio None` → `_ND`.
- `parent_code "CLN"`, `parent_total` mirrors; provenance carries the exclusivity + benign-flag
  notes.

## Docs

- `docs/reference/scoring.md`: extend the CLN line — CLN is complete with `reference_score_cln_ccs`
  (case-control, standalone `CaseControlStudyEvidence`; OR>5+robust→+4, CI-includes-1 veto, the
  robustness gate, benign-unquantified, exclusivity deferred).
- `docs/reference/known-gaps.md`: a WG/source-gap row — SM 4 gives no CLN_CCS **benign** point
  value for a low OR (only "evidence of benignity").

## Quality gates

`pytest`, `ruff`, drift gate (no schema), `mkdocs build --strict`, clean tree. All existing
scorers untouched.

## Out of scope

The CLN_CCS **exclusivity** enforcement (aggregation-layer), the cross-proband/cross-code CLN
aggregation, quantifying the benign OR direction (no SM 4 value). LOC (SM 5); classification band;
validate_case.
