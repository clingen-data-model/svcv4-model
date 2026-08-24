# Reference Scorer — CLN finalize: CCS exclusivity + POP_FRQ gating (Inc 3c) — Design

**Goal:** Add `reference_finalize_cln(cln_subtotal, ccs=None, *, pop_frq_points)` — apply the two
CLN cross-code override rules to the 3b cross-proband CLN subtotal: **CLN_CCS exclusivity** and the
**POP_FRQ gate**. Reference / NON-AUTHORITATIVE; CSpec authoritative. This **completes Increment
3** (the CLN family). The result is the CLN family's contribution to the Inc-4 cross-code combine.

**Architecture:** Extends `src/svcv4_model/scoring/aggregate.py`. Consumes the 3b CLN subtotal
`ScoreResult` + the standalone CLN_CCS `ScoreResult` (from `reference_score_cln_ccs`, which scores
`CaseControlStudyEvidence`, not a `Case`) + `pop_frq_points`; produces the finalized CLN
`ScoreResult`. NOT re-exported from the root (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Source:** SM 4 — CLN_CCS exclusivity L25 ("When CLN_CCS is applied … all other CLN codes … 'NA',
with the sole exception of CLN_DNV"); POP_FRQ gate L27 ("only using Tables 1 and 2 … when the VBC
POP_FRQ is at 0.0 or −1.0"), L10 ("scoring for several CLN codes depends on POP_FRQ being assigned
only 0.0 or −1.0"). The precise branch structure is in **SM 4 Figure 1 (image-only)** — a flagged
gap; the prose thresholds are encoded here.

---

## API

```python
def reference_finalize_cln(
    cln_subtotal: ScoreResult,
    ccs: ScoreResult | None = None,
    *,
    pop_frq_points: float | None,
) -> ScoreResult: ...
```

- `cln_subtotal` — the 3b cross-proband CLN subtotal (`CLN_AFF` / `CLN_DNV` / `CLN_ALT` /
  `CLN_UAF` summed across probands). May be `_ND`.
- `ccs` — the standalone `reference_score_cln_ccs` result (its `CLN_CCS` sub-code, or `_ND`), or
  `None` when no case-control study exists.
- `pop_frq_points` — `WorkflowParameters.pop_frq_points` (field-constrained `≥ −1.0`).

## The two override rules

**CLN_CCS exclusivity (SM 4 L25).** When a `CLN_CCS` sub-code is *present* (scored, incl. `0.0` —
"regardless of the point value assigned"), all other CLN codes become NA **except CLN_DNV**: remove
`CLN_AFF` / `CLN_ALT` / `CLN_UAF`; keep `CLN_CCS` + `CLN_DNV`. (A non-robust study returns `_ND`
from the CCS scorer → no `CLN_CCS` sub-code → exclusivity does not fire.)

**POP_FRQ gate (SM 4 L27/L10).** The CLN pathogenic **counting** codes are awarded only when the
VBC is rare — `pop_frq_points ∈ {0.0, −1.0}`. Otherwise (`None`, or an intermediate like `−0.5`)
NA them: remove `CLN_AFF` **and** `CLN_DNV`. SM 4 states the gate explicitly for CLN_AFF (L27);
extending it to CLN_DNV is the **faithful default** (DNV rides on AFF-counted probands, L143) —
**flagged**, since the exact DNV branch lives in the image-only Figure 1. The benign codes
(`CLN_ALT` / `CLN_UAF`) are **not** POP-gated.

**Combined as an NA-set** (order-independent — both are removals; the union is applied once):

```python
def reference_finalize_cln(cln_subtotal, ccs=None, *, pop_frq_points):
    sub: dict[str, float] = dict(cln_subtotal.sub_code_points)
    if ccs is not None:
        sub.update(ccs.sub_code_points)          # add CLN_CCS if the study scored (else nothing)
    prov = ["CLN: finalize (reference) -- CLN_CCS exclusivity + POP_FRQ gate (SM 4)."]

    na: set[str] = set()
    if "CLN_CCS" in sub:
        na |= {"CLN_AFF", "CLN_ALT", "CLN_UAF"}  # SM 4 L25: keep CLN_CCS + CLN_DNV
        prov.append("CLN: CLN_CCS applied -> NA CLN_AFF/CLN_ALT/CLN_UAF (keep CLN_CCS + CLN_DNV).")
    if pop_frq_points not in (0.0, -1.0):
        na |= {"CLN_AFF", "CLN_DNV"}             # SM 4 L27 (DNV = flagged faithful default)
        prov.append(
            f"CLN: POP_FRQ gate -- pop_frq_points={pop_frq_points} not in {{0.0, -1.0}} -> "
            "NA CLN_AFF + CLN_DNV (SM 4 L27; DNV-gating is the faithful default, Fig 1 image-gap)."
        )

    kept = {c: p for c, p in sub.items() if c not in na}
    if not kept:
        prov.append("CLN: _ND (all CLN codes NA / none scored after finalize).")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)
    total = sum(kept.values())
    prov.append(f"CLN: final {', '.join(f'{c}={p}' for c, p in kept.items())} -> {total}.")
    return ScoreResult(
        parent_code="CLN", sub_code_points=kept, parent_total=total,
        provenance=prov, authoritative=False,
    )
```

## Interaction table (verifies the NA-set logic)

| CLN_CCS present? | rare (`pop∈{0,−1}`)? | kept codes | note |
|---|---|---|---|
| no | yes | AFF, DNV, ALT, UAF (as scored) | nothing removed |
| no | no | ALT, UAF (AFF, DNV removed) | POP gate NAs pathogenic counting codes |
| yes | yes | CCS, DNV | CCS exclusivity NAs AFF/ALT/UAF |
| yes | no | CCS | CCS NAs AFF/ALT/UAF **and** POP NAs DNV → only CCS |

The last row is the faithful reading: even under CCS, an un-rare VBC has its DNV gated (the
`CLN_CCS` exception keeps DNV *from the exclusivity rule*, but the POP gate still applies). Flagged
against Figure 1.

## Semantics / edge cases

- **`ccs=None` or CCS `_ND`** (no `CLN_CCS` sub-code) → exclusivity does not fire.
- **`cln_subtotal` `_ND`** + a scored CCS → result is `{CLN_CCS: …}` (+ POP gate on DNV, which
  isn't present) → just `CLN_CCS`.
- **All-NA → `_ND`**: e.g. an un-rare VBC with only `CLN_AFF`/`CLN_DNV` scored → both NA'd →
  `_ND` (`parent_total=None`).
- **Recorded `0.0`** survives as scored unless NA'd (a `CLN_CCS=0.0` still fires exclusivity — SM 4
  "regardless of the point value").
- **`pop_frq_points` membership** uses the exact floats `{0.0, −1.0}`; `None` and any intermediate
  (`−0.5`) fail the gate (→ NA pathogenic). `−0.0 == 0.0` in Python, so a signed zero passes.
- **Benign codes are never POP-gated** and never excluded by CCS-DNV-exception logic — only the
  CCS-exclusivity NA-set touches `CLN_ALT`/`CLN_UAF`.

## Testing (TDD)

`tests/test_cln_finalize.py` — build `ScoreResult` inputs directly:

1. **No CCS, rare → unchanged:** subtotal `{CLN_AFF:1, CLN_DNV:7, CLN_UAF:-4}`, `ccs=None`,
   `pop_frq_points=0.0` → same codes, `parent_total==4.0`.
2. **No CCS, not rare → AFF+DNV gated:** same subtotal, `pop_frq_points=-0.5` → `{CLN_UAF:-4}`,
   total `-4.0`.
3. **No CCS, pop None → gated:** `pop_frq_points=None` → AFF/DNV removed.
4. **CCS present, rare → CCS+DNV kept, AFF/ALT/UAF NA:** subtotal `{CLN_AFF:1, CLN_DNV:7,
   CLN_ALT:-0.5}` + ccs `{CLN_CCS:4.0}`, `pop=-1.0` → `{CLN_CCS:4.0, CLN_DNV:7.0}`, total `11.0`.
5. **CCS present, not rare → only CCS:** same + `pop=None` → `{CLN_CCS:4.0}` (DNV POP-gated).
6. **CCS 0.0 still fires exclusivity:** ccs `{CLN_CCS:0.0}`, rare → `{CLN_CCS:0.0, CLN_DNV:…}`;
   AFF/ALT/UAF removed.
7. **All-NA → _ND:** subtotal `{CLN_AFF:1, CLN_DNV:7}`, no CCS, `pop=None` → `parent_total is None`.
8. **_ND subtotal + scored CCS:** `_ND` subtotal + `{CLN_CCS:4.0}`, rare → `{CLN_CCS:4.0}`.
9. **ccs `_ND` does not fire:** subtotal `{CLN_AFF:1}`, ccs `_ND` (empty), rare → `{CLN_AFF:1}`.

## Docs

- `docs/reference/scoring.md`: extend the CLN note — `reference_finalize_cln` applies CLN_CCS
  exclusivity (CCS present → NA AFF/ALT/UAF, keep CCS + DNV) and the POP_FRQ gate (award CLN
  pathogenic counting codes only when `pop_frq_points ∈ {0.0, −1.0}`, else NA AFF + DNV), producing
  the CLN family's contribution to the cross-code combine. **CLN is now complete through
  aggregation.**
- `docs/reference/known-gaps.md`: the SM 4 Figure 1 image-only row (added in 3a) already covers the
  exact gate/branch; note the DNV-POP-gating faithful-default in that row (no new row needed).

## Quality gates

`uv run pytest -q`; `uv run ruff check .` (LL 100); drift gate (clean); `uv run mkdocs build
--strict`; no scorer schema leaked; clean tree.

## Non-goals / deferred

- **Inc 4** cross-code combine (PFD + POP + CLN + LOC → one (VBC,MDE) total) — needs the
  global-sum-clamp WG decision.
- **Inc 5** `validate_case` — including the unrelated-proband (distinct `family_id`) enforcement
  the 3b summer assumes.
