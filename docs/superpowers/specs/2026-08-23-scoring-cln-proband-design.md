# Reference Scorer — Per-proband CLN combine (aggregation Inc 3a) — Design

**Goal:** Add `reference_score_cln_proband(case, *, moi)` — the per-proband CLN combiner: it
**routes** the affected-counting table (mono Table 1 vs biallelic Table 2 per MOI/sex/zygosity),
calls the AFF + DNV + ALT + UAF per-code scorers (each self-gating), and merges whichever CLN_*
sub-codes scored into ONE per-proband `ScoreResult`. Reference / NON-AUTHORITATIVE; CSpec
authoritative. This is **Increment 3a**; cross-proband summation (3b) and CLN_CCS exclusivity +
POP_FRQ gating (3c) follow.

**Architecture:** Extends `src/svcv4_model/scoring/hod/clinical.py` (it already holds all six CLN
per-code scorers; the per-proband combiner belongs with them). Consumes a `Case` + `moi` (routing
needs `moi`/`sex`/`zygosity`, which a `ScoreResult` does not carry); produces a `ScoreResult`
(matching the aggregator contract for 3b/3c). NOT re-exported from the root (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Source:** SM 4 — routing L28 / L77 (X-linked by sex) / L80 (semidominant); AFF+DNV additivity
L143/L147 (PTPN11: +1.0 AFF + +7.0 DNV = +8.0). The AD "+1.0/proband" is a *descriptive fact about
Table 1's top cell*, already enforced by `reference_score_cln_aff_mono` — **no separate ceiling
here** (resolved in the SM4 investigation).

---

## Routing (which AFF table for this proband)

Per SM 4 L28 / L77 / L80 — MOI first, then sex (X-linked), then zygosity (SD):

| MOI | AFF table |
|---|---|
| `AD`, `XLD` | **mono** (Table 1) |
| `AR` | **biallelic** (Table 2) |
| `XLR` | **mono** if `case.sex == M` (XY/hemizygous); **biallelic** if `case.sex == F` (XX); else unroutable |
| `SD` | **biallelic** if `zygosity == HOM` or (`zygosity == HET` and `compound_het_variant` present); else **mono** (heterozygote) |
| `None` | unroutable |

```python
def _route_cln_aff(case: Case, moi: MOI | None) -> Callable[..., ScoreResult] | None:
    if moi in (MOI.AD, MOI.XLD):
        return reference_score_cln_aff_mono
    if moi == MOI.AR:
        return reference_score_cln_aff_biallelic
    if moi == MOI.XLR:
        if case.sex == Sex.M:
            return reference_score_cln_aff_mono
        if case.sex == Sex.F:
            return reference_score_cln_aff_biallelic
        return None                       # XLR needs a known sex (SM 4 L77)
    if moi == MOI.SD:
        biallelic = case.vbc_zygosity == Zygosity.HOM or (
            case.vbc_zygosity == Zygosity.HET and case.compound_het_variant is not None
        )
        return reference_score_cln_aff_biallelic if biallelic else reference_score_cln_aff_mono
    return None                           # moi None -> unroutable
```

- Semidominant "sum mono + biallelic" (SM 4 L80) is a **cross-proband** effect (some probands are
  het→mono, others biallelic→biallelic; both feed the CLN_AFF sub-code and sum in 3b). A single SD
  proband is either het or biallelic, so it routes to exactly one table here.
- Unroutable (`XLR` without sex, `moi is None`) → the AFF code is simply not scored (a provenance
  note); DNV/ALT/UAF are still attempted.

## Per-proband combine

```python
def reference_score_cln_proband(case: Case, *, moi: MOI | None) -> ScoreResult:
    prov = ['CLN: per-proband combine (reference); cross-proband sum + CLN_CCS exclusivity + '
            "POP_FRQ gating deferred to Inc 3b/3c."]
    merged: dict[str, float] = {}

    aff_scorer = _route_cln_aff(case, moi)
    if aff_scorer is None:
        prov.append("CLN_AFF: _ND (unroutable -- moi None, or XLR without a known sex)")
    else:
        _merge(merged, aff_scorer(case, moi=moi), prov)

    for scorer in (reference_score_cln_dnv, reference_score_cln_alt, reference_score_cln_uaf):
        _merge(merged, scorer(case, moi=moi), prov)

    if not merged:
        prov.append("CLN: _ND (no CLN sub-code scored for this proband)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)
    return ScoreResult(
        parent_code="CLN",
        sub_code_points=merged,
        parent_total=sum(merged.values()),
        provenance=prov,
        authoritative=False,
    )
```

`_merge` copies each scored sub-code (there is exactly one per CLN per-code scorer) into `merged`
and appends that scorer's provenance:

```python
def _merge(merged: dict[str, float], result: ScoreResult, prov: list[str]) -> None:
    for code, pts in result.sub_code_points.items():
        merged[code] = pts               # distinct CLN_* codes; no collision within one proband
    prov.extend(result.provenance[1:])   # skip each scorer's own "CLN grouping label" preamble
```

## Semantics / edge cases

- **AFF + DNV additivity** (SM 4 L147): a de-novo affected proband scores BOTH `CLN_AFF` and
  `CLN_DNV`; both land in `sub_code_points`, and `parent_total` is their sum (e.g. `+1.0 + +7.0 =
  +8.0`). The AD `+1.0` bound applies to `CLN_AFF` only (already in the Table-1 scorer) — DNV rides
  on top, uncapped here.
- **No per-proband ceiling** beyond what the per-code scorers already return (SM 4/SM 5
  investigation, decision B). `parent_total` is a plain sum of the scored sub-codes.
- **Self-gating trust** (SM 4 investigation, decision 3): all four scorers are called; each returns
  `_ND` (or `0.0`) when its own preconditions aren't met (UAF only for unaffected; ALT only with a
  P/LP alternate cause; AFF `0.0`/`_ND` for inconsistent/explained). Calling all and merging the
  scored ones cannot double-count — an affected-but-explained proband legitimately yields
  `CLN_AFF=0.0` **and** `CLN_ALT=-0.5`. **Assumes the `Case`'s fields are internally consistent**
  (an unaffected proband should not carry affected-phenotype fields); that is the curator's
  responsibility.
- **Distinct sub-codes:** the four CLN per-code scorers each emit at most one distinct sub-code
  (`CLN_AFF` / `CLN_DNV` / `CLN_ALT` / `CLN_UAF`), so `_merge` never collides within one proband.
  (Cross-*proband* summing of the SAME code is 3b's separate axis.)
- **`_ND` proband:** if no scorer produced a sub-code, return an `_ND` `ScoreResult`
  (`parent_total=None`).
- **Invariant preserved for 3b:** `parent_total == sum(sub_code_points)`, so the 3b cross-proband
  aggregator's input-invariant guard holds.
- **`CLN_CCS` is NOT part of this combine** — it is standalone (`CaseControlStudyEvidence`, not a
  `Case`) and its exclusivity override is applied in 3c.

## Testing (TDD)

`tests/test_cln_proband.py` — build `Case`/`WorkflowParameters` fixtures:

1. **AD routes to mono:** an AD affected proband with a SPECIFIC/thorough Case → `CLN_AFF` present
   (from Table 1), `parent_code=="CLN"`.
2. **AR routes to biallelic:** an AR proband (HOM or HET+compound_het) → `CLN_AFF` from Table 2.
3. **XLR by sex:** same XLR proband with `sex=M` → mono; `sex=F` → biallelic; `sex=None` →
   `CLN_AFF` not scored (unroutable note in provenance), other codes still attempted.
4. **SD by zygosity:** SD `HET` (no compound_het) → mono; SD `HOM` → biallelic.
5. **AFF + DNV additivity:** a de-novo affected proband (confirmed parental, SPECIFIC) →
   `sub_code_points` has BOTH `CLN_AFF` and `CLN_DNV`; `parent_total == CLN_AFF + CLN_DNV`.
6. **ALT alongside AFF=0.0:** affected proband explained by a P/LP alternate cause →
   `CLN_AFF == 0.0` and `CLN_ALT` present (both recorded).
7. **UAF only (unaffected):** an unaffected carrier proband → `CLN_UAF` present; AFF/DNV/ALT not
   scored (or `_ND`).
8. **moi None → AFF unroutable:** `moi=None` → no `CLN_AFF`; provenance notes unroutable; if no
   other code scores → `_ND` (`parent_total is None`).
9. **`_ND` proband:** a Case with nothing scoreable → `parent_total is None`,
   `sub_code_points == {}`.
10. **parent_total == sum invariant** holds on a multi-code result.

## Docs

- `docs/reference/scoring.md`: add a "Per-proband CLN combine" note — `reference_score_cln_proband`
  routes the AFF table (mono/biallelic by MOI/sex/zygosity), calls AFF+DNV+ALT+UAF (self-gating),
  and merges the scored CLN_* sub-codes into one per-proband `ScoreResult`; AFF+DNV are additive;
  the AD `+1.0` is already in Table 1 (no extra ceiling); cross-proband sum + CCS exclusivity +
  POP_FRQ gating follow in 3b/3c.
- `docs/reference/known-gaps.md`: add a Working-Group-follow-up row — **SM 4 Figure 1 is
  image-only**; it authoritatively encodes the CCS-vs-counting branch, the exact POP_FRQ gate, and
  the CLN_DNV exception. Routing (this increment) is fully in SM 4 *text*; only the 3c gate/branch
  depends on the figure.

## Quality gates

`uv run pytest -q`; `uv run ruff check .` (LL 100); drift gate (`export_schemas.py` then
`git diff --quiet -- schemas/json docs/workflows/case-model.md` — clean; clinical.py additions are
scoring, not re-exported); `uv run mkdocs build --strict`; no scorer schema leaked; clean tree.

## Non-goals / deferred

- **3b** cross-proband summation (sum each CLN_* across unrelated probands; distinct `family_id`;
  SD mono+biallelic summing falls out) — a cross-proband summing aggregator (SUMS duplicate
  sub-codes, unlike Inc 2's raise-on-duplicate).
- **3c** CLN_CCS exclusivity (CCS present → NA AFF/ALT/UAF, keep CCS + DNV) + POP_FRQ gating (award
  CLN pathogenic codes only when `pop_frq_points ∈ {0.0, −1.0}`; the DNV-gating branch is behind
  SM 4 Figure 1 — default to gating both, flagged).
- **Cross-code combine** (PFD + POP + CLN + LOC) and the global-sum clamp — Inc 4.
