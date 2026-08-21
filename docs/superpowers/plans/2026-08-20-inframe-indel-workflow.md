# In-Frame InDel Variants (`CDS_`) Workflow Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the SVCv4 In-Frame InDel variants workflow (SM 10) as a new capture-only Pydantic module `inframe_indel.py` — one `InframeIndelAssessment` parameterized by a two-value branch enum (SSR / non-repeat), always resolving to the `CDS_` parent code and reusing the SM 18/19/20 submodules.

**Architecture:** One new standalone module `src/svcv4_model/inframe_indel.py` mirroring `nonsense.py` / `frameshift.py` (a single-parent-code CDS workflow). Permissive all-optional models, `ConfigDict(extra="forbid")`, `from __future__ import annotations`. `InframeIndelAssessment` reuses `PfdParentCode` (always CDS here), `MechanismExonRelevanceEvidence`, `FunctionalAssayEvidence`, and `InformativeVariantsEvidence`, and adds a typed `InframeIndelPredictiveEvidence` spanning both branches. Standalone PFD payload — no `Case`, no `Workflow` enum entry, no applicability-matrix row, so `case-model.md` and the per-workflow case views are untouched. Two new committed JSON schemas (one per BaseModel); the StrEnum gets none. Scoring is documented in prose, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv`, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-20-inframe-indel-workflow-design.md` (committed on this branch).

**Branch:** `feat/pfd-inframe-indel` (checked out; spec committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/inframe_indel.py` | The workflow: 1 enum + 2 models | Create |
| `src/svcv4_model/__init__.py` | Export the three new public names | Modify |
| `tests/test_inframe_indel.py` | Unit tests (round-trip, permissive-empty, extra-forbid, enum, importable) | Create |
| `schemas/json/InframeIndelAssessment.schema.json` | Generated (embeds reused models + enums as `$defs`) | Generate + `git add` |
| `schemas/json/InframeIndelPredictiveEvidence.schema.json` | Generated | Generate + `git add` |
| `docs/workflows/pfd/inframe-indel.md` | New In-Frame InDel workflow page | Create |
| `mkdocs.yml` | Add the new page to the PFD nav | Modify |
| `docs/workflows/pfd/index.md` | Add In-Frame InDel to the modeled workflows | Modify |
| `docs/reference/spec-alignment.md` | SM 10 row → modeled | Modify |
| `docs/reference/known-gaps.md` | "Full PFD modeling" row → In-Frame InDel done | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.InframeIndelAssessment` | Modify |

---

## Chunk 1: In-Frame InDel workflow module, exports, schemas, docs

### Task 1: Create the `inframe_indel.py` module (TDD)

**Files:**
- Create: `src/svcv4_model/inframe_indel.py`
- Create: `tests/test_inframe_indel.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_inframe_indel.py`. It imports from `svcv4_model.inframe_indel` (doesn't exist yet → collection fails). The maximal assessment populates both branches' predictive fields and the reused submodules with real values:

```python
"""Tests for the SVCv4 In-Frame InDel variants (CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.inframe_indel import (
    InframeIndelAssessment,
    InframeIndelBranch,
    InframeIndelPredictiveEvidence,
)
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


def _maximal_assessment() -> InframeIndelAssessment:
    return InframeIndelAssessment(
        branch=InframeIndelBranch.NON_REPEAT,
        parent_code=PfdParentCode.CDS,
        predictive=InframeIndelPredictiveEvidence(
            basis="Removes >50% of the protein",
            initial_points=6.0,
            protein_fraction_reduced=0.6,
            in_silico_predictor="MutationTaster2021",
            in_silico_calibrated=True,
            repeat_stable_in_controls=None,
            adjusted_points=6.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.ALL,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000101",
                    classification=VariantClassification.PATHOGENIC,
                )
            ]
        ),
        prd_points=6.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_fxn_combined=8.0,
        parent_total=9.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = InframeIndelAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = InframeIndelAssessment()
    assert empty.branch is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        InframeIndelAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        InframeIndelPredictiveEvidence(not_a_field=1)


def test_branch_values_round_trip() -> None:
    for branch in InframeIndelBranch:
        assert InframeIndelAssessment(branch=branch).branch is branch


def test_parent_code_accepts_cds() -> None:
    assert InframeIndelAssessment(parent_code=PfdParentCode.CDS).parent_code is PfdParentCode.CDS


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "InframeIndelAssessment",
        "InframeIndelBranch",
        "InframeIndelPredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_inframe_indel.py -q`
Expected: collection **ERROR** — `ModuleNotFoundError: No module named 'svcv4_model.inframe_indel'`.

- [ ] **Step 3: Create the module**

Create `src/svcv4_model/inframe_indel.py` with exactly this content (from spec §5.1; longest line is 97 chars, under the 100 limit):

```python
"""SVCv4 In-Frame InDel variants workflow (SM 10).

In-frame insertions, duplications, deletions, and insertion-deletions within a
single exon (length change a multiple of three) always resolve to the CDS_ parent
code via one of two branches: a simple sequence repeat (SSR / tandem repeat) or a
non-repeat InDel. Both run the same pipeline — predictive (PRD) → functional (FXN,
SM 20) → informative (INF, SM 19) → the CDS_ total — with the SM 18 mechanism/exon
matrix applied to the non-repeat branch's predictive points. This module captures
the analyst's inputs; the scoring is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class InframeIndelBranch(StrEnum):
    """Which of the two in-frame InDel branches applies to the VBC (SM 10)."""

    SIMPLE_SEQUENCE_REPEAT = "SIMPLE_SEQUENCE_REPEAT"
    NON_REPEAT = "NON_REPEAT"


class InframeIndelPredictiveEvidence(BaseModel):
    """The in-frame InDel predictive (CDS_PRD) step (SM 10).

    The SSR branch scores 0.0 (stable in controls) or −1.0 (polymorphic); the
    non-repeat branch derives initial points from the protein fraction removed / a
    critical domain / an indel in-silico predictor, then applies the SM 18 matrix.
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None, description="Predictive basis (e.g. repeat length; deleted fraction)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial CDS_PRD points before the SM 18 adjustment."
    )
    protein_fraction_reduced: float | None = Field(
        default=None,
        description="Fraction of protein removed (the non-repeat initial-points table).",
    )
    in_silico_predictor: str | None = Field(
        default=None,
        description="Indel in-silico predictor used (e.g. MutationTaster2021, PROVEAN).",
    )
    in_silico_calibrated: bool | None = Field(
        default=None,
        description="Whether the indel predictor is calibrated (calibrated reaches +2.0).",
    )
    repeat_stable_in_controls: bool | None = Field(
        default=None,
        description="SSR branch: the repeat is stable in large control sets (else polymorphic).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded CDS_PRD points after the SM 18 adjustment."
    )


class InframeIndelAssessment(BaseModel):
    """An in-frame InDel (CDS_) assessment (SM 10).

    One entity for both branches, parameterized by ``branch``; reuses the SM 18/19/20
    submodules and the shared ``PfdParentCode`` (always CDS here). Permissive
    superset; the per-branch pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    branch: InframeIndelBranch | None = Field(
        default=None, description="Which of the two in-frame InDel branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (always CDS for in-frame InDels)."
    )
    predictive: InframeIndelPredictiveEvidence | None = Field(
        default=None, description="The CDS_PRD predictive step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (CDS_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (CDS_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded CDS_PRD point value.")
    fxn_points: float | None = Field(default=None, description="Coded CDS_FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded CDS_INF point value.")
    prd_fxn_combined: float | None = Field(
        default=None, description="Held CDS_PRD + CDS_FXN combined value (no distinct code)."
    )
    parent_total: float | None = Field(
        default=None, description="Capped CDS_ parent-code total (−8.0 to +10.0)."
    )
```

- [ ] **Step 4: Format + lint the new files**

Run: `uv run ruff format src/svcv4_model/inframe_indel.py tests/test_inframe_indel.py && uv run ruff check --fix src/svcv4_model/inframe_indel.py tests/test_inframe_indel.py`
Expected: `ruff format` reports files unchanged (or reformats trivially); `ruff check --fix` clean (fixes any import ordering).

- [ ] **Step 5: Run the tests — expect only the package-root import test to fail**

Run: `uv run pytest tests/test_inframe_indel.py -q`
Expected: `test_importable_from_package_root` **FAILS** (names not yet in `svcv4_model.__all__`); all other tests **PASS** (they import from `svcv4_model.inframe_indel` directly). This isolates the remaining work to the export step.

- [ ] **Step 6: Commit the module + tests**

```bash
git add src/svcv4_model/inframe_indel.py tests/test_inframe_indel.py
git commit -m "feat: add In-Frame InDel variants (CDS_) workflow module

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Export the three names from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Add the import block**

In `src/svcv4_model/__init__.py`, add a new import block **after** the `from svcv4_model.informative import (...)` block (which ends with a line `)`) and **before** the `from svcv4_model.inputs import MDE, VBC` line (module order: `informative` < `inframe_indel` < `inputs`):

```python
from svcv4_model.inframe_indel import (
    InframeIndelAssessment,
    InframeIndelBranch,
    InframeIndelPredictiveEvidence,
)
```

- [ ] **Step 2: Add the three names to `__all__`, in sorted position**

`__all__` is hand-sorted (ruff does not sort it). Insert the three strings **between `"InformativeVariantsEvidence"` and `"ManeStatus"`** (`Info` < `Infr`, and `Infr` < `Mane`):

```python
    "InformativeVariantsEvidence",
    "InframeIndelAssessment",
    "InframeIndelBranch",
    "InframeIndelPredictiveEvidence",
    "ManeStatus",
```

- [ ] **Step 3: Let ruff sort the import block and verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: the import block is isort-sorted (the `__all__` list is already correct from Step 2 — ruff does not reorder it); both clean (exit 0).

- [ ] **Step 4: Run the full In-Frame InDel test file — all green now**

Run: `uv run pytest tests/test_inframe_indel.py -q`
Expected: **all tests PASS**, including `test_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export In-Frame InDel workflow from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Regenerate and commit the JSON schemas

**Files:**
- Generate: `schemas/json/InframeIndelAssessment.schema.json`
- Generate: `schemas/json/InframeIndelPredictiveEvidence.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: **two new** files appear (the two BaseModels). The StrEnum gets none. Existing schema files (including the reused `MechanismExonRelevanceEvidence` / `FunctionalAssayEvidence` / `InformativeVariantsEvidence` / `PfdCodeAssessment`) are unchanged.

- [ ] **Step 2: Sanity-check the top-level assessment schema**

Run: `uv run python -c "import json; d=json.load(open('schemas/json/InframeIndelAssessment.schema.json')); print(sorted(d.get('\$defs', {}).keys()))"`
Expected: `$defs` include `InframeIndelPredictiveEvidence`, `InframeIndelBranch`, `PfdParentCode`, `MechanismExonRelevanceEvidence`, `FunctionalAssayEvidence`, `InformativeVariantsEvidence` (and their transitively-nested defs). Confirms reused models embed as `$ref`/`$defs` and enums are `$defs` (not inlined).

- [ ] **Step 3: Confirm `git status` shows exactly two new untracked files**

Run: `git status --porcelain schemas/json`
Expected: two `??` lines for the two new files only. **No modifications** to any existing schema. If any existing schema shows modified, stop and investigate.

- [ ] **Step 4: Verify the case-views drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`. `git diff --quiet` ignores untracked files, so the two new schemas don't trip it; `case-model.md` is unchanged (no `Workflow` entry).

- [ ] **Step 5: `git add` the two new schemas (load-bearing) and commit**

```bash
git add schemas/json/InframeIndelAssessment.schema.json \
        schemas/json/InframeIndelPredictiveEvidence.schema.json
git commit -m "chore: generate In-Frame InDel workflow JSON schemas

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Documentation

**Files:**
- Create: `docs/workflows/pfd/inframe-indel.md`
- Modify: `mkdocs.yml`
- Modify: `docs/workflows/pfd/index.md`
- Modify: `docs/reference/spec-alignment.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`

- [ ] **Step 1: Create the In-Frame InDel workflow page**

Create `docs/workflows/pfd/inframe-indel.md`:

```markdown
# In-Frame InDel variants (`CDS_`)

**In-frame InDels** are insertions, duplications, deletions, and insertion-deletions
that start and end within a single exon and change its length by a multiple of three
nucleotides. SVCv4 (Supplementary Material 10) routes each VBC down **one** of two
branches — a **simple sequence repeat** (SSR / tandem repeat) or a **non-repeat**
InDel — both of which always resolve to the **`CDS_`** parent code via the same
pipeline: **PRD** (predictive) → **FXN** (functional, SM 20) → **INF** (informative,
SM 19) → the capped `CDS_` total. Modeled as one `InframeIndelAssessment`
(`branch` = `InframeIndelBranch`); each step is **documented, not computed**.

!!! note "Modeled here — inputs captured"

    Both models (`InframeIndelAssessment`, `InframeIndelPredictiveEvidence`) capture
    the analyst's inputs; the scoring is documented, not computed.

| Branch (`branch`) | PRD initial | Held PRD+FXN | `CDS_` total |
|---|---|---|---|
| `SIMPLE_SEQUENCE_REPEAT` | `0.0` (stable in controls) / `−1.0` (polymorphic) | `−8.0 to +8.0` | `−8.0 to +10.0` |
| `NON_REPEAT` | `−1.0 to +6.0` (protein fraction / critical domain / in-silico tool) | `−8.0 to +9.0` | `−8.0 to +10.0` |

The parent code reuses `PfdParentCode` and is **always `CDS`** for in-frame InDels
(the field is kept for uniformity with the other variant-type assessments).

## Predictive (`CDS_PRD_`)

For a **simple sequence repeat** (a repeat ≥5 units), the analyst awards `0.0` if
the repeat is stable in large control sets (e.g. gnomAD) or `−1.0` if it is
polymorphic (`repeat_stable_in_controls`); a novel TRE length with unestablished
thresholds scores `0.0`. The SM 18 matrix is **not** applied on this branch.

For a **non-repeat** InDel, initial points come from a table keyed on the fraction
of protein removed (`protein_fraction_reduced`; `+6.0` for >50% removed or a
critical domain removed) and an indel **in-silico predictor** (`in_silico_predictor`
— CADD / CAPICE / PROVEAN / MutationTaster2021 / …): a **calibrated** tool reaches
`+2.0`, an **uncalibrated** one `+1.0 to −1.0` (`in_silico_calibrated`). Positive
points are then reduced by the
[Molecular Mechanism & Exon Relevance](index.md#molecular-mechanism-exon-relevance-modeled-inputs)
matrix (SM 18); the result is coded `CDS_PRD_ −1.0 to +6.0`.

## Functional (`CDS_FXN_`) and informative (`CDS_INF_`)

`FXN` reuses the generic [Functional Assays](index.md#functional-assays-modeled-inputs)
module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0`. `INF` reuses the generic
[Informative Variants](index.md#informative-variants-modeled-inputs) module
(`InformativeVariantsEvidence`, SM 19): +2.0 first P / +1.0 first LP / +1.0 each
additional (negatives for B/LB), VUS → 0.0, coded `−8.0 to +8.0`. The **eligibility**
differs per branch: for an SSR, a *shorter* repeat length for pathogenic informative
variants and a *longer* one for benign; for a non-repeat InDel, an informative
variant whose predicted effect is the *same or less damaging* (pathogenic) or *same
or more damaging* (benign) than the VBC — a documented eligibility rule, not separate
fields.

*(SM 10 has two source typos in the non-repeat section: the `CDS_INF_` heading is
mislabeled `CDS_FXN_`, and the functional no-data code appears as `CDN_FXN_ND`; the
correct codes are `CDS_INF_` and `CDS_FXN_ND`.)*

## Held combined value and the `CDS_` total

Per SM 10, the model records **both** the separate coded values and the one held
`CDS_PRD_ + CDS_FXN_` combined value (`prd_fxn_combined`, no distinct code). Note the
held cap is **`−8.0 to +8.0` for the SSR branch** but **`−8.0 to +9.0` for the
non-repeat branch**, even though both *parent* totals cap at `+10.0`. The parent
total (`parent_total`) is coded `CDS_ −8.0 to +10.0`.

## Out of scope

Two situations are handled elsewhere and are **not modeled** here:

- **MDE-specific guidance** — when disease-specific repeat guidance exists (e.g.
  Huntington disease), the analyst uses that guidance and does *not* score with this
  diagram.
- **Splice effects** — an indel at/near an exon/intron junction or one that creates a
  cryptic splice site is assessed via the splice flow ([Missense](missense.md) SM 6 /
  Canonical Splice SM 11), not here.

!!! note "SM 7 cross-reference"

    The critical-domain axis (an alternative to the protein-fraction table for the
    non-repeat branch) leans on
    [Determining Critical Amino Acids (SM 7)](../../reference/spec-alignment.md) and
    is deferred to that increment.
```

- [ ] **Step 2: Add the page to the mkdocs nav**

In `mkdocs.yml`, under the PFD nav section, add the In-Frame InDel page after Frameshift. Change:

```yaml
          - Nonsense (NUL_/CDS_): workflows/pfd/nonsense.md
          - Frameshift (NUL_/CDS_): workflows/pfd/frameshift.md
```

to:

```yaml
          - Nonsense (NUL_/CDS_): workflows/pfd/nonsense.md
          - Frameshift (NUL_/CDS_): workflows/pfd/frameshift.md
          - In-Frame InDel (CDS_): workflows/pfd/inframe-indel.md
```

- [ ] **Step 3: Add In-Frame InDel to the closing note in `pfd/index.md`**

In `docs/workflows/pfd/index.md`, replace the closing paragraph:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). Three
per-variant-type workflows are modeled: the full [Missense](missense.md) workflow
(the `MIS_` amino-acid path, the `SPL_` splice paths, and the `MIS_`-vs-`SPL_`
comparison), the [Nonsense](nonsense.md) workflow (`NUL_`/`CDS_`, three branches),
and the [Frameshift](frameshift.md) workflow (`NUL_`/`CDS_`, five branches). The
remaining variant-type workflows and Determining Critical Amino Acids (SM 7) are
still to come.
```

with:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). Four
per-variant-type workflows are modeled: the full [Missense](missense.md) workflow
(the `MIS_` amino-acid path, the `SPL_` splice paths, and the `MIS_`-vs-`SPL_`
comparison), the [Nonsense](nonsense.md) workflow (`NUL_`/`CDS_`, three branches),
the [Frameshift](frameshift.md) workflow (`NUL_`/`CDS_`, five branches), and the
[In-Frame InDel](inframe-indel.md) workflow (`CDS_`, two branches). The remaining
variant-type workflows and Determining Critical Amino Acids (SM 7) are still to
come.
```

- [ ] **Step 4: Update the SM 10 row in `spec-alignment.md`**

In `docs/reference/spec-alignment.md`, replace the SM 10 row:

```markdown
| 10 | [In-Frame InDel Variants](https://docs.google.com/document/d/1278qhDIDX94nlTUzwl7oIgZDLPc8YgEoFSVHXTHgRKk/edit) | `CDS_*` (assumed) | Not yet modeled |
```

with:

```markdown
| 10 | [In-Frame InDel Variants](https://docs.google.com/document/d/1278qhDIDX94nlTUzwl7oIgZDLPc8YgEoFSVHXTHgRKk/edit) | `CDS_*` | **Modeled (inputs)** — `InframeIndelAssessment` captures the two branches (simple sequence repeat; non-repeat InDel), both → `CDS_`, reusing SM 18/19/20; the criticality axis (SM 7) is deferred. See [In-Frame InDel](../workflows/pfd/inframe-indel.md) |
```

- [ ] **Step 5: Update the "Full PFD modeling" row in `known-gaps.md`**

In `docs/reference/known-gaps.md`, replace the current row:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), the **complete Missense workflow** (`MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`, `MissenseAssessment`), the **Nonsense workflow** (`NonsenseAssessment`, three branches), and the **Frameshift workflow** (`FrameshiftAssessment`, five branches → `NUL_`/`CDS_`) are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

with:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), the **complete Missense workflow** (`MissenseAminoAcidAssessment`, `MissenseSpliceAssessment`, `MissenseAssessment`), the **Nonsense workflow** (`NonsenseAssessment`, three branches), the **Frameshift workflow** (`FrameshiftAssessment`, five branches → `NUL_`/`CDS_`), and the **In-Frame InDel workflow** (`InframeIndelAssessment`, two branches → `CDS_`) are now modeled (inputs only). What remains: Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

- [ ] **Step 6: Append the model.md entry**

In `docs/reference/model.md`, after the **last** `::: svcv4_model.FrameshiftAssessment` entry, append:

```markdown

---

::: svcv4_model.InframeIndelAssessment
```

- [ ] **Step 7: Build the docs strictly**

Run: `uv run mkdocs build --strict 2>&1 | tail -20`
Expected: `Documentation built…` with **no** WARNING lines. The new page must be in the nav (Step 2) or strict fails on an unreferenced page. The `index.md#…` and `missense.md` links used all resolve to existing pages/headings; if strict flags a broken link, read the warning and fix it. (Use inline notes, not `[^...]` footnotes — the repo does not enable the `footnotes` markdown extension.)

- [ ] **Step 8: Commit the docs**

```bash
git add docs/workflows/pfd/inframe-indel.md mkdocs.yml docs/workflows/pfd/index.md \
        docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: document the In-Frame InDel variants (CDS_) workflow

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Full quality gates

**Files:** none (verification only)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -q`
Expected: all tests pass (the new `tests/test_inframe_indel.py` plus the existing suite).

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

- `InframeIndelAssessment`, `InframeIndelBranch`, `InframeIndelPredictiveEvidence` importable from `svcv4_model`, all-optional, `extra="forbid"`.
- Two new committed JSON schemas; no existing schema changed; `case-model.md` untouched.
- New `pfd/inframe-indel.md` page in the nav; PFD overview lists In-Frame InDel; spec-alignment/known-gaps/model docs updated.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR for the In-Frame InDel workflow, run the `code-review` skill on the diff, address findings, then merge on request. The remaining variant-type workflows (Canonical Splice SM 11, Start/Stop loss SM 15/16, Exon del/dup SM 13/14) and SM 7 Critical Amino Acids remain on the backlog.
