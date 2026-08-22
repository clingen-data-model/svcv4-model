# Reference scorer — Start-Lost (SM 15) + Stop-Lost (SM 16) + BranchSpec generalization — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Parent scoping doc:** `2026-08-21-scoring-computation-scoping.md`
**Branch:** `feat/scoring-start-stop-lost` (off `main`)
**Scope:** two more NUL_/CDS_ scorers, and the generalization Start-Lost forces (per-branch
parent + INF caps).

## Goal

Add `reference_score_start_lost` (SM 15, 3 branches) and `reference_score_stop_lost`
(SM 16, 2 branches), and generalize the shared `score_nul_cds_workflow` so a branch can carry
**per-branch parent and INF caps** — which Start-Lost requires and the current
`(parent_code, prd_lo, prd_hi, held_hi)` tuple cannot express. Non-authoritative; CSpec
authoritative.

## Why the tuple must become a `BranchSpec`

The Nonsense/Frameshift scorers held two things constant that Start-Lost does not:

- **Parent floor.** Nonsense/Frameshift/Stop-Lost all cap the parent total at `−8.0 .. +10.0`.
  **Start-Lost's yellow and orange branches floor at `−4.0`** (not −8), and its **violet branch
  caps at `−8.0 .. 0.0`** (ceiling 0, benignity-only). The floor bites only when the positive
  held (PRD+FXN) is small: e.g. a yellow Start-Lost with **no positive predictive/functional
  evidence** and a strongly-benign INF of `−6.0` must clamp to `−4.0`, where the shared `−8.0`
  floor would wrongly leave it at `−6.0`. (With yellow's canonical PRD `+6.0`, both floors give
  the same result — the change only shows up once held is low.) This is a real fidelity gap the
  4-tuple cannot fix.
- **INF ceiling.** Start-Lost's **violet** branch is benignity-only: INF `−8.0 .. 0.0`. The
  shared `−8.0 .. +8.0` INF cap only matches when the analyst captured B/LB-only variants;
  to be faithful the ceiling must be per-branch.

So the branch descriptor becomes a small frozen dataclass with defaults, overriding only where
a workflow differs. **FXN stays consumed-raw** (no cap) — the analyst's coded value is trusted,
as in every prior increment; violet's benignity-only FXN constraint is the analyst's
responsibility, not the scorer's. (The SM 18 "no multiplier" on violet is already automatic:
violet's PRD initial is `−1.0`, which the positive-only multiplier passes through unchanged.)

```python
@dataclass(frozen=True)
class BranchSpec:
    parent_code: str          # "NUL" / "CDS"
    prd_lo: float
    prd_hi: float
    held_hi: float = 9.0       # held PRD+FXN ceiling (held floor is the shared -8.0)
    parent_lo: float = -8.0
    parent_hi: float = 10.0
    inf_lo: float = -8.0
    inf_hi: float = 8.0
```

`branch_table` becomes `Mapping[object, BranchSpec]`. The helper reads `spec.parent_code`,
caps PRD to `[spec.prd_lo, spec.prd_hi]`, held to `[_HELD_LO, spec.held_hi]`, INF to
`[spec.inf_lo, spec.inf_hi]`, and the parent total to `[spec.parent_lo, spec.parent_hi]`. The
`branch is None` fallback (unknown outcome) keeps today's defaults (`held_hi 9.0`, parent
`−8..+10`, INF `−8..+8`).

## Behaviour-preserving refactor of Nonsense + Frameshift

Both branch tables convert tuple → `BranchSpec`, defaulting the new fields so behaviour is
**identical** (their unchanged tests are the guard):

- Nonsense: `NMD_NO_RESCUE = BranchSpec("NUL", 0.0, 6.0, held_hi=10.0)`;
  `NMD_WITH_RESCUE = BranchSpec("CDS", -1.0, 6.0, held_hi=9.0)`;
  `NO_NMD = BranchSpec("CDS", 0.0, 6.0, held_hi=9.0)`. (parent/INF caps default to −8..+10 /
  −8..+8 — unchanged.)
- Frameshift: the five branches likewise, `held_hi=10.0` for yellow, `9.0` for the other four;
  NSD `BranchSpec("NUL", 0.0, 4.0, held_hi=9.0)`, extension `BranchSpec("CDS", 0.0, 4.0,
  held_hi=9.0)`.

## `reference_score_start_lost` — `scoring/pfd/start_lost.py`

`StartLostOutcome`: `NO_ALT_START`, `ALT_START_UNPROVEN`, `ALT_START_FUNCTIONAL`. Branch table
(verified vs `pfd/start-lost.md`):

| Branch | parent | PRD range | held_hi | parent caps | INF caps |
|---|---|---|---|---|---|
| `NO_ALT_START` (yellow) | `NUL` | `0.0 .. +6.0` | `+10.0` (no separate held cap → parent ceiling) | **`−4.0 .. +10.0`** | `−8.0 .. +8.0` |
| `ALT_START_UNPROVEN` (orange) | `CDS` | `0.0 .. +6.0` | `+9.0` | **`−4.0 .. +10.0`** | `−8.0 .. +8.0` |
| `ALT_START_FUNCTIONAL` (violet) | `CDS` | `−1.0 .. 0.0` | `0.0` | **`−8.0 .. 0.0`** | **`−8.0 .. 0.0`** |

- Yellow SM 15 gives no explicit held cap → use the parent ceiling `+10.0` (the held step adds
  no extra constraint, exactly as Nonsense/Frameshift yellow).
- Violet PRD initial is `−1.0` (SM 18 no-ops on negatives); `prd_lo=-1.0, prd_hi=0.0` keeps it
  at −1.0. Violet held ceiling `0.0` and INF ceiling `0.0` (benignity-only).

Informative-variant position eligibility (+1/+2/+3 MET positions) and the c.1A>C caveat are
analyst determinations captured upstream — the scorer tallies the captured list (as with every
workflow), not those eligibility rules.

## `reference_score_stop_lost` — `scoring/pfd/stop_lost.py`

`StopLostOutcome`: `NSD_PREDICTED`, `NO_NSD`. Fits the defaults (parent `−8..+10`, INF
`−8..+8`); only PRD range and held cap set:

| Branch | parent | PRD range | held_hi |
|---|---|---|---|
| `NSD_PREDICTED` (yellow) | `NUL` | `0.0 .. +4.0` | `+9.0` |
| `NO_NSD` (orange) | `CDS` | `0.0 .. +4.0` | `+9.0` |

Both parent totals `−8..+10`, held `−8..+9`, full SM 18, FXN consumed raw. The orange four-tier
interference/extension PRD scale (+4/+3/+2/0) is analyst-applied → captured as `initial_points`;
the scorer does not recompute it.

Both scorers are `reference_score_<x>(assessment, *, gene_disease_validity)` and are exported
from `svcv4_model.scoring` (sorted `__all__`).

## Tests (TDD)

- `tests/test_start_lost_scoring.py`: yellow maximal (PRD +6, parent cap +10); **the −4 floor**
  — a yellow branch with **`predictive=None`** (PRD `_ND` → held `None`, so no positive held)
  and a benign INF of `−6.0` (five B variants: −2 + 4×−1) → `parent_total == -4.0`; the shared
  −8 floor would give −6.0, so this proves the per-branch floor. (With PRD +6 present, the floor
  cannot bite — the minimum reachable is −2 — so PRD must be suppressed for this test.) Then
  orange held cap +9; violet (`parent_code == "CDS"`, PRD −1.0, benign INF, parent capped to
  `[−8, 0]`, INF ceiling 0); empty → all `_ND`.
- `tests/test_stop_lost_scoring.py`: yellow (PRD +4, `NUL`, held +9); orange (`CDS`, held +9);
  empty → `_ND`.
- Unchanged `tests/test_nonsense_scoring.py` + `tests/test_frameshift_scoring.py` guard the
  BranchSpec refactor.

## Docs

`docs/reference/scoring.md`: add Start-Lost (SM 15) and Stop-Lost (SM 16) to the "What is
modeled so far" list, noting the `BranchSpec` per-branch caps.

## Quality gates

`pytest`, `ruff`, drift gate (**no schema** — scoring still absent from the root `__all__`),
`mkdocs build --strict`, clean tree.

## Out of scope

Exon Deletion (needs mechanism-only SM 18 for whole-gene) and Exon Duplication (FXN-NA gain
paths + whole-gene NA) — their extra generalizations are deferred to their own increments. The
splice family; POP/LOC/CLN; aggregation; `validate_case`. The SM 18 Figure-1 Suspected×Most
0.25 assumption is unchanged.
