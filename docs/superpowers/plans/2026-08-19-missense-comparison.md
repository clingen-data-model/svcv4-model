# Missense `MIS_`/`SPL_` Comparison Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the final step of the SVCv4 Missense workflow (SM 6) — increment 2c — by extending `missense.py` with a `MissenseAssessment` umbrella entity that embeds both path assessments plus the selected path and applied total, completing the Missense workflow.

**Architecture:** Extend the existing `src/svcv4_model/missense.py` (the whole Missense workflow lives in one module). Add a `MissenseSelectedPath` StrEnum and a `MissenseAssessment` model that composes the two already-shipped assessments (`MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`) as optional fields — satisfying SM 6's "save both pathways" — plus `selected_path` and `applied_total`. Permissive all-optional, `ConfigDict(extra="forbid")`. Standalone PFD payload — no `Case`, no `Workflow` enum entry, no applicability-matrix row, so `case-model.md` and the per-workflow case views are untouched. One new committed JSON schema; the StrEnum gets none. The "take the higher" rule is documented in prose, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv`, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-19-missense-comparison-design.md` (committed on this branch).

**Branch:** `feat/pfd-missense-compare` (checked out; spec committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/missense.py` | Add `MissenseSelectedPath` enum + `MissenseAssessment` model | Modify |
| `src/svcv4_model/__init__.py` | Export the two new public names | Modify |
| `tests/test_missense.py` | Add comparison tests (round-trip, permissive-empty, extra-forbid, enum, importable) | Modify |
| `schemas/json/MissenseAssessment.schema.json` | Generated (embeds both assessments + enum as `$defs`) | Generate + `git add` |
| `docs/workflows/pfd/missense.md` | Add the comparison section; flip the admonition to "complete" | Modify |
| `docs/reference/spec-alignment.md` | SM 6 row → fully modeled | Modify |
| `docs/reference/known-gaps.md` | "Full PFD modeling" row → Missense complete | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.MissenseAssessment` | Modify |

**Note:** the model uses no new imports — `missense.py` already imports `StrEnum`, `BaseModel`, `ConfigDict`, `Field`, and both embedded classes are defined in the same module.

---

## Chunk 1: Missense comparison model, exports, schema, docs

### Task 1: Extend `missense.py` with the comparison model (TDD)

**Files:**
- Modify: `src/svcv4_model/missense.py`
- Modify: `tests/test_missense.py`

- [ ] **Step 1: Add the failing comparison tests**

Append to `tests/test_missense.py`. First widen the `from svcv4_model.missense import (...)` block to add the two new names (`MissenseAssessment`, `MissenseSelectedPath`); those don't exist yet → collection fails. Add them in sorted position in the import block:

```python
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
    MissenseSelectedPath,
    MissenseSpliceAssessment,
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)
```

Append these test functions at the end of the file (they reuse the existing `_maximal_assessment()` and `_maximal_splice_assessment()` helpers):

```python
def _maximal_missense_assessment() -> MissenseAssessment:
    return MissenseAssessment(
        amino_acid=_maximal_assessment(),
        splice=_maximal_splice_assessment(),
        selected_path=MissenseSelectedPath.AMINO_ACID,
        applied_total=8.0,
    )


def test_missense_assessment_round_trips_json() -> None:
    original = _maximal_missense_assessment()
    rehydrated = MissenseAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_missense_assessment_is_permissive_when_empty() -> None:
    empty = MissenseAssessment()
    assert empty.amino_acid is None
    assert empty.splice is None
    assert empty.selected_path is None
    assert empty.applied_total is None


def test_missense_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseAssessment(not_a_field=1)


def test_selected_path_values_round_trip() -> None:
    for path in MissenseSelectedPath:
        assert MissenseAssessment(selected_path=path).selected_path is path


def test_missense_assessment_importable_from_package_root() -> None:
    import svcv4_model

    for name in ("MissenseAssessment", "MissenseSelectedPath"):
        assert name in svcv4_model.__all__
```

- [ ] **Step 2: Run the comparison tests to verify they fail**

Run: `uv run pytest tests/test_missense.py -q 2>&1 | tail -5`
Expected: collection **ERROR** — `ImportError: cannot import name 'MissenseAssessment' from 'svcv4_model.missense'`.

- [ ] **Step 3: Append the enum and model to `missense.py`**

At the **end** of `src/svcv4_model/missense.py`, append (from spec §5.1; longest line is 97 chars, under the 100 limit; no new imports needed):

```python
class MissenseSelectedPath(StrEnum):
    """Which missense path was applied to the VBC after the comparison (SM 6)."""

    AMINO_ACID = "AMINO_ACID"
    SPLICE = "SPLICE"


class MissenseAssessment(BaseModel):
    """The overall missense workflow assessment (SM 6).

    Holds both the amino-acid (MIS_) and splice (SPL_) path assessments — SM 6
    requires saving both — plus which path was applied and the final applied
    total. The comparison rule (splice-negative → amino-acid; else the higher;
    ties → amino-acid) is documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    amino_acid: MissenseAminoAcidAssessment | None = Field(
        default=None, description="The amino-acid (MIS_) path assessment."
    )
    splice: MissenseSpliceAssessment | None = Field(
        default=None, description="The splice (SPL_) path assessment."
    )
    selected_path: MissenseSelectedPath | None = Field(
        default=None, description="Which path was applied to the VBC after the comparison."
    )
    applied_total: float | None = Field(
        default=None, description="The final points applied to the VBC (the MIS_ or SPL_ total)."
    )
```

- [ ] **Step 4: Format + lint the module and tests**

Run: `uv run ruff format src/svcv4_model/missense.py tests/test_missense.py && uv run ruff check --fix src/svcv4_model/missense.py tests/test_missense.py`
Expected: `ruff format` reports files unchanged (or reformats trivially); `ruff check --fix` sorts the widened test import block and exits clean.

- [ ] **Step 5: Run the comparison tests — expect only the package-root import test to fail**

Run: `uv run pytest tests/test_missense.py -q`
Expected: `test_missense_assessment_importable_from_package_root` **FAILS** (names not yet in `svcv4_model.__all__`); every other test (amino-acid, splice, and the new comparison ones) **PASSES**. This isolates the remaining work to the export step.

- [ ] **Step 6: Commit the module + tests**

```bash
git add src/svcv4_model/missense.py tests/test_missense.py
git commit -m "feat: add Missense MIS_/SPL_ comparison model

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Export the two new names from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Widen the missense import block**

In `src/svcv4_model/__init__.py`, add `MissenseAssessment` and `MissenseSelectedPath` to the existing `from svcv4_model.missense import (...)` block, in sorted position — `MissenseAssessment` **after `MissenseAminoAcidAssessment`** and before `MissenseInfCategory`; `MissenseSelectedPath` **after `MissensePredictor`** and before `MissenseSpliceAssessment`:

```python
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
    MissenseSelectedPath,
    MissenseSpliceAssessment,
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)
```

- [ ] **Step 2: Add the two names to `__all__`, in sorted position**

`__all__` is hand-sorted (ruff does not sort it). Two insertions:

(a) Insert `"MissenseAssessment"` **between `"MissenseAminoAcidAssessment"` and `"MissenseInfCategory"`**:

```python
    "MissenseAminoAcidAssessment",
    "MissenseAssessment",
    "MissenseInfCategory",
```

(b) Insert `"MissenseSelectedPath"` **between `"MissensePredictor"` and `"MissenseSpliceAssessment"`**:

```python
    "MissensePredictor",
    "MissenseSelectedPath",
    "MissenseSpliceAssessment",
```

- [ ] **Step 3: Let ruff sort the import block and verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: the import block is isort-sorted (the `__all__` list is already correct from Step 2 — ruff does not reorder it); both clean (exit 0).

- [ ] **Step 4: Run the full test file — all green now**

Run: `uv run pytest tests/test_missense.py -q`
Expected: **all tests PASS**, including `test_missense_assessment_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export Missense comparison assessment from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Regenerate and commit the JSON schema

**Files:**
- Generate: `schemas/json/MissenseAssessment.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: **one new** file — `schemas/json/MissenseAssessment.schema.json`. The StrEnum gets none. Existing schema files (including the two embedded assessments' own files) are unchanged.

- [ ] **Step 2: Sanity-check the schema**

Run: `uv run python -c "import json; d=json.load(open('schemas/json/MissenseAssessment.schema.json')); print(sorted(d.get('\$defs', {}).keys()))"`
Expected: `$defs` include `MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`, `MissenseSelectedPath` (and their transitively-nested defs). Confirms both embedded assessments serialize as `$ref`/`$defs` and the enum is a `$def`.

- [ ] **Step 3: Confirm `git status` shows exactly one new untracked file**

Run: `git status --porcelain schemas/json`
Expected: one `??` line for `MissenseAssessment.schema.json` only. **No modifications** to any existing schema. If any existing schema shows modified, stop and investigate.

- [ ] **Step 4: Verify the case-views drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`. `git diff --quiet` ignores untracked files, so the new schema doesn't trip it; `case-model.md` is unchanged (no `Workflow` entry).

- [ ] **Step 5: `git add` the new schema (load-bearing) and commit**

```bash
git add schemas/json/MissenseAssessment.schema.json
git commit -m "chore: generate Missense comparison JSON schema

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Documentation

**Files:**
- Modify: `docs/workflows/pfd/missense.md`
- Modify: `docs/reference/spec-alignment.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`

- [ ] **Step 1: Add the comparison section to `missense.md`**

At the **end** of `docs/workflows/pfd/missense.md` (after the splice section, whose last paragraph ends "…to decide which applies."), append:

```markdown
## Selecting the final code (`MIS_` vs `SPL_`)

The analyst evaluates **both** paths for every missense VBC, then applies one. The
overall workflow assessment is captured as `MissenseAssessment`, which holds both
the `amino_acid` (`MissenseAminoAcidAssessment`) and `splice`
(`MissenseSpliceAssessment`) assessments — SM 6 requires **saving both** so a
future re-evaluation can reconsider — plus the `selected_path`
(`MissenseSelectedPath`: amino-acid or splice) and the `applied_total`.

The selection rule is **documented, not computed**:

- if the splice (`SPL_`) total is **negative**, use the **amino-acid** (`MIS_`) path;
- if the splice total is **positive**, use the **higher** (more positive) of the two;
- if both are positive **and equal**, use the **amino-acid** path (higher prior
  probability the effect is via the amino-acid change).

The applied code is `MIS_ −8.0 to +9.0` or `SPL_ −8.0 to +10.0` accordingly (the
code follows from `selected_path`).
```

- [ ] **Step 2: Flip the top admonition in `missense.md`**

Replace the admonition:

```markdown
!!! note "Modeling underway — both paths landed"

    Both the **amino-acid (`MIS_`) path** (`MissenseAminoAcidAssessment`) and the
    **splice (`SPL_`) paths** (`MissenseSpliceAssessment`) are modeled (inputs
    captured, scoring documented not computed). The `MIS_`-vs-`SPL_` comparison
    ("take the higher") is a later increment.
```

with:

```markdown
!!! note "Modeling complete — both paths + the comparison landed"

    The full Missense workflow is modeled (inputs captured, scoring documented not
    computed): the **amino-acid (`MIS_`) path** (`MissenseAminoAcidAssessment`), the
    **splice (`SPL_`) paths** (`MissenseSpliceAssessment`), and the `MIS_`-vs-`SPL_`
    comparison (`MissenseAssessment`, "take the higher"). Only the motif-variant
    special case (with SM 7) remains.
```

- [ ] **Step 3: Update the SM 6 row in `spec-alignment.md`**

Replace the SM 6 row:

```markdown
| 6 | [Missense Variants](https://docs.google.com/document/d/1eerqnL0kRq1se341-pxHxNI7HrPP9_kDlLL4eDvt-Gk/edit) | `MIS_*`, `SPL_*` (missense path) | **Modeled (inputs)** — both the amino-acid (`MIS_`) path (`MissenseAminoAcidAssessment`) and the splice (`SPL_`) paths (`MissenseSpliceAssessment`, five prediction outcomes reusing SM 18/19/20) are modeled; only the `MIS_`-vs-`SPL_` comparison ("take the higher") is pending. See [Missense](../workflows/pfd/missense.md) |
```

with:

```markdown
| 6 | [Missense Variants](https://docs.google.com/document/d/1eerqnL0kRq1se341-pxHxNI7HrPP9_kDlLL4eDvt-Gk/edit) | `MIS_*`, `SPL_*` (missense path) | **Modeled (inputs)** — the full Missense workflow: the amino-acid (`MIS_`) path (`MissenseAminoAcidAssessment`), the splice (`SPL_`) paths (`MissenseSpliceAssessment`, five prediction outcomes reusing SM 18/19/20), and the `MIS_`-vs-`SPL_` comparison (`MissenseAssessment`). Only the SM 7 motif-variant special case remains. See [Missense](../workflows/pfd/missense.md) |
```

- [ ] **Step 4: Update the "Full PFD modeling" row in `known-gaps.md`**

Replace the current row:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), and **both Missense paths** — amino-acid (`MissenseAminoAcidAssessment`) and splice (`MissenseSpliceAssessment`) — are now modeled (inputs only). What remains: the `MIS_`-vs-`SPL_` comparison; Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

with:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), and the **complete Missense workflow** — amino-acid (`MissenseAminoAcidAssessment`), splice (`MissenseSpliceAssessment`), and the `MIS_`-vs-`SPL_` comparison (`MissenseAssessment`) — are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

- [ ] **Step 5: Append the model.md entry**

In `docs/reference/model.md`, after the `::: svcv4_model.MissenseSpliceAssessment` entry (the current last entry), append:

```markdown

---

::: svcv4_model.MissenseAssessment
```

- [ ] **Step 6: Build the docs strictly**

Run: `uv run mkdocs build --strict 2>&1 | tail -10`
Expected: `Documentation built…` with **no** WARNING lines. (This increment adds no new page or cross-page link — only a new same-page section and text edits — so strict has nothing new to validate beyond the existing structure.)

- [ ] **Step 7: Commit the docs**

```bash
git add docs/workflows/pfd/missense.md docs/reference/spec-alignment.md \
        docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: document the Missense MIS_/SPL_ comparison

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Full quality gates

**Files:** none (verification only)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -q`
Expected: all tests pass (the extended `tests/test_missense.py` plus the existing suite).

- [ ] **Step 2: Lint + format**

Run: `uv run ruff check && uv run ruff format --check .`
Expected: both clean (exit 0).

- [ ] **Step 3: Schema/case-view drift gate**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`.

- [ ] **Step 4: Strict docs build**

Run: `uv run mkdocs build --strict 2>&1 | tail -5`
Expected: built with no warnings.

- [ ] **Step 5: Confirm a clean tree**

Run: `git status --porcelain`
Expected: only pre-existing untracked files unrelated to this work (`docs/Docsite Review Plan.md`, `docs/phenopackets-case-mapping.pptx`, `docs/superpowers/context/`). Nothing from this increment left uncommitted.

---

## Definition of done

- `MissenseSelectedPath` and `MissenseAssessment` importable from `svcv4_model`, all-optional, `extra="forbid"`.
- One new committed JSON schema; no existing schema changed; `case-model.md` untouched.
- The Missense page has the comparison section and the "complete" admonition; spec-alignment, known-gaps, and model docs updated.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR for increment 2c, run the `code-review` skill on the diff, address findings, then merge on request. This **completes the Missense workflow** (2a MIS + 2b SPL + 2c comparison). The next PFD variant-type workflows (Nonsense, Frameshift, …), SM 7 Critical Amino Acids, and the scoring computation remain on the backlog.
