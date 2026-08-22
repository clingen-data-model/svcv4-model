# Reference Scorer — Missense amino-acid path (SM 6, MIS_) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_score_missense_amino_acid` (SM 6 green path → `MIS_`) + two new primitives: `transcript_relevance_points` (positive-only exon-fraction, no mechanism/GDV) and `missense_informative_points` (the 4-category MIS_INF tally). Increment C1 of the splice family (C2 = the SPL_ path + take-higher).

**Architecture:** A standalone single-path scorer (no outcome branches, no branch table) — the MIS_ pipeline (PRD → FXN → held → INF → total) differs enough from the NUL_/CDS_ and SPL_ helpers to be its own function. The MIS_ path has **no GDV gate**, so the scorer takes **no `gene_disease_validity`**. Reuses `cap`/`hold_combined`/`_EXON_FRACTION`. Non-authoritative; scoring stays out of root `__all__` (no schema).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Caps (all SM 6-verified):** MIS_PRD −4..+4; MIS_FXN −8..+8; held PRD+FXN −8..+6; MIS_INF −8..+8; mis_total −8..+9.

---

## Task 1: `transcript_relevance_points` primitive (TDD)

**Files:** Modify `src/svcv4_model/scoring/primitives.py`; `tests/test_scoring_primitives.py`

- [ ] **Step 1: Write the failing test** — append to `tests/test_scoring_primitives.py`

```python
from svcv4_model.mechanism import ExonRelevance
from svcv4_model.scoring.primitives import transcript_relevance_points


def test_transcript_relevance_positive_scaled_by_exon() -> None:
    assert transcript_relevance_points(4.0, ExonRelevance.ALL) == 4.0
    assert transcript_relevance_points(4.0, ExonRelevance.MOST) == 2.0
    assert transcript_relevance_points(4.0, ExonRelevance.FEW) == 0.0


def test_transcript_relevance_nonpositive_passthrough() -> None:
    assert transcript_relevance_points(-3.0, ExonRelevance.FEW) == -3.0  # skips the step
    assert transcript_relevance_points(0.0, ExonRelevance.ALL) == 0.0
    assert transcript_relevance_points(None, ExonRelevance.ALL) is None


def test_transcript_relevance_none_exon_is_full() -> None:
    assert transcript_relevance_points(4.0, None) == 4.0  # generous default
```

- [ ] **Step 2: Run — expect ImportError.** `uv run pytest tests/test_scoring_primitives.py -q`

- [ ] **Step 3: Implement in `primitives.py`** — add after `apply_sm18_multiplier` (reuses the existing `_EXON_FRACTION`):

```python
def transcript_relevance_points(
    points: float | None, exon_relevance: ExonRelevance | None
) -> float | None:
    """Missense MIS_PRD transcript-relevance reduction (SM 6 L21), positive points only.

    None/<=0 pass through (a zero/negative in-silico score skips this step; the caller floors
    at -4). Positive points are scaled by the exon fraction (All 1.0 / Most 0.5 / Few 0.0);
    None exon -> x1.0 (the generous default). No molecular mechanism and no GDV gate apply on
    the missense amino-acid path, so this is deliberately simpler than ``apply_sm18_multiplier``.
    """
    if points is None or points <= 0:
        return points
    frac = 1.0 if exon_relevance is None else _EXON_FRACTION.get(exon_relevance, 1.0)
    return points * frac
```

- [ ] **Step 4: Run** `uv run pytest tests/test_scoring_primitives.py -q` — PASS.
- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat(scoring): add transcript_relevance_points primitive (SM 6 MIS_PRD)"`

---

## Task 2: `missense_informative_points` primitive (TDD)

**Files:** Modify `src/svcv4_model/scoring/primitives.py`; `tests/test_scoring_primitives.py`

- [ ] **Step 1: Write the failing test** — append to `tests/test_scoring_primitives.py`

```python
from svcv4_model.missense import MissenseInfCategory, MissenseInformativeVariant
from svcv4_model.scoring.primitives import missense_informative_points

_P = VariantClassification.PATHOGENIC
_LP = VariantClassification.LIKELY_PATHOGENIC
_B = VariantClassification.BENIGN
_LB = VariantClassification.LIKELY_BENIGN
_VUS = VariantClassification.VUS


def _mv(cat: MissenseInfCategory, cls: VariantClassification) -> MissenseInformativeVariant:
    return MissenseInformativeVariant(category=cat, classification=cls)


def test_mis_inf_empty_is_none() -> None:
    assert missense_informative_points([]) is None
    # a VUS (and an off-polarity class) score nothing -> None
    assert missense_informative_points([_mv(MissenseInfCategory.SAME_AA_PATHOGENIC, _VUS)]) is None
    assert missense_informative_points([_mv(MissenseInfCategory.SAME_AA_PATHOGENIC, _B)]) is None


def test_mis_inf_cat1_same_aa_pathogenic_doubled() -> None:
    C = MissenseInfCategory.SAME_AA_PATHOGENIC
    assert missense_informative_points([_mv(C, _P)]) == 4.0
    assert missense_informative_points([_mv(C, _P), _mv(C, _P)]) == 6.0
    assert missense_informative_points([_mv(C, _LP)]) == 2.0
    assert missense_informative_points([_mv(C, _LP), _mv(C, _LP)]) == 4.0
    assert missense_informative_points([_mv(C, _P), _mv(C, _LP)]) == 6.0


def test_mis_inf_cat2_distinct_aa_pathogenic_standard() -> None:
    C = MissenseInfCategory.DISTINCT_AA_PATHOGENIC
    assert missense_informative_points([_mv(C, _P)]) == 2.0
    assert missense_informative_points([_mv(C, _P), _mv(C, _LP)]) == 3.0


def test_mis_inf_cat3_distinct_aa_benign_standard_negative() -> None:
    C = MissenseInfCategory.DISTINCT_AA_BENIGN
    assert missense_informative_points([_mv(C, _B)]) == -2.0
    assert missense_informative_points([_mv(C, _B), _mv(C, _LB)]) == -3.0


def test_mis_inf_cat4_same_aa_benign_doubled_negative() -> None:
    C = MissenseInfCategory.SAME_AA_BENIGN
    assert missense_informative_points([_mv(C, _B)]) == -4.0
    assert missense_informative_points([_mv(C, _LB)]) == -2.0
    assert missense_informative_points([_mv(C, _LB), _mv(C, _LB)]) == -4.0
    assert missense_informative_points([_mv(C, _B), _mv(C, _LB)]) == -6.0


def test_mis_inf_sums_all_categories_uncapped() -> None:
    # cat1 +4, cat3 -2 -> +2 (uncapped; the caller applies the -8..+8 cap)
    variants = [
        _mv(MissenseInfCategory.SAME_AA_PATHOGENIC, _P),
        _mv(MissenseInfCategory.DISTINCT_AA_BENIGN, _B),
    ]
    assert missense_informative_points(variants) == 2.0
```

- [ ] **Step 2: Run — expect ImportError.**

- [ ] **Step 3: Implement in `primitives.py`** — add module-private helpers + the primitive. Add the imports `from svcv4_model.missense import MissenseInfCategory, MissenseInformativeVariant` at the top (one-way scoring→models; no cycle — `missense.py` does not import scoring).

```python
def _doubled_tally(n_strong: int, n_weak: int) -> float:
    """Cat 1/4 magnitude: 4 for the first strong (else 2 for the first weak), +2 each more."""
    n = n_strong + n_weak
    if n == 0:
        return 0.0
    first = 4.0 if n_strong else 2.0
    return first + 2.0 * (n - 1)


def _standard_tally(n_strong: int, n_weak: int) -> float:
    """Cat 2/3 magnitude: the standard +2 first strong / +1 first weak / +1 each additional."""
    if n_strong + n_weak == 0:
        return 0.0
    pts = (2.0 if n_strong else 0.0) + (1.0 if n_weak else 0.0)
    return pts + max(n_strong - 1, 0) + max(n_weak - 1, 0)


def missense_informative_points(
    variants: Iterable[MissenseInformativeVariant],
) -> float | None:
    """SM 6 (L32-35) four-category MIS_INF tally. Returns None when nothing scores (MIS_INF_ND).

    Each variant's analyst-assigned ``category`` selects the rule; only the matching polarity
    counts (cats 1-2 tally P/LP, cats 3-4 tally B/LB). A VUS or off-polarity class scores
    nothing. UNCAPPED -- the caller applies the -8..+8 cap. The SM 7 motif-variant special
    case (cat 2, +2 once) is deferred with the critical-amino-acids increment.
    """
    per_cat: dict[MissenseInfCategory, Counter[VariantClassification]] = {
        c: Counter() for c in MissenseInfCategory
    }
    for v in variants:
        if v.category is not None and v.classification is not None:
            per_cat[v.category][v.classification] += 1

    c1 = per_cat[MissenseInfCategory.SAME_AA_PATHOGENIC]
    c2 = per_cat[MissenseInfCategory.DISTINCT_AA_PATHOGENIC]
    c3 = per_cat[MissenseInfCategory.DISTINCT_AA_BENIGN]
    c4 = per_cat[MissenseInfCategory.SAME_AA_BENIGN]
    p, lp = VariantClassification.PATHOGENIC, VariantClassification.LIKELY_PATHOGENIC
    b, lb = VariantClassification.BENIGN, VariantClassification.LIKELY_BENIGN

    scored = c1[p] + c1[lp] + c2[p] + c2[lp] + c3[b] + c3[lb] + c4[b] + c4[lb]
    if scored == 0:
        return None
    return (
        _doubled_tally(c1[p], c1[lp])
        + _standard_tally(c2[p], c2[lp])
        - _standard_tally(c3[b], c3[lb])
        - _doubled_tally(c4[b], c4[lb])
    )
```

(Confirm `Counter` is imported at the top of `primitives.py` — it already is, for `informative_points`.)

- [ ] **Step 4: Run** `uv run pytest tests/test_scoring_primitives.py -q` — all PASS.
- [ ] **Step 5: Commit** — `git commit -am "feat(scoring): add missense_informative_points 4-category tally (SM 6 MIS_INF)"`

---

## Task 3: `reference_score_missense_amino_acid` (TDD)

**Files:** Create `src/svcv4_model/scoring/pfd/missense_amino_acid.py`, `tests/test_missense_amino_acid_scoring.py`; modify `src/svcv4_model/scoring/__init__.py`

- [ ] **Step 1: Write the failing test** — `tests/test_missense_amino_acid_scoring.py`

```python
"""Tests for reference_score_missense_amino_acid (non-authoritative)."""

from __future__ import annotations

from svcv4_model.informative import VariantClassification
from svcv4_model.mechanism import ExonRelevance
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
)
from svcv4_model.scoring import reference_score_missense_amino_acid


def _inf(*pairs: tuple[MissenseInfCategory, VariantClassification]) -> MissenseInformativeEvidence:
    return MissenseInformativeEvidence(
        variants=[MissenseInformativeVariant(category=c, classification=cls) for c, cls in pairs]
    )


def test_prd_transcript_relevance() -> None:
    cases = [(ExonRelevance.ALL, 4.0), (ExonRelevance.MOST, 2.0), (ExonRelevance.FEW, 0.0)]
    for exon, expected in cases:
        a = MissenseAminoAcidAssessment(
            predictive=MissensePredictiveEvidence(initial_points=4.0, transcript_relevance=exon)
        )
        r = reference_score_missense_amino_acid(a)
        assert r.parent_code == "MIS"
        assert r.sub_code_points["PRD"] == expected


def test_prd_negative_passthrough() -> None:
    a = MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(initial_points=-3.0, transcript_relevance=ExonRelevance.FEW)
    )
    r = reference_score_missense_amino_acid(a)
    assert r.sub_code_points["PRD"] == -3.0  # skips relevance, floored -4


def test_maximal_held_and_total() -> None:
    a = MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(initial_points=4.0, transcript_relevance=ExonRelevance.ALL),
        fxn_points=8.0,
        informative=_inf((MissenseInfCategory.SAME_AA_PATHOGENIC, VariantClassification.PATHOGENIC)),
    )
    r = reference_score_missense_amino_acid(a)
    assert r.sub_code_points["PRD"] == 4.0
    assert r.sub_code_points["FXN"] == 8.0
    assert r.held_combined["PRD+FXN"] == 6.0  # cap(4+8, +6)
    assert r.sub_code_points["INF"] == 4.0
    assert r.parent_total == 9.0  # cap(6+4, +9)


def test_held_floor() -> None:
    a = MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(initial_points=-4.0),
        fxn_points=-8.0,
    )
    r = reference_score_missense_amino_acid(a)
    assert r.held_combined["PRD+FXN"] == -8.0  # cap(-12, -8)


def test_inf_cap_and_categories() -> None:
    # cat1 P (+4) + cat4 B (-4) -> 0
    a = MissenseAminoAcidAssessment(
        informative=_inf(
            (MissenseInfCategory.SAME_AA_PATHOGENIC, VariantClassification.PATHOGENIC),
            (MissenseInfCategory.SAME_AA_BENIGN, VariantClassification.BENIGN),
        )
    )
    r = reference_score_missense_amino_acid(a)
    assert r.sub_code_points["INF"] == 0.0


def test_fxn_nd_and_inf_nd() -> None:
    a = MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(initial_points=4.0, transcript_relevance=ExonRelevance.ALL)
    )
    r = reference_score_missense_amino_acid(a)
    assert "FXN" not in r.sub_code_points
    assert "INF" not in r.sub_code_points
    assert r.held_combined["PRD+FXN"] == 4.0  # prd alone
    assert r.parent_total == 4.0


def test_empty_is_all_nd() -> None:
    r = reference_score_missense_amino_acid(MissenseAminoAcidAssessment())
    assert r.parent_code == "MIS"
    assert r.sub_code_points == {}
    assert r.parent_total is None
```

- [ ] **Step 2: Run — expect ImportError.**

- [ ] **Step 3: Implement `scoring/pfd/missense_amino_acid.py`**

```python
"""Reference (non-authoritative) scorer for the Missense amino-acid path (SM 6, MIS_)."""

from __future__ import annotations

from svcv4_model.missense import MissenseAminoAcidAssessment
from svcv4_model.scoring.primitives import (
    cap,
    hold_combined,
    missense_informative_points,
    transcript_relevance_points,
)
from svcv4_model.scoring.result import ScoreResult


def reference_score_missense_amino_acid(
    assessment: MissenseAminoAcidAssessment,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Missense amino-acid (MIS_) total (SM 6).

    CSpec is authoritative. Unlike every other scorer, the MIS_ path takes **no**
    ``gene_disease_validity`` -- MIS_PRD is reduced by transcript relevance only, with no
    molecular-mechanism axis and no GDV gate (predictors already capture LoF+GoF). FXN is
    consumed raw; MIS_INF is the computed 4-category tally. The SM 7 motif-variant special
    case and the SPL_ splice path / MIS_-vs-SPL_ comparison are separate increments.
    """
    prov: list[str] = []
    sub: dict[str, float] = {}
    held: dict[str, float] = {}

    # MIS_PRD (computed: transcript relevance only)
    prd: float | None = None
    pred = assessment.predictive
    initial = pred.initial_points if pred else None
    exon = pred.transcript_relevance if pred else None
    if initial is None:
        prov.append("MIS_PRD: _ND (no initial points)")
    else:
        adj = transcript_relevance_points(initial, exon)
        prd = cap(adj, -4.0, 4.0)
        sub["PRD"] = prd
        prov.append(f"MIS_PRD: {initial} x transcript-relevance = {adj}, capped [-4.0, 4.0] -> {prd}")

    # MIS_FXN (consumed raw)
    fxn = assessment.fxn_points
    if fxn is None:
        prov.append("MIS_FXN: _ND (no coded fxn_points; OddsPath not recomputed)")
    else:
        sub["FXN"] = fxn
        prov.append(f"MIS_FXN: consumed coded value {fxn}")

    # held PRD+FXN
    prd_fxn = hold_combined(prd, fxn, lo=-8.0, hi=6.0)
    if prd_fxn is not None:
        held["PRD+FXN"] = prd_fxn
        prov.append(f"held PRD+FXN: {prd_fxn} (cap [-8.0, 6.0])")

    # MIS_INF (computed 4-category tally)
    inf: float | None = None
    if assessment.informative is not None:
        inf = cap(missense_informative_points(assessment.informative.variants), -8.0, 8.0)
    if inf is None:
        prov.append("MIS_INF: _ND (no categorized informative variants; SM7 motif deferred)")
    else:
        sub["INF"] = inf
        prov.append(f"MIS_INF: {inf} (cap [-8.0, 8.0]); SM7 motif special-case deferred")

    # mis_total
    mis_total = hold_combined(prd_fxn, inf, lo=-8.0, hi=9.0)
    if mis_total is not None:
        prov.append(f"mis_total: {mis_total} (cap [-8.0, 9.0])")

    return ScoreResult(
        parent_code="MIS",
        sub_code_points=sub,
        held_combined=held,
        parent_total=mis_total,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 4: Add the export** — `scoring/__init__.py`: import (after `intronic_synonymous`, before `nonsense`) + `"reference_score_missense_amino_acid"` in `__all__` (same position). Do NOT export the primitives.

- [ ] **Step 5: Run** `uv run pytest tests/test_missense_amino_acid_scoring.py -q` — all PASS.
- [ ] **Step 6: Commit** — `git commit -am "feat(scoring): add reference_score_missense_amino_acid (SM 6 MIS_ path)"`

---

## Task 4: Docs

- [ ] **Step 1: Extend `docs/reference/scoring.md`** — after the Intronic & Synonymous bullet:

```markdown
- **Missense — amino-acid path** (SM 6) — `reference_score_missense_amino_acid`, the first
  `MIS_` scorer. A standalone single-path pipeline: MIS_PRD is reduced by **transcript relevance
  only** (no molecular mechanism, **no GDV gate** — so this scorer takes no `gene_disease_validity`),
  and MIS_INF is a computed **4-category Grantham tally** (`missense_informative_points`). The
  `SPL_` splice path and the `MIS_`-vs-`SPL_` take-higher comparison are a follow-up increment.
```

- [ ] **Step 2: Build strict** — `uv run mkdocs build --strict` (0 warnings).
- [ ] **Step 3: Commit** — `git commit -am "docs: note the Missense amino-acid reference scorer"`

---

## Task 5: Full quality gates

- [ ] `uv run pytest -q`; `uv run ruff check .`; drift gate (`export_schemas.py` then `git diff --quiet -- schemas/json docs/workflows/case-model.md`); `mkdocs build --strict` (exit 0); no scorer schema leaked; clean tree (except pre-existing untracked).

---

## Notes for the implementer

- The MIS_ scorer takes **NO** `gene_disease_validity` (unique among the scorers). Do not add it.
- `primitives.py` gains an import from `svcv4_model.missense` — verify no import cycle (missense.py imports only model modules, never scoring).
- The primitives are internal — export ONLY `reference_score_missense_amino_acid` from `scoring/__init__.py`, not the two primitives (mirrors `informative_points`/`apply_sm18_multiplier`, which are unexported).
- Watch line length 100 on the PRD provenance f-string and the test constructor lines; wrap if needed.
