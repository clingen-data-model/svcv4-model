# CLN_CCS Case-Control Studies Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture the SVCv4 `CLN_CCS` case-control study result as a new `CaseControlStudyEvidence` model, documenting the scoring and exclusivity rule without computing them.

**Architecture:** A new `src/svcv4_model/case_control.py` module holds one permissive `CaseControlStudyEvidence` payload (a curation-level, study-level EvidenceItem payload, `PopulationEvidence` pattern) — deliberately **not** part of `Case`, not a `Workflow` enum entry, not in the Case applicability matrix. `case-model.md` untouched. Docs flip CLN_CCS from "not yet modeled" to modeled.

**Tech Stack:** Python 3 / Pydantic v2 (`BaseModel`, `ConfigDict(extra="forbid")`), `uv`, pytest, ruff (line-length 100), MkDocs (`strict: true`).

**Spec:** `docs/superpowers/specs/2026-08-15-cln-ccs-modeling-design.md`

---

## File Structure

- `src/svcv4_model/case_control.py` — **new.** `CaseControlStudyEvidence` (no enums). Single responsibility: the CLN_CCS study payload.
- `src/svcv4_model/__init__.py` — export the one new name.
- `tests/test_case_control.py` — **new.** Round-trip, permissiveness, package-root import.
- `schemas/json/CaseControlStudyEvidence.schema.json` — **generated**; commit (`git add`).
- `docs/workflows/hod/cln/index.md`, `docs/reference/spec-alignment.md`, `docs/reference/known-gaps.md`, `docs/reference/model.md` — docs.

**Conventions (mirror `population.py`):** `from __future__ import annotations`; every field `Field(default=None, ...)`; `ConfigDict(extra="forbid")`; descriptions ≤100 chars.

---

## Chunk 1: Model + export + schema regeneration

### Task 1: `CaseControlStudyEvidence` model + export (TDD)

**Files:**
- Create: `src/svcv4_model/case_control.py`
- Modify: `src/svcv4_model/__init__.py`
- Create: `tests/test_case_control.py`

- [ ] **Step 1: Write the failing test.** Create `tests/test_case_control.py`:

```python
"""Tests for the SVCv4 CLN_CCS case-control study model."""

from __future__ import annotations

import pytest

from svcv4_model.case_control import CaseControlStudyEvidence


def _maximal() -> CaseControlStudyEvidence:
    return CaseControlStudyEvidence(
        odds_ratio=5.5,
        ci_lower=3.1,
        ci_upper=9.8,
        case_cohort_size=250,
        case_variant_count=12,
        control_cohort_size=5000,
        controls_matched=True,
        ascertainment_bias_considered=True,
    )


def test_round_trips_json() -> None:
    original = _maximal()
    rehydrated = CaseControlStudyEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_is_permissive_when_empty() -> None:
    assert CaseControlStudyEvidence().odds_ratio is None


def test_forbids_extra() -> None:
    with pytest.raises(ValueError):
        CaseControlStudyEvidence(not_a_field=1)


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "CaseControlStudyEvidence" in svcv4_model.__all__
```

- [ ] **Step 2: Run to verify failure.**

Run: `uv run pytest tests/test_case_control.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'svcv4_model.case_control'`.

- [ ] **Step 3: Create `src/svcv4_model/case_control.py`** with exactly the `CaseControlStudyEvidence` code from spec §5.1 (module docstring, `from __future__ import annotations`, `from pydantic import BaseModel, ConfigDict, Field`, then the class with its eight optional fields). No enums.

- [ ] **Step 4: Export the name** in `src/svcv4_model/__init__.py`:
  - Add `from svcv4_model.case_control import CaseControlStudyEvidence` **after the `from svcv4_model.case import (...)` block (the line that closes it with `)`) and before `from svcv4_model.classification import VariantPathogenicityClassification`** (`case` < `case_control` < `classification`; ruff isort `I` is enabled — or run `uv run ruff check --fix src/svcv4_model/__init__.py`).
  - Add `"CaseControlStudyEvidence"` to `__all__` between `"Case"` and `"CaseRelative"` (`CaseC…` < `CaseR…`).

- [ ] **Step 5: Run tests + lint to verify green.**

Run: `uv run pytest tests/test_case_control.py -q && uv run ruff check src/svcv4_model/case_control.py src/svcv4_model/__init__.py tests/test_case_control.py && uv run ruff format --check src/svcv4_model/case_control.py src/svcv4_model/__init__.py tests/test_case_control.py`
Expected: tests PASS; ruff no errors; "would reformat" nothing. If I001 fires on the import, run `ruff check --fix`.

- [ ] **Step 6: Run the full suite.**

Run: `uv run pytest -q`
Expected: PASS.

- [ ] **Step 7: Commit.**

```bash
git add src/svcv4_model/case_control.py src/svcv4_model/__init__.py tests/test_case_control.py
git commit -m "feat: model CLN_CCS case-control study evidence"
```

### Task 2: Regenerate JSON Schema

**Files:** Create (generated): `schemas/json/CaseControlStudyEvidence.schema.json`

- [ ] **Step 1: Regenerate.**

Run: `uv run python scripts/export_schemas.py`
Expected: output lists the one new file `CaseControlStudyEvidence.schema.json`.

- [ ] **Step 2: Verify only the one new file appears, nothing else changed.**

Run: `git status --short schemas/json docs/workflows/case-model.md`
Expected: exactly one **new (untracked)** file — `schemas/json/CaseControlStudyEvidence.schema.json`. `docs/workflows/case-model.md` and all existing `schemas/json/*` must be **unchanged**.

- [ ] **Step 3: Commit the generated schema (`git add` is essential).**

```bash
git add schemas/json/CaseControlStudyEvidence.schema.json
git commit -m "chore: generate JSON schema for CaseControlStudyEvidence"
```

(The CI drift gate `git diff --quiet -- schemas/json` does **not** flag a forgotten *untracked* schema, so the `git add` here is load-bearing.)

- [ ] **Step 4: Confirm the drift gate (exact CI command).**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo CLEAN`
Expected: `CLEAN`.

---

## Chunk 2: Documentation

Pure docs. Verification is `mkdocs build --strict`. External SM link isn't checked by mkdocs — spot check manually.

### Task 3: `cln/index.md` — CLN_CCS admonition → modeled

**Files:** Modify `docs/workflows/hod/cln/index.md`

- [ ] **Step 1: Read the current admonition** (the `!!! note "Not yet modeled here"` block for CLN_CCS). Rewrite it:
  - Change the title to `!!! note "Modeled here — inputs captured"`.
  - Keep the first paragraph describing the process (variant-specific case-control analysis; eligibility ≥5 case-variant / ≥100 cases / matched controls; `OR > 5.0` → `CLN_CCS_+4.0`; CI including 1.0 → no points; OR ≤ 1.0 → benignity; the exclusivity rule "all other CLN codes NA except `CLN_DNV`").
  - Replace the second paragraph's "it is simply **not yet modeled** here, alongside [Population (POP)] and [Predictive & Functional Data]" with: the inputs are **now modeled** as `CaseControlStudyEvidence` (the OR, CI bounds, case/control cohort sizes, case-variant count, and robustness flags); **scoring is documented, not computed**; only *finer* case-control guidance is deferred to future SVCv4 iterations. (Do not re-assert that POP/PFD are unmodeled — they are now modeled too.)

- [ ] **Step 2 (optional):** In the code table, the `| \`CLN_CCS\` | Case-control studies | — |` row's "Detailed here" cell may stay `—` (CLN_CCS has no dedicated workflow page) or link to the admonition; leaving `—` is fine.

- [ ] **Step 3: Verify.** `grep -ni "not yet modeled" docs/workflows/hod/cln/index.md` returns **0** — this catches both the admonition title *and* the body sentence (both currently say "not yet modeled"; both must be gone).

### Task 4: `spec-alignment.md` — SM 4 row CLN_CCS clause → modeled

**Files:** Modify `docs/reference/spec-alignment.md`

- [ ] **Step 1:** In the SM 4 row, change the CLN_CCS clause from "`CLN_CCS` has a defined case-control process … but is **not yet modeled** here — a capture-only case-control study result (OR, CI, cohort sizes, variant counts) is the natural shape (see the note on the CLN page)" to state it **is now captured** as `CaseControlStudyEvidence` (OR, CI, cohort sizes, robustness flags); scoring documented, not computed. Keep the SM 4 Google Doc link on the title.

- [ ] **Step 2: Verify.** `grep -ni "not yet modeled" docs/reference/spec-alignment.md` shows no CLN_CCS/SM 4 hit (rows 6–17 for the still-unmodeled PFD supplements may still match — confirm the SM 4 row itself no longer says "not yet modeled").

### Task 5: `known-gaps.md` — remove the CLN_CCS row

**Files:** Modify `docs/reference/known-gaps.md`

- [ ] **Step 1:** Remove the "`CLN_CCS` (case-control studies) not modeled" model-gap row. Prefer exact-string Edit; if it fails on a special char, use `grep -v 'CLN_CCS` (case-control studies) not modeled'` (or a unique substring) to drop the line.

- [ ] **Step 2: Verify.** `grep -c "case-control studies) not modeled" docs/reference/known-gaps.md` returns 0.

### Task 6: `model.md` — render the new class

**Files:** Modify `docs/reference/model.md`

- [ ] **Step 1:** After the last `:::` entry (`::: svcv4_model.InformativeVariantsEvidence`), add a `---` separator and `::: svcv4_model.CaseControlStudyEvidence`.

### Task 7: Build + commit docs

- [ ] **Step 1: Build strict.**

Run: `uv run mkdocs build --strict`
Expected: no warnings/errors. Fix any broken internal link (don't disable strict). If the plan doc itself trips a relative-link warning, wrap the offending `[text](../path)` example in backticks.

- [ ] **Step 2: Manual external-link spot check.** Open the SM 4 link once to confirm it resolves.

- [ ] **Step 3: Commit.**

```bash
git add docs/workflows/hod/cln/index.md docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: model CLN_CCS case-control studies"
```

---

## Done criteria

- `uv run pytest -q` green (new `tests/test_case_control.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean.
- `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md` → clean (new schema committed).
- `uv run mkdocs build --strict` passes.
- `grep -c "case-control studies) not modeled" docs/reference/known-gaps.md` → 0.
- No scoring-computation code added (scope boundary respected).
