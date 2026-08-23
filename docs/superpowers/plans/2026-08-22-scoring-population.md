# Reference Scorer — Population (POP, SM 3) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_population` (SM 3): POP_FRQ (FAF/DAFT fold bands) + POP_HMZ (MOI-dependent occurrence weights). The first HOD scorer — establishes `scoring/hod/`.

**Architecture:** A standalone two-code scorer (no PFD/SPL pipeline). Reuses `ScoreResult`. `moi` is a required kwarg (POP_HMZ only). Non-authoritative; scoring stays out of root `__all__` (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Key facts (spec-verified):** FBN1 fixture DAFT 0.000118 → 1.5×/5×/15× at 0.000177/0.000590/0.001770; top band inclusive (`≥15×`); each band's lower edge inclusive (flagged). POP_HMZ weight is **AD −1.0 / else −0.5** per SM 3 **Table 7** (the prose's uniform −0.5 is wrong — flagged; `pop.md` corrected).

---

## Task 1: `reference_score_population` (TDD)

**Files:** Create `src/svcv4_model/scoring/hod/__init__.py`, `src/svcv4_model/scoring/hod/population.py`, `tests/test_population_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_population_scoring.py`

```python
"""Tests for reference_score_population (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import MOI, TriState
from svcv4_model.population import PopulationEvidence
from svcv4_model.scoring import reference_score_population

_DAFT = 0.000118  # FBN1-Marfan golden fixture (SM 3 L28)


def _frq(faf: float | None, daft: float | None = _DAFT) -> PopulationEvidence:
    return PopulationEvidence(faf=faf, daft=daft)


def test_pop_frq_fbn1_golden_bands() -> None:
    # SM 3 L28 worked example: DAFT 0.000118
    for faf, expected in [
        (0.000100, 0.0),    # < 0.000177 (< 1.5x)
        (0.000300, -1.0),   # 0.000177 .. 0.000590
        (0.001000, -3.0),   # 0.000590 .. 0.001770
        (0.001770, -6.0),   # = 15x, inclusive
        (0.002000, -6.0),   # > 15x
    ]:
        r = reference_score_population(_frq(faf), moi=MOI.AD)
        assert r.parent_code == "POP"
        assert r.sub_code_points["POP_FRQ"] == expected


def test_pop_frq_boundary_assumption_inclusive_lower() -> None:
    # exactly 1.5x and 5x -> the more-benign band (flagged assumption)
    assert reference_score_population(_frq(0.000177), moi=MOI.AD).sub_code_points["POP_FRQ"] == -1.0
    assert reference_score_population(_frq(0.000590), moi=MOI.AD).sub_code_points["POP_FRQ"] == -3.0


def test_pop_frq_nd() -> None:
    for ev in [_frq(None), _frq(0.001, daft=None), _frq(0.001, daft=0.0)]:
        r = reference_score_population(ev, moi=MOI.AD)
        assert "POP_FRQ" not in r.sub_code_points


def test_pop_hmz_ar_minus_half_per_occurrence() -> None:
    ev = PopulationEvidence(homozygote_count=3, hmz_eligible=TriState.TRUE)
    r = reference_score_population(ev, moi=MOI.AR)
    assert r.sub_code_points["POP_HMZ"] == -1.0  # -0.5 x (3 - 1)


def test_pop_hmz_ad_minus_one_per_occurrence() -> None:
    # SM 3 Table 7: AD homozygous is -1.0/observation (NOT the prose -0.5)
    ev = PopulationEvidence(homozygote_count=3, hmz_eligible=TriState.TRUE)
    r = reference_score_population(ev, moi=MOI.AD)
    assert r.sub_code_points["POP_HMZ"] == -2.0  # -1.0 x (3 - 1)


def test_pop_hmz_xlinked_counts_hemizygotes() -> None:
    ev = PopulationEvidence(
        homozygote_count=1, hemizygote_count=2, hmz_eligible=TriState.TRUE
    )
    r = reference_score_population(ev, moi=MOI.XLR)
    assert r.sub_code_points["POP_HMZ"] == -1.0  # count 3 -> -0.5 x 2


def test_pop_hmz_hemizygotes_ignored_off_xlinked() -> None:
    ev = PopulationEvidence(
        homozygote_count=1, hemizygote_count=5, hmz_eligible=TriState.TRUE
    )
    r = reference_score_population(ev, moi=MOI.AD)
    assert r.sub_code_points["POP_HMZ"] == 0.0  # count 1 (hemi ignored) -> 1 free


def test_pop_hmz_nd_when_ineligible_or_no_counts() -> None:
    ineligible = PopulationEvidence(homozygote_count=3, hmz_eligible=TriState.FALSE)
    no_counts = PopulationEvidence(hmz_eligible=TriState.TRUE)
    assert "POP_HMZ" not in reference_score_population(ineligible, moi=MOI.AR).sub_code_points
    assert "POP_HMZ" not in reference_score_population(no_counts, moi=MOI.AR).sub_code_points


def test_parent_total_sums_recorded_codes() -> None:
    ev = PopulationEvidence(
        faf=0.002000, daft=_DAFT, homozygote_count=3, hmz_eligible=TriState.TRUE
    )
    r = reference_score_population(ev, moi=MOI.AR)
    assert r.sub_code_points["POP_FRQ"] == -6.0
    assert r.sub_code_points["POP_HMZ"] == -1.0
    assert r.parent_total == -7.0


def test_empty_is_all_nd() -> None:
    r = reference_score_population(PopulationEvidence(), moi=MOI.AD)
    assert r.parent_code == "POP"
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect ModuleNotFoundError.** `uv run pytest tests/test_population_scoring.py -q`

- [ ] **Step 3: Create the package marker `scoring/hod/__init__.py`**

```python
"""Reference (non-authoritative) scorers for Human Observational Data (HOD) evidence."""
```

- [ ] **Step 4: Implement `scoring/hod/population.py`**

```python
"""Reference (non-authoritative) scorer for Population evidence (SM 3, POP_FRQ + POP_HMZ)."""

from __future__ import annotations

from svcv4_model.case import MOI, TriState
from svcv4_model.population import PopulationEvidence
from svcv4_model.scoring.result import ScoreResult

_X_LINKED = frozenset({MOI.XLD, MOI.XLR})


def _pop_frq_points(faf: float | None, daft: float | None) -> float | None:
    """POP_FRQ benignity by FAF/DAFT fold (SM 3). None when no fold is computable."""
    if faf is None or daft is None or daft <= 0:
        return None
    fold = faf / daft
    if fold < 1.5:
        return 0.0
    if fold < 5.0:
        return -1.0
    if fold < 15.0:
        return -3.0
    return -6.0


def _pop_hmz_points(evidence: PopulationEvidence, moi: MOI | None) -> float | None:
    """POP_HMZ benignity from eligible occurrences (SM 3 Table 7). None when not applicable."""
    if evidence.hmz_eligible != TriState.TRUE:
        return None
    homo = evidence.homozygote_count
    hemi = evidence.hemizygote_count if moi in _X_LINKED else None
    if homo is None and hemi is None:
        return None
    count = (homo or 0) + (hemi or 0)
    weight = -1.0 if moi == MOI.AD else -0.5
    return weight * max(count - 1, 0)


def reference_score_population(
    evidence: PopulationEvidence,
    *,
    moi: MOI | None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Population points (SM 3): POP_FRQ + POP_HMZ.

    CSpec is authoritative. Both codes are benignity-only (<= 0). ``moi`` is required (consumed
    only by POP_HMZ, for X-linked hemizygote counting; pass explicit None when unknown ->
    homozygotes only). ``parent_code`` is the grouping label ``"POP"`` (not an SVCv4 parent code);
    ``parent_total`` is the sum of the recorded sub-codes (a convenience subtotal, no SM 3 cap).
    """
    prov: list[str] = [
        'POP: "POP" is a grouping label (POP_FRQ/POP_HMZ are independent case-level codes), '
        "not an SVCv4 parent code; parent_total is a convenience subtotal (no SM 3 combined cap)."
    ]
    sub: dict[str, float] = {}

    frq = _pop_frq_points(evidence.faf, evidence.daft)
    if frq is None:
        prov.append("POP_FRQ: _ND (no FAF and/or DAFT; absent-in-db is faf=0.0 -> 0.0, not None)")
    else:
        sub["POP_FRQ"] = frq
        prov.append(
            f"POP_FRQ: FAF {evidence.faf} / DAFT {evidence.daft} = "
            f"{evidence.faf / evidence.daft:.3g}x -> {frq} "
            "(bands <1.5x/5x/15x, lower edge inclusive -- SM 3 boundary assumption)"
        )

    hmz = _pop_hmz_points(evidence, moi)
    if hmz is None:
        prov.append("POP_HMZ: _ND (not hmz_eligible, or no homozygote/hemizygote count)")
    else:
        sub["POP_HMZ"] = hmz
        weight = -1.0 if moi == MOI.AD else -0.5
        prov.append(
            f"POP_HMZ: {hmz} (weight {weight}/obs from the 2nd -- SM 3 Table 7; "
            "AD -1.0 vs prose -0.5 conflict, encoded to Table 7)"
        )

    total = sum(sub.values()) if sub else None
    if total is not None:
        prov.append(f"POP total: {total} (POP_FRQ + POP_HMZ; no SM 3 combined cap)")

    return ScoreResult(
        parent_code="POP",
        sub_code_points=sub,
        parent_total=total,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 5: Add the export** — `scoring/__init__.py`: import (after `nonsense`, before `start_lost`) + `"reference_score_population"` in `__all__` (same position).

- [ ] **Step 6: Run** `uv run pytest tests/test_population_scoring.py -q` — all PASS.

- [ ] **Step 7: Commit**

```bash
git add src/svcv4_model/scoring/hod/ tests/test_population_scoring.py src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_score_population (SM 3 POP_FRQ + POP_HMZ)"
```

---

## Task 2: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — after the last Missense bullet:

```markdown
- **Population** (SM 3) — `reference_score_population`, the first **HOD** scorer (lives in
  `scoring/hod/`). Two benignity-only codes: **POP_FRQ** (FAF/DAFT fold bands `<1.5×`/`5×`/`15×`
  → `0/−1/−3/−6`, each band's lower edge inclusive — a flagged SM 3 boundary gap) and **POP_HMZ**
  (`−0.5`/observation from the 2nd, **`−1.0` for AD** per SM 3 Table 7; X-linked counts
  hemizygotes — needs the `moi`). `parent_code="POP"` is a grouping label (not an SVCv4 parent
  code); `parent_total` sums the two.
```

- [ ] **Step 2: Correct `docs/workflows/hod/pop.md`** — the POP_HMZ paragraph (currently "−0.5 points per eligible occurrence" uniformly). Replace with the Table 7 reading:

```markdown
`POP_HMZ` awards benignity **per eligible occurrence, counted only from the
2nd** — homozygous occurrences for AD/AR/semidominant MDEs, homozygous *or*
hemizygous for X-linked — and only when `hmz_eligible` holds. The weight per
observation is **−1.0 for Autosomal Dominant** and **−0.5 for
AR / semidominant / X-linked** (SM 3 Table 7). Example: three homozygous
occurrences for an **AR** MDE → `POP_HMZ_-1.0` (1st free; 2nd and 3rd −0.5
each); for an **AD** MDE → `POP_HMZ_-2.0` (−1.0 each). This is distinct from
`CLN_UAF`, which requires explicit clinical details.

!!! note "SM 3 prose vs Table 7"

    SM 3's prose text lumps AD with AR at −0.5, but **Table 7** (the explicit
    point-value table) assigns Autosomal Dominant −1.0. This project follows
    Table 7; the conflict is logged under [Known gaps](../../reference/known-gaps.md).
```

- [ ] **Step 3: Add a `known-gaps.md` Working Group follow-up row** — in the "Working Group follow-ups" table:

```markdown
| SM 3 POP_HMZ Autosomal Dominant weight | SM 3 | Prose (L93) says −0.5 pts per homozygous occurrence for AD *or* AR, but **Table 7** assigns Autosomal Dominant **−1.0** (AR/semidominant/X-linked −0.5). The reference scorer follows Table 7. A good candidate to raise with the working group — same category as the SM 18 Figure-1 open item. |
```

- [ ] **Step 4: Build strict** — `uv run mkdocs build --strict` (exit 0).
- [ ] **Step 5: Commit** — `git commit -am "docs: Population reference scorer; correct pop.md POP_HMZ weight (Table 7); log WG follow-up"`

---

## Task 3: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`export_schemas.py` then `git diff --quiet -- schemas/json docs/workflows/case-model.md`); `mkdocs build --strict` (exit 0); no scorer schema leaked; clean tree.

---

## Notes for the implementer

- `moi` is a **required** keyword (no default) — mirrors `gene_disease_validity`. POP_FRQ never reads it.
- The X-linked set is `{MOI.XLD, MOI.XLR}`; AD weight is −1.0, everything else −0.5.
- `homo or 0` / `hemi or 0` treat `None` as 0 in the sum, but the `homo is None and hemi is None` guard first returns `_ND` so an all-absent count is not scored as `0.0`.
- Scoring is NOT in the root `__all__` (no schema). Line length 100 — watch the provenance f-strings.
