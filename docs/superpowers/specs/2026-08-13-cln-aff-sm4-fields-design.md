# CLN_AFF Sub-Fields from SM 4 — Design Spec

**Date:** 2026-08-13
**Status:** Proposed
**Builds on:** `docs/superpowers/specs/2026-06-11-case-model-design.md` (PR #17),
`docs/superpowers/specs/2026-08-13-gene-disease-validity-design.md` (PR #23), and
`docs/superpowers/specs/2026-08-13-pop-modeling-design.md` (PR #25). Same
**capture + document, do not enforce** stance.

## 1. Purpose & goal

Add the two `CLN_AFF` (Affected Probands) evidence factors that Supplementary
Material 4 defines but the Case model does not yet carry:

1. The **gnomAD co-occurrence-likelihood bucket** used to place a biallelic
   `CLN_AFF` proband in the correct Table 2 row.
2. The **non-genetic-etiology** factor that (with testing thoroughness and
   alternative-variant presence) refines/downgrades a `CLN_AFF` category.

Both are tracked model gaps on [Known gaps](../../reference/known-gaps.md). This
pass **captures** them as fields and **documents** what they mean; it computes no
scores (consistent with the scope boundary — method/rule enforcement is deferred,
e.g. `validate_case`).

## 2. Source material (this pass)

- **Supplementary Material 4 (Clinical Observations)**, verbatim in
  `source-material/svcv4-supplements/SM04-clinical-observations.txt` (gitignored).
- **Existing model surfaces:** `src/svcv4_model/case.py`
  (`CompoundHetVariant` — "the second variant in a biallelic evaluation against a
  het VBC"; `CaseTesting` — with the sibling `covers_all_genes_relevant_to_mde`;
  `TriState`), `schemas/applicability/case_applicability.yaml`,
  `scripts/export_schemas.py`, `scripts/export_case_views.py`,
  `tests/test_case_applicability.py` (the model↔matrix parity tests).

## 3. Key findings driving this work

### 3.1 Co-occurrence likelihood — a biallelic `CLN_AFF` (Table 2) input

Verbatim (SM 4): "A unique requirement for biallelic assessment is evaluating the
statistical likelihood of observing two rare heterozygous variants within the
gene of interest. To confirm a low likelihood (<0.0001), analysts should use the
gnomAD co-occurrence data … sum the in trans and unphased counts and divide by
the total number of gnomAD v2 exomes (125,748)." Table 2 has exactly two buckets
for this quantity: **"<0.0001"** and **">0.0001- 0.01"**. It is a property of the
VBC paired with the second variant in trans — so it belongs on
`CompoundHetVariant`. Because SM 4 also describes a case where the analyst does
not/ cannot compute it (falling back to the next most permissive combination), a
`NOT_ASSESSED` state is meaningful and distinct from "not captured" (`None`).

### 3.2 Non-genetic etiology — a `CLN_AFF` refinement factor

Verbatim (SM 4, monoallelic and biallelic paragraphs): the CLN_AFF categories are
"further refined by the thoroughness of genetic testing … the likelihood of a
non-genetic etiology, or the presence of any alternative variant that could
explain the clinical presentation." The model already carries testing
thoroughness (`testing.covers_all_genes_relevant_to_mde`) and alternative-variant
presence (`additional_variant_exists` / `additional_variants`), but not the
non-genetic-etiology factor. It is a proband-workup judgment sibling to
`covers_all_genes_relevant_to_mde`, so it goes on `CaseTesting` as a `TriState`.

SM 4 names this factor explicitly in the `CLN_AFF` tables only; this pass scopes
it to `CLN_AFF` (not `CLN_DNV`), avoiding an unsourced inference.

### 3.3 Both fields are `CLN_AFF`-only, optional, and add no scoring

Neither field changes which *other* fields apply, and neither is computed. In the
applicability matrix both are `o` (optional) for `CLN_AFF` and `x` (not
applicable) for every other workflow — including `LOC_SEG`, where
`compound_het_variant` itself is `o` but the co-occurrence likelihood (a CLN_AFF
scoring input) does not apply. A flat `o` is chosen over a conditional `c` rule:
the true condition is "biallelic evaluation", which spans AR *and* X-linked-
recessive-XX and depends on `WorkflowParameters.moi`, so no clean matrix `rule`
expresses it — and capture-only does not need one.

### 3.4 Model↔matrix parity is test-enforced

`tests/test_case_applicability.py::test_case_matrix_and_model_paths_match_exactly`
enumerates every `Case` dotted field path (including nested paths like
`compound_het_variant.id` and `testing.method`) against the matrix. The two new
nested paths therefore **must** get matrix entries in the same change, or that
test fails.

## 4. Scope

**In scope:**
- New `CoOccurrenceLikelihood` enum + `CompoundHetVariant.co_occurrence_likelihood`
  field (§5.1).
- `CaseTesting.non_genetic_etiology_excluded: TriState | None` field (§5.1).
- Two applicability-matrix entries, `o` for `CLN_AFF`, `x` elsewhere (§5.2).
- Regenerate the committed schemas and `case-model.md` (§5.3).
- Export `CoOccurrenceLikelihood` from the package root (§5.1).
- Docs: `cln-aff.md` documents both fields; `known-gaps.md` removes the two rows;
  `spec-alignment.md` SM 4 row note (§5.4).
- Tests (§5.5).

**Out of scope / deferred:**
- Table 2 row-selection / any `CLN_AFF` scoring computation.
- A conditional (`c`) matrix rule tying co-occurrence to biallelic MOI (§3.3).
- Extending non-genetic-etiology to `CLN_DNV` (§3.2).
- Structuring the raw gnomAD co-occurrence counts (in-trans / unphased / total) —
  only the resulting bucket is captured.

## 5. Content changes, item by item

### 5.1 Model (`src/svcv4_model/case.py`) + export (`__init__.py`)

New enum, near the other `StrEnum`s:

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

Add to `CompoundHetVariant`:

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

Add to `CaseTesting`:

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

Export `CoOccurrenceLikelihood` from `src/svcv4_model/__init__.py` (imports +
`__all__`, alphabetical), mirroring the other enums. (`CompoundHetVariant` and
`CaseTesting` are already exported; adding fields to them needs no new export.)

### 5.2 Applicability matrix (`schemas/applicability/case_applicability.yaml`)

Add, in the `case` group next to the sibling entries:

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

### 5.3 Regenerate committed artifacts

```bash
uv run python scripts/export_schemas.py       # Case, CompoundHetVariant, CaseTesting, case/CLN_AFF views
uv run python scripts/export_case_views.py     # docs/workflows/case-model.md
```

Expected changed files: `schemas/json/Case.schema.json`,
`schemas/json/CompoundHetVariant.schema.json`,
`schemas/json/CaseTesting.schema.json`,
`schemas/json/case/CLN_AFF.schema.json`, and `docs/workflows/case-model.md`.
Other per-workflow `case/*` views are unchanged (both fields are `x` there). CI
drift gate: `git diff --quiet -- schemas/json docs/workflows/case-model.md`.

### 5.4 Docs

- **`docs/workflows/hod/cln/cln-aff.md`** — in the evidence-capture content, add
  the two fields: the co-occurrence likelihood bucket (`CompoundHetVariant`,
  biallelic row-selection) and `non_genetic_etiology_excluded` (`CaseTesting`
  refinement factor), each noted as *captured; scoring documented, not computed*.
  Link [SM 4](https://docs.google.com/document/d/17XnPmgTpzgQ8hfzOZNCcXIBwnNwbVkP0KIv3Dw5Bz_M/edit).
- **`docs/reference/known-gaps.md`** — remove the "gnomAD co-occurrence-likelihood
  bucket" and "'Non-genetic etiology excluded' flag" model-gap rows.
- **`docs/reference/spec-alignment.md`** — the SM 4 row already reads "Modeled";
  append a short note that the two remaining `CLN_AFF` completeness factors
  (co-occurrence bucket, non-genetic-etiology) are now captured.

### 5.5 Tests (`tests/test_case.py`)

- Extend the maximal `CompoundHetVariant`/`Case` fixtures (or add a focused test)
  so `co_occurrence_likelihood` and `non_genetic_etiology_excluded` round-trip
  through `model_dump(mode="json")` → `model_validate`.
- Assert each `CoOccurrenceLikelihood` value is accepted, and `NOT_ASSESSED` is
  distinct from `None`.
- `tests/test_case_applicability.py::test_case_matrix_and_model_paths_match_exactly`
  must stay green (the new matrix entries satisfy it).

## 6. Quality gates

- `uv run pytest -q` green.
- `uv run ruff check` + `uv run ruff format --check .` clean (line-length 100 —
  keep long field descriptions wrapped).
- Drift gate clean after committing regenerated files:
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md`.
- `uv run mkdocs build --strict` passes.
- `grep -in "co-occurrence-likelihood bucket\|Non-genetic etiology excluded" docs/reference/known-gaps.md` returns nothing.

## 7. Follow-up backlog (explicitly not this pass)

1. `CLN_AFF` scoring computation (Table 1/2 row selection → points), with the
   deferred rule/method enforcement.
2. Non-genetic-etiology for `CLN_DNV`, if a later reading of SM 4's DNV tables
   shows it applies there.
3. Structuring the raw gnomAD co-occurrence counts if reproducibility needs them.
4. Remaining known-gaps items: PFD; `CLN_CCS` (blocked on a future SVCv4 version).

## 8. Delivery

Branch `feat/cln-aff-sm4-fields` off `main`. Single PR. CI: pytest, ruff, the
schema/docs drift gate, and `mkdocs build --strict`.
