# PFD Scaffold (`PfdCodeAssessment`) Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a variant-agnostic PFD scaffold — `PfdCodeAssessment` — that composes the three shipped PFD submodules (SM 18/19/20) plus a generic `PfdPredictiveEvidence` step and a `PfdParentCode` enum into one per-parent-code evidence payload, capture-only.

**Architecture:** One new standalone module `src/svcv4_model/pfd.py` following the `population.py` / `case_control.py` precedent — permissive all-optional Pydantic models, `ConfigDict(extra="forbid")`, `from __future__ import annotations`. `PfdCodeAssessment` *embeds* the three already-exported submodule models as optional fields (no ids, no cross-refs). It is **not** part of `Case`, gets **no** `Workflow` enum entry and **no** applicability-matrix row, so `case-model.md` and the per-workflow case views are untouched. Two new BaseModels → two new committed JSON schemas; the StrEnum gets none. Scoring is documented in prose, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv` for env/scripts, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-16-pfd-scaffold-design.md` (committed on this branch, `58b1449`).

**Branch:** `feat/pfd-scaffold-missense` (already checked out; spec already committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/pfd.py` | The scaffold: `PfdParentCode`, `PfdPredictiveEvidence`, `PfdCodeAssessment` | Create |
| `src/svcv4_model/__init__.py` | Export the three new public names (imports + `__all__`) | Modify |
| `tests/test_pfd.py` | Unit tests for the scaffold (round-trip, permissive-empty, extra-forbid, enum, importable) | Create |
| `schemas/json/PfdCodeAssessment.schema.json` | Generated schema (embeds the submodules + enum as `$defs`) | Generate + `git add` |
| `schemas/json/PfdPredictiveEvidence.schema.json` | Generated schema | Generate + `git add` |
| `docs/workflows/pfd/index.md` | Add the scaffold section; flip the two now-stale "still to come" notes | Modify |
| `docs/reference/known-gaps.md` | Update the "Full PFD modeling" row (scaffold now done) | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.PfdCodeAssessment` after the last entry | Modify |

**Note on the existing `tests/test_pfd_*.py` files:** there are already `test_pfd_functional.py`, `test_pfd_informative.py`, `test_pfd_mechanism.py`. The new file is `tests/test_pfd.py` (no name clash) — do **not** touch the existing three.

---

## Chunk 1: PFD scaffold module, exports, schemas, docs

### Task 1: Create the `pfd.py` module (TDD)

**Files:**
- Create: `src/svcv4_model/pfd.py`
- Create: `tests/test_pfd.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_pfd.py` with the full test suite. It imports from `svcv4_model.pfd` (the module doesn't exist yet, so collection fails):

```python
"""Tests for the SVCv4 PFD scaffold (PfdCodeAssessment)."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import InformativeVariant, InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import (
    PfdCodeAssessment,
    PfdParentCode,
    PfdPredictiveEvidence,
)


def _maximal_assessment() -> PfdCodeAssessment:
    return PfdCodeAssessment(
        parent_code=PfdParentCode.MIS,
        predictive=PfdPredictiveEvidence(
            predictor="REVEL",
            raw_score=0.92,
            initial_points=4.0,
            path_label="GREEN",
            transcript_relevance_applied=True,
            mechanism_applied=False,
            adjusted_points=4.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(variants=[InformativeVariant()]),
        prd_points=4.0,
        spa_points=0.0,
        fxn_points=2.0,
        inf_points=1.0,
        parent_total=7.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = PfdCodeAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = PfdCodeAssessment()
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        PfdCodeAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        PfdPredictiveEvidence(not_a_field=1)


def test_parent_code_values_round_trip() -> None:
    for code in PfdParentCode:
        assert PfdCodeAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "PfdCodeAssessment" in svcv4_model.__all__
    assert "PfdParentCode" in svcv4_model.__all__
    assert "PfdPredictiveEvidence" in svcv4_model.__all__
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_pfd.py -q`
Expected: collection/import **ERROR** — `ModuleNotFoundError: No module named 'svcv4_model.pfd'`.

- [ ] **Step 3: Create the module**

Create `src/svcv4_model/pfd.py` with exactly this content (reproduced from spec §5.1; longest field description is 99 chars — under the 100 limit):

```python
"""SVCv4 PFD scaffold — the shared, variant-agnostic assessment structure.

Every PFD variant-type workflow (missense, nonsense, splice, …) produces a
parent-code score from the same pipeline: predictive (PRD) → adjust by molecular
mechanism / exon relevance (SM 18) → functional (SM 20) → informative (SM 19) →
parent-code total, with a splice-only splice-assay (SPA) step. This module
captures one parent code's assessment, embedding the three shared submodules;
the scoring (see docs/workflows/pfd/index.md) is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence


class PfdParentCode(StrEnum):
    """The PFD parent evidence code a variant-type workflow resolves to (SM 1)."""

    NUL = "NUL"
    CDS = "CDS"
    SPL = "SPL"
    MIS = "MIS"
    NCG = "NCG"
    REG = "REG"


class PfdPredictiveEvidence(BaseModel):
    """The predictive (PRD) step of a PFD assessment.

    Variant-type-agnostic shape: an in-silico prediction, its SM 18 transcript-
    relevance / mechanism adjustment, and the resulting coded ``_PRD`` value.
    Typed predictor/path enums arrive with the per-variant-type workflows.
    """

    model_config = ConfigDict(extra="forbid")

    predictor: str | None = Field(
        default=None, description="In-silico predictor or basis used (e.g. REVEL, NMD prediction)."
    )
    raw_score: float | None = Field(
        default=None, description="The predictor's raw score, if applicable."
    )
    initial_points: float | None = Field(
        default=None, description="Initial evidence points before the SM 18 adjustment."
    )
    path_label: str | None = Field(
        default=None, description="Flow-diagram path/color (e.g. GREEN, YELLOW); typed later."
    )
    transcript_relevance_applied: bool | None = Field(
        default=None,
        description="Whether the SM 18 transcript-relevance step reduced the points.",
    )
    mechanism_applied: bool | None = Field(
        default=None,
        description=(
            "Whether the SM 18 mechanism step applied (not for the missense "
            "amino-acid path, where predictors capture both LoF and GoF)."
        ),
    )
    adjusted_points: float | None = Field(
        default=None,
        description="Coded _PRD points after the SM 18 adjustment.",
    )


class PfdCodeAssessment(BaseModel):
    """One PFD parent-code assessment: the shared pipeline's captured inputs.

    Embeds the three shared submodules (SM 18/19/20) and captures the coded
    sub-code point values and the parent total. Permissive superset; the scoring
    (the pipeline, its caps, the held separate+combined values, the _ND coding)
    is documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    parent_code: PfdParentCode | None = Field(
        default=None, description="The parent evidence code this assessment resolves to."
    )
    predictive: PfdPredictiveEvidence | None = Field(
        default=None, description="The predictive (_PRD) step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded _PRD point value.")
    spa_points: float | None = Field(
        default=None, description="Coded _SPA (splice-assay) point value; splice paths only."
    )
    fxn_points: float | None = Field(default=None, description="Coded _FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded _INF point value.")
    parent_total: float | None = Field(
        default=None, description="Capped parent-code total for this assessment."
    )
```

- [ ] **Step 4: Run ruff format + check on the new module**

Run: `uv run ruff format src/svcv4_model/pfd.py tests/test_pfd.py && uv run ruff check src/svcv4_model/pfd.py tests/test_pfd.py`
Expected: `ruff format` reports files left unchanged (or reformats trivially — accept its output as canonical); `ruff check` clean. If check reports an unused import in the test (e.g. an embedded submodule imported but not used), remove that import.

- [ ] **Step 5: Run the tests — expect failure on import of package root, NOT on `svcv4_model.pfd`**

Run: `uv run pytest tests/test_pfd.py -q`
Expected: `test_importable_from_package_root` **FAILS** (the names aren't in `svcv4_model.__all__` yet); the other tests **PASS** (they import straight from `svcv4_model.pfd`). This confirms the module is correct and isolates the remaining work to the export step.

- [ ] **Step 6: Commit the module + tests**

```bash
git add src/svcv4_model/pfd.py tests/test_pfd.py
git commit -m "feat: add PFD scaffold module (PfdCodeAssessment)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Export the three names from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Add the import block**

In `src/svcv4_model/__init__.py`, add a new import block. It goes **after** the `from svcv4_model.method import Method` line and **before** the `from svcv4_model.population import (` block (module order: `mechanism` < `method` < `pfd` < `population`):

```python
from svcv4_model.pfd import (
    PfdCodeAssessment,
    PfdParentCode,
    PfdPredictiveEvidence,
)
```

- [ ] **Step 2: Add the three names to `__all__`, in sorted position**

`__all__` is kept alphabetically sorted **by hand** — ruff does **not** sort it in this repo (`RUF022` is not enabled; isort's `I` sorts imports only). Insert the three strings in the correct place: **between `"MolecularMechanism"` and `"Phase"`** (`"Pfd…"` < `"Pha…"` because `f` < `h`, so the block sorts *before* the `Phase`/`Pheno` entries, not after):

```python
    "MolecularMechanism",
    "PfdCodeAssessment",
    "PfdParentCode",
    "PfdPredictiveEvidence",
    "Phase",
```

- [ ] **Step 3: Let ruff sort the import block and verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: the *import block* is sorted by isort (the `__all__` list is already correct from Step 2); `ruff check` and `format --check` clean (exit 0). Note: `ruff check --fix` will **not** reorder `__all__`, so the manual placement in Step 2 must already be correct.

- [ ] **Step 4: Run the full PFD test file — all green now**

Run: `uv run pytest tests/test_pfd.py -q`
Expected: **all tests PASS**, including `test_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export PFD scaffold from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Regenerate and commit the JSON schemas

**Files:**
- Generate: `schemas/json/PfdCodeAssessment.schema.json`
- Generate: `schemas/json/PfdPredictiveEvidence.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: two **new** files appear — `schemas/json/PfdCodeAssessment.schema.json` and `schemas/json/PfdPredictiveEvidence.schema.json`. Existing schema files (including the three embedded submodules' own files) are unchanged.

- [ ] **Step 2: Sanity-check the generated `PfdCodeAssessment` schema**

Run: `uv run python -c "import json; d=json.load(open('schemas/json/PfdCodeAssessment.schema.json')); print(sorted(d.get('\$defs', {}).keys()))"`
Expected: the `$defs` include `PfdParentCode`, `PfdPredictiveEvidence`, and the embedded submodule models (e.g. `MechanismExonRelevanceEvidence`, `FunctionalAssayEvidence`, `InformativeVariantsEvidence`, and their own nested `$defs`). Confirms embedding-by-`$ref` worked and the enum is a `$def` (not inlined).

- [ ] **Step 3: Confirm `git status` shows exactly two new untracked files**

Run: `git status --porcelain schemas/json`
Expected: two lines, both `??` (untracked), for the two new files only. **No modifications** to any existing schema. If any existing schema shows as modified, stop — something drifted; investigate before continuing.

- [ ] **Step 4: Verify the case-views drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`. `git diff --quiet` ignores untracked files, so the two new (untracked) schemas do not trip it; `case-model.md` is unchanged (PFD adds no `Workflow` entry).

- [ ] **Step 5: `git add` the two new schemas (load-bearing) and commit**

```bash
git add schemas/json/PfdCodeAssessment.schema.json schemas/json/PfdPredictiveEvidence.schema.json
git commit -m "chore: generate PFD scaffold JSON schemas

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Documentation

**Files:**
- Modify: `docs/workflows/pfd/index.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`

- [ ] **Step 1: Add the scaffold section to `pfd/index.md`**

After the `### Functional Assays ✅ modeled (inputs)` subsection (which currently ends at the "…not modeled here." paragraph, before the final "**All three shared sub-modules are now modeled**…" paragraph), insert this new subsection:

```markdown
### PFD scaffold ✅ modeled (inputs)

The shared, variant-agnostic scaffold is modeled as `PfdCodeAssessment`. It ties
one **parent code**'s pipeline together: a `predictive` (`_PRD`) step
(`PfdPredictiveEvidence`), the three embedded shared submodules
(`mechanism_exon_relevance` / `functional` / `informative`, SM 18/19/20), the
coded sub-code point values (`prd_points` / `spa_points` / `fxn_points` /
`inf_points`), and the capped `parent_total`. The `parent_code` is one of
`NUL` / `CDS` / `SPL` / `MIS` (plus `NCG` / `REG`) — `PfdParentCode`.

The pipeline is **documented here, not computed**: `_PRD` (in-silico prediction)
→ adjusted by the [Molecular Mechanism & Exon Relevance](#molecular-mechanism-exon-relevance-modeled-inputs)
matrix (SM 18) → for splice paths, an `_SPA` (splice-assay) step → `_FXN`
(functional) → `_INF` (informative) → the capped parent-code total. Each sub-code
and intermediate has its own cap (SM 6 gives `MIS_` −8.0 to +9.0 and `SPL_` −8.0
to +10.0). Following SM 6, the model records **both** the separate coded sub-code
values and the parent total; the *combined-held* intermediates (e.g. PRD+FXN,
which has no distinct evidence code) and the `_ND` (No Data) coding for an absent
step are captured through the same optional fields. The typed predictor/path
enums and the dual missense **MIS_ / SPL_** path (evaluate both, apply the
higher) arrive with the per-variant-type workflows.
```

- [ ] **Step 2: Update the top admonition in `pfd/index.md`**

Replace the `!!! note "Modeling underway — first submodule landed"` admonition (lines ~15–22) so it no longer lists the scaffold as pending. New version:

```markdown
!!! note "Modeling underway — shared submodules + scaffold landed"

    The **three shared PFD submodules** — Molecular Mechanism & Exon Relevance
    (SM 18), Informative Variants (SM 19), Functional Assays (SM 20) — and the
    **variant-agnostic scaffold** (`PfdCodeAssessment`) that composes them are now
    modeled (inputs captured, scoring documented not computed); see
    [below](#the-shape-of-the-remaining-work). What remains is the per-variant-type
    workflows (Missense first) and Critical Amino Acids (SM 7). This page
    summarizes the concepts and tracks what has landed.
```

- [ ] **Step 3: Update the closing paragraph in `pfd/index.md`**

Replace the final paragraph (currently: "**All three shared sub-modules are now modeled** (inputs). The remaining PFD work — Determining Critical Amino Acids (SM 7), the PRD/FXN/INF scaffold and parent codes, and the per-variant-type workflows — is still to come.") with:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). The
remaining PFD work — Determining Critical Amino Acids (SM 7) and the
per-variant-type workflows (Missense first, with its typed predictors and dual
MIS_/SPL_ path) — is still to come.
```

- [ ] **Step 4: Update the "Full PFD modeling" row in `known-gaps.md`**

Replace the `| Full PFD modeling | PFD | … |` row (line ~26) with:

```markdown
| Full PFD modeling | PFD | The **three shared sub-modules** (SM 18 `MechanismExonRelevanceEvidence`, SM 19 `InformativeVariantsEvidence`, SM 20 `FunctionalAssayEvidence`) and the **variant-agnostic scaffold** (`PfdCodeAssessment` — parent codes NUL/CDS/SPL/MIS, the PRD step, embedded submodules, sub-code point captures) are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the per-variant-type workflows (Missense first — typed predictors, dual MIS_/SPL_ path); the path-specific combined-held / `SPL_SPA` structuring; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

- [ ] **Step 5: Append the model.md entry**

In `docs/reference/model.md`, after the **last** `::: svcv4_model.CaseControlStudyEvidence` entry (the current final entry), append:

```markdown

---

::: svcv4_model.PfdCodeAssessment
```

(Only `PfdCodeAssessment` is documented here — it transitively renders `PfdPredictiveEvidence` and the embedded submodules. Do not add a separate entry for the enum or the predictive sub-model.)

- [ ] **Step 6: Build the docs strictly**

Run: `uv run mkdocs build --strict 2>&1 | tail -20`
Expected: `INFO - Documentation built…` with **no** WARNING lines. If strict trips on a same-page anchor, verify the `#molecular-mechanism-exon-relevance-modeled-inputs` fragment against the built HTML slug (emoji/`&` collapse to a single hyphen); note strict does **not** validate same-page fragments, so the likely culprit is a broken *relative* link or a missing file — read the warning and fix it.

- [ ] **Step 7: Commit the docs**

```bash
git add docs/workflows/pfd/index.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: document the PFD scaffold (PfdCodeAssessment)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Full quality gates

**Files:** none (verification only)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -q`
Expected: all tests pass (the new `tests/test_pfd.py` plus the existing suite).

- [ ] **Step 2: Lint + format**

Run: `uv run ruff check && uv run ruff format --check .`
Expected: both clean (exit 0).

- [ ] **Step 3: Schema/case-view drift gate**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN` (schemas already committed → no diff; `case-model.md` unaffected).

- [ ] **Step 4: Strict docs build**

Run: `uv run mkdocs build --strict 2>&1 | tail -5`
Expected: built with no warnings.

- [ ] **Step 5: Confirm a clean tree**

Run: `git status --porcelain`
Expected: empty (everything committed). If the schema regen in Step 3 left the two schema files modified, something is nondeterministic — investigate; otherwise the tree is clean.

---

## Definition of done

- `PfdCodeAssessment`, `PfdPredictiveEvidence`, `PfdParentCode` importable from `svcv4_model`, all-optional, `extra="forbid"`.
- Two new committed JSON schemas; no existing schema changed; `case-model.md` untouched.
- `pfd/index.md` has the scaffold section and no longer lists the scaffold as pending; `known-gaps.md` and `model.md` updated.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR for the increment, run the `code-review` skill on the diff, address findings, then merge on request. The **Missense** workflow (typed 7-predictor enum, color-path enum, dual MIS_/SPL_ "take the higher" path, missense `_INF` Grantham categories) is the next increment on a follow-on branch.
