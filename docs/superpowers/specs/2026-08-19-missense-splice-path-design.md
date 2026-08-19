# Missense — Splice (`SPL_`) Paths — Design Spec

**Date:** 2026-08-19
**Status:** Proposed
**Builds on:** the Missense amino-acid path (`MissenseAminoAcidAssessment`, #33),
the PFD scaffold (#32), and the three shared submodules SM 18/19/20. Same
**capture + document, do not compute** stance.

## 1. Purpose & goal

Model the **splice effect paths** of the SVCv4 Missense workflow (SM 6) — the
lower yellow/orange/blue/violet paths that yield the `SPL_` parent code. This is
increment **2b**; the `MIS_`-vs-`SPL_` "take the higher" comparison is 2c.

Scope is capture-only: model the analyst's inputs along the splice paths and
document each path's pipeline (SPL_PRD → SPL_SPA → SPL_FXN → SPL_INF → SPL_ total),
its per-path point ranges, and the splice-assay semantics; compute no points.

## 2. Source material

- **Supplementary Material 6 (Missense)**, verbatim in
  `source-material/svcv4-supplements/SM06-missense.txt` — the splice paths
  (lines 40–157): the five prediction outcomes, the SPL_SPA splice-assay module,
  and the per-path point ranges.
- **Existing architecture:** `src/svcv4_model/missense.py` (the module this
  extends), `pfd.py` (the scaffold), `mechanism.py`
  (`MechanismExonRelevanceEvidence`), `functional.py` (`FunctionalAssayEvidence`),
  `informative.py` (`InformativeVariantsEvidence`, `SimilarityBasis`).

## 3. Key findings driving this work

### 3.1 Five color-paths, one shared pipeline

The in-silico splice prediction selects **one** of five paths (SM 6 Fig. 1):

- **yellow** — splice impact predicted, frameshift predicted, **NMD predicted**;
- **upper orange** — frameshift predicted, **NMD not** predicted;
- **lower orange** — splice change, **no frameshift**, no NMD;
- **blue** — splice impact **uncertain**;
- **violet** — splice impact **unlikely**.

All five run the same four steps — **SPL_PRD** (splice prediction) → **SPL_SPA**
(splice assay) → **SPL_FXN** (functional, SM 20) → **SPL_INF** (informative,
SM 19) → **SPL_** parent total — but the point ranges and the SPA semantics differ
per path. This is modeled as **one** `MissenseSpliceAssessment` parameterized by a
`SplicePredictionOutcome` enum; the per-path ranges/semantics are documented, not
computed.

### 3.2 Per-path SPL_PRD and SPL_SPA differ

- **SPL_PRD initial points:** yellow `+3.0`; orange paths from a critical-amino-acid
  table (`−1.0 to +3.0`, driven by the fraction of protein altered and an
  alternative-start rescue); blue `0.0`; violet `−1.0`. Positive orange/yellow
  points are then reduced by the **SM 18 mechanism/exon matrix** (0–100%) — unlike
  the amino-acid path, the splice paths **do** apply this matrix.
- **SPL_SPA semantics:** yellow/orange — the assay *scales* SPL_PRD (near-complete
  → 100%/double, substantial → 50%, incomplete/none → 0); blue — the assay is
  *additive* (`−2.0 to +2.0`); violet — the assay adds *benignity* (`−2.0 to 0.0`).
  No data → `SPL_SPA_ND`.

### 3.3 SPL_FXN and SPL_INF reuse the shared submodules

SPL_FXN is the generic SM 20 module (`FunctionalAssayEvidence`), coded `−8.0 to
+8.0` and combined with the held PRD+SPA value. SPL_INF is the generic SM 19
informative pattern (`InformativeVariantsEvidence`): a P/LP/B/LB variant in the
**same exon** with the **same predicted splice impact** (+2.0 first P / +1.0 first
LP / +1.0 each additional, negatives for B/LB), coded `−8.0 to +8.0`. SM 6 L69
explicitly defers to SM 19. The violet path restricts SPL_INF to B/LB only. Note:
`InformativeVariant.similarity_basis` is single-valued, so the *compound*
same-exon-**and**-same-splice-impact eligibility is documented in prose rather than
fully typed (the curator records `SAME_EXON`; the same-impact condition is a
documented eligibility rule) — acceptable under the capture-only stance.

### 3.4 Record both separate and held-combined values

Per SM 6, the splice paths hold two combined values with no distinct code:
`SPL_PRD_ + SPL_SPA_` and `SPL_PRD_ + SPL_SPA_ + SPL_FXN_`. Software must record
both the separate coded sub-code values and these combined values.

### 3.5 Parent SPL_ range varies by path

The parent `SPL_` total is coded per path: yellow/orange `−8.0 to +10.0`; blue
`−8.0 to 0.0`; violet `−8.0 to +8.0`. Captured as `spl_total`, documented.

## 4. Scope

**In scope:**

- Extend `src/svcv4_model/missense.py`: `SplicePredictionOutcome`,
  `SplicePredictor`, `SpliceAssayResult` enums; `SplicePredictiveEvidence`,
  `SpliceAssayEvidence`, `MissenseSpliceAssessment` models (§5.1).
- Export the six new public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — three new files (§5.3).
- Docs: flesh out the splice section on `docs/workflows/pfd/missense.md`,
  `spec-alignment.md` SM 6 row, `known-gaps.md` PFD row, `model.md` (§5.4).
- Tests: extend `tests/test_missense.py` (§5.5).

**Out of scope / deferred:**

- The `MIS_`-vs-`SPL_` comparison container + "take the higher" rule (increment 2c).
- The motif-variant flag (with SM 7).
- All point computation (per-path ranges, SPA scaling, the SM 18 reduction, sums).

## 5. Content changes, item by item

### 5.1 Extend `src/svcv4_model/missense.py`

Add the following imports (alongside the existing ones) — `MechanismExonRelevanceEvidence`
from `mechanism.py` and `InformativeVariantsEvidence` from `informative.py`:

```python
from svcv4_model.informative import InformativeVariantsEvidence, VariantClassification
from svcv4_model.mechanism import ExonRelevance, MechanismExonRelevanceEvidence
```

Append these enums and models after the existing amino-acid path code:

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

Note: the existing `from svcv4_model.informative import VariantClassification` and
`from svcv4_model.mechanism import ExonRelevance` lines are widened to also import
`InformativeVariantsEvidence` and `MechanismExonRelevanceEvidence` (run
`ruff check --fix` / `ruff format` to normalize).

### 5.2 Export (`src/svcv4_model/__init__.py`)

The `from svcv4_model.missense import (...)` block already exists (after `method`,
before `pfd`). Add the six new names to it and to `__all__`, keeping both sorted.
The six sort in two runs (confirmed via `sorted()`): `MissenseSpliceAssessment`
goes **after `MissensePredictor` and before `MolecularMechanism`** (joining the
`Missense*` block); the five `Splice*` names (`SpliceAssayEvidence`,
`SpliceAssayResult`, `SplicePredictionOutcome`, `SplicePredictiveEvidence`,
`SplicePredictor`, in that order) go **after `SimilarityBasis` and before
`Statement`**. `__all__` is hand-sorted (ruff does not sort it). The three enums
get no schema file; the three `BaseModel`s do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **three** new files —
`MissenseSpliceAssessment.schema.json` (which `$ref`s `SplicePredictiveEvidence`,
`SpliceAssayEvidence`, the reused `MechanismExonRelevanceEvidence` /
`FunctionalAssayEvidence` / `InformativeVariantsEvidence`, and the three enums
under `$defs`), `SplicePredictiveEvidence.schema.json`, and
`SpliceAssayEvidence.schema.json`. **`git add` all three** — the drift gate does
not flag untracked files. `export_case_views.py` and `case-model.md` are
unaffected (no `Workflow` entry). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/missense.md`** — replace the placeholder
  `## Splice effect path (SPL_)` section with the modeled content: the five
  prediction-outcome paths (`SplicePredictionOutcome`), the shared SPL_PRD →
  SPL_SPA → SPL_FXN → SPL_INF → SPL_ pipeline, the per-path point ranges (a table),
  the SPL_SPA semantics (scale / additive / benignity), the SM 18 matrix reduction,
  the SM 19 reuse for SPL_INF, and the two held-combined values — all *documented,
  not computed*. Flip the top admonition to "amino-acid + splice paths landed;
  comparison to follow".
- **`docs/reference/spec-alignment.md`** — SM 6 row: both the `MIS_` and `SPL_`
  paths now modeled (inputs); only the MIS/SPL comparison pending.
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: the Missense
  splice paths now join; remaining = the MIS/SPL comparison, SM 7, the other
  variant types, and the scoring.
- **`docs/reference/model.md`** — add `::: svcv4_model.MissenseSpliceAssessment`
  after the `MissenseAminoAcidAssessment` entry.

### 5.5 Tests: extend `tests/test_missense.py`

- Round-trip a maximal `MissenseSpliceAssessment` (a `prediction_outcome`, a
  `SplicePredictiveEvidence`, a `MechanismExonRelevanceEvidence`, a
  `SpliceAssayEvidence`, a `FunctionalAssayEvidence`, an
  `InformativeVariantsEvidence`, all point fields including both combined values)
  through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields on the three
  new models.
- Each `SplicePredictionOutcome`, `SplicePredictor`, and `SpliceAssayResult` value
  round-trips.
- The six new names are importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (extended `tests/test_missense.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the three new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes.

## 7. Follow-up backlog

1. **MIS_/SPL_ comparison** (2c): a Missense container holding both assessments +
   the documented "take the higher (more positive), ties → amino acid, negative
   splice → amino acid" rule, saving both totals.
2. The motif-variant flag + rule with **SM 7** Critical Amino Acids.
3. The other variant-type workflows (Nonsense, Frameshift, Splice, …).
4. The full PFD scoring computation.

## 8. Delivery

Branch `feat/pfd-missense-splice` off `main`. Single PR for this increment (2b).
CI: pytest, ruff, the schema/docs drift gate, `mkdocs build --strict`.
