# Reference scorer — Exon Duplication (SM 14) + FXN-NA + whole-gene-NA — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Parent scoping doc:** `2026-08-21-scoring-computation-scoping.md`
**Branch:** `feat/scoring-exon-duplication` (off `main`)
**Scope:** the sixth and final NUL_/CDS_ scorer, and the two generalizations it needs.

## Goal

Add `reference_score_exon_duplication` (SM 14, six scored branches + a whole-gene-NA outcome)
and the two generalizations it requires: a **FXN-NA** per-branch flag (the gain paths do not
consider functional data) and a **WHOLE_GENE_NA** all-NA short-circuit. This completes the
NUL_/CDS_ scorer family. Non-authoritative; CSpec authoritative.

## Two new generalizations

### 1. FXN-NA (gain paths skip the FXN step)

SM 14's gain paths (blue `GAIN_NMD`, violet `GAIN_NO_NMD`, green `GAIN_TERMINAL_EXON`) code
functional data as **`*_FXN_NA`** — functional is *not considered* (these genomic consequences
are unique per occurrence, rarely assayed). So the pipeline is PRD → (no FXN) → INF → parent,
with no held PRD+FXN combine. Add `BranchSpec.fxn_na: bool = False`; the helper, when
`branch.fxn_na`, does not consume `fxn_points`, records `FXN: NA` in provenance, carries PRD
straight forward as the pre-INF value (`held_val = prd`), and records **no** `held_combined`
entry.

Helper FXN step becomes:

```python
    if branch is not None and branch.fxn_na:
        prov.append("FXN: NA (functional not considered on this gain path)")
        held_val = prd                      # no PRD+FXN combine when FXN is NA
    else:
        fxn = assessment.fxn_points
        if fxn is None:
            prov.append("FXN: _ND (no coded fxn_points captured; OddsPath not recomputed)")
        else:
            sub["FXN"] = fxn
            prov.append(f"FXN: consumed coded value {fxn}")
        held_hi = branch.held_hi if branch else _DEFAULT_HELD_HI
        held_val = hold_combined(prd, fxn, lo=_HELD_LO, hi=held_hi)
        if held_val is not None:
            held["PRD+FXN"] = held_val
```

Behaviour-preserving: every existing scorer has `fxn_na=False`, so the `else` branch (today's
exact logic) runs unchanged.

### 2. WHOLE_GENE_NA all-NA outcome

SM 14's whole-gene duplication is coded `CDS_NA` (all of `CDS_PRD_NA`, `CDS_FXN_NA`,
`CDS_INF_NA`) — evaluated, determined not applicable (few genes have triplosensitivity). Handle
it in the `exon_duplication.py` wrapper, **before** delegating:

```python
    if assessment.prediction_outcome == ExonDuplicationOutcome.WHOLE_GENE_NA:
        return ScoreResult(
            parent_code="CDS",
            parent_total=None,
            provenance=["WHOLE_GENE_NA: CDS_NA (evaluated, determined not applicable)"],
            authoritative=False,
        )
```

(It is deliberately **not** in the branch table — the wrapper gives the correct `CDS` parent
code and an explicit NA provenance, rather than the helper's generic unknown-outcome `_ND`.)

## `reference_score_exon_duplication` — `scoring/pfd/exon_duplication.py`

`ExonDuplicationOutcome`: `TANDEM_NMD`, `TANDEM_NO_NMD`, `TANDEM_TERMINAL_EXON`, `GAIN_NMD`,
`GAIN_NO_NMD`, `GAIN_TERMINAL_EXON`, `WHOLE_GENE_NA`. Branch table (verified vs
`pfd/exon-duplication.md`):

| Branch | parent | PRD range | FXN | held_hi | parent caps | INF caps |
|---|---|---|---|---|---|---|
| `TANDEM_NMD` (yellow) | `NUL` | `0.0 .. +6.0` | SM 20 | `+10.0` | `−8 .. +10` | `−8 .. +8` |
| `TANDEM_NO_NMD` (upper orange) | `CDS` | `0.0 .. +3.0` | SM 20 | `+9.0` | `−8 .. +10` | `−8 .. +8` |
| `TANDEM_TERMINAL_EXON` (lower orange) | `CDS` | `0.0` (no SM 18) | SM 20 | `+9.0` | `−8 .. +10` | `−8 .. +8` |
| `GAIN_NMD` (blue) | `NUL` | `0.0 .. +4.0` | **NA** | (n/a) | **`−1 .. +6`** | **`−8 .. +6`** |
| `GAIN_NO_NMD` (violet) | `CDS` | `0.0 .. +2.0` | **NA** | (n/a) | **`−1 .. +6`** | **`−8 .. +6`** |
| `GAIN_TERMINAL_EXON` (green) | `CDS` | `0.0` (no SM 18) | **NA** | (n/a) | **`−8 .. 0.0`** | **`−8 .. 0.0`** |
| `WHOLE_GENE_NA` | `CDS` | NA | NA | — | NA (wrapper) | NA |

Notes:
- **Lower-orange** PRD is fixed `0.0` (SM 18 no-ops on 0); its FXN+INF merge with upper-orange
  and its parent follows the upper-orange coding (`CDS_ −8..+10`); held `+9` (never binds since
  PRD 0 + FXN ≤ +8).
- **Gain paths** (blue/violet/green) set `fxn_na=True`. Blue/violet parent `−1..+6`
  (`parent_lo=-1, parent_hi=6`), INF `−8..+6` (`inf_hi=6`). Green is benignity-only
  (`parent_hi=0, inf_hi=0`), PRD fixed 0.
- FXN, on the tandem paths, is consumed raw (as always).

As `BranchSpec` (only overrides shown; `fxn_na`/`sm18_mechanism_only` default False):

```python
_BRANCH = {
    TANDEM_NMD: BranchSpec("NUL", 0.0, 6.0, held_hi=10.0),
    TANDEM_NO_NMD: BranchSpec("CDS", 0.0, 3.0, held_hi=9.0),
    TANDEM_TERMINAL_EXON: BranchSpec("CDS", 0.0, 0.0, held_hi=9.0),
    GAIN_NMD: BranchSpec("NUL", 0.0, 4.0, fxn_na=True, parent_lo=-1.0, parent_hi=6.0, inf_hi=6.0),
    GAIN_NO_NMD: BranchSpec("CDS", 0.0, 2.0, fxn_na=True, parent_lo=-1.0, parent_hi=6.0, inf_hi=6.0),
    GAIN_TERMINAL_EXON: BranchSpec("CDS", 0.0, 0.0, fxn_na=True, parent_hi=0.0, inf_hi=0.0),
    # WHOLE_GENE_NA handled in the wrapper (all NA)
}
```

`reference_score_exon_duplication(assessment, *, gene_disease_validity)`, exported from
`svcv4_model.scoring` (sorted `__all__` — `exon_deletion` < `exon_duplication` < `frameshift`).

## Tests (TDD)

`tests/test_exon_duplication_scoring.py`:
- Tandem yellow maximal (PRD +6, FXN consumed, held +10, `NUL`).
- Upper-orange held +9 (`CDS`).
- **Gain FXN-NA proof:** a blue `GAIN_NMD` with `fxn_points=8.0` set → FXN is **ignored**
  (`"FXN" not in sub_code_points`, no `held_combined`), and the +8 does not inflate the total;
  parent = PRD (+4) + INF, capped `[−1, +6]`. Assert a benign INF floors the parent at `−1.0`
  (PRD suppressed) — proving `parent_lo=-1`.
- Gain INF ceiling `+6`: blue with a large positive INF clamps to +6 in `[−1,+6]`... (parent
  ceiling +6); and the INF sub-code clamps to +6 via `inf_hi=6`.
- Green (`GAIN_TERMINAL_EXON`): FXN-NA, benignity-only (a P informative clamped to 0 by
  `inf_hi=0`, parent in `[−8, 0]`).
- **WHOLE_GENE_NA:** `parent_code == "CDS"`, `parent_total is None`, `sub_code_points == {}`,
  provenance mentions NA.
- All-seven-outcomes loop (scores without error).
- Empty → all `_ND`.
- Unchanged existing scoring tests guard the `fxn_na` helper change (default False).

## Docs

`docs/reference/scoring.md`: add Exon Duplication (SM 14) — noting the FXN-NA gain paths and the
whole-gene-NA outcome; and that **all six NUL_/CDS_ scorers are now modeled**.

## Quality gates

`pytest`, `ruff`, drift gate (no schema), `mkdocs build --strict`, clean tree.

## Out of scope

The splice family (SPL_SPA primitive + MIS_-vs-SPL_ take-higher); POP/LOC/CLN; aggregation;
`validate_case`.
