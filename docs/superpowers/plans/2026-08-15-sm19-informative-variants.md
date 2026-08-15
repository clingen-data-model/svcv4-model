# SM 19 Informative Variants Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture the SVCv4 SM 19 informative-variants inputs as a new `InformativeVariantsEvidence` model — the second PFD submodule — documenting the scoring without computing it.

**Architecture:** A new `src/svcv4_model/informative.py` module holds two `StrEnum`s (`VariantClassification`, `SimilarityBasis`), the `InformativeVariant` sub-model, and the `InformativeVariantsEvidence` payload (a curation-level PFD entity, `MechanismExonRelevanceEvidence` pattern) with a `variants: list[InformativeVariant]`. No Case applicability matrix; `case-model.md` untouched. Docs mark SM 19 modeled.

**Tech Stack:** Python 3 / Pydantic v2 (`StrEnum`, `ConfigDict(extra="forbid")`), `uv`, pytest, ruff (line-length 100), MkDocs (`strict: true`).

**Spec:** `docs/superpowers/specs/2026-08-15-sm19-informative-variants-design.md`

---

## File Structure

- `src/svcv4_model/informative.py` — **new.** `VariantClassification`, `SimilarityBasis`, `InformativeVariant`, `InformativeVariantsEvidence`. Single responsibility: the SM 19 evidence payload.
- `src/svcv4_model/__init__.py` — export the four new public names.
- `tests/test_pfd_informative.py` — **new.** Round-trip, permissiveness, enum acceptance, package-root import.
- `schemas/json/InformativeVariant.schema.json`, `schemas/json/InformativeVariantsEvidence.schema.json` — **generated**; commit.
- `docs/workflows/pfd/index.md`, `docs/reference/spec-alignment.md`, `docs/reference/known-gaps.md`, `docs/reference/model.md` — docs.

**Conventions (mirror `mechanism.py`):** `from __future__ import annotations`; every field `Field(default=None, ...)` (the list field uses `Field(default_factory=list, ...)`); `ConfigDict(extra="forbid")`; wrap descriptions to stay ≤100 chars; `StrEnum` members `VALUE = "VALUE"`.

---

## Chunk 1: Model + export + schema regeneration

### Task 1: `InformativeVariantsEvidence` model + export (TDD)

**Files:**
- Create: `src/svcv4_model/informative.py`
- Modify: `src/svcv4_model/__init__.py`
- Create: `tests/test_pfd_informative.py`

- [ ] **Step 1: Write the failing test.** Create `tests/test_pfd_informative.py`:

```python
"""Tests for the SVCv4 PFD Informative Variants model (SM 19)."""

from __future__ import annotations

import pytest

from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    SimilarityBasis,
    VariantClassification,
)


def _maximal_variant() -> InformativeVariant:
    return InformativeVariant(
        id="clinvar:VCV000000009",
        classification=VariantClassification.PATHOGENIC,
        similarity_basis=SimilarityBasis.SAME_EXON,
        distinct_evidence_from_vbc=True,
        star_rating=3,
        circularity_checked=True,
    )


def test_evidence_round_trips_json() -> None:
    original = InformativeVariantsEvidence(variants=[_maximal_variant()])
    rehydrated = InformativeVariantsEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_evidence_is_permissive_when_empty() -> None:
    assert InformativeVariantsEvidence().variants == []


def test_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        InformativeVariantsEvidence(not_a_field=1)


def test_variant_forbids_extra() -> None:
    with pytest.raises(ValueError):
        InformativeVariant(not_a_field=1)


def test_classification_values_round_trip() -> None:
    for cls in VariantClassification:
        assert InformativeVariant(classification=cls).classification is cls


def test_similarity_basis_values_round_trip() -> None:
    for basis in SimilarityBasis:
        assert InformativeVariant(similarity_basis=basis).similarity_basis is basis


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "InformativeVariantsEvidence" in svcv4_model.__all__
```

- [ ] **Step 2: Run to verify failure.**

Run: `uv run pytest tests/test_pfd_informative.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'svcv4_model.informative'`.

- [ ] **Step 3: Create `src/svcv4_model/informative.py`** with exactly the code from spec §5.1 (the two enums, `InformativeVariant`, then `InformativeVariantsEvidence`). Reproduce the field descriptions **as wrapped in the spec** (do not re-flatten — they are wrapped to stay ≤100 chars). Imports only: `from __future__ import annotations`, `from enum import StrEnum`, `from pydantic import BaseModel, ConfigDict, Field` (this module reuses nothing from other svcv4 modules).

- [ ] **Step 4: Export the four names** in `src/svcv4_model/__init__.py`:
  - Add a new import block **after `from svcv4_model.evidence_line import EvidenceLine` and before `from svcv4_model.inputs import MDE, VBC`** (`informative` < `inputs`; ruff isort `I` is enabled — keep alphabetical or run `uv run ruff check --fix src/svcv4_model/__init__.py`):

    ```python
    from svcv4_model.informative import (
        InformativeVariant,
        InformativeVariantsEvidence,
        SimilarityBasis,
        VariantClassification,
    )
    ```
  - Add to `__all__` (ASCII order): `"InformativeVariant"` and `"InformativeVariantsEvidence"` in the `G…`/`M…` neighborhood (after `"GeneDiseaseValidity"`, before `"ManeStatus"`); `"SimilarityBasis"` after `"Sex"`/before `"Statement"`; `"VariantClassification"` after `"TriState"`/before `"VariantPathogenicityClassification"`. (Order isn't ruff-enforced for `__all__`; keep it tidy.)

- [ ] **Step 5: Run tests + lint to verify green.**

Run: `uv run pytest tests/test_pfd_informative.py -q && uv run ruff check src/svcv4_model/informative.py src/svcv4_model/__init__.py tests/test_pfd_informative.py && uv run ruff format --check src/svcv4_model/informative.py src/svcv4_model/__init__.py tests/test_pfd_informative.py`
Expected: tests PASS; ruff reports no errors; "would reformat" nothing. If E501 fires, split a `description` across two parenthesized fragments; if I001 fires on the import, run `ruff check --fix`.

- [ ] **Step 6: Run the full suite.**

Run: `uv run pytest -q`
Expected: PASS (no schema/model-parity test exists, so nothing else breaks).

- [ ] **Step 7: Commit.**

```bash
git add src/svcv4_model/informative.py src/svcv4_model/__init__.py tests/test_pfd_informative.py
git commit -m "feat: model SM 19 informative variants (second PFD submodule)"
```

### Task 2: Regenerate JSON Schemas

**Files:** Create (generated): `schemas/json/InformativeVariant.schema.json`, `schemas/json/InformativeVariantsEvidence.schema.json`

- [ ] **Step 1: Regenerate.**

Run: `uv run python scripts/export_schemas.py`
Expected: output lists the two new files among those written.

- [ ] **Step 2: Verify only the two new files appear, nothing else changed.**

Run: `git status --short schemas/json docs/workflows/case-model.md`
Expected: exactly two **new** files — `InformativeVariant.schema.json` and `InformativeVariantsEvidence.schema.json`. `docs/workflows/case-model.md` and all existing `schemas/json/*` (incl. `Case.schema.json`, `case/*`) must be **unchanged**. If anything else changed, stop and investigate.

- [ ] **Step 3: Commit the generated schemas.**

```bash
git add schemas/json/InformativeVariant.schema.json schemas/json/InformativeVariantsEvidence.schema.json
git commit -m "chore: generate JSON schemas for InformativeVariantsEvidence"
```

- [ ] **Step 4: Confirm the drift gate (exact CI command).**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo CLEAN`
Expected: `CLEAN`.

---

## Chunk 2: Documentation

Pure docs. Verification is `mkdocs build --strict`. External SM link isn't checked by mkdocs — spot check manually.

### Task 3: `pfd/index.md` — add the modeled Informative Variants subsection

**Files:** Modify `docs/workflows/pfd/index.md`

- [ ] **Step 1: Add a new subsection** after the "### Molecular Mechanism & Exon Relevance ✅ modeled (inputs)" block (which ends just before the "The remaining shared sub-modules …" sentence). Title it `### Informative Variants ✅ modeled (inputs)`. Content: the second shared sub-module is modeled as `InformativeVariantsEvidence` (a list of `InformativeVariant`), each capturing the variant `id`, its `classification`, the `similarity_basis` (position/exon/effect/gene-deletion), and the eligibility gates (`distinct_evidence_from_vbc`, `star_rating`, `circularity_checked`). Document the scoring, **not computed**: +2.0 for the first distinct Pathogenic informative variant, +1.0 each additional distinct P; +1.0 each for LP-only; **only distinct variants count** (observation counts don't matter); its own cap of **−8 to +8**. Note the B/LB negative side is **inferred from the cap**, not spelled out in SM 19. Note that INF points are **not reduced by the SM 18 matrix**. Link [SM 19](https://docs.google.com/document/d/1hNfdtdvDT4dob9oDBrL_UzVV_MYiWnwERfli76EAbyQ/edit).

- [ ] **Step 2: Update the "remaining shared sub-modules" sentence** (currently "The remaining shared sub-modules (Informative Variants, Functional Assays, Determining Critical Amino Acids), …") to **drop Informative Variants** → "(Functional Assays, Determining Critical Amino Acids)".

- [ ] **Step 3: Verify.** `grep -n "Informative Variants ✅ modeled" docs/workflows/pfd/index.md` matches; `grep -n "remaining shared sub-modules (Informative Variants" docs/workflows/pfd/index.md` returns nothing.

### Task 4: `spec-alignment.md` — SM 19 row → modeled

**Files:** Modify `docs/reference/spec-alignment.md`

- [ ] **Step 1:** Change the SM 19 row (currently `(shared sub-module) | Not yet modeled`) to: "**Modeled (inputs)** — `InformativeVariantsEvidence` captures the distinct informative variants (classification, similarity basis, eligibility flags); the scoring is documented, not computed. See `[Predictive & Functional Data](../workflows/pfd/index.md)`." Keep the SM 19 Google Doc link on the title.

### Task 5: `known-gaps.md` — note SM 19 landed

**Files:** Modify `docs/reference/known-gaps.md`

- [ ] **Step 1:** Update the "Full PFD modeling" content-gap row: SM 18 **and now SM 19** are modeled; what remains is SM 20 (Functional Assays), SM 7 (Critical Amino Acids), the PRD/FXN/INF scaffold + parent codes, the per-variant-type workflows, and the scoring computation.

### Task 6: `model.md` — render the new class

**Files:** Modify `docs/reference/model.md`

- [ ] **Step 1:** After the `::: svcv4_model.MechanismExonRelevanceEvidence` entry (the last one), add a `---` separator and `::: svcv4_model.InformativeVariantsEvidence`.

### Task 7: Build + commit docs

- [ ] **Step 1: Build strict.**

Run: `uv run mkdocs build --strict`
Expected: no warnings/errors. Fix any broken internal link (don't disable strict). If the plan doc itself trips a relative-link warning, wrap the offending `[text](../path)` example in backticks.

- [ ] **Step 2: Manual external-link spot check.** Open the SM 19 link once to confirm it resolves.

- [ ] **Step 3: Commit.**

```bash
git add docs/workflows/pfd/index.md docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: model SM 19 informative variants (second PFD submodule)"
```

---

## Done criteria

- `uv run pytest -q` green (new `tests/test_pfd_informative.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean.
- `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md` → clean (two new schema files committed).
- `uv run mkdocs build --strict` passes.
- `grep -n "remaining shared sub-modules (Informative Variants" docs/workflows/pfd/index.md` → nothing.
- No scoring-computation code added (scope boundary respected).
