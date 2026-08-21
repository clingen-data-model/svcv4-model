# Single/Multi-Exon Deletion (`NUL_`/`CDS_`) Workflow Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the SVCv4 Single/Multi-Exon Deletion workflow (SM 13) as a new capture-only Pydantic module `exon_deletion.py` — one `ExonDeletionAssessment` parameterized by a six-value branch enum, resolving to a `NUL_`/`CDS_` parent code and reusing the SM 18/19/20 submodules.

**Architecture:** One new standalone module `src/svcv4_model/exon_deletion.py` mirroring `nonsense.py` / `frameshift.py`. Permissive all-optional models, `ConfigDict(extra="forbid")`, `from __future__ import annotations`. `ExonDeletionAssessment` reuses `PfdParentCode` (NUL/CDS), `MechanismExonRelevanceEvidence`, `FunctionalAssayEvidence`, and `InformativeVariantsEvidence`, and adds a typed `ExonDeletionPredictiveEvidence`. Standalone PFD payload — no `Case`, no `Workflow` enum entry; `case-model.md` untouched. Two new committed JSON schemas (one per BaseModel); the StrEnum gets none. Scoring documented, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv`, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-20-exon-deletion-workflow-design.md` (committed on this branch).

**Branch:** `feat/pfd-exon-deletion` (checked out; spec committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/exon_deletion.py` | The workflow: 1 enum + 2 models | Create |
| `src/svcv4_model/__init__.py` | Export the three new public names | Modify |
| `tests/test_exon_deletion.py` | Unit tests | Create |
| `schemas/json/ExonDeletionAssessment.schema.json` | Generated | Generate + `git add` |
| `schemas/json/ExonDeletionPredictiveEvidence.schema.json` | Generated | Generate + `git add` |
| `docs/workflows/pfd/exon-deletion.md` | New workflow page | Create |
| `mkdocs.yml` | Add the new page to the PFD nav | Modify |
| `docs/workflows/pfd/index.md` | Add the workflow + bump count Six→Seven | Modify |
| `docs/reference/spec-alignment.md` | SM 13 row → modeled | Modify |
| `docs/reference/known-gaps.md` | "Full PFD modeling" row → this workflow done | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.ExonDeletionAssessment` | Modify |

---

## Chunk 1: Exon Deletion workflow module, export, schemas, docs

### Task 1: Create the `exon_deletion.py` module (TDD)

**Files:**
- Create: `src/svcv4_model/exon_deletion.py`
- Create: `tests/test_exon_deletion.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_exon_deletion.py` (imports from `svcv4_model.exon_deletion`, which doesn't exist yet → collection fails):

```python
"""Tests for the SVCv4 Single/Multi-Exon Deletion (NUL_/CDS_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.exon_deletion import (
    ExonDeletionAssessment,
    ExonDeletionOutcome,
    ExonDeletionPredictiveEvidence,
)
from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


def _maximal_assessment() -> ExonDeletionAssessment:
    return ExonDeletionAssessment(
        prediction_outcome=ExonDeletionOutcome.WHOLE_GENE,
        parent_code=PfdParentCode.NUL,
        predictive=ExonDeletionPredictiveEvidence(
            basis="Whole-gene deletion (LoF)",
            initial_points=10.0,
            protein_fraction_removed=1.0,
            alternative_start_functional=False,
            adjusted_points=10.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.ALL,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000131",
                    classification=VariantClassification.PATHOGENIC,
                )
            ]
        ),
        prd_points=10.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_fxn_combined=10.0,
        parent_total=10.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = ExonDeletionAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = ExonDeletionAssessment()
    assert empty.prediction_outcome is None
    assert empty.parent_code is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.parent_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        ExonDeletionAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        ExonDeletionPredictiveEvidence(not_a_field=1)


def test_prediction_outcome_values_round_trip() -> None:
    for outcome in ExonDeletionOutcome:
        assert ExonDeletionAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_parent_code_accepts_nul_and_cds() -> None:
    for code in (PfdParentCode.NUL, PfdParentCode.CDS):
        assert ExonDeletionAssessment(parent_code=code).parent_code is code


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "ExonDeletionAssessment",
        "ExonDeletionOutcome",
        "ExonDeletionPredictiveEvidence",
    ):
        assert name in svcv4_model.__all__
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_exon_deletion.py -q`
Expected: collection **ERROR** — `ModuleNotFoundError: No module named 'svcv4_model.exon_deletion'`.

- [ ] **Step 3: Create the module**

Create `src/svcv4_model/exon_deletion.py` with exactly this content (from spec §5.1; longest line under 100):

```python
"""SVCv4 Single/Multi-Exon Deletion variants workflow (SM 13).

Deletions of one or more exons up to an entire single gene resolve to a NUL_ or
CDS_ parent code via one of six branches selected by a decision tree (whole-gene? /
includes the first coding exon? / NMD predicted? / alternative in-frame start codon
and its functionality). All six run the same pipeline — predictive (PRD) →
functional (FXN, SM 20) → informative (INF, SM 19) → parent total — with the SM 18
mechanism/exon matrix applied to the predictive points (mechanism-only for the
whole-gene branch). This module captures the analyst's inputs; the scoring is
documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class ExonDeletionOutcome(StrEnum):
    """Which of the six exon-deletion branches applies to the VBC (SM 13)."""

    WHOLE_GENE = "WHOLE_GENE"
    SUBGENIC_NMD = "SUBGENIC_NMD"
    SUBGENIC_NO_NMD = "SUBGENIC_NO_NMD"
    START_CODON_NO_ALT_START = "START_CODON_NO_ALT_START"
    START_CODON_ALT_START_UNPROVEN = "START_CODON_ALT_START_UNPROVEN"
    START_CODON_ALT_START_FUNCTIONAL = "START_CODON_ALT_START_FUNCTIONAL"


class ExonDeletionPredictiveEvidence(BaseModel):
    """The exon-deletion predictive (PRD) step of a deletion branch (SM 13).

    Whole-gene starts at +10.0; the NMD / start-exon branches at +6.0; the no-NMD
    and unproven-alt-start branches derive initial points from the fraction of
    protein removed; the functional-alt-start branch starts at −1.0. Positive points
    are reduced by the SM 18 matrix (mechanism-only for whole-gene).
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None, description="Predictive basis (e.g. whole-gene LoF; NMD; % protein lost)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial PRD points before the SM 18 adjustment."
    )
    protein_fraction_removed: float | None = Field(
        default=None,
        description="Fraction of protein removed (the violet/blue initial-points table).",
    )
    alternative_start_functional: bool | None = Field(
        default=None,
        description="Demonstrated functional alternative in-frame start (the grey branch).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class ExonDeletionAssessment(BaseModel):
    """A single/multi-exon deletion (NUL_/CDS_) assessment (SM 13).

    One entity for all six branches, parameterized by ``prediction_outcome``; reuses
    the SM 18/19/20 submodules and the shared ``PfdParentCode`` (NUL/CDS). Permissive
    superset; the per-branch pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: ExonDeletionOutcome | None = Field(
        default=None, description="Which of the six exon-deletion branches applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL or CDS per branch)."
    )
    predictive: ExonDeletionPredictiveEvidence | None = Field(
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
        default=None, description="Capped parent-code total for this branch."
    )
```

- [ ] **Step 4: Format + lint the new files**

Run: `uv run ruff format src/svcv4_model/exon_deletion.py tests/test_exon_deletion.py && uv run ruff check --fix src/svcv4_model/exon_deletion.py tests/test_exon_deletion.py`
Expected: `ruff format` reports files unchanged (or reformats trivially); `ruff check --fix` clean.

- [ ] **Step 5: Run the tests — expect only the package-root import test to fail**

Run: `uv run pytest tests/test_exon_deletion.py -q`
Expected: `test_importable_from_package_root` **FAILS** (names not yet in `svcv4_model.__all__`); all other tests **PASS** (they import from `svcv4_model.exon_deletion` directly).

- [ ] **Step 6: Commit the module + tests**

```bash
git add src/svcv4_model/exon_deletion.py tests/test_exon_deletion.py
git commit -m "feat: add Single/Multi-Exon Deletion (NUL_/CDS_) workflow module

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Export the three names from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Add the import block**

In `src/svcv4_model/__init__.py`, add a new import block **after** `from svcv4_model.evidence_line import EvidenceLine` and **before** the `from svcv4_model.frameshift import (` block (module order: `evidence_line` < `exon_deletion` < `frameshift`):

```python
from svcv4_model.exon_deletion import (
    ExonDeletionAssessment,
    ExonDeletionOutcome,
    ExonDeletionPredictiveEvidence,
)
```

- [ ] **Step 2: Add the three names to `__all__`, in sorted position**

Insert the three strings **between `"EvidenceLine"` and `"ExonRelevance"`** (`Evidence` < `ExonD` < `ExonR`):

```python
    "EvidenceLine",
    "ExonDeletionAssessment",
    "ExonDeletionOutcome",
    "ExonDeletionPredictiveEvidence",
    "ExonRelevance",
```

- [ ] **Step 3: Verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: the import block is isort-sorted (the `__all__` list is already correct from Step 2 — ruff does not reorder it); both clean.

- [ ] **Step 4: Run the full Exon Deletion test file — all green now**

Run: `uv run pytest tests/test_exon_deletion.py -q`
Expected: **all tests PASS**, including `test_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export Exon Deletion workflow from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Regenerate and commit the JSON schemas

**Files:**
- Generate: `schemas/json/ExonDeletionAssessment.schema.json`
- Generate: `schemas/json/ExonDeletionPredictiveEvidence.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: **two new** files appear (the two BaseModels). The StrEnum gets none. Existing schema files (including the reused submodules) are unchanged.

- [ ] **Step 2: Sanity-check the top-level assessment schema**

Run: `uv run python -c "import json; d=json.load(open('schemas/json/ExonDeletionAssessment.schema.json')); print(sorted(d.get('\$defs', {}).keys()))"`
Expected: `$defs` include `ExonDeletionPredictiveEvidence`, `ExonDeletionOutcome`, `PfdParentCode`, `MechanismExonRelevanceEvidence`, `FunctionalAssayEvidence`, `InformativeVariantsEvidence` (and their transitively-nested defs).

- [ ] **Step 3: Confirm `git status` shows exactly two new untracked files**

Run: `git status --porcelain schemas/json`
Expected: two `??` lines for the two new files only. **No modifications** to any existing schema. If any existing schema shows modified, stop and investigate.

- [ ] **Step 4: Verify the drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`.

- [ ] **Step 5: `git add` the two new schemas and commit**

```bash
git add schemas/json/ExonDeletionAssessment.schema.json \
        schemas/json/ExonDeletionPredictiveEvidence.schema.json
git commit -m "chore: generate Exon Deletion workflow JSON schemas

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Documentation

**Files:**
- Create: `docs/workflows/pfd/exon-deletion.md`
- Modify: `mkdocs.yml`
- Modify: `docs/workflows/pfd/index.md`
- Modify: `docs/reference/spec-alignment.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`

- [ ] **Step 1: Create the Exon Deletion workflow page**

Create `docs/workflows/pfd/exon-deletion.md`:

```markdown
# Single/Multi-Exon Deletion variants (`NUL_` / `CDS_`)

**Single- or multi-exon deletions** range from a single exon up to an entire single
gene (the sequence ontology calls these "transcript ablation"). SVCv4 (Supplementary
Material 13) routes each VBC down **one** of six branches, selected by a decision
tree — whole-gene? / includes the first coding (start) exon? / NMD predicted? /
alternative in-frame start codon and its functionality. Each branch resolves to a
parent code — `NUL_` or `CDS_` — via the same pipeline: **PRD** (predictive) →
**FXN** (functional, SM 20) → **INF** (informative, SM 19) → the capped parent total.
Modeled as one `ExonDeletionAssessment`
(`prediction_outcome` = `ExonDeletionOutcome`); each step is **documented, not
computed**.

!!! note "Modeled here — inputs captured"

    Both models (`ExonDeletionAssessment`, `ExonDeletionPredictiveEvidence`) capture
    the analyst's inputs; the scoring is documented, not computed.

| Branch (`prediction_outcome`) | Condition | Parent code | PRD initial | Parent total |
|---|---|---|---|---|
| `WHOLE_GENE` (yellow) | whole-gene deletion | `NUL_` | `+10.0` | `−8.0 to +10.0` |
| `SUBGENIC_NMD` (orange) | subgenic, not first exon, NMD | `NUL_` | `+6.0` | `−8.0 to +10.0` |
| `SUBGENIC_NO_NMD` (violet) | subgenic, not first exon, no NMD | `CDS_` | `0.0 to +6.0` | `−8.0 to +10.0` |
| `START_CODON_NO_ALT_START` (green) | includes start exon, no alt-start | `NUL_` | `+6.0` | `−8.0 to +10.0` |
| `START_CODON_ALT_START_UNPROVEN` (blue) | includes start, unproven alt-start | `CDS_` | `0.0 to +6.0` | `−8.0 to +10.0` |
| `START_CODON_ALT_START_FUNCTIONAL` (grey) | includes start, functional alt-start | `CDS_` | `−1.0` | `−8.0 to 0.0` |

The parent code reuses `PfdParentCode` (`NUL` / `CDS`).

## Predictive (`*_PRD_`)

The **whole-gene (yellow)** branch awards a fixed **+10.0**, then applies the SM 18
matrix **mechanism-only** — the exon-relevance axis is *removed* because the VBC is
the entire gene. The **NMD (orange)** and **start-exon-no-alt (green)** branches
award a fixed **+6.0**, then the full SM 18 matrix. The **no-NMD (violet)** and
**unproven-alt-start (blue)** branches read `0.0 to +6.0` from a table keyed on the
fraction of protein removed (`protein_fraction_removed`) or critical-domain loss —
violet applies the criteria strictly in order, blue may take the highest applicable —
then the SM 18 matrix. The **functional-alt-start (grey)** branch awards a fixed
**−1.0** (the alternative start yields normal function, `alternative_start_functional`)
and **skips** the SM 18 matrix.

## Functional (`*_FXN_`) and informative (`*_INF_`)

`FXN` reuses the generic [Functional Assays](index.md#functional-assays-modeled-inputs)
module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0` — **capped `−8.0 to 0.0`
(benignity-only) on the grey path**. `INF` reuses the generic
[Informative Variants](index.md#informative-variants-modeled-inputs) module
(`InformativeVariantsEvidence`, SM 19): a variant deleting a similarly altered/removed
region (or, for the NMD paths, a same-exon PTC) — +2.0 first P / +1.0 first LP / +1.0
each additional (negatives for B/LB), VUS → 0.0, coded `−8.0 to +8.0` — **grey INF is
benignity-only (`−8.0 to 0.0`)**. For whole-gene, subgenic P/LP deletions count for
pathogenicity but subgenic B/LB deletions do not count for benignity.

## Held combined value and the parent total

Per SM 13, the model records **both** the separate coded values and the one held
`PRD + FXN` combined value (`prd_fxn_combined`, no distinct code) — capped `−8.0 to
+10.0` (the `NUL_` paths), `−8.0 to +9.0` (violet / blue), or `−8.0 to 0.0` (grey).
The parent total (`parent_total`) is coded `NUL_ −8.0 to +10.0` (yellow / orange /
green), `CDS_ −8.0 to +10.0` (violet / blue), or `CDS_ −8.0 to 0.0` (grey).

*(SM 13 has a source typo: the whole-gene no-functional-data code reads `SPL_FXN_ND`;
the correct code is `NUL_FXN_ND`.)*

## Out of scope

Three situations are handled elsewhere and are **not modeled** here: multi-gene
deletions (→ the CNV recommendations), deletions smaller than an exon (→
[In-Frame InDel](inframe-indel.md) SM 10 / [Frameshift](frameshift.md) SM 9), and
deletions flanking a single exon-intron boundary (→ [Canonical Splice](canonical-splice.md)
SM 11). Gain-of-function effects are not addressed.
```

- [ ] **Step 2: Add the page to the mkdocs nav**

In `mkdocs.yml`, under the PFD nav section, add the page after Intronic & Synonymous. Change:

```yaml
          - Canonical Splice (SPL_): workflows/pfd/canonical-splice.md
          - Intronic & Synonymous (SPL_): workflows/pfd/intronic-synonymous.md
```

to:

```yaml
          - Canonical Splice (SPL_): workflows/pfd/canonical-splice.md
          - Intronic & Synonymous (SPL_): workflows/pfd/intronic-synonymous.md
          - Exon Deletion (NUL_/CDS_): workflows/pfd/exon-deletion.md
```

- [ ] **Step 3: Add the workflow + bump the count in `pfd/index.md`**

In `docs/workflows/pfd/index.md`, replace the closing paragraph:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). Six
per-variant-type workflows are modeled: the full [Missense](missense.md) workflow
(the `MIS_` amino-acid path, the `SPL_` splice paths, and the `MIS_`-vs-`SPL_`
comparison), the [Nonsense](nonsense.md) workflow (`NUL_`/`CDS_`, three branches),
the [Frameshift](frameshift.md) workflow (`NUL_`/`CDS_`, five branches), the
[In-Frame InDel](inframe-indel.md) workflow (`CDS_`, two branches), the
[Canonical Splice](canonical-splice.md) workflow (`SPL_`, five color paths), and the
[Intronic & Synonymous](intronic-synonymous.md) workflow (`SPL_`, five splice paths).
The remaining variant-type workflows and Determining Critical Amino Acids (SM 7) are
still to come.
```

with:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). Seven
per-variant-type workflows are modeled: the full [Missense](missense.md) workflow
(the `MIS_` amino-acid path, the `SPL_` splice paths, and the `MIS_`-vs-`SPL_`
comparison), the [Nonsense](nonsense.md) workflow (`NUL_`/`CDS_`, three branches),
the [Frameshift](frameshift.md) workflow (`NUL_`/`CDS_`, five branches), the
[In-Frame InDel](inframe-indel.md) workflow (`CDS_`, two branches), the
[Canonical Splice](canonical-splice.md) workflow (`SPL_`, five color paths), the
[Intronic & Synonymous](intronic-synonymous.md) workflow (`SPL_`, five splice paths),
and the [Exon Deletion](exon-deletion.md) workflow (`NUL_`/`CDS_`, six branches). The
remaining variant-type workflows and Determining Critical Amino Acids (SM 7) are
still to come.
```

- [ ] **Step 4: Update the SM 13 row in `spec-alignment.md`**

In `docs/reference/spec-alignment.md`, replace the SM 13 row:

```markdown
| 13 | [Exon Deletion Variants](https://docs.google.com/document/d/1354VHASLCzQ-73Ha1-TdVL5t7RsVzq-Hgl1tqmuLQlk/edit) | `NUL_*`, `CDS_*` | Not yet modeled |
```

with:

```markdown
| 13 | [Exon Deletion Variants](https://docs.google.com/document/d/1354VHASLCzQ-73Ha1-TdVL5t7RsVzq-Hgl1tqmuLQlk/edit) | `NUL_*`, `CDS_*` | **Modeled (inputs)** — `ExonDeletionAssessment` captures the six branches (whole-gene / subgenic ± NMD / start-codon ± alternative start), resolving to `NUL_`/`CDS_`, reusing SM 18/19/20; the criticality axis (SM 7) is deferred. See [Exon Deletion](../workflows/pfd/exon-deletion.md) |
```

- [ ] **Step 5: Update the "Full PFD modeling" row in `known-gaps.md`**

In `docs/reference/known-gaps.md`, replace the segment `and the **Intronic & Synonymous workflow** (`IntronicSynonymousAssessment`, five splice paths → `SPL_`, reusing the shared `Splice*` vocabulary) are now modeled (inputs only).` with:

```markdown
the **Intronic & Synonymous workflow** (`IntronicSynonymousAssessment`, five splice paths → `SPL_`), and the **Exon Deletion workflow** (`ExonDeletionAssessment`, six branches → `NUL_`/`CDS_`) are now modeled (inputs only).
```

(Locate the row by grepping `Full PFD modeling`; swap the Intronic-tail clause for the two-workflow clause above, leaving the rest of the row intact.)

- [ ] **Step 6: Append the model.md entry**

In `docs/reference/model.md`, after the **last** `::: svcv4_model.IntronicSynonymousAssessment` entry, append:

```markdown

---

::: svcv4_model.ExonDeletionAssessment
```

- [ ] **Step 7: Build the docs strictly**

Run: `uv run mkdocs build --strict 2>&1 | tail -20`
Expected: `Documentation built…` with **no** WARNING lines. The new page must be in the nav (Step 2). The `index.md#…` anchors and the `inframe-indel.md` / `frameshift.md` / `canonical-splice.md` links all resolve; if strict flags a broken link, read the warning and fix it. (Use inline notes, not `[^...]` footnotes — the repo does not enable the `footnotes` extension.)

- [ ] **Step 8: Commit the docs**

```bash
git add docs/workflows/pfd/exon-deletion.md mkdocs.yml docs/workflows/pfd/index.md \
        docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: document the Single/Multi-Exon Deletion (NUL_/CDS_) workflow

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Full quality gates

**Files:** none (verification only)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -q`
Expected: all tests pass (existing suite + new `tests/test_exon_deletion.py`).

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

- `ExonDeletionAssessment`, `ExonDeletionOutcome`, `ExonDeletionPredictiveEvidence` importable from `svcv4_model`, all-optional, `extra="forbid"`.
- Two new committed JSON schemas; no existing schema changed; `case-model.md` untouched.
- New `pfd/exon-deletion.md` page in the nav; PFD overview lists it (count bumped Six→Seven); spec-alignment/known-gaps/model docs updated.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR, run the `code-review` skill on the diff, address findings, then merge on request. The remaining variant-type workflows (Exon Duplication SM 14, Start/Stop loss SM 15/16) and SM 7 Critical Amino Acids remain on the backlog.
