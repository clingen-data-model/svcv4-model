# Initial Scaffold — Design Document

*Date: 2026-05-19. Status: design accepted; implementation pending.*

## Context

`svcv4-model` is a brand-new public repository that will host the **computational reference documentation** for the forthcoming **Sequence Variant Classification v4 (SVCv4)** community guidelines (planned publication later in 2026). The repository's deliverable is a **single integrated published doc site** that combines:

- the SVCv4 data model expressed in Pydantic,
- machine-readable JSON Schemas generated from those Pydantic models, and
- worked examples that demonstrate a complete classification of a germline **Variant Being Classified (VBC)** against a **Mendelian Disease Entity (MDE)**.

The audience is software engineers in clinical labs, research groups, and consortia who will integrate, automate, and exchange SVCv4 data. The site is therefore engineering-facing and emphasises **Interoperability** and **Reusability** (the I and R of FAIR). The data model must compose with **GA4GH GKS** (Genomic Knowledge Standards) schemas — VRS, Cat-VRS, gks-core, VA-Spec — rather than redefine what they already standardise.

**Why this scope:** picking the repo layout, modelling format, doc pipeline, GKS interop posture, examples format, and CI shape *up front* is what determines whether downstream content (real evidence-line definitions, real workflows, real worked examples) lands cleanly or is wedged into a bad foundation. The actual SVCv4 hierarchy details (evidence lines, leaf workflows, evidence-item structures, Bayesian-rollup logic) will be filled in as the guidelines stabilise — this design covers the **scaffold only**.

**Foundational decisions:**

1. Single integrated site (schemas + examples + generated docs together). Split later only if it grows.
2. Author the data model in **Pydantic v2** (Python). Emit JSON Schema as a byproduct. (Chosen over LinkML despite LinkML being the canonical GKS authoring format upstream.)
3. SVCv4-specific structure is captured collaboratively as the guidelines firm up; the scaffold uses faithfully-shaped placeholders in the meantime.

**GKS landscape (from upstream reconnaissance):** `ga4gh.vrs` (v2.x), `ga4gh.cat-vrs`, and `ga4gh.va-spec` are available as Pydantic packages, **generated from LinkML upstream** by the GKS maintainers. There is no umbrella install; you pick per sub-schema. The cleanest exemplar prior-art doc site is **[vrs.ga4gh.org](https://vrs.ga4gh.org/)** (spec narrative + JSON examples + schema). This repository will depend on `ga4gh.vrs` from day one for VBC variant representation and add `cat-vrs` / `va-spec` only when SVCv4's model genuinely needs them.

## Approach

Build a Python package (`svcv4_model`) of placeholder Pydantic v2 models that capture SVCv4's three-level evidence hierarchy (**Evidence Line → Workflow → Evidence Item**) and its **Classification / Bayesian-score / spectrum** outputs, **without inventing SVCv4 specifics yet**. Layer on a MkDocs Material doc site with `mkdocstrings` that auto-generates the model-reference section from those Pydantic classes; a JSON Schema export step that emits `schemas/json/*.json` from `model_json_schema()` and renders them in the docs via `json-schema-for-humans`; an `examples/` directory of JSON fixtures validated in CI against the generated schemas; and a GitHub Actions pipeline that runs tests + schema export + example validation + docs build, deploying to GitHub Pages. GKS types are referenced via typed Pydantic fields backed by the `ga4gh.vrs` package — VRS is not redefined — and a dedicated `docs/gks-interop.md` page explains the alignment posture (CURIE-by-reference, no duplication).

## Repository Layout

```
svcv4-model/
├── LICENSE
├── .gitignore
├── README.md
├── pyproject.toml                   # uv-managed, Pydantic v2, dev deps, ga4gh.vrs
├── mkdocs.yml                       # Material + mkdocstrings + jsonschema rendering
├── .github/
│   └── workflows/
│       ├── ci.yml                   # ruff + pytest + schema export + example validation
│       └── docs.yml                 # build & deploy site to gh-pages
├── src/
│   └── svcv4_model/
│       ├── __init__.py
│       ├── classification.py        # Classification, BayesianScore, ClassificationSpectrum
│       ├── evidence_line.py         # EvidenceLine
│       ├── workflow.py              # Workflow (leaf-level, method definition)
│       ├── evidence_item.py         # EvidenceItem
│       ├── inputs.py                # VBC (typed to ga4gh.vrs Variation), MDE
│       └── gks.py                   # thin re-exports / CURIE helpers for GKS types
├── schemas/
│   └── json/                        # generated JSON Schemas (committed, regenerated in CI)
├── examples/
│   ├── README.md
│   └── classification-example-01.json   # one full (VBC, MDE) classification placeholder
├── docs/
│   ├── index.md                     # what is SVCv4, what this repo is, FAIR posture
│   ├── concepts/
│   │   ├── evidence-hierarchy.md    # Evidence Line → Workflow → Evidence Item explained
│   │   ├── bayesian-rollup.md       # how scores compose to the final Bayesian score
│   │   └── classification-spectrum.md  # Benign ↔ Pathogenic spectrum, score mapping
│   ├── model/                       # auto-generated from Pydantic via mkdocstrings
│   ├── schemas/                     # rendered JSON Schema reference (json-schema-for-humans)
│   ├── examples/                    # narrative walkthroughs of examples/*.json
│   ├── gks-interop.md               # alignment with VRS / Cat-VRS / VA / gks-core
│   ├── contributing.md              # dev setup, conventions, how to add an evidence line
│   ├── glossary.md                  # SVCv4 / VBC / MDE / GA4GH / GKS / FAIR
│   └── plans/
│       └── 2026-05-19-initial-scaffold.md   # this file
├── scripts/
│   ├── export_schemas.py            # iterate Pydantic models → write schemas/json/*.json
│   └── validate_examples.py         # validate examples/*.json against schemas/json/*.json
└── tests/
    ├── test_model.py                # model instantiates, round-trips JSON
    └── test_examples.py             # every example loads as svcv4_model.Classification
```

## Tooling Choices

| Concern | Choice | Why |
|---|---|---|
| Python | ≥ 3.11 | Pydantic v2 baseline; modern typing. |
| Package manager | `uv` | Fast, single tool; standard `pyproject.toml`. |
| Modelling | Pydantic v2 | Project decision; native JSON Schema export. |
| GKS variant types | `ga4gh.vrs` (v2.x) | Mature, official, LinkML-generated upstream. |
| Docs engine | MkDocs Material | Idiomatic Python docs, easy GitHub Pages deploy. |
| API reference generator | `mkdocstrings[python]` | Pulls docs straight from Pydantic class fields and docstrings. |
| Schema rendering | `json-schema-for-humans` | Generates browsable HTML for JSON Schemas. |
| Lint / format | `ruff` | Single tool, fast. |
| Tests | `pytest` + `jsonschema` | Validate examples conform to generated schemas. |
| CI | GitHub Actions | Standard; gh-pages deploy via `mkdocs gh-deploy` step. |

## Placeholder Model Skeleton

Goal: **shape** correct, **content** stubbed. Real evidence-line names, workflow methods, score logic, and MDE typing get filled in as SVCv4 stabilises.

- `Classification` — holds `list[EvidenceLine]`, a `BayesianScore`, and a `ClassificationSpectrum` enum value; references one `VBC` and one `MDE`.
- `EvidenceLine` — `name`, `category` (placeholder enum), `list[Workflow]`, rolled-up score.
- `Workflow` — `name`, `method` description, `list[EvidenceItem]`, rolled-up score.
- `EvidenceItem` — a structured datum plus its score contribution.
- `BayesianScore` — numeric value plus provenance of how it was composed.
- `ClassificationSpectrum` — enum spanning Benign ↔ Pathogenic (exact bins to be confirmed with SVCv4 authors).
- `VBC` — typed field referencing a `ga4gh.vrs.models.Variation` (germline context).
- `MDE` — `label` + `curie` reference (MONDO / OMIM); precise typing deferred.

All score-rollup methods are typed but return placeholder values; the logic is explicitly TODO-marked so it is obvious where domain content plugs in.

## GKS Interop Strategy

- Depend on `ga4gh.vrs` from day one; type VBC's variant slot to a VRS `Variation`.
- **Do not redefine** VRS / Cat-VRS / VA types — reference by CURIE per GKS conventions.
- Add `ga4gh.cat-vrs` and `ga4gh.va-spec` as dependencies only when a concrete SVCv4 model element actually needs them.
- Document the posture in `docs/gks-interop.md`: which GKS sub-schemas are touched, why, and how SVCv4 extends versus references them.
- GKS package pinning policy: pin per release and document changes in the CHANGELOG once one exists.

## Examples & Validation Pipeline

- `examples/classification-example-01.json` — one end-to-end placeholder classification (real shape, dummy content).
- `scripts/export_schemas.py` walks the public model classes and writes `schemas/json/<ClassName>.schema.json`.
- `scripts/validate_examples.py` loads every `examples/*.json`, validates against `schemas/json/Classification.schema.json` via `jsonschema`, and round-trips through `svcv4_model.Classification.model_validate(...)`.
- CI runs both scripts on every PR; the site build fails if any example desyncs from the schemas.

## CI / Publishing

- `ci.yml`: install via `uv sync`, run `ruff check`, run `pytest`, run schema export, run example validation. Fail on diff between committed `schemas/json/` and freshly generated output (forces contributors to regenerate).
- `docs.yml`: on push to `main`, build `mkdocs build --strict` and deploy to the `gh-pages` branch via `mkdocs gh-deploy --force`. Site URL is the GitHub Pages default unless a custom domain is later confirmed.

## Out of Scope (intentional YAGNI)

- Authoring real SVCv4 evidence-line / workflow / evidence-item definitions (handled as guidelines stabilise).
- Real Bayesian-rollup logic.
- Cat-VRS and VA-Spec integration (added when SVCv4 model needs them).
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
6. `uv run mkdocs serve` — open `http://localhost:8000`, confirm: home renders; model-reference page shows the Pydantic classes with their fields; JSON Schema pages render; example walkthroughs render; GKS interop page renders; glossary present; no broken links (`mkdocs build --strict` passes in CI).
7. Push to a feature branch; confirm GitHub Actions runs both workflows green.

## Open Questions

These do not block the scaffold but should be resolved early:

- Published site URL: GitHub Pages default (`https://clingen-data-model.github.io/svcv4-model/`) or a custom domain?
- `ClassificationSpectrum` bins: exact enum values and human labels (Benign / Likely Benign / VUS / Likely Pathogenic / Pathogenic, or SVCv4-specific bins).
- MDE typing: MONDO-only, or also OMIM and Orphanet CURIEs?
- Licence for the *documentation content* — same as the code `LICENSE`, or a separate CC-BY-style licence for narrative.
- GKS package pinning policy (pin per release versus floating minor).
