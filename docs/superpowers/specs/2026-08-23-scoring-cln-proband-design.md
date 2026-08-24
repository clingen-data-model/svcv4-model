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
- Unroutable (`XLR` without sex, `moi is None`, or SD `HEMI`/`None` zygosity → defaults to mono
  with a note) → the AFF code is simply not scored (a provenance note).

## Proband category — an explicit gate (spec-review: the scorers do NOT self-gate)

The per-code scorers key on *different* fields, so calling all four blindly double-scores: SM 4
review found `reference_score_cln_uaf` scores on `moi`/`zygosity`/`penetrance` (no affected check)
so it co-fires with CLN_AFF on an affected proband; `reference_score_cln_dnv` scores on
`pheno_specificity` alone (no de-novo check). 3a therefore imposes the SM 4 L17/L29/L76
affected-vs-unaffected split itself:

- **Affected** = `pheno_specificity_for_mde ∈ {SPECIFIC, CONSISTENT}` → the **affected path**: AFF
  (routed) + ALT (unless `moi == AR`, SM 4 L186) + DNV (only if de-novo inferred *and* AFF scored).
  UAF is **not** called.
- **Unaffected / inconsistent** = `pheno_specificity_for_mde` is `INCONSISTENT` or `None` → the
  **unaffected path**: UAF only. AFF/ALT/DNV are **not** called.

**De-novo inference** (settled: infer from relatives; no model change — the `Case` has no `de_novo`
field, a flagged model gap): the proband is de-novo when both parents are present as relatives and
both lack the VBC, with confirmed parentage:

```python
def _is_de_novo(case: Case) -> bool:
    parents = [r for r in case.relatives if r.parent_of_proband == TriState.TRUE]
    return (
        len(parents) >= 2
        and all(r.vbc_exists == TriState.FALSE for r in parents)
        and case.confirmed_parental_relationship == TriState.TRUE
    )
```

CLN_DNV is scored only when the proband is affected, `_is_de_novo(case)` is true, **and** CLN_AFF
was scored for this proband (SM 4 L143: DNV rides on AFF-counted probands).

## Per-proband combine

```python
_AFFECTED = frozenset({PhenoSpecificity.SPECIFIC, PhenoSpecificity.CONSISTENT})

def reference_score_cln_proband(case: Case, *, moi: MOI | None) -> ScoreResult:
    prov = ['CLN: per-proband combine (reference); cross-proband sum + CLN_CCS exclusivity + '
            "POP_FRQ gating deferred to Inc 3b/3c."]
    merged: dict[str, float] = {}
    affected = case.pheno_specificity_for_mde in _AFFECTED

    if affected:
        aff_scorer = _route_cln_aff(case, moi)
        if aff_scorer is None:
            prov.append("CLN_AFF: _ND (unroutable -- moi None, or XLR without a known sex)")
        else:
            is_biallelic = aff_scorer is reference_score_cln_aff_biallelic
            _merge(merged, aff_scorer(case, moi=moi), prov)
            if moi != MOI.AR:                                   # SM 4 L186: no CLN_ALT for AR
                _merge(merged, reference_score_cln_alt(case, moi=moi), prov)
            if "CLN_AFF" in merged and _is_de_novo(case):       # DNV rides on an AFF-counted proband
                _merge(merged, reference_score_cln_dnv(case, moi=moi, is_biallelic=is_biallelic), prov)
            elif "CLN_AFF" in merged:
                prov.append("CLN_DNV: not scored (proband not inferred de-novo)")
    else:
        prov.append("CLN: unaffected/inconsistent path (pheno not SPECIFIC/CONSISTENT) -> CLN_UAF")
        _merge(merged, reference_score_cln_uaf(case, moi=moi), prov)

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

`_merge` copies each scored sub-code (exactly one per CLN per-code scorer) into `merged` and
appends that scorer's real provenance (asserting the skippable preamble to stay robust):

```python
def _merge(merged: dict[str, float], result: ScoreResult, prov: list[str]) -> None:
    for code, pts in result.sub_code_points.items():
        merged[code] = pts               # distinct CLN_* codes; no collision within one proband
    if result.provenance:
        assert result.provenance[0].startswith("CLN:")   # the grouping-label preamble
        prov.extend(result.provenance[1:])
```

**DNV scorer change (drive the fold from routing):** `reference_score_cln_dnv` gains an
`is_biallelic: bool | None = None` kwarg. When `None` it keeps the legacy `moi in {AR, XLR}` fold
(so existing standalone callers/tests are unchanged); 3a passes the **explicit** routing decision
(`aff_scorer is reference_score_cln_aff_biallelic`), which fixes the XLR-male (mono → SPECIFIC
stays `+7.0`) and SD-biallelic (→ CONSISTENT `+4.0`) mis-scores.

## Semantics / edge cases

- **AFF + DNV additivity** (SM 4 L147): a de-novo affected proband scores BOTH `CLN_AFF` and
  `CLN_DNV`; both land in `sub_code_points`, and `parent_total` is their sum (e.g. `+1.0 + +7.0 =
  +8.0`). The AD `+1.0` bound applies to `CLN_AFF` only (already in the Table-1 scorer) — DNV rides
  on top, uncapped here.
- **No per-proband ceiling** beyond what the per-code scorers already return (SM 4/SM 5
  investigation, decision B). `parent_total` is a plain sum of the scored sub-codes.
- **Explicit category gate (not self-gating):** the affected path (AFF/ALT/DNV) and the unaffected
  path (UAF) are mutually exclusive per proband, so CLN_UAF can no longer co-fire with CLN_AFF.
  On the affected path, `CLN_AFF=0.0` and `CLN_ALT=-0.5` may legitimately co-occur (an affected
  proband explained by a P/LP alternate cause) — both are recorded.
- **CLN_ALT excluded for AR** (SM 4 L186 — "should not be used for a MDE with autosomal recessive
  inheritance"). The "multiple genetic contributions" MDE exclusion (also L186) is not modeled →
  known-gaps.
- **Distinct sub-codes:** each CLN per-code scorer emits at most one distinct sub-code
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

1. **AD / XLD route to mono:** an AD (and an XLD) affected SPECIFIC/thorough Case → `CLN_AFF`
   present (Table 1), `parent_code=="CLN"`.
2. **AR routes to biallelic:** an AR affected proband (HOM or HET+compound_het) → `CLN_AFF` from
   Table 2; and **no `CLN_ALT`** even with a P/LP alternate cause (SM 4 L186).
3. **XLR by sex:** same XLR affected proband with `sex=M` → mono; `sex=F` → biallelic; `sex=None`
   → `CLN_AFF` not scored (unroutable note).
4. **SD by zygosity:** SD `HET` (no compound_het) → mono; SD `HOM` → biallelic; SD `HEMI`/`None`
   → mono (default note).
5. **AFF + DNV additivity (de-novo inferred):** an affected SPECIFIC proband with two parent
   relatives both VBC-absent + `confirmed_parental_relationship=TRUE` → BOTH `CLN_AFF` and
   `CLN_DNV`; `parent_total == CLN_AFF + CLN_DNV`.
6. **DNV gated off when NOT de-novo:** the same affected SPECIFIC proband but WITHOUT the
   VBC-absent-parents evidence → `CLN_DNV` absent; provenance "not scored (not inferred de-novo)".
7. **DNV fold from routing (the mis-score fix):** XLR-male SPECIFIC de-novo → `CLN_DNV == +7.0`
   (mono, SPECIFIC stays); SD-biallelic SPECIFIC de-novo → `CLN_DNV == +4.0` (folded to CONSISTENT).
8. **UAF gate — no co-fire with AFF:** an **affected** (`SPECIFIC`) proband that also has
   `age_matched_penetrance=NEAR_100` set → `CLN_UAF` **absent** (affected path); `CLN_AFF` present.
9. **UAF only (unaffected/inconsistent):** a `pheno=None` (or `INCONSISTENT`) unaffected carrier →
   `CLN_UAF` present; AFF/DNV/ALT absent.
10. **moi None → AFF unroutable:** affected proband with `moi=None` → no `CLN_AFF` (unroutable
    note); no DNV (rides on AFF); if nothing scores → `_ND` (`parent_total is None`).
11. **`_ND` proband:** a Case with nothing scoreable → `parent_total is None`, `sub_code_points ==
    {}`.
12. **parent_total == sum invariant** holds on a multi-code result.
13. **DNV legacy fallback unchanged:** `reference_score_cln_dnv(case, moi=AR)` (no `is_biallelic`)
    still folds via `moi` (existing tests unaffected).

## Docs

- `docs/reference/scoring.md`: add a "Per-proband CLN combine" note — `reference_score_cln_proband`
  routes the AFF table (mono/biallelic by MOI/sex/zygosity), calls AFF+DNV+ALT+UAF (self-gating),
  and merges the scored CLN_* sub-codes into one per-proband `ScoreResult`; AFF+DNV are additive;
  the AD `+1.0` is already in Table 1 (no extra ceiling); cross-proband sum + CCS exclusivity +
  POP_FRQ gating follow in 3b/3c.
- `docs/reference/known-gaps.md`: add rows —
    - (Model gap) **No `de_novo` field on `Case`** — CLN_DNV's de-novo trigger is *inferred* (both
      parents present as relatives + both VBC-absent + confirmed parentage). Curators who don't
      capture the parents-are-VBC-negative relatives will under-score CLN_DNV.
    - (Model gap) **No explicit affected-status field** — 3a infers affected from
      `pheno_specificity_for_mde ∈ {SPECIFIC, CONSISTENT}` (else the unaffected/UAF path); a truly
      affected proband with only `INCONSISTENT`/absent phenotype specificity is routed to UAF.
    - (WG follow-up) **SM 4 Figure 1 is image-only** — it authoritatively encodes the
      CCS-vs-counting branch, the exact POP_FRQ gate, and the CLN_DNV exception (all 3c concerns).
      Routing (this increment) is fully in SM 4 *text*.
    - (Not modeled) SM 4 L186 CLN_ALT "multiple genetic contributions" MDE exclusion — only the AR
      exclusion is enforced.

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
