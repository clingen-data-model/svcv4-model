# SM 20 Functional Assays Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture the SVCv4 SM 20 functional-assay inputs as a new `FunctionalAssayEvidence` model — the third and last PFD shared submodule — documenting the scoring without computing it.

**Architecture:** A new `src/svcv4_model/functional.py` module holds four `StrEnum`s, two focused sub-models (`ProteinFunctionalAssay`, `AnimalModelEvidence`), and the `FunctionalAssayEvidence` payload (a curation-level PFD entity, `InformativeVariantsEvidence` pattern) with two `list[...]` fields + a shared `disease_mechanism`. No Case applicability matrix; `case-model.md` untouched. Docs mark SM 20 modeled — completing all three PFD shared submodules.

**Tech Stack:** Python 3 / Pydantic v2 (`StrEnum`, `ConfigDict(extra="forbid")`), `uv`, pytest, ruff (line-length 100), MkDocs (`strict: true`).

**Spec:** `docs/superpowers/specs/2026-08-15-sm20-functional-assays-design.md`

---

## File Structure

- `src/svcv4_model/functional.py` — **new.** 4 enums + `ProteinFunctionalAssay`, `AnimalModelEvidence`, `FunctionalAssayEvidence`. Single responsibility: the SM 20 evidence payload.
- `src/svcv4_model/__init__.py` — export the seven new public names.
- `tests/test_pfd_functional.py` — **new.** Round-trip, permissiveness, enum acceptance, package-root import.
- `schemas/json/FunctionalAssayEvidence.schema.json`, `ProteinFunctionalAssay.schema.json`, `AnimalModelEvidence.schema.json` — **generated**; commit.
- `docs/workflows/pfd/index.md`, `docs/reference/spec-alignment.md`, `docs/reference/known-gaps.md`, `docs/reference/model.md` — docs.

**Conventions (mirror `informative.py`):** `from __future__ import annotations`; every field `Field(default=None, ...)` (list fields use `Field(default_factory=list, ...)`); `ConfigDict(extra="forbid")`; **run `uv run ruff format` after writing the module** — do not hand-tune wrapping.

---

## Chunk 1: Model + export + schema regeneration

### Task 1: `FunctionalAssayEvidence` model + export (TDD)

**Files:**
- Create: `src/svcv4_model/functional.py`
- Modify: `src/svcv4_model/__init__.py`
- Create: `tests/test_pfd_functional.py`

- [ ] **Step 1: Write the failing test.** Create `tests/test_pfd_functional.py`:

```python
"""Tests for the SVCv4 PFD Functional Assay Evidence model (SM 20)."""

from __future__ import annotations

import pytest

from svcv4_model.functional import (
    AnimalModelEvidence,
    AnimalModelType,
    FunctionalAssayEvidence,
    MolecularMechanism,
    PhenotypeReplication,
    ProteinAssayType,
    ProteinFunctionalAssay,
)


def _maximal_protein() -> ProteinFunctionalAssay:
    return ProteinFunctionalAssay(
        assay_type=ProteinAssayType.ENZYME_KINETIC,
        odds_path=8.42,
        has_pathogenic_controls=True,
        has_benign_controls=True,
        pathogenic_control_count=11,
        benign_control_count=10,
        has_false_positives_or_negatives=False,
        fidelity_to_mechanism=True,
    )


def _maximal_animal() -> AnimalModelEvidence:
    return AnimalModelEvidence(
        model_type=AnimalModelType.ENGINEERED,
        species="mouse",
        ortholog_established=True,
        phenotype_replication=PhenotypeReplication.SPECIFIC,
        inheritance_match=True,
        local_sequence_similarity_high=True,
        fidelity_to_mechanism=True,
    )


def _maximal() -> FunctionalAssayEvidence:
    return FunctionalAssayEvidence(
        disease_mechanism=MolecularMechanism.LOSS_OF_FUNCTION,
        protein_assays=[_maximal_protein()],
        animal_models=[_maximal_animal()],
    )


def test_evidence_round_trips_json() -> None:
    original = _maximal()
    rehydrated = FunctionalAssayEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_evidence_is_permissive_when_empty() -> None:
    ev = FunctionalAssayEvidence()
    assert ev.protein_assays == []
    assert ev.animal_models == []


def test_all_three_models_forbid_extra() -> None:
    for model in (FunctionalAssayEvidence, ProteinFunctionalAssay, AnimalModelEvidence):
        with pytest.raises(ValueError):
            model(not_a_field=1)


def test_mechanism_values_round_trip() -> None:
    for mech in MolecularMechanism:
        assert FunctionalAssayEvidence(disease_mechanism=mech).disease_mechanism is mech


def test_protein_enums_round_trip() -> None:
    for at in ProteinAssayType:
        assert ProteinFunctionalAssay(assay_type=at).assay_type is at


def test_animal_enums_round_trip() -> None:
    for mt in AnimalModelType:
        assert AnimalModelEvidence(model_type=mt).model_type is mt
    for pr in PhenotypeReplication:
        assert AnimalModelEvidence(phenotype_replication=pr).phenotype_replication is pr


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "FunctionalAssayEvidence" in svcv4_model.__all__
```

- [ ] **Step 2: Run to verify failure.**

Run: `uv run pytest tests/test_pfd_functional.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'svcv4_model.functional'`.

- [ ] **Step 3: Create `src/svcv4_model/functional.py`** with the code from spec §5.1 (the four enums, `ProteinFunctionalAssay`, `AnimalModelEvidence`, then `FunctionalAssayEvidence`). Imports only: `from __future__ import annotations`, `from enum import StrEnum`, `from pydantic import BaseModel, ConfigDict, Field`.

- [ ] **Step 4: Normalize formatting.**

Run: `uv run ruff format src/svcv4_model/functional.py`
(the spec's field-description wrapping is illustrative; let ruff pick the canonical form so `ruff format --check` passes later.)

- [ ] **Step 5: Export the seven names** in `src/svcv4_model/__init__.py`:
  - Add a new import block **after `from svcv4_model.evidence_line import EvidenceLine` and before `from svcv4_model.informative import (...)`** (`functional` < `informative`; ruff isort `I` is enabled — keep alphabetical or run `uv run ruff check --fix src/svcv4_model/__init__.py`):

    ```python
    from svcv4_model.functional import (
        AnimalModelEvidence,
        AnimalModelType,
        FunctionalAssayEvidence,
        MolecularMechanism,
        PhenotypeReplication,
        ProteinAssayType,
        ProteinFunctionalAssay,
    )
    ```
  - Add all seven names to `__all__` in ASCII order (`AnimalModelEvidence`/`AnimalModelType` in the `A…` block; `FunctionalAssayEvidence` after `ExonRelevance`/before `GenccMechanism`; `MolecularMechanism` after `Method`/before `Phase` (case-sensitive ASCII: `Method` < `MolecularMechanism`); `PhenotypeReplication` and `ProteinAssayType`/`ProteinFunctionalAssay` in the `P…` block). If unsure, run `uv run ruff check --fix` (note: `__all__` order isn't ruff-enforced, but keep it tidy).

- [ ] **Step 6: Run tests + lint to verify green.**

Run: `uv run pytest tests/test_pfd_functional.py -q && uv run ruff check src/svcv4_model/functional.py src/svcv4_model/__init__.py tests/test_pfd_functional.py && uv run ruff format --check src/svcv4_model/functional.py src/svcv4_model/__init__.py tests/test_pfd_functional.py`
Expected: tests PASS; ruff reports no errors; "would reformat" nothing. If I001 fires on the import, run `ruff check --fix`; if E501 fires on a test line, split it.

- [ ] **Step 7: Run the full suite.**

Run: `uv run pytest -q`
Expected: PASS.

- [ ] **Step 8: Commit.**

```bash
git add src/svcv4_model/functional.py src/svcv4_model/__init__.py tests/test_pfd_functional.py
git commit -m "feat: model SM 20 functional assays (third PFD submodule)"
```

### Task 2: Regenerate JSON Schemas

**Files:** Create (generated): three `schemas/json/*.schema.json`

- [ ] **Step 1: Regenerate.**

Run: `uv run python scripts/export_schemas.py`
Expected: output lists the three new files among those written.

- [ ] **Step 2: Verify only the three new files appear, nothing else changed.**

Run: `git status --short schemas/json docs/workflows/case-model.md`
Expected: exactly three **new** files — `FunctionalAssayEvidence.schema.json`, `ProteinFunctionalAssay.schema.json`, `AnimalModelEvidence.schema.json`. `docs/workflows/case-model.md` and all existing `schemas/json/*` (incl. `Case.schema.json`, `case/*`) must be **unchanged**. If anything else changed, stop and investigate.

- [ ] **Step 3: Commit the generated schemas.**

```bash
git add schemas/json/FunctionalAssayEvidence.schema.json schemas/json/ProteinFunctionalAssay.schema.json schemas/json/AnimalModelEvidence.schema.json
git commit -m "chore: generate JSON schemas for FunctionalAssayEvidence"
```

- [ ] **Step 4: Confirm the drift gate (exact CI command).**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo CLEAN`
Expected: `CLEAN`.

---

## Chunk 2: Documentation

Pure docs. Verification is `mkdocs build --strict`. External SM link isn't checked by mkdocs — spot check manually.

### Task 3: `pfd/index.md` — add the modeled Functional Assays subsection

**Files:** Modify `docs/workflows/pfd/index.md`

- [ ] **Step 1: Add a new subsection** after the "### Informative Variants ✅ modeled (inputs)" block (which ends just before the "The remaining shared sub-modules …" sentence). Title it `### Functional Assays ✅ modeled (inputs)`. Content: the third shared sub-module is modeled as `FunctionalAssayEvidence`, holding two lists — `protein_assays` (`ProteinFunctionalAssay`: `assay_type`, `odds_path`, `has_pathogenic_controls`/`has_benign_controls` + counts, `has_false_positives_or_negatives`, `fidelity_to_mechanism`) and `animal_models` (`AnimalModelEvidence`: `model_type`, `species`, `ortholog_established`, `phenotype_replication`, `inheritance_match`, `local_sequence_similarity_high`, `fidelity_to_mechanism`) — plus a shared `disease_mechanism`. Document, **not computed**: protein assays are calibrated by an **OddsPath** requiring **both** pathogenic and benign controls (small no-FP/FN experiments use lookup Tables 1/2; FP/FN, trichotomized, or MAVE → expert math, out of scope); animal-model evidence ranges **`_FXN_0.0` to `+4.0`** per Table 3. Note the **fidelity gate** (an assay that doesn't faithfully recapitulate the disease mechanism scores `FXN_0.0`), the multiple-assay **combination rules** (same readout+direction → strongest only; opposite → sum; distinct functions → most disease-relevant), that `*_FXN` **adds to** `*_PRD`, and the **splice-assay carve-out** (RNA assays are `SPL_SPA`, not `_FXN`). Link [SM 20](https://docs.google.com/document/d/1X68otBl4YvdXlP1bOD83JO4kIod0Ol5BoLB4CLxqijA/edit).
  - **Anchor caution:** if you add any intra-page link to this or the sibling subsections, use single hyphens (mkdocs collapses `&`/emoji/`()` to single hyphens) and verify against the built HTML `id=` (mkdocs `--strict` does NOT validate same-page fragments).

- [ ] **Step 2: Update the "remaining shared sub-modules" sentence** (currently "The remaining shared sub-modules (Functional Assays, Determining Critical Amino Acids), …") to leave only **Determining Critical Amino Acids** and add that **all three shared sub-modules are now modeled**; the remaining PFD work is SM 7, the PRD/FXN/INF scaffold + parent codes, and the per-variant-type workflows.

- [ ] **Step 3: Verify.** `grep -n "Functional Assays ✅ modeled" docs/workflows/pfd/index.md` matches; `grep -n "remaining shared sub-modules (Functional Assays" docs/workflows/pfd/index.md` returns nothing.

### Task 4: `spec-alignment.md` — SM 20 row → modeled

**Files:** Modify `docs/reference/spec-alignment.md`

- [ ] **Step 1:** Change the SM 20 row (currently `(shared sub-module) | Not yet modeled`) to: "**Modeled (inputs)** — `FunctionalAssayEvidence` captures protein/cellular assays (OddsPath, pathogenic + benign controls) and animal-model evidence; the scoring is documented, not computed. See `[Predictive & Functional Data](../workflows/pfd/index.md)`." Keep the SM 20 Google Doc link on the title. (When editing the real doc, drop the backticks around the link — they are here only so this plan passes `mkdocs --strict`.)

### Task 5: `known-gaps.md` — all three submodules landed

**Files:** Modify `docs/reference/known-gaps.md`

- [ ] **Step 1:** Update the "Full PFD modeling" content-gap row: **all three shared sub-modules (SM 18/19/20) are now modeled** (inputs); what remains is SM 7 (Critical Amino Acids), the PRD/FXN/INF scaffold + parent codes (NUL/CDS/SPL/MIS), the per-variant-type workflows, and the scoring computation.

### Task 6: `model.md` — render the new class

**Files:** Modify `docs/reference/model.md`

- [ ] **Step 1:** After the `::: svcv4_model.InformativeVariantsEvidence` entry (the last one), add a `---` separator and `::: svcv4_model.FunctionalAssayEvidence`.

### Task 7: Build + commit docs

- [ ] **Step 1: Build strict.**

Run: `uv run mkdocs build --strict`
Expected: no warnings/errors. Fix any broken internal link (don't disable strict). If the plan doc itself trips a relative-link warning, wrap the offending `[text](../path)` example in backticks.

- [ ] **Step 2: Manual external-link spot check.** Open the SM 20 link once to confirm it resolves.

- [ ] **Step 3: Commit.**

```bash
git add docs/workflows/pfd/index.md docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: model SM 20 functional assays (third PFD submodule)"
```

---

## Done criteria

- `uv run pytest -q` green (new `tests/test_pfd_functional.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean.
- `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md` → clean (three new schema files committed).
- `uv run mkdocs build --strict` passes.
- `grep -n "remaining shared sub-modules (Functional Assays" docs/workflows/pfd/index.md` → nothing.
- No scoring-computation code added (scope boundary respected).
