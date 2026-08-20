# Nonsense Variants (`NUL_`/`CDS_`) Workflow Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the SVCv4 Nonsense variants workflow (SM 8) as a new capture-only Pydantic module `nonsense.py` — one `NonsenseAssessment` parameterized by a three-value branch enum, resolving to a `NUL_`/`CDS_` parent code and reusing the SM 18/19/20 submodules.

**Architecture:** One new standalone module `src/svcv4_model/nonsense.py` following the `missense.py` / `pfd.py` precedent — permissive all-optional models, `ConfigDict(extra="forbid")`, `from __future__ import annotations`. `NonsenseAssessment` mirrors `PfdCodeAssessment`'s shape but swaps in a typed `NonsensePredictiveEvidence` and adds a `NonsensePredictionOutcome` branch selector, reusing `PfdParentCode` (NUL/CDS), `MechanismExonRelevanceEvidence`, `FunctionalAssayEvidence`, and `InformativeVariantsEvidence`. Standalone PFD payload — no `Case`, no `Workflow` enum entry, no applicability-matrix row, so `case-model.md` and the per-workflow case views are untouched. Two new committed JSON schemas (one per BaseModel); the StrEnum gets none. Scoring is documented in prose, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv`, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-20-nonsense-workflow-design.md` (committed on this branch).

**Branch:** `feat/pfd-nonsense` (checked out; spec committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/nonsense.py` | The workflow: 1 enum + 2 models | Create |
| `src/svcv4_model/__init__.py` | Export the three new public names | Modify |
| `tests/test_nonsense.py` | Unit tests (round-trip, permissive-empty, extra-forbid, enums, importable) | Create |
| `schemas/json/NonsenseAssessment.schema.json` | Generated (embeds reused models + enums as `$defs`) | Generate + `git add` |
| `schemas/json/NonsensePredictiveEvidence.schema.json` | Generated | Generate + `git add` |
| `docs/workflows/pfd/nonsense.md` | New Nonsense workflow page | Create |
| `mkdocs.yml` | Add the new page to the PFD nav | Modify |
| `docs/workflows/pfd/index.md` | Add Nonsense to the modeled workflows + fix stale Missense text | Modify |
| `docs/reference/spec-alignment.md` | SM 8 row → modeled | Modify |
| `docs/reference/known-gaps.md` | "Full PFD modeling" row → Nonsense done | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.NonsenseAssessment` | Modify |

---

## Chunk 1: Nonsense workflow module, exports, schemas, docs

### Task 1: Create the `nonsense.py` module (TDD)

**Files:**
- Create: `src/svcv4_model/nonsense.py`
- Create: `tests/test_nonsense.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_nonsense.py`. It imports from `svcv4_model.nonsense` (doesn't exist yet → collection fails):

```python
"""Tests for the SVCv4 Nonsense variants (NUL_/CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import InformativeVariant, InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.nonsense import (
    NonsenseAssessment,
    NonsensePredictionOutcome,
    NonsensePredictiveEvidence,
)
from svcv4_model.pfd import PfdParentCode


def _maximal_assessment() -> NonsenseAssessment:
    return NonsenseAssessment(
        prediction_outcome=NonsensePredictionOutcome.NMD_NO_RESCUE,
        parent_code=PfdParentCode.NUL,
        predictive=NonsensePredictiveEvidence(
            basis="NMD predicted (PTC >=50nt upstream of last exon-intron boundary)",
            initial_points=6.0,
            protein_fraction_reduced=0.9,
            alternative_met_rescue=False,
            adjusted_points=6.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(variants=[InformativeVariant()]),
        prd_points=6.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_fxn_combined=8.0,
        parent_total=9.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = NonsenseAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = NonsenseAssessment()
    assert empty.prediction_outcome is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        NonsenseAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        NonsensePredictiveEvidence(not_a_field=1)


def test_prediction_outcome_values_round_trip() -> None:
    for outcome in NonsensePredictionOutcome:
        assert NonsenseAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_parent_code_accepts_nul_and_cds() -> None:
    for code in (PfdParentCode.NUL, PfdParentCode.CDS):
        assert NonsenseAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "NonsenseAssessment",
        "NonsensePredictionOutcome",
        "NonsensePredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_nonsense.py -q`
Expected: collection **ERROR** — `ModuleNotFoundError: No module named 'svcv4_model.nonsense'`.

- [ ] **Step 3: Create the module**

Create `src/svcv4_model/nonsense.py` with exactly this content (from spec §5.1; longest line is 95 chars, under the 100 limit):

```python
"""SVCv4 Nonsense variants workflow (SM 8).

Nonsense variants resolve to a NUL_ or CDS_ parent code via one of three branches
selected by whether NMD is predicted and whether an alternative-Met rescue codon
has evidence: NMD + no rescue → NUL_; NMD + rescue → CDS_; no NMD → CDS_. All three
run the same pipeline — predictive (PRD) → functional (FXN, SM 20) → informative
(INF, SM 19) → parent total — with the SM 18 mechanism/exon matrix applied to the
predictive points. This module captures the analyst's inputs; the scoring is
documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class NonsensePredictionOutcome(StrEnum):
    """Which of the three nonsense branches applies to the VBC (SM 8)."""

    NMD_NO_RESCUE = "NMD_NO_RESCUE"
    NMD_WITH_RESCUE = "NMD_WITH_RESCUE"
    NO_NMD = "NO_NMD"


class NonsensePredictiveEvidence(BaseModel):
    """The nonsense predictive (PRD) step of a nonsense branch (SM 8).

    NMD-predicted (yellow) starts at a fixed +6.0; the rescue (orange) and no-NMD
    (violet) branches derive initial points from the fraction of protein lost.
    Positive points are reduced by the SM 18 mechanism/exon matrix.
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None, description="Predictive basis (e.g. NMD prediction; PTC position)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial PRD points before the SM 18 adjustment."
    )
    protein_fraction_reduced: float | None = Field(
        default=None,
        description="Fraction of protein lost (the orange/violet initial-points table).",
    )
    alternative_met_rescue: bool | None = Field(
        default=None,
        description="Evidence an alternative-Met start codon rescues function (orange branch).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class NonsenseAssessment(BaseModel):
    """A nonsense variant (NUL_/CDS_) assessment (SM 8).

    One entity for all three branches, parameterized by ``prediction_outcome``;
    reuses the SM 18/19/20 submodules and the shared ``PfdParentCode`` (NUL/CDS).
    Permissive superset; the per-branch pipeline and its caps are documented, not
    computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: NonsensePredictionOutcome | None = Field(
        default=None, description="Which of the three nonsense branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL for yellow; CDS otherwise)."
    )
    predictive: NonsensePredictiveEvidence | None = Field(
        default=None, description="The PRD predictive step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded PRD point value.")
    fxn_points: float | None = Field(default=None, description="Coded FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded INF point value.")
    prd_fxn_combined: float | None = Field(
        default=None, description="Held PRD + FXN combined value (no distinct code)."
    )
    parent_total: float | None = Field(
        default=None, description="Capped parent-code total (NUL_/CDS_ −8.0 to +10.0)."
    )
```

- [ ] **Step 4: Format + lint the new files**

Run: `uv run ruff format src/svcv4_model/nonsense.py tests/test_nonsense.py && uv run ruff check --fix src/svcv4_model/nonsense.py tests/test_nonsense.py`
Expected: `ruff format` reports files unchanged (or reformats trivially); `ruff check --fix` clean (fixes any import ordering).

- [ ] **Step 5: Run the tests — expect only the package-root import test to fail**

Run: `uv run pytest tests/test_nonsense.py -q`
Expected: `test_importable_from_package_root` **FAILS** (names not yet in `svcv4_model.__all__`); all other tests **PASS** (they import from `svcv4_model.nonsense` directly). This isolates the remaining work to the export step.

- [ ] **Step 6: Commit the module + tests**

```bash
git add src/svcv4_model/nonsense.py tests/test_nonsense.py
git commit -m "feat: add Nonsense variants (NUL_/CDS_) workflow module

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Export the three names from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Add the import block**

In `src/svcv4_model/__init__.py`, add a new import block **after** the `from svcv4_model.missense import (...)` block (which ends with a line `)`) and **before** the `from svcv4_model.pfd import (` block (module order: `missense` < `nonsense` < `pfd`):

```python
from svcv4_model.nonsense import (
    NonsenseAssessment,
    NonsensePredictionOutcome,
    NonsensePredictiveEvidence,
)
```

- [ ] **Step 2: Add the three names to `__all__`, in sorted position**

`__all__` is hand-sorted (ruff does not sort it). Insert the three strings **between `"MolecularMechanism"` and `"PfdCodeAssessment"`** (`Mo` < `No` < `Pf`):

```python
    "MolecularMechanism",
    "NonsenseAssessment",
    "NonsensePredictionOutcome",
    "NonsensePredictiveEvidence",
    "PfdCodeAssessment",
```

- [ ] **Step 3: Let ruff sort the import block and verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: the import block is isort-sorted (the `__all__` list is already correct from Step 2 — ruff does not reorder it); both clean (exit 0).

- [ ] **Step 4: Run the full Nonsense test file — all green now**

Run: `uv run pytest tests/test_nonsense.py -q`
Expected: **all tests PASS**, including `test_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export Nonsense workflow from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Regenerate and commit the JSON schemas

**Files:**
- Generate: `schemas/json/NonsenseAssessment.schema.json`
- Generate: `schemas/json/NonsensePredictiveEvidence.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: **two new** files appear (the two BaseModels). The StrEnum gets none. Existing schema files (including the reused `MechanismExonRelevanceEvidence` / `FunctionalAssayEvidence` / `InformativeVariantsEvidence` / `PfdCodeAssessment`) are unchanged.

- [ ] **Step 2: Sanity-check the top-level assessment schema**

Run: `uv run python -c "import json; d=json.load(open('schemas/json/NonsenseAssessment.schema.json')); print(sorted(d.get('\$defs', {}).keys()))"`
Expected: `$defs` include `NonsensePredictiveEvidence`, `NonsensePredictionOutcome`, `PfdParentCode`, `MechanismExonRelevanceEvidence`, `FunctionalAssayEvidence`, `InformativeVariantsEvidence` (and their transitively-nested defs). Confirms reused models embed as `$ref`/`$defs` and enums are `$defs` (not inlined).

- [ ] **Step 3: Confirm `git status` shows exactly two new untracked files**

Run: `git status --porcelain schemas/json`
Expected: two `??` lines for the two new files only. **No modifications** to any existing schema. If any existing schema shows modified, stop and investigate.

- [ ] **Step 4: Verify the case-views drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`. `git diff --quiet` ignores untracked files, so the two new schemas don't trip it; `case-model.md` is unchanged (no `Workflow` entry).

- [ ] **Step 5: `git add` the two new schemas (load-bearing) and commit**

```bash
git add schemas/json/NonsenseAssessment.schema.json \
        schemas/json/NonsensePredictiveEvidence.schema.json
git commit -m "chore: generate Nonsense workflow JSON schemas

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Documentation

**Files:**
- Create: `docs/workflows/pfd/nonsense.md`
- Modify: `mkdocs.yml`
- Modify: `docs/workflows/pfd/index.md`
- Modify: `docs/reference/spec-alignment.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`

- [ ] **Step 1: Create the Nonsense workflow page**

Create `docs/workflows/pfd/nonsense.md`:

```markdown
# Nonsense variants (`NUL_` / `CDS_`)

**Nonsense variants** introduce a premature termination codon (PTC). SVCv4
(Supplementary Material 8) routes each VBC down **one** of three branches, selected
by whether **NMD** is predicted and whether an alternative-Met **rescue** codon has
evidence. Each branch resolves to a parent code — `NUL_` or `CDS_` — via the same
pipeline: **PRD** (predictive) → **FXN** (functional, SM 20) → **INF** (informative,
SM 19) → the capped parent total. Modeled as one `NonsenseAssessment`
(`prediction_outcome` = `NonsensePredictionOutcome`); each step is **documented, not
computed**.

!!! note "Modeled here — inputs captured"

    Both models (`NonsenseAssessment`, `NonsensePredictiveEvidence`) capture the
    analyst's inputs; the scoring is documented, not computed.

| Branch (`prediction_outcome`) | NMD? | Rescue? | Parent code | PRD initial | Parent total |
|---|---|---|---|---|---|
| `NMD_NO_RESCUE` (yellow) | yes | no | `NUL_` | `+6.0` | `−8.0 to +10.0` |
| `NMD_WITH_RESCUE` (orange) | yes | yes | `CDS_` | `−1.0 to +6.0` | `−8.0 to +10.0` |
| `NO_NMD` (violet) | no | — | `CDS_` | `0.0 to +6.0` | `−8.0 to +10.0` |

The parent code reuses `PfdParentCode` (`NUL` / `CDS`).

### Predictive (`*_PRD_`)

The **yellow** branch awards a fixed **+6.0** for a predicted NMD event. The
**orange** and **violet** branches instead read initial points from a table keyed on
the **fraction of protein lost** (`protein_fraction_reduced`) — and, as an
alternative axis, the **criticality of the deleted amino acids**, which leans on
Critical Amino Acids and is **deferred** (see the cross-reference note below). The
`alternative_met_rescue` flag records the rescue-codon evidence that distinguishes
the orange branch. Positive initial points are then reduced by the
[Molecular Mechanism & Exon Relevance](index.md#molecular-mechanism-exon-relevance-modeled-inputs)
matrix (SM 18); the result is coded `*_PRD_` per the branch's range above.

### Functional (`*_FXN_`) and informative (`*_INF_`)

`FXN` reuses the generic [Functional Assays](index.md#functional-assays-modeled-inputs)
module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0` — for the yellow branch the
functional data must confirm **loss of transcript/protein** (validating NMD), not a
truncated-protein effect. `INF` reuses the generic
[Informative Variants](index.md#informative-variants-modeled-inputs) module
(`InformativeVariantsEvidence`, SM 19): same-exon PTC (nonsense/frameshift) variants
(+2.0 first P / +1.0 first LP / +1.0 each additional; negatives for B/LB), coded
`−8.0 to +8.0`. The **position** eligibility differs subtly per branch: same-exon
same-NMD (yellow); a P/LP PTC between the VBC and the alternate start (orange); a PTC
downstream of the VBC (violet) — a documented eligibility rule, not separate fields.

### Held combined value and the parent total

Per SM 8, the model records **both** the separate coded values and the one held
`PRD + FXN` combined value (`prd_fxn_combined`, no distinct code). Note the held cap
is **`+10.0` for yellow** but **`+9.0` for orange/violet**, even though all three
*parent* totals cap at `+10.0`. The parent total (`parent_total`) is coded
`NUL_ −8.0 to +10.0` (yellow) or `CDS_ −8.0 to +10.0` (orange/violet).

**Gain-of-function** truncation effects (when NMD is not induced) are explicitly out
of scope in SM 8 and are not modeled here.

!!! note "SM 7 vs SM 11 cross-reference"

    SM 8's text cites "Supplementary Material 11" for Determining Critical Amino
    Acids, but in this project's [Spec coverage](../../reference/spec-alignment.md)
    Critical Amino Acids is **SM 7** (SM 11 is Canonical Splice Variants). Treat
    **SM 7** as the canonical reference; the critical-domain criticality axis is
    deferred to that increment.
```

- [ ] **Step 2: Add the page to the mkdocs nav**

In `mkdocs.yml`, under the PFD nav section, add the Nonsense page after Missense. Change:

```yaml
      - Predictive & Functional Data (PFD):
          - workflows/pfd/index.md
          - Missense (MIS_/SPL_): workflows/pfd/missense.md
```

to:

```yaml
      - Predictive & Functional Data (PFD):
          - workflows/pfd/index.md
          - Missense (MIS_/SPL_): workflows/pfd/missense.md
          - Nonsense (NUL_/CDS_): workflows/pfd/nonsense.md
```

- [ ] **Step 3: Update the closing note in `pfd/index.md` (add Nonsense + fix stale Missense text)**

In `docs/workflows/pfd/index.md`, replace the closing paragraph:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). The
first per-variant-type workflow has begun: the
[Missense](missense.md) amino-acid (`MIS_`) path is now modeled (inputs); its
splice (`SPL_`) paths and the `MIS_`-vs-`SPL_` comparison, the other variant-type
workflows, and Determining Critical Amino Acids (SM 7) are still to come.
```

with:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). Two
per-variant-type workflows are modeled: the full [Missense](missense.md) workflow
(the `MIS_` amino-acid path, the `SPL_` splice paths, and the `MIS_`-vs-`SPL_`
comparison) and the [Nonsense](nonsense.md) workflow (`NUL_`/`CDS_`, three
branches). The remaining variant-type workflows and Determining Critical Amino
Acids (SM 7) are still to come.
```

- [ ] **Step 4: Update the SM 8 row in `spec-alignment.md`**

In `docs/reference/spec-alignment.md`, replace the SM 8 row:

```markdown
| 8 | [Nonsense Variants](https://docs.google.com/document/d/1LFqIBpmw_plE8CFmRLbS2aeUYMibpVpxDjkbzJPHQsA/edit) | `NUL_*`, `CDS_*` | Not yet modeled |
```

with:

```markdown
| 8 | [Nonsense Variants](https://docs.google.com/document/d/1LFqIBpmw_plE8CFmRLbS2aeUYMibpVpxDjkbzJPHQsA/edit) | `NUL_*`, `CDS_*` | **Modeled (inputs)** — `NonsenseAssessment` captures the three branches (NMD+no-rescue → `NUL_`; NMD+rescue → `CDS_`; no-NMD → `CDS_`), reusing SM 18/19/20; the criticality axis (SM 7) is deferred. See [Nonsense](../workflows/pfd/nonsense.md) |
```

- [ ] **Step 5: Update the "Full PFD modeling" row in `known-gaps.md`**

In `docs/reference/known-gaps.md`, replace the current row:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), and the **complete Missense workflow** — amino-acid (`MissenseAminoAcidAssessment`), splice (`MissenseSpliceAssessment`), and the `MIS_`-vs-`SPL_` comparison (`MissenseAssessment`) — are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

with:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), the **complete Missense workflow** (`MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`, `MissenseAssessment`), and the **Nonsense workflow** (`NonsenseAssessment`, three branches → `NUL_`/`CDS_`) are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

- [ ] **Step 6: Append the model.md entry**

In `docs/reference/model.md`, after the **last** `::: svcv4_model.MissenseAssessment` entry, append:

```markdown

---

::: svcv4_model.NonsenseAssessment
```

- [ ] **Step 7: Build the docs strictly**

Run: `uv run mkdocs build --strict 2>&1 | tail -20`
Expected: `Documentation built…` with **no** WARNING lines. The new page must be in the nav (Step 2) or strict fails on an unreferenced page. The three `index.md#…` anchors used (`molecular-mechanism-exon-relevance-modeled-inputs`, `functional-assays-modeled-inputs`, `informative-variants-modeled-inputs`) all resolve to existing headings on `index.md`; if strict flags a broken link, read the warning and fix the offending link/page.

- [ ] **Step 8: Commit the docs**

```bash
git add docs/workflows/pfd/nonsense.md mkdocs.yml docs/workflows/pfd/index.md \
        docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: document the Nonsense variants (NUL_/CDS_) workflow

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Full quality gates

**Files:** none (verification only)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -q`
Expected: all tests pass (the new `tests/test_nonsense.py` plus the existing suite).

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

- `NonsenseAssessment`, `NonsensePredictionOutcome`, `NonsensePredictiveEvidence` importable from `svcv4_model`, all-optional, `extra="forbid"`.
- Two new committed JSON schemas; no existing schema changed; `case-model.md` untouched.
- New `pfd/nonsense.md` page in the nav; PFD overview lists Nonsense (and the stale Missense text is fixed); spec-alignment/known-gaps/model docs updated.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR for the Nonsense workflow, run the `code-review` skill on the diff, address findings, then merge on request. The remaining variant-type workflows (Frameshift, Canonical Splice, In-Frame InDel, Start/Stop loss, Exon del/dup) and SM 7 Critical Amino Acids remain on the backlog — several reuse `NUL_`/`CDS_`.
