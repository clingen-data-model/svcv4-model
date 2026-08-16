# CLN_CCS Case-Control Studies — Design Spec

**Date:** 2026-08-15
**Status:** Proposed
**Builds on:** the shipped capture-only increments (GDV #23, POP #25, CLN_AFF #26,
PFD SM 18/19/20 #28/#29/#30) and the **CLN_CCS reframe (#27)** that established
CLN_CCS is *modelable now*, not blocked. Same **capture + document, do not
compute** stance.

## 1. Purpose & goal

Model the `CLN_CCS` (Case-Control Studies) evidence code — the last of the
tracked known-gaps model items — as capturable structured evidence. PR #27
corrected the earlier "blocked / out of scope" framing: SVCv4 (Supplementary
Material 4) defines a usable case-control process. This pass **captures** the
study result and **documents** the scoring and the exclusivity rule; it computes
no points.

## 2. Source material (this pass)

- **Supplementary Material 4 (Clinical Observations), "Case-Control Studies
  (CLN_CCS)" section**, verbatim in
  `source-material/svcv4-supplements/SM04-clinical-observations.txt` (gitignored).
- **Existing architecture:** `src/svcv4_model/population.py` (the standalone
  curation-level typed-payload precedent this most closely mirrors);
  `src/svcv4_model/case.py` (the `Workflow` enum, which deliberately does **not**
  include CLN_CCS); `scripts/export_schemas.py`; the reframed CLN_CCS docs from
  #27 (`docs/workflows/hod/cln/index.md`, `docs/reference/spec-alignment.md` SM 4
  row, `docs/reference/known-gaps.md`).

## 3. Key findings driving this work

### 3.1 CLN_CCS is a study-level result, not a per-proband Case observation

Verbatim (SM 4): "A variant-specific case-control analysis can help determine if
there is an association between a VBC and a phenotype by comparing the observed
frequency of the VBC in a series of probands with the relevant phenotype versus
… individuals without the phenotype." This is a **study-level** datum (an odds
ratio over cohorts), fundamentally unlike the per-proband `Case` observations
(`CLN_AFF`/`CLN_DNV`/…). CLN_CCS is **not** in the `Case` model's `Workflow`
enum and does not belong in the Case applicability matrix. So it is modeled as a
**standalone typed EvidenceItem payload** in its own module, like
`PopulationEvidence` — `case-model.md` and the per-workflow `case/*` views are
unaffected.

### 3.2 Scoring and eligibility (documented, not computed)

- **Association measure:** an **odds ratio (OR)**. "If the calculated OR … is
  >5.0, then the analyst can award `CLN_CCS_+4.0`." The **confidence interval**
  matters: "If the CI includes 1.0 (e.g., OR = 5.5, CI = 0.9–7.4), points should
  not be assigned." OR near/below 1.0 is evidence of benignity.
- **Eligibility / robustness:** restricted to moderate-frequency variants;
  **≥5** observations of the variant in the case cohort; **≥100** unrelated
  cases; cases and controls **matched** (ancestry, sequencing platform, QC);
  ascertainment bias considered; the variant AF compatible with the disorder.
- **Fallback:** no robust study / fails statistical criteria → `CLN_CCS_ND`, and
  individual probands are evaluated under `CLN_AFF` instead.

### 3.3 The exclusivity rule (documented)

"When the CLN_CCS evidence code is applied, regardless of the point value
assigned, all other Clinical Observation (CLN) codes should be marked as 'NA'
(Not Applicable), with the sole exception of `CLN_DNV`." Documented on the CLN
page; not enforced (no cross-code enforcement exists yet).

## 4. Scope

**In scope:**
- New module `src/svcv4_model/case_control.py`: `CaseControlStudyEvidence` (§5.1).
- Export it from `__init__.py` (§5.2).
- Regenerate JSON Schemas — one new file (§5.3).
- Docs: `cln/index.md` (admonition → modeled), `spec-alignment.md` (SM 4 row),
  `known-gaps.md` (remove the CLN_CCS row), `model.md` (§5.4).
- Tests: new `tests/test_case_control.py` (§5.5).

**Out of scope / deferred:**
- The OR/CI → points computation and the exclusivity-rule enforcement.
- Finer eligibility structure (variant-AF-compatible-with-disorder; specific
  ascertainment-bias sub-cases) — documented, not fields.

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/case_control.py`

```python
"""SVCv4 CLN_CCS evidence — the payload behind a case_control Evidence Item.

A variant-specific case-control study result: the odds ratio of the VBC's
frequency in phenotyped cases vs controls, plus the cohort sizes and robustness
attributes SVCv4 (Supplementary Material 4) requires. A study-level datum,
distinct from the per-proband ``Case`` observations — so it is a standalone
curation-level payload like ``PopulationEvidence``, not part of ``Case``.

Scoring (see docs/workflows/hod/cln/index.md) is documented, not computed.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CaseControlStudyEvidence(BaseModel):
    """CLN_CCS case-control study inputs for a VBC.

    Permissive superset (every field optional). Captured; the scoring
    (OR > 5.0 → +4.0; CI including 1.0 → no points; OR ≤ 1.0 → benignity) and
    the exclusivity rule (other CLN codes NA except CLN_DNV) are documented,
    not computed.
    """

    model_config = ConfigDict(extra="forbid")

    odds_ratio: float | None = Field(
        default=None, description="Odds ratio for the VBC's enrichment in cases vs controls."
    )
    ci_lower: float | None = Field(
        default=None, description="Lower bound of the confidence interval around the OR."
    )
    ci_upper: float | None = Field(
        default=None, description="Upper bound of the confidence interval around the OR."
    )
    case_cohort_size: int | None = Field(
        default=None,
        description="Number of unrelated cases in the cohort (SM 4 recommends >= 100).",
    )
    case_variant_count: int | None = Field(
        default=None,
        description="Observations of the VBC in the case cohort (SM 4 recommends >= 5).",
    )
    control_cohort_size: int | None = Field(
        default=None, description="Number of individuals in the control cohort."
    )
    controls_matched: bool | None = Field(
        default=None,
        description=(
            "Whether cases and controls were matched (ancestry, sequencing "
            "platform, QC) per SM 4."
        ),
    )
    ascertainment_bias_considered: bool | None = Field(
        default=None,
        description="Whether ascertainment bias was considered (SM 4).",
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `from svcv4_model.case_control import CaseControlStudyEvidence` in module
order: `case` < `case_control` < `classification` (`case_control` vs
`classification` is decided at index 1, `a` < `l`), so the block goes **after
`from svcv4_model.case import (...)` and before `from svcv4_model.classification
import ...`** — or run `ruff check --fix`. Add `"CaseControlStudyEvidence"` to
`__all__` (ASCII order — between `Case`/`CaseRelative`… run `ruff check --fix` if
unsure). It is a `BaseModel`, so it gets one schema file.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes one new file,
`schemas/json/CaseControlStudyEvidence.schema.json`. **`git add` it** — the CI
drift gate (`git diff --quiet -- schemas/json docs/workflows/case-model.md`) does
not detect a brand-new *untracked* file, so a forgotten `git add` would pass CI
with the schema missing. `export_case_views.py` and `case-model.md` are
**unaffected** (CLN_CCS is not a `Workflow` entry).

### 5.4 Docs

- **`docs/workflows/hod/cln/index.md`** — the `!!! note "Not yet modeled here"`
  CLN_CCS admonition (from #27) flips to note the inputs are **now modeled** as
  `CaseControlStudyEvidence` (OR, CI, cohort sizes, robustness flags), keeping the
  process description (OR > 5.0 → +4.0; CI including 1.0 → no points) and the
  **exclusivity rule** (other CLN codes NA except CLN_DNV). State that scoring is
  documented, not computed. Optionally update the code table row's "Detailed
  here" cell for CLN_CCS.
- **`docs/reference/spec-alignment.md`** — in the SM 4 row, change the CLN_CCS
  clause from "…is **not yet modeled** here — a capture-only case-control study
  result … is the natural shape" to state it **is now captured** as
  `CaseControlStudyEvidence`.
- **`docs/reference/known-gaps.md`** — remove the "`CLN_CCS` (case-control
  studies) not modeled" model-gap row.
- **`docs/reference/model.md`** — add `::: svcv4_model.CaseControlStudyEvidence`
  after the last entry.

### 5.5 Tests: `tests/test_case_control.py`

- Round-trip a maximal `CaseControlStudyEvidence` (all fields) through
  `model_dump(mode="json")` → `model_validate`.
- Permissive-empty validates (`odds_ratio is None`); `extra="forbid"` rejects an
  unknown field.
- Importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (new `tests/test_case_control.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the new schema:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes.
- `grep -in "not modeled" docs/reference/known-gaps.md` no longer matches a
  CLN_CCS row.

## 7. Follow-up backlog

1. The OR/CI → points computation and the exclusivity-rule enforcement (with the
   deferred rule/method enforcement).
2. Finer eligibility structure (variant-AF-compatibility; ascertainment-bias
   sub-cases) if a downstream consumer needs it.
3. Reconcile with a formal VA-Spec case-control Study Result profile, alongside
   the same reconciliation planned for `PopulationEvidence`.

## 8. Delivery

Branch `feat/cln-ccs-modeling` off `main`. Single PR. CI: pytest, ruff, the
schema/docs drift gate, `mkdocs build --strict`.
