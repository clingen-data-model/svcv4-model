# Reference scorer — Missense amino-acid path (SM 6, MIS_) — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-missense-amino-acid` (off `main`)
**Scope:** Increment C1 of the splice family — the **new** MIS_ amino-acid pipeline. The SPL_
splice path + the MIS_-vs-SPL_ take-higher comparison are C2 (a follow-up increment).

## Goal

Add `reference_score_missense_amino_acid` (SM 6 green path → the `MIS_` parent code) plus two
new primitives it needs. This is the **first** scorer that (a) uses **transcript-relevance-only**
PRD (no SM 18 mechanism, **no GDV gate**), and (b) computes a **distinct 4-category informative
tally**. Non-authoritative; CSpec authoritative.

## The MIS_ pipeline (single path — no outcome branches)

```
MIS_PRD  ->  MIS_FXN  ->  held prd_fxn  ->  MIS_INF  ->  mis_total
```

- **MIS_PRD** — computed: `predictive.initial_points` adjusted by **transcript relevance only**
  (`ExonRelevance`: All ×1.0 / Most ×0.5 / Few ×0.0), then capped **`−4.0 .. +4.0`**. Per SM 6
  L21: a zero/negative in-silico score skips the relevance step (passthrough, floored at −4); a
  positive score is reduced by the exon fraction. The molecular-mechanism axis is **not** applied
  (predictors already capture LoF+GoF), and there is **no GDV gate** (unlike the SM 18 path).
- **MIS_FXN** — consumed raw (`fxn_points`), `−8.0 .. +8.0` (OddsPath not recomputed).
- **held prd_fxn** = `hold_combined(prd, fxn)`, capped **`−8.0 .. +6.0`** (SM 6 L26).
- **MIS_INF** — computed via the new 4-category tally, capped **`−8.0 .. +8.0`** (SM 6 L31–37).
- **mis_total** = `hold_combined(prd_fxn, inf)`, capped **`−8.0 .. +9.0`** (SM 6 L39). Parent
  code is always **`MIS`**.

## New primitive 1 — `transcript_relevance_points(points, exon_relevance)` (`primitives.py`)

Positive-only exon-fraction reduction, reusing the existing `_EXON_FRACTION` map (All 1.0 / Most
0.5 / Few 0.0):

```python
def transcript_relevance_points(points, exon_relevance):
    if points is None or points <= 0:
        return points  # zero/negative skips the step (caller floors at -4)
    frac = 1.0 if exon_relevance is None else _EXON_FRACTION.get(exon_relevance, 1.0)
    return points * frac
```

None exon → ×1.0 (the generous default, matching `apply_sm18_multiplier`'s exon axis). No
mechanism, no GDV — deliberately simpler than `apply_sm18_multiplier`.

## New primitive 2 — `missense_informative_points(variants)` (`primitives.py`)

The distinct 4-category MIS_INF tally (SM 6 L32–35). Each `MissenseInformativeVariant` carries an
analyst-assigned `category` (`MissenseInfCategory`) + `classification` (`VariantClassification`).
The Grantham judgment is already captured in `category`; this primitive applies each category's
point rule and sums. Returns `None` when no variant has a scoring (category, class) pair
(`MIS_INF_ND`). **Uncapped** — the caller caps `−8..+8`.

Per-category rules (verified verbatim vs SM 6 L32–35):

| Category | Counts | Rule |
|---|---|---|
| `SAME_AA_PATHOGENIC` | P/LP | +4 first P (or +2 if first is LP), **+2 each additional** → `first + 2·(n−1)`, first = 4 if any P else 2 |
| `DISTINCT_AA_PATHOGENIC` | P/LP | standard: +2 first P, +1 first LP, +1 each additional |
| `DISTINCT_AA_BENIGN` | B/LB | standard negative: −2 first B, −1 first LB, −1 each additional |
| `SAME_AA_BENIGN` | B/LB | −4 first B (or −2 if first is LB), **−2 each additional** → `−(first + 2·(n−1))`, first = 4 if any B else 2 |

Only the matching classifications count per category (cats 1–2 tally P/LP; cats 3–4 tally B/LB).
A `VUS` (or a class that doesn't match the category's polarity) contributes nothing — SM 6 /
docs: a VUS informative variant maps to no category. The **motif-variant** special case (cat 2,
+2 once, leaning on SM 7) is **out of scope** (deferred with SM 7 critical-amino-acids), noted in
provenance.

Helper shape (both bonuses share one form):

```python
def _doubled(n_strong, n_weak):        # cat 1 / cat 4 magnitude
    n = n_strong + n_weak
    if n == 0:
        return 0.0
    first = 4.0 if n_strong else 2.0
    return first + 2.0 * (n - 1)

def _standard(n_strong, n_weak):       # cat 2 / cat 3 magnitude (== informative_points half)
    if n_strong + n_weak == 0:
        return 0.0
    pts = (2.0 if n_strong else 0.0) + (1.0 if n_weak else 0.0)
    return pts + max(n_strong - 1, 0) + max(n_weak - 1, 0)
```

MIS_INF = `_doubled(c1_P, c1_LP) + _standard(c2_P, c2_LP) − _standard(c3_B, c3_LB) − _doubled(c4_B, c4_LB)`;
return `None` if every category is empty.

## `reference_score_missense_amino_acid` — `scoring/pfd/missense_amino_acid.py`

`reference_score_missense_amino_acid(assessment: MissenseAminoAcidAssessment) -> ScoreResult`
— **no `gene_disease_validity`** (the MIS_ path has no GDV gate; this is the first such scorer).
Reads `predictive.{initial_points, transcript_relevance}`, `fxn_points`, `informative.variants`.
Sub-codes omitted when `_ND`; `held_combined` carries `PRD+FXN`; `parent_code = "MIS"`; every step
recorded in `provenance` (incl. the deferred-motif note). Exported from `svcv4_model.scoring`
(sorted `__all__`: `missense_amino_acid` sorts after `intronic_synonymous`, before `nonsense`).

## Tests (TDD) — `tests/test_missense_amino_acid_scoring.py` (+ primitive tests in `test_scoring_primitives.py`)

- PRD transcript relevance: initial +4, All → +4; Most → +2; Few → 0; a −3 initial → −3
  (passthrough, no relevance); a +4 with All but capped stays +4.
- Maximal: PRD +4 (All), FXN +8 → held `PRD+FXN`=cap(12, +6)=**+6**; a cat-1 `SAME_AA_PATHOGENIC`
  P (+4 INF) → mis_total=cap(6+4, +9)=**+9**; `parent_code "MIS"`.
- 4-category INF tally: one cat-1 P (+4); cat-1 P+LP (+6); cat-2 P (+2, == standard); cat-3 B
  (−2); cat-4 B (−4); cat-4 B+LB (−6); a mix summing then capped +8; a VUS → 0/None.
- held PRD+FXN floor: PRD −4, FXN −8 → held cap(−12, −8)=−8.
- FXN `_ND`; INF `_ND`; empty → all `_ND`, `parent_total` None, `parent_code "MIS"`.
- `transcript_relevance_points` + `missense_informative_points` unit tests (each category, empty,
  VUS-only, mismatched class).

## Docs

`docs/reference/scoring.md`: add a Missense (amino-acid path) line — note it is the first
`MIS_` scorer, transcript-relevance-only PRD (no GDV), and the computed 4-category MIS_INF; the
SPL_ path + take-higher are a follow-up (C2).

## Quality gates

`pytest`, `ruff`, drift gate (no schema — scoring stays out of root `__all__`),
`mkdocs build --strict`, clean tree. The splice scorers/helpers and the 6 NUL_/CDS_ scorers are
untouched.

## Out of scope (→ C2 and beyond)

The missense **SPL_ splice path** (a `score_spl_workflow` branch table — note SM 6's surprising
blue `−8..0` / violet `−8..+8` parent caps, to be encoded faithfully + flagged) and the
**`reference_score_missense` take-higher** comparison. The **motif-variant** SM 7 special case.
POP/LOC/CLN; aggregation; classification band; validate_case.
