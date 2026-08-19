# Missense — Amino-Acid (MIS_) Path — Design Spec

**Date:** 2026-08-18
**Status:** Proposed
**Builds on:** the PFD scaffold (`PfdCodeAssessment`, #32) and the three shared
submodules SM 18/19/20. Same **capture + document, do not compute** stance.

## 1. Purpose & goal

Model the **amino-acid effect path** of the SVCv4 Missense workflow (SM 6) — the
"GREEN" upper path that yields the `MIS_` parent code. This is increment **2a** of
the Missense effort; the splice paths (`SPL_`, five color sub-paths) are 2b and the
`MIS_`-vs-`SPL_` "take the higher" comparison is 2c.

Scope is capture-only: model the inputs an analyst records along the amino-acid
path and document the pipeline (MIS_PRD → MIS_FXN → MIS_INF → MIS_ total) with its
caps; compute no points.

## 2. Source material

- **Supplementary Material 6 (Missense)**, verbatim in
  `source-material/svcv4-supplements/SM06-missense.txt` — the amino-acid path
  (lines 4–39): the seven calibrated predictors, transcript relevance, the four
  MIS_INF Grantham categories, and the caps.
- **Existing architecture:** `src/svcv4_model/pfd.py` (the scaffold this mirrors),
  `mechanism.py` (`ExonRelevance`), `informative.py` (`VariantClassification`),
  `functional.py` (`FunctionalAssayEvidence`), `population.py` (payload precedent).

## 3. Key findings driving this work

### 3.1 MIS_PRD: one pre-selected calibrated predictor, transcript-relevance only

SM 6: a single calibrated in-silico predictor, **selected in advance**, from seven
approved (AlphaMissense, BayesDel, ESM1b, MutPred2, REVEL, VARITY_R, VEST4) — or an
in-house-calibrated alternative. Each can reach **+4.0** (pathogenic); three reach
−4.0 and the other four −3.0 (benign). The raw points are then adjusted for
**transcript relevance** (exon present in All / Most / Few disease-relevant
transcripts → full / half / zero), then capped and coded `MIS_PRD_ −4.0 to +4.0`.
Crucially, the **molecular-mechanism** axis is *not* applied here (unlike other
variant types) because predictors capture both LoF and GoF effects — so
`MissensePredictiveEvidence` reuses `ExonRelevance` but has **no** mechanism field.

### 3.2 MIS_FXN reuses the shared functional module

The functional step is the generic SM 20 module (`FunctionalAssayEvidence`), coded
`MIS_FXN_ −8.0 to +8.0`. `MIS_PRD_` + `MIS_FXN_` are combined and held (no distinct
code) capped `−8.0 to +6.0`; SM 6 requires software to record **both** the separate
and the combined values.

### 3.3 MIS_INF: four summable Grantham categories (distinct structure)

MIS_INF is structurally unlike the generic SM 19 module — it has **four** distinct
informative-variant categories, any combination summable, coded `MIS_INF_ −8.0 to
+8.0`:

1. **Same-codon, same predicted AA as VBC, P/LP** → +4.0 first P; +2.0 each LP;
   +2.0 each additional. (Grantham not relevant.)
2. **Same-codon, distinct AA, P/LP, Grantham(wt→inf) ≤ Grantham(wt→VBC)** → +2.0
   first P; +1.0 first LP; +1.0 each additional.
3. **Same-codon, distinct AA, B/LB, Grantham(wt→inf) ≥ Grantham(wt→VBC)** → −2.0
   first B; −1.0 first LB; −1.0 each additional.
4. **Same-codon, same predicted AA as VBC, B/LB** → −4.0 first B; −2.0 each LB;
   −2.0 each additional. (Grantham not relevant.)

Points are for **distinct variants** regardless of observation count; the same
nucleotide change as the VBC is excluded (it is CLN_AFF evidence instead). The
**motif-variant** special case (category 2, +2.0 once, leaning on SM 7 Critical
Amino Acids) is **deferred to the SM 7 increment**.

### 3.4 Standalone assessment mirroring the scaffold

Per the approved shape, `MissenseAminoAcidAssessment` is a standalone entity that
mirrors `PfdCodeAssessment`'s shape but swaps in the missense-specific predictive
step and the Grantham informative module (the scaffold's generic `informative`
field does not fit MIS_INF). It reuses `FunctionalAssayEvidence`. Finally combined
and coded with the parent code `MIS_ −8.0 to +9.0`. Standalone PFD payload — **no**
`Workflow` enum entry, no applicability matrix; `case-model.md` unaffected.

## 4. Scope

**In scope:**

- New module `src/svcv4_model/missense.py`: `MissensePredictor` +
  `MissenseInfCategory` enums; `MissensePredictiveEvidence`,
  `MissenseInformativeVariant`, `MissenseInformativeEvidence`,
  `MissenseAminoAcidAssessment` (§5.1).
- Export the six public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — four new files (§5.3).
- Docs: new `docs/workflows/pfd/missense.md` (+ nav + link from `pfd/index.md`),
  `spec-alignment.md` SM 6 row, `known-gaps.md` PFD row, `model.md` (§5.4).
- Tests: new `tests/test_missense.py` (§5.5).

**Out of scope / deferred:**

- The entire splice half (`SPL_`, the five color sub-paths, `SPL_SPA`) — increment
  2b — and the `MIS_`-vs-`SPL_` comparison — increment 2c.
- The motif-variant flag + rule (with SM 7 Critical Amino Acids).
- All point computation (caps, sums, transcript-relevance reduction, Grantham
  comparison).

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/missense.py`

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

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `from svcv4_model.missense import (...)` in module order. Comparing the module
names char-by-char: `mechanism`, `method`, `missense` share `m`; then `e`(`mechanism`,
`method`) < `i`(`missense`), so `missense` sorts **after both** `mechanism` and
`method`; and `missense` < `population`. So the import block goes **after `from
svcv4_model.method import Method`** and **before `from svcv4_model.pfd import (...)`**
(`missense` < `pfd`). Export the six names and add them to `__all__` in sorted
position — all six `Missense…` (`Mi…`) entries sort **after**
`MechanismExonRelevanceEvidence`/`Method` (`Me…`) and **before** `MolecularMechanism`
(`Mo…`). `__all__` is hand-sorted (ruff does not sort it). The two enums get no
schema file; the four `BaseModel`s do.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **four** new files —
`MissenseAminoAcidAssessment.schema.json` (which `$ref`s `MissensePredictiveEvidence`,
`FunctionalAssayEvidence`, `MissenseInformativeEvidence`, and the enums under
`$defs`), `MissensePredictiveEvidence.schema.json`,
`MissenseInformativeVariant.schema.json`, and
`MissenseInformativeEvidence.schema.json`. **`git add` all four** — the drift gate
does not flag forgotten untracked files. `export_case_views.py` and `case-model.md`
are unaffected (no `Workflow` entry). CI drift gate:
`git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/missense.md`** (new) — the Missense workflow page. Document
  the dual-path framing (this increment models the amino-acid/GREEN path; splice +
  comparison are later), then the MIS_PRD (seven predictors, transcript relevance,
  no mechanism axis, −4.0 to +4.0), MIS_FXN (reuse SM 20, held PRD+FXN −8.0 to +6.0),
  and MIS_INF (the four Grantham categories with their point rules, distinct-variants
  rule, motif deferred) steps, then the MIS_ −8.0 to +9.0 total — all *documented,
  not computed*. Note the four MIS_INF categories key on P/LP/B/LB only; a `VUS`
  informative variant is out-of-band for MIS_INF scoring (the reused
  `VariantClassification` enum permits it, but it maps to no category).
- **`mkdocs.yml`** — add `- Missense (MIS_/SPL_): workflows/pfd/missense.md` under
  the PFD nav section (after `workflows/pfd/index.md`).
- **`docs/workflows/pfd/index.md`** — in the scaffold section's closing note, link
  the first per-variant-type workflow to the new page and note the amino-acid path
  is now modeled (splice + comparison to follow).
- **`docs/reference/spec-alignment.md`** — SM 6 row: from "Not yet modeled" to
  "Partially modeled — the amino-acid (`MIS_`) path (`MissenseAminoAcidAssessment`);
  the splice (`SPL_`) paths and the MIS/SPL comparison are pending."
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: the Missense
  amino-acid path now joins the scaffold + submodules; remaining = the Missense
  splice paths + comparison, the other variant types, SM 7, and the scoring.
- **`docs/reference/model.md`** — add `::: svcv4_model.MissenseAminoAcidAssessment`
  after the last entry (the predictive/informative sub-models appear as its field
  type annotations, matching the existing `PfdCodeAssessment` entry's behavior).

### 5.5 Tests: `tests/test_missense.py`

- Round-trip a maximal `MissenseAminoAcidAssessment` (predictive with a typed
  predictor + `ExonRelevance`, a `FunctionalAssayEvidence`, a
  `MissenseInformativeEvidence` with one variant per category, all point fields)
  through `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields on each of the
  four models.
- Each `MissensePredictor` and each `MissenseInfCategory` value round-trips.
- `MissenseInformativeEvidence().variants == []`.
- The six names are importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_missense.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the four new schemas:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes (new page in nav; no broken links).

## 7. Follow-up backlog

1. **Missense splice paths** (2b): `SPL_` codes, the five color sub-paths
   (yellow/upper-orange/lower-orange/blue/violet), the `SPL_SPA` splice-assay
   entity, and the per-path point ranges.
2. **MIS_/SPL_ comparison** (2c): a Missense container holding both assessments +
   the documented "take the higher (more positive), ties → amino acid" rule, saving
   both totals.
3. The motif-variant flag + rule with **SM 7** Critical Amino Acids.
4. The other variant-type workflows (Nonsense, Frameshift, Splice, …).
5. The full PFD scoring computation.

## 8. Delivery

Branch `feat/pfd-missense` off `main`. Single PR for this increment (2a). CI:
pytest, ruff, the schema/docs drift gate, `mkdocs build --strict`.
