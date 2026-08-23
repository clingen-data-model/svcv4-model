# Reference Scorer — LOC_PHE phenotype specificity (SM 5) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_loc_phe` (SM 5) — the reference (NON-AUTHORITATIVE) LOC_PHE
phenotype-specificity code, increment **LOC-1**. New module `scoring/hod/locus.py`.
`parent_code="LOC"` grouping label, single sub-code `LOC_PHE`. CSpec authoritative.

**Architecture:** New `src/svcv4_model/scoring/hod/locus.py` (parallel to `clinical.py` /
`population.py`); pure function; NOT re-exported from root `svcv4_model/__init__.py` (leaks no
schema). Band from `testing.diagnostic_yield_for_phenotypes`; non-segregation zeroing (two-case
rule, MOI-gated). LOC_SEG (LOC-2) + the LOC combined +4.0 cap deferred.

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Design:** `docs/superpowers/specs/2026-08-23-scoring-loc-phe-design.md` (approved).

**Band (SM 5 Fig 1; +2.0 band + (81,82) sliver inferred):** `<33→0.0`, `33-50→+1.0`,
`50<pct<68→+2.0`, `68≤pct<82→+3.0`, `≥82→+4.0`.

**Non-seg (two-case rule, MOI-gated):** rule (a) affected+VBC-absent (MOI-independent); rule (b)
unaffected VBC-carrier at `NEAR_100` penetrance (from `case.age_matched_penetrance`), suppressed
for `AR` and `moi is None`. A non-seg zeroes `+1..+4` → `0.0`; AR adds a provenance caveat.

---

## Task 1: `reference_score_loc_phe` (TDD)

**Files:**
- Create: `src/svcv4_model/scoring/hod/locus.py`
- Create: `tests/test_loc_phe_scoring.py`
- Modify: `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_loc_phe_scoring.py`

```python
"""Tests for reference_score_loc_phe (SM 5 phenotype specificity, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import (
    MOI,
    AgeMatchedPenetrance,
    Case,
    CaseRelative,
    CaseTesting,
    TriState,
)
from svcv4_model.scoring import reference_score_loc_phe


def _case(yield_: str | None = None, *, relatives: list[CaseRelative] | None = None,
          penetrance: AgeMatchedPenetrance | None = None, gene_spec: str | None = None,
          no_testing: bool = False) -> Case:
    testing = None if no_testing else CaseTesting(diagnostic_yield_for_phenotypes=yield_)
    return Case(
        testing=testing,
        gene_specificity_for_phenotypes=gene_spec,
        age_matched_penetrance=penetrance,
        relatives=relatives or [],
    )


def _phe(case: Case, *, moi: MOI | None = MOI.AD) -> float | None:
    return reference_score_loc_phe(case, moi=moi).sub_code_points.get("LOC_PHE")


# --- bands ---------------------------------------------------------------
def test_band_top() -> None:
    r = reference_score_loc_phe(_case("90%"), moi=MOI.AD)
    assert r.parent_code == "LOC"
    assert r.sub_code_points["LOC_PHE"] == 4.0
    assert r.parent_total == 4.0


def test_bands() -> None:
    assert _phe(_case("45%")) == 1.0
    assert _phe(_case("60%")) == 2.0
    assert _phe(_case("75%")) == 3.0
    assert _phe(_case("20%")) == 0.0
    assert _phe(_case("2.6%")) == 0.0


def test_boundaries() -> None:
    assert _phe(_case("33%")) == 1.0
    assert _phe(_case("50%")) == 1.0
    assert _phe(_case("68%")) == 3.0
    assert _phe(_case("81%")) == 3.0
    assert _phe(_case("81.5%")) == 3.0  # (81,82) sliver folds down
    assert _phe(_case("82%")) == 4.0


def test_range_lower_bound() -> None:
    assert _phe(_case("91-93%")) == 4.0


def test_leading_lt_is_below() -> None:
    assert _phe(_case("<33%")) == 0.0  # NOT +1.0


# --- No Data -------------------------------------------------------------
def test_nd_no_testing() -> None:
    r = reference_score_loc_phe(_case(no_testing=True), moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_nd_no_yield() -> None:
    r = reference_score_loc_phe(_case(None), moi=MOI.AD)
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_nd_empty_and_unparseable() -> None:
    assert reference_score_loc_phe(_case(""), moi=MOI.AD).parent_total is None
    assert reference_score_loc_phe(_case("not available"), moi=MOI.AD).parent_total is None


# --- non-segregation -----------------------------------------------------
def _affected_no_vbc() -> CaseRelative:
    return CaseRelative(affected_w_mde=TriState.TRUE, vbc_exists=TriState.FALSE)


def _unaffected_carrier() -> CaseRelative:
    return CaseRelative(affected_w_mde=TriState.FALSE, vbc_exists=TriState.TRUE)


def test_nonseg_rule_a_zeroes() -> None:
    r = reference_score_loc_phe(_case("90%", relatives=[_affected_no_vbc()]), moi=MOI.AD)
    assert r.sub_code_points["LOC_PHE"] == 0.0
    assert any("non-segregation" in p.lower() for p in r.provenance)


def test_nonseg_rule_b_zeroes() -> None:
    c = _case("90%", relatives=[_unaffected_carrier()], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _phe(c, moi=MOI.AD) == 0.0


def test_rule_b_needs_near_100() -> None:
    c1 = _case("90%", relatives=[_unaffected_carrier()],
               penetrance=AgeMatchedPenetrance.PCT_80_100)
    c2 = _case("90%", relatives=[_unaffected_carrier()], penetrance=None)
    assert _phe(c1, moi=MOI.AD) == 4.0
    assert _phe(c2, moi=MOI.AD) == 4.0


def test_rule_b_suppressed_for_ar() -> None:
    c = _case("90%", relatives=[_unaffected_carrier()], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _phe(c, moi=MOI.AR) == 4.0


def test_rule_a_under_ar_zeroes_with_caveat() -> None:
    r = reference_score_loc_phe(_case("90%", relatives=[_affected_no_vbc()]), moi=MOI.AR)
    assert r.sub_code_points["LOC_PHE"] == 0.0
    assert any("AR" in p and "locus" in p for p in r.provenance)


def test_moi_none_rule_a_zeroes_rule_b_does_not() -> None:
    c_a = _case("90%", relatives=[_affected_no_vbc()])
    c_b = _case("90%", relatives=[_unaffected_carrier()], penetrance=AgeMatchedPenetrance.NEAR_100)
    assert _phe(c_a, moi=None) == 0.0
    assert _phe(c_b, moi=None) == 4.0


def test_already_zero_plus_nonseg_stays_zero() -> None:
    assert _phe(_case("20%", relatives=[_affected_no_vbc()]), moi=MOI.AD) == 0.0


def test_unknown_none_relatives_do_not_trigger() -> None:
    all_unknown = CaseRelative()  # all fields None
    affected_vbc_unknown = CaseRelative(affected_w_mde=TriState.TRUE)  # vbc_exists None
    unaffected_unknown_affect = CaseRelative(  # affected UNKNOWN + vbc present -> no rule b
        affected_w_mde=TriState.UNKNOWN, vbc_exists=TriState.TRUE)
    for rel in (all_unknown, affected_vbc_unknown, unaffected_unknown_affect):
        c = _case("90%", relatives=[rel], penetrance=AgeMatchedPenetrance.NEAR_100)
        assert _phe(c, moi=MOI.AD) == 4.0


def test_gene_specificity_ignored() -> None:
    r = reference_score_loc_phe(_case(None, gene_spec="100%"), moi=MOI.AD)
    assert r.parent_total is None  # gene_specificity is not the band input
```

- [ ] **Step 2: Run — expect ImportError.** `uv run pytest tests/test_loc_phe_scoring.py -q`

- [ ] **Step 3: Implement** — create `src/svcv4_model/scoring/hod/locus.py`:

```python
"""Reference (non-authoritative) scorer for Locus specificity -- phenotype (SM 5, LOC_PHE).

Increment LOC-1: LOC_PHE only. LOC_SEG (co-segregation) and the combined LOC +4.0 cap are
deferred (LOC_SEG's per-MOI affected-segregant point values are in the SM 5 Figure 2 image, not
the text). CSpec is authoritative. ``parent_code="LOC"`` is a display/grouping label (not an
SVCv4 parent code); ``parent_total`` is the recorded LOC_PHE value.
"""

from __future__ import annotations

import re

from svcv4_model.case import MOI, AgeMatchedPenetrance, Case, TriState
from svcv4_model.scoring.result import ScoreResult

_NUM = re.compile(r"[0-9]*\.?[0-9]+")
_RULE_B_SUPPRESSED = frozenset({MOI.AR})  # None also suppresses rule (b)


def _parse_percent(raw: str | None) -> float | None:
    """First numeric token of a yield string as a percent, or None if none found.

    Clean point estimates ('90%', '2.6%') and the LOWER bound of a range ('91-93%' -> 91.0). A
    leading '<' is honored as "just below" (SM 5's idiomatic '<33%' -> band 0.0, not +1.0); a
    leading '>' keeps the number as a conservative floor. The raw string is echoed in provenance.
    """
    if raw is None:
        return None
    m = _NUM.search(raw)
    if m is None:
        return None
    pct = float(m.group())
    if raw.lstrip().startswith("<"):
        pct -= 1e-9
    return pct


def _loc_phe_band(pct: float) -> float:
    """SM 5 Figure 1 phenotype-specificity points. The +2.0 band and the (81,82) sliver are
    inferred (SM 5 gives no explicit anchor) -- see known-gaps.md."""
    if pct < 33.0:
        return 0.0
    if pct <= 50.0:
        return 1.0
    if pct < 68.0:
        return 2.0
    if pct < 82.0:
        return 3.0
    return 4.0


def _non_segregation(case: Case, *, moi: MOI | None) -> list[str]:
    """Reasons (one per triggering relative) a non-segregation was observed; empty if none.

    Two-case rule (MOI-gated): (a) affected + VBC-absent (MOI-independent); (b) unaffected
    VBC-carrier at NEAR_100 penetrance, suppressed for AR and moi None. Uses ``==``/``!=`` so
    UNKNOWN/None never trigger.
    """
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


def reference_score_loc_phe(case: Case, *, moi: MOI | None) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) LOC_PHE phenotype-specificity points (SM 5).

    CSpec is authoritative. Bands ``testing.diagnostic_yield_for_phenotypes`` (SM 5 Figure 1),
    then zeroes on an observed non-segregation. ``moi`` is required for signature parity but is
    consumed ONLY for the AR non-segregation gate -- the band itself has no MOI axis.
    LOC_SEG and the combined LOC +4.0 cap are deferred to LOC-2 / case aggregation.
    """
    prov: list[str] = [
        'LOC: "LOC" is the HOD grouping label. LOC_SEG (co-segregation) and the combined '
        "LOC +4.0 cap are computed in LOC-2 / case aggregation."
    ]
    raw = case.testing.diagnostic_yield_for_phenotypes if case.testing is not None else None
    pct = _parse_percent(raw)
    if pct is None:
        prov.append(f"LOC_PHE: _ND (no parseable diagnostic yield; raw={raw!r})")
        return ScoreResult(parent_code="LOC", provenance=prov, authoritative=False)

    pts = _loc_phe_band(pct)
    prov.append(
        f"LOC_PHE: +{pts} from diagnostic yield (raw={raw!r}); robustness caveats (sample size, "
        "95% CI, methodology match) and most-specific-proband selection not verifiable from "
        "captured inputs -- reference-only."
    )
    if pts > 0.0:
        reasons = _non_segregation(case, moi=moi)
        if reasons:
            prov.append("LOC_PHE: zeroed to 0.0 -- non-segregation observed: " + "; ".join(reasons))
            if moi is MOI.AR:
                prov.append(
                    "LOC_PHE: AR caveat -- an AR non-segregation may reflect another causative "
                    "locus, not benignity; the LOC_SEG -4.0 flip is not applied (LOC_SEG is "
                    "deferred to LOC-2)."
                )
            pts = 0.0
    return ScoreResult(
        parent_code="LOC",
        sub_code_points={"LOC_PHE": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 4: Export** — `src/svcv4_model/scoring/__init__.py`:
    - Add the import `from svcv4_model.scoring.hod.locus import reference_score_loc_phe` **between**
      the `hod.clinical` import block and the `from svcv4_model.scoring.hod.population import ...`
      line (isort: `clinical` < `locus` < `population`).
    - Add `"reference_score_loc_phe"` to `__all__` **between** `"reference_score_intronic_synonymous"`
      and `"reference_score_missense"` (`intronic_synonymous` < `loc_phe` < `missense`).

- [ ] **Step 5: Run** `uv run pytest tests/test_loc_phe_scoring.py -q` — all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/hod/locus.py tests/test_loc_phe_scoring.py \
        src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_score_loc_phe (SM 5 phenotype specificity) -- LOC-1"
```

---

## Task 2: Docs

**Files:** Modify `docs/reference/scoring.md`, `docs/reference/known-gaps.md`

- [ ] **Step 1: `scoring.md`** — add a LOC line (new HOD family): `reference_score_loc_phe` (SM 5)
  — `parent_code="LOC"` grouping label, sub-code `LOC_PHE`; band from
  `testing.diagnostic_yield_for_phenotypes` (`<33→0 / 33-50→+1 / 51-67→+2 / 68-81→+3 / ≥82→+4`);
  non-segregation zeroing (two-case rule, MOI-gated, AR suppresses rule b + caveat); `_ND` for
  absent/unparseable yield. Note LOC_SEG + the combined LOC +4.0 cap are deferred (LOC-2 /
  aggregation).

- [ ] **Step 2: `known-gaps.md`** — add rows (Working-group follow-ups / Model gaps as fits the
  existing table split):
    - LOC_PHE `+2.0` band + the (81,82) boundary + `≥82` vs "83%" are inferred (SM 5 gives no
      explicit anchor for +2.0).
    - The ultra-rare **semantic-similarity +2.0** alt-path is not capturable (no field).
    - Non-segregation **MOI × zygosity** semantics under-specified; rule (b) not yet zygosity-gated
      (an unaffected XLR het carrier can trip it). `relative.sex`/`relative.vbc_zygosity` ARE
      captured — "data available, not yet gated"; suppression stays `{AR}` per the settled design.
    - Under **AR**, SM 5's non-seg note argues zeroing LOC_PHE may over-negate (a non-seg may mean
      another locus explains it); the scorer zeroes conservatively + flags the caveat.
    - Parse: leading `>` treated as a floor; `"1 in N"` ratios misparse (curators record a percent).

- [ ] **Step 3: Build strict** — `uv run mkdocs build --strict` (exit 0).

- [ ] **Step 4: Commit** — `git commit -am "docs: LOC_PHE scoring line + SM 5 known-gaps"`

---

## Task 3: Full quality gates

- [ ] `uv run pytest -q` (all pass, no regressions to the 16+ existing scorers).
- [ ] `uv run ruff check .` (LL 100, clean).
- [ ] Drift gate: `uv run python scripts/export_schemas.py` (or the repo's export entrypoint) then
  `git diff --quiet -- schemas/json docs/workflows/case-model.md` (must be clean — `locus.py` is
  scoring, not re-exported, so NO schema change).
- [ ] `uv run mkdocs build --strict` (exit 0).
- [ ] No scorer schema leaked: `git status` shows no new/changed file under `schemas/json`.
- [ ] Clean tree after commits.

---

## Notes for the implementer

- `reference_score_loc_phe` takes `Case` + required `moi` kwarg (parity with the HOD scorers).
  `moi` is consumed ONLY by `_non_segregation` (AR gate) — the band ignores it.
- **`==`/`!=` for `TriState`, never `is`** — matches `clinical.py`/`population.py`; UNKNOWN/None
  are non-TRUE/non-FALSE so neither rule fires on them.
- `_parse_percent`: `_NUM.search` grabs the first numeric token (range → lower bound); a leading
  `<` subtracts a tiny epsilon so `"<33%"` lands in the band below the boundary.
- `_ND` = absent/unparseable yield (empty `sub_code_points`, `parent_total=None`). `0.0` = present
  yield `<33%` OR a non-seg zeroing — both RECORDED (`sub_code_points={"LOC_PHE": 0.0}`).
- Band `0.0` short-circuits the non-seg check (nothing to zero). A non-seg on an already-zero
  LOC_PHE stays `0.0` (no benign value — benignity is LOC_SEG's `−4.0`, deferred).
- Watch LL 100 on the provenance f-strings (wrap as shown).
- Confirm the exact `export_schemas` entrypoint from a prior scorer PR (the repo's drift-gate
  command) before running Task 3.
