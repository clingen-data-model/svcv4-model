# Reference Scorer — CLN_CCS case-control (SM 4) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_cln_ccs` (SM 4) — the case-control clinical code, the **last** CLN code. Operates on the standalone `CaseControlStudyEvidence` (like POP). `parent_code="CLN"`, single sub-code `CLN_CCS`.

**Architecture:** Extends `scoring/hod/clinical.py` (adds an import from `svcv4_model.case_control`). Non-authoritative; scoring out of root `__all__` (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Scoring (spec-verified):** robustness gate (`case_variant_count>=5` AND `case_cohort_size>=100` AND `controls_matched is True`) else `_ND`; `OR>5.0` AND CI excludes 1.0 → `+4.0`; else `0.0` (CI veto / `1<OR<=5` / `OR<=1` benignity-indicated-but-unquantified). `odds_ratio None` → `_ND`.

---

## Task 1: `reference_score_cln_ccs` (TDD)

**Files:** Modify `src/svcv4_model/scoring/hod/clinical.py`, create `tests/test_cln_ccs_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_cln_ccs_scoring.py`

```python
"""Tests for reference_score_cln_ccs (SM 4 case-control, non-authoritative)."""

from __future__ import annotations

from svcv4_model.case_control import CaseControlStudyEvidence
from svcv4_model.scoring import reference_score_cln_ccs


def _cc(**kw: object) -> CaseControlStudyEvidence:
    # a robust study by default; override per test
    base: dict[str, object] = {
        "odds_ratio": 6.0,
        "case_variant_count": 5,
        "case_cohort_size": 100,
        "controls_matched": True,
    }
    base.update(kw)
    return CaseControlStudyEvidence(**base)


def _ccs(ev: CaseControlStudyEvidence) -> float | None:
    return reference_score_cln_ccs(ev).sub_code_points.get("CLN_CCS")


def test_robust_or_gt5_ci_excludes_one() -> None:
    r = reference_score_cln_ccs(_cc(odds_ratio=6.0, ci_lower=2.0, ci_upper=9.0))
    assert r.parent_code == "CLN"
    assert r.sub_code_points["CLN_CCS"] == 4.0
    assert r.parent_total == 4.0


def test_ci_includes_one_vetoes() -> None:
    assert _ccs(_cc(odds_ratio=5.5, ci_lower=0.9, ci_upper=7.4)) == 0.0


def test_none_ci_does_not_veto() -> None:
    assert _ccs(_cc(odds_ratio=6.0)) == 4.0  # ci_lower/upper None


def test_or_between_one_and_five_is_zero() -> None:
    assert _ccs(_cc(odds_ratio=3.0)) == 0.0


def test_or_le_one_is_zero_benign_flagged() -> None:
    r = reference_score_cln_ccs(_cc(odds_ratio=0.5))
    assert r.sub_code_points["CLN_CCS"] == 0.0
    assert any("benign" in p.lower() for p in r.provenance)


def test_gate_fails_are_nd() -> None:
    assert _ccs(_cc(case_variant_count=4)) is None
    assert _ccs(_cc(case_cohort_size=50)) is None
    assert _ccs(_cc(controls_matched=False)) is None
    assert _ccs(_cc(controls_matched=None)) is None


def test_odds_ratio_none_is_nd() -> None:
    r = reference_score_cln_ccs(_cc(odds_ratio=None))
    assert r.sub_code_points == {}
    assert r.parent_total is None


def test_exclusivity_note_in_provenance() -> None:
    r = reference_score_cln_ccs(_cc(odds_ratio=6.0, ci_lower=2.0, ci_upper=9.0))
    assert any("CLN_DNV" in p for p in r.provenance)
```

- [ ] **Step 2: Run — expect ImportError.** `uv run pytest tests/test_cln_ccs_scoring.py -q`

- [ ] **Step 3: Implement `reference_score_cln_ccs`** in `clinical.py`. Add the import `from svcv4_model.case_control import CaseControlStudyEvidence` (isort: `svcv4_model.case` block, then `svcv4_model.case_control`, then `svcv4_model.scoring.result` — `case` < `case_control` < `scoring`). Then:

```python
def reference_score_cln_ccs(evidence: CaseControlStudyEvidence) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) CLN_CCS case-control points (SM 4). CSpec is
    authoritative. Operates on the standalone ``CaseControlStudyEvidence`` (like POP), not a
    per-proband Case. When CLN_CCS is applied, SM 4 marks all other CLN codes NA except CLN_DNV
    -- that exclusivity is an aggregation-layer rule, deferred here.
    """
    prov: list[str] = [
        'CLN: "CLN" is the HOD grouping label. When CLN_CCS is applied, SM 4 marks all other '
        "CLN codes NA except CLN_DNV -- exclusivity deferred to case aggregation."
    ]
    or_ = evidence.odds_ratio
    if or_ is None:
        prov.append("CLN_CCS: _ND (no odds_ratio)")
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)

    robust = (
        evidence.case_variant_count is not None
        and evidence.case_variant_count >= 5
        and evidence.case_cohort_size is not None
        and evidence.case_cohort_size >= 100
        and evidence.controls_matched is True
    )
    if not robust:
        prov.append(
            "CLN_CCS: _ND (study not robust -- SM 4 requires >=5 case-variant observations, "
            ">=100 unrelated cases, and matched controls)."
        )
        return ScoreResult(parent_code="CLN", provenance=prov, authoritative=False)
    if not evidence.ascertainment_bias_considered:
        prov.append("CLN_CCS: note -- ascertainment_bias_considered is not TRUE (SM 4 caution).")

    ci_includes_1 = (
        evidence.ci_lower is not None
        and evidence.ci_upper is not None
        and evidence.ci_lower <= 1.0 <= evidence.ci_upper
    )
    if or_ > 5.0 and not ci_includes_1:
        pts = 4.0
        prov.append(f"CLN_CCS: +4.0 (OR {or_} > 5.0, CI excludes 1.0)")
    else:
        pts = 0.0
        if or_ <= 1.0:
            prov.append(
                f"CLN_CCS: 0.0 (OR {or_} <= 1.0 -- benignity indicated, but SM 4 assigns no "
                "CLN_CCS benign point value; see known-gaps)."
            )
        elif ci_includes_1:
            prov.append(
                f"CLN_CCS: 0.0 (OR {or_} > 5.0 but CI includes 1.0 -- not significant)"
            )
        else:
            prov.append(f"CLN_CCS: 0.0 (OR {or_} <= 5.0 -- insufficient enrichment)")

    return ScoreResult(
        parent_code="CLN",
        sub_code_points={"CLN_CCS": pts},
        parent_total=pts,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 4: Export** — `scoring/__init__.py`: add `reference_score_cln_ccs` to the clinical import (alphabetical: `cln_aff_biallelic` < `cln_aff_mono` < `cln_alt` < `cln_ccs` < `cln_dnv` < `cln_uaf`) and to `__all__` (same position, after `reference_score_cln_alt`).

- [ ] **Step 5: Run** `uv run pytest tests/test_cln_ccs_scoring.py -q` — all PASS.
- [ ] **Step 6: Commit** — `git commit -am "feat(scoring): add reference_score_cln_ccs (SM 4 case-control) -- completes CLN"`

---

## Task 2: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — the CLN line: CLN is **complete** — add `reference_score_cln_ccs` (case-control, standalone `CaseControlStudyEvidence`; `OR>5` + robust → `+4.0`, CI-includes-1.0 veto, robustness gate `≥5`/`≥100`/matched → `_ND`; a low OR indicates benignity but SM 4 gives no CLN_CCS benign value; the exclusivity rule — other CLN NA except CLN_DNV — is deferred to aggregation).

- [ ] **Step 2: `known-gaps.md`** — a source-gap row under "Working Group follow-ups": SM 4 gives **no CLN_CCS benign point value** for a low OR (only "evidence of benignity"); the reference scorer records `0.0` + a provenance flag.

- [ ] **Step 3: Build strict** — `uv run mkdocs build --strict` (exit 0).
- [ ] **Step 4: Commit** — `git commit -am "docs: CLN complete (CLN_CCS); log the missing CLN_CCS benign value"`

---

## Task 3: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`export_schemas.py` then `git diff --quiet -- schemas/json docs/workflows/case-model.md`); `mkdocs build --strict` (exit 0); no scorer schema leaked; clean tree.

---

## Notes for the implementer

- `reference_score_cln_ccs` takes `CaseControlStudyEvidence` (no `Case`, no `moi`) — the POP standalone pattern. Add the `case_control` import (between the `case` and `scoring.result` imports for isort).
- The robustness gate short-circuits on `None` counts (no `AttributeError`; `None is not None` is False → not robust). `controls_matched is True` excludes both `None` and `False`.
- `or_ <= 1.0` and `ci_includes_1` differentiate the 0.0 provenance only (both award 0.0). Watch LL 100 on the provenance f-strings (the CI-veto line is long — wrap if ruff flags).
