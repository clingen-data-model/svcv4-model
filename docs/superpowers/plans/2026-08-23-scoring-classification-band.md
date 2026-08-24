# Reference Scorer — Classification band (SM 1) — Implementation Plan

> **For agentic workers:** REQUIRED: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add `reference_classify(points)` mapping a Bayesian point total → SVCv4 category
(P/LP/VUS/LB/B) + VUS subclass (low/mid/high). Pure, total, non-authoritative. Aggregation Inc 1.

**Architecture:** New `src/svcv4_model/scoring/classification.py`; imports `VariantClassification`
(model enum); defines `VusSubclass` (StrEnum) + `Classification` (NamedTuple) in the scoring
package (no schema leak). Exported from `scoring/__init__.py`.

**Design:** `docs/superpowers/specs/2026-08-23-scoring-classification-band-design.md` (approved;
all 6 SM 1 boundaries verified in spec-review).

**Band (SM 1 L6–14):** `≤−4 B` / `(−4,−1] LB` / `(−1,+2) VUS-low` / `[2,4) VUS-mid` /
`[4,6) VUS-high` / `[6,10) LP` / `≥10 P`.

---

## Task 1: `reference_classify` (TDD)

**Files:** Create `src/svcv4_model/scoring/classification.py`, `tests/test_classification_band.py`;
modify `src/svcv4_model/scoring/__init__.py`.

- [ ] **Step 1: Write the failing test** — `tests/test_classification_band.py`

```python
"""Tests for reference_classify (SM 1 classification band, non-authoritative)."""

from __future__ import annotations

from svcv4_model.informative import VariantClassification as VC
from svcv4_model.scoring import Classification, VusSubclass, reference_classify


def test_midband_representatives() -> None:
    assert reference_classify(12.0) == Classification(VC.PATHOGENIC, None)
    assert reference_classify(8.0) == Classification(VC.LIKELY_PATHOGENIC, None)
    assert reference_classify(5.0) == Classification(VC.VUS, VusSubclass.HIGH)
    assert reference_classify(3.0) == Classification(VC.VUS, VusSubclass.MID)
    assert reference_classify(0.0) == Classification(VC.VUS, VusSubclass.LOW)
    assert reference_classify(-2.0) == Classification(VC.LIKELY_BENIGN, None)
    assert reference_classify(-6.0) == Classification(VC.BENIGN, None)


def test_exact_boundaries() -> None:
    assert reference_classify(-4.0) == Classification(VC.BENIGN, None)
    assert reference_classify(-1.0) == Classification(VC.LIKELY_BENIGN, None)
    assert reference_classify(2.0) == Classification(VC.VUS, VusSubclass.MID)
    assert reference_classify(4.0) == Classification(VC.VUS, VusSubclass.HIGH)
    assert reference_classify(6.0) == Classification(VC.LIKELY_PATHOGENIC, None)
    assert reference_classify(10.0) == Classification(VC.PATHOGENIC, None)


def test_across_boundary_neighbours() -> None:
    assert reference_classify(-3.999) == Classification(VC.LIKELY_BENIGN, None)
    assert reference_classify(-0.999) == Classification(VC.VUS, VusSubclass.LOW)
    assert reference_classify(1.999) == Classification(VC.VUS, VusSubclass.LOW)
    assert reference_classify(3.999) == Classification(VC.VUS, VusSubclass.MID)
    assert reference_classify(5.999) == Classification(VC.VUS, VusSubclass.HIGH)
    assert reference_classify(9.999) == Classification(VC.LIKELY_PATHOGENIC, None)


def test_vus_subclass_discipline() -> None:
    for p in (-6.0, -4.0, -2.0, -1.0, 0.0, 2.0, 4.0, 6.0, 10.0, 12.0):
        c = reference_classify(p)
        if c.category == VC.VUS:
            assert c.vus_subclass is not None
        else:
            assert c.vus_subclass is None


def test_namedtuple_ergonomics() -> None:
    cat, sub = reference_classify(3.0)
    assert cat == VC.VUS
    assert sub == VusSubclass.MID
    assert reference_classify(3.0).category == VC.VUS


def test_extremes_not_clamped() -> None:
    assert reference_classify(50.0).category == VC.PATHOGENIC
    assert reference_classify(-50.0).category == VC.BENIGN
```

- [ ] **Step 2: Run — expect ImportError.** `uv run pytest tests/test_classification_band.py -q`

- [ ] **Step 3: Implement** — create `src/svcv4_model/scoring/classification.py`:

```python
"""Reference (non-authoritative) classification band (SM 1): points -> category + VUS subclass.

CSpec is authoritative. Maps a summed Bayesian point total to the SM 1 pathogenicity descriptor
(``SM01-glossary.txt`` L6-14). Pure and total -- every finite point value maps to exactly one
band; there is no No-Data return (that concept belongs to the per-code scorers). ``VusSubclass``
lives here (not the model) so it stays off the JSON-Schema surface. The summing that produces
``points`` and the open global-sum-clamp question live in later aggregation increments.
"""

from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple

from svcv4_model.informative import VariantClassification


class VusSubclass(StrEnum):
    """The three SM 1 VUS subclasses (low is LB-adjacent; high is LP-adjacent)."""

    LOW = "VUS-low"
    MID = "VUS-mid"
    HIGH = "VUS-high"


class Classification(NamedTuple):
    """A banded result: the 5-way category, plus the VUS subclass iff category is VUS."""

    category: VariantClassification
    vus_subclass: VusSubclass | None


def reference_classify(points: float) -> Classification:
    """Map a Bayesian point total to the reference (NON-AUTHORITATIVE) SM 1 band.

    ``>=+10`` P; ``[+6,+10)`` LP; ``[+4,+6)`` VUS-high; ``[+2,+4)`` VUS-mid; ``(-1,+2)`` VUS-low;
    ``(-4,-1]`` LB; ``<=-4`` B. Not clamped (SM 1 P is open-ended ``>=+10``); the global-sum-clamp
    question is deferred to the cross-code-combination increment.
    """
    if points >= 10.0:
        return Classification(VariantClassification.PATHOGENIC, None)
    if points >= 6.0:
        return Classification(VariantClassification.LIKELY_PATHOGENIC, None)
    if points >= 4.0:
        return Classification(VariantClassification.VUS, VusSubclass.HIGH)
    if points >= 2.0:
        return Classification(VariantClassification.VUS, VusSubclass.MID)
    if points > -1.0:
        return Classification(VariantClassification.VUS, VusSubclass.LOW)
    if points > -4.0:
        return Classification(VariantClassification.LIKELY_BENIGN, None)
    return Classification(VariantClassification.BENIGN, None)
```

- [ ] **Step 4: Export** — `src/svcv4_model/scoring/__init__.py`:
    - Add `from svcv4_model.scoring.classification import (Classification, VusSubclass,
      reference_classify)` — isort places `scoring.classification` **before**
      `scoring.hod.clinical` (`classification` < `hod`).
    - Add `"Classification"`, `"VusSubclass"`, `"reference_classify"` to `__all__`. Placement per
      isort's `order-by-type` (classes then functions, each alphabetical): `"Classification"` goes
      with the other classes at the top (after `"ScoreResult"`? — no: `Classification` < `Mission…`;
      alphabetically `Classification` < `MissenseScoreResult` < `ScoreResult`, so it sorts FIRST
      among the exported classes); `"VusSubclass"` after `ScoreResult` (`ScoreResult` < `VusSubclass`);
      `"reference_classify"` among the `reference_*` names (`reference_classify` < `reference_score_*`
      — `classify` < `score`, so first). **Let ruff/isort settle exact order — run `ruff check
      --fix` and accept its ordering.**

- [ ] **Step 5: Run** `uv run pytest tests/test_classification_band.py -q` — all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/svcv4_model/scoring/classification.py tests/test_classification_band.py \
        src/svcv4_model/scoring/__init__.py
git commit -m "feat(scoring): add reference_classify (SM 1 classification band) -- aggregation Inc 1"
```

---

## Task 2: Docs

**Files:** Modify `docs/reference/scoring.md`, `docs/reference/known-gaps.md`.

- [ ] **Step 1: `scoring.md`** — add a short "Classification band" subsection: `reference_classify`
  maps a summed point total → SM 1 category + VUS subclass
  (`≤−4 B / (−4,−1] LB / (−1,+2) VUS-low / [2,4) VUS-mid / [4,6) VUS-high / [6,10) LP / ≥10 P`);
  the capstone the aggregation increments feed; not clamped (global-sum clamp is an open WG
  question).

- [ ] **Step 2: `known-gaps.md`** — add a Working-Group-follow-up row: the **global sum clamp** is
  unspecified/contradictory (SM 1 makes P open-ended `≥+10`, but the GA4GH JSON `scale` caps at
  `10.0`/`−8.0`); `reference_classify` does not clamp (faithful to SM 1); the clamp belongs to the
  future cross-code-combination increment.

- [ ] **Step 3: Build strict** — `uv run mkdocs build --strict` (exit 0).
- [ ] **Step 4: Commit** — `git commit -am "docs: classification band + global-clamp known-gap"`

---

## Task 3: Full quality gates

- [ ] `uv run pytest -q` (all pass, no regressions).
- [ ] `uv run ruff check .` (LL 100, clean).
- [ ] Drift gate: `uv run python scripts/export_schemas.py` then
  `git diff --quiet -- schemas/json docs/workflows/case-model.md` (clean — `classification.py`
  and `VusSubclass` are in the non-re-exported scoring package).
- [ ] `uv run mkdocs build --strict` (exit 0).
- [ ] No scorer schema leaked (`git status` shows nothing new under `schemas/json`).
- [ ] Clean tree.

---

## Notes for the implementer

- The cascade order is exact and verified boundary-by-boundary in spec-review — do not reorder or
  change any `>=` / `>` operator. `-1.0` must be LB (`> -1.0` is False for -1.0 → falls to
  `> -4.0` → LB); `-4.0` must be B.
- `Classification` is a `NamedTuple`, so `==` compares by value (the tests rely on this) and it
  unpacks as `cat, sub = reference_classify(p)`.
- `VusSubclass` and `Classification` MUST stay in the scoring package (not `svcv4_model/`) — the
  scoring package is not re-exported, so nothing enters the JSON Schema. Confirm the drift gate is
  clean.
- Accept ruff/isort's exact `__all__` and import ordering (`ruff check --fix`).
