# Start-Lost (`NUL_`/`CDS_`) workflow — design

**Date:** 2026-08-21
**Status:** Approved (design)
**Supplementary Material:** SM 15 (Start Lost Variants)
**Branch:** `feat/pfd-start-lost` (off `main`)
**Scope:** capture + document only — NO scoring computation (deferred to ClinGen CSpec)

## Goal

Model the SM 15 Start-Lost workflow as the **ninth** per-variant-type PFD increment: one
permissive, capture-only `StartLostAssessment` entity that routes a start-lost VBC down one
of three branches to a `NUL_` or `CDS_` parent code, reusing the shared `PfdParentCode` and
the SM 18/19/20 submodules. Structurally a close mirror of the three "start codon" branches
of Exon Deletion (SM 13), so it follows the `exon_deletion.py` module shape.

## The three branches

A start-lost VBC disrupts the initiator methionine (MET) codon. The first branch point has
three options keyed on the alternative start codon: none/blocked, potential-but-unproven, or
experimentally-proven-functional.

`StartLostOutcome` (StrEnum, three values):

| Branch (`prediction_outcome`) | SM 15 color | Alt-start | Parent | PRD initial |
|---|---|---|---|---|
| `NO_ALT_START` | yellow | none, or blocked by P/LP PTC variants | `NUL_` | `+6.0` |
| `ALT_START_UNPROVEN` | orange | potential, unproven | `CDS_` | `0.0 to +6.0` |
| `ALT_START_FUNCTIONAL` | violet | experimentally proven functional | `CDS_` | `−1.0` (no SM 18) |

Per-branch pipeline detail (all **documented, not computed**):

- **`NO_ALT_START` (yellow → `NUL_`):** used when there is no alternate in-frame MET, **or**
  a potential alt-MET exists but there are P/LP LoF variants introducing a PTC between the
  VBC and the alt-MET (good evidence rescue is unlikely; no fixed count — analyst judgment,
  variants robustly classified / 3–4★ ClinVar). Awards **+6.0** → SM 18 matrix
  (`NUL_PRD_0.0..+6.0`) → FXN (SM 20, must confirm transcript/protein loss,
  `NUL_FXN_-8.0..+8.0`, `NUL_FXN_ND` if none) → held `PRD+FXN` (no distinct code) → INF
  (SM 19; see the shared INF rules below; `NUL_INF_-8.0..+8.0`, `NUL_INF_ND` if none) →
  parent **`NUL_ −4.0..+10.0`**.
- **`ALT_START_UNPROVEN` (orange → `CDS_`):** a plausible alt-start, no P/LP PTC between the
  VBC and it, and no experimental functional data. Initial **0.0 to +6.0** from the fraction
  of protein deleted if the alt-start is used, or critical functional domains in the deleted
  segment (SM 7). → SM 18 matrix (same LoF logic as yellow; `CDS_PRD_0.0..+6.0`) → FXN
  (must confirm the amino-terminal truncation — distinct from the data proving alt-start
  usage; `CDS_FXN_-8.0..+8.0`, `CDS_FXN_ND` if none; held `PRD+FXN` capped `-8.0..+9.0`) →
  INF (`CDS_INF_-8.0..+8.0`, `CDS_INF_ND` if none) → parent **`CDS_ −4.0..+10.0`**.
- **`ALT_START_FUNCTIONAL` (violet → `CDS_`):** an in-vitro functional assay has shown the
  protein from the alternative start codon is functional, so a VBC upstream of it is highly
  likely benign. Awards **−1.0** and **skips** the SM 18 matrix (the mechanism/relevance
  considerations are already incorporated in the alt-start functional evaluation). FXN is
  **benignity-only** (`CDS_FXN_-8.0..0.0`, `CDS_FXN_ND` if none; pathogenic functional data
  → reconsider the path). INF is **benignity-only** (`CDS_INF_-8.0..0.0`, `CDS_INF_ND` if
  none; only B/LB at +1/+2/+3 or B/LB PTC upstream of the alt-start; any P/LP → reconsider
  the path) → parent **`CDS_ −8.0..0.0`**.

### Shared informative-variants (INF) rules (documented, not computed)

Across all three branches, informative variants are **limited to distinct variants at the
first, second, or third nucleotide of the MET codon** (positions +1/+2/+3): +2.0 first P /
+1.0 first LP or subsequent P/LP; same-MDE; pathogenicity only if similar-or-less-damaging
than the VBC, benignity only if similar-or-more-damaging. Two SM 15 specifics captured in
prose:

- **Benignity-only extra criterion:** a B/LB variant that introduces a PTC *after* the
  normal start but *upstream* of the putative alt-start counts for benignity (no
  pathogenicity equivalent — P/LP PTC variants there were already used in the yellow first
  step, so they are not re-counted as informative).
- **c.1A>C caveat:** because CTG can act as an initiator codon, a c.1A>C VBC does **not**
  inherit pathogenicity from P/LP variants at c.1A>T / c.1A>G or any +2/+3 P/LP variant.

## Entities

New module `src/svcv4_model/start_lost.py`, three public entities, mirroring the Exon
Deletion module shape.

### `StartLostOutcome(StrEnum)`
`NO_ALT_START`, `ALT_START_UNPROVEN`, `ALT_START_FUNCTIONAL`.

### `StartLostPredictiveEvidence(BaseModel)` — `extra="forbid"`, all-optional
The predictive (`_PRD`) step, capturing both first-branch decision axes plus the orange
fraction input:

- `basis: str | None` — predictive basis (e.g. no alt-start; % protein lost; proven alt-start)
- `initial_points: float | None` — initial PRD points before the SM 18 adjustment
- `alternative_start_present: bool | None` — a potential alternate in-frame MET exists
- `rescue_blocked_by_ptc: bool | None` — P/LP LoF variants introduce a PTC between the VBC
  and the alt-MET, making rescue unlikely (forces the yellow branch even when an alt-MET
  is present)
- `protein_fraction_lost: float | None` — fraction of protein deleted if the alt-start is
  used (the orange initial-points table)
- `alternative_start_functional: bool | None` — the alt-start is experimentally shown
  functional (the violet branch)
- `adjusted_points: float | None` — coded PRD points after the SM 18 adjustment

### `StartLostAssessment(BaseModel)` — `extra="forbid"`, all-optional
One entity for all three branches, parameterized by `prediction_outcome`; reuses the
SM 18/19/20 submodules and the shared `PfdParentCode` (NUL/CDS). Field-parallel to
`ExonDeletionAssessment`:

- `prediction_outcome: StartLostOutcome | None`
- `parent_code: PfdParentCode | None`
- `predictive: StartLostPredictiveEvidence | None`
- `mechanism_exon_relevance: MechanismExonRelevanceEvidence | None` (SM 18)
- `functional: FunctionalAssayEvidence | None` (SM 20)
- `informative: InformativeVariantsEvidence | None` (SM 19)
- `prd_points: float | None`
- `fxn_points: float | None`
- `inf_points: float | None`
- `prd_fxn_combined: float | None` — held PRD+FXN combined value (no distinct code)
- `parent_total: float | None`

## Conventions (identical to the eight prior PFD increments)

- Permissive superset: every field optional, defaults `None`.
- `model_config = ConfigDict(extra="forbid")`; `from __future__ import annotations`;
  `StrEnum`.
- Reuses `PfdParentCode` (NUL/CDS) + the SM 18/19/20 submodules.
- Standalone payload: **no `Workflow` enum entry, no `Case` applicability-matrix entry**.
- Two new committed JSON schemas (`StartLostAssessment`, `StartLostPredictiveEvidence`);
  the reused submodules + `PfdParentCode` + `StartLostOutcome` appear as `$defs`.
- Exported from the package root (sorted `__all__`); added to `docs/reference/model.md`
  (only the top-level `StartLostAssessment` `:::` block).

## Docs

- New page `docs/workflows/pfd/start-lost.md` with a **Mermaid decision-tree diagram**
  (three-branch, color-tinted per SM 15 path — yellow/orange/violet — consistent with the
  Exon Duplication page), the branch table, per-branch PRD/FXN/INF/parent caps (noting the
  **−4.0** parent floor on yellow/orange), the shared +1/+2/+3 INF restriction, the
  benignity-only extra criterion, and the c.1A>C caveat.
- `mkdocs.yml` nav: `- Start Lost (NUL_/CDS_): workflows/pfd/start-lost.md` after
  `exon-duplication.md`.
- `pfd/index.md` closing note: bump **Eight → Nine**, add the Start-Lost sentence.
- `spec-alignment.md` SM 15 row: `Not yet modeled` → Modeled inputs.
- `known-gaps.md` PFD row: add the Start-Lost clause.

## Out of scope (documented, not modeled)

- Gain-of-function effects (the workflow is LoF-framed).
- The SM 7 Determining Critical Amino Acids axis (the orange critical-domain criterion) —
  deferred, as in every prior PFD increment.

## Testing (TDD)

`tests/test_start_lost.py`, following the Exon Deletion / Exon Duplication test shape and
its code-review lesson (exercise a non-default branch, populate reused submodules, cover
both parent codes):

- A maximal `NO_ALT_START` (`NUL_`) round-trip with populated `predictive` (all seven
  fields), `mechanism_exon_relevance`, `functional`, and a real `InformativeVariant`.
- An `ALT_START_FUNCTIONAL` (violet / `CDS_`) round-trip: `alternative_start_functional=True`,
  `mechanism_exon_relevance=None` (SM-18-skipped), benignity-only negative FXN/INF/parent
  points, a B/LB `InformativeVariant`.
- Permissive-empty; `extra="forbid"` on both models; all three `prediction_outcome` values
  round-trip; `parent_code` accepts NUL and CDS; importable from package root.

## Quality gates

`pytest`, `ruff check`, schema-drift gate (`git diff --quiet -- schemas/json
docs/workflows/case-model.md` → only the two new schema files added, nothing modified),
`mkdocs build --strict` (0 warnings; the Mermaid diagram renders client-side so `--strict`
does not validate its syntax — eyeball via a rendered preview), clean tree.
