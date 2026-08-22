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

The shared `score_nul_cds_workflow` now carries per-branch caps via a `BranchSpec` (parent
floor/ceiling, held ceiling, INF ceiling), so each LoF scorer is just its branch table.

The remaining PFD workflows, POP/LOC/CLN, case aggregation, the classification band, and
`validate_case` follow in later increments (see the scoping doc).

## Known assumption (flagged for WG confirmation)

The SM 18 matrix's **Suspected mechanism × Most exon-relevance** cell was deliberately not
compounded to 12.5% by the Working Group; the authoritative value is in SM 18 Figure 1 (not
in this repo's text extracts). The reference scorer assumes **0.25** (keep the Suspected
fraction, drop the further Most halving) and records the assumption in `provenance`. This
affects only that single matrix cell.
