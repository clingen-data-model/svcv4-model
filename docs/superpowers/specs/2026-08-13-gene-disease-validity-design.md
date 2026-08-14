# Gene-Disease Validity + SM Link-Outs — Design Spec

**Date:** 2026-08-13
**Status:** Proposed
**Builds on:** `docs/superpowers/specs/2026-06-11-case-model-design.md` (PR #17, merged) and
`docs/superpowers/specs/2026-07-29-docsite-review-readiness-design.md` (PR #20, merged)

## 1. Purpose & goal

Two related pieces of work, delivered together:

1. **Model Gene-Disease Validity** — the first of the tracked *model* gaps on
   [Known gaps](../../reference/known-gaps.md). It is the ClinGen gene-disease
   validity classification for the gene↔MDE pair under evaluation. This pass
   **captures** it as a field and **documents** how it gates classification, but
   deliberately does **not** implement enforcement — consistent with this repo's
   scope boundary (it models evidence + classification; method/rule enforcement,
   e.g. `validate_case`, is owned elsewhere and already deferred).
2. **Add SM Google Doc link-outs to the docsite** — now that all 20 available
   SVCv4 Supplementary Materials have been ingested with stable, link-accessible
   Google Doc URLs (see §2), surface those links from the docsite where a page
   refers to a specific supplement, so readers can consult the source directly.

This is deliberately a small, well-bounded first model increment: one enum, one
field, one applicability-matrix row, and the documentation to match — plus a
cross-cutting docs enhancement (the link-outs) that does not touch the model.

## 2. Source material (this pass)

- **All 20 available SVCv4 Supplementary Materials**, ingested 2026-08-13 as
  verbatim text via the Google Docs export endpoint and stored under the
  gitignored `source-material/svcv4-supplements/` directory (index at
  `source-material/svcv4-supplements/INDEX.md`, which maps each SM number →
  title → evidence codes → Google Doc ID). SM 17 (Non-Coding) is **not**
  available — the Working Group has deferred it; the manuscript flags that
  section as an unwritten placeholder.
- **Supplementary Material 18 (Molecular Mechanism and Exon Relevance)** — the
  primary source for the upstream gating semantics (§3.2). Verbatim, the
  relevant passage reads:

  > "The mechanism framework should also only be used for human MDEs that have
  > scored at moderate or higher level using the ClinGen gene gene-disease
  > validity framework. MDEs that are Limited or below on the gene-disease
  > validity framework should be considered as being 'Uncertain' with respect
  > to LoF being the mechanism of disease."

- **The main SVCv4 manuscript** — source for the downstream tier-reachability
  gating (§3.1). Its precise phrasing is not re-quoted here (it was read via the
  Drive connector during the PR #20 pass, not ingested as a file); the gating
  behavior it describes is captured in the existing
  [Core concepts](../../reference/concepts.md) Gene-Disease Validity entry and is
  treated here as the authoritative statement of that behavior. If exact
  manuscript wording is needed later, confirm against the manuscript directly.
- **Existing model + docs surfaces** audited for this spec: `src/svcv4_model/case.py`
  (`WorkflowParameters`), `schemas/applicability/case_applicability.yaml`,
  `scripts/export_case_views.py`, `docs/reference/concepts.md`,
  `docs/reference/known-gaps.md`, `docs/reference/spec-alignment.md`.

## 3. Key findings driving this work

### 3.1 Gene-Disease Validity gates *downstream* tier-reachability

Independent of how much variant-level evidence is accumulated, the ClinGen
gene-disease validity classification bounds which final classification tiers are
reachable at all: a `Limited` classification blocks `Pathogenic`/`Likely
Pathogenic` outright; `Disputed` or `Refuted` blocks reporting entirely. This is
already documented in `concepts.md` and is unchanged by this spec except to make
it a *modeled* concept.

### 3.2 Gene-Disease Validity also gates *upstream* mechanism scoring (new)

SM 18 (now in hand) shows a second, distinct gating effect not previously
captured in the docs: the molecular-mechanism multiplier that scales predictive
points in the PFD/LoF workflows may only be applied for MDEs at **Moderate or
higher** gene-disease validity. For MDEs at **Limited or below**, the mechanism
is treated as **`Uncertain`**, which zeroes the mechanism multiplier (and hence
the mechanism-scaled predictive points). So validity is not purely a downstream
gate — it also feeds the SM 18 mechanism-and-exon-relevance matrix upstream, in
the not-yet-modeled PFD workflows.

This spec documents that linkage but does **not** model the mechanism multiplier
itself (that lands with PFD/SM 18 work). See §7.

### 3.3 Every `WorkflowParameters` field is represented in the applicability matrix — and a test enforces it

`schemas/applicability/case_applicability.yaml` carries a per-workflow
applicability entry (`r`/`o`/`c`/`x`) for every `WorkflowParameters` field
(`vbc`, `mde`, `moi`, `pop_frq_points`, and their sub-paths), and
`scripts/export_case_views.py` drives the generated per-workflow tables and JSON
examples from that matrix. A new `WorkflowParameters` field therefore needs a
matrix entry to appear consistently in the generated views — so Gene-Disease
Validity gets one (§5.2).

This parity is **enforced by an existing test**,
`test_param_matrix_and_model_paths_match_exactly`
(`tests/test_case_applicability.py`), which enumerates
`WorkflowParameters.model_fields` against the matrix. Consequently: adding the
field *without* a matrix entry fails that test, and adding a matrix entry
*without* the field also fails it — the two changes in §5.1 and §5.2 must land
together to keep it green. This existing test already covers most of what §6's
"matrix entry exists across all seven workflows" check would assert.

### 3.4 Adding a `WorkflowParameters` field regenerates a committed JSON Schema, and CI gates on it

`scripts/export_schemas.py` writes one JSON Schema per public model class into
`schemas/json/`; `schemas/json/WorkflowParameters.schema.json` is committed and
today exposes exactly `mde`/`moi`/`pop_frq_points`/`vbc`. Adding
`gene_disease_validity` + the `GeneDiseaseValidity` enum will add a
`gene_disease_validity` property and a `$defs/GeneDiseaseValidity` to that file.
The CI drift gate (`.github/workflows/ci.yml`) runs **both** `export_schemas.py`
**and** `export_case_views.py`, then checks
`git diff --quiet -- schemas/json docs/workflows/case-model.md` — so both the
regenerated schema **and** the regenerated docs page must be committed, or CI
fails. `Case.schema.json` and the per-workflow Case views are **unaffected**
(they derive from `Case`, not `WorkflowParameters`), so exactly two generated
files change: `schemas/json/WorkflowParameters.schema.json` and
`docs/workflows/case-model.md`.

### 3.5 "Not classified" is a real, distinct state

SM 18 explicitly notes that an MDE not yet classified for mechanism must be
classified manually by an experienced analyst — i.e. "no classification exists"
is a real state a curator encounters, distinct from "I have not captured this."
The model already draws this null-vs-known distinction elsewhere (`TriState`'s
`null` vs `UNKNOWN`). Gene-Disease Validity follows suit: an absent
(`None`) field means *not captured*; an explicit `NOT_CLASSIFIED` member means
*looked, and ClinGen has no gene-disease validity classification for this
gene↔MDE pair* (§5.1).

## 4. Scope

**In scope (this pass):**
- New `GeneDiseaseValidity` enum and `WorkflowParameters.gene_disease_validity`
  field (§5.1).
- One `workflow_parameters` applicability-matrix entry, `o` (optional) across all
  seven current workflows, with an explanatory `notes:` line (§5.2).
- Regenerate `docs/workflows/case-model.md` via the exporter; commit the
  regenerated file (§5.2).
- `concepts.md`: flip the Gene-Disease Validity entry from "Not yet modeled" to
  modeled, and add the SM 18 upstream-gate semantics + a link-out to SM 18 (§5.3).
- `known-gaps.md`: remove the Gene-Disease Validity model-gap row (§5.4).
- `spec-alignment.md`: add per-row SM Google Doc link-outs, and note the GDV gate
  on the SM 18 row (§5.5).
- SM Google Doc link-outs on other docsite pages where a page already cites a
  specific supplement (§5.6).
- Tests: a round-trip/enum test asserting each validity value (including
  `NOT_CLASSIFIED`) validates on `WorkflowParameters` (§6).

**Out of scope / deferred (see §7):**
- Any enforcement logic — tier-blocking, mechanism-zeroing, or a `validate_case`
  that acts on validity. Documented, not enforced.
- Modeling the SM 18 molecular-mechanism multiplier and exon-relevance matrix
  (belongs to PFD work).
- Capturing GenCC **molecular-mechanism level** (Established/Likely/Suspected/
  Uncertain) — related but distinct from *validity*; belongs to PFD/SM 18 work.
- Validity **source/version/date** provenance (ClinGen validity is versioned);
  YAGNI for a capture-only first increment.
- Committing the verbatim SM text to the repo — it stays gitignored under
  `source-material/`; only the *links* are made public.

## 5. Content changes, item by item

### 5.1 Model: enum + field (`src/svcv4_model/case.py`)

Add an enum near the other `StrEnum`s:

```python
class GeneDiseaseValidity(StrEnum):
    """ClinGen gene-disease validity classification for the gene↔MDE pair.

    A classification-level *precondition*, not a per-workflow evidence input:
    it gates which final classification tiers are reachable (Limited blocks
    P/LP; Disputed/Refuted block reporting) and, per SVCv4 Supplementary
    Material 18, whether the molecular-mechanism multiplier may be applied at
    all (usable only at MODERATE or higher; LIMITED or below is treated as an
    'Uncertain' mechanism and zeroed).

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

Add the field to `WorkflowParameters`, alongside `mde` (it's a property of the
gene↔MDE pair, set once per classification):

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

No change to `Case`. No change to any existing field.

### 5.2 Applicability matrix (`schemas/applicability/case_applicability.yaml`)

Add one entry in the `workflow_parameters` group (near `mde`/`moi`):

```yaml
gene_disease_validity:
  model: workflow_parameters
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: o, CLN_ALTG: o, CLN_UAF: o, LOC_PHE: o, LOC_SEG: o }
  notes: "ClinGen gene-disease validity for the gene↔MDE pair; a classification-level precondition (gates final tier-reachability and the future SM18 mechanism multiplier), not a per-workflow field driver like moi"
```

Then regenerate **both** committed generated artifacts (per §3.4) and commit
them:

```bash
uv run python scripts/export_schemas.py       # regenerates schemas/json/WorkflowParameters.schema.json
uv run python scripts/export_case_views.py    # regenerates docs/workflows/case-model.md
```

The field will appear in the WorkflowParameters table as optional across all
workflows, and `WorkflowParameters.schema.json` will gain the
`gene_disease_validity` property + `$defs/GeneDiseaseValidity`.

### 5.3 `docs/reference/concepts.md` — Gene-Disease Validity entry

- Replace the `!!! note "Not yet modeled here"` admonition; the concept is now
  modeled (as a captured field).
- Keep the existing **six-tier** classification list
  (Definitive/Strong/Moderate/Limited/Disputed/Refuted) as the validity levels,
  and the downstream tier-reachability explanation. Present `NOT_CLASSIFIED`
  separately as the distinct "looked, and ClinGen has no classification for this
  gene↔MDE pair" state — not a seventh validity level.
- **Add** the SM 18 upstream gate: mechanism scoring is usable only at Moderate+
  validity; Limited-or-below is treated as an 'Uncertain' mechanism and zeroed
  in the SM 18 matrix. State clearly that this repo captures the field and
  documents the gate but does not enforce it this phase.
- Add the `NOT_CLASSIFIED`-vs-`None` distinction.
- Update "Current representation" to describe
  `WorkflowParameters.gene_disease_validity` → `GeneDiseaseValidity`.
- Add a link-out to SM 18's Google Doc (§5.6 convention).

### 5.4 `docs/reference/known-gaps.md`

Remove the `Gene-Disease Validity field` row from the Model-gaps table (it is now
underway/modeled per the how-to-use-this-page instruction on that page). Leave the
remaining rows unchanged.

### 5.5 `docs/reference/spec-alignment.md`

- Add a **Google Doc link-out to each SM row** (the `#` column or the SM title
  links to the corresponding Google Doc). SM 17's row stays link-less (not
  available). Keep the existing coverage wording.
- Update the SM 18 row's coverage note to mention that gene-disease validity —
  the Moderate+ gate SM 18 depends on — is now captured (`WorkflowParameters`),
  with the mechanism multiplier itself still to come with PFD.

### 5.6 SM link-outs elsewhere (folded in per user request)

Add a Google Doc link wherever a docsite page *already* names a specific
supplement, so a reader can jump to the source. Known cite sites to update
(grep `Supplementary Material` / `Spec coverage` references across `docs/`):
- `concepts.md`: MDE entry → SM 21; DAFT entry → SM 3; Cohort Allele Frequency
  entry (VA-Spec, keep existing external link) — and the GDV entry → SM 18 (§5.3).
- Any CLN/LOC/POP/PFD page that names an SM by number.

Convention: link the human-readable supplement name (e.g. "Supplementary
Material 18") to its Google Doc URL. Verbatim text remains gitignored; only links
are public. Use the URLs recorded in `source-material/svcv4-supplements/INDEX.md`.

## 6. Quality gates

- `uv run mkdocs build --strict` passes. Note this validates internal
  nav/links only — it does **not** verify that the external Google Doc SM
  link-outs resolve. External URL correctness is a manual check (use the URLs
  recorded in `source-material/svcv4-supplements/INDEX.md`, which is gitignored,
  so reviewers can't confirm them from the repo alone).
- **Drift gate matches CI exactly** (`.github/workflows/ci.yml`): regenerate
  both artifacts, then confirm no diff, then commit:

  ```bash
  uv run python scripts/export_schemas.py
  uv run python scripts/export_case_views.py
  git diff --quiet -- schemas/json docs/workflows/case-model.md   # must pass in CI
  ```

  The intended regeneration is exactly two files:
  `schemas/json/WorkflowParameters.schema.json` (new property + `$defs`) and
  `docs/workflows/case-model.md` (new optional row).
- `test_param_matrix_and_model_paths_match_exactly`
  (`tests/test_case_applicability.py`) still passes — it already enforces the
  field↔matrix parity (§3.3). Optionally add a small test asserting a
  `WorkflowParameters` instance accepts each `GeneDiseaseValidity` value
  including `NOT_CLASSIFIED` (the parity test does not exercise enum values).
- `grep -rn "Not yet modeled" docs/reference/concepts.md` no longer matches the
  Gene-Disease Validity section.

## 7. Follow-up backlog (explicitly not this pass)

1. **SM 18 mechanism + exon-relevance modeling** — the multiplier matrix that
   *consumes* gene-disease validity (Moderate+ gate) and GenCC mechanism level;
   lands with PFD.
2. **Enforcement** — if/when this repo takes on any rule enforcement, wire
   validity into tier-reachability and the mechanism gate. Tracked with the
   existing deferred `validate_case` work, not started here.
3. **Validity provenance** (source/version/date) — add if a downstream consumer
   needs to know *which* ClinGen classification snapshot was used.
4. Remaining known-gaps model items (POP: Cohort Allele Frequency + DAFT; the two
   `CLN_AFF` sub-fields; `CLN_CCS` once SVCv4 defines evidence concepts for it).

## 8. Delivery

New branch already in progress: `docs/review-followup` off `main`. Single PR
covering the model change (§5.1–5.2), the docs changes (§5.3–5.6), and the
gitignore/source-material addition already made. CI: the docs build/link-audit
and the Case schema/docs drift gate both apply (the drift gate will expect the
regenerated `case-model.md`).
