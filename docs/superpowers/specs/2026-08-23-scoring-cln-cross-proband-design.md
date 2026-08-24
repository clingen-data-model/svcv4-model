# Reference Scorer — Cross-proband CLN summation (aggregation Inc 3b) — Design

**Goal:** Add `reference_aggregate_cln_cases(results)` — sum each CLN sub-code across the
per-proband `ScoreResult`s (from 3a) into one CLN subtotal for a (VBC, MDE). Reference /
NON-AUTHORITATIVE; CSpec authoritative. This is **Increment 3b**; CLN_CCS exclusivity + POP_FRQ
gating (3c) apply on top.

**Architecture:** Extends `src/svcv4_model/scoring/aggregate.py` (the family-subtotal home).
Consumes and produces `ScoreResult`s. The one structural difference from Inc 2's
`_aggregate_family`: it **sums** a repeated sub-code across inputs (cross-proband is the summing
axis) rather than raising. NOT re-exported from the root (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Source:** SM 4 — "the point values for all unrelated probands should be assessed individually
and then summed" (L29); CLN_AFF sum L80; CLN_DNV sum L147; **unrelated** probands only, related
individuals go to segregation/LOC not CLN counts (L27); **no cross-proband cap** (SM 4 leaves the
CLN_AFF/DNV/total sums unbounded — the only ceiling is the SM 1 classification band, a later layer).

---

## API

```python
def reference_aggregate_cln_cases(results: Iterable[ScoreResult]) -> ScoreResult: ...
```

- **Input:** the per-proband CLN `ScoreResult`s (each from `reference_score_cln_proband`), one per
  **unrelated index proband**. The caller assembles this list as one proband per family (SM 4 L27
  — related individuals are segregation evidence, LOC, not additional CLN counts). `ScoreResult`
  carries no `family_id`, so the *unrelated* precondition is the **caller's responsibility**
  (enforced later at the case-orchestration / `validate_case` layer, not here); this function
  simply sums whatever per-proband results it is given.
- **Output:** one CLN subtotal `ScoreResult` — `parent_code="CLN"`, `sub_code_points` = each
  CLN_* code summed across probands, `parent_total` = the grand sum, no cap. `_ND` (empty
  `sub_code_points`, `parent_total=None`) when no proband scored any CLN sub-code.

## Component

```python
def reference_aggregate_cln_cases(results: Iterable[ScoreResult]) -> ScoreResult:
    merged: dict[str, float] = {}
    n = 0
    for r in results:
        n += 1
        for code, pts in r.sub_code_points.items():
            merged[code] = merged.get(code, 0.0) + pts     # SUM across probands (the 3b axis)
    prov = [
        f"CLN: cross-proband subtotal over {n} proband(s) (reference); assumes unrelated index "
        "probands -- one per family (SM 4 L27); related individuals are LOC segregation, not CLN."
    ]
    if not merged:
        prov.append("CLN: _ND (no CLN sub-code scored across probands)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)
    total = sum(merged.values())
    detail = ", ".join(f"{c}={p}" for c, p in merged.items())
    prov.append(f"CLN: summed {detail} -> {total} (no cross-proband cap, SM 4).")
    return ScoreResult(
        parent_code="CLN",
        sub_code_points=merged,
        parent_total=total,
        provenance=prov,
        authoritative=False,
    )
```

## Semantics / edge cases

- **Summing is the point** (opposite of Inc 2): each CLN_* code accumulates across probands
  (`CLN_AFF` from proband A + `CLN_AFF` from proband B → one summed `CLN_AFF`). **SD mono+biallelic
  summing falls out for free** — 3a routed each proband to one table, both emit `CLN_AFF`, and they
  sum here (SM 4 L80).
- **Pathogenic + benign mix:** a proband contributing `CLN_AFF=+1.0` and another contributing
  `CLN_UAF=−4.0` produce `{CLN_AFF: +1.0, CLN_UAF: −4.0}`, `parent_total=−3.0`. All CLN codes sum
  into the CLN total here; the CLN_CCS **exclusivity** and POP_FRQ **gating** that could zero/NA
  some of them are applied on top in 3c.
- **No cross-proband cap** (SM 4). `parent_total` is the raw grand sum; the SM 1 classification
  band is the only ceiling, applied far downstream.
- **`_ND` inputs contribute nothing** (empty `sub_code_points` add no keys); an all-`_ND` /
  empty list → `_ND` subtotal.
- **Recorded `0.0` counts** (e.g. a `CLN_AFF=0.0` proband) — it creates/keeps the key with a `0.0`
  contribution, so the subtotal is scored (the ScoreResult omit-vs-0.0 contract distinguishes it
  from `_ND`).
- **No duplicate-raise, no input-invariant assert** here — unlike `_aggregate_family`, summing a
  repeated code is the intended behavior, and a per-proband 3a result already satisfies
  `parent_total == sum(sub_code_points)`.

## Testing (TDD)

`tests/test_cln_cross_proband.py` — build inputs with `ScoreResult(...)` directly:

1. **Sum one code across probands:** two `{CLN_AFF: 1.0}` probands → `{CLN_AFF: 2.0}`,
   `parent_total == 2.0`, `parent_code=="CLN"`.
2. **Distinct codes union:** `{CLN_AFF: 1.0}` + `{CLN_DNV: 7.0}` → `{CLN_AFF: 1.0, CLN_DNV: 7.0}`,
   `parent_total == 8.0`.
3. **Same-proband multi-code + cross-proband sum:** proband A `{CLN_AFF: 1.0, CLN_DNV: 7.0}` +
   proband B `{CLN_AFF: 0.5}` → `{CLN_AFF: 1.5, CLN_DNV: 7.0}`, total `8.5`.
4. **Pathogenic + benign mix:** `{CLN_AFF: 1.0}` + `{CLN_UAF: -4.0}` → `parent_total == -3.0`.
5. **`_ND` / empty:** empty list → `parent_total is None`, `sub_code_points == {}`; a single `_ND`
   ScoreResult → `_ND`.
6. **`_ND` + scored mix:** an `_ND` result + `{CLN_AFF: 1.0}` → `{CLN_AFF: 1.0}`.
7. **Recorded `0.0` stays scored:** two `{CLN_AFF: 0.0}` probands → `{CLN_AFF: 0.0}`,
   `parent_total == 0.0` (not `_ND`).

## Docs

- `docs/reference/scoring.md`: extend the CLN note — `reference_aggregate_cln_cases` sums each
  CLN sub-code across unrelated index probands (one per family, SM 4 L27), no cross-proband cap;
  SD mono+biallelic summing falls out; CLN_CCS exclusivity + POP_FRQ gating follow in 3c.
- `docs/reference/known-gaps.md`: no new row (the unrelated-proband precondition is noted; its
  *enforcement* is part of the deferred `validate_case`/orchestration, already tracked).

## Quality gates

`uv run pytest -q`; `uv run ruff check .` (LL 100); drift gate (`export_schemas.py` then
`git diff --quiet -- schemas/json docs/workflows/case-model.md` — clean); `uv run mkdocs build
--strict`; no scorer schema leaked; clean tree.

## Non-goals / deferred

- **3c** CLN_CCS exclusivity (CCS present → NA CLN_AFF/ALT/UAF, keep CCS + CLN_DNV) + POP_FRQ
  gating (award CLN pathogenic codes only when `pop_frq_points ∈ {0.0, −1.0}`).
- **Unrelated-proband enforcement** (distinct `family_id`) — belongs to the case-orchestration /
  `validate_case` layer (Inc 5), not this pure summer.
- **Cross-code combine** (PFD + POP + CLN + LOC) — Inc 4.
