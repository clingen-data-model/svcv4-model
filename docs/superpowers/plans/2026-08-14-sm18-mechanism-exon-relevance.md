# SM 18 Mechanism & Exon Relevance Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture the SVCv4 SM 18 mechanism × exon-relevance inputs as a new `MechanismExonRelevanceEvidence` model — the first PFD submodule — documenting the multiplier without computing it.

**Architecture:** A new `src/svcv4_model/mechanism.py` module holds three `StrEnum`s (`GenccMechanism`, `ExonRelevance`, `ManeStatus`) and the permissive `MechanismExonRelevanceEvidence` payload (a curation-level PFD evidence entity, `PopulationEvidence` pattern). No Case applicability matrix; `case-model.md` untouched. Docs flip SM 18 from stub to modeled.

**Tech Stack:** Python 3 / Pydantic v2 (`StrEnum`, `ConfigDict(extra="forbid")`), `uv`, pytest, ruff (line-length 100), MkDocs (`strict: true`).

**Spec:** `docs/superpowers/specs/2026-08-14-sm18-mechanism-exon-relevance-design.md`

---

## File Structure

- `src/svcv4_model/mechanism.py` — **new.** `GenccMechanism`, `ExonRelevance`, `ManeStatus`, `MechanismExonRelevanceEvidence`. Single responsibility: the SM 18 evidence payload.
- `src/svcv4_model/__init__.py` — export the four new public names.
- `tests/test_pfd_mechanism.py` — **new.** Round-trip, permissiveness, enum/flag acceptance, package-root import.
- `schemas/json/MechanismExonRelevanceEvidence.schema.json` — **generated** (`scripts/export_schemas.py`); commit.
- `docs/workflows/pfd/index.md` — SM 18 submodule → modeled; soften the top admonition.
- `docs/reference/concepts.md`, `docs/reference/spec-alignment.md`, `docs/reference/known-gaps.md`, `docs/reference/model.md` — docs.

**Conventions (mirror `population.py`):** `from __future__ import annotations`; every field `Field(default=None, ...)`; `ConfigDict(extra="forbid")`; wrap any description that would exceed **100** chars with parenthesized concatenation (ruff E501 + `ruff format --check` run in CI); `StrEnum` members `VALUE = "VALUE"`.

---

## Chunk 1: Model + export + schema regeneration

### Task 1: `MechanismExonRelevanceEvidence` model + export (TDD)

**Files:**
- Create: `src/svcv4_model/mechanism.py`
- Modify: `src/svcv4_model/__init__.py`
- Create: `tests/test_pfd_mechanism.py`

- [ ] **Step 1: Write the failing test.** Create `tests/test_pfd_mechanism.py`:

```python
"""Tests for the SVCv4 PFD Molecular Mechanism & Exon Relevance model (SM 18)."""

from __future__ import annotations

import pytest

from svcv4_model.mechanism import (
    ExonRelevance,
    GenccMechanism,
    ManeStatus,
    MechanismExonRelevanceEvidence,
)


def _maximal() -> MechanismExonRelevanceEvidence:
    return MechanismExonRelevanceEvidence(
        gencc_mechanism=GenccMechanism.ESTABLISHED,
        exon_relevance=ExonRelevance.ALL,
        mane_status=ManeStatus.MANE_SELECT,
        exon_known_irrelevant=False,
        exon_has_established_pathogenic=True,
    )


def test_mechanism_evidence_round_trips_json() -> None:
    original = _maximal()
    rehydrated = MechanismExonRelevanceEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_mechanism_evidence_is_permissive_when_empty() -> None:
    assert MechanismExonRelevanceEvidence().gencc_mechanism is None


def test_mechanism_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MechanismExonRelevanceEvidence(not_a_field=1)


def test_enums_round_trip() -> None:
    for level in GenccMechanism:
        assert MechanismExonRelevanceEvidence(gencc_mechanism=level).gencc_mechanism is level
    for rel in ExonRelevance:
        assert MechanismExonRelevanceEvidence(exon_relevance=rel).exon_relevance is rel
    for mane in ManeStatus:
        assert MechanismExonRelevanceEvidence(mane_status=mane).mane_status is mane


def test_override_flags_accept_booleans() -> None:
    for flag in (True, False):
        ev = MechanismExonRelevanceEvidence(
            exon_known_irrelevant=flag, exon_has_established_pathogenic=flag
        )
        assert ev.exon_known_irrelevant is flag
        assert ev.exon_has_established_pathogenic is flag


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "MechanismExonRelevanceEvidence" in svcv4_model.__all__
```

- [ ] **Step 2: Run to verify failure.**

Run: `uv run pytest tests/test_pfd_mechanism.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'svcv4_model.mechanism'`.

- [ ] **Step 3: Create `src/svcv4_model/mechanism.py`** with exactly the code from spec §5.1 (the three enums, then `MechanismExonRelevanceEvidence`). Reproduce the field descriptions **as wrapped in the spec** (do not re-flatten — they are wrapped to stay ≤100 chars). No imports beyond `from __future__ import annotations`, `from enum import StrEnum`, and `from pydantic import BaseModel, ConfigDict, Field` (this module reuses nothing from `case.py`).

- [ ] **Step 4: Export the four names** in `src/svcv4_model/__init__.py`:
  - Add a new import block **immediately before** `from svcv4_model.method import Method` (module order: `mechanism` sorts *before* `method` — they diverge at char 3, `c` < `t`; ruff isort `I` is enabled, so keep the block alphabetical by module and the names alphabetical inside it — or run `ruff check --fix`):

    ```python
    from svcv4_model.mechanism import (
        ExonRelevance,
        GenccMechanism,
        ManeStatus,
        MechanismExonRelevanceEvidence,
    )
    ```
  - Add to `__all__` (ASCII order): `"ExonRelevance"` before `"Gene"`; `"GenccMechanism"` before `"Gene"`; `"ManeStatus"` and `"MechanismExonRelevanceEvidence"` before `"Method"`. (`__all__` order is not ruff-enforced, but keep it tidy.)

- [ ] **Step 5: Run tests + lint to verify green.**

Run: `uv run pytest tests/test_pfd_mechanism.py -q && uv run ruff check src/svcv4_model/mechanism.py src/svcv4_model/__init__.py tests/test_pfd_mechanism.py && uv run ruff format --check src/svcv4_model/mechanism.py src/svcv4_model/__init__.py tests/test_pfd_mechanism.py`
Expected: tests PASS; ruff reports no errors; "would reformat" nothing. If E501 fires, split a `description` across two parenthesized fragments.

- [ ] **Step 6: Run the full suite** (no schema/model-parity test exists, so nothing else breaks).

Run: `uv run pytest -q`
Expected: PASS.

- [ ] **Step 7: Commit.**

```bash
git add src/svcv4_model/mechanism.py src/svcv4_model/__init__.py tests/test_pfd_mechanism.py
git commit -m "feat: model SM 18 mechanism & exon relevance (first PFD submodule)"
```

### Task 2: Regenerate JSON Schema

**Files:** Create (generated): `schemas/json/MechanismExonRelevanceEvidence.schema.json`

- [ ] **Step 1: Regenerate.**

Run: `uv run python scripts/export_schemas.py`
Expected: output lists the one new file `MechanismExonRelevanceEvidence.schema.json` among those written.

- [ ] **Step 2: Verify only the one new file appears, and nothing else changed.**

Run: `git status --short schemas/json docs/workflows/case-model.md`
Expected: exactly one **new** file — `schemas/json/MechanismExonRelevanceEvidence.schema.json`. `docs/workflows/case-model.md` and all existing `schemas/json/*` (incl. `Case.schema.json`, `case/*`) must be **unchanged**. If anything else changed, stop and investigate.

- [ ] **Step 3: Commit the generated schema.**

```bash
git add schemas/json/MechanismExonRelevanceEvidence.schema.json
git commit -m "chore: generate JSON schema for MechanismExonRelevanceEvidence"
```

- [ ] **Step 4: Confirm the drift gate is clean (exact CI command).**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo CLEAN`
Expected: `CLEAN`.

---

## Chunk 2: Documentation

Pure docs. Verification is `mkdocs build --strict`. External SM link isn't checked by mkdocs — spot check manually.

### Task 3: `pfd/index.md` — SM 18 submodule modeled + soften admonition

**Files:** Modify `docs/workflows/pfd/index.md`

- [ ] **Step 1: Soften the top admonition (lines 15-19).** Replace the flat "PFD is … **not yet covered by this data model** … detailed modeling is a later phase" with a statement that the **first PFD submodule (SM 18 Molecular Mechanism & Exon Relevance) is now modeled** (inputs captured, scoring documented not computed), while the rest of the pipeline (PRD/FXN/INF scaffold, SM 19, SM 20, variant-type workflows) is a later phase.

- [ ] **Step 2: Extend "The shape of the remaining work" (lines 37-46).** Add a subsection for the now-modeled SM 18 submodule: `MechanismExonRelevanceEvidence` captures the two axes (mechanism level, exon-relevance category) + MANE status + the two override flags. Include the multiplier table as *documented, not computed*:

  | GenCC mechanism | ×  | | Exon relevance | × |
  |---|---|---|---|---|
  | Established | 1.0 | | All | 1.0 |
  | Likely | 0.5 | | Most | 0.5 |
  | Suspected | 0.25 | | Few | 0 |
  | Uncertain | 0 | | | |

  Note the **GDV gate** (mechanism usable only at Moderate+ `gene_disease_validity`; Limited-or-below → `UNCERTAIN` → ×0), that the two reductions are not compounded, and link [SM 18](https://docs.google.com/document/d/1BLnsgxLY0TibwylFWz0SeGGeCusWwSokrgU4qsmBiaw/edit). Keep the rest of the pipeline framed as still to come.

- [ ] **Step 3: Verify.** `grep -in "not yet covered by this data model" docs/workflows/pfd/index.md` returns nothing (the flat claim is gone).

### Task 4: `concepts.md` — point the GDV SM 18 paragraph at the new entity

**Files:** Modify `docs/reference/concepts.md`

- [ ] **Step 1:** In the Gene-Disease Validity entry's SM 18 upstream-gate paragraph, update the "the mechanism multiplier itself is not modeled yet … arrives with the PFD workflows" wording to point at the now-modeled `MechanismExonRelevanceEvidence` (the mechanism/exon-relevance *inputs* are modeled; the multiplier itself remains documented-not-computed).

- [ ] **Step 2:** Add a one-line note that `MechanismExonRelevanceEvidence` intentionally has **no** `NOT_ASSESSED` mechanism member (unlike GDV's `NOT_CLASSIFIED`-vs-`None`): SM 18 folds "not assessed" into `UNCERTAIN` (×0), so `None` = not captured vs `UNCERTAIN` = ×0 is a lossless split — the asymmetry is deliberate.

### Task 5: `spec-alignment.md` — SM 18 row → modeled

**Files:** Modify `docs/reference/spec-alignment.md`

- [ ] **Step 1:** Change the SM 18 row (currently "Not yet modeled — but the **gene-disease validity** gate … the mechanism multiplier itself arrives with PFD") to: "**Modeled (inputs)** — `MechanismExonRelevanceEvidence` captures mechanism level + exon relevance + MANE status; the multiplier is documented, not computed. See `[Predictive & Functional Data](../workflows/pfd/index.md)`." Keep the SM 18 Google Doc link on the title.

### Task 6: `known-gaps.md` — note the first PFD submodule landed

**Files:** Modify `docs/reference/known-gaps.md`

- [ ] **Step 1:** Update the "Full PFD modeling" content-gap row: the first PFD submodule (SM 18 Molecular Mechanism & Exon Relevance) is now modeled (`MechanismExonRelevanceEvidence`); what remains is the PRD/FXN/INF scaffold, SM 19 (Informative Variants), SM 20 (Functional Assays), the variant-type workflows, and the multiplier/scoring computation.

### Task 7: `model.md` — render the new class

**Files:** Modify `docs/reference/model.md`

- [ ] **Step 1:** After the `::: svcv4_model.PopulationEvidence` entry (the last one), add a `---` separator and `::: svcv4_model.MechanismExonRelevanceEvidence`.

### Task 8: Build + commit docs

- [ ] **Step 1: Build strict.**

Run: `uv run mkdocs build --strict`
Expected: no warnings/errors. Fix any broken internal link (don't disable strict). If the plan doc itself trips a relative-link warning, wrap the offending `[text](../path)` example in backticks.

- [ ] **Step 2: Manual external-link spot check.** Open the SM 18 link once to confirm it resolves.

- [ ] **Step 3: Commit.**

```bash
git add docs/workflows/pfd/index.md docs/reference/concepts.md docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: model SM 18 mechanism & exon relevance (first PFD submodule)"
```

---

## Done criteria

- `uv run pytest -q` green (new `tests/test_pfd_mechanism.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean.
- `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md` → clean (one new schema file committed).
- `uv run mkdocs build --strict` passes.
- `grep -in "not yet covered by this data model" docs/workflows/pfd/index.md` → nothing.
- No multiplier-computation code added (scope boundary respected).
