# Missense Amino-Acid (MIS_) Path Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the SVCv4 Missense amino-acid (`MIS_`) path (SM 6) — increment 2a — as a new capture-only Pydantic module `missense.py` composing a typed predictor, transcript relevance, the shared functional module, and the four-category Grantham informative module.

**Architecture:** One new standalone module `src/svcv4_model/missense.py` following the `pfd.py` / `population.py` precedent — permissive all-optional models, `ConfigDict(extra="forbid")`, `from __future__ import annotations`. `MissenseAminoAcidAssessment` mirrors `PfdCodeAssessment`'s shape but swaps in the missense-specific `MissensePredictiveEvidence` and `MissenseInformativeEvidence` (the four Grantham categories), while reusing `FunctionalAssayEvidence`, `ExonRelevance`, and `VariantClassification`. Standalone PFD payload — no `Case` involvement, no `Workflow` enum entry, no applicability-matrix row, so `case-model.md` and the per-workflow case views are untouched. Four new committed JSON schemas (one per BaseModel); the two StrEnums get none. Scoring is documented in prose, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv`, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-18-missense-amino-acid-path-design.md` (committed on this branch).

**Branch:** `feat/pfd-missense` (checked out; spec committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/missense.py` | The MIS_ path: 2 enums + 4 models | Create |
| `src/svcv4_model/__init__.py` | Export the six new public names | Modify |
| `tests/test_missense.py` | Unit tests (round-trip, permissive-empty, extra-forbid, enums, importable) | Create |
| `schemas/json/MissenseAminoAcidAssessment.schema.json` | Generated (embeds reused models + enums as `$defs`) | Generate + `git add` |
| `schemas/json/MissensePredictiveEvidence.schema.json` | Generated | Generate + `git add` |
| `schemas/json/MissenseInformativeVariant.schema.json` | Generated | Generate + `git add` |
| `schemas/json/MissenseInformativeEvidence.schema.json` | Generated | Generate + `git add` |
| `docs/workflows/pfd/missense.md` | New Missense workflow page (MIS path now) | Create |
| `mkdocs.yml` | Add the new page to the PFD nav section | Modify |
| `docs/workflows/pfd/index.md` | Link the first per-variant-type workflow to the new page | Modify |
| `docs/reference/spec-alignment.md` | SM 6 row → partially modeled | Modify |
| `docs/reference/known-gaps.md` | "Full PFD modeling" row → MIS path done | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.MissenseAminoAcidAssessment` | Modify |

**Note:** existing `tests/test_pfd*.py` files are untouched; the new file is `tests/test_missense.py` (no clash).

---

## Chunk 1: Missense MIS_ path module, exports, schemas, docs

### Task 1: Create the `missense.py` module (TDD)

**Files:**
- Create: `src/svcv4_model/missense.py`
- Create: `tests/test_missense.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_missense.py`. It imports from `svcv4_model.missense` (doesn't exist yet → collection fails):

```python
"""Tests for the SVCv4 Missense amino-acid (MIS_) path model."""

from __future__ import annotations

import pytest

from svcv4_model.functional import FunctionalAssayEvidence, ProteinFunctionalAssay
from svcv4_model.mechanism import ExonRelevance
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
)
from svcv4_model.informative import VariantClassification


def _maximal_assessment() -> MissenseAminoAcidAssessment:
    return MissenseAminoAcidAssessment(
        predictive=MissensePredictiveEvidence(
            predictor=MissensePredictor.REVEL,
            raw_score=0.92,
            initial_points=4.0,
            transcript_relevance=ExonRelevance.ALL,
            adjusted_points=4.0,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=MissenseInformativeEvidence(
            variants=[
                MissenseInformativeVariant(
                    id="clinvar:VCV000000021",
                    category=MissenseInfCategory.DISTINCT_AA_PATHOGENIC,
                    classification=VariantClassification.PATHOGENIC,
                    grantham_wt_to_vbc=100.0,
                    grantham_wt_to_informative=50.0,
                )
            ]
        ),
        prd_points=4.0,
        fxn_points=2.0,
        inf_points=2.0,
        prd_fxn_combined=6.0,
        mis_total=8.0,
    )


def test_assessment_round_trips_json() -> None:
    original = _maximal_assessment()
    rehydrated = MissenseAminoAcidAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_assessment_is_permissive_when_empty() -> None:
    empty = MissenseAminoAcidAssessment()
    assert empty.predictive is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.mis_total is None


def test_informative_evidence_defaults_to_empty_list() -> None:
    assert MissenseInformativeEvidence().variants == []


def test_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseAminoAcidAssessment(not_a_field=1)


def test_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissensePredictiveEvidence(not_a_field=1)


def test_informative_variant_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseInformativeVariant(not_a_field=1)


def test_informative_evidence_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseInformativeEvidence(not_a_field=1)


def test_predictor_values_round_trip() -> None:
    for predictor in MissensePredictor:
        model = MissensePredictiveEvidence(predictor=predictor)
        assert model.predictor is predictor


def test_inf_category_values_round_trip() -> None:
    for category in MissenseInfCategory:
        model = MissenseInformativeVariant(category=category)
        assert model.category is category


def test_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "MissenseAminoAcidAssessment",
        "MissenseInfCategory",
        "MissenseInformativeEvidence",
        "MissenseInformativeVariant",
        "MissensePredictiveEvidence",
        "MissensePredictor",
    ):
        assert name in svcv4_model.__all__
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_missense.py -q`
Expected: collection **ERROR** — `ModuleNotFoundError: No module named 'svcv4_model.missense'`.

- [ ] **Step 3: Create the module**

Create `src/svcv4_model/missense.py` with exactly this content (from spec §5.1; longest field description is 96 chars, under the 100 limit):

```python
"""SVCv4 Missense — amino-acid effect path (SM 6).

The "GREEN" upper path of the missense flow diagram, yielding the ``MIS_`` parent
code: a single calibrated in-silico predictor adjusted for transcript relevance
(MIS_PRD) → functional evidence (MIS_FXN, the shared SM 20 module) → the four
summable Grantham informative categories (MIS_INF) → the capped MIS_ total. The
splice paths (SPL_) and the MIS_-vs-SPL_ comparison are separate increments. This
module captures the analyst's inputs; the scoring is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import VariantClassification
from svcv4_model.mechanism import ExonRelevance


class MissensePredictor(StrEnum):
    """A calibrated in-silico missense predictor, pre-selected per VBC (SM 6)."""

    ALPHAMISSENSE = "ALPHAMISSENSE"
    BAYESDEL = "BAYESDEL"
    ESM1B = "ESM1B"
    MUTPRED2 = "MUTPRED2"
    REVEL = "REVEL"
    VARITY_R = "VARITY_R"
    VEST4 = "VEST4"
    OTHER_CALIBRATED = "OTHER_CALIBRATED"


class MissenseInfCategory(StrEnum):
    """One of the four summable MIS_INF informative-variant categories (SM 6)."""

    SAME_AA_PATHOGENIC = "SAME_AA_PATHOGENIC"
    DISTINCT_AA_PATHOGENIC = "DISTINCT_AA_PATHOGENIC"
    DISTINCT_AA_BENIGN = "DISTINCT_AA_BENIGN"
    SAME_AA_BENIGN = "SAME_AA_BENIGN"


class MissensePredictiveEvidence(BaseModel):
    """The amino-acid predictive (MIS_PRD) step: one calibrated predictor.

    Transcript relevance (ExonRelevance) reduces positive points; the molecular-
    mechanism axis is deliberately not applied on the missense amino-acid path,
    since predictors capture both loss- and gain-of-function effects.
    """

    model_config = ConfigDict(extra="forbid")

    predictor: MissensePredictor | None = Field(
        default=None, description="The single pre-selected calibrated predictor."
    )
    raw_score: float | None = Field(
        default=None, description="The predictor's raw score, if applicable."
    )
    initial_points: float | None = Field(
        default=None, description="Calibrated points before the transcript-relevance step."
    )
    transcript_relevance: ExonRelevance | None = Field(
        default=None,
        description="Exon presence across disease-relevant transcripts (All/Most/Few).",
    )
    adjusted_points: float | None = Field(
        default=None,
        description="Coded MIS_PRD points after transcript relevance (−4.0 to +4.0).",
    )


class MissenseInformativeVariant(BaseModel):
    """One MIS_INF informative variant in the same codon as the VBC (SM 6)."""

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None, description="Variant identifier (e.g. a ClinVar VCV).")
    category: MissenseInfCategory | None = Field(
        default=None, description="Which of the four summable MIS_INF categories applies."
    )
    classification: VariantClassification | None = Field(
        default=None, description="The informative variant's classification (P/LP/B/LB)."
    )
    grantham_wt_to_vbc: float | None = Field(
        default=None,
        description="Grantham distance wild-type → VBC amino acid (categories 2 & 3).",
    )
    grantham_wt_to_informative: float | None = Field(
        default=None,
        description="Grantham distance wild-type → informative amino acid (categories 2 & 3).",
    )


class MissenseInformativeEvidence(BaseModel):
    """The MIS_INF step: the summable informative variants for the VBC's codon."""

    model_config = ConfigDict(extra="forbid")

    variants: list[MissenseInformativeVariant] = Field(
        default_factory=list, description="Distinct informative variants; summed, not counted."
    )


class MissenseAminoAcidAssessment(BaseModel):
    """The missense amino-acid (MIS_) path assessment (SM 6).

    Mirrors the PFD scaffold but swaps in the missense-specific predictive step and
    the Grantham informative module, reusing the shared SM 20 functional module.
    Permissive superset; the pipeline and its caps are documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    predictive: MissensePredictiveEvidence | None = Field(
        default=None, description="The MIS_PRD amino-acid predictive step."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (MIS_FXN)."
    )
    informative: MissenseInformativeEvidence | None = Field(
        default=None, description="The four-category Grantham informative evidence (MIS_INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded MIS_PRD point value.")
    fxn_points: float | None = Field(default=None, description="Coded MIS_FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded MIS_INF point value.")
    prd_fxn_combined: float | None = Field(
        default=None, description="Held MIS_PRD + MIS_FXN combined value (−8.0 to +6.0)."
    )
    mis_total: float | None = Field(
        default=None, description="Capped MIS_ parent-code total (−8.0 to +9.0)."
    )
```

- [ ] **Step 4: Run ruff format + check --fix on the new files**

Run: `uv run ruff format src/svcv4_model/missense.py tests/test_missense.py && uv run ruff check --fix src/svcv4_model/missense.py tests/test_missense.py`
Expected: `ruff format` reports files unchanged (or reformats trivially — accept its output as canonical); `ruff check --fix` reports+fixes **I001** on the test file (the `from svcv4_model.informative import VariantClassification` line is intentionally placed out of order so isort moves it up above `mechanism`/`missense`), then exits clean. Plain `ruff check` (no `--fix`) would only *report* I001 and exit 1 — use `--fix`.

- [ ] **Step 5: Run the tests — expect only the package-root import test to fail**

Run: `uv run pytest tests/test_missense.py -q`
Expected: `test_importable_from_package_root` **FAILS** (names not yet in `svcv4_model.__all__`); all other tests **PASS** (they import from `svcv4_model.missense` directly). This isolates the remaining work to the export step.

- [ ] **Step 6: Commit the module + tests**

```bash
git add src/svcv4_model/missense.py tests/test_missense.py
git commit -m "feat: add Missense amino-acid (MIS_) path module

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Export the six names from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Add the import block**

In `src/svcv4_model/__init__.py`, add a new import block **after** the `from svcv4_model.method import Method` line and **before** the `from svcv4_model.pfd import (` block (module order: `mechanism` < `method` < `missense` < `pfd`):

```python
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
)
```

- [ ] **Step 2: Add the six names to `__all__`, in sorted position**

`__all__` is kept alphabetically sorted **by hand** — ruff does **not** sort it in this repo (`RUF022` is not enabled). Insert the six strings **between `"Method"` and `"MolecularMechanism"`** (`Method` < `Missense…` < `MolecularMechanism` because `Me` < `Mi` < `Mo`), in this exact internal order:

```python
    "Method",
    "MissenseAminoAcidAssessment",
    "MissenseInfCategory",
    "MissenseInformativeEvidence",
    "MissenseInformativeVariant",
    "MissensePredictiveEvidence",
    "MissensePredictor",
    "MolecularMechanism",
```

- [ ] **Step 3: Let ruff sort the import block and verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: the import block is isort-sorted (the `__all__` list is already correct from Step 2 — ruff will **not** reorder it); `ruff check` and `format --check` clean (exit 0).

- [ ] **Step 4: Run the full Missense test file — all green now**

Run: `uv run pytest tests/test_missense.py -q`
Expected: **all tests PASS**, including `test_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export Missense MIS_ path from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Regenerate and commit the JSON schemas

**Files:**
- Generate: `schemas/json/MissenseAminoAcidAssessment.schema.json`
- Generate: `schemas/json/MissensePredictiveEvidence.schema.json`
- Generate: `schemas/json/MissenseInformativeVariant.schema.json`
- Generate: `schemas/json/MissenseInformativeEvidence.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: **four new** files appear (the four BaseModels). The two StrEnums get none. Existing schema files (including the reused `FunctionalAssayEvidence` etc.) are unchanged.

- [ ] **Step 2: Sanity-check the top-level assessment schema**

Run: `uv run python -c "import json; d=json.load(open('schemas/json/MissenseAminoAcidAssessment.schema.json')); print(sorted(d.get('\$defs', {}).keys()))"`
Expected: `$defs` include `MissensePredictiveEvidence`, `MissenseInformativeEvidence`, `MissenseInformativeVariant`, `MissensePredictor`, `MissenseInfCategory`, `ExonRelevance`, `VariantClassification`, `FunctionalAssayEvidence` (and its nested defs). Confirms reused models embed as `$ref`/`$defs` and enums are `$defs` (not inlined).

- [ ] **Step 3: Confirm `git status` shows exactly four new untracked files**

Run: `git status --porcelain schemas/json`
Expected: four `??` lines for the four new files only. **No modifications** to any existing schema. If any existing schema shows modified, stop and investigate.

- [ ] **Step 4: Verify the case-views drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`. `git diff --quiet` ignores untracked files, so the four new schemas don't trip it; `case-model.md` is unchanged (no `Workflow` entry).

- [ ] **Step 5: `git add` the four new schemas (load-bearing) and commit**

```bash
git add schemas/json/MissenseAminoAcidAssessment.schema.json \
        schemas/json/MissensePredictiveEvidence.schema.json \
        schemas/json/MissenseInformativeVariant.schema.json \
        schemas/json/MissenseInformativeEvidence.schema.json
git commit -m "chore: generate Missense MIS_ path JSON schemas

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Documentation

**Files:**
- Create: `docs/workflows/pfd/missense.md`
- Modify: `mkdocs.yml`
- Modify: `docs/workflows/pfd/index.md`
- Modify: `docs/reference/spec-alignment.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`

- [ ] **Step 1: Create the Missense workflow page**

Create `docs/workflows/pfd/missense.md`:

```markdown
# Missense (`MIS_` / `SPL_`)

**Missense variants** are evaluated on **two** paths of the SVCv4 missense flow
diagram (Supplementary Material 6): an **amino-acid effect** path (the upper,
green path → the `MIS_` parent code) and a **splicing effect** path (the lower
yellow/orange/blue/violet paths → the `SPL_` parent code). The analyst follows
**both**, then applies the higher (more positive) of the two scores.

!!! note "Modeling underway — amino-acid path landed"

    This increment models the **amino-acid (`MIS_`) path** as
    `MissenseAminoAcidAssessment` (inputs captured, scoring documented not
    computed). The splice (`SPL_`) paths and the `MIS_`-vs-`SPL_` comparison are
    later increments.

## Amino-acid effect path (`MIS_`) ✅ modeled (inputs)

The amino-acid path runs the shared PFD pipeline for the `MIS_` parent code. Each
step below is **documented, not computed**.

### Predictive evidence (`MIS_PRD_`)

The analyst selects **one** calibrated in-silico predictor **in advance** from the
seven approved by ClinGen — AlphaMissense, BayesDel, ESM1b, MutPred2, REVEL,
VARITY_R, VEST4 — or an in-house-calibrated alternative (`MissensePredictor`, with
`OTHER_CALIBRATED` for the latter). Each can reach **+4.0** for pathogenicity;
three reach −4.0 and four reach −3.0 for benignity. Positive points are then
adjusted for **transcript relevance** (`ExonRelevance`): the exon is present in
**All** disease-relevant transcripts (full points), **Most** (half), or **Few**
(zero). Unlike other variant types, the **molecular-mechanism** axis is *not*
applied here — missense predictors already capture both loss- and gain-of-function
effects. The result is coded and capped `MIS_PRD_ −4.0 to +4.0`.

### Functional evidence (`MIS_FXN_`)

The generic [Functional Assays](index.md#functional-assays-modeled-inputs) module
(`FunctionalAssayEvidence`), coded `MIS_FXN_ −8.0 to +8.0`. The `MIS_PRD_` and
`MIS_FXN_` points are combined and **held** (no distinct code) capped `−8.0 to
+6.0`; per SM 6, the model records **both** the separate values and the combined
value (`prd_fxn_combined`).

### Informative variants (`MIS_INF_`)

The missense informative-variants module is **distinct** from the general
[Informative Variants](index.md#informative-variants-modeled-inputs) module: it has
**four** categories (`MissenseInfCategory`), any combination of which may be
**summed**, coded `MIS_INF_ −8.0 to +8.0`. All concern nucleotide changes in the
**same codon** as the VBC (the same nucleotide change as the VBC is excluded — that
is `CLN_AFF` evidence):

| Category | Description | Points |
|---|---|---|
| `SAME_AA_PATHOGENIC` | Distinct nucleotide, **same** predicted amino acid, P/LP | +4.0 first P; +2.0 each LP; +2.0 each additional |
| `DISTINCT_AA_PATHOGENIC` | Distinct amino acid, P/LP, Grantham(wt→inf) ≤ Grantham(wt→VBC) | +2.0 first P; +1.0 first LP; +1.0 each additional |
| `DISTINCT_AA_BENIGN` | Distinct amino acid, B/LB, Grantham(wt→inf) ≥ Grantham(wt→VBC) | −2.0 first B; −1.0 first LB; −1.0 each additional |
| `SAME_AA_BENIGN` | Distinct nucleotide, **same** predicted amino acid, B/LB | −4.0 first B; −2.0 each LB; −2.0 each additional |

Points are awarded for **distinct variants**, regardless of how many times each is
observed. The two Grantham distances (`grantham_wt_to_vbc`,
`grantham_wt_to_informative`) gate categories 2 and 3 only. The categories key on
P/LP/B/LB; a `VUS` informative variant is out-of-band for `MIS_INF_` scoring (the
reused `VariantClassification` enum permits it, but it maps to no category). The
**motif-variant** special case (category 2, +2.0 once) leans on
[Determining Critical Amino Acids (SM 7)](../../reference/spec-alignment.md) and is
deferred to that increment.

### Amino-acid total (`MIS_`)

The `MIS_INF_` points are combined with the prior steps and coded with the parent
code `MIS_ −8.0 to +9.0` (`mis_total`). This value is later compared with the
splice path's `SPL_` total (a future increment) to decide which applies.

## Splice effect path (`SPL_`)

Modeled in a later increment — the five color sub-paths (yellow/upper-orange/
lower-orange/blue/violet), the `SPL_SPA` splice-assay module, and the
`MIS_`-vs-`SPL_` comparison.
```

- [ ] **Step 2: Add the page to the mkdocs nav**

In `mkdocs.yml`, under the PFD nav section, add the Missense page after the index. Change:

```yaml
      - Predictive & Functional Data (PFD):
          - workflows/pfd/index.md
```

to:

```yaml
      - Predictive & Functional Data (PFD):
          - workflows/pfd/index.md
          - Missense (MIS_/SPL_): workflows/pfd/missense.md
```

- [ ] **Step 3: Link the new page from the PFD overview**

In `docs/workflows/pfd/index.md`, replace the closing paragraph:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). The
remaining PFD work — Determining Critical Amino Acids (SM 7) and the
per-variant-type workflows (Missense first, with its typed predictors and dual
MIS_/SPL_ path) — is still to come.
```

with:

```markdown
**The three shared sub-modules and the scaffold are now modeled** (inputs). The
first per-variant-type workflow has begun: the
[Missense](missense.md) amino-acid (`MIS_`) path is now modeled (inputs); its
splice (`SPL_`) paths and the `MIS_`-vs-`SPL_` comparison, the other variant-type
workflows, and Determining Critical Amino Acids (SM 7) are still to come.
```

- [ ] **Step 4: Update the SM 6 row in `spec-alignment.md`**

In `docs/reference/spec-alignment.md`, replace the SM 6 row:

```markdown
| 6 | [Missense Variants](https://docs.google.com/document/d/1eerqnL0kRq1se341-pxHxNI7HrPP9_kDlLL4eDvt-Gk/edit) | `MIS_*`, `SPL_*` (missense path) | Not yet modeled — see [Predictive & Functional Data](../workflows/pfd/index.md) |
```

with:

```markdown
| 6 | [Missense Variants](https://docs.google.com/document/d/1eerqnL0kRq1se341-pxHxNI7HrPP9_kDlLL4eDvt-Gk/edit) | `MIS_*`, `SPL_*` (missense path) | **Partially modeled (inputs)** — the amino-acid (`MIS_`) path is modeled as `MissenseAminoAcidAssessment` (typed predictor, transcript relevance, the four MIS_INF Grantham categories); the splice (`SPL_`) paths and the MIS/SPL comparison are pending. See [Missense](../workflows/pfd/missense.md) |
```

- [ ] **Step 5: Update the "Full PFD modeling" row in `known-gaps.md`**

In `docs/reference/known-gaps.md`, replace the `| Full PFD modeling | PFD | … |` row with:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), and the **Missense amino-acid (`MIS_`) path** (`MissenseAminoAcidAssessment`) are now modeled (inputs only). What remains: the Missense splice (`SPL_`) paths + the MIS/SPL comparison; Critical Amino Acids (SM 7); the other variant-type workflows; the combined-held / `SPL_SPA` structuring; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

- [ ] **Step 6: Append the model.md entry**

In `docs/reference/model.md`, after the **last** `::: svcv4_model.PfdCodeAssessment` entry, append:

```markdown

---

::: svcv4_model.MissenseAminoAcidAssessment
```

(Only the top-level assessment is documented; its predictive/informative sub-models
appear as field type annotations, matching the existing `PfdCodeAssessment` entry.)

- [ ] **Step 7: Build the docs strictly**

Run: `uv run mkdocs build --strict 2>&1 | tail -20`
Expected: `Documentation built…` with **no** WARNING lines. The new page must be in the nav (Step 2) or strict fails on an unreferenced page. If strict flags a broken same-page anchor (e.g. the `index.md#functional-assays-modeled-inputs` / `#informative-variants-modeled-inputs` links), verify the target slugs against the built HTML under `site/workflows/pfd/index.html` and adjust; those two headings on `index.md` are `### Functional Assays ✅ modeled (inputs)` and `### Informative Variants ✅ modeled (inputs)`, whose slugs collapse the emoji/`&` — confirm with `grep -o 'id="functional-assays-modeled-inputs"' site/workflows/pfd/index.html`.

- [ ] **Step 8: Commit the docs**

```bash
git add docs/workflows/pfd/missense.md mkdocs.yml docs/workflows/pfd/index.md \
        docs/reference/spec-alignment.md docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: document the Missense amino-acid (MIS_) path

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Full quality gates

**Files:** none (verification only)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -q`
Expected: all tests pass (new `tests/test_missense.py` plus the existing suite).

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

- `MissensePredictor`, `MissenseInfCategory`, `MissensePredictiveEvidence`, `MissenseInformativeVariant`, `MissenseInformativeEvidence`, `MissenseAminoAcidAssessment` importable from `svcv4_model`, all-optional, `extra="forbid"`.
- Four new committed JSON schemas; no existing schema changed; `case-model.md` untouched.
- New `pfd/missense.md` page in the nav; PFD overview links to it; spec-alignment/known-gaps/model docs updated.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR for increment 2a, run the `code-review` skill on the diff, address findings, then merge on request. Increment **2b** (the splice `SPL_` paths + `SPL_SPA`) and **2c** (the MIS/SPL comparison) follow on later branches.
