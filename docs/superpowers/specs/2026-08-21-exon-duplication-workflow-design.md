# Single/Multi-Exon Duplication/Gain (`NUL_`/`CDS_`) workflow — design

**Date:** 2026-08-21
**Status:** Approved (design)
**Supplementary Material:** SM 14 (Single or Multiexon Duplication/Gain Variants)
**Branch:** `feat/pfd-exon-duplication` (off `main`)
**Scope:** capture + document only — NO scoring computation (deferred to ClinGen CSpec)

## Goal

Model the SM 14 Single/Multi-Exon Duplication/Gain workflow as the **eighth**
per-variant-type PFD increment: one permissive, capture-only `ExonDuplicationAssessment`
entity that routes a duplication/gain VBC down one of six scored branches (plus a
documented whole-gene NA outcome) to a `NUL_` or `CDS_` parent code, reusing the
shared `PfdParentCode` and the SM 18/19/20 submodules. Mirrors the shape of
`exon_deletion.py` / `nonsense.py` / `frameshift.py`.

## Background — what SM 14 adds over Exon Deletion (SM 13)

SM 14 is the most branched variant workflow so far because it carries a **new axis**:
whether the duplication is **molecularly proven to be tandem** (a "duplication") or is
an **unproven copy-number gain** (a "gain"). Tandem-proven variants accrue more points
than gains (only ~80% of subgenic gains are actually tandem, which sits in the VUS-High
posterior range). Each of the tandem/gain groups then splits on NMD-predicted and on
whether the variant includes a terminal (first/last) exon/UTR.

Two further differences from Exon Deletion:

- The **not-tandem "gain" paths do not consider functional data** — functional is
  explicitly `_FXN_NA` (genomic consequences are unique per occurrence, rarely assayed).
- **Whole-gene duplication is `NA`, not scored** — few genes have documented
  triplosensitivity, so whole-gene dup is awarded `CDS_PRD_NA … CDS_NA` and deferred to
  the CNV recommendations. (Contrast Exon Deletion, where whole-gene was a scored `+10`
  branch.)

## The six scored branches + whole-gene NA

`ExonDuplicationOutcome` (StrEnum, seven values):

| Branch (`prediction_outcome`) | SM 14 color | Tandem? | NMD? | Terminal exon/UTR? | Parent | PRD initial |
|---|---|---|---|---|---|---|
| `TANDEM_NMD` | yellow | proven | yes | no | `NUL_` | `+6.0` |
| `TANDEM_NO_NMD` | upper orange | proven | no (in-frame elongation) | no | `CDS_` | `0.0 to +3.0` |
| `TANDEM_TERMINAL_EXON` | lower orange | proven | — | yes | `CDS_` | `0.0` (PRD follows green; no SM 18) |
| `GAIN_NMD` | blue | not proven | yes | no | `NUL_` | `+4.0` |
| `GAIN_NO_NMD` | violet | not proven | no | no | `CDS_` | `0.0 to +2.0` |
| `GAIN_TERMINAL_EXON` | green | not proven | — | yes | `CDS_` | `0.0` (no SM 18) |
| `WHOLE_GENE_NA` | — | — | — | — | `CDS_` | `NA` (documented not-applicable) |

Per-branch pipeline detail (all **documented, not computed**):

- **`TANDEM_NMD` (yellow → `NUL_`):** `+6.0` initial → SM 18 matrix (`NUL_PRD_0.0..+6.0`)
  → FXN (SM 20, must confirm transcript/protein loss, `NUL_FXN_-8.0..+8.0`) → held
  `PRD+FXN` (`-8.0..+10.0`, no distinct code) → INF (SM 19; P/LP dup overlapping VBC
  exons, size ≤ VBC ORF; B/LB similarly duplicated region; `NUL_INF_-8.0..+8.0`) →
  parent `NUL_ -8.0..+10.0`.
- **`TANDEM_NO_NMD` (upper orange → `CDS_`):** initial `0.0..+3.0` keyed on fraction of
  ORF duplicated (>50% → `+3.0`; <10% → `0.0`) **or** the criticality of the duplicated
  amino acids (critical disease-relevant domain → `+3.0`) → SM 18 matrix → FXN
  (confirming protein elongation, `CDS_FXN_-8.0..+8.0`) → held `PRD+FXN` (`-8.0..+9.0`)
  → INF (P/LP same-or-less-damaging → pathogenic; B/LB same-or-more-damaging → benign;
  +2.0 first P / +1.0 first LP / +1.0 each additional; `CDS_INF_-8.0..+8.0`) → parent
  `CDS_ -8.0..+10.0`.
- **`TANDEM_TERMINAL_EXON` (lower orange → `CDS_`):** predictive **follows the green-path
  logic** (unlikely to be LoF → no initial points awarded, SM 18 matrix not applicable);
  FXN and INF **merge with the upper-orange path** (same treatment). Parent `CDS_`.
- **`GAIN_NMD` (blue → `NUL_`):** `+4.0` initial (lower than tandem `+6.0` for the ~80%
  uncertainty) → SM 18 matrix (`NUL_PRD_0.0..+4.0`) → **FXN not considered → `NUL_FXN_NA`**
  → INF (P/LP dup of same exons *confirmed tandem in prior cases*; B/LB likewise;
  `NUL_INF_-8.0..+6.0`) → parent `NUL_ -1.0..+6.0`.
- **`GAIN_NO_NMD` (violet → `CDS_`):** `0.0..+2.0` initial (>50% protein disruption /
  entire critical domain → `+2.0`; <10% or unknown role → `0.0`; low confidence → `0.0`)
  → SM 18 matrix (`CDS_PRD_0.0..+2.0`) → **FXN `CDS_FXN_NA`** → INF (`CDS_INF_-8.0..+6.0`)
  → parent `CDS_ -1.0..+6.0`.
- **`GAIN_TERMINAL_EXON` (green → `CDS_`):** no initial points (SM 18 not applicable) →
  **FXN `CDS_FXN_NA`** → INF **benignity-only** (`-2.0` first B / `-1.0` first LB /
  `-1.0` each additional; if any P/LP informative variant exists the analyst should
  reconsider the pathway) → parent `CDS_ -8.0..0.0`.
- **`WHOLE_GENE_NA` (→ `CDS_`):** all steps `NA` — `CDS_PRD_NA`, `CDS_FXN_NA`,
  `CDS_INF_NA`, `CDS_NA` — recorded to document that the recommendations were evaluated
  and found not applicable; classification deferred to CNV recommendations / expert.

## Entities

New module `src/svcv4_model/exon_duplication.py`, three public entities, mirroring the
Exon Deletion module exactly in shape.

### `ExonDuplicationOutcome(StrEnum)`
The seven values above.

### `ExonDuplicationPredictiveEvidence(BaseModel)` — `extra="forbid"`, all-optional
The predictive (`_PRD`) step, capturing all three decision-tree axes plus both
alternative predictive criteria:

- `basis: str | None` — predictive basis (e.g. tandem NMD; % ORF duplicated; critical domain)
- `initial_points: float | None` — initial PRD points before the SM 18 adjustment
- `molecularly_tandem: bool | None` — the VBC is molecularly proven tandem (vs an
  unproven gain); the axis that separates the yellow/upper-orange/lower-orange group
  from the blue/violet/green group
- `nmd_predicted: bool | None` — an introduced PTC > 50 bp upstream of the last
  exon-intron boundary predicts NMD
- `includes_terminal_exon_or_utr: bool | None` — the duplication includes the first
  exon, last exon, or either UTR (the terminal-exon branches)
- `orf_fraction_duplicated: float | None` — fraction of the ORF duplicated (the
  >50%→full / <10%→zero table for the upper-orange and violet branches)
- `duplicated_domain_critical: bool | None` — the duplicated amino acids alter a region
  with a proven critical role in disease-relevant protein function (the alternative
  criticality criterion)
- `adjusted_points: float | None` — coded PRD points after the SM 18 adjustment

### `ExonDuplicationAssessment(BaseModel)` — `extra="forbid"`, all-optional
One entity for all seven branches, parameterized by `prediction_outcome`; reuses the
SM 18/19/20 submodules and the shared `PfdParentCode` (NUL/CDS). Field-parallel to
`ExonDeletionAssessment`:

- `prediction_outcome: ExonDuplicationOutcome | None`
- `parent_code: PfdParentCode | None`
- `predictive: ExonDuplicationPredictiveEvidence | None`
- `mechanism_exon_relevance: MechanismExonRelevanceEvidence | None` (SM 18)
- `functional: FunctionalAssayEvidence | None` (SM 20; left `None` on the FXN-NA paths)
- `informative: InformativeVariantsEvidence | None` (SM 19)
- `prd_points: float | None`
- `fxn_points: float | None`
- `inf_points: float | None`
- `prd_fxn_combined: float | None` — held PRD+FXN combined value (no distinct code;
  only meaningful on the two tandem-with-FXN branches)
- `parent_total: float | None`

## Conventions (identical to the seven prior PFD increments)

- Permissive superset: every field optional, defaults `None`.
- `model_config = ConfigDict(extra="forbid")`; `from __future__ import annotations`;
  `StrEnum`.
- Reuses `PfdParentCode` (NUL/CDS) + `MechanismExonRelevanceEvidence` /
  `FunctionalAssayEvidence` / `InformativeVariantsEvidence`.
- Standalone payload: **no `Workflow` enum entry, no `Case` applicability-matrix entry**
  (`case-model.md` and the per-workflow `case/*` views untouched).
- Two new committed JSON schemas (`ExonDuplicationAssessment`,
  `ExonDuplicationPredictiveEvidence`); the reused submodules + `PfdParentCode` +
  `ExonDuplicationOutcome` appear as `$defs`. StrEnums get no standalone schema file.
- Exported from the package root (sorted `__all__`); added to `docs/reference/model.md`
  (only the top-level `ExonDuplicationAssessment` `:::` block, per the established
  model.md pattern).

## Docs

- New page `docs/workflows/pfd/exon-duplication.md`: the seven-branch table, the
  tandem-vs-gain axis, per-branch PRD/FXN/INF/parent caps, the three FXN-NA gain paths,
  the green benignity-only INF, the whole-gene NA outcome, and the out-of-scope escapes
  (multi-gene dup → CNV recs; within-single-exon dup → In-Frame InDel SM 10).
- `mkdocs.yml` nav: `- Exon Duplication (NUL_/CDS_): workflows/pfd/exon-duplication.md`
  after `exon-deletion.md`.
- `pfd/index.md` closing note: bump **Seven → Eight**, add the Exon Duplication sentence.
- `spec-alignment.md` SM 14 row: `Not yet modeled` → Modeled inputs.
- `known-gaps.md` PFD row: add the Exon Duplication clause.

## Out of scope (documented on the page, not modeled)

- **Multi-gene duplication** → CNV recommendations (PMID 31690835).
- **Duplication beginning and ending within a single exon** → In-Frame InDel (SM 10).
- **Whole-gene duplication** → recorded as the `WHOLE_GENE_NA` outcome; classification
  deferred to CNV recs / expert (few genes have curated triplosensitivity).
- Analytic-validity PPV adjustments (labs calibrate their platform; recommendation is to
  adjust points downward toward 0.0 for low-PPV detection) — prose note only.

## Testing (TDD)

`tests/test_exon_duplication.py`, following the Exon Deletion test shape and its
code-review lesson (exercise a non-default branch, populate reused submodules):

- A maximal `TANDEM_NMD` (`NUL_`) round-trip with populated `predictive` (all eight
  fields), `mechanism_exon_relevance`, `functional`, and a real `InformativeVariant`.
- A `GAIN_TERMINAL_EXON` (green / `CDS_`) round-trip: FXN left `None` (FXN-NA path),
  benignity-only negative INF/parent points, `molecularly_tandem=False`,
  `includes_terminal_exon_or_utr=True`.
- Permissive-empty; `extra="forbid"` on both models; all seven `prediction_outcome`
  values round-trip; `parent_code` accepts NUL and CDS; importable from package root.

## Quality gates

`pytest`, `ruff check`, schema-drift gate (`git diff --quiet -- schemas/json
docs/workflows/case-model.md` → only the two new schema files added, nothing modified),
`mkdocs build --strict` (0 warnings), clean tree.
