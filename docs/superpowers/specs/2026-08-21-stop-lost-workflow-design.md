# Stop-Lost (`NUL_`/`CDS_`) workflow — design

**Date:** 2026-08-21
**Status:** Approved (design)
**Supplementary Material:** SM 16 (Stop Lost Variants)
**Branch:** `feat/pfd-stop-lost` (off `main`)
**Scope:** capture + document only — NO scoring computation (deferred to ClinGen CSpec)

## Goal

Model the SM 16 Stop-Lost workflow as the **tenth and final** per-variant-type PFD
increment: one permissive, capture-only `StopLostAssessment` entity that routes a stop-lost
VBC down one of two branches to a `NUL_` or `CDS_` parent code, reusing the shared
`PfdParentCode` and the SM 18/19/20 submodules. The simplest variant workflow so far — two
branches split on the **non-stop decay (NSD)** prediction. Follows the `exon_deletion.py`
module shape.

## Background

Stop-lost (nonstop / readthrough / nonstop-extension) variants disrupt the normal stop
codon so it encodes an amino acid, extending the ORF. They are conceptually similar to
nonsense/frameshift but have a distinct decay mechanism — **non-stop decay (NSD)**,
analogous to but distinct from NMD. The first (and only) branch point is whether NSD is
predicted, which depends on the position of the next in-frame stop codon relative to the
polyA site. (Explicitly out of scope: deletions of a large portion / the entirety of the
last coding exon → In-Frame Deletion / Exon Deletion; frameshifts extending the ORF past
the stop → Frameshift.)

## The two branches

`StopLostOutcome` (StrEnum, two values):

| Branch (`prediction_outcome`) | SM 16 color | NSD? | Parent | PRD initial |
|---|---|---|---|---|
| `NSD_PREDICTED` | yellow | yes (no in-frame stop before polyA) | `NUL_` | `+4.0` |
| `NO_NSD` | orange | no (in-frame stop before polyA) | `CDS_` | `0.0 to +4.0` |

Per-branch pipeline detail (all **documented, not computed**):

- **`NSD_PREDICTED` (yellow → `NUL_`):** no in-frame stop before the mRNA polyA site →
  mRNA degraded. Awards **+4.0** (lower than other LoF flows given less experience with
  NSD than NMD; the +10.0 parent cap is nonetheless retained) → SM 18 matrix
  (`NUL_PRD_0.0..+4.0`) → FXN (SM 20, must confirm transcript/protein loss — **not** an
  elongated-protein effect; `NUL_FXN_-8.0..+8.0`, `NUL_FXN_ND` if none; held `PRD+FXN`
  capped `-8.0..+9.0`) → INF (SM 19; informative P variants must produce a termination
  codon **downstream of the polyA site** — the codon need not match the VBC's;
  `NUL_INF_-8.0..+8.0`) → parent **`NUL_ −8.0..+10.0`**.
- **`NO_NSD` (orange → `CDS_`):** an in-frame stop exists before the polyA hexamer, so the
  protein is extended with non-native C-terminal amino acids. No in-silico tool predicts
  this consequence, so the initial points come from **functional data of similar variants**
  plus the **extension length**, on a four-tier scale:
    - **+4.0** — experimental data from similar variants show loss of protein function
    - **+3.0** — some interference evidence **AND** predicted extension ≥30 aa past the
      native stop
    - **+2.0** — some interference evidence **OR** predicted extension ≥30 aa
    - **0.0** — no functional data implicating the added C-terminal amino acids

  → SM 18 matrix (`CDS_PRD_0.0..+4.0`) → FXN (rarely available beyond the initial-points
  data, included for completeness; `CDS_FXN_-8.0..+8.0`, `CDS_FXN_ND` if none; held
  `PRD+FXN` capped `-8.0..+9.0`) → INF (limited to other stop-lost variants predicted to
  cause an equivalent protein extension; `CDS_INF_-8.0..+8.0`) → parent
  **`CDS_ −8.0..+10.0`**.

### Shared informative-variants (INF) rules (documented, not computed)

Both branches: +2.0 first P / +1.0 first LP / +1.0 each additional distinct P/LP; negatives
for B/LB with similar logic; a B/LB + P/LP mix is summed; VUS-only → 0.0; none → `_ND`;
same-MDE; only distinct variants count. Capped `−8.0 to +8.0`.

## Entities

New module `src/svcv4_model/stop_lost.py`, four public names (two enums + two models),
mirroring the Exon Deletion module shape.

### `StopLostOutcome(StrEnum)`
`NSD_PREDICTED`, `NO_NSD`.

### `StopLostInterference(StrEnum)`
The orange functional-of-similar-variants tier: `LOSS_OF_FUNCTION`, `SOME_INTERFERENCE`,
`NONE`.

### `StopLostPredictiveEvidence(BaseModel)` — `extra="forbid"`, all-optional
- `basis: str | None` — predictive basis (e.g. NSD predicted; extension length; interference)
- `initial_points: float | None` — initial PRD points before the SM 18 adjustment
- `nsd_predicted: bool | None` — no in-frame stop before the polyA site → NSD (the yellow
  gate)
- `similar_variant_interference: StopLostInterference | None` — the orange functional-data
  tier from similar variants (loss-of-function / some / none)
- `extension_length_aa: int | None` — predicted extension length in amino acids past the
  native stop (the ≥30 aa threshold for the orange +3.0/+2.0 tiers is derivable)
- `adjusted_points: float | None` — coded PRD points after the SM 18 adjustment

### `StopLostAssessment(BaseModel)` — `extra="forbid"`, all-optional
Field-parallel to `ExonDeletionAssessment`:

- `prediction_outcome: StopLostOutcome | None`
- `parent_code: PfdParentCode | None`
- `predictive: StopLostPredictiveEvidence | None`
- `mechanism_exon_relevance: MechanismExonRelevanceEvidence | None` (SM 18)
- `functional: FunctionalAssayEvidence | None` (SM 20)
- `informative: InformativeVariantsEvidence | None` (SM 19)
- `prd_points: float | None`
- `fxn_points: float | None`
- `inf_points: float | None`
- `prd_fxn_combined: float | None` — held PRD+FXN combined value (no distinct code)
- `parent_total: float | None`

## Conventions (identical to the nine prior PFD increments)

- Permissive superset: every field optional, defaults `None`.
- `model_config = ConfigDict(extra="forbid")`; `from __future__ import annotations`;
  `StrEnum`.
- Reuses `PfdParentCode` (NUL/CDS) + the SM 18/19/20 submodules.
- Standalone payload: **no `Workflow` enum entry, no `Case` applicability-matrix entry**.
- Two new committed JSON schemas (`StopLostAssessment`, `StopLostPredictiveEvidence`); the
  reused submodules + `PfdParentCode` + both StrEnums appear as `$defs`. StrEnums get no
  standalone schema file.
- Exported from the package root (sorted `__all__`); added to `docs/reference/model.md`
  (only the top-level `StopLostAssessment` `:::` block).

## Docs

- New page `docs/workflows/pfd/stop-lost.md` with a **two-branch Mermaid decision tree**
  (color-tinted per SM 16 path — yellow/orange — consistent with the Start-Lost / Exon
  Duplication pages), the branch table, the orange four-tier PRD scale, and the shared INF
  rules.
- `mkdocs.yml` nav: `- Stop Lost (NUL_/CDS_): workflows/pfd/stop-lost.md` after
  `start-lost.md`.
- `pfd/index.md` closing note: bump **Nine → Ten**, add the Stop-Lost sentence; and since
  this completes the variant-type workflows, adjust the closing "remaining variant-type
  workflows" phrasing to note only SM 7 + scoring remain.
- `spec-alignment.md` SM 16 row: `Not yet modeled` → Modeled inputs.
- `known-gaps.md` PFD row: add the Stop-Lost clause.

## Out of scope (documented, not modeled)

- Deletions of a large portion / the entirety of the last coding exon → In-Frame Deletion
  (SM 10) / Exon Deletion (SM 13).
- Frameshifts extending the ORF past the native stop → Frameshift (SM 9).
- The 3′-end / polyA-site determination tooling (analyst uses a genome browser / UCSC
  polyA track) — a prose note, not modeled.

## Testing (TDD)

`tests/test_stop_lost.py`, following the Exon Deletion / Start-Lost test shape and its
code-review lessons (exercise a non-default branch, populate reused submodules, cover both
parent codes):

- A maximal `NSD_PREDICTED` (`NUL_`) round-trip with populated `predictive` (all six
  fields, `similar_variant_interference=LOSS_OF_FUNCTION` — or an NSD-appropriate value),
  `mechanism_exon_relevance`, `functional`, and a real `InformativeVariant`, plus the held
  `prd_fxn_combined`.
- A `NO_NSD` (orange / `CDS_`) round-trip populating `similar_variant_interference` and
  `extension_length_aa`, `functional`, and the held `prd_fxn_combined`.
- Permissive-empty; `extra="forbid"` on both models; all `StopLostOutcome` (and, ideally,
  `StopLostInterference`) values round-trip; `parent_code` accepts NUL and CDS; importable
  from package root.

## Quality gates

`pytest`, `ruff check`, schema-drift gate (`git diff --quiet -- schemas/json
docs/workflows/case-model.md` → only the two new schema files added, nothing modified),
`mkdocs build --strict` (0 warnings; the Mermaid diagram renders client-side so `--strict`
does not validate its syntax — eyeball via a rendered preview; keep `<br/>` in node labels
only, never in edge labels), clean tree.
