# Case Model — Design Spec

**Date:** 2026-06-11
**Status:** Proposed
**Branch:** `feat/case-model`
**Source data:** [SVCv4 case-attributes sheet, tab `138412089`](https://docs.google.com/spreadsheets/d/1f6iXEUgjLY4a404N4e8XcE5sg_ewdBgTEdlbjGUzDX4/edit?gid=138412089#gid=138412089)

## 1. Purpose & scope

Model the **`Case`** data structure: a superset of all case-level attributes a
curator captures from the literature to represent a single human clinical
observation (CLN) supporting (or opposing) variant pathogenicity. A `Case` is
the structured payload behind a `clinical_observation` Evidence Item.

The attributes span five CLN evidence-assessment workflows. Each attribute is
**required (`r`)**, **optional (`o`)**, **conditional (`c`)**, or **not
applicable (`x`)** in at least one workflow:

| Code | Workflow | Generalization |
|------|----------|----------------|
| `CLN_AFF` | Affected | — |
| `CLN_DNV` | De Novo | — |
| `CLN_ALTV` | Alternative Variant | `CLN_ALT` |
| `CLN_ALTG` | Alternative Gene | `CLN_ALT` |
| `CLN_UAF` | Unaffected | — |

`CLN_ALT` is documented as the generalization over `CLN_ALTV` + `CLN_ALTG`; the
matrix keys the two leaf workflows separately because their rules diverge.

### In scope (this phase)

- The superset `Case` model (Pydantic + exported JSON Schema).
- A declarative **applicability matrix** (single source of truth for r/o/c/x +
  conditional rules + value vocabularies + curator notes).
- Five **derived per-workflow views** (generated JSON Schemas + docs tables).
- Docs pages explaining the model and the conditional attributes.

### Out of scope (later phases)

- **Enforcement** of the conditional rules (`validate_case`). This phase
  documents the rules as structured data; enforcement is deferred.
- Aggregation of multiple cases within a workflow, case counting, and mapping to
  the SVCv4 point system.
- Worked example cases per workflow.
- Wiring `Case` into the broader VCEP-specification rule coordination (the sheet
  explicitly defers this to the curator's judgment).

## 2. Placement in the existing model

`Case` is a **standalone entity** — its own module and schema — that a
`clinical_observation` Evidence Item references/embeds as its `data` payload.
This preserves the repo's scope boundary (capture evidence + classification;
ClinGen CSpec owns methods/rules) and lets `Case` evolve independently while
deriving per-workflow subsets cleanly.

- A `Case` references the **VBC by `id`** and records *case-level* observations
  only (e.g. case-level zygosity). The full VBC/MDE context lives in the parent
  classification, not duplicated here.
- `additional_variants[].gene.mde_associated_gene` is the one place the case
  references an MDE-associated gene, used when an additional variant sits in a
  gene other than the VBC's.

## 3. The superset `Case` structure

Mirrors the sheet's hierarchy exactly. **Every field is optional at the Pydantic
layer** — the superset is permissive by design; per-workflow applicability is
expressed by the matrix (§4), not by the type.

```
Case
├─ moi                          enum: AD | AR | XLD | XLR | SD
├─ pop_frq_points               number (≥ -1.0)
├─ case_proband_info
│   ├─ sex                      enum: M | F | U | T
│   ├─ age                      Age (structured, see §3.1)
│   ├─ phenotypes[]             Phenotype { name, hpo_id }
│   ├─ pheno_specificity_for_gene   enum: SPECIFIC | CONSISTENT | INCONSISTENT
│   ├─ pheno_severity           enum: MONO_GT_OR_BIALLELIC_EQ_EXPECTED
│   │                                 | MONO_EQ_EXPECTED
│   │                                 | BIALLELIC_LT_EXPECTED
│   ├─ age_matched_penetrance   enum: LT_80 | PCT_80_100 | NEAR_100
│   ├─ confirmed_parental_relationship   bool
│   └─ all_relevant_genes_tested         bool
├─ vbc                          CaseVariant { id, zygosity }
├─ compound_het_variant         CompoundHetVariant {
│                                  id, zygosity=HET (fixed), phase_in_ref_to_vbc=TRANS (fixed),
│                                  phase_confidence, classification }
├─ additional_variant_exists    bool
└─ additional_variants[]        AdditionalVariant {
                                   id, gene { symbol, mde_associated_gene },
                                   zygosity: HOM | HET | HEMI,
                                   phase_in_ref_to_vbc, phase_confidence, classification }
```

### 3.1 The `Age` type

The sheet's age values are loose ("7 mo", ">10 years", "5–10 months", "under 2
years"). One structured type covers all of them:

```
Age
├─ value     number | null     point value (used with EXACT/GT/LT/APPROX)
├─ min       number | null     lower bound (used with RANGE)
├─ max       number | null     upper bound (used with RANGE)
├─ unit      enum: DAY | WEEK | MONTH | YEAR
├─ qualifier enum: EXACT | GT | LT | APPROX | RANGE
└─ raw       string | null     original curator text, preserved verbatim
```

Examples → `{value:7, unit:MONTH, qualifier:EXACT, raw:"7 mo"}`;
`{value:10, unit:YEAR, qualifier:GT, raw:">10 years"}`;
`{min:5, max:10, unit:MONTH, qualifier:RANGE, raw:"5-10 months"}`;
`{value:2, unit:YEAR, qualifier:LT, raw:"under 2 years"}`.

### 3.2 Enumerations

All vocabularies use canonical UPPER_SNAKE tokens; the sheet's human strings are
preserved as the field/enum descriptions.

| Enum | Tokens |
|------|--------|
| `MOI` | `AD`, `AR`, `XLD`, `XLR`, `SD` |
| `Sex` | `M`, `F`, `U`, `T` |
| `PhenoSpecificity` | `SPECIFIC`, `CONSISTENT`, `INCONSISTENT` |
| `PhenoSeverity` | `MONO_GT_OR_BIALLELIC_EQ_EXPECTED`, `MONO_EQ_EXPECTED`, `BIALLELIC_LT_EXPECTED` |
| `AgeMatchedPenetrance` | `LT_80`, `PCT_80_100`, `NEAR_100` |
| `Zygosity` | `HOM`, `HET`, `HEMI` |
| `Phase` | `TRANS`, `CIS`, `UNKNOWN` |
| `AgeUnit` | `DAY`, `WEEK`, `MONTH`, `YEAR` |
| `AgeQualifier` | `EXACT`, `GT`, `LT`, `APPROX`, `RANGE` |

`classification` and `phase_confidence` carry placeholder string types in this
phase, to be tightened against the SVCv4 VA-Spec community profile later.

## 4. The applicability matrix (single source of truth)

`schemas/applicability/case_applicability.yaml` is keyed by **dotted field
path** and holds exactly what the sheet's columns hold. It is the *only* place
r/o/c/x, value vocabularies, conditional rules, and curator notes are
maintained; the model docstrings, the docs tables, and the derived per-workflow
schemas all generate from it.

```yaml
moi:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: r }
  value: "AD, AR, XLD, XLR, SD"
  notes: "ALTV does not yet support AR/XLR"

pop_frq_points:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }
  notes: "must be >= -1.0"

case_proband_info.pheno_severity:
  applicability: { CLN_AFF: x, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: "c*", CLN_UAF: x }
  rule: { workflow: CLN_ALTG, effect: enum_exclude, value: BIALLELIC_LT_EXPECTED }
  notes: "BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG"

case_proband_info.age_matched_penetrance:
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: x, CLN_ALTG: "c*", CLN_UAF: r }
  notes: "only applicable at all for ALT Gene among the conditional workflows"

compound_het_variant:
  applicability: { CLN_AFF: "c*", CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }
  rule: { requires: { context: "biallelic disease eval with a het VBC" } }
  notes: "AFF only; otherwise use additional_variant. zygosity fixed HET, phase fixed TRANS"

additional_variant_exists:
  applicability: { CLN_AFF: r, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }

additional_variants:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }
  rule: { requires: { field: additional_variant_exists, equals: true } }
  notes: "compound-het additional variants are NOT supported; classification must be P-LP for ALTV/ALTG"
```

The full matrix carries one entry per leaf and nested field shown in §3, each
with its five-workflow applicability row and, where present in the sheet, its
`value`, `rule`, and `notes`.

### 4.1 Conditional-rule kinds

Three machine-readable rule kinds capture every conditional in the sheet; the
rest stays as free-text `notes`:

- **`requires`** — the field applies only when another field/context holds
  (`additional_variants` ⇐ `additional_variant_exists == true`; the AFF-only
  compound-het block).
- **`enum_exclude`** — a workflow drops one enum value (`CLN_ALTG` drops
  `BIALLELIC_LT_EXPECTED` from `pheno_severity`).
- **`fixed`** — a value is pinned in a workflow (compound-het `zygosity = HET`,
  `phase_in_ref_to_vbc = TRANS`).

This phase **stores** these rules as data and **documents** them. It does not
build an enforcer; enforcement (`validate_case`) is a later phase.

## 5. Derived per-workflow views

`scripts/export_case_views.py` reads the superset model + the matrix and emits,
for each of the five workflows:

- `schemas/json/case/CLN_AFF.schema.json`, `…/CLN_DNV.schema.json`,
  `…/CLN_ALTV.schema.json`, `…/CLN_ALTG.schema.json`, `…/CLN_UAF.schema.json`
- the docs applicability table for that workflow (never hand-maintained).

Generation rules (structural facts only; conditionals are annotated, not
enforced):

- `r` → field listed in the schema's `required[]`.
- `o` / `c` → present, not required.
- `x` → field omitted from the workflow schema (and noted as not-applicable).
- `enum_exclude` → the excluded token removed from that workflow's enum.
- `fixed` → the value pinned via `const` in that workflow's schema.
- `requires` → rendered as an `if/then` **annotation** in the schema description
  and the docs (informational this phase).

This mirrors the existing `scripts/export_schemas.py` pattern; CI runs it to
verify the committed schemas are in sync.

## 6. File layout

| Path | Purpose |
|------|---------|
| `src/svcv4_model/case.py` | Superset `Case` model + sub-models + enums + `Workflow` enum |
| `schemas/applicability/case_applicability.yaml` | The applicability matrix (single source of truth) |
| `src/svcv4_model/case_applicability.py` | Loader exposing the matrix to the exporter/docs |
| `schemas/json/Case.schema.json` | Exported superset JSON Schema |
| `schemas/json/case/CLN_*.schema.json` | Five derived per-workflow schemas |
| `scripts/export_case_views.py` | Generates derived schemas + docs tables from model + matrix |
| `docs/concepts/case-model.md` | Narrative + generated superset/per-workflow tables |
| `tests/test_case.py` | Round-trip + matrix-shape + generated-schema-in-sync tests |

`src/svcv4_model/__init__.py` exports `Case` (and its public sub-models/enums);
`mkdocs.yml` adds the new docs page; `docs/model/index.md` adds a `::: svcv4_model.Case`
stanza.

## 7. Testing

- **Model round-trip:** construct a maximal `Case`, serialize, re-parse, assert equality.
- **Matrix shape:** every field path in the matrix exists on the model and vice
  versa (no orphans, no gaps); every applicability value ∈ {`r`,`o`,`c`,`c*`,`x`}.
- **Derived schemas in sync:** running the exporter produces no diff against the
  committed `schemas/json/case/*.json` (mirrors the scaffold's schema-sync check).
- **Per-workflow required/excluded:** for each workflow, the derived schema's
  `required[]` and omitted fields match the matrix.

## 8. Delivery & process

Work proceeds on `feat/case-model` off `main`, kept in sync via PRs:

1. **PR #1 — this spec** (docs only).
2. After spec approval, an implementation plan (writing-plans skill), then
   implementation PR(s) for the model, matrix, exporter, derived schemas, and docs.

## 9. Open items deferred by decision

- `validate_case` rule enforcement — later phase.
- Tightening `classification` / `phase_confidence` to VA-Spec profile types.
- Case aggregation, counting, and SVCv4 point mapping — subsequent phase, one
  workflow at a time.
