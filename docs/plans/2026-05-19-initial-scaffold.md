# Initial Scaffold — Design Document

*Date: 2026-05-19 (revised 2026-05-21 to align with the SVCv4 Standards & Data Model deck). Status: design accepted; implementation pending.*

## Context

`svcv4-model` is a public repository that will host the **computational reference documentation** for the **Classification Model** of the forthcoming **ACMG/AMP/CAP/ClinGen Sequence Variant Classification v4 (SVCv4) Standards** (publication target October 2026 in *Genetics in Medicine*). The repository's deliverable is a **single integrated published doc site** that combines:

- the SVCv4 Classification Model expressed in Pydantic as the Python source of truth;
- machine-readable JSON Schemas emitted from those Pydantic models;
- worked examples that demonstrate a complete classification of a germline **Variant Being Considered (VBC)** against a **Mendelian Disease Entity (MDE)**; and
- narrative documentation that frames the model, its VA-Spec layering, and its boundary with the Method Model in ClinGen CSpec.

The audience is software engineers in clinical labs, research groups, and consortia who will integrate, automate, and exchange SVCv4 data. The site is engineering-facing and emphasises **Interoperability** and **Reusability** (the I and R of FAIR).

### Scope: Classification Model only

This repository covers only the **Classification Model** — the shape of a SVCv4 Variant Pathogenicity Classification. It does **not** cover the **Method Model** (the prescriptive workflows, scoring rules, criteria definitions, gene-disease-MOI scoping, and specialised configurations); those live in **ClinGen CSpec**. The Classification Model's Evidence Lines reference methods and evidence codes; CSpec defines what those references mean.

### Foundation: GA4GH GKS VA-Spec

The Classification Model is authored as the **VA-Spec SVCv4 community profile** — a layering of SVCv4-specific constraints on top of the VA-Spec baseline classes (`Statement`, `Proposition`, `EvidenceLine`, `InformationEntity`, `EvidenceData`). VA-Spec v1.0 is the primary GKS dependency; VRS v2.0 supports it for representing the VBC; Cat-VRS and gks-core support categorical variation and shared identifier constructs. ClinGen ERepo's JSON-LD SEPIO implementation informed VA-Spec; this project further informs the SVCv4 community profile.

### Foundational decisions

1. Single integrated site (schemas + examples + generated docs together). Split later only if it grows.
2. Author the Classification Model in **Pydantic v2** (Python). Emit JSON Schema as a byproduct.
3. SVCv4-specific structure is captured collaboratively as the guidelines and the VA-Spec SVCv4 community profile firm up; the scaffold uses faithfully-shaped placeholders in the meantime.
4. **Use VA-Spec canonical entity names** in code and schemas — `Statement`, `Proposition`, `EvidenceLine`, `EvidenceItem`, `InformationEntity`, `VariantPathogenicityClassification` — not bespoke project-local names.

### GKS landscape (from upstream reconnaissance)

`ga4gh.vrs` (v2.x), `ga4gh.cat-vrs`, and `ga4gh.va-spec` are available as Pydantic packages, **generated from LinkML upstream** by the GKS maintainers. No umbrella install; pick per sub-schema. The cleanest exemplar prior-art doc site is **[vrs.ga4gh.org](https://vrs.ga4gh.org/)** (spec narrative + JSON examples + schema). This repository will depend on `ga4gh.va-spec` and `ga4gh.vrs` from day one — VA-Spec for the baseline classes the SVCv4 profile extends, VRS for the VBC variant representation. `cat-vrs` is added when SVCv4's profile needs categorical variation support.

## Approach

Build a Python package (`svcv4_model`) of Pydantic v2 classes that **profile** the VA-Spec baseline for the SVCv4 use case: `Statement`, `Proposition` (SPOQ), `EvidenceLine`, `EvidenceItem`, `VariantPathogenicityClassification`, plus the `VBC` (typed via `ga4gh.vrs`) and `MDE` (typed via a disease CURIE). Where SVCv4 specifics aren't yet locked, the classes are **faithfully-shaped placeholders** — VA-Spec-conformant skeletons that real Evidence Categories / Concepts / Codes can plug into as the baseline stabilises.

Layer on a MkDocs Material doc site with `mkdocstrings` that auto-generates the model-reference section from the Pydantic classes; a JSON Schema export step that emits `schemas/json/*.json` from `model_json_schema()` and renders them in the docs via `json-schema-for-humans`; an `examples/` directory of JSON fixtures validated in CI against the generated schemas; and a GitHub Actions pipeline that runs tests + schema export + example validation + docs build, deploying to GitHub Pages.

GKS types are referenced via typed Pydantic fields backed by the `ga4gh.va-spec` and `ga4gh.vrs` packages — VA-Spec and VRS are not redefined — and dedicated docs pages explain the VA-Spec community-profile layering and the Classification ↔ Method-Model boundary.

## Repository Layout

```
svcv4-model/
├── LICENSE
├── .gitignore
├── README.md
├── pyproject.toml                   # uv-managed, Pydantic v2, dev deps, ga4gh.va-spec, ga4gh.vrs
├── mkdocs.yml                       # Material + mkdocstrings + jsonschema rendering
├── .github/
│   └── workflows/
│       ├── ci.yml                   # ruff + pytest + schema export + example validation
│       └── docs.yml                 # build & deploy site to gh-pages
├── src/
│   └── svcv4_model/
│       ├── __init__.py
│       ├── statement.py             # Statement (top-level VA-Spec entity)
│       ├── proposition.py           # Proposition (SPOQ: Subject, Predicate, Object, Qualifier)
│       ├── evidence_line.py         # EvidenceLine (profiled for SVCv4)
│       ├── evidence_item.py         # EvidenceItem / EvidenceData
│       ├── classification.py        # VariantPathogenicityClassification + spectrum enum
│       ├── inputs.py                # VBC (typed to ga4gh.vrs Variation), MDE (CURIE-typed)
│       └── gks.py                   # thin re-exports / helpers for VA-Spec + VRS types
├── schemas/
│   └── json/                        # generated JSON Schemas (committed, regenerated in CI)
├── examples/
│   ├── README.md
│   └── classification-example-01.json   # one full (VBC, MDE) classification placeholder
├── docs/
│   ├── index.md                     # what SVCv4 is, what this repo is, FAIR posture
│   ├── concepts/
│   │   ├── classification-vs-method-model.md   # the scope boundary, with CSpec
│   │   ├── va-spec-community-profile.md        # how SVCv4 layers on top of VA-Spec
│   │   ├── statement-and-proposition.md        # Statement, Proposition (SPOQ), score
│   │   ├── evidence-lines-and-items.md         # Evidence Line / Item structure
│   │   └── summary-table.md                    # Evidence Category → Concept → Code → Workflow
│   ├── model/                       # auto-generated from Pydantic via mkdocstrings
│   ├── schemas/                     # rendered JSON Schema reference (json-schema-for-humans)
│   ├── examples/                    # narrative walkthroughs of examples/*.json
│   ├── gks-interop.md               # alignment with VA-Spec / VRS / Cat-VRS / gks-core
│   ├── cspec-interop.md             # how method/evidence codes reference CSpec
│   ├── contributing.md              # dev setup, conventions, how to extend the profile
│   ├── glossary.md                  # SVCv4 / VBC / MDE / GA4GH / GKS / FAIR / CSpec / etc.
│   └── plans/
│       └── 2026-05-19-initial-scaffold.md   # this file
├── scripts/
│   ├── export_schemas.py            # iterate Pydantic models → write schemas/json/*.json
│   └── validate_examples.py         # validate examples/*.json against schemas/json/*.json
└── tests/
    ├── test_model.py                # model instantiates, round-trips JSON
    └── test_examples.py             # every example loads as svcv4_model.Statement
```

## Tooling Choices

| Concern | Choice | Why |
|---|---|---|
| Python | ≥ 3.11 | Pydantic v2 baseline; modern typing. |
| Package manager | `uv` | Fast, single tool; standard `pyproject.toml`. |
| Modelling | Pydantic v2 | Project decision; native JSON Schema export. |
| GKS dependencies | `ga4gh.va-spec` (primary) + `ga4gh.vrs` | VA-Spec is the baseline this repo profiles; VRS represents the VBC. Both Pydantic, both LinkML-generated upstream. |
| Docs engine | MkDocs Material | Idiomatic Python docs, easy GitHub Pages deploy. |
| API reference generator | `mkdocstrings[python]` | Pulls docs straight from Pydantic class fields and docstrings. |
| Schema rendering | `json-schema-for-humans` | Generates browsable HTML for JSON Schemas. |
| Lint / format | `ruff` | Single tool, fast. |
| Tests | `pytest` + `jsonschema` | Validate examples conform to generated schemas. |
| CI | GitHub Actions | Standard; gh-pages deploy via `mkdocs gh-deploy` step. |

## Placeholder Model Skeleton (VA-Spec aligned)

Goal: **shape** correct, **content** stubbed. Real Evidence Categories / Concepts / Codes, propositional predicates, and disease-domain content get filled in as SVCv4 and the VA-Spec community profile stabilise.

- `Statement` — VA-Spec `Statement` profiled for SVCv4. Carries a `Proposition`, a final score, `strength_direction`, `score_classification`, `method` (reference), `contribution`, and `evidence_lines: list[EvidenceLine]`.
- `Proposition` — VA-Spec `Proposition` with SPOQ slots: `subject: VBC`, `predicate`, `object: MDE`, `qualifiers`.
- `VariantPathogenicityClassification` — categorical classification (placeholder enum spanning Benign ↔ Pathogenic). The score-to-class mapping is a placeholder; SVCv4 thresholds will be confirmed.
- `EvidenceLine` — VA-Spec `EvidenceLine` profiled for SVCv4. Carries `score`, optional `score_classification`, evidence (`list[EvidenceItem]`), optional `code` (evidence-code reference), optional `strength_direction`, `method` (reference), `contribution`. Any process that yields a score lands here.
- `EvidenceItem` (alias: `EvidenceData`) — structured datum supporting an Evidence Line's score.
- `VBC` (Variant Being Considered) — typed field referencing a `ga4gh.vrs.models.Variation` (germline context).
- `MDE` (Mendelian Disease Entity) — `label` + `curie` reference (MONDO / OMIM / Orphanet); precise typing deferred.

Score values are carried; score *computation* is **not** modelled here — it belongs to the workflows defined in CSpec. Where `method` or `code` slots appear, they are **references** pointing into the (out-of-scope) Method Model.

## VA-Spec & CSpec Interop Strategy

- Depend on `ga4gh.va-spec` and `ga4gh.vrs` from day one. The SVCv4 classes **profile** the VA-Spec baseline rather than redefine it.
- Do not redefine VRS / Cat-VRS / VA types — reference by CURIE per GKS conventions.
- Add `ga4gh.cat-vrs` as a dependency only when the SVCv4 profile genuinely needs categorical variation.
- Document the VA-Spec layering in `docs/gks-interop.md` and the VA-Spec community-profile concept in `docs/concepts/va-spec-community-profile.md`.
- Document the **Classification ↔ Method-Model boundary** in `docs/concepts/classification-vs-method-model.md` and the CSpec junction (method codes, evidence codes) in `docs/cspec-interop.md`.
- GKS package pinning policy: pin per release and document changes in the CHANGELOG once one exists.

## Examples & Validation Pipeline

- `examples/classification-example-01.json` — one end-to-end placeholder Statement carrying a Proposition and Evidence Lines (real shape, dummy content).
- `scripts/export_schemas.py` walks the public model classes and writes `schemas/json/<ClassName>.schema.json`.
- `scripts/validate_examples.py` loads every `examples/*.json`, validates against `schemas/json/Statement.schema.json` via `jsonschema`, and round-trips through `svcv4_model.Statement.model_validate(...)`.
- CI runs both scripts on every PR; the site build fails if any example desyncs from the schemas.

## CI / Publishing

- `ci.yml`: install via `uv sync`, run `ruff check`, run `pytest`, run schema export, run example validation. Fail on diff between committed `schemas/json/` and freshly generated output (forces contributors to regenerate).
- `docs.yml`: on push to `main`, build `mkdocs build --strict` and deploy to the `gh-pages` branch via `mkdocs gh-deploy --force`. Site URL is the GitHub Pages default (`https://clingen-data-model.github.io/svcv4-model/`) unless a custom domain is later confirmed.

## Out of Scope (intentional YAGNI)

- The **Method Model** in any form — workflow definitions, scoring rules, criteria-specification mechanics, gene-disease-MOI scoping, VCEP specialisations. All of that lives in **CSpec**.
- Authoring real SVCv4 Evidence Category / Concept / Code content (handled as the Summary Table stabilises).
- Cat-VRS integration (added when the SVCv4 profile needs it).
- LinkML round-trip (deferred unless GKS interop requires it).
- Non-Python language bindings beyond what JSON Schema provides.
- Versioning / release tooling (added when the first release nears).
- Custom-domain DNS for the published site.

## Verification

After implementation, run end-to-end from the repo root:

1. `uv sync` — installs dependencies cleanly.
2. `uv run ruff check .` — passes.
3. `uv run pytest -q` — all tests pass.
4. `uv run python scripts/export_schemas.py` — writes `schemas/json/*.json`; `git status` shows no diff versus committed copies.
5. `uv run python scripts/validate_examples.py` — every example validates; exits 0.
6. `uv run mkdocs serve` — open `http://localhost:8000`, confirm: home renders; model-reference page shows the Pydantic classes with their fields; JSON Schema pages render; example walkthroughs render; VA-Spec interop page renders; CSpec interop page renders; classification-vs-method-model concept page renders; glossary present; no broken links (`mkdocs build --strict` passes in CI).
7. Push to a feature branch; confirm GitHub Actions runs both workflows green.

## Open Questions

These do not block the scaffold but should be resolved early:

- Published site URL — GitHub Pages default (`https://clingen-data-model.github.io/svcv4-model/`) or a custom domain?
- `VariantPathogenicityClassification` enum values — confirm with SVCv4 working group; placeholder for now uses the familiar five-tier (Benign / Likely Benign / VUS / Likely Pathogenic / Pathogenic) with explicit note that the points→class mapping is provisional.
- `MDE` typing — MONDO-only, or also OMIM and Orphanet CURIEs? Profile the slot accordingly.
- Method/evidence code typing — what CURIE-style scheme will CSpec issue for codes? Until known, treat codes as opaque strings with a documented format expectation.
- Licence for the *documentation content* — same as the code `LICENSE`, or a separate CC-BY-style licence for narrative.
- GKS package pinning policy (pin per release versus floating minor).
- VA-Spec SVCv4 community profile draft availability — track upstream release timing so this repo's profile schemas mirror it.
