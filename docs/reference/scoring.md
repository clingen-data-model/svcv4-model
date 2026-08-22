# Reference scoring (non-authoritative)

!!! warning "Non-authoritative"

    The `svcv4_model.scoring` layer is a **reference** implementation of the documented
    Supplementary-Material point rules — for tests, worked examples, and the
    practice-variant-set. **ClinGen CSpec is the authoritative scorer.** Any divergence from
    CSpec is a bug in *this* layer, never in CSpec. Every result is a `ScoreResult` with
    `authoritative = False` (constructing it `True` raises).

`reference_score_*` functions are pure: they take a captured assessment/evidence entity and
return a `ScoreResult` — the coded sub-code points, any held-combined intermediates, the
capped parent-code total, and a `provenance` trail. A step that is un-scoreable / No-Data is
**omitted** (never recorded as `0.0`). Expert-calibrated inputs (functional OddsPath) are
**consumed** from the analyst's coded value, not recomputed.

```python
from svcv4_model.scoring import reference_score_nonsense

result = reference_score_nonsense(assessment, gene_disease_validity=gdv)
result.parent_total      # e.g. 10.0
result.provenance        # the audit trail, step by step
```

## What is modeled so far

- **Shared primitives** — the SM 18 mechanism/exon multiplier, caps, held-combined, and the
  informative-variant tally (`svcv4_model.scoring.primitives`).
- **Nonsense** (SM 8) — `reference_score_nonsense`, all three branches.
- **Frameshift** (SM 9) — `reference_score_frameshift`, all five branches (shares the
  `score_nul_cds_workflow` pipeline with Nonsense).
- **Start-Lost** (SM 15) — `reference_score_start_lost`, three branches (yellow/orange floor
  the parent total at −4.0; violet is benignity-only).
- **Stop-Lost** (SM 16) — `reference_score_stop_lost`, two branches.
- **Exon Deletion** (SM 13) — `reference_score_exon_deletion`, six branches (the whole-gene
  branch applies SM 18 mechanism-only; the grey functional-alt-start branch is benignity-only).
- **Exon Duplication** (SM 14) — `reference_score_exon_duplication`, six scored branches + a
  whole-gene-NA outcome (the gain paths code functional data as NA; the shared helper skips
  FXN on those branches via `BranchSpec.fxn_na`). **All six NUL_/CDS_ scorers are now modeled.**
- **Canonical Splice** (SM 11) — `reference_score_canonical_splice`, five paths. The first
  `SPL_` scorer: it uses a separate `score_spl_workflow` helper whose pipeline adds an
  **SPL_SPA** (splice-assay) step and records **two** held values (`PRD+SPA`, `PRD+SPA+FXN`);
  the parent code is always `SPL`. SPA is consumed raw — `spa_points` is the analyst's coded
  delta (on the canonical paths the assay *reduces* the PRD). Per-path caps live in a
  `SplBranchSpec` (the yellow/orange second held value caps at +9, the violet path is
  benignity-only).
- **Intronic & Synonymous** (SM 12) — `reference_score_intronic_synonymous`, five paths (the
  same `score_spl_workflow`, a new `SplBranchSpec` table). Field-identical to Canonical Splice;
  the point values differ — PRD tops at +3, the orange paths carry an explicit held `PRD+SPA`
  cap (`−1..+6`, since SPA scales the PRD *up* here), and blue's second held caps at +9.
- **Missense — amino-acid path** (SM 6) — `reference_score_missense_amino_acid`, the first
  `MIS_` scorer. A standalone single-path pipeline: MIS_PRD is reduced by **transcript relevance
  only** (no molecular mechanism, **no GDV gate** — so this scorer takes no
  `gene_disease_validity`), and MIS_INF is a computed **4-category Grantham tally**
  (`missense_informative_points`). The `SPL_` splice path and the `MIS_`-vs-`SPL_` take-higher
  comparison are below.
- **Missense — splice path + comparison** (SM 6) — `reference_score_missense_splice` (a
  `score_spl_workflow` branch table) and `reference_score_missense`, the `MIS_`-vs-`SPL_`
  **take-higher** (negative/absent splice or a positive tie → the amino-acid path; else the
  higher), returning a `MissenseScoreResult` that saves both sub-path scores. **Note:** SM 6's
  splice blue/violet parent caps are inverted vs SM 11/12 (blue `−8..0`, violet `−8..+8`) —
  encoded faithfully and flagged as a suspected SM 6 inconsistency. This completes the splice
  family (Canonical, Intronic, Missense).

The shared `score_nul_cds_workflow` carries per-branch caps via a `BranchSpec` (parent
floor/ceiling, held ceiling, INF ceiling), so each LoF scorer is just its branch table; the
`SPL_` workflows use the parallel `score_spl_workflow` / `SplBranchSpec` pair.

The remaining PFD workflows, POP/LOC/CLN, case aggregation, the classification band, and
`validate_case` follow in later increments (see the scoping doc).

## Known assumption (flagged for WG confirmation)

The SM 18 matrix's **Suspected mechanism × Most exon-relevance** cell was deliberately not
compounded to 12.5% by the Working Group; the authoritative value is in SM 18 Figure 1 (not
in this repo's text extracts). The reference scorer assumes **0.25** (keep the Suspected
fraction, drop the further Most halving) and records the assumption in `provenance`. This
affects only that single matrix cell.
