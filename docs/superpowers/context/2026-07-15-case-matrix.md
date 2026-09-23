# Case applicability matrix — context & maintenance guide

**Date captured:** 2026-07-15
**Status:** Living reference (matrix + generators as of PR #17, merged to `main` 2026-06-11, squash `af87eaa`)

This file preserves the context around **creating and modifying the Case
applicability matrix table** — the `r/o/c/x` grid that drives which Case
attributes apply to each CLN workflow. Read this before touching the matrix,
the exporter, or the generated docs table. Design rationale lives in the spec
([`../specs/2026-06-11-case-model-design.md`](../specs/2026-06-11-case-model-design.md));
this is the operational "how it fits together and how to change it" companion.

## What the matrix is

The **Case** entity is a permissive superset of every attribute a curator
captures for a single clinical (CLN) observation. Every field is optional at
the Pydantic layer. The *applicability matrix* is the single source of truth
that says, per attribute × per workflow, whether the attribute is:

| Code | Meaning |
|------|---------|
| `r` | required |
| `o` | optional |
| `c` | conditional — applies only when a stated `rule` holds |
| `x` | not applicable |

The five workflows (matrix columns) are:

| Code | Label | Generalization |
|------|-------|----------------|
| `CLN_AFF` | Affected | — |
| `CLN_DNV` | De novo | — |
| `CLN_ALTV` | Alternative Cause-Variant | `CLN_ALT` |
| `CLN_ALTG` | Alternative Cause-Gene | `CLN_ALT` |
| `CLN_UAF` | Unaffected | — |

`CLN_ALTV` + `CLN_ALTG` generalize to `CLN_ALT` but are kept as separate matrix
columns because their rules diverge (e.g. `pheno_severity`, `phase_in_ref_to_vbc`).

> **Scope boundary:** this repo captures **evidence + classification**; ClinGen
> CSpec owns methods/rules. The matrix therefore *stores and documents* the
> conditional rules but does **not** enforce them (no `validate_case` yet).

## The pieces and how they connect

The matrix is one YAML file that everything else derives from. Data flows one
direction: **YAML → loader → exporter → (per-workflow schemas + generated docs table)**.

| File | Role |
|------|------|
| `schemas/applicability/case_applicability.yaml` | **THE source of truth.** Keyed by dotted field path; each entry has `applicability` (the 5-workflow row) + optional `value`, `notes`, `rule`. |
| `src/svcv4_model/case.py` | The permissive superset `Case` Pydantic model + sub-models + enums + the `Workflow` enum. Every field optional. |
| `src/svcv4_model/case_applicability.py` | Loader (`load_matrix`, `field_paths`, `workflow_codes`). Deliberately **not** a Pydantic model and **not** in `__all__`, so `export_schemas.py` auto-discovery won't emit a stray schema for it. |
| `scripts/export_case_views.py` | Generator. Reads model + matrix, writes the five per-workflow JSON Schemas and the docs matrix table. |
| `schemas/json/Case.schema.json` | Exported superset schema (via the *other* exporter, `export_schemas.py`, once `Case` is in `__all__`). |
| `schemas/json/case/CLN_*.schema.json` | Five derived per-workflow schemas (via `export_case_views.py`). Do not edit by hand. |
| `docs/workflows/case-model.md` | Narrative + the generated matrix table + per-workflow JSON examples, all between the `<!-- BEGIN/END GENERATED: applicability tables -->` markers. |
| `tests/test_case.py`, `tests/test_case_applicability.py`, `tests/test_case_views.py` | Round-trip, matrix-shape (no orphans/gaps, codes ∈ {r,o,c,x}), and generated-in-sync tests. |

### Two exporters, both must run in CI

- `export_schemas.py` — auto-discovers public models in `__all__`; emits `schemas/json/Case.schema.json`.
- `export_case_views.py` — the separate generator for `schemas/json/case/CLN_*.schema.json` **and** the docs table.

CI (`.github/workflows/ci.yml`, step "Export schemas and check no drift") runs
**both**, then does a drift check:

```
uv run python scripts/export_schemas.py
uv run python scripts/export_case_views.py
git diff --quiet -- schemas/json docs/workflows/case-model.md   # fails if stale
```

So: **regenerate and commit** after any matrix/model change, or CI fails.

## How the generator turns codes into schemas

`build_workflow_schema()` derefs the superset `Case` JSON Schema, then prunes it
per workflow using the matrix codes and rules:

- `r` → field added to that object's `required[]`.
- `o` / `c` → field present, not required.
- `x` → field **removed** from that workflow's schema.
- `enum_exclude` rule → the named token dropped from the field's enum.
- `fixed` rule → field pinned via `const`.
- `requires` rule → recorded as an informational `x-svcv4-conditional` annotation (NOT enforced).

The docs matrix table (`_matrix_table()`) renders every field with its nested
depth (`↳` + `&nbsp;` indent), a colored `R/C/O/X` span per workflow, the
property name, and a **Notes** column assembled from `value` + `notes` + a
human summary of any `rule`.

### The three machine-readable rule kinds

Everything else stays as free-text `notes`. The three structured kinds:

- **`requires`** — field applies only when another field/context holds.
  `{ requires: { field: additional_variant_exists, equals: "TRUE" } }` or
  `{ requires: { context: "biallelic disease eval with a het VBC" } }`.
- **`enum_exclude`** — a workflow drops one enum value.
  `{ workflow: CLN_ALTG, effect: enum_exclude, value: BIALLELIC_LT_EXPECTED }`.
- **`fixed`** — a value pinned in a workflow.
  `{ workflow: CLN_AFF, effect: fixed, value: HET }`.

## Non-obvious facts worth preserving

- **Column order differs from the source sheet.** The matrix and generated table
  order columns **AFF / DNV / ALTV / ALTG / UAF** (the `Workflow` enum order).
  The source Google Sheet (tab `138412089`) lists them **UAF / ALTG / ALTV / DNV / AFF**.
  Reconcile carefully when transcribing.
- **`c*` collapsed to `c`.** The sheet flags some conditional cells `c*`; we
  collapse to plain `c` (applicability-identical). If distinct per-workflow
  conditions emerge later, attach an explicit rule id to the `c` cell rather than
  overloading the token — the token set stays `{r, o, c, x}`.
- **`TriState` vs `null`.** Yes/no fields use `TriState` (`TRUE/FALSE/UNKNOWN`),
  not bool. `UNKNOWN` = curator looked and couldn't tell; `null` (absent) = not
  captured at all. Semantically distinct.
- **VBC referenced by `id` only.** A Case records case-level observations
  (e.g. case-level `zygosity`); the full VBC/MDE context lives in the parent
  classification, not duplicated in the Case.
- **`classification` / `phase_confidence` are placeholder strings** this phase,
  to be tightened against the SVCv4 VA-Spec community profile later.
- **`compound_het_variant` is AFF-only**; other workflows use `additional_variants`.
  Compound-het *additional* variants are not supported.
- **`ARRAYS` set in the exporter** (`case_proband_info.phenotypes`,
  `additional_variants`) is asserted against the matrix at generation time — if
  you add/rename an array field, update this set or the assert fails.

## To modify the matrix (checklist)

1. **Edit `schemas/applicability/case_applicability.yaml`** — the only place
   `r/o/c/x`, `value`, `notes`, and `rule` are maintained.
2. **If you add/rename/remove a field**, mirror it in the `Case` model
   (`src/svcv4_model/case.py`) — the matrix-shape test requires **exact
   correspondence** between matrix dotted paths and model fields (no orphans, no
   gaps). Update the `MOCK` values and `ARRAYS`/`WORKFLOW_LABELS` in
   `scripts/export_case_views.py` if relevant.
3. **Regenerate:**
   ```
   uv run python scripts/export_schemas.py
   uv run python scripts/export_case_views.py
   ```
4. **Run tests:** `uv run pytest tests/test_case.py tests/test_case_applicability.py tests/test_case_views.py`
5. **Commit the generated artifacts** (`schemas/json/**`, `docs/workflows/case-model.md`) alongside the source change, or CI drift check fails.

## Deferred / expected next work

Stored-but-not-built (the expected next phases, one workflow/use-case at a time):

1. **Rule enforcement** — a `validate_case` that actually checks the `requires`/`enum_exclude`/`fixed` rules (today they are data + docs only).
2. **Case aggregation / counting** within a workflow.
3. **Mapping** aggregated cases to the **SVCv4 point system**.

## Pointers

- Design spec: [`../specs/2026-06-11-case-model-design.md`](../specs/2026-06-11-case-model-design.md)
- Implementation plan: [`../plans/2026-06-11-case-model.md`](../plans/2026-06-11-case-model.md)
- Rendered docs page: [`../../workflows/case-model.md`](../../workflows/case-model.md)
- Source data: SVCv4 case-attributes Google Sheet, tab `138412089`
