# Reference Scorer — POP + LOC family subtotals (aggregation Inc 2) — Design

**Goal:** Add the first **family-subtotal** aggregators — `reference_aggregate_pop` and
`reference_aggregate_loc` — that collapse a family's per-code `ScoreResult`(s) into one subtotal
`ScoreResult`, applying the family cap (LOC `+4.0`; POP none). Reference / NON-AUTHORITATIVE;
CSpec authoritative. This is **Increment 2** of the case-aggregation subsystem; it establishes the
input-shape convention (aggregators **consume and produce `ScoreResult`s**) on the two simplest
families before CLN (Inc 3) and the cross-code combine (Inc 4).

**Architecture:** New module `src/svcv4_model/scoring/aggregate.py`. Pure functions; depend only
on `ScoreResult`. NOT re-exported from the root package (no schema). A shared private
`_aggregate_family(results, *, family, cap)` does the work; the two public functions are thin
family-configured wrappers.

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Sources:** SM 3 (POP — POP_FRQ + POP_HMZ are independent case-level codes, **no combined cap**);
SM 5 L38 (LOC — LOC_PHE + LOC_SEG summed then **capped at +4.0**, coded as combined `LOC_0.0..+4.0`).

---

## Input-shape convention (decision, applied here first)

Aggregators **consume the per-code `ScoreResult`(s)** a scorer already produced and **return a
`ScoreResult`** (the family subtotal). This keeps the whole pipeline uniform:

```
per-code scorer(s) -> ScoreResult(s)  ──►  family aggregator -> subtotal ScoreResult
      (Inc 0/LOC-1)                              (Inc 2, here)
                                          ──►  cross-code combine -> final total (Inc 4)
                                          ──►  reference_classify -> band (Inc 1, done)
```

The `parent_code` display-label vs real-SVCv4-code reconciliation (POP/CLN/LOC are labels; PFD
NUL/CDS/SPL/MIS are real) is **not needed here** — each family aggregator is told its family
explicitly — and is deferred to Inc 4 where PFD and HOD totals actually mix.

## What each family needs

| Family | Scorer output today | Aggregation | Cap |
|---|---|---|---|
| **POP** | ONE `ScoreResult` (`parent_code="POP"`, sub-codes `POP_FRQ`/`POP_HMZ`, `parent_total`=their sum) | pass-through: re-sum the sub-codes | **none** (SM 3) |
| **LOC** | `LOC_PHE` `ScoreResult` today; a `LOC_SEG` one later (LOC-2, blocked on SM 5 Fig 2) | sum `LOC_PHE` + `LOC_SEG` sub-codes | **`+4.0`** (SM 5 L38) |

> The LOC `+4.0` cap **cannot bind today**: `LOC_PHE` alone is `0..+4`, so `min(LOC_PHE, +4) ==
> LOC_PHE`. The cap is built forward-looking (for when `LOC_SEG` lands) and is exercised in tests
> with a synthetic second LOC sub-code. POP aggregation is a pass-through today (its scorer already
> subtotals) — included for a uniform family-subtotal layer that Inc 4 consumes.

> **LOC negative / non-segregation semantics are OUT OF SCOPE here.** SM 5 codes the combined
> LOC as **`LOC_0.0 to LOC_+4.0`** (L38) — a positive combine of two `0..+4` codes. The `−4.0`
> non-segregation is a **separate benign signal** that SM 5 (L37) applies by *zeroing the positive
> points and assigning `−4.0`* — a **replacement, not a summand**. This family aggregator computes
> only the **positive combine** (`min(LOC_PHE + LOC_SEG, +4.0)`); the `−4.0` non-seg flip is
> computed elsewhere in LOC-2 and is **not** fed through this sum. Inputs are therefore assumed
> within each code's documented non-negative range; this function does not define negative-LOC
> semantics.

## API

```python
def reference_aggregate_pop(results: Iterable[ScoreResult]) -> ScoreResult: ...
def reference_aggregate_loc(results: Iterable[ScoreResult]) -> ScoreResult: ...
```

Each returns a subtotal `ScoreResult`:
- `parent_code` = the family label (`"POP"` / `"LOC"`).
- `sub_code_points` = the union of the inputs' sub-code points (per-code values preserved for
  transparency — **not** capped).
- `parent_total` = the capped sum (raw sum for POP; `min(raw, +4.0)` for LOC).
- `provenance` = the family label note, the per-code contributions, the raw sum, and whether the
  cap bound.
- `authoritative=False`.

## Component — `_aggregate_family`

```python
from collections.abc import Iterable

def _aggregate_family(results: Iterable[ScoreResult], *, family: str, cap: float | None) -> ScoreResult:
    merged: dict[str, float] = {}
    for r in results:
        # Input invariant (holds for POP/LOC): parent_total == sum(sub_code_points). Guard so a
        # future sub-capping scorer (parent_total != sum) fails loudly rather than drifting.
        if r.parent_total is not None and abs(r.parent_total - sum(r.sub_code_points.values())) > 1e-9:
            raise ValueError(
                f"{family}: input parent_total {r.parent_total} != sum(sub_code_points) "
                f"{sum(r.sub_code_points.values())} -- this family aggregator assumes they match."
            )
        for code, pts in r.sub_code_points.items():
            if code in merged:                              # singleton families -> a dup is a caller bug
                raise ValueError(f"{family}: duplicate sub-code {code!r} across inputs.")
            merged[code] = pts
    prov = [f'{family}: "{family}" is the HOD grouping label; family subtotal (reference).']
    if not merged:
        prov.append(f"{family}: _ND (no scored sub-codes)")
        return ScoreResult(parent_code=family, provenance=prov, authoritative=False)
    raw = sum(merged.values())
    total = raw if cap is None else min(raw, cap)
    detail = ", ".join(f"{c}={p}" for c, p in merged.items())
    held: dict[str, float] = {}
    if cap is not None and raw > cap:
        held = {f"{family}_raw": raw}                       # keep the uncapped sum machine-readable
        prov.append(f"{family}: subtotal capped {raw} -> {total} (+{cap} cap): {detail}")
    else:
        prov.append(f"{family}: subtotal {total} ({detail}; cap {cap})")
    return ScoreResult(
        parent_code=family,
        sub_code_points=dict(merged),
        held_combined=held,
        parent_total=total,
        provenance=prov,
        authoritative=False,
    )


def reference_aggregate_pop(results): return _aggregate_family(results, family="POP", cap=None)
def reference_aggregate_loc(results): return _aggregate_family(results, family="LOC", cap=4.0)
```

Design notes from spec-review:
- **Duplicate sub-code raises** (POP_FRQ/POP_HMZ/LOC_PHE/LOC_SEG are locus-/case-level singletons
  within one (VBC,MDE) — a repeat is a caller error, e.g. Inc 4 passing a result twice, not a
  legitimate sum). CLN cross-*proband* summing (same code, many probands) is a different axis, in
  Inc 3.
- **Input invariant asserted** (`parent_total == sum(sub_code_points)`), true for POP/LOC today;
  the aggregator re-derives the total from the merged sub-codes, so this guard makes any future
  sub-capping scorer fail loudly instead of silently diverging.
- **The uncapped sum is preserved** in `held_combined[f"{family}_raw"]` when the cap binds
  (machine-readable for Inc 4 / audit), not only in prose. Inputs' own `held_combined` is **not**
  merged forward (POP/LOC scorers leave it empty); the subtotal starts fresh.
- Relies on the `ScoreResult` **input contract** (a No-Data sub-code is omitted, never recorded as
  `0.0`), so `if not merged` correctly distinguishes `_ND` from a recorded `0.0`.

## Semantics / edge cases

- **`_ND` propagation:** if every input is `_ND` (empty `sub_code_points`) — or the iterable is
  empty — the subtotal is `_ND` (empty `sub_code_points`, `parent_total=None`). A subtotal is
  scored only when at least one sub-code was scored.
- **A single `_ND` among scored inputs** contributes nothing (its empty `sub_code_points` add no
  keys); the subtotal reflects the scored ones.
- **Recorded `0.0` sub-codes** (e.g. `LOC_PHE=0.0`, `POP_HMZ=0.0`) ARE included — they are scored,
  not `_ND` — so the subtotal is scored (`parent_total` a real `0.0`, not `None`).
- **Cap is an upper bound** (`min`): LOC `+4.0` clamps the pathogenic side. POP is benignity-only
  (negative) with no cap. The LOC aggregator computes only the **positive combine**; the `−4.0`
  non-seg benign flip is a separate LOC-2 signal (not a summand here — see the LOC note above).
- **Same sub-code in two inputs raises** `ValueError` (singleton families; a repeat is a caller
  bug). CLN cross-*proband* summing (same code, many probands) is a different axis, in Inc 3.
- **Input invariant** `parent_total == sum(sub_code_points)` is asserted per input (raises on
  violation) so a future sub-capping scorer cannot drift silently.

## Testing (TDD)

`tests/test_aggregate_pop_loc.py` — build inputs with `ScoreResult(...)` directly (the aggregators
consume ScoreResults, so no scorer calls needed):

1. **POP pass-through:** `ScoreResult(parent_code="POP", sub_code_points={"POP_FRQ": -3.0,
   "POP_HMZ": -0.5}, parent_total=-3.5)` → aggregate → `parent_total == -3.5`, both sub-codes
   present, `parent_code=="POP"`, `held_combined == {}` (no cap).
2. **POP single-code / real-0.0:** `{"POP_FRQ": 0.0}` (parent_total 0.0) → `parent_total == 0.0`
   (scored, not `_ND`).
3. **POP recorded `POP_HMZ=0.0` only:** `{"POP_HMZ": 0.0}` (parent_total 0.0) → `parent_total ==
   0.0`, `sub_code_points == {"POP_HMZ": 0.0}` (a recorded 0.0 stays scored, not `_ND`).
4. **LOC pass-through (cap doesn't bind):** one `ScoreResult(parent_code="LOC",
   sub_code_points={"LOC_PHE": 4.0}, parent_total=4.0)` → `parent_total == 4.0`,
   `held_combined == {}`.
5. **LOC cap binds (synthetic LOC_SEG):** two results `{"LOC_PHE": 4.0}` + `{"LOC_SEG": 3.0}` →
   raw 7.0 → `parent_total == 4.0` (capped); both sub-codes preserved in `sub_code_points`;
   `held_combined == {"LOC_raw": 7.0}`; provenance says "capped".
6. **`_ND` propagation:** empty iterable → `parent_total is None`, `sub_code_points == {}`; also a
   single `_ND` `ScoreResult` (no sub-codes) → `_ND`.
7. **`_ND` + scored mix:** an `_ND` LOC result + a `{"LOC_PHE": 2.0}` result → `parent_total ==
   2.0`.
8. **Duplicate sub-code raises:** two results each `{"LOC_PHE": 2.0}` →
   `pytest.raises(ValueError)`.
9. **Input-invariant guard raises:** a malformed `ScoreResult(sub_code_points={"POP_FRQ": -3.0},
   parent_total=-1.0)` (total ≠ sum) → `pytest.raises(ValueError)`.

## Docs

- `docs/reference/scoring.md`: add a short "Family subtotals (aggregation)" note — POP
  (`reference_aggregate_pop`, no cap) and LOC (`reference_aggregate_loc`, `+4.0` cap) collapse
  per-code results into a subtotal `ScoreResult`; note the LOC cap is inert until `LOC_SEG` lands,
  and that CLN cross-proband aggregation + the cross-code combine follow.
- `docs/reference/known-gaps.md`: no new row (POP no-cap and LOC `+4.0` cap are both in-text).

## Quality gates

`uv run pytest -q`; `uv run ruff check .` (LL 100); drift gate (`export_schemas.py` then
`git diff --quiet -- schemas/json docs/workflows/case-model.md` — clean; `aggregate.py` is not
re-exported); `uv run mkdocs build --strict`; no scorer schema leaked; clean tree.

## Non-goals / deferred

- **CLN cross-proband aggregation + exclusivity** — Inc 3 (the substantive family; different axis:
  same code across probands).
- **Cross-code combination** (PFD + POP + CLN + LOC → one total) and the `parent_code`
  label-vs-real reconciliation — Inc 4; also settles the global-sum-clamp WG question.
- **`LOC_SEG` itself** — LOC-2, blocked on SM 5 Figure 2 point values (image-only).
- **`validate_case`** applicability enforcement — Inc 5.
