# Reference Scorer — Cross-code combine (aggregation Inc 4) — Design

**Goal:** Add `reference_combine_case(subtotals)` — sum the family subtotals (a PFD parent-code
result + the POP / CLN / LOC subtotals) into one **(VBC, MDE) total**, the number
`reference_classify` (Inc 1) then bands. Reference / NON-AUTHORITATIVE; CSpec authoritative.
**Unclamped** (settled: faithful to SM 1's open-ended Pathogenic `≥ +10` / Benign `≤ −4`; the
GA4GH JSON `scale` cap of `[−8, +10]` is a display concern, flagged).

**Architecture:** Extends `src/svcv4_model/scoring/aggregate.py`. Consumes the per-family
`ScoreResult`s (and the missense `MissenseScoreResult`) and produces one combined `ScoreResult`
whose `parent_total` is the final sum and whose `sub_code_points` is the per-family breakdown. NOT
re-exported from the root (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Source:** the main SVCv4 spec — evidence categories "sum directly to a posterior probability of
pathogenicity"; the summands are the one PFD parent code (per-variant) + POP + CLN + LOC. No global
sum cap in any supplement (the SM 1 band is the only ceiling; the clamp question is a flagged WG
follow-up already in known-gaps).

---

## What combines

For one (VBC, MDE), the final total is the sum of at most four family contributions:

| Family | Source | `parent_code` / total |
|---|---|---|
| PFD parent | the variant-type workflow scorer | a real SVCv4 code `NUL`/`CDS`/`SPL`/`MIS`; `ScoreResult.parent_total`. **Missense** returns a `MissenseScoreResult` → use `applied_parent_code` + `applied_total` (the take-higher outcome). |
| POP | `reference_aggregate_pop` | label `"POP"`, `parent_total` |
| CLN | `reference_finalize_cln` | label `"CLN"`, `parent_total` |
| LOC | `reference_aggregate_loc` | label `"LOC"`, `parent_total` |

Reconciling the two `parent_code` namespaces (real PFD codes vs the POP/CLN/LOC display labels) is
resolved **here** simply by keying the breakdown on whatever `parent_code`/`applied_parent_code`
each input carries — a variant has exactly one PFD code, so the four keys are distinct.

## API

```python
def reference_combine_case(
    subtotals: Iterable[ScoreResult | MissenseScoreResult],
) -> ScoreResult: ...
```

- **Input:** any subset of the four family results (order-independent). A family that is `_ND`
  (`parent_total is None`) contributes **0** (it is simply absent from the sum and the breakdown).
- **Output:** one `ScoreResult` — `parent_code=None` (this is the whole-case total, not a single
  code), `sub_code_points` = the per-family breakdown `{code: family_total}`, `parent_total` = the
  grand sum (unclamped), provenance describing the components + the clamp flag. `_ND` (empty
  breakdown, `parent_total=None`) when no family scored.

Chaining to the band (Inc 1): `reference_classify(reference_combine_case([...]).parent_total)`.

## Component

```python
from svcv4_model.scoring.result import MissenseScoreResult, ScoreResult

def _family_total(r: ScoreResult | MissenseScoreResult) -> tuple[str | None, float | None]:
    if isinstance(r, MissenseScoreResult):
        return r.applied_parent_code, r.applied_total   # take-higher MIS_/SPL_ outcome
    return r.parent_code, r.parent_total

def reference_combine_case(
    subtotals: Iterable[ScoreResult | MissenseScoreResult],
) -> ScoreResult:
    breakdown: dict[str, float] = {}
    prov = [
        "CASE: cross-code combine (reference) -- PFD parent + POP + CLN + LOC summed; "
        "UNCLAMPED (SM 1 Pathogenic is open-ended >=+10; the GA4GH scale 10/-8 is a display "
        "concern -- see known-gaps)."
    ]
    for r in subtotals:
        code, total = _family_total(r)
        if total is None:
            continue                                    # _ND family -> contributes 0
        key = code if code is not None else "?"
        if key in breakdown:
            raise ValueError(f"CASE: duplicate family code {key!r} across subtotals.")
        breakdown[key] = total
    if not breakdown:
        prov.append("CASE: _ND (no family scored).")
        return ScoreResult(provenance=prov, authoritative=False)
    grand = sum(breakdown.values())
    detail = ", ".join(f"{c}={p}" for c, p in breakdown.items())
    prov.append(f"CASE: final total {grand} ({detail}).")
    return ScoreResult(
        sub_code_points=breakdown,
        parent_total=grand,
        provenance=prov,
        authoritative=False,
    )
```

## Semantics / edge cases

- **`_ND` family contributes 0** — a family with `parent_total is None` (no data) is skipped; it
  neither adds to the sum nor appears in the breakdown. (Distinct from a scored `0.0`, which IS a
  component keyed with value `0.0`.)
- **Missense normalization** — a `MissenseScoreResult` is read via `applied_parent_code` /
  `applied_total` (its take-higher result); a `MissenseScoreResult` whose `applied_total is None`
  contributes 0.
- **Distinct family keys** — POP/CLN/LOC and the single PFD code are distinct; a **duplicate**
  key (e.g. two PFD results, or the same subtotal passed twice) raises `ValueError` (caller bug),
  mirroring the Inc-2 family aggregator.
- **Unclamped** — `grand` is the raw sum; e.g. `NUL=+10` + `CLN=+8` → `+18` (→ Pathogenic). No cap
  (settled decision; flagged vs the GA4GH scale).
- **All-`_ND` / empty** → `_ND` combined result (`parent_total=None`).
- **`parent_code=None`** on the combined result — it is the whole-case total, not a single code;
  the per-family breakdown lives in `sub_code_points`.

## Testing (TDD)

`tests/test_combine_case.py`:

1. **Four families sum:** `NUL(ScoreResult parent_total=+10)` + POP(−1) + CLN(+4) + LOC(+4) →
   `parent_total == +17`; breakdown has all four keys.
2. **Missense take-higher input:** a `MissenseScoreResult(applied_parent_code="MIS",
   applied_total=+9)` + CLN(+1) → `parent_total == +10`; breakdown `{MIS: 9.0, CLN: 1.0}`.
3. **`_ND` family skipped:** POP(+0.0 scored) + CLN(`_ND`, parent_total None) → breakdown
   `{POP: 0.0}` (CLN absent), `parent_total == 0.0`.
4. **Unclamped high/low:** NUL(+10) + CLN(+8) → `+18`; a benign case POP(−6) + PFD(−8) → `−14`.
5. **Duplicate family raises:** two `ScoreResult(parent_code="CLN", parent_total=…)` →
   `pytest.raises(ValueError)`.
6. **All `_ND` / empty:** empty list, and a list of only `_ND` results → `parent_total is None`,
   `sub_code_points == {}`.
7. **Missense applied_total None contributes 0:** `MissenseScoreResult(applied_total=None)` + CLN(+2)
   → `{CLN: 2.0}`, total `2.0`.
8. **Chains to the band:** `reference_classify(reference_combine_case([...]).parent_total)` yields
   the expected category for a representative total (e.g. `+17 → PATHOGENIC`).

## Docs

- `docs/reference/scoring.md`: add a "Cross-code combine" note — `reference_combine_case` sums the
  PFD-parent + POP + CLN + LOC subtotals into the (VBC, MDE) total (an `_ND` family contributes 0;
  missense uses its applied take-higher total), **unclamped** (flagged vs the GA4GH scale), which
  `reference_classify` then bands. This is the point where all evidence families meet.
- `docs/reference/known-gaps.md`: the global-sum-clamp WG row (added with the band) already covers
  the unclamped choice — extend it to note Inc 4 sums unclamped.

## Quality gates

`uv run pytest -q`; `uv run ruff check .` (LL 100); drift gate (clean); `uv run mkdocs build
--strict`; no scorer schema leaked; clean tree.

## Non-goals / deferred

- **Inc 5** `validate_case` — applicability r/o/c/x enforcement + the unrelated-proband / distinct
  `family_id` check + `pop_frq_points ≥ −1` / `gene_disease_validity` preconditions.
- **The `family` enum** to formally reconcile display-labels vs real codes — not needed (the
  combine keys on the carried `parent_code`); revisit only if a consumer needs typed families.
- **Multi-MDE (SM 21)** orchestration — a later outer layer.
