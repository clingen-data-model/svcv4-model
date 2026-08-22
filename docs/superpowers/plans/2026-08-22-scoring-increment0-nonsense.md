# Reference Scorer — Increment 0 (scaffold + primitives + Nonsense) Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Stand up the non-authoritative `svcv4_model.scoring` subpackage with `ScoreResult`, shared `primitives.py`, and `reference_score_nonsense` (all three SM 8 branches), plus a `reference/scoring.md` contract page.

**Architecture:** Pure functions in a new `src/svcv4_model/scoring/` subpackage, **not** re-exported from the root `svcv4_model/__init__.py` (so `export_schemas.py`, which iterates the root `__all__`, emits no schema for it and the drift gate stays clean). Dependency is one-way: `scoring → svcv4_model.*` models. Capture models untouched. NON-AUTHORITATIVE — CSpec is authoritative.

**Tech Stack:** Python 3.11+, stdlib `dataclasses`/`collections`, `uv`, ruff (line-length 100), pytest, mkdocs-material (strict).

**Confirmed enum spellings (do not guess):** `GenccMechanism.{ESTABLISHED,LIKELY,SUSPECTED,UNCERTAIN}`; `ExonRelevance.{ALL,MOST,FEW}`; `GeneDiseaseValidity.{DEFINITIVE,STRONG,MODERATE,LIMITED,DISPUTED,REFUTED,NOT_CLASSIFIED}`; `VariantClassification.{PATHOGENIC,LIKELY_PATHOGENIC,VUS,LIKELY_BENIGN,BENIGN}`; `PfdParentCode.NUL == "NUL"`, `.CDS == "CDS"` (no underscore); `MechanismExonRelevanceEvidence.gencc_mechanism` / `.exon_relevance`; `NonsensePredictionOutcome.{NMD_NO_RESCUE,NMD_WITH_RESCUE,NO_NMD}`. Tests live **flat** in `tests/` (matching the repo's existing flat test layout), not a `tests/scoring/` subdir.

---

## Task 1: `ScoreResult` + `primitives.py` (TDD)

**Files:**
- Create: `src/svcv4_model/scoring/__init__.py`, `src/svcv4_model/scoring/result.py`, `src/svcv4_model/scoring/primitives.py`
- Test: `tests/test_scoring_primitives.py`

- [ ] **Step 1: Write the failing test** — `tests/test_scoring_primitives.py`

```python
"""Tests for the reference-scorer primitives (non-authoritative)."""

from __future__ import annotations

import pytest

from svcv4_model.informative import InformativeVariant, VariantClassification
from svcv4_model.mechanism import ExonRelevance, GenccMechanism
from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.scoring import ScoreResult
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
)

MOD = GeneDiseaseValidity.MODERATE


def test_cap_clamps_and_passes_none() -> None:
    assert cap(5.0, -8.0, 10.0) == 5.0
    assert cap(-20.0, -8.0, 10.0) == -8.0
    assert cap(99.0, -8.0, 10.0) == 10.0
    assert cap(None, -8.0, 10.0) is None


def test_hold_combined_sums_caps_and_handles_none() -> None:
    assert hold_combined(6.0, 2.0, lo=-8.0, hi=10.0) == 8.0
    assert hold_combined(6.0, 8.0, lo=-8.0, hi=9.0) == 9.0  # capped
    assert hold_combined(6.0, None, lo=-8.0, hi=10.0) == 6.0
    assert hold_combined(None, None, lo=-8.0, hi=10.0) is None


def test_sm18_multiplier_mechanism_and_exon() -> None:
    # Established x All -> full
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) == 6.0
    # Likely x All -> half
    assert apply_sm18_multiplier(6.0, GenccMechanism.LIKELY, ExonRelevance.ALL, MOD) == 3.0
    # Suspected x All -> quarter (fractional carried forward)
    assert apply_sm18_multiplier(3.0, GenccMechanism.SUSPECTED, ExonRelevance.ALL, MOD) == 0.75
    # Uncertain -> 0
    assert apply_sm18_multiplier(6.0, GenccMechanism.UNCERTAIN, ExonRelevance.ALL, MOD) == 0.0
    # exon Few -> 0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.FEW, MOD) == 0.0
    # Most halves
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.MOST, MOD) == 3.0


def test_sm18_special_case_suspected_most_is_quarter() -> None:
    # Figure-1-pending assumption: keep the Suspected fraction (0.25), NOT 0.125 and NOT 0.0
    assert apply_sm18_multiplier(4.0, GenccMechanism.SUSPECTED, ExonRelevance.MOST, MOD) == 1.0


def test_sm18_only_positive_and_gdv_gate() -> None:
    # negatives and zero pass through unchanged
    assert apply_sm18_multiplier(-1.0, GenccMechanism.UNCERTAIN, ExonRelevance.FEW, MOD) == -1.0
    assert apply_sm18_multiplier(0.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) == 0.0
    assert apply_sm18_multiplier(None, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) is None
    # GDV below Moderate zeroes a positive
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL,
                                 GeneDiseaseValidity.LIMITED) == 0.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, None) == 0.0
    # None mechanism -> 0.0; None exon -> no reduction (generous, asymmetric)
    assert apply_sm18_multiplier(6.0, None, ExonRelevance.ALL, MOD) == 0.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, None, MOD) == 6.0


def _iv(cls: VariantClassification) -> InformativeVariant:
    return InformativeVariant(id="x", classification=cls)


def test_informative_points_tally() -> None:
    P, LP = VariantClassification.PATHOGENIC, VariantClassification.LIKELY_PATHOGENIC
    B, LB, VUS = (VariantClassification.BENIGN, VariantClassification.LIKELY_BENIGN,
                  VariantClassification.VUS)
    assert informative_points([_iv(P)]) == 2.0
    assert informative_points([_iv(P), _iv(LP), _iv(LP)]) == 4.0
    assert informative_points([_iv(LP)]) == 1.0
    assert informative_points([_iv(B), _iv(B)]) == -3.0
    assert informative_points([_iv(P), _iv(B)]) == 0.0
    assert informative_points([_iv(VUS), _iv(VUS)]) == 0.0
    assert informative_points([]) is None
    assert informative_points([InformativeVariant(id="x")]) is None  # classification None


def test_score_result_rejects_authoritative_true() -> None:
    ScoreResult()  # default authoritative=False is fine
    with pytest.raises(ValueError):
        ScoreResult(authoritative=True)
```

- [ ] **Step 2: Run — expect ModuleNotFoundError**

Run: `uv run pytest tests/test_scoring_primitives.py -q`
Expected: FAIL — `No module named 'svcv4_model.scoring'`.

- [ ] **Step 3: Implement `result.py`**

```python
"""The reference-scorer result DTO (non-authoritative)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScoreResult:
    """A reference (NON-AUTHORITATIVE) scoring result. CSpec is authoritative.

    Holds the coded sub-code point values, any held-combined intermediates, the capped
    parent-code total, and a human-readable ``provenance`` trail (the rule/cap applied at
    each step). A sub-code that is un-scoreable / No-Data is OMITTED from ``sub_code_points``
    (never recorded as 0.0). ``authoritative`` is fixed False — constructing it True raises,
    so the non-authoritative contract cannot be bypassed.
    """

    parent_code: str | None = None
    sub_code_points: dict[str, float] = field(default_factory=dict)
    held_combined: dict[str, float] = field(default_factory=dict)
    parent_total: float | None = None
    provenance: list[str] = field(default_factory=list)
    authoritative: bool = False

    def __post_init__(self) -> None:
        if self.authoritative:
            raise ValueError(
                "ScoreResult is a reference (non-authoritative) computation; "
                "authoritative must be False — CSpec is the authoritative scorer."
            )
```

- [ ] **Step 4: Implement `primitives.py`**

```python
"""Shared, workflow-agnostic reference-scoring primitives (non-authoritative).

CSpec is authoritative. The SM 18 multiplier here encodes one Figure-1-pending assumption
(the Suspected x Most matrix cell = 0.25); see ``apply_sm18_multiplier``.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import InformativeVariant, VariantClassification
from svcv4_model.mechanism import ExonRelevance, GenccMechanism

_MECHANISM_FRACTION: dict[GenccMechanism, float] = {
    GenccMechanism.ESTABLISHED: 1.0,
    GenccMechanism.LIKELY: 0.5,
    GenccMechanism.SUSPECTED: 0.25,
    GenccMechanism.UNCERTAIN: 0.0,
}
_EXON_FRACTION: dict[ExonRelevance, float] = {
    ExonRelevance.ALL: 1.0,
    ExonRelevance.MOST: 0.5,
    ExonRelevance.FEW: 0.0,
}
_GDV_MODERATE_PLUS = frozenset(
    {GeneDiseaseValidity.DEFINITIVE, GeneDiseaseValidity.STRONG, GeneDiseaseValidity.MODERATE}
)


def cap(value: float | None, lo: float, hi: float) -> float | None:
    """Clamp ``value`` to [lo, hi]; ``None`` passes through."""
    if value is None:
        return None
    return max(lo, min(hi, value))


def hold_combined(*parts: float | None, lo: float, hi: float) -> float | None:
    """Sum the non-None ``parts`` and cap; return None if every part is None."""
    present = [p for p in parts if p is not None]
    if not present:
        return None
    return cap(sum(present), lo, hi)


def informative_points(variants: Iterable[InformativeVariant]) -> float | None:
    """SM 19 (+ SM 8) informative tally: +2 first P / +1 first LP / +1 each additional P/LP;
    symmetric negatives for B/LB (inferred per SM 8 'similar logic'); VUS -> 0.

    Returns None when there are no classified variants (``_INF_ND``). Uncapped — the caller
    applies the per-workflow INF cap.
    """
    classes = [v.classification for v in variants if v.classification is not None]
    if not classes:
        return None
    n = Counter(classes)
    n_p = n.get(VariantClassification.PATHOGENIC, 0)
    n_lp = n.get(VariantClassification.LIKELY_PATHOGENIC, 0)
    n_b = n.get(VariantClassification.BENIGN, 0)
    n_lb = n.get(VariantClassification.LIKELY_BENIGN, 0)
    pts = 0.0
    if n_p:
        pts += 2.0
    if n_lp:
        pts += 1.0
    pts += max(n_p - 1, 0) + max(n_lp - 1, 0)
    if n_b:
        pts -= 2.0
    if n_lb:
        pts -= 1.0
    pts -= max(n_b - 1, 0) + max(n_lb - 1, 0)
    return pts


def apply_sm18_multiplier(
    points: float | None,
    gencc_mechanism: GenccMechanism | None,
    exon_relevance: ExonRelevance | None,
    gene_disease_validity: GeneDiseaseValidity | None,
) -> float | None:
    """SM 18 mechanism x exon-relevance reduction, applied ONLY to positive ``points``.

    None/<=0 pass through. GDV below Moderate (incl. None) -> mechanism treated as Uncertain
    -> x0 (documented project gate, SM 18 L11). None mechanism -> 0.0; None exon -> no
    reduction (x1.0, the generous default, asymmetric with mechanism by project choice).
    Suspected x Most is special-cased to 0.25 (Figure-1-pending assumption), not the 0.125
    product SM 18 declined to use.
    """
    if points is None or points <= 0:
        return points
    if gene_disease_validity not in _GDV_MODERATE_PLUS:
        return 0.0
    mech = _MECHANISM_FRACTION.get(gencc_mechanism, 0.0) if gencc_mechanism else 0.0
    exon = 1.0 if exon_relevance is None else _EXON_FRACTION.get(exon_relevance, 1.0)
    if gencc_mechanism == GenccMechanism.SUSPECTED and exon_relevance == ExonRelevance.MOST:
        fraction = 0.25
    else:
        fraction = mech * exon
    return points * fraction
```

- [ ] **Step 5: Implement `scoring/__init__.py` (minimal — ScoreResult only for now)**

The nonsense scorer does not exist until Task 2, so Task 1's `__init__` exports only
`ScoreResult`. Task 2 Step 5 extends this file with the `reference_score_nonsense` import.

```python
"""Reference (non-authoritative) scoring layer for the SVCv4 model.

CSpec is the authoritative scorer. This package mirrors the documented Supplementary-Material
point rules for tests, worked examples, and the practice-variant-set. It is intentionally NOT
re-exported from the top-level ``svcv4_model`` package (so schema generation ignores it).
"""

from svcv4_model.scoring.result import ScoreResult

__all__ = ["ScoreResult"]
```

- [ ] **Step 6: Run the primitive tests**

Run: `uv run pytest tests/test_scoring_primitives.py -q`
Expected: all primitive tests PASS (they import `ScoreResult` and `svcv4_model.scoring.primitives` directly; the nonsense scorer is added in Task 2).

- [ ] **Step 7: Commit**

```bash
git add src/svcv4_model/scoring/__init__.py src/svcv4_model/scoring/result.py src/svcv4_model/scoring/primitives.py tests/test_scoring_primitives.py
git commit -m "feat(scoring): add non-authoritative ScoreResult + shared primitives"
```

---

## Task 2: `reference_score_nonsense` (TDD)

**Files:**
- Create: `src/svcv4_model/scoring/pfd/__init__.py`, `src/svcv4_model/scoring/pfd/nonsense.py`
- Modify: `src/svcv4_model/scoring/__init__.py` (add the nonsense import/export)
- Test: `tests/test_nonsense_scoring.py`

- [ ] **Step 1: Write the failing test** — `tests/test_nonsense_scoring.py`

```python
"""Tests for reference_score_nonsense (non-authoritative)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, GenccMechanism, MechanismExonRelevanceEvidence
from svcv4_model.nonsense import (
    NonsenseAssessment,
    NonsensePredictionOutcome,
    NonsensePredictiveEvidence,
)
from svcv4_model.pfd import PfdParentCode
from svcv4_model.scoring import reference_score_nonsense

MOD = GeneDiseaseValidity.MODERATE


def test_yellow_maximal() -> None:
    a = NonsenseAssessment(
        prediction_outcome=NonsensePredictionOutcome.NMD_NO_RESCUE,
        parent_code=PfdParentCode.NUL,
        predictive=NonsensePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        fxn_points=2.0,
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="a", classification=VariantClassification.PATHOGENIC)]
        ),
    )
    r = reference_score_nonsense(a, gene_disease_validity=MOD)
    assert r.parent_code == "NUL"
    assert r.sub_code_points["PRD"] == 6.0
    assert r.sub_code_points["FXN"] == 2.0
    assert r.sub_code_points["INF"] == 2.0
    assert r.held_combined["PRD+FXN"] == 8.0
    assert r.parent_total == 10.0  # capped at +10
    assert r.authoritative is False
    assert r.provenance  # non-empty trail


def test_violet_reduced_mechanism_and_fxn_nd() -> None:
    a = NonsenseAssessment(
        prediction_outcome=NonsensePredictionOutcome.NO_NMD,
        parent_code=PfdParentCode.CDS,
        predictive=NonsensePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.LIKELY, exon_relevance=ExonRelevance.MOST
        ),
        informative=InformativeVariantsEvidence(
            variants=[InformativeVariant(id="b", classification=VariantClassification.BENIGN)]
        ),
    )
    r = reference_score_nonsense(a, gene_disease_validity=MOD)
    assert r.parent_code == "CDS"
    assert r.sub_code_points["PRD"] == 1.5  # 6.0 x 0.5 x 0.5
    assert "FXN" not in r.sub_code_points  # fxn_points absent -> _FXN_ND
    assert r.held_combined["PRD+FXN"] == 1.5  # held = prd alone
    assert r.sub_code_points["INF"] == -2.0
    assert r.parent_total == -0.5


def test_orange_held_cap_is_9() -> None:
    a = NonsenseAssessment(
        prediction_outcome=NonsensePredictionOutcome.NMD_WITH_RESCUE,
        predictive=NonsensePredictiveEvidence(initial_points=6.0),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            gencc_mechanism=GenccMechanism.ESTABLISHED, exon_relevance=ExonRelevance.ALL
        ),
        fxn_points=8.0,
    )
    r = reference_score_nonsense(a, gene_disease_validity=MOD)
    assert r.held_combined["PRD+FXN"] == 9.0  # 6+8 capped at +9 (orange)


def test_empty_assessment_is_all_nd() -> None:
    r = reference_score_nonsense(NonsenseAssessment(), gene_disease_validity=MOD)
    assert r.sub_code_points == {}
    assert r.held_combined == {}
    assert r.parent_total is None
    assert r.parent_code is None
```

- [ ] **Step 2: Run — expect failure** (`reference_score_nonsense` not importable / not implemented).

Run: `uv run pytest tests/test_nonsense_scoring.py -q`

- [ ] **Step 3: Implement `scoring/pfd/__init__.py`** (empty package marker with a one-line docstring).

- [ ] **Step 4: Implement `scoring/pfd/nonsense.py`**

```python
"""Reference (non-authoritative) scorer for the Nonsense workflow (SM 8)."""

from __future__ import annotations

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.nonsense import NonsenseAssessment, NonsensePredictionOutcome
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
)
from svcv4_model.scoring.result import ScoreResult

# per-branch: (parent_code, prd_lo, prd_hi, held_hi)
_BRANCH = {
    NonsensePredictionOutcome.NMD_NO_RESCUE: ("NUL", 0.0, 6.0, 10.0),
    NonsensePredictionOutcome.NMD_WITH_RESCUE: ("CDS", -1.0, 6.0, 9.0),
    NonsensePredictionOutcome.NO_NMD: ("CDS", 0.0, 6.0, 9.0),
}


def reference_score_nonsense(
    assessment: NonsenseAssessment,
    *,
    gene_disease_validity: GeneDiseaseValidity | None = None,
) -> ScoreResult:
    """Compute the reference (NON-AUTHORITATIVE) Nonsense point total from a captured
    ``NonsenseAssessment``. CSpec is authoritative. FXN is consumed from ``fxn_points``
    (OddsPath is not recomputed)."""
    prov: list[str] = []
    sub: dict[str, float] = {}
    held: dict[str, float] = {}

    outcome = assessment.prediction_outcome
    branch = _BRANCH.get(outcome) if outcome is not None else None
    parent_code = branch[0] if branch else None

    # PRD
    prd: float | None = None
    initial = assessment.predictive.initial_points if assessment.predictive else None
    mer = assessment.mechanism_exon_relevance
    mech = mer.gencc_mechanism if mer else None
    exon = mer.exon_relevance if mer else None
    if initial is None or branch is None:
        prov.append("PRD: _ND (no initial points and/or unknown branch)")
    else:
        adj = apply_sm18_multiplier(initial, mech, exon, gene_disease_validity)
        prd = cap(adj, branch[1], branch[2])
        sub["PRD"] = prd
        prov.append(
            f"PRD: initial {initial} x SM18(mech={mech}, exon={exon}, "
            f"gdv={gene_disease_validity}) = {adj}, capped [{branch[1]}, {branch[2]}] -> {prd}"
        )

    # FXN (consumed, not recomputed)
    fxn = assessment.fxn_points
    if fxn is None:
        prov.append("FXN: _ND (no coded fxn_points captured; OddsPath not recomputed)")
    else:
        sub["FXN"] = fxn
        prov.append(f"FXN: consumed coded value {fxn}")

    # held PRD+FXN
    held_hi = branch[3] if branch else 9.0
    held_val = hold_combined(prd, fxn, lo=-8.0, hi=held_hi)
    if held_val is not None:
        held["PRD+FXN"] = held_val
        prov.append(f"held PRD+FXN: {held_val} (cap [-8.0, {held_hi}])")

    # INF
    inf: float | None = None
    if assessment.informative is not None:
        inf = cap(informative_points(assessment.informative.variants), -8.0, 8.0)
    if inf is None:
        prov.append("INF: _ND (no classified informative variants)")
    else:
        sub["INF"] = inf
        prov.append(f"INF: {inf} (cap [-8.0, 8.0])")

    # parent total
    parent_total = hold_combined(held_val, inf, lo=-8.0, hi=10.0)
    if parent_total is not None:
        prov.append(f"parent_total: {parent_total} (cap [-8.0, 10.0])")

    # captured parent_code cross-check (report, do not fix)
    captured = assessment.parent_code
    if captured is not None and parent_code is not None and captured.value != parent_code:
        prov.append(
            f"NOTE: captured parent_code {captured.value} != branch-derived {parent_code}"
        )

    return ScoreResult(
        parent_code=parent_code,
        sub_code_points=sub,
        held_combined=held,
        parent_total=parent_total,
        provenance=prov,
        authoritative=False,
    )
```

- [ ] **Step 5: Add the nonsense export** — `scoring/__init__.py`: restore `from svcv4_model.scoring.nonsense import reference_score_nonsense`. **Correction:** the import path is `svcv4_model.scoring.pfd.nonsense`, so use:

```python
from svcv4_model.scoring.pfd.nonsense import reference_score_nonsense
from svcv4_model.scoring.result import ScoreResult

__all__ = ["ScoreResult", "reference_score_nonsense"]
```

- [ ] **Step 6: Run the full suite**

Run: `uv run pytest -q`
Expected: all PASS (primitives + nonsense + the whole existing suite).

- [ ] **Step 7: Commit**

```bash
git add src/svcv4_model/scoring/pfd/__init__.py src/svcv4_model/scoring/pfd/nonsense.py src/svcv4_model/scoring/__init__.py tests/test_nonsense_scoring.py
git commit -m "feat(scoring): add reference_score_nonsense (SM 8, all 3 branches)"
```

---

## Task 3: Docs — `reference/scoring.md`

**Files:**
- Create: `docs/reference/scoring.md`
- Modify: `mkdocs.yml` (nav under Reference)

- [ ] **Step 1: Create `docs/reference/scoring.md`**

````markdown
# Reference scoring (non-authoritative)

!!! warning "Non-authoritative"

    The `svcv4_model.scoring` layer is a **reference** implementation of the documented
    Supplementary-Material point rules — for tests, worked examples, and the
    practice-variant-set. **ClinGen CSpec is the authoritative scorer.** Any divergence from
    CSpec is a bug in *this* layer, never in CSpec. Every result is a `ScoreResult` with
    `authoritative = False` (constructing it `True` raises).

`reference_score_*` functions are pure: they take a captured assessment/evidence entity and
return a `ScoreResult` — the coded sub-code points, any held-combined intermediates, the
capped parent-code total, and a `provenance` trail. A step that is un-scoreable / No-Data is
**omitted** (never recorded as `0.0`). Expert-calibrated inputs (functional OddsPath) are
**consumed** from the analyst's coded value, not recomputed.

```python
from svcv4_model.scoring import reference_score_nonsense
result = reference_score_nonsense(assessment, gene_disease_validity=gdv)
result.parent_total      # e.g. 10.0
result.provenance        # the audit trail, step by step
```

## What is modeled so far

- **Shared primitives** — the SM 18 mechanism/exon multiplier, caps, held-combined, and the
  informative-variant tally (`svcv4_model.scoring.primitives`).
- **Nonsense** (SM 8) — `reference_score_nonsense`, all three branches.

The remaining PFD workflows, POP/LOC/CLN, case aggregation, the classification band, and
`validate_case` follow in later increments (see the scoping doc).

## Known assumption (flagged for WG confirmation)

The SM 18 matrix's **Suspected mechanism × Most exon-relevance** cell was deliberately not
compounded to 12.5% by the Working Group; the authoritative value is in SM 18 Figure 1 (not
in this repo's text extracts). The reference scorer assumes **0.25** (keep the Suspected
fraction, drop the further Most halving) and records the assumption in `provenance`. This
affects only that single matrix cell.
````

- [ ] **Step 2: Add the nav entry** — `mkdocs.yml`, under the `Reference:` section (e.g. after `Known gaps:`):

```yaml
      - Reference scoring: reference/scoring.md
```

- [ ] **Step 3: Build strict**

Run: `uv run mkdocs build --strict`
Expected: 0 warnings referencing the new page.

- [ ] **Step 4: Commit**

```bash
git add docs/reference/scoring.md mkdocs.yml
git commit -m "docs: add the reference-scoring contract page"
```

---

## Task 4: Full quality gates

- [ ] **Step 1: Run everything**

```bash
uv run pytest -q
uv run ruff check .
git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN || echo GATE_DIRTY
uv run mkdocs build --strict
git status --porcelain
```

Expected: pytest all pass; ruff clean; **`GATE_CLEAN`** — critically, `git status --porcelain schemas/json` must show **no new schema files** (the scoring subpackage is not in the root `__all__`, so `export_schemas.py` ignores it; confirm by running `uv run python scripts/export_schemas.py` and checking `git status --porcelain schemas/json` is empty); strict build clean; tree clean except the pre-existing untracked files.

- [ ] **Step 2: Confirm import + no schema leak**

Run: `uv run python -c "from svcv4_model.scoring import reference_score_nonsense, ScoreResult; print('ok')"`
Run: `uv run python scripts/export_schemas.py && git status --porcelain schemas/json`
Expected: `ok`; and the schema status is empty (no `ScoreResult`/scoring schema produced).

- [ ] **Step 3: Ready for code review + PR.**

---

## Notes for the implementer

- **Packaging:** confirm the new `src/svcv4_model/scoring/` (and `scoring/pfd/`) subpackages are importable after install (Step 2 of Task 4). If the build config uses explicit package lists rather than auto-discovery, add the subpackages; most `hatch`/`setuptools`-autodiscovery configs pick them up automatically.
- **Do NOT** add anything to the root `svcv4_model/__init__.py` `__all__` — that would generate a schema and trip the drift gate. The scoring layer is imported via `svcv4_model.scoring`.
- **Line length 100** (ruff), not the 79 the IDE shows.
- `ScoreResult` is a frozen dataclass by design (compute DTO, not a persisted model) — do not convert it to Pydantic.
- The Suspected×Most = 0.25 value is a **flagged assumption** (SM 18 Figure 1 unknown) — keep the provenance flag and the test comment so it is easy to revisit.
