# Missense — `MIS_`/`SPL_` Comparison — Design Spec

**Date:** 2026-08-19
**Status:** Proposed
**Builds on:** the Missense amino-acid path (`MissenseAminoAcidAssessment`, #33)
and the splice paths (`MissenseSpliceAssessment`, #34). Same **capture +
document, do not compute** stance. This increment (**2c**) completes the Missense
workflow.

## 1. Purpose & goal

Model the final step of the SVCv4 Missense workflow (SM 6): comparing the
amino-acid `MIS_` total with the splice `SPL_` total and selecting one to apply
to the VBC. A single umbrella entity `MissenseAssessment` holds **both**
sub-assessments (SM 6 requires saving both), records which path the analyst
applied, and the final applied total. The "take the higher" rule is documented,
not computed.

## 2. Source material

- **Supplementary Material 6 (Missense)**, verbatim in
  `source-material/svcv4-supplements/SM06-missense.txt` — the comparison rule
  (line 157) and Table 1.
- **Existing architecture:** `src/svcv4_model/missense.py` (the two shipped
  sub-assessments this composes).

## 3. Key findings driving this work

### 3.1 The comparison rule (SM 6 L157)

Verbatim intent: compare the amino-acid path final value with the splice path
final value —

- if the splice value is **negative**, use the **amino-acid** path;
- if the splice value is **positive**, use the **higher** (more positive) of the
  two;
- if both are positive **and equal**, use the **amino-acid** path (higher prior
  probability the effect is via the amino-acid change).

The applied code is `MIS_ −8.0 to +9.0` or `SPL_ −8.0 to +10.0` accordingly. The
curation system **must save the scoring of the other pathway** so a future
re-evaluation can reconsider. All documented, not computed.

### 3.2 An umbrella entity that embeds both sub-assessments

`MissenseAssessment` composes the two already-shipped assessments as optional
fields (satisfying "save both"), plus a `selected_path` (which was applied) and
the `applied_total` (the final points). It changes neither sub-assessment. It is
a standalone PFD payload — **not** part of `Case`, no `Workflow` enum entry, no
applicability matrix; `case-model.md` is unaffected.

## 4. Scope

**In scope:**

- Extend `src/svcv4_model/missense.py`: `MissenseSelectedPath` enum;
  `MissenseAssessment` model (§5.1).
- Export the two new public names from `__init__.py` (§5.2).
- Regenerate JSON Schemas — one new file (§5.3).
- Docs: add a comparison section on `docs/workflows/pfd/missense.md`, flip the
  admonition to "complete", update `spec-alignment.md` SM 6 row and
  `known-gaps.md`, append to `model.md` (§5.4).
- Tests: extend `tests/test_missense.py` (§5.5).

**Out of scope / deferred:**

- The motif-variant flag (with SM 7).
- All point computation (the comparison itself, the parent totals).

## 5. Content changes, item by item

### 5.1 Extend `src/svcv4_model/missense.py`

Append this enum and model after the existing splice-path code:

```python
class MissenseSelectedPath(StrEnum):
    """Which missense path was applied to the VBC after the comparison (SM 6)."""

    AMINO_ACID = "AMINO_ACID"
    SPLICE = "SPLICE"


class MissenseAssessment(BaseModel):
    """The overall missense workflow assessment (SM 6).

    Holds both the amino-acid (MIS_) and splice (SPL_) path assessments — SM 6
    requires saving both — plus which path was applied and the final applied
    total. The comparison rule (splice-negative → amino-acid; else the higher;
    ties → amino-acid) is documented, not computed.
    """

    model_config = ConfigDict(extra="forbid")

    amino_acid: MissenseAminoAcidAssessment | None = Field(
        default=None, description="The amino-acid (MIS_) path assessment."
    )
    splice: MissenseSpliceAssessment | None = Field(
        default=None, description="The splice (SPL_) path assessment."
    )
    selected_path: MissenseSelectedPath | None = Field(
        default=None, description="Which path was applied to the VBC after the comparison."
    )
    applied_total: float | None = Field(
        default=None, description="The final points applied to the VBC (the MIS_ or SPL_ total)."
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `MissenseAssessment` and `MissenseSelectedPath` to the existing
`from svcv4_model.missense import (...)` block and to `__all__`, keeping both
sorted. `MissenseAssessment` sorts **before** `MissenseAminoAcidAssessment`?
No — compare `MissenseA…`: `MissenseAssessment` vs `MissenseAminoAcidAssessment`
share `MissenseA`, then `s`(`Assessment`) vs `m`(`AminoAcid`) → `m` < `s`, so
`MissenseAminoAcidAssessment` < `MissenseAssessment`. So `MissenseAssessment`
goes **after `MissenseAminoAcidAssessment`** and before `MissenseInfCategory`
(`As` < `In`). `MissenseSelectedPath` sorts **after `MissensePredictor`** and
before `MissenseSpliceAssessment` (`Se` < `Sp`). Verify exact positions with
`sorted()` at implementation time. `__all__` is hand-sorted (ruff does not sort
it). The enum gets no schema file; the `BaseModel` does.

### 5.3 Regenerate JSON Schemas

`uv run python scripts/export_schemas.py` writes **one** new file —
`MissenseAssessment.schema.json` (which `$ref`s `MissenseAminoAcidAssessment`,
`MissenseSpliceAssessment`, and the `MissenseSelectedPath` enum under `$defs`).
**`git add` it** — the drift gate does not flag untracked files.
`export_case_views.py` and `case-model.md` are unaffected (no `Workflow` entry).
CI drift gate: `git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/pfd/missense.md`** — add a
  `## Selecting the final code (\`MIS_\` vs \`SPL_\`)` section after the splice
  section: the analyst compares the two totals, `MissenseAssessment` holds both
  (`amino_acid`/`splice`), records `selected_path` and `applied_total`, and the
  rule (splice-negative → amino-acid; else the higher; ties → amino-acid; save
  both) is *documented, not computed*. Flip the top admonition to "complete —
  both paths + the comparison modeled".
- **`docs/reference/spec-alignment.md`** — SM 6 row: fully modeled (inputs), incl.
  the `MIS_`/`SPL_` comparison; note only the motif variant (SM 7) is outstanding.
- **`docs/reference/known-gaps.md`** — the "Full PFD modeling" row: the Missense
  workflow is now complete (both paths + comparison); remaining = SM 7, the other
  variant types, and the scoring computation.
- **`docs/reference/model.md`** — add `::: svcv4_model.MissenseAssessment` after
  the `MissenseSpliceAssessment` entry.

### 5.5 Tests: extend `tests/test_missense.py`

- Round-trip a maximal `MissenseAssessment` (both sub-assessments populated via the
  existing `_maximal_assessment()` / `_maximal_splice_assessment()` helpers, a
  `selected_path`, and an `applied_total`) through `model_dump(mode="json")` →
  `model_validate`.
- Permissive-empty validates; `extra="forbid"` rejects unknown fields.
- Each `MissenseSelectedPath` value round-trips.
- The two new names are importable from the package root.

## 6. Quality gates

- `uv run pytest -q` green (extended `tests/test_missense.py`).
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100).
- Drift gate clean after committing the new schema:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes.

## 7. Follow-up backlog

1. The motif-variant flag + rule with **SM 7** Critical Amino Acids.
2. The other variant-type workflows (Nonsense, Frameshift, Splice, …).
3. The full PFD scoring computation (the per-path pipelines and the comparison).

## 8. Delivery

Branch `feat/pfd-missense-compare` off `main`. Single PR for this increment (2c);
it completes the Missense workflow. CI: pytest, ruff, the schema/docs drift gate,
`mkdocs build --strict`.
