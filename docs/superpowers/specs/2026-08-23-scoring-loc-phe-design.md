# Reference Scorer — LOC_PHE phenotype specificity (SM 5) — Design

**Goal:** Add `reference_score_loc_phe` — the **reference (NON-AUTHORITATIVE)** LOC_PHE
phenotype-specificity code (SM 5), the first of the two Locus-specificity (LOC) codes. CSpec
remains authoritative. This is increment **LOC-1**; LOC_SEG (co-segregation, LOC-2) is deferred
because its per-MOI affected-segregant point values live only in the SM 5 Figure 2 image, not the
text.

**Architecture:** New module `src/svcv4_model/scoring/hod/locus.py` (parallel to `clinical.py`
and `population.py`). Pure function; one-way dependency (scoring → models); NOT re-exported from
the root `svcv4_model/__init__.py`, so it leaks no schema. Follows the established **HOD grouping
pattern**: `parent_code="LOC"` is a display/grouping label (not an SVCv4 parent code), and
`parent_total` is the recorded LOC_PHE value (a single sub-code here).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

---

## Signature

```python
def reference_score_loc_phe(case: Case, *, moi: MOI | None) -> ScoreResult: ...
```

- `moi` is a **required keyword** for signature parity with every HOD scorer. LOC_PHE's *band*
  has no MOI axis (SM 5 frames it purely on diagnostic yield); `moi` is consumed **only** for the
  autosomal-recessive non-segregation gate (below). SM 5 notes MOI is "not applicable" to LOC_PHE
  as an *evidence-input* — that refers to the phenotype-specificity concept, not to the
  non-segregation caveat, which does need to know whether the disorder is AR. Documented in the
  docstring + provenance.

Returns a `ScoreResult`:
- `parent_code="LOC"` (grouping label), `authoritative=False`.
- On data present: `sub_code_points={"LOC_PHE": pts}`, `parent_total=pts`.
- On No Data: no `sub_code_points`, `parent_total=None` (the `_ND` shape).
- `provenance`: the LOC grouping-label note, the band decision (with the raw yield string echoed),
  any non-segregation zeroing, and the deferral note (LOC_SEG + the LOC combined +4.0 cap are
  computed in LOC-2 / case aggregation).

## Data flow

```
case.testing.diagnostic_yield_for_phenotypes (str | None)
    │  guard: case.testing may be None
    ▼
_parse_percent(s) ─── None ──► LOC_PHE_ND
    │ float pct
    ▼
_loc_phe_band(pct) ─► initial points ∈ {0.0, +1.0, +2.0, +3.0, +4.0}
    │
    ├─ points == 0.0 ─► record 0.0 (no zeroing to do)
    │
    └─ points > 0.0 ─► _non_segregation(case, moi=moi)
                         │  non-seg found?
                         ├─ yes ─► zero to 0.0 (+ AR caveat if moi is AR)
                         └─ no  ─► keep points
```

## Imports (module top)

```python
from __future__ import annotations

import re

from svcv4_model.case import MOI, AgeMatchedPenetrance, Case, TriState
from svcv4_model.scoring.result import ScoreResult
```

`re` is a stdlib group above the first-party imports. Within `svcv4_model.case`, isort's
`order-by-type` sorts the all-caps `MOI` first, then `AgeMatchedPenetrance`, `Case`, `TriState`
(matching `clinical.py`). Export `reference_score_loc_phe` from `scoring/__init__.py` (add to both
the import and `__all__`, alphabetically among the `reference_score_*` names).

## Component 1 — diagnostic-yield parse (`_parse_percent`)

`gene_specificity_for_phenotypes` is **unscored context** (settled decision 1); the band is driven
**only** by `testing.diagnostic_yield_for_phenotypes`.

```python
import re
_NUM = re.compile(r"[0-9]*\.?[0-9]+")

def _parse_percent(raw: str | None) -> float | None:
    """First numeric token of a yield string as a percent, or None if none found.

    Handles clean point estimates ('90%', '2.6%') and takes the LOWER bound of a written
    range ('91-93%' -> 91.0, the conservative/least-pathogenic end). A leading '<' is honored
    as "just below" (so SM 5's idiomatic '<33%' -> 32.999... -> band 0.0, NOT +1.0); a leading
    '>' keeps the number as a conservative floor ('>82%' -> 82.0 -> +4.0). The raw string is
    always echoed in provenance for transparency.
    """
    if raw is None:
        return None
    m = _NUM.search(raw)
    if m is None:
        return None
    pct = float(m.group())
    # A leading '<' before the number means the true yield is below it -> nudge into the band
    # just below the boundary (SM 5 writes '<33%' for the 0.0 case).
    if raw.lstrip().startswith("<"):
        pct -= 1e-9
    return pct
```

- `case.testing is None` OR parse returns `None` → `LOC_PHE_ND`, provenance notes why (no testing,
  no yield, or unparseable — echoing the raw string when present).
- **Documented parse limitations** (raw always echoed in provenance; see `known-gaps.md`): a
  leading `>` is treated as a floor, not an interval; a ratio like `"1 in 2"` misparses to its
  first token (`1.0` → band `0.0`) — curators should record a percent, not a ratio.

## Component 2 — the band (`_loc_phe_band`)

SM 5 Figure 1 "Phenotype Specificity Points". Explicit text anchors: `<33→0.0`, `33-50→+1.0`,
`68-81→+3.0`, `>82→+4.0`. The `+2.0` band (SM 5 gives no explicit anchor) and the exact
boundary treatment of the (81, 82) sliver are **inferred** — flagged in `known-gaps.md` alongside
the SM 18 Figure-1 assumption. Continuous, monotonic cut points:

| Yield `pct` | LOC_PHE | Basis |
|---|---|---|
| `pct < 33` | 0.0 | SM 5: "<33% → 0.0" |
| `33 ≤ pct ≤ 50` | +1.0 | SM 5: "33-50% → +1.0" (Pendred 50% example) |
| `50 < pct < 68` | +2.0 | **inferred** — the unanchored middle band |
| `68 ≤ pct < 82` | +3.0 | SM 5: "68-81% → +3.0" (TSC2 example); the (81,82) sliver folds **down** into +3.0 (conservative) |
| `pct ≥ 82` | +4.0 | SM 5: ">82% → +4.0" (FBN1 91-93%, "83% → +4.0" examples) |

```python
def _loc_phe_band(pct: float) -> float:
    if pct < 33.0:
        return 0.0
    if pct <= 50.0:
        return 1.0
    if pct < 68.0:
        return 2.0
    if pct < 82.0:
        return 3.0
    return 4.0
```

A yield below 33% records `LOC_PHE_0.0` (computed-and-present, **not** `_ND`). `_ND` is reserved
for absent/unparseable yield.

**Out of scope (flagged), not modeled here:** SM 5's ultra-rare-disease alternative — up to
`+2.0` from phenotype **semantic-similarity** scores when diagnostic-yield data don't exist — has
no capturable field, so it is a `known-gaps.md` entry, not a code path. Likewise the robustness
caveats (adequate sample size, 95% CI of the yield, testing-methodology match to the VBC lab) are
not structured fields; the scorer bands on the stated yield and flags in provenance that these
caveats are **not verifiable from captured inputs** (reference-only; CSpec authoritative).

## Component 3 — non-segregation zeroing (`_non_segregation`)

Settled decision 3: the **two-case rule, MOI-gated**. `CaseRelative` has no explicit
non-segregation flag; it is inferred from `case.relatives`. A relative `r` is a non-segregation
event when **either**:

- **(a)** `r.affected_w_mde is TRUE and r.vbc_exists is FALSE` — affected but genotype-negative; OR
- **(b)** `r.affected_w_mde is FALSE and r.vbc_exists is TRUE and case.age_matched_penetrance is
  NEAR_100` — a VBC carrier who is unaffected despite near-complete penetrance.

Penetrance for rule (b) is read from **`case.age_matched_penetrance`** (a disorder/case-level
property — `CaseRelative` has no penetrance field).

MOI gate (settled decision 3): **for AR, rule (b) is suppressed** — a single unaffected VBC
carrier is an *expected* recessive carrier, not a non-segregation. Rule (a) is MOI-independent and
still applies. When `moi is None` we cannot confirm the disorder is non-AR, so rule (b) is
suppressed conservatively and rule (a) still applies.

If any non-segregation is found and the banded points are `> 0.0`, the LOC_PHE points are **zeroed
to 0.0** (SM 5: a non-segregation "excludes the locus with a log odds of −∞"; it negates the
phenotype-specificity points). Provenance records the zeroing and the triggering relative index.

**AR caveat (SM 5 "Note Regarding Non-segregation in AR"):** when `moi is MOI.AR` and a rule-(a)
non-segregation zeroes the points, provenance additionally warns that an AR non-segregation may
reflect *another causative locus* rather than benignity of this VBC (the LOC_SEG `−4.0` benign
flip is **not** applied for AR — and LOC_SEG itself is deferred to LOC-2).

```python
_RULE_B_SUPPRESSED = frozenset({MOI.AR})  # None also suppresses rule (b)

def _non_segregation(case: Case, *, moi: MOI | None) -> list[str]:
    """Reasons (one per triggering relative) a non-segregation was observed; empty if none."""
    reasons: list[str] = []
    rule_b_ok = moi is not None and moi not in _RULE_B_SUPPRESSED
    near_100 = case.age_matched_penetrance == AgeMatchedPenetrance.NEAR_100
    for i, r in enumerate(case.relatives):
        if r.affected_w_mde == TriState.TRUE and r.vbc_exists == TriState.FALSE:
            reasons.append(f"relative[{i}] affected but VBC-absent (rule a)")
        elif (
            rule_b_ok
            and near_100
            and r.affected_w_mde == TriState.FALSE
            and r.vbc_exists == TriState.TRUE
        ):
            reasons.append(f"relative[{i}] unaffected VBC-carrier at ~100% penetrance (rule b)")
    return reasons
```

> **Comparison idiom:** use `==` / `!=` for `TriState` (matching `clinical.py` / `population.py`),
> **not** `is`. `UNKNOWN` / `None` are non-`TRUE` and non-`FALSE`, so neither rule triggers on
> them (the None-guard is preserved). `==` is deliberate — an `is`-identity check would silently
> stop firing (never zeroing LOC_PHE → over-scoring) if a model ever adopted `use_enum_values`.

```python  # (block continues in the assembly section below)
```

> **Known-gap (WG follow-up):** the exact MOI × zygosity semantics of a non-segregation are
> under-specified in SM 5 (which defers to PMID 38103548 and assumes analysts trained in
> segregation analysis). In particular, an unaffected **XLR** female carrier (het) can trip rule
> (b) here even though she is an expected carrier — the reference heuristic does not yet gate rule
> (b) by `relative.vbc_zygosity`. Recorded in `known-gaps.md`.

## Result assembly

```python
def reference_score_loc_phe(case, *, moi):
    prov = ['LOC: "LOC" is the HOD grouping label. LOC_SEG (co-segregation) and the combined '
            "LOC +4.0 cap are computed in LOC-2 / case aggregation."]
    raw = case.testing.diagnostic_yield_for_phenotypes if case.testing is not None else None
    pct = _parse_percent(raw)
    if pct is None:
        prov.append(f"LOC_PHE: _ND (no parseable diagnostic yield; raw={raw!r})")
        return ScoreResult(parent_code="LOC", provenance=prov, authoritative=False)

    pts = _loc_phe_band(pct)
    prov.append(f"LOC_PHE: +{pts} from diagnostic yield {pct}% (raw={raw!r}); robustness caveats "
                "(sample size, 95% CI, methodology match) not verifiable from captured inputs.")
    if pts > 0.0:
        reasons = _non_segregation(case, moi=moi)
        if reasons:
            prov.append("LOC_PHE: zeroed to 0.0 -- non-segregation observed: " + "; ".join(reasons))
            if moi is MOI.AR:
                prov.append("LOC_PHE: AR caveat -- an AR non-segregation may reflect another "
                            "causative locus, not benignity; LOC_SEG -4.0 flip not applied (and "
                            "LOC_SEG is deferred to LOC-2).")
            pts = 0.0
    return ScoreResult(parent_code="LOC", sub_code_points={"LOC_PHE": pts},
                       parent_total=pts, provenance=prov, authoritative=False)
```

## Error handling / edge cases

- `case.testing is None` → `_ND` (short-circuit before attribute access).
- Unparseable yield (`"not available"`, `""`, `None`) → `_ND`.
- Range `"91-93%"` → lower bound `91.0` → `+4.0`. Leading `<`/`>` not interpreted (documented
  limitation; raw echoed in provenance).
- Band `0.0` short-circuits the non-segregation check (nothing to zero); a non-segregation on an
  already-zero LOC_PHE stays `0.0` (LOC_PHE has no benign value — benignity is LOC_SEG's `−4.0`,
  deferred).
- `moi is None` → rule (b) suppressed, rule (a) still applies.

## Testing (TDD)

`tests/test_loc_phe_scoring.py`, a `_case(**kw)` builder wrapping `Case` (+ nested `CaseTesting` /
`CaseRelative`). Assertions cover:

1. Bands: `"90%"→+4.0`, `"45%"→+1.0`, `"60%"→+2.0`, `"75%"→+3.0`, `"20%"→0.0`, `"2.6%"→0.0`;
   `parent_code=="LOC"`, `parent_total==pts`.
2. Boundaries: `"33%"→+1.0`, `"50%"→+1.0`, `"68%"→+3.0`, `"81%"→+3.0`, `"81.5%"→+3.0` (sliver
   folds down), `"82%"→+4.0`.
3. Range: `"91-93%"→+4.0` (lower bound). Leading `<`: `"<33%"→0.0` (documents the fixed footgun).
4. `_ND`: `testing=None`; `diagnostic_yield_for_phenotypes=None`; `""` (empty); `"not available"`
   — each yields empty `sub_code_points` + `parent_total is None`.
5. Non-seg rule (a): `"90%"`, moi AD, relative affected+VBC-absent → `0.0`, provenance says
   "non-segregation".
6. Non-seg rule (b): `"90%"`, moi AD, `age_matched_penetrance=NEAR_100`, relative
   unaffected+VBC-present → `0.0`.
7. Rule (b) needs NEAR_100: `"90%"`, moi AD, penetrance `PCT_80_100` (and separately `None`),
   unaffected carrier → stays `+4.0`.
8. Rule (b) suppressed for AR: `"90%"`, moi AR, NEAR_100, unaffected carrier → stays `+4.0`.
9. Rule (a) under AR zeroes + AR caveat: `"90%"`, moi AR, affected+VBC-absent → `0.0`, provenance
   has the AR caveat.
10. `moi=None`: rule (a) still zeroes; a lone unaffected carrier (rule b) does not.
11. Already-zero + non-seg: `"20%"` + affected-VBC-absent relative → stays `0.0`.
12. `gene_specificity_for_phenotypes` is ignored: setting it without a yield → `_ND`.
13. **UNKNOWN/None non-trigger** (guards the `==` idiom): `"90%"`, moi AD, and a relative with
    (i) all fields `UNKNOWN`/`None`, (ii) `affected_w_mde=TRUE` + `vbc_exists=UNKNOWN`/`None` (no
    rule a), (iii) `affected_w_mde=FALSE` + `vbc_exists=TRUE` + penetrance `NEAR_100` but that's
    rule (b) — so instead test `affected_w_mde=UNKNOWN` + `vbc_exists=TRUE` (no rule b) → each stays
    `+4.0`.

## Docs

- `docs/reference/scoring.md`: add the LOC line — LOC_PHE (SM 5) computed; band from
  `testing.diagnostic_yield_for_phenotypes` (`<33→0 / 33-50→+1 / 51-67→+2 / 68-81→+3 / ≥82→+4`),
  non-segregation zeroing (two-case rule, MOI-gated, AR suppresses rule b); LOC_SEG and the LOC
  combined +4.0 cap are deferred (LOC-2 / aggregation).
- `docs/reference/known-gaps.md`: add rows —
    - (i) LOC_PHE `+2.0` band + the (81,82) boundary are **inferred** (SM 5 gives no anchor); the
      `≥82` +4.0 threshold slightly over-awards on `[82,83)` vs SM 5's "83%" examples.
    - (ii) the ultra-rare **semantic-similarity `+2.0`** alt-path is not capturable (no field).
    - (iii) non-segregation **MOI × zygosity** semantics are under-specified in SM 5; rule (b) is
      not yet zygosity-gated, so an unaffected **XLR** het carrier can trip it. Note: the needed
      fields (`relative.sex`, `relative.vbc_zygosity`) **are** captured — this is "data available,
      not yet gated" (a deliberate LOC-1 deferral), not a source limitation. Suppression stays
      `{AR}` per the settled decision (widening it to XLR is a decision change, deferred).
    - (iv) under **AR**, SM 5's "Note Regarding Non-segregation in AR" argues a non-segregation may
      reflect *another causative locus*, not benignity — so whether LOC_PHE rule-(a) zeroing should
      apply under AR **at all** is under-specified. The reference scorer zeroes conservatively and
      flags the caveat in provenance; this may over-negate. (SM 5's only worked LOC_PHE
      non-seg example, TSC2, is dominant.)
    - (v) SM 5 says phenotype specificity uses "the single proband with the **most specific**
      phenotypic information"; selecting that proband is a **curator** responsibility — the scorer
      bands whatever single value sits in `diagnostic_yield_for_phenotypes`. Flagged in provenance.
    - (vi) parse limitations: a leading `>` is a floor not an interval; `"1 in N"` ratios misparse.
- `docs/workflows/hod/loc/loc-phe.md`: no change needed (it already documents capture; scoring is
  cross-linked via scoring.md).

## Quality gates

`uv run pytest -q`; `uv run ruff check .` (LL 100); drift gate (`export_schemas.py` then
`git diff --quiet -- schemas/json docs/workflows/case-model.md` — must stay clean: locus.py is
scoring, not re-exported); `uv run mkdocs build --strict`; no scorer schema leaked; clean tree.

## Non-goals / deferred

- **LOC_SEG (LOC-2):** the co-segregation positive scoring (per-MOI affected-segregant points,
  unaffected `+1.0` / AR `+0.4`, cap `+4.0`) and the non-segregation `−4.0` benign flip — blocked
  on the SM 5 Figure 2 point values (image-only).
- The **LOC combined +4.0 cap** (LOC_PHE + LOC_SEG) → case aggregation.
- Biallelic apportionment (comp-het → both variants; homozygote → single variant, same points) →
  case aggregation.
