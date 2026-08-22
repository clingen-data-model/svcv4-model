# Reference scorer — Missense splice path + MIS_-vs-SPL_ take-higher (SM 6) — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-missense-splice-compare` (off `main`)
**Scope:** Increment C2 — the **last** splice-family piece. Completes Missense (SM 6) and the
whole splice family.

## Goal

Add (1) `reference_score_missense_splice` (the SM 6 splice path — a `score_spl_workflow` branch
table, reusing the Inc-A helper unchanged), (2) a `MissenseScoreResult` DTO, and (3)
`reference_score_missense` — the top-level **MIS_-vs-SPL_ take-higher** that scores both paths and
selects one. Non-authoritative; CSpec authoritative.

## Part 1 — `reference_score_missense_splice` — `scoring/pfd/missense_splice.py`

`MissenseSpliceAssessment` is field-identical to the other splice assessments, so this is a new
`SplBranchSpec` table + a one-line delegation to `score_spl_workflow` (needs
`gene_disease_validity` — the splice PRD uses SM 18). Branch table (verified vs SM 6):

| Path | PRD | held prd_spa | held prd_spa_fxn | INF | parent |
|---|---|---|---|---|---|
| `NMD_PREDICTED` (yellow) | `0.0..+3.0` | **`0.0..+6.0`** | `−8..+9` | `−8..+8` | `−8..+10` |
| `FRAMESHIFT_NO_NMD` (upper orange) | `−1.0..+3.0` | **`0.0..+6.0`** | `−8..+9` | `−8..+8` | `−8..+10` |
| `SPLICE_NO_FRAMESHIFT` (lower orange) | `−1.0..+3.0` | **`0.0..+6.0`** | `−8..+9` | `−8..+8` | `−8..+10` |
| `UNCERTAIN` (blue) | `0.0..0.0` | **`−2.0..+2.0`** | `−8..+9` | `−8..+8` | **`−8..0.0`** |
| `UNLIKELY` (violet) | `−1.0..0.0` | **`−3.0..0.0`** | `−8..+9` | **`−8..0.0`** | **`−8..+8.0`** |

### ⚠️ The SM 6 blue/violet parent-cap oddity (flagged, encoded faithfully)

SM 6's missense-splice parent caps are the **opposite** of Canonical (SM 11) / Intronic
(SM 12): **blue `UNCERTAIN` → `−8..0`** (L132) and **violet `UNLIKELY` → `−8..+8`** (L155). This
looks semantically backwards (an *uncertain* variant capped at 0; an *unlikely* one allowed to
+8 — reachable via functional data, since violet INF is B/LB-only). It reads like a possible
SM 6 typo, **but the already-merged `docs/workflows/pfd/missense.md` encodes it faithfully** and
the reference scorer's job is to mirror the *documented* rules. **Decision:** encode to match
SM 6 + `missense.md`, add a `provenance` note flagging the suspected inconsistency, and surface
it to the WG (same posture as the SM 18 Figure-1 open item). Not "corrected" here.

As `SplBranchSpec` (`_ORANGE` shared for the two identical orange paths):

```python
_ORANGE = SplBranchSpec(-1.0, 3.0, prd_spa_lo=0.0, prd_spa_hi=6.0)
_BRANCH = {
    NMD_PREDICTED: SplBranchSpec(0.0, 3.0, prd_spa_lo=0.0, prd_spa_hi=6.0),
    FRAMESHIFT_NO_NMD: _ORANGE,
    SPLICE_NO_FRAMESHIFT: _ORANGE,
    UNCERTAIN: SplBranchSpec(0.0, 0.0, prd_spa_lo=-2.0, prd_spa_hi=2.0, parent_hi=0.0),
    UNLIKELY: SplBranchSpec(-1.0, 0.0, prd_spa_lo=-3.0, prd_spa_hi=0.0, inf_hi=0.0, parent_hi=8.0),
}
```

(All five keep the default `prd_spa_fxn_hi=9`. SPA/FXN consumed raw. Provenance gains a
one-line "SM 6 blue/violet parent caps are inverted vs SM 11/12 — encoded as documented,
suspected SM 6 inconsistency" note, emitted by the wrapper before delegating.)

## Part 2 — `MissenseScoreResult` DTO — `scoring/result.py`

A frozen dataclass mirroring `ScoreResult`'s non-authoritative guard, holding **both** sub-path
results (SM 6 requires saving both) plus the selection:

```python
@dataclass(frozen=True)
class MissenseScoreResult:
    amino_acid: ScoreResult          # the MIS_ path
    splice: ScoreResult              # the SPL_ path
    selected_path: str               # "AMINO_ACID" | "SPLICE"
    applied_parent_code: str         # "MIS" | "SPL"
    applied_total: float | None
    provenance: list[str]
    authoritative: bool = False      # __post_init__ raises if True

    def __post_init__(self) -> None:
        if self.authoritative:
            raise ValueError(...)  # same message shape as ScoreResult
```

## Part 3 — `reference_score_missense` — `scoring/pfd/missense.py`

`reference_score_missense(assessment: MissenseAssessment, *, gene_disease_validity) ->
MissenseScoreResult`. Scores both sub-paths (amino-acid via
`reference_score_missense_amino_acid` — **no** GDV; splice via `reference_score_missense_splice`
— **with** GDV), then applies the SM 6 L157 take-higher rule to their `parent_total`s:

```
mis = amino.parent_total        # may be None
spl = splice.parent_total       # may be None
if spl is None or spl <= 0:            selected = AMINO_ACID   # negative/absent splice -> amino
elif mis is None or spl > mis:         selected = SPLICE       # splice positive & strictly higher
else:                                  selected = AMINO_ACID   # spl <= mis (incl. a positive tie)
```

Faithful to SM 6 L157: "if the splice value is negative, use amino-acid; if positive, use the
higher; if both positive and equal, use amino-acid (higher prior for the amino-acid effect)."
`None` totals are treated as not-positive (an empty sub-path never wins). `applied_total` and
`applied_parent_code` follow `selected_path`; `provenance` records both totals + the decision.
Missing sub-assessments: if `assessment.amino_acid`/`.splice` is None, score an empty
`MissenseAminoAcidAssessment()`/`MissenseSpliceAssessment()` for that path (yields an all-`_ND`
ScoreResult), so the comparison still runs.

## Exports (`scoring/__init__.py`, sorted `__all__`)

Add `MissenseScoreResult` (classes: `MissenseScoreResult` < `ScoreResult`), and the two
functions — `reference_score_missense` < `reference_score_missense_amino_acid` <
`reference_score_missense_splice` (all between `intronic_synonymous` and `nonsense`).

## Tests (TDD)

`tests/test_missense_splice_scoring.py` (the SPL_ path): yellow maximal (PRD +3, SPA scales to
held `PRD+SPA`=+6, FXN +8, INF +8 → parent +10). **The oddity is the blue-vs-violet contrast:**
the **blue parent-0 clamp** (blue with +2 SPA/+8 FXN/+8 INF → 2nd held +9, parent capped **0** —
an *uncertain* variant's positive evidence is zeroed) vs the **violet positive total** (violet
PRD −1, FXN +8, no SPA/INF → 2nd held cap(−1+8, +9)=+7, parent **+7** — an *unlikely* variant
reaching positive). Note the violet `parent_hi=+8` (SM 6 L155) is faithful but never binds — the
reachable violet max is +7 (PRD −1 + FXN +8; SPA ≤0, INF ≤0). Also: violet INF B/LB-only (a P INF
clamped to 0 by `inf_hi=0`); all-five-outcomes loop (`parent_code "SPL"`); empty → `_ND`.

`tests/test_missense_compare_scoring.py` (the take-higher + DTO): splice negative → amino;
splice positive & higher → splice; positive tie → amino; splice None (empty) → amino; amino None
& splice positive → splice; both empty → amino, `applied_total` None; `MissenseScoreResult`
holds both sub-results; `authoritative=True` raises.

## Docs

`docs/reference/scoring.md`: a Missense (splice path + comparison) line — the SPL_ branch table
(note the flagged blue/violet oddity), `reference_score_missense` take-higher, and the
`MissenseScoreResult` DTO. **This completes the splice family** (Canonical, Intronic, Missense).

## Quality gates

`pytest`, `ruff`, drift gate (`MissenseScoreResult` is a frozen dataclass, NOT Pydantic — no
schema; scoring stays out of root `__all__`), `mkdocs build --strict`, clean tree. The MIS_
amino-acid scorer, `score_spl_workflow`, and all prior scorers are untouched.

## Out of scope

The SM 7 motif-variant special case (deferred with critical-amino-acids). POP/LOC/CLN; case
aggregation; the classification band; `validate_case`.
