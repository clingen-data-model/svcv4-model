# POP Modeling Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture SVCv4 POP (population database frequency) evidence — POP_FRQ + POP_HMZ — as a new `PopulationEvidence` model, documenting the scoring without computing points.

**Architecture:** A new `src/svcv4_model/population.py` module holds a `DaftMethod` enum, a nested `DaftCalculatorInputs`, and the permissive `PopulationEvidence` entity (the typed payload for a `population_frequency` Evidence Item — parallel to `Case`). It reuses `TriState` from `case.py` (acyclic). No applicability matrix; the Case generated views are untouched. Docs flip POP from stub to modeled.

**Tech Stack:** Python 3 / Pydantic v2 (`StrEnum`, `BaseModel`, `ConfigDict(extra="forbid")`), `uv`, pytest, ruff (line-length 100), MkDocs (`strict: true`).

**Spec:** `docs/superpowers/specs/2026-08-13-pop-modeling-design.md`

---

## File Structure

- `src/svcv4_model/population.py` — **new.** `DaftMethod`, `DaftCalculatorInputs`, `PopulationEvidence`. Single responsibility: the POP evidence payload model.
- `src/svcv4_model/__init__.py` — export the three new public names (imports + `__all__`, alphabetical).
- `tests/test_population.py` — **new.** Round-trip, permissiveness, enum acceptance, package-root import.
- `schemas/json/PopulationEvidence.schema.json`, `schemas/json/DaftCalculatorInputs.schema.json` — **generated** (`scripts/export_schemas.py`); commit them.
- `docs/workflows/hod/pop.md` — stub → modeled.
- `docs/reference/concepts.md` — Cohort Allele Frequency + DAFT entries → modeled.
- `docs/reference/known-gaps.md` — remove the two POP model-gap rows; update the "Full POP modeling" content row.
- `docs/reference/spec-alignment.md` — SM 3 row → modeled.
- `docs/getting-started/capturing-basic-evidence.md` — forward pointer to `PopulationEvidence`.

**Conventions to follow (verified against the repo):** every field optional with `Field(default=None, ...)`; `ConfigDict(extra="forbid")`; wrap any field `description` that would exceed **100** chars using parenthesized string concatenation (ruff E501 + `ruff format --check` both run in CI); enums are `StrEnum` with `VALUE = "VALUE"`; nested helper models and top-level models both go in `__init__.__all__` (see `Age`, `CaseTesting`, `Case`).

---

## Chunk 1: Model + export + schema regeneration

### Task 1: `PopulationEvidence` model + export (TDD)

**Files:**
- Create: `src/svcv4_model/population.py`
- Modify: `src/svcv4_model/__init__.py`
- Create: `tests/test_population.py`

- [ ] **Step 1: Write the failing test.** Create `tests/test_population.py`:

```python
"""Tests for the SVCv4 Population (POP) evidence model."""

from __future__ import annotations

import pytest

from svcv4_model.case import TriState
from svcv4_model.population import (
    DaftCalculatorInputs,
    DaftMethod,
    PopulationEvidence,
)


def _maximal() -> PopulationEvidence:
    return PopulationEvidence(
        faf=0.00062,
        faf_source="gnomAD v4.1.1",
        daft=0.000118,
        daft_method=DaftMethod.CALCULATOR,
        daft_calculator_inputs=DaftCalculatorInputs(
            prevalence_denominator=5000,
            penetrance=0.85,
            locus_heterogeneity=1.0,
            allelic_heterogeneity=0.10,
        ),
        homozygote_count=3,
        hemizygote_count=0,
        hmz_eligible=TriState.TRUE,
    )


def test_population_evidence_round_trips_json() -> None:
    original = _maximal()
    rehydrated = PopulationEvidence.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_population_evidence_is_permissive_when_empty() -> None:
    assert PopulationEvidence().faf is None


def test_population_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        PopulationEvidence(not_a_field=1)


def test_daft_method_values_round_trip() -> None:
    for method in DaftMethod:
        pe = PopulationEvidence(daft_method=method)
        assert pe.daft_method is method
    assert DaftMethod.VCEP_CURATED.value == "VCEP_CURATED"


def test_hmz_eligible_accepts_each_tristate() -> None:
    for state in TriState:
        assert PopulationEvidence(hmz_eligible=state).hmz_eligible is state


def test_population_evidence_importable_from_package_root() -> None:
    import svcv4_model

    assert "PopulationEvidence" in svcv4_model.__all__
```

- [ ] **Step 2: Run the test to verify it fails.**

Run: `uv run pytest tests/test_population.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'svcv4_model.population'`.

- [ ] **Step 3: Create `src/svcv4_model/population.py`** with exactly the code from spec §5.1 (the `DaftMethod` enum, `DaftCalculatorInputs`, and `PopulationEvidence`, importing `TriState` from `svcv4_model.case`). Reproduce the field descriptions **as wrapped in the spec** — do not re-flatten them (they are wrapped to stay ≤100 chars).

- [ ] **Step 4: Export the new names** in `src/svcv4_model/__init__.py`:
  - In the `from svcv4_model.population import (...)` — add a new import block (place it after the `from svcv4_model.method import Method` line or wherever alphabetical by module; the repo groups by module). Import `DaftCalculatorInputs`, `DaftMethod`, `PopulationEvidence`.
  - In `__all__`, add `"DaftCalculatorInputs"`, `"DaftMethod"`, `"PopulationEvidence"` in alphabetical position.

- [ ] **Step 5: Run the tests + lint to verify green.**

Run: `uv run pytest tests/test_population.py -q && uv run ruff check src/svcv4_model/population.py tests/test_population.py && uv run ruff format --check src/svcv4_model/population.py tests/test_population.py`
Expected: tests PASS; ruff reports no errors and "would reformat" nothing. If E501 fires, a `description` is >100 chars — split the string across two parenthesized fragments.

- [ ] **Step 6: Run the full suite** (nothing else should break — no schema/model-parity test exists).

Run: `uv run pytest -q`
Expected: PASS.

- [ ] **Step 7: Commit.**

```bash
git add src/svcv4_model/population.py src/svcv4_model/__init__.py tests/test_population.py
git commit -m "feat: model POP (population database frequency) evidence"
```

### Task 2: Regenerate JSON Schemas

**Files:**
- Create (generated): `schemas/json/PopulationEvidence.schema.json`, `schemas/json/DaftCalculatorInputs.schema.json`

- [ ] **Step 1: Regenerate.**

Run: `uv run python scripts/export_schemas.py`
Expected: output lists the two new files among those written.

- [ ] **Step 2: Verify the diff is only additive and only under `schemas/json/`.**

Run: `git status --short schemas/json docs/workflows/case-model.md`
Expected: exactly two **new** files — `schemas/json/PopulationEvidence.schema.json` and `schemas/json/DaftCalculatorInputs.schema.json`. `docs/workflows/case-model.md` and all existing `schemas/json/*` files (incl. `Case.schema.json`, `WorkflowParameters.schema.json`, `case/*`) must be **unchanged**. If any existing file changed, stop and investigate.

- [ ] **Step 3: Commit the generated schemas.**

```bash
git add schemas/json/PopulationEvidence.schema.json schemas/json/DaftCalculatorInputs.schema.json
git commit -m "chore: generate JSON schemas for PopulationEvidence"
```

- [ ] **Step 4: Confirm the drift gate is clean (exact CI command).**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo CLEAN`
Expected: `CLEAN`.

---

## Chunk 2: Documentation

Pure docs. Verification is `mkdocs build --strict` + targeted greps. External SM links aren't checked by mkdocs — spot check manually.

### Task 3: `pop.md` stub → modeled

**Files:**
- Modify: `docs/workflows/hod/pop.md`

- [ ] **Step 1:** Replace the `!!! note "Not yet modeled here"` admonition — POP inputs are now modeled (scoring still documented-only).

- [ ] **Step 2:** Add a "What to capture" section describing `PopulationEvidence` fields: POP_FRQ (`faf`, `faf_source`, `daft`, `daft_method`, `daft_calculator_inputs`) and POP_HMZ (`homozygote_count`, `hemizygote_count`, `hmz_eligible`). Note inheritance is the shared `WorkflowParameters.moi`, not re-captured, and that this model captures inputs but does **not** compute points.

- [ ] **Step 3:** Add the POP_FRQ band table (spec §3.1) and the POP_HMZ rule (spec §3.3, −0.5/occurrence from the 2nd), each labeled as *documented scoring from SM 3, not computed here*. Include the boundary-ambiguity caveat from spec §3.1.

- [ ] **Step 4:** Link "Supplementary Material 3" → `https://docs.google.com/document/d/1XON2eq4HSM-guWlqitEnb8PghY0quNbA7_1WmmxvLj8/edit`. Update the stale line that says POP_HMZ's source "hasn't been read into this project yet."

- [ ] **Step 5: Verify.** `grep -in "been read\|Not yet modeled" docs/workflows/hod/pop.md` returns nothing (the stale line is "…material hasn't **been read** into this project yet").

### Task 4: `concepts.md` Cohort Allele Frequency + DAFT → modeled

**Files:**
- Modify: `docs/reference/concepts.md`

- [ ] **Step 1:** In the **Cohort Allele Frequency** entry, remove the `!!! note "Not yet modeled here"`; update "Current representation" to point at `PopulationEvidence` (`faf`/`faf_source`), noting it's a curation-level counterpart to the VA-Spec Cohort Allele Frequency Study Result (keep the existing VA-Spec profile link).

- [ ] **Step 2:** In the **Disease Allele Frequency Threshold (DAFT)** entry, remove its `!!! note "Not yet modeled here"`; update "Current representation" to `PopulationEvidence.daft` / `daft_method` / `daft_calculator_inputs`, and note points are documented not computed.

- [ ] **Step 3: Verify.** `grep -n "Not yet modeled" docs/reference/concepts.md` no longer matches inside the Cohort Allele Frequency or DAFT sections (it may still match nothing at all if GDV already removed the last one — that's fine).

### Task 5: `known-gaps.md` remove POP rows + update content row

**Files:**
- Modify: `docs/reference/known-gaps.md`

- [ ] **Step 1:** Remove the "Cohort Allele Frequency representation" model-gap row and the "Disease Allele Frequency Threshold (DAFT)" model-gap row. (If exact-string Edit fails on a special char, remove by unique substring with `grep -v`.)

- [ ] **Step 2:** Update the "Full POP modeling" content-gap row: POP_FRQ/POP_HMZ **inputs are now modeled** (`PopulationEvidence`); what remains is point computation (deferred with the other rule/method enforcement) and the binning lookup grids / pathogenic-variants list.

- [ ] **Step 3: Verify.** `grep -cn "Cohort Allele Frequency representation\|Disease Allele Frequency Threshold (DAFT)" docs/reference/known-gaps.md` returns 0.

### Task 6: `spec-alignment.md` SM 3 → modeled

**Files:**
- Modify: `docs/reference/spec-alignment.md`

- [ ] **Step 1:** Change the SM 3 row's Model-coverage cell from "Not yet modeled …" to: "**Modeled** (inputs) — `PopulationEvidence` captures FAF/DAFT/method + homozygote occurrences; scoring documented, not computed. See `[Population (POP)](../workflows/hod/pop.md)`." Keep the existing SM 3 Google Doc link on the title.

- [ ] **Step 2: Verify.** SM 3 row now says "Modeled"; row count unchanged.

### Task 7: `capturing-basic-evidence.md` — flip "not yet modeled" framing

This page currently asserts POP is unmodeled in three places; all become false. Revise
each while **keeping the still-true caveat** that POP has no `Workflow` enum entry and no
applicability-matrix entries (it isn't a Case workflow — spec §3.4).

**Files:**
- Modify: `docs/getting-started/capturing-basic-evidence.md`

- [ ] **Step 1: Revise the "What this project models today" opening (lines 53–60).** Replace the "is **not yet modeled** in this repo. Population (POP) is a genuine stub… both documented there as forward-looking concepts only." passage. New framing: the raw evidence above (FAF as a first-class value, DAFT + method, homozygote/hemizygote occurrences) **is now captured** by `PopulationEvidence` (see `[Population (POP)](../workflows/hod/pop.md)` and `[Core concepts](../reference/concepts.md)`). Preserve the accurate distinction: POP still has **no `Workflow` enum entry and no applicability-matrix entries** (unlike the CLN/LOC workflows), because it is a standalone Evidence Item payload rather than a Case workflow; and scoring is documented, not computed.

- [ ] **Step 2: Update the result paragraph (lines 62–69).** Keep it (the `pop_frq_points` result on `WorkflowParameters` is unchanged), but adjust any wording implying the raw evidence *isn't* modeled — e.g. change "without yet modeling the evaluation itself" to note the model now carries the **evidence inputs** (`PopulationEvidence`) *and* the scored `pop_frq_points` result, while the point **computation** between them remains out of scope.

- [ ] **Step 3: Update the "See also" captions (lines 85–88).** `pop.md` is no longer "the stub page" — recaption to "the Population Evidence Concept, now modeled." `concepts.md` is no longer "forward-looking-only" for these — recaption to "Cohort Allele Frequency and DAFT."

- [ ] **Step 4: Verify.** `grep -in "not yet modeled\|genuine stub\|forward-looking concepts only\|stub page" docs/getting-started/capturing-basic-evidence.md` returns nothing.

### Task 8: Build + commit docs

- [ ] **Step 1: Build strict.**

Run: `uv run mkdocs build --strict`
Expected: no warnings/errors. Fix any broken internal link (don't disable strict).

- [ ] **Step 2: Manual external-link spot check.** Open the SM 3 link once to confirm it resolves.

- [ ] **Step 3: Commit.**

```bash
git add docs/workflows/hod/pop.md docs/reference/concepts.md docs/reference/known-gaps.md docs/reference/spec-alignment.md docs/getting-started/capturing-basic-evidence.md
git commit -m "docs: model POP (population frequency) evidence + scoring reference"
```

---

## Done criteria

- `uv run pytest -q` green (new `tests/test_population.py`; no regressions).
- `uv run ruff check` and `uv run ruff format --check .` clean.
- `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md` → clean (two new schema files committed).
- `uv run mkdocs build --strict` passes.
- `grep -rn "Not yet modeled" docs/reference/concepts.md` no longer matches the Cohort Allele Frequency or DAFT sections.
- `grep -in "not yet modeled\|genuine stub\|forward-looking concepts only\|stub page" docs/getting-started/capturing-basic-evidence.md` returns nothing (POP no longer described as unmodeled anywhere).
- No point-computation code added (scope boundary respected).
