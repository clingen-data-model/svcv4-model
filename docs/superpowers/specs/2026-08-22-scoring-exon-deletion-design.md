# Reference scorer — Exon Deletion (SM 13) + mechanism-only SM 18 — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Parent scoping doc:** `2026-08-21-scoring-computation-scoping.md`
**Branch:** `feat/scoring-exon-deletion` (off `main`)
**Scope:** the fifth NUL_/CDS_ scorer, and the one generalization it needs (mechanism-only SM 18).

## Goal

Add `reference_score_exon_deletion` (SM 13, six branches) and the single generalization its
whole-gene branch requires: a **mechanism-only** mode for `apply_sm18_multiplier` (the
exon-relevance axis is removed for a whole-gene deletion). Every other Exon Deletion branch
fits the existing `BranchSpec` — the grey branch reuses the benignity-only ceilings introduced
for Start-Lost's violet. Non-authoritative; CSpec authoritative.

## The one new generalization: mechanism-only SM 18

SM 13's whole-gene branch awards `+10.0` then applies the SM 18 matrix **mechanism-only** —
the exon-relevance axis is removed because the VBC is the entire gene (exon relevance is
meaningless). The current `apply_sm18_multiplier` always multiplies mechanism × exon. Add a
keyword:

```python
def apply_sm18_multiplier(points, gencc_mechanism, exon_relevance, gene_disease_validity,
                          *, mechanism_only=False) -> float | None:
    if points is None or points <= 0:
        return points
    if gene_disease_validity not in _GDV_MODERATE_PLUS:
        return 0.0
    mech = _MECHANISM_FRACTION.get(gencc_mechanism, 0.0) if gencc_mechanism else 0.0
    if mechanism_only:
        return points * mech          # exon axis removed (whole-gene)
    exon = 1.0 if exon_relevance is None else _EXON_FRACTION.get(exon_relevance, 1.0)
    if gencc_mechanism == GenccMechanism.SUSPECTED and exon_relevance == ExonRelevance.MOST:
        fraction = 0.25
    else:
        fraction = mech * exon
    return points * fraction
```

`BranchSpec` gains `sm18_mechanism_only: bool = False`; the helper passes
`mechanism_only=branch.sm18_mechanism_only` in the PRD step. (Nonsense/Frameshift/Start-/Stop-Lost
all default to `False` — unchanged behaviour, guarded by their tests.)

The Suspected×Most special-case is only reachable in full mode (mechanism-only ignores exon),
so the flagged 0.25 assumption is untouched.

## `reference_score_exon_deletion` — `scoring/pfd/exon_deletion.py`

`ExonDeletionOutcome`: `WHOLE_GENE`, `SUBGENIC_NMD`, `SUBGENIC_NO_NMD`,
`START_CODON_NO_ALT_START`, `START_CODON_ALT_START_UNPROVEN`, `START_CODON_ALT_START_FUNCTIONAL`.
Branch table (verified vs `pfd/exon-deletion.md`):

| Branch | parent | PRD range | held_hi | parent caps | INF caps | SM 18 |
|---|---|---|---|---|---|---|
| `WHOLE_GENE` (yellow) | `NUL` | `0.0 .. +10.0` (initial +10) | `+10.0` | `−8 .. +10` | `−8 .. +8` | **mechanism-only** |
| `SUBGENIC_NMD` (orange) | `NUL` | `0.0 .. +6.0` (initial +6) | `+10.0` | `−8 .. +10` | `−8 .. +8` | full |
| `SUBGENIC_NO_NMD` (violet) | `CDS` | `0.0 .. +6.0` | `+9.0` | `−8 .. +10` | `−8 .. +8` | full |
| `START_CODON_NO_ALT_START` (green) | `NUL` | `0.0 .. +6.0` (initial +6) | `+10.0` | `−8 .. +10` | `−8 .. +8` | full |
| `START_CODON_ALT_START_UNPROVEN` (blue) | `CDS` | `0.0 .. +6.0` | `+9.0` | `−8 .. +10` | `−8 .. +8` | full |
| `START_CODON_ALT_START_FUNCTIONAL` (grey) | `CDS` | `−1.0 .. 0.0` | `0.0` | `−8 .. 0.0` | `−8 .. 0.0` | (PRD −1 → no-op) |

- **Held caps:** the three NUL_ branches (whole-gene, subgenic-NMD, start-codon-no-alt) hold
  `+10.0`; the two CDS_ non-grey (violet/blue) hold `+9.0`; grey holds `0.0` (benignity-only).
- **Grey** reuses the Start-Lost-violet pattern: PRD −1.0 (SM 18 no-op on negatives), held/
  parent/INF ceilings `0.0` (benignity-only). FXN stays consumed raw (grey's benignity-only FXN
  is the analyst's coded value; the `held_hi=0` clamps any positive FXN anyway).

As `BranchSpec` (only overrides shown; `sm18_mechanism_only` defaults False):

```python
_BRANCH = {
    WHOLE_GENE: BranchSpec("NUL", 0.0, 10.0, held_hi=10.0, sm18_mechanism_only=True),
    SUBGENIC_NMD: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    SUBGENIC_NO_NMD: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
    START_CODON_NO_ALT_START: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    START_CODON_ALT_START_UNPROVEN: BranchSpec("CDS", 0.0, 6.0, held_hi=9.0),
    START_CODON_ALT_START_FUNCTIONAL: BranchSpec("CDS", -1.0, 0.0, held_hi=0.0,
                                                 parent_hi=0.0, inf_hi=0.0),
}
```

`reference_score_exon_deletion(assessment, *, gene_disease_validity)`, exported from
`svcv4_model.scoring` (sorted `__all__`).

Informative-variant eligibility (a similarly-deleted region; whole-gene B/LB not counting for
benignity) is an analyst determination captured upstream — the scorer tallies the captured
list, as with every workflow.

## Tests (TDD)

`tests/test_exon_deletion_scoring.py`:
- Whole-gene maximal: initial +10, Established×All, → PRD +10, parent cap +10, `NUL`.
- **The mechanism-only proof:** whole-gene, `Suspected` mechanism + **`Few` exon relevance**,
  initial +10 → PRD `+2.5` (10 × 0.25, exon ignored). Full mode would give `0.0` (Few → ×0), so
  this proves the exon axis is removed. Add a sibling assertion that a *subgenic* (full-mode)
  branch with the same Suspected+Few → PRD `0.0`.
- Subgenic-NMD (`NUL`, held +10); violet held +9; grey (`CDS`, PRD −1.0, benign INF, parent in
  `[−8, 0]`, and a P-informative-variant clamped to 0 by `inf_hi=0`).
- Empty → all `_ND`.
- Unchanged nonsense/frameshift/start/stop tests guard the `apply_sm18_multiplier` +
  `BranchSpec` change (mechanism_only defaults False).

## Docs

`docs/reference/scoring.md`: add Exon Deletion (SM 13) to the list, noting the mechanism-only
SM 18 whole-gene case.

## Quality gates

`pytest`, `ruff`, drift gate (no schema), `mkdocs build --strict`, clean tree.

## Out of scope

Exon Duplication (SM 14 — needs the FXN-NA gain-path skip + whole-gene-NA outcome) is the
immediate next increment. Splice family; POP/LOC/CLN; aggregation; `validate_case`.
