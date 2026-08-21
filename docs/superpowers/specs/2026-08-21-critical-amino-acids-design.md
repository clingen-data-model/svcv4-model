# Determining Critical Amino Acids (SM 7) shared submodule — design

**Date:** 2026-08-21
**Status:** Approved (design)
**Supplementary Material:** SM 7 (Determining Critical Amino Acids)
**Branch:** `feat/pfd-critical-amino-acids` (off `main`)
**Scope:** capture + document only — NO scoring computation (deferred to ClinGen CSpec)

## Goal

Model SM 7 as the **fourth and final shared PFD submodule** (alongside SM 18 Mechanism &
Exon Relevance, SM 19 Informative Variants, SM 20 Functional Assays): a permissive,
capture-only `CriticalAminoAcidEvidence` payload that records an analyst's determination
that a VBC lies in a critical residue or domain, the small additional evidence (up to +2.0)
that may be added on top of the in-silico predictor, and the SM 7 gating conditions and
caution. Like the other shared submodules, it is a **standalone curation-level payload** —
no `Workflow` enum entry, no `Case` applicability-matrix entry, no new workflow page.

## Background — what SM 7 actually says

SM 7 is guidance, not a scored decision tree. Its structured content:

- **Critical domains:** because v4 substantially strengthened the in-silico predictors
  (which already capture much of what v3's PM1 "critical domain" code did), the WG **makes
  no specific point recommendation** for adding evidence when a VBC lies in a critical or
  conserved domain — doing so risks *double-counting* the predictor evidence. Experienced
  analysts **may** nonetheless add evidence if it is robustly supported. (Not every conserved
  domain is critical: immunoglobulin-like domains generally do not qualify; duplicated
  domains like the BRCT motif may tolerate disruption of one copy.)
- **Critical residues (individual amino acids):** some residues are critical to structure /
  function — e.g. the Glycine of the Gly-X-Y motif in triple-helical collagens; cysteines
  forming a Cys–Cys bridge (FBN1, NOTCH3); the cysteines/histidines of a C2H2 zinc finger
  (GLI3). (SM 7 prints "C2H4" here — an apparent source typo; the canonical GLI3 motif is
  C2H2.) For these, an analyst **may add up to +2.0 points** on top of the in-silico score,
  **only if**:
    1. the residue's involvement in protein function is **well-established**, **and**
    2. a maximum score has **not already been reached** through the combination of the
       predictive (`###_PRD_`) and informative (`###_INF_`) evidence.
- **Caution:** the analyst should avoid using this concept to push a variant to **+6.0 on
  prediction alone**, especially if the variant has **never been observed** in an individual
  affected with that MDE.

The additional evidence is added to whichever parent code's predictive step applies (most
commonly `MIS_PRD_`), so SM 7 has no parent code of its own.

## Entities

New module `src/svcv4_model/critical_amino_acid.py`, two public names (one enum + one
model), following the SM 18/19/20 standalone-payload pattern.

### `CriticalityKind(StrEnum)`
`CRITICAL_RESIDUE`, `CRITICAL_DOMAIN`.

### `CriticalAminoAcidEvidence(BaseModel)` — `extra="forbid"`, all-optional
Full field set (both gating conditions + the never-observed caution):

- `criticality_kind: CriticalityKind | None` — whether the VBC affects a critical single
  residue or a critical domain (the two are treated differently by SM 7)
- `motif_or_domain_name: str | None` — the named motif / domain / residue role (e.g.
  "Gly-X-Y triple-helix glycine", "C2H2 zinc-finger cysteine", "BRCT motif")
- `function_role_established: bool | None` — the residue's / domain's involvement in protein
  function is well-established (SM 7 gate 1 for the residue bump)
- `additional_points: float | None` — the additional evidence points added on top of the
  in-silico predictor (up to +2.0 for a critical residue; for a critical domain SM 7 makes
  no specific recommendation, so this is analyst discretion)
- `max_score_not_reached: bool | None` — the predictive (`_PRD_`) + informative (`_INF_`)
  combination has not already reached its maximum cap (SM 7 gate 2)
- `observed_in_affected: bool | None` — the variant has been observed in an individual
  affected with the MDE (the caution against reaching +6.0 on prediction alone for a
  never-observed variant)
- `double_counting_considered: bool | None` — the analyst has confirmed this addition does
  not double-count the in-silico predictor evidence (the central SM 7 concern)

All scoring — the +2.0 cap, the two gates, the +6.0 caution — is **documented in prose,
not computed**.

## Conventions (identical to the SM 18/19/20 shared submodules)

- Permissive superset: every field optional, defaults `None`.
- `model_config = ConfigDict(extra="forbid")`; `from __future__ import annotations`;
  `StrEnum`.
- Standalone payload: **no `Workflow` enum entry, no `Case` applicability-matrix entry**
  (`case-model.md` and the per-workflow `case/*` views untouched); no parent code.
- One new committed JSON schema (`CriticalAminoAcidEvidence`); `CriticalityKind` inlines as
  a `$def` (StrEnums get no standalone schema file). Note: unlike the variant-type
  workflows, this submodule adds **one** schema file, not two (there is no separate
  predictive-evidence class).
- Exported from the package root (sorted `__all__`); added to `docs/reference/model.md`
  (the `:::` block).

## Docs

Because SM 7 is a shared submodule (not a variant-type workflow), it is documented on the
**PFD index** alongside SM 18/19/20 — **not** a new page, and **no** Mermaid diagram / nav
entry.

- `docs/workflows/pfd/index.md`: add a `### Determining Critical Amino Acids ✅ modeled
  (inputs)` subsection (mirroring the SM 18/19/20 subsections), and flip the four-shared-
  submodules framing so Critical Amino Acids is no longer "the starting point / to come".
  Include a **compact Mermaid decision diagram** in this subsection — SM 7 has a genuine
  small decision flow (critical residue vs domain → the two residue gates → up to +2.0 /
  analyst-discretion for domains), so a diagram is useful here (unlike SM 18/19/20, which
  are matrices/calibration tables and get none). Keep `<br/>` in node labels only, never in
  edge labels (the established Mermaid lesson).
- `spec-alignment.md` SM 7 row: `Not yet modeled` → Modeled inputs.
- `known-gaps.md` PFD row: SM 7 is no longer outstanding — update "What remains" to name
  only the scoring computation (SM 7 is now modeled).
- `model.md`: append the `::: svcv4_model.CriticalAminoAcidEvidence` block.

(The many per-workflow "the criticality axis (SM 7) is deferred" notes on the individual
workflow pages are **left as-is** — they correctly describe that the *scoring* is deferred;
this increment models the *inputs*, consistent with every other submodule. A sweep of those
notes is out of scope for this increment.)

## Out of scope (documented, not modeled)

- The actual point computation / the +2.0 cap / the two gates / the +6.0 caution — prose
  only (capture + document).
- A structured catalog of known critical residues/domains — analyst free-texts the
  `motif_or_domain_name`; SM 7 explicitly declines to enumerate a complete list.

## Testing (TDD)

`tests/test_critical_amino_acid.py`, following the SM 18/19/20 submodule test shape:

- A maximal round-trip populating all seven fields (a `CRITICAL_RESIDUE` example — e.g. a
  Gly-X-Y glycine with `function_role_established=True`, `additional_points=2.0`,
  `max_score_not_reached=True`, `observed_in_affected=True`,
  `double_counting_considered=True`).
- A `CRITICAL_DOMAIN` round-trip (a documented critical functional domain,
  `additional_points=0.0` / analyst discretion — SM 7 makes no specific recommendation for
  domains). Deliberately not BRCT: SM 7 cites the BRCA1 BRCT motif as a *duplicated,
  disruption-tolerant* domain, i.e. the opposite of a clear-cut critical one.
- Permissive-empty; `extra="forbid"`; all `CriticalityKind` values round-trip; importable
  from package root.

## Quality gates

`pytest`, `ruff check`, schema-drift gate (`git diff --quiet -- schemas/json
docs/workflows/case-model.md` → only the **one** new schema file added, nothing modified),
`mkdocs build --strict` (0 warnings), clean tree.
