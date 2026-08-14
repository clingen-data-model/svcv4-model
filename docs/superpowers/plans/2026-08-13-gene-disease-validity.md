# Gene-Disease Validity + SM Link-Outs Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture ClinGen Gene-Disease Validity as a `WorkflowParameters` field and document its two gating semantics (without enforcing them), and add SM Google Doc link-outs across the docsite.

**Architecture:** One `StrEnum` + one optional field on `WorkflowParameters`; one applicability-matrix row (optional across all seven workflows); regenerate the two committed generated artifacts the change touches; then docs edits. No enforcement logic — consistent with the repo's scope boundary (evidence + classification, not method/rule enforcement).

**Tech Stack:** Python 3 / Pydantic v2 (`StrEnum`), YAML applicability matrix, `uv`, pytest, MkDocs (Material, `strict: true`).

**Spec:** `docs/superpowers/specs/2026-08-13-gene-disease-validity-design.md`

---

## File Structure

- `src/svcv4_model/case.py` — add `GeneDiseaseValidity` enum (near the other `StrEnum`s) and `WorkflowParameters.gene_disease_validity` field (bottom of file, in `WorkflowParameters`, alongside `mde`). Single responsibility: the model.
- `src/svcv4_model/__init__.py` — export `GeneDiseaseValidity` (import + `__all__`), mirroring how every other enum (`MOI`, `Zygosity`, …) is exported.
- `schemas/applicability/case_applicability.yaml` — add one `workflow_parameters` entry for `gene_disease_validity`.
- `tests/test_case.py` — extend `_maximal_params()` + add an enum-token/round-trip assertion covering the new field incl. `NOT_CLASSIFIED`.
- `schemas/json/WorkflowParameters.schema.json` — **generated** (via `scripts/export_schemas.py`); commit the regenerated file.
- `docs/workflows/case-model.md` — **generated** (via `scripts/export_case_views.py`); commit the regenerated file.
- `docs/reference/concepts.md` — flip the Gene-Disease Validity entry to "modeled" + add SM 18 upstream gate + SM link-out.
- `docs/reference/known-gaps.md` — remove the Gene-Disease Validity model-gap row; refresh the now-stale "Remaining Supplementary Materials" row (all 20 available SMs are ingested; the Drive-folder unreliability note no longer applies).
- `docs/reference/spec-alignment.md` — add per-SM Google Doc link-outs; note the GDV gate on the SM 18 row.

### SM → Google Doc URL table (for the link-outs; `source-material/…/INDEX.md` is gitignored, so the canonical list is embedded here)

URL form: `https://docs.google.com/document/d/<ID>/edit`

| SM | Title | ID |
|----|-------|----|
| 1 | Glossary of Terms and Abbreviations | `1CZBvar2it9Biq7tIf8UPa7caQV6Luo8eTScQD1ar5XM` |
| 2 | SVC v3 → v4.0 code status | `1arjMP34ylJY7xoaT2Hblqhzmnr7iBlLXlxgJgh2-URY` |
| 3 | Population Database Frequency | `1XON2eq4HSM-guWlqitEnb8PghY0quNbA7_1WmmxvLj8` |
| 4 | Clinical Observations | `17XnPmgTpzgQ8hfzOZNCcXIBwnNwbVkP0KIv3Dw5Bz_M` |
| 5 | Specific Phenotype and Segregation | `15arEcguLCzjiKKjibE3U0SNdrUjbKjpPoDoBPi2o40Y` |
| 6 | Missense Variants | `1eerqnL0kRq1se341-pxHxNI7HrPP9_kDlLL4eDvt-Gk` |
| 7 | Determining Critical Amino Acids | `1a64UTev9P35YGStF7YjaprB8znWS5OC5qbBZBMMLA_s` |
| 8 | Nonsense Variants | `1LFqIBpmw_plE8CFmRLbS2aeUYMibpVpxDjkbzJPHQsA` |
| 9 | Frameshift Variants | `1s-0OfNWc5h3pHiJFsFjmrdoEmitbJfXzkA29WQisaXo` |
| 10 | In-Frame InDel Variants | `1278qhDIDX94nlTUzwl7oIgZDLPc8YgEoFSVHXTHgRKk` |
| 11 | Canonical Splice Variants | `1LGSPW90-n0EbqGjfLKQ2MpTHPK8Ai-hUuMAkqqhyi80` |
| 12 | Intronic and Synonymous Variants | `1mqZnp72N3IC3adenRrVVufOuqkgPAgkD_D5vNmb32gc` |
| 13 | Single- or Multi-Exon Deletions | `1354VHASLCzQ-73Ha1-TdVL5t7RsVzq-Hgl1tqmuLQlk` |
| 14 | Single or Multiexon Duplication/Gain | `1yMgN3Y54V3fnaV_4zjVas1aoOtwfNNyL7hziZA3EdvQ` |
| 15 | Start Lost Variants | `1mn-IsUQSzV5traLH5G8KDa3DE1Q3OueTPfsDV9qBRvA` |
| 16 | Stop Lost Variants | `1OqEbx2FtQ2mL-7y3n6mpmQwCWuFIysFT_Vyo5lw3kWA` |
| 17 | Non-Coding Variants | *(not available — WG placeholder; no link)* |
| 18 | Molecular Mechanism and Exon Relevance | `1BLnsgxLY0TibwylFWz0SeGGeCusWwSokrgU4qsmBiaw` |
| 19 | Informative Variants | `1hNfdtdvDT4dob9oDBrL_UzVV_MYiWnwERfli76EAbyQ` |
| 20 | Functional Assay Evidence | `1X68otBl4YvdXlP1bOD83JO4kIod0Ol5BoLB4CLxqijA` |
| 21 | Genes with Multiple Disorders | `1_qkcglOow-l6hLKNH2QipxAJDOn3XZEmoC8Koq9EB6o` |

---

## Chunk 1: Model + matrix + regenerate

Add the enum, field, matrix entry, and tests together (they must land together — the
existing `test_param_matrix_and_model_paths_match_exactly` fails if the field and matrix
entry are out of sync), then regenerate the two committed artifacts.

### Task 1: Enum, field, export, matrix entry (TDD)

**Files:**
- Modify: `src/svcv4_model/case.py` (add enum near other `StrEnum`s; add field to `WorkflowParameters`)
- Modify: `src/svcv4_model/__init__.py` (export `GeneDiseaseValidity`)
- Modify: `schemas/applicability/case_applicability.yaml` (add `gene_disease_validity` entry in the `workflow_parameters` group)
- Test: `tests/test_case.py`

- [ ] **Step 1: Write the failing test.** In `tests/test_case.py`, import `GeneDiseaseValidity` in the existing `from svcv4_model.case import (…)` block, and add:

```python
def test_gene_disease_validity_accepts_all_values() -> None:
    for level in GeneDiseaseValidity:
        params = WorkflowParameters(gene_disease_validity=level)
        assert params.gene_disease_validity is level
    # NOT_CLASSIFIED is a real, distinct state (looked, none exists)…
    assert GeneDiseaseValidity.NOT_CLASSIFIED.value == "NOT_CLASSIFIED"
    # …and is distinct from the field being absent (not captured).
    assert WorkflowParameters().gene_disease_validity is None
```

Also add `gene_disease_validity=GeneDiseaseValidity.MODERATE` to the `WorkflowParameters(...)` built in `_maximal_params()` so the existing `test_workflow_parameters_round_trip` exercises the field through JSON.

- [ ] **Step 2: Run the test to verify it fails.**

Run: `uv run pytest tests/test_case.py::test_gene_disease_validity_accepts_all_values -v`
Expected: FAIL — `ImportError`/`cannot import name 'GeneDiseaseValidity'`.

- [ ] **Step 3: Add the enum** in `src/svcv4_model/case.py`, placed among the other `StrEnum`s (e.g. after `MOI`):

```python
class GeneDiseaseValidity(StrEnum):
    """ClinGen gene-disease validity classification for the gene↔MDE pair.

    A classification-level *precondition*, not a per-workflow evidence input:
    it gates which final classification tiers are reachable (Limited blocks
    P/LP; Disputed/Refuted block reporting) and, per SVCv4 Supplementary
    Material 18, whether the molecular-mechanism multiplier may be applied at
    all (usable only at MODERATE or higher; LIMITED or below is treated as an
    'Uncertain' mechanism and zeroed). Gating is documented, not enforced this
    phase.

    ``NOT_CLASSIFIED`` means ClinGen has no gene-disease validity
    classification for this gene↔MDE pair — distinct from the field being
    absent (``None``), which means the value was not captured at all.
    """

    DEFINITIVE = "DEFINITIVE"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    LIMITED = "LIMITED"
    DISPUTED = "DISPUTED"
    REFUTED = "REFUTED"
    NOT_CLASSIFIED = "NOT_CLASSIFIED"
```

- [ ] **Step 4: Add the field** to `WorkflowParameters` in the same file, alongside `mde`:

```python
    gene_disease_validity: GeneDiseaseValidity | None = Field(
        default=None,
        description=(
            "ClinGen gene-disease validity for the gene↔MDE pair — a "
            "classification-level precondition (see the enum docstring). "
            "Captured here; gating is documented, not enforced this phase."
        ),
    )
```

- [ ] **Step 5: Export the enum** in `src/svcv4_model/__init__.py`: add `GeneDiseaseValidity,` to the `from .case import (…)` block and `"GeneDiseaseValidity",` to `__all__`, mirroring the other enums. (It is a `StrEnum`, not a `BaseModel`, so it produces no schema file of its own — it is inlined as `$defs/GeneDiseaseValidity` in `WorkflowParameters.schema.json`.)

- [ ] **Step 6: Add the matrix entry** in `schemas/applicability/case_applicability.yaml`, in the `workflow_parameters` group near `mde`/`moi`:

```yaml
gene_disease_validity:
  model: workflow_parameters
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: o, CLN_ALTG: o, CLN_UAF: o, LOC_PHE: o, LOC_SEG: o }
  notes: "ClinGen gene-disease validity for the gene↔MDE pair; a classification-level precondition (gates final tier-reachability and the future SM18 mechanism multiplier), not a per-workflow field driver like moi"
```

- [ ] **Step 7: Run the full test suite to verify green** (the new test passes, and the parity test `test_param_matrix_and_model_paths_match_exactly` still passes because field + matrix entry landed together):

Run: `uv run pytest -q`
Expected: PASS (no failures). If `test_param_matrix_and_model_paths_match_exactly` fails, the matrix key must exactly equal the model field name `gene_disease_validity`.

- [ ] **Step 8: Commit.**

```bash
git add src/svcv4_model/case.py src/svcv4_model/__init__.py schemas/applicability/case_applicability.yaml tests/test_case.py
git commit -m "feat: capture Gene-Disease Validity on WorkflowParameters"
```

### Task 2: Regenerate the two committed artifacts

**Files:**
- Regenerate + Modify: `schemas/json/WorkflowParameters.schema.json`
- Regenerate + Modify: `docs/workflows/case-model.md`

- [ ] **Step 1: Regenerate both.**

```bash
uv run python scripts/export_schemas.py
uv run python scripts/export_case_views.py
```

- [ ] **Step 2: Verify the diff is exactly the two expected files and nothing else.**

Run: `git status --short schemas/json docs/workflows/case-model.md`
Expected: exactly two files modified —
- `schemas/json/WorkflowParameters.schema.json` (new `gene_disease_validity` property + `$defs/GeneDiseaseValidity`).
- `docs/workflows/case-model.md`. Its diff has **two** expected parts: (a) a new optional `gene_disease_validity` row in the WorkflowParameters applicability table, and (b) a new `"gene_disease_validity": "..."` line inside the **full** JSON example block of all seven per-workflow sections (it's `o`, so it appears in the full view and is dropped from the required-only view). Both are expected — not drift.

`Case.schema.json` and the per-workflow **Case** schema views must be unchanged (they derive from `Case`, not `WorkflowParameters`). If any other file shows as modified, stop and investigate.

- [ ] **Step 3: Commit the regenerated artifacts.**

```bash
git add schemas/json/WorkflowParameters.schema.json docs/workflows/case-model.md
git commit -m "chore: regenerate schema + case-model views for gene_disease_validity"
```

- [ ] **Step 4: Final drift-gate confirmation — matches CI exactly, must print CLEAN.**

Run: `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md && echo CLEAN`
Expected: `CLEAN` — regenerating again after committing produces no diff (this is the exact `.github/workflows/ci.yml` gate).

---

## Chunk 2: Documentation + SM link-outs

Pure docs. No TDD; verification is `mkdocs build --strict` + targeted greps. Note `mkdocs
build --strict` validates internal links only — external Google Doc URLs are a manual check.

### Task 3: `concepts.md` — Gene-Disease Validity entry → modeled

**Files:**
- Modify: `docs/reference/concepts.md` (the `## Gene-Disease Validity` section, currently starting with `!!! note "Not yet modeled here"`)

- [ ] **Step 1:** Remove the `!!! note "Not yet modeled here"` admonition from the Gene-Disease Validity section (it is now modeled as a captured field).

- [ ] **Step 2:** Keep the six-tier classification list (Definitive/Strong/Moderate/Limited/Disputed/Refuted) as the validity levels and the existing downstream tier-reachability explanation. Add a short paragraph for the **SM 18 upstream gate**: the molecular-mechanism multiplier is usable only at Moderate+ validity; Limited-or-below is treated as an 'Uncertain' mechanism and zeroed. Link "Supplementary Material 18" to `https://docs.google.com/document/d/1BLnsgxLY0TibwylFWz0SeGGeCusWwSokrgU4qsmBiaw/edit`. State that gating is documented, not enforced this phase.

- [ ] **Step 3:** Add the `NOT_CLASSIFIED`-vs-`None` distinction (looked-and-none-exists vs not-captured), and update **Current representation** to: `WorkflowParameters.gene_disease_validity` → `GeneDiseaseValidity` (six tiers + `NOT_CLASSIFIED`).

- [ ] **Step 4:** In the same file, add the SM 3 link-out on the existing DAFT mention (line ~226, "Supplementary Material 3" → `https://docs.google.com/document/d/1XON2eq4HSM-guWlqitEnb8PghY0quNbA7_1WmmxvLj8/edit`) and, in the MDE entry, link "Supplementary Material 21" → `https://docs.google.com/document/d/1_qkcglOow-l6hLKNH2QipxAJDOn3XZEmoC8Koq9EB6o/edit`.

- [ ] **Step 5: Verify.** `grep -n "Not yet modeled" docs/reference/concepts.md` must NOT match inside the Gene-Disease Validity section (Cohort Allele Frequency and DAFT sections keep theirs).

### Task 4: `known-gaps.md` — remove GDV row + refresh stale SM row

**Files:**
- Modify: `docs/reference/known-gaps.md`

- [ ] **Step 1:** Delete the `Gene-Disease Validity field` row from the Model-gaps table (per the page's own "remove or update the row once it's underway" instruction).

- [ ] **Step 2:** Update the "Remaining Supplementary Materials" row in the Documentation/content-gaps table: all 20 available SMs (SM 1–16, 18–21) are now ingested and linked from [Spec coverage](spec-alignment.md); SM 17 remains unavailable (WG placeholder). Drop the now-obsolete "Drive folder has inconsistent search-index visibility" phrasing.

- [ ] **Step 3:** Add SM 3/SM 4 link-outs on the DAFT and CLN_CCS/co-occurrence rows that name those supplements (use the URL table above).

- [ ] **Step 4: Verify.** `grep -n "Gene-Disease Validity" docs/reference/known-gaps.md` returns nothing.

### Task 5: `spec-alignment.md` — per-SM link-outs + SM 18 note

**Files:**
- Modify: `docs/reference/spec-alignment.md`

- [ ] **Step 1:** For each SM row (1–16, 18–21), link the supplement to its Google Doc (link the title text in the "Supplementary Material" column, using the URL table above). Leave SM 17's row link-less (not available).

- [ ] **Step 2:** Update the SM 18 row's coverage note: gene-disease validity — the Moderate+ gate SM 18 relies on — is now captured on `WorkflowParameters`; the mechanism multiplier itself is still to come with PFD.

- [ ] **Step 3: Verify.** Row count unchanged (21 rows); SM 17 still present and link-less.

### Task 6: Build + commit docs

- [ ] **Step 1: Build strict.**

Run: `uv run mkdocs build --strict`
Expected: builds with no warnings/errors (all internal links resolve). If a broken internal link appears, fix it — do not disable strict.

- [ ] **Step 2: Manual external-link spot check.** Open 1–2 of the new Google Doc links to confirm they resolve (CI does not check external URLs).

- [ ] **Step 3: Commit.**

```bash
git add docs/reference/concepts.md docs/reference/known-gaps.md docs/reference/spec-alignment.md
git commit -m "docs: model Gene-Disease Validity + add SM Google Doc link-outs"
```

---

## Done criteria

- `uv run pytest -q` green (incl. the new field test and the parity test).
- `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md` → clean.
- `uv run mkdocs build --strict` passes.
- `grep -rn "Not yet modeled" docs/reference/concepts.md` no longer matches the Gene-Disease Validity section; `grep -n "Gene-Disease Validity" docs/reference/known-gaps.md` returns nothing.
- No enforcement code added (scope boundary respected).
