# Missense Splice (`SPL_`) Paths Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the SVCv4 Missense splice (`SPL_`) paths (SM 6) — increment 2b — by extending `missense.py` with three enums and three capture-only models: one `MissenseSpliceAssessment` parameterized by a five-value prediction-outcome enum, reusing the SM 18/19/20 submodules.

**Architecture:** Extend the existing `src/svcv4_model/missense.py` (the Missense workflow is one cohesive module; increment 2c's comparison container will import both paths from here). Add `SplicePredictionOutcome` / `SplicePredictor` / `SpliceAssayResult` StrEnums and `SplicePredictiveEvidence` / `SpliceAssayEvidence` / `MissenseSpliceAssessment` models — all permissive all-optional, `ConfigDict(extra="forbid")`. `MissenseSpliceAssessment` reuses `MechanismExonRelevanceEvidence` (SM 18), `FunctionalAssayEvidence` (SM 20), and `InformativeVariantsEvidence` (SM 19). Standalone PFD payload — no `Case`, no `Workflow` enum entry, no applicability-matrix row, so `case-model.md` and the per-workflow case views are untouched. Three new committed JSON schemas (one per BaseModel); the three StrEnums get none. Scoring is documented in prose, never computed.

**Tech Stack:** Python 3.13, Pydantic v2, `uv`, pytest, ruff (line-length 100), MkDocs (`--strict`).

**Spec:** `docs/superpowers/specs/2026-08-19-missense-splice-path-design.md` (committed on this branch).

**Branch:** `feat/pfd-missense-splice` (checked out; spec committed here).

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/svcv4_model/missense.py` | Add the splice enums + models (widen 2 imports) | Modify |
| `src/svcv4_model/__init__.py` | Export the six new public names | Modify |
| `tests/test_missense.py` | Add splice tests (round-trip, permissive-empty, extra-forbid, enums, importable) | Modify |
| `schemas/json/MissenseSpliceAssessment.schema.json` | Generated (embeds reused models + enums as `$defs`) | Generate + `git add` |
| `schemas/json/SplicePredictiveEvidence.schema.json` | Generated | Generate + `git add` |
| `schemas/json/SpliceAssayEvidence.schema.json` | Generated | Generate + `git add` |
| `docs/workflows/pfd/missense.md` | Replace the splice placeholder section; flip the admonition | Modify |
| `docs/reference/spec-alignment.md` | SM 6 row → both paths modeled | Modify |
| `docs/reference/known-gaps.md` | "Full PFD modeling" row → splice paths done | Modify |
| `docs/reference/model.md` | Append `::: svcv4_model.MissenseSpliceAssessment` | Modify |

---

## Chunk 1: Missense splice models, exports, schemas, docs

### Task 1: Extend `missense.py` with the splice models (TDD)

**Files:**
- Modify: `src/svcv4_model/missense.py`
- Modify: `tests/test_missense.py`

- [ ] **Step 1: Add the failing splice tests**

Append to `tests/test_missense.py`. First widen the existing import block from `svcv4_model.missense` to add the six new names, and add reused-model imports at the top. The new imports reference names that don't exist yet → collection fails.

Add to the top imports (after the existing `from svcv4_model.mechanism import ExonRelevance` line, widen it, and add informative/functional as needed):

```python
from svcv4_model.informative import InformativeVariantsEvidence, VariantClassification
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
```

Widen the `from svcv4_model.missense import (...)` block to include the six new names:

```python
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
    MissenseSpliceAssessment,
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)
```

Append these test functions at the end of the file:

```python
def _maximal_splice_assessment() -> MissenseSpliceAssessment:
    return MissenseSpliceAssessment(
        prediction_outcome=SplicePredictionOutcome.NMD_PREDICTED,
        predictive=SplicePredictiveEvidence(
            splice_predictor=SplicePredictor.SPLICEAI,
            initial_points=3.0,
            protein_fraction_altered=0.6,
            alternative_start_rescue=False,
            adjusted_points=3.0,
        ),
        mechanism_exon_relevance=MechanismExonRelevanceEvidence(),
        splice_assay=SpliceAssayEvidence(
            assay_type="minigene",
            result=SpliceAssayResult.NEAR_COMPLETE_OR_COMPLETE,
            calibrated=False,
        ),
        functional=FunctionalAssayEvidence(protein_assays=[ProteinFunctionalAssay()]),
        informative=InformativeVariantsEvidence(),
        prd_points=3.0,
        spa_points=3.0,
        fxn_points=2.0,
        inf_points=1.0,
        prd_spa_combined=6.0,
        prd_spa_fxn_combined=8.0,
        spl_total=9.0,
    )


def test_splice_assessment_round_trips_json() -> None:
    original = _maximal_splice_assessment()
    rehydrated = MissenseSpliceAssessment.model_validate(original.model_dump(mode="json"))
    assert rehydrated == original


def test_splice_assessment_is_permissive_when_empty() -> None:
    empty = MissenseSpliceAssessment()
    assert empty.prediction_outcome is None
    assert empty.predictive is None
    assert empty.mechanism_exon_relevance is None
    assert empty.splice_assay is None
    assert empty.functional is None
    assert empty.informative is None
    assert empty.spl_total is None


def test_splice_assessment_forbids_extra() -> None:
    with pytest.raises(ValueError):
        MissenseSpliceAssessment(not_a_field=1)


def test_splice_predictive_forbids_extra() -> None:
    with pytest.raises(ValueError):
        SplicePredictiveEvidence(not_a_field=1)


def test_splice_assay_forbids_extra() -> None:
    with pytest.raises(ValueError):
        SpliceAssayEvidence(not_a_field=1)


def test_splice_prediction_outcome_values_round_trip() -> None:
    for outcome in SplicePredictionOutcome:
        assert MissenseSpliceAssessment(prediction_outcome=outcome).prediction_outcome is outcome


def test_splice_predictor_values_round_trip() -> None:
    for predictor in SplicePredictor:
        assert SplicePredictiveEvidence(splice_predictor=predictor).splice_predictor is predictor


def test_splice_assay_result_values_round_trip() -> None:
    for result in SpliceAssayResult:
        assert SpliceAssayEvidence(result=result).result is result


def test_splice_names_importable_from_package_root() -> None:
    import svcv4_model

    for name in (
        "MissenseSpliceAssessment",
        "SpliceAssayEvidence",
        "SpliceAssayResult",
        "SplicePredictionOutcome",
        "SplicePredictiveEvidence",
        "SplicePredictor",
    ):
        assert name in svcv4_model.__all__
```

- [ ] **Step 2: Run the splice tests to verify they fail**

Run: `uv run pytest tests/test_missense.py -q 2>&1 | tail -5`
Expected: collection **ERROR** — `ImportError: cannot import name 'MissenseSpliceAssessment' from 'svcv4_model.missense'`.

- [ ] **Step 3: Widen the two reused imports in `missense.py`**

In `src/svcv4_model/missense.py`, replace:

```python
from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import VariantClassification
from svcv4_model.mechanism import ExonRelevance
```

with:

```python
from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence, VariantClassification
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
```

- [ ] **Step 4: Append the splice enums and models**

At the **end** of `src/svcv4_model/missense.py`, append (from spec §5.1; longest field description is under 100 chars):

```python
class SplicePredictionOutcome(StrEnum):
    """The in-silico splice-prediction outcome selecting one of five paths (SM 6)."""

    NMD_PREDICTED = "NMD_PREDICTED"
    FRAMESHIFT_NO_NMD = "FRAMESHIFT_NO_NMD"
    SPLICE_NO_FRAMESHIFT = "SPLICE_NO_FRAMESHIFT"
    UNCERTAIN = "UNCERTAIN"
    UNLIKELY = "UNLIKELY"


class SplicePredictor(StrEnum):
    """An in-silico splice-effect predictor (SM 6)."""

    SPLICEAI = "SPLICEAI"
    PANGOLIN = "PANGOLIN"
    OTHER = "OTHER"


class SpliceAssayResult(StrEnum):
    """The qualitative degree of aberrant splice product in a splice assay (SM 6)."""

    NEAR_COMPLETE_OR_COMPLETE = "NEAR_COMPLETE_OR_COMPLETE"
    SUBSTANTIAL = "SUBSTANTIAL"
    INCOMPLETE_OR_NONE = "INCOMPLETE_OR_NONE"


class SplicePredictiveEvidence(BaseModel):
    """The splice predictive (SPL_PRD) step of a splice path (SM 6).

    Positive initial points (yellow/orange paths) are reduced by the SM 18
    mechanism/exon matrix; blue starts at 0.0 and violet at −1.0.
    """

    model_config = ConfigDict(extra="forbid")

    splice_predictor: SplicePredictor | None = Field(
        default=None, description="The in-silico splice predictor used (e.g. SpliceAI)."
    )
    initial_points: float | None = Field(
        default=None, description="Initial SPL_PRD points before the SM 18 adjustment."
    )
    protein_fraction_altered: float | None = Field(
        default=None,
        description="Fraction of protein altered (orange paths' initial-points table).",
    )
    alternative_start_rescue: bool | None = Field(
        default=None,
        description="An alternative start codon rescues the 5' PTC (the −1.0 case).",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded SPL_PRD points after the SM 18 adjustment."
    )
    # Note: the lower-orange path's protein-deletion in-silico tool input
    # (MutationTaster/Provean, +2.0 / −0.5; SM 6, not yet calibrated) folds into
    # ``initial_points`` for now rather than a dedicated field.


class SpliceAssayEvidence(BaseModel):
    """The splice-assay (SPL_SPA) step: RNA / minigene evidence for splicing (SM 6).

    Distinct from SM 20 functional evidence (which is SPL_FXN). Semantics vary by
    path: it scales SPL_PRD (yellow/orange), is additive (blue), or adds benignity
    (violet). Absent = SPL_SPA_ND.
    """

    model_config = ConfigDict(extra="forbid")

    assay_type: str | None = Field(
        default=None, description="Assay modality (e.g. RT-PCR, RNAseq, minigene)."
    )
    result: SpliceAssayResult | None = Field(
        default=None, description="Qualitative degree of the aberrant splice product."
    )
    calibrated: bool | None = Field(
        default=None,
        description="Whether an activity-threshold calibration allows adjusted scoring.",
    )


class MissenseSpliceAssessment(BaseModel):
    """The missense splice (SPL_) path assessment (SM 6).

    One entity for all five color-paths, parameterized by ``prediction_outcome``;
    reuses the SM 18/19/20 submodules. Permissive superset; the per-path pipeline
    and its caps are documented, not computed.
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
        default=None, description="SM 6 splice-assay evidence (SPL_SPA)."
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

- [ ] **Step 5: Format + lint the module and tests**

Run: `uv run ruff format src/svcv4_model/missense.py tests/test_missense.py && uv run ruff check --fix src/svcv4_model/missense.py tests/test_missense.py`
Expected: `ruff format` reports files unchanged (or reformats trivially); `ruff check --fix` sorts the widened import blocks and exits clean.

- [ ] **Step 6: Run the splice tests — expect only the package-root import test to fail**

Run: `uv run pytest tests/test_missense.py -q`
Expected: `test_splice_names_importable_from_package_root` **FAILS** (names not yet in `svcv4_model.__all__`); every other test (the amino-acid ones and the new splice ones) **PASSES**. This isolates the remaining work to the export step.

- [ ] **Step 7: Commit the module + tests**

```bash
git add src/svcv4_model/missense.py tests/test_missense.py
git commit -m "feat: add Missense splice (SPL_) path models

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Export the six new names from the package root

**Files:**
- Modify: `src/svcv4_model/__init__.py`

- [ ] **Step 1: Widen the missense import block**

In `src/svcv4_model/__init__.py`, add `MissenseSpliceAssessment`, `SpliceAssayEvidence`, `SpliceAssayResult`, `SplicePredictionOutcome`, `SplicePredictiveEvidence`, `SplicePredictor` to the existing `from svcv4_model.missense import (...)` block. The whole block sorted:

```python
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
    MissenseSpliceAssessment,
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)
```

- [ ] **Step 2: Add the six names to `__all__`, in sorted position**

`__all__` is hand-sorted (ruff does not sort it). Two insertions:

(a) Insert `"MissenseSpliceAssessment"` **between `"MissensePredictor"` and `"MolecularMechanism"`**:

```python
    "MissensePredictor",
    "MissenseSpliceAssessment",
    "MolecularMechanism",
```

(b) Insert the five `Splice*` names **between `"SimilarityBasis"` and `"Statement"`** (`Se` < `Si` < `Sp` < `St`, so the block follows `SimilarityBasis`):

```python
    "SimilarityBasis",
    "SpliceAssayEvidence",
    "SpliceAssayResult",
    "SplicePredictionOutcome",
    "SplicePredictiveEvidence",
    "SplicePredictor",
    "Statement",
```

- [ ] **Step 3: Let ruff sort the import block and verify format**

Run: `uv run ruff check --fix src/svcv4_model/__init__.py && uv run ruff format --check src/svcv4_model/__init__.py`
Expected: the import block is isort-sorted (the `__all__` list is already correct from Step 2 — ruff does not reorder it); both clean (exit 0).

- [ ] **Step 4: Run the full test file — all green now**

Run: `uv run pytest tests/test_missense.py -q`
Expected: **all tests PASS**, including `test_splice_names_importable_from_package_root`.

- [ ] **Step 5: Commit the export**

```bash
git add src/svcv4_model/__init__.py
git commit -m "feat: export Missense splice (SPL_) path from package root

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Regenerate and commit the JSON schemas

**Files:**
- Generate: `schemas/json/MissenseSpliceAssessment.schema.json`
- Generate: `schemas/json/SplicePredictiveEvidence.schema.json`
- Generate: `schemas/json/SpliceAssayEvidence.schema.json`

- [ ] **Step 1: Regenerate schemas**

Run: `uv run python scripts/export_schemas.py`
Expected: **three new** files appear (the three new BaseModels). The three StrEnums get none. Existing schema files (including the reused `MechanismExonRelevanceEvidence` / `FunctionalAssayEvidence` / `InformativeVariantsEvidence` and the amino-acid path's files) are unchanged.

- [ ] **Step 2: Sanity-check the top-level assessment schema**

Run: `uv run python -c "import json; d=json.load(open('schemas/json/MissenseSpliceAssessment.schema.json')); print(sorted(d.get('\$defs', {}).keys()))"`
Expected: `$defs` include `SplicePredictiveEvidence`, `SpliceAssayEvidence`, `SplicePredictionOutcome`, `SplicePredictor`, `SpliceAssayResult`, `MechanismExonRelevanceEvidence`, `FunctionalAssayEvidence`, `InformativeVariantsEvidence` (and their nested defs). Confirms reused models embed as `$ref`/`$defs` and enums are `$defs` (not inlined).

- [ ] **Step 3: Confirm `git status` shows exactly three new untracked files**

Run: `git status --porcelain schemas/json`
Expected: three `??` lines for the three new files only. **No modifications** to any existing schema. If any existing schema shows modified, stop and investigate.

- [ ] **Step 4: Verify the case-views drift gate is clean**

Run: `uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo GATE_CLEAN`
Expected: prints `GATE_CLEAN`. `git diff --quiet` ignores untracked files, so the three new schemas don't trip it; `case-model.md` is unchanged (no `Workflow` entry).

- [ ] **Step 5: `git add` the three new schemas (load-bearing) and commit**

```bash
git add schemas/json/MissenseSpliceAssessment.schema.json \
        schemas/json/SplicePredictiveEvidence.schema.json \
        schemas/json/SpliceAssayEvidence.schema.json
git commit -m "chore: generate Missense splice (SPL_) path JSON schemas

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Documentation

**Files:**
- Modify: `docs/workflows/pfd/missense.md`
- Modify: `docs/reference/spec-alignment.md`
- Modify: `docs/reference/known-gaps.md`
- Modify: `docs/reference/model.md`

- [ ] **Step 1: Replace the splice placeholder section in `missense.md`**

In `docs/workflows/pfd/missense.md`, replace the placeholder section:

```markdown
## Splice effect path (`SPL_`)

Modeled in a later increment — the five color sub-paths (yellow/upper-orange/
lower-orange/blue/violet), the `SPL_SPA` splice-assay module, and the
`MIS_`-vs-`SPL_` comparison.
```

with:

```markdown
## Splice effect path (`SPL_`) ✅ modeled (inputs)

The splice path evaluates the nucleotide change's effect on splicing. The in-silico
splice prediction (SpliceAI / Pangolin — `SplicePredictor`) selects **one** of five
paths (`SplicePredictionOutcome`), and all five run the same pipeline: **SPL_PRD**
(prediction) → **SPL_SPA** (splice assay) → **SPL_FXN** (functional, SM 20) →
**SPL_INF** (informative, SM 19) → the capped **SPL_** total. Modeled as one
`MissenseSpliceAssessment`; each step is **documented, not computed**.

| Path (`prediction_outcome`) | Splice prediction | SPL_PRD initial | SPL_ total |
|---|---|---|---|
| `NMD_PREDICTED` (yellow) | frameshift + NMD | `+3.0` | `−8.0 to +10.0` |
| `FRAMESHIFT_NO_NMD` (upper orange) | frameshift, no NMD | `−1.0 to +3.0` | `−8.0 to +10.0` |
| `SPLICE_NO_FRAMESHIFT` (lower orange) | splice, no frameshift/NMD | `−1.0 to +3.0` | `−8.0 to +10.0` |
| `UNCERTAIN` (blue) | uncertain | `0.0` | `−8.0 to 0.0` |
| `UNLIKELY` (violet) | unlikely | `−1.0` | `−8.0 to +8.0` |

### Splice prediction (`SPL_PRD_`)

Positive initial points (yellow/orange) are reduced by the
[Molecular Mechanism & Exon Relevance](index.md#molecular-mechanism-exon-relevance-modeled-inputs)
matrix (SM 18) — unlike the amino-acid path, the splice paths **do** apply it. The
orange paths derive their initial points from a critical-amino-acid table (the
fraction of protein altered; an alternative start codon that rescues a 5′ PTC gives
`−1.0`). The lower-orange path may also fold in a protein-deletion in-silico tool
(MutationTaster / Provean, not yet calibrated). Captured on `SplicePredictiveEvidence`.

### Splice assay (`SPL_SPA_`)

`SpliceAssayEvidence` captures RNA / minigene / RT-PCR evidence for the aberrant
splice product (`SpliceAssayResult`: near-complete / substantial / incomplete-or-none;
absent = `SPL_SPA_ND`). Its semantics differ by path: for yellow/orange it **scales**
SPL_PRD (near-complete → full/double, substantial → half, incomplete/none → zero);
for blue it is **additive** (`−2.0 to +2.0`); for violet it adds **benignity**
(`−2.0 to 0.0`). This is distinct from SPL_FXN, to avoid double-counting.

### Functional (`SPL_FXN_`) and informative (`SPL_INF_`)

`SPL_FXN` reuses the generic [Functional Assays](index.md#functional-assays-modeled-inputs)
module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0`. `SPL_INF` reuses the
generic [Informative Variants](index.md#informative-variants-modeled-inputs) module
(`InformativeVariantsEvidence`, SM 19): a P/LP/B/LB variant in the **same exon** with
the **same predicted splice impact** (+2.0 first P / +1.0 first LP / +1.0 each
additional; negatives for B/LB), coded `−8.0 to +8.0`; the violet path restricts it
to B/LB only. (`similarity_basis` is single-valued, so the compound same-exon-and-
same-impact eligibility is a documented rule rather than fully typed.)

### Held combined values and the `SPL_` total

Per SM 6, the model records **both** the separate coded values and the two held
combined values (`prd_spa_combined` = SPL_PRD + SPL_SPA; `prd_spa_fxn_combined` =
SPL_PRD + SPL_SPA + SPL_FXN), then the capped parent `SPL_` total (`spl_total`),
whose range depends on the path (table above). The `SPL_` total is later compared
with the amino-acid `MIS_` total (increment 2c) to decide which applies.
```

- [ ] **Step 2: Flip the top admonition in `missense.md`**

Replace the admonition:

```markdown
!!! note "Modeling underway — amino-acid path landed"

    This increment models the **amino-acid (`MIS_`) path** as
    `MissenseAminoAcidAssessment` (inputs captured, scoring documented not
    computed). The splice (`SPL_`) paths and the `MIS_`-vs-`SPL_` comparison are
    later increments.
```

with:

```markdown
!!! note "Modeling underway — both paths landed"

    Both the **amino-acid (`MIS_`) path** (`MissenseAminoAcidAssessment`) and the
    **splice (`SPL_`) paths** (`MissenseSpliceAssessment`) are modeled (inputs
    captured, scoring documented not computed). The `MIS_`-vs-`SPL_` comparison
    ("take the higher") is a later increment.
```

- [ ] **Step 3: Update the SM 6 row in `spec-alignment.md`**

Replace the SM 6 row:

```markdown
| 6 | [Missense Variants](https://docs.google.com/document/d/1eerqnL0kRq1se341-pxHxNI7HrPP9_kDlLL4eDvt-Gk/edit) | `MIS_*`, `SPL_*` (missense path) | **Partially modeled (inputs)** — the amino-acid (`MIS_`) path is modeled as `MissenseAminoAcidAssessment` (typed predictor, transcript relevance, the four MIS_INF Grantham categories); the splice (`SPL_`) paths and the MIS/SPL comparison are pending. See [Missense](../workflows/pfd/missense.md) |
```

with:

```markdown
| 6 | [Missense Variants](https://docs.google.com/document/d/1eerqnL0kRq1se341-pxHxNI7HrPP9_kDlLL4eDvt-Gk/edit) | `MIS_*`, `SPL_*` (missense path) | **Modeled (inputs)** — both the amino-acid (`MIS_`) path (`MissenseAminoAcidAssessment`) and the splice (`SPL_`) paths (`MissenseSpliceAssessment`, five prediction outcomes reusing SM 18/19/20) are modeled; only the `MIS_`-vs-`SPL_` comparison ("take the higher") is pending. See [Missense](../workflows/pfd/missense.md) |
```

- [ ] **Step 4: Update the "Full PFD modeling" row in `known-gaps.md`**

Replace the current row:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), and the **Missense amino-acid (`MIS_`) path** (`MissenseAminoAcidAssessment`) are now modeled (inputs only). What remains: the Missense splice (`SPL_`) paths + the MIS/SPL comparison; Critical Amino Acids (SM 7); the other variant-type workflows; the combined-held / `SPL_SPA` structuring; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

with:

```markdown
| Full PFD modeling | PFD | The three shared sub-modules (SM 18/19/20), the variant-agnostic scaffold (`PfdCodeAssessment`), and **both Missense paths** — amino-acid (`MissenseAminoAcidAssessment`) and splice (`MissenseSpliceAssessment`) — are now modeled (inputs only). What remains: the `MIS_`-vs-`SPL_` comparison; Critical Amino Acids (SM 7); the other variant-type workflows; and the multiplier/scoring computation. See [Predictive & Functional Data](../workflows/pfd/index.md). |
```

- [ ] **Step 5: Append the model.md entry**

In `docs/reference/model.md`, after the `::: svcv4_model.MissenseAminoAcidAssessment` entry (the current last entry), append:

```markdown

---

::: svcv4_model.MissenseSpliceAssessment
```

- [ ] **Step 6: Build the docs strictly**

Run: `uv run mkdocs build --strict 2>&1 | tail -20`
Expected: `Documentation built…` with **no** WARNING lines. The three same-page-style anchors used (`index.md#molecular-mechanism-exon-relevance-modeled-inputs`, `#functional-assays-modeled-inputs`, `#informative-variants-modeled-inputs`) all resolve to existing headings on `index.md` (mkdocs strict validates page existence, not fragments — all three target the existing `index.md` page). If strict warns, read the warning and fix the offending link/page.

- [ ] **Step 7: Commit the docs**

```bash
git add docs/workflows/pfd/missense.md docs/reference/spec-alignment.md \
        docs/reference/known-gaps.md docs/reference/model.md
git commit -m "docs: document the Missense splice (SPL_) paths

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

- `SplicePredictionOutcome`, `SplicePredictor`, `SpliceAssayResult`, `SplicePredictiveEvidence`, `SpliceAssayEvidence`, `MissenseSpliceAssessment` importable from `svcv4_model`, all-optional, `extra="forbid"`.
- Three new committed JSON schemas; no existing schema changed; `case-model.md` untouched.
- The Missense page's splice section is modeled (five paths, ranges, SPA semantics); the admonition, spec-alignment, known-gaps, and model docs updated.
- `pytest`, `ruff check`, `ruff format --check`, the drift gate, and `mkdocs build --strict` all pass.
- No scoring/computation added — capture + document only.

## After this plan

Open a single PR for increment 2b, run the `code-review` skill on the diff, address findings, then merge on request. Increment **2c** (the `MIS_`-vs-`SPL_` comparison container + "take the higher" rule) follows on a later branch and completes the Missense workflow.
