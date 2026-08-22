# Reference scoring computation — scoping & architecture

**Date:** 2026-08-21
**Status:** Scoping (direction) — awaiting user approval before Increment 0
**Branch:** `feat/scoring-computation` (off `main`)
**Decision (settled):** build a **reference, non-authoritative** scorer *in this repo*.
ClinGen CSpec remains the **authoritative** source of the scoring rules; this layer mirrors
the documented SM point rules for tests, worked examples, and the practice-variant-set — it
does **not** replace or compete with CSpec.

## Why this exists (and why it's the first thing that "computes")

Every increment so far has held a hard line — **capture + document, never compute** — because
the project boundary is "this repo captures evidence + classification; CSpec owns the
methods/rules." A reference scorer deliberately crosses that line, but *narrowly and
labelled*: it lets the modeled entities be exercised end-to-end (does a populated
`NonsenseAssessment` reduce to the point total the SM says it should?), gives the
practice-variant-set examples computable totals, and turns the prose caps/ranges we've
documented on every workflow page into executable, testable rules. The boundary is preserved
by **marking**, not by exclusion (see below), so there is exactly one *authoritative* rule
source (CSpec) and one clearly-subordinate *reference* implementation (here).

## Non-authoritativeness — how it is enforced (not just asserted)

1. **Isolation:** all compute lives in a new `src/svcv4_model/scoring/` subpackage. The
   capture entities (`svcv4_model.*` models) never import from `scoring/` — the dependency
   points one way (scoring → models), so the capture layer stays pure and the scorer is
   deletable without touching the model.
2. **Naming:** the public entry points are `reference_score_*` (never `score_*`), and the
   subpackage docstring states the non-authoritative contract verbatim.
3. **Typed result carries the disclaimer:** every scorer returns a `ScoreResult` whose
   `authoritative` field is hard-wired `False`, alongside the computed values and a
   `provenance` list (the SM rule + cap applied at each step), so a consumer can never mistake
   it for a CSpec verdict and can audit how a number was reached.
4. **Docs:** a single reference page states the contract; the per-workflow pages keep their
   "scoring documented, not computed **here in the model**" framing, updated to point at the
   reference scorer as illustrative.

## Architecture

```
src/svcv4_model/scoring/
    __init__.py            # exports reference_score_* + ScoreResult (marked non-authoritative)
    result.py              # ScoreResult: coded sub-code points, held-combined values,
                           #   parent_total, provenance[], authoritative=False
    primitives.py          # SHARED, workflow-agnostic:
                           #   apply_sm18_multiplier(points, mechanism, exon_relevance,
                           #       gene_disease_validity) -> reduced points
                           #   cap(value, lo, hi); hold_combined(*parts, lo, hi)
                           #   informative_points(variants) ; ...
    pfd/
        nonsense.py        # reference_score_nonsense(NonsenseAssessment) -> ScoreResult
        ...                # one module per PFD workflow, all composing primitives
    hod/
        population.py      # reference_score_population(PopulationEvidence) -> ScoreResult
        ...
    aggregate.py           # later: combine per-proband/observation results
    classify.py            # later: Bayesian point total -> P/LP/VUS/LB/B band
    validate.py            # later: validate_case against the applicability matrix (r/o/c/x)
```

- **Pure functions.** Each `reference_score_*` takes a captured assessment/evidence entity
  and returns a `ScoreResult`. No I/O, no mutation of the input, deterministic.
- **Primitives first.** The SM 18 mechanism/exon multiplier, the per-step caps, the held-
  combined (`PRD+FXN`, `PRD+SPA`, …) arithmetic, and the informative-variant tally are shared
  across nearly every PFD workflow — they live in `primitives.py` and every workflow scorer
  composes them. This is why the first slice builds the primitives *and* the first workflow
  together (below).
- **Missing inputs → explicit, not zero.** A scorer over a permissive/partly-empty entity
  returns a `ScoreResult` that records which steps were `None`/un-scoreable (e.g. `_ND`),
  rather than silently treating absent evidence as `0.0`.
- **Expert-calibration carve-outs stay captured, not computed.** Where an SM defers to expert
  calibration the reference scorer cannot invent (protein-assay OddsPath from raw data,
  trichotomized/MAVE calibration), the scorer consumes the analyst-provided coded value
  (`fxn_points`) and does not recompute it — faithful to the SM, and to the capture boundary.

## Decomposition into increments (built one workflow/use-case at a time)

The scorer is large; it ships as a sequence of small, independently-valuable increments, each
following the established brainstorm → spec → plan → TDD → review → PR pipeline.

- **Increment 0 — scaffold + first workflow (the pattern-setter):** `ScoreResult`,
  `primitives.py` (SM 18 multiplier + `cap` + `hold_combined` + informative tally), and the
  **Nonsense** (`reference_score_nonsense`) scorer end-to-end (PRD → SM 18 → FXN cap → held
  `PRD+FXN` → INF → capped parent total, all three branches). Nonsense is chosen as the
  pattern-setter: three branches, the full `NUL_`/`CDS_` pipeline, and the shared primitives,
  without splice/SPA complexity. Establishes the module shape, the `ScoreResult` contract, and
  the primitives every later scorer reuses.
- **Increments 1..k — the remaining PFD workflows:** Frameshift, In-Frame InDel, Exon
  Deletion/Duplication, Start-/Stop-Lost (reuse the NUL_/CDS_ pattern); then the splice family
  (Missense dual-path, Canonical Splice, Intronic/Synonymous) which adds the `SPL_SPA`
  primitive and the `MIS_`-vs-`SPL_` "take the higher" comparison. Grouped a few per increment
  where they share mechanics.
- **Increment — POP scorer:** `reference_score_population` (FAF-vs-DAFT fold-difference bands
  + POP_HMZ 2nd-occurrence counting). Highest-fidelity validation target — SM 3's FBN1-Marfan
  worked example (DAFT 0.000118 → exact FAF thresholds → `POP_FRQ_0.0/-1.0/-3.0/-6.0`) is an
  exact golden fixture.
- **Increment — LOC / CLN scorers** where scoring is documented (LOC_PHE/LOC_SEG; the CLN
  per-proband category → points). These lean on the Case model + SM 4/5.
- **Increment — case aggregation:** combine per-proband/observation `ScoreResult`s within a
  workflow (counting, distinct-variant rules) into an evidence-line total.
- **Increment — classification band:** map the aggregated Bayesian point total to
  P/LP/VUS/LB/B (`classify.py`), the last mile.
- **Increment — `validate_case`:** enforce the applicability matrix `r/o/c/x` + conditional
  rules (the long-deferred rule-*enforcement* item), returning structured violations. This is
  rule-checking rather than point-computation and can proceed in parallel with the scorers.

## Validation strategy

- **Golden fixtures from SM worked examples** (highest fidelity): SM 3's FBN1-Marfan POP
  example is input→expected-points exact; other SMs give per-branch caps/values. Each scorer's
  tests assert the documented caps and the worked-example outputs.
- **Practice-variant-set as integration:** once several scorers + aggregation land, the
  practice-variant-set entries become end-to-end integration cases (captured evidence →
  reference total), surfacing gaps.
- **Property tests for primitives:** caps clamp; the SM 18 multiplier never *increases* points
  and zeroes at `UNCERTAIN`/`Few`/Limited-GDV; held-combined respects its own cap.

## Non-goals / boundary reminders

- **Not authoritative.** Divergence from CSpec is a bug in *this* layer, never in CSpec.
- **No expert-calibration invention** (OddsPath from raw assay data, MAVE) — consume the coded
  value the analyst captured.
- **SM 17 Non-Coding** is unreleased (WG gap) — out.
- The reference scorer does **not** change any capture model, schema, or the applicability
  matrix; it is purely additive.

## Resolved decisions (user-approved 2026-08-21)

1. **First slice = Nonsense + shared primitives.** Increment 0 builds `ScoreResult`,
   `primitives.py`, and `reference_score_nonsense` (all three branches).
2. **`ScoreResult` shape as proposed:** coded sub-code points + held-combined + `parent_total`
   + `provenance: list[str]` + hard-wired `authoritative = False`.
3. **Docs surfacing:** one new `reference/scoring.md` page describing the non-authoritative
   contract + linking worked examples; **computed totals live in tests only for now** — the
   practice-variant-set example pages are left unchanged.
4. **`validate_case` deferred** until after the PFD scorers land (this scoping's decomposition
   keeps it as a later, parallel-capable track).
