# CLN_AFF SM 4 Sub-Fields Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture the two SM 4 `CLN_AFF` factors the Case model lacks — the gnomAD co-occurrence-likelihood bucket and the non-genetic-etiology flag — documenting their meaning without computing scores.

**Architecture:** One new `StrEnum` + one field on `CompoundHetVariant` + one `TriState` field on `CaseTesting`, each with a matching applicability-matrix entry (optional for `CLN_AFF`, not-applicable elsewhere). Regenerate the committed schemas + `case-model.md`. Docs flip the two known-gaps rows to modeled. No scoring.

**Tech Stack:** Python 3 / Pydantic v2 (`StrEnum`, `ConfigDict(extra="forbid")`), YAML matrix, `uv`, pytest, ruff (line-length 100), MkDocs (`strict: true`).

**Spec:** `docs/superpowers/specs/2026-08-13-cln-aff-sm4-fields-design.md`

---

## File Structure

- `src/svcv4_model/case.py` — add `CoOccurrenceLikelihood` enum; add `co_occurrence_likelihood` to `CompoundHetVariant`; add `non_genetic_etiology_excluded` to `CaseTesting`.
- `src/svcv4_model/__init__.py` — export `CoOccurrenceLikelihood` (imports + `__all__`).
- `schemas/applicability/case_applicability.yaml` — two new `model: case` entries.
- `tests/test_case.py` — extend `_maximal_case()` fixture + a focused enum test.
- `schemas/json/{Case,CompoundHetVariant,CaseTesting}.schema.json`, `schemas/json/case/CLN_AFF.schema.json` — **generated**; commit.
- `docs/workflows/case-model.md` — **generated**; commit.
- `docs/workflows/hod/cln/cln-aff.md`, `docs/reference/known-gaps.md`, `docs/reference/spec-alignment.md` — docs.

**Conventions:** every field optional (`Field(default=None, ...)`); `ConfigDict(extra="forbid")`; wrap any field `description` >100 chars with parenthesized string concatenation (ruff E501 + `ruff format --check` run in CI); `StrEnum` members `VALUE = "VALUE"`.

---

## Chunk 1: Model + matrix + regenerate

### Task 1: Enum + two fields + matrix entries + tests (TDD)

**Files:**
- Modify: `src/svcv4_model/case.py`, `src/svcv4_model/__init__.py`, `schemas/applicability/case_applicability.yaml`
- Test: `tests/test_case.py`

- [ ] **Step 1: Write the failing test.** In `tests/test_case.py`:
  - Add `CoOccurrenceLikelihood` to the existing `from svcv4_model.case import (…)` block. Ruff's isort (`I`) is enabled, so place it in sorted order — between `CompoundHetVariant` and `Gene` (case-insensitive) — or just run `uv run ruff check --fix tests/test_case.py` after.
  - Extend `_maximal_case()`: in the `CompoundHetVariant(...)` add `co_occurrence_likelihood=CoOccurrenceLikelihood.LT_0_0001`, and in the `CaseTesting(...)` add `non_genetic_etiology_excluded=TriState.TRUE`.
  - Add:

```python
def test_co_occurrence_likelihood_accepts_all_values() -> None:
    for level in CoOccurrenceLikelihood:
        chv = CompoundHetVariant(co_occurrence_likelihood=level)
        assert chv.co_occurrence_likelihood is level
    # NOT_ASSESSED (looked, didn't compute) is distinct from absent (not captured)
    assert CoOccurrenceLikelihood.NOT_ASSESSED.value == "NOT_ASSESSED"
    assert CompoundHetVariant().co_occurrence_likelihood is None


def test_non_genetic_etiology_excluded_accepts_tristate() -> None:
    for state in TriState:
        testing = CaseTesting(non_genetic_etiology_excluded=state)
        assert testing.non_genetic_etiology_excluded is state
    assert CaseTesting().non_genetic_etiology_excluded is None
```

- [ ] **Step 2: Run to verify failure.**

Run: `uv run pytest tests/test_case.py::test_co_occurrence_likelihood_accepts_all_values -q`
Expected: FAIL — `ImportError: cannot import name 'CoOccurrenceLikelihood'`.

- [ ] **Step 3: Add the enum** in `src/svcv4_model/case.py`, near the other `StrEnum`s:

```python
class CoOccurrenceLikelihood(StrEnum):
    """gnomAD co-occurrence likelihood that the VBC and the in-trans variant are
    two independent rare heterozygous variants, used to place a biallelic
    ``CLN_AFF`` proband in the correct scoring-table row (SVCv4 Supplementary
    Material 4). Computed as (in-trans + unphased counts) / gnomAD v2 exome
    total; SM 4 buckets it as <0.0001 or >0.0001-0.01.

    ``NOT_ASSESSED`` means the analyst did not/could not compute it — distinct
    from the field being absent (``None``), which means it was not captured.
    """

    LT_0_0001 = "LT_0_0001"
    BETWEEN_0_0001_0_01 = "BETWEEN_0_0001_0_01"
    NOT_ASSESSED = "NOT_ASSESSED"
```

- [ ] **Step 4: Add the field to `CompoundHetVariant`** (in the same file):

```python
    co_occurrence_likelihood: CoOccurrenceLikelihood | None = Field(
        default=None,
        description=(
            "gnomAD co-occurrence likelihood bucket for the VBC + in-trans "
            "variant pairing (biallelic CLN_AFF, SM 4 Table 2). Captured; "
            "row-selection/scoring is documented, not computed."
        ),
    )
```

- [ ] **Step 5: Add the field to `CaseTesting`**:

```python
    non_genetic_etiology_excluded: TriState | None = Field(
        default=None,
        description=(
            "Whether a non-genetic etiology for the proband's phenotype has "
            "been excluded — a CLN_AFF refinement factor (SM 4), sibling to "
            "covers_all_genes_relevant_to_mde."
        ),
    )
```

- [ ] **Step 6: Export the enum** in `src/svcv4_model/__init__.py`: add `CoOccurrenceLikelihood,` to the `from svcv4_model.case import (…)` block (isort slot: between `CompoundHetVariant` and `Gene`, case-insensitive — or `ruff check --fix`) and `"CoOccurrenceLikelihood",` to `__all__` (alphabetical — between `CompoundHetVariant` and `DaftCalculatorInputs`; `__all__` order is not ruff-enforced).

- [ ] **Step 7: Add the two matrix entries** in `schemas/applicability/case_applicability.yaml`. Place each next to its siblings (the `compound_het_variant.*` block and the `testing.*` block). No `model:` key (default `case`):

```yaml
compound_het_variant.co_occurrence_likelihood:
  applicability: { CLN_AFF: o, CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x, LOC_PHE: x, LOC_SEG: x }
  value: "LT_0_0001, BETWEEN_0_0001_0_01, NOT_ASSESSED"
  notes: "gnomAD co-occurrence likelihood bucket for biallelic CLN_AFF (SM 4 Table 2); captured, not scored"
```

```yaml
testing.non_genetic_etiology_excluded:
  applicability: { CLN_AFF: o, CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x, LOC_PHE: x, LOC_SEG: x }
  value: "TRUE / FALSE / UNKNOWN"
  notes: "whether a non-genetic etiology was excluded — CLN_AFF refinement factor (SM 4)"
```

- [ ] **Step 8: Run the full suite + lint to verify green.**

Run: `uv run pytest -q && uv run ruff check src/svcv4_model/case.py src/svcv4_model/__init__.py tests/test_case.py && uv run ruff format --check src/svcv4_model/case.py src/svcv4_model/__init__.py tests/test_case.py`
Expected: all PASS. In particular the parity test `test_case_matrix_and_model_paths_match_exactly` passes (both new nested paths now have matrix entries). If it fails complaining about a path, the matrix key must exactly equal the dotted field path.

- [ ] **Step 9: Commit.**

```bash
git add src/svcv4_model/case.py src/svcv4_model/__init__.py schemas/applicability/case_applicability.yaml tests/test_case.py
git commit -m "feat: capture CLN_AFF co-occurrence-likelihood + non-genetic-etiology fields"
```

### Task 2: Regenerate committed artifacts

**Files:** generated `schemas/json/*` + `docs/workflows/case-model.md`

- [ ] **Step 1: Regenerate.**

```bash
uv run python scripts/export_schemas.py
uv run python scripts/export_case_views.py
```

- [ ] **Step 2: Verify the changed set.**

Run: `git status --short schemas/json docs/workflows/case-model.md`
Expected: modified — `schemas/json/Case.schema.json`, `schemas/json/CompoundHetVariant.schema.json`, `schemas/json/CaseTesting.schema.json`, `schemas/json/case/CLN_AFF.schema.json`, and `docs/workflows/case-model.md`. The other `schemas/json/case/*.schema.json` (CLN_DNV, CLN_ALTV, CLN_ALTG, CLN_UAF, LOC_PHE, LOC_SEG) must be **unchanged** (the new fields are `x` there and get pruned). If any other `case/*` view changed, stop and investigate.

- [ ] **Step 3: Commit the regenerated artifacts.**

```bash
git add schemas/json docs/workflows/case-model.md
git commit -m "chore: regenerate schemas + case-model views for CLN_AFF SM4 fields"
```

- [ ] **Step 4: Confirm the drift gate (exact CI command).**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo CLEAN`
Expected: `CLEAN`.

---

## Chunk 2: Documentation

### Task 3: `cln-aff.md` — document both fields

**Files:** Modify `docs/workflows/hod/cln/cln-aff.md`

- [ ] **Step 1:** Read the file first (it has a "What evidence to capture" section). Add the co-occurrence likelihood field: for a **biallelic** `CLN_AFF` proband (VBC het with a variant in trans), `CompoundHetVariant.co_occurrence_likelihood` records the gnomAD-derived bucket (`<0.0001` vs `>0.0001–0.01`, or `NOT_ASSESSED`) that SM 4 Table 2 uses to select a row — noted as *captured; row-selection is documented, not computed*.

- [ ] **Step 2:** Add the non-genetic-etiology field: `testing.non_genetic_etiology_excluded` (TriState) records whether a non-genetic cause was excluded — one of SM 4's CLN_AFF refinement factors alongside testing thoroughness and alternative-variant presence.

- [ ] **Step 3:** Ensure an SM 4 link exists on the page: `https://docs.google.com/document/d/17XnPmgTpzgQ8hfzOZNCcXIBwnNwbVkP0KIv3Dw5Bz_M/edit` (add if absent).

### Task 4: `known-gaps.md` — remove the two rows

**Files:** Modify `docs/reference/known-gaps.md`

- [ ] **Step 1:** Remove the "gnomAD co-occurrence-likelihood bucket" model-gap row and the "'Non-genetic etiology excluded' flag" model-gap row. Prefer exact-string Edit; if it fails on a special char, use `grep -v` with a unique substring per row (e.g. `grep -v 'gnomAD co-occurrence-likelihood bucket'` then `grep -v 'Non-genetic etiology excluded'`).

- [ ] **Step 2: Verify.** `grep -cE "co-occurrence-likelihood bucket|Non-genetic etiology excluded" docs/reference/known-gaps.md` returns 0.

### Task 5: `spec-alignment.md` — SM 4 note

**Files:** Modify `docs/reference/spec-alignment.md`

- [ ] **Step 1:** The SM 4 row already reads "**Modeled**". Append a short clause that the two remaining `CLN_AFF` completeness factors — the co-occurrence-likelihood bucket and the non-genetic-etiology flag — are now captured too.

### Task 6: Build + commit docs

- [ ] **Step 1: Build strict.**

Run: `uv run mkdocs build --strict`
Expected: no warnings/errors. Fix any broken internal link (don't disable strict). If the plan doc itself trips a relative-link warning, wrap the offending `[text](../path)` example in backticks.

- [ ] **Step 2: Commit.**

```bash
git add docs/workflows/hod/cln/cln-aff.md docs/reference/known-gaps.md docs/reference/spec-alignment.md
git commit -m "docs: document CLN_AFF co-occurrence + non-genetic-etiology fields"
```

---

## Done criteria

- `uv run pytest -q` green (new tests; parity test green).
- `uv run ruff check` + `uv run ruff format --check .` clean.
- `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md` → clean.
- `uv run mkdocs build --strict` passes.
- `grep -cE "co-occurrence-likelihood bucket|Non-genetic etiology excluded" docs/reference/known-gaps.md` → 0.
- No scoring-computation code added (scope boundary respected).
