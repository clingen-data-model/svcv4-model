# Intronic & Synonymous Variants (`SPL_`) Workflow Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the SVCv4 Intronic & Synonymous variants workflow (SM 12) as `IntronicSynonymousAssessment` — a capture-only entity field-identical to `CanonicalSpliceAssessment`, reusing the shared `Splice*` vocabulary from `splice.py` (its third consumer).

**Architecture:** One new standalone module `src/svcv4_model/intronic_synonymous.py` holding `IntronicSynonymousAssessment` (the five-path `SPL_` splice pipeline, always `SPL_`, no `parent_code`), importing `SplicePredictionOutcome` / `SplicePredictiveEvidence` / `SpliceAssayEvidence` from `splice.py` plus SM 18/19/20. Permissive all-optional, `ConfigDict(extra="forbid")`, `from __future__ import annotations`. Standalone PFD payload — no `Case`, no `Workflow` enum entry; `case-model.md` untouched. One new committed JSON schema; no existing schema changes. Scoring documented, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv`, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-20-intronic-synonymous-workflow-design.md` (committed on this branch).

**Branch:** `feat/pfd-intronic-synonymous` (checked out; spec committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/intronic_synonymous.py` | `IntronicSynonymousAssessment` (SM 12) | Create |
| `src/svcv4_model/__init__.py` | Export the new name | Modify |
| `tests/test_intronic_synonymous.py` | Unit tests | Create |
| `schemas/json/IntronicSynonymousAssessment.schema.json` | Generated (one new file) | Generate + `git add` |
| `docs/workflows/pfd/intronic-synonymous.md` | New workflow page | Create |
| `mkdocs.yml` | Add the new page to the PFD nav | Modify |
| `docs/workflows/pfd/index.md` | Add the workflow + bump count Five→Six | Modify |
| `docs/reference/spec-alignment.md` | SM 12 row → modeled (drop the NCG assumption) | Modify |
| `docs/reference/known-gaps.md` | "Full PFD modeling" row → this workflow done | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.IntronicSynonymousAssessment` | Modify |
| `src/svcv4_model/splice.py` | Update the **module docstring only** (schema-safe) | Modify |

---

## Chunk 1: Intronic & Synonymous workflow module, export, schema, docs

### Task 1: Create the `intronic_synonymous.py` module (TDD)

**Files:**
- Create: `src/svcv4_model/intronic_synonymous.py`
- Create: `tests/test_intronic_synonymous.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_intronic_synonymous.py` (imports from `svcv4_model.intronic_synonymous`, which doesn't exist yet → collection fails):

```python
"""Tests for the SVCv4 Intronic & Synonymous variants (SPL_) workflow model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    VariantClassification,
)
from svcv4_model.intronic_synonymous import IntronicSynonymousAssessment
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)


def _maximal_assessment() -> IntronicSynonymousAssessment:
    return IntronicSynonymousAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(
            splice_predictor=SplicePredictor.SPLICEAI,
            initial_points=3.0,
            adjusted_points=3.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(
            exon_relevance=ExonRelevance.ALL,
        ),
        splice_assay=SpliceAssayEvidence(
            assay_type="RNAseq",
            result=SpliceAssayResult.NEAR_COMPLETE_OR_COMPLETE,
            calibrated=False,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(
            variants=[
                InformativeVariant(
                    id="clinvar:VCV000000121",
                    classification=VariantClassification.PATHOGENIC,
                )
            ]
        ),
        prd_points=3.0,
        spa_points=3.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_spa_combined=6.0,
        prd_spa_fxn_combined=8.0,
        spl_total=9.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = IntronicSynonymousAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = IntronicSynonymousAssessment()
    assert empty.prediction_outcome is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.splice_assay is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.spl_total is None


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        IntronicSynonymousAssessment(not_a_field=1)


def test_importable_from_package_root() -> None:
    import svcv4_model

    assert "IntronicSynonymousAssessment" in svcv4_model.__all__
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_intronic_synonymous.py -q`
Expected: collection **ERROR** — `ModuleNotFoundError: No module named 'svcv4_model.intronic_synonymous'`.

- [ ] **Step 3: Create the module**

Create `src/svcv4_model/intronic_synonymous.py` with exactly this content (from spec §5.1; field-identical to `CanonicalSpliceAssessment`; longest line under 100):

```python
"""SVCv4 Intronic & Synonymous variants workflow (SM 12).

Intronic variants (excluding the essential ±1,2 GT/AG splice sites) and synonymous
variants are evaluated for their splicing potential and resolve to the SPL_ parent
code via one of five paths (NMD / frameshift-no-NMD / no-frameshift / uncertain /
unlikely), each running the shared splice pipeline — predictive (SPL_PRD) → splice
assay (SPL_SPA) → functional (SPL_FXN, SM 20) → informative (SPL_INF, SM 19) → the
capped SPL_ total. Field-identical to the canonical splice assessment (SM 11); the
SM 12 point values track the missense splice half (SM 6) and are documented, not
computed.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
)


class IntronicSynonymousAssessment(BaseModel):
    """An intronic / synonymous variant (SPL_) assessment (SM 12).

    One entity for all five splice paths, parameterized by ``prediction_outcome``;
    reuses the shared splice vocabulary and the SM 18/19/20 submodules. Permissive
    superset; the per-path pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: SplicePredictionOutcome | None = Field(
        default=None, description="Which of the five splice prediction paths applies."
    )
    predictive: SplicePredictiveEvidence | None = Field(
        default=None, description="The SPL_PRD splice-prediction step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    splice_assay: SpliceAssayEvidence | None = Field(
        default=None, description="SM 12 splice-assay evidence (SPL_SPA)."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (SPL_FXN)."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (SPL_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded SPL_PRD point value.")
    spa_points: float | None = Field(default=None, description="Coded SPL_SPA point value.")
    fxn_points: float | None = Field(default=None, description="Coded SPL_FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded SPL_INF point value.")
    prd_spa_combined: float | None = Field(
        default=None, description="Held SPL_PRD + SPL_SPA combined value."
    )
    prd_spa_fxn_combined: float | None = Field(
        default=None, description="Held SPL_PRD + SPL_SPA + SPL_FXN combined value."
    )
    spl_total: float | None = Field(
        default=None, description="Capped SPL_ parent-code total for this path."
    )
```

- [ ] **Step 4: Format + lint the new files**

Run: `uv run ruff format src/svcv4_model/intronic_synonymous.py tests/test_intronic_synonymous.py && uv run ruff check --fix src/svcv4_model/intronic_synonymous.py tests/test_intronic_synonymous.py`
Expected: `ruff format` reports files unchanged (or reformats trivially); `ruff check --fix` clean.

- [ ] **Step 5: Run the tests — expect only the package-root import test to fail**

Run: `uv run pytest tests/test_intronic_synonymous.py -q`
Expected: `test_importable_from_package_root` **FAILS** (name not yet in `svcv4_model.__all__`); all other tests **PASS** (they import from `svcv4_model.intronic_synonymous` directly).

- [ ] **Step 6: Commit the module + tests**

```bash
git add src/svcv4_model/intronic_synonymous.py tests/test_intronic_synonymous.py
git commit -m "feat: add Intronic & Synonymous variants (SPL_) workflow module

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Export `IntronicSynonymousAssessment` from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Add the import**

In `src/svcv4_model/__init__.py`, add the import **after** `from svcv4_model.inputs import MDE, VBC` and **before** `from svcv4_model.mechanism import (` (module order: `inputs` < `intronic_synonymous` < `mechanism`):

```python
from svcv4_model.intronic_synonymous import IntronicSynonymousAssessment
```

- [ ] **Step 2: Add the name to `__all__`, in sorted position**

Insert `"IntronicSynonymousAssessment"` **between `"InframeIndelPredictiveEvidence"` and `"ManeStatus"`** (`Inframe` < `Intronic` < `Mane`):

```python
    "InframeIndelPredictiveEvidence",
    "IntronicSynonymousAssessment",
    "ManeStatus",
```

- [ ] **Step 3: Verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: both clean.

- [ ] **Step 4: Run the full test file — all green now**

Run: `uv run pytest tests/test_intronic_synonymous.py -q`
Expected: **all tests PASS**, including `test_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export Intronic & Synonymous workflow from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Regenerate and commit the JSON schema

**Files:**
- Generate: `schemas/json/IntronicSynonymousAssessment.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: **one new** file — `IntronicSynonymousAssessment.schema.json`. No existing schema changes (the shared `Splice*` schemas are untouched).

- [ ] **Step 2: Confirm `git status` shows exactly one new untracked file**

Run: `git status --porcelain schemas/json`
Expected: one `??` line for `IntronicSynonymousAssessment.schema.json` only. **No modifications** to any existing schema. If any existing schema shows modified, stop and investigate.

- [ ] **Step 3: Verify the drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN` (the new schema is untracked, so `git diff --quiet` ignores it; `case-model.md` unchanged).

- [ ] **Step 4: `git add` the new schema and commit**

```bash
git add schemas/json/IntronicSynonymousAssessment.schema.json
git commit -m "chore: generate Intronic & Synonymous workflow JSON schema

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Documentation

**Files:**
- Create: `docs/workflows/pfd/intronic-synonymous.md`
- Modify: `mkdocs.yml`
- Modify: `docs/workflows/pfd/index.md`
- Modify: `docs/reference/spec-alignment.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`
- Modify: `src/svcv4_model/splice.py` (module docstring only)

- [ ] **Step 1: Create the Intronic & Synonymous workflow page**

Create `docs/workflows/pfd/intronic-synonymous.md`:

```markdown
# Intronic & Synonymous variants (`SPL_`)

**Intronic variants** (SNVs / indels in an intron, *excluding* the essential ±1,2
`GT`/`AG` splice sites) and **synonymous variants** are both evaluated for their
**splicing** potential — synonymous variants because a distant splice disruption can
be pathogenic even when the variant itself is silent. SVCv4 (Supplementary Material
12) routes each VBC down **one** of five paths — the *same five* the
[Missense](missense.md) and [Canonical Splice](canonical-splice.md) flows use — all
resolving to the **`SPL_`** parent code via the shared pipeline: **SPL_PRD**
(prediction) → **SPL_SPA** (splice assay) → **SPL_FXN** (functional, SM 20) →
**SPL_INF** (informative, SM 19) → the capped `SPL_` total. Modeled as one
`IntronicSynonymousAssessment` (`prediction_outcome` = `SplicePredictionOutcome`);
each step is **documented, not computed**.

!!! note "Modeled here — inputs captured"

    `IntronicSynonymousAssessment` reuses the shared splice vocabulary
    (`SplicePredictionOutcome`, `SplicePredictiveEvidence`, `SpliceAssayEvidence`)
    and is field-identical to `CanonicalSpliceAssessment`. Only the point values
    differ (documented below); the structure is shared.

A ±1,2 dinucleotide variant whose wild-type sequence is **not** `GT`/`AG` uses *this*
flow rather than Canonical Splice (in-silico tools are less reliable for non-GT/AG
sites). Intronic genomic rearrangements / CNVs and gain-of-function effects are out
of scope here.

## Path selection (SpliceAI trichotomy)

The first decision uses an in-silico splice predictor (SpliceAI / Pangolin) chosen
consistently. Using SpliceAI's SVI-calibrated thresholds: **likely** (score > 0.2),
**uncertain** (0.1–0.2), **unlikely** (< 0.1). A high score with an ambiguous
consequence (e.g. near-equal normal-loss and cryptic-gain deltas) is treated as
**uncertain**.

| Path (`prediction_outcome`) | Splice prediction | SPL_PRD initial | SPL_ total |
|---|---|---|---|
| `NMD_PREDICTED` (yellow) | likely, frameshift + NMD | `+3.0` | `−8.0 to +10.0` |
| `FRAMESHIFT_NO_NMD` (upper orange) | likely, frameshift, no NMD | `−1.0 to +3.0` | `−8.0 to +10.0` |
| `SPLICE_NO_FRAMESHIFT` (lower orange) | likely, no frameshift, no NMD | `−1.0 to +3.0` | `−8.0 to +10.0` |
| `UNCERTAIN` (blue) | uncertain | `0.0` | `−8.0 to +8.0` |
| `UNLIKELY` (lilac) | unlikely | `−1.0` | `−8.0 to 0.0` |

### Predictive (`SPL_PRD_`)

Positive initial points (yellow/orange) are reduced by the
[Molecular Mechanism & Exon Relevance](index.md#molecular-mechanism-exon-relevance-modeled-inputs)
matrix (SM 18); blue and lilac skip it. The yellow branch awards a fixed **+3.0** for
a predicted NMD event — lower than a nonsense variant's, reflecting splice-prediction
uncertainty. The orange branches read `−1.0 to +3.0` from a critical-amino-acid table
(the lower-orange path may fold in an in-frame in-silico deletion tool, `+0.5` /
`−0.5`).

### Splice assay (`SPL_SPA_`)

`SpliceAssayEvidence` captures RNA / minigene / RT-PCR evidence. Its semantics **scale
up** the SPL_PRD evidence (the missense-splice direction): for yellow it **adds** a
fraction of SPL_PRD (near-complete → +100%, substantial → +50%, incomplete/none → 0);
for orange it **doubles** (near-complete → +100%, substantial → +50%; held PRD+SPA
`−1.0 to +6.0`); for blue it is **additive** (`−2.0 to +2.0`); for lilac it adds
**benignity** (`−2.0 to 0.0`, held PRD+SPA `−3.0 to 0.0`).

### Functional (`SPL_FXN_`) and informative (`SPL_INF_`)

`SPL_FXN` reuses the generic [Functional Assays](index.md#functional-assays-modeled-inputs)
module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0` (capped `−8.0 to 0.0` on the
lilac path). `SPL_INF` reuses the generic
[Informative Variants](index.md#informative-variants-modeled-inputs) module
(`InformativeVariantsEvidence`, SM 19): +2.0 first P / +1.0 first LP / +1.0 each
additional (negatives for B/LB), coded `−8.0 to +8.0` — the **lilac path restricts it
to B/LB only**. Informative variants must have the same predicted splicing impact,
and (for pathogenicity) a VBC prediction of similar-or-higher strength.

### Held combined values and the `SPL_` total

Per SM 12, the model records **both** the separate coded values and the two held
combined values (`prd_spa_combined` = SPL_PRD + SPL_SPA; `prd_spa_fxn_combined` =
SPL_PRD + SPL_SPA + SPL_FXN), then the capped parent `SPL_` total (`spl_total`),
whose range depends on the path (table above).
```

- [ ] **Step 2: Add the page to the mkdocs nav**

In `mkdocs.yml`, under the PFD nav section, add the page after Canonical Splice. Change:

```yaml
          - In-Frame InDel (CDS_): workflows/pfd/inframe-indel.md
          - Canonical Splice (SPL_): workflows/pfd/canonical-splice.md
```

to:

```yaml
          - In-Frame InDel (CDS_): workflows/pfd/inframe-indel.md
          - Canonical Splice (SPL_): workflows/pfd/canonical-splice.md
          - Intronic & Synonymous (SPL_): workflows/pfd/intronic-synonymous.md
```

- [ ] **Step 3: Add the workflow + bump the count in `pfd/index.md`**

In `docs/workflows/pfd/index.md`, replace the closing paragraph:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). Five
per-variant-type workflows are modeled: the full [Missense](missense.md) workflow
(the `MIS_` amino-acid path, the `SPL_` splice paths, and the `MIS_`-vs-`SPL_`
comparison), the [Nonsense](nonsense.md) workflow (`NUL_`/`CDS_`, three branches),
the [Frameshift](frameshift.md) workflow (`NUL_`/`CDS_`, five branches), the
[In-Frame InDel](inframe-indel.md) workflow (`CDS_`, two branches), and the
[Canonical Splice](canonical-splice.md) workflow (`SPL_`, five color paths). The
remaining variant-type workflows and Determining Critical Amino Acids (SM 7) are
still to come.
```

with:

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

- [ ] **Step 4: Update the SM 12 row in `spec-alignment.md`**

In `docs/reference/spec-alignment.md`, replace the SM 12 row:

```markdown
| 12 | [Intronic & Synonymous Variants](https://docs.google.com/document/d/1mqZnp72N3IC3adenRrVVufOuqkgPAgkD_D5vNmb32gc/edit) | `SPL_*`/`NCG_*` (assumed) | Not yet modeled |
```

with:

```markdown
| 12 | [Intronic & Synonymous Variants](https://docs.google.com/document/d/1mqZnp72N3IC3adenRrVVufOuqkgPAgkD_D5vNmb32gc/edit) | `SPL_*` | **Modeled (inputs)** — `IntronicSynonymousAssessment` captures the five splice paths → `SPL_`, reusing the shared `Splice*` vocabulary + SM 18/19/20; the criticality axis (SM 7) is deferred. See [Intronic & Synonymous](../workflows/pfd/intronic-synonymous.md) |
```

- [ ] **Step 5: Update the "Full PFD modeling" row in `known-gaps.md`**

In `docs/reference/known-gaps.md`, replace the segment `and the **Canonical Splice workflow** (`CanonicalSpliceAssessment`, five color paths → `SPL_`, reusing the shared `Splice*` vocabulary) are now modeled (inputs only).` with:

```markdown
the **Canonical Splice workflow** (`CanonicalSpliceAssessment`, five color paths → `SPL_`), and the **Intronic & Synonymous workflow** (`IntronicSynonymousAssessment`, five splice paths → `SPL_`, reusing the shared `Splice*` vocabulary) are now modeled (inputs only).
```

(Locate the row by grepping `Full PFD modeling`; the edit swaps the Canonical-Splice tail clause for the two-workflow clause above, leaving the rest of the row intact.)

- [ ] **Step 6: Append the model.md entry**

In `docs/reference/model.md`, after the **last** `::: svcv4_model.CanonicalSpliceAssessment` entry, append:

```markdown

---

::: svcv4_model.IntronicSynonymousAssessment
```

- [ ] **Step 7: Update the `splice.py` module docstring (schema-safe)**

In `src/svcv4_model/splice.py`, update the **module docstring only** (do NOT touch any class docstring or field). Replace:

```python
the Missense splice half (SM 6) and Canonical Splice variants (SM 11). They are
```

with:

```python
the Missense splice half (SM 6), Canonical Splice variants (SM 11), and Intronic &
Synonymous variants (SM 12). They are
```

- [ ] **Step 8: Build the docs strictly + verify zero schema drift from the docstring edit**

Run: `uv run python scripts/export_schemas.py && git status --porcelain schemas/json`
Expected: only `IntronicSynonymousAssessment.schema.json` is untracked (already committed in Task 3 — so if it re-appears as untracked it means it wasn't committed; otherwise empty). Crucially, **no `SplicePredictiveEvidence.schema.json` / `SpliceAssayEvidence.schema.json` modification** — the module-docstring edit does not touch per-class schemas.
Then: `uv run mkdocs build --strict 2>&1 | tail -20`
Expected: `Documentation built…` with **no** WARNING lines. (Use inline notes, not `[^...]` footnotes — the repo does not enable the `footnotes` extension. Watch for relative-link warnings in the SPEC as well; if strict flags one, backtick or reword it.)

- [ ] **Step 9: Commit the docs**

```bash
git add docs/workflows/pfd/intronic-synonymous.md mkdocs.yml docs/workflows/pfd/index.md \
        docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md \
        src/svcv4_model/splice.py
git commit -m "docs: document the Intronic & Synonymous variants (SPL_) workflow

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Full quality gates

**Files:** none (verification only)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -q`
Expected: all tests pass (existing suite + new `tests/test_intronic_synonymous.py`).

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

- `IntronicSynonymousAssessment` importable from `svcv4_model`, all-optional, `extra="forbid"`, field-identical to `CanonicalSpliceAssessment`.
- One new committed JSON schema; no existing schema changed (incl. the shared `Splice*` schemas after the module-docstring edit); `case-model.md` untouched.
- New `pfd/intronic-synonymous.md` page in the nav; PFD overview lists it (count bumped Five→Six); spec-alignment (NCG assumption dropped)/known-gaps/model docs updated; `splice.py` module docstring lists SM 12.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR, run the `code-review` skill on the diff, address findings, then merge on request. The remaining variant-type workflows (Start/Stop loss SM 15/16, Exon del/dup SM 13/14) and SM 7 Critical Amino Acids remain on the backlog.
