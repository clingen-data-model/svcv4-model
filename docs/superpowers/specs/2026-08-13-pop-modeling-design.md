# POP (Population Database Frequency) Modeling — Design Spec

**Date:** 2026-08-13
**Status:** Proposed
**Builds on:** `docs/superpowers/specs/2026-06-11-case-model-design.md` (PR #17),
`docs/superpowers/specs/2026-07-29-docsite-review-readiness-design.md` (PR #20), and
`docs/superpowers/specs/2026-08-13-gene-disease-validity-design.md` (PR #23) — this
spec follows the same **capture + document, do not enforce** stance GDV established.

## 1. Purpose & goal

Model the **POP (Population database frequency)** evidence concept — currently a
documented stub — as capturable structured evidence. POP has two evidence codes,
both benignity-only:

- **`POP_FRQ`** — the variant's population frequency (a Filtering Allele
  Frequency, FAF) compared against a Disease Allele Frequency Threshold (DAFT).
- **`POP_HMZ`** — homozygous/hemizygous occurrences of the variant in an
  unselected population database (gnomAD).

This is the second known-gaps **model** item (after Gene-Disease Validity). It
**captures** the structured inputs a curator records and **documents** how they
score — but computes no points, consistent with the repo's scope boundary
(evidence + classification; method/rule enforcement is owned elsewhere and
deferred, e.g. `validate_case`).

## 2. Source material (this pass)

- **Supplementary Material 3 (Population Database Frequency)**, verbatim in
  `source-material/svcv4-supplements/SM03-population-frequency.txt` (gitignored;
  ingested 2026-08-13). All scoring specifics below are from it.
- **Existing model architecture:** `src/svcv4_model/evidence_item.py`
  (`EvidenceItem` — the generic VA-Spec container with an open `data: dict`
  payload), `src/svcv4_model/case.py` (`Case` — the typed payload for a
  `clinical_observation` item; `TriState`; `WorkflowParameters.moi` /
  `pop_frq_points`), `src/svcv4_model/inputs.py` (`Vbc`/`Mde` curation-level
  counterparts to formal VA-Spec inputs).
- **VA-Spec Cohort Allele Frequency Study Result** profile
  (<https://va-spec.ga4gh.org/en/1.0/va-standard-profiles/base-profiles/study-result-profiles.html#cohort-allele-frequency-study-result>):
  `focusAllele`, `focusAlleleCount`, `locusAlleleCount`, `focusAlleleFrequency`,
  `cohort`, `subCohortFrequency`, `ancillaryResults`, `qualityMeasures`. Note it
  carries a *raw* cohort frequency, **not** the FAF or DAFT that SVCv4 scoring
  actually uses — those are SVCv4-specific derived/threshold values.
- **Current POP stub:** `docs/workflows/hod/pop.md` (already sketches the intended
  VA-Spec-adoption + DAFT approach; its "POP_HMZ source not read yet" note is now
  stale) and the forward-looking `concepts.md` Cohort Allele Frequency / DAFT
  entries.

## 3. Key findings driving this work

### 3.1 POP_FRQ scoring (documented, not computed)

Benignity-only, four strengths by fold-change of the variant's **FAF** vs the
MDE's **DAFT**:

| FAF vs DAFT | `POP_FRQ` points |
|---|---|
| < 1.5× | 0.0 |
| > 1.5× and < 5× | −1.0 |
| > 5× and < 15× | −3.0 |
| ≥ 15× | −6.0 |

(Worked example from SM 3: FBN1-related Marfan, DAFT 0.000118 → band cutoffs at
FAF 0.000177 / 0.000590 / 0.001770.) The inequalities are reproduced verbatim
from SM 3, which does not crisply assign the exact boundary values (=1.5×, =5×,
=15×); the worked example treats the top boundary as inclusive (FAF ≥ 0.001770 →
−6.0). Since nothing in this pass computes points, the docs mirror SM 3's wording
and flag the boundary ambiguity rather than inventing a rule.

### 3.2 DAFT — one value, four provenances

DAFT is the MDE-specific ceiling on a pathogenic variant's population frequency.
**Preferred:** a VCEP/community-curated threshold. Otherwise one of three
derivation methods:

- **Calculator** (preferred derivation): five inputs — prevalence, penetrance,
  locus heterogeneity, allelic heterogeneity, inheritance pattern
  (cardiodb.org/allelefrequencyapp).
- **Binning** (sparse-data / X-linked): eight prevalence bins × three penetrance
  bins, DAFT read from lookup Tables 1–6 by inheritance.
- **Pathogenic-variants** (≥ 10 P/LP; also a cross-check).

The **inheritance pattern** the calculator needs is already the shared
`WorkflowParameters.moi` — it is **not** re-captured on the POP entity.

### 3.3 POP_HMZ scoring (documented, not computed)

−0.5 points per eligible occurrence, **counted only from the 2nd** eligible
occurrence: homozygous occurrences for AD/AR MDEs, homozygous *or* hemizygous for
X-linked. Eligibility is gated on the MDE's penetrance + severity making affected
individuals implausible in gnomAD (Table 7). Example: 3 homozygous occurrences
in an AR MDE → `POP_HMZ_-1.0` (1st free; 2nd and 3rd −0.5 each). This is
distinct from `CLN_UAF`, which requires explicit clinical details.

### 3.4 POP is a different evidence payload than Case, with no applicability matrix

`Case` is the typed payload for a `clinical_observation` `EvidenceItem`. POP
evidence is population-database evidence *about the variant*, a **separate**
payload for a `population_frequency` `EvidenceItem`. Unlike `Case`, POP has **no
seven-workflow required/optional/conditional structure** — `POP_FRQ` and
`POP_HMZ` are simply two facets of one population-evidence datum. So POP is
modeled as a single permissive entity (every field optional) with documented
field semantics, and it gets **no applicability-matrix entry** and does **not**
touch `docs/workflows/case-model.md` or the Case applicability tests.

### 3.5 Curation-level counterpart, per the Vbc/Mde precedent

Like `Vbc`/`Mde`, the POP entity is a lightweight **curation-level** counterpart
carrying what SVCv4 curators actually record (FAF, DAFT + method + inputs,
homozygote/hemizygote counts), documented as reconciling later with the formal
VA-Spec Cohort Allele Frequency Study Result — which is not adopted wholesale
here because it carries raw cohort counts SVCv4 scoring does not use and lacks
FAF/DAFT entirely.

## 4. Scope

**In scope (this pass):**
- New module `src/svcv4_model/population.py` with `PopulationEvidence` (permissive
  superset, every field optional), a nested `DaftCalculatorInputs`, and a
  `DaftMethod` enum (§5.1).
- Export the new public names from `src/svcv4_model/__init__.py` (§5.2).
- Regenerate the committed JSON Schemas (`export_schemas.py`) — new
  `schemas/json/PopulationEvidence.schema.json` (and any nested `$defs`
  inline) (§5.3).
- Docs: `pop.md` stub → modeled; `concepts.md` Cohort Allele Frequency + DAFT
  entries → modeled; `known-gaps.md` remove the two POP rows; `spec-alignment.md`
  SM 3 row → modeled; forward pointer from `capturing-basic-evidence.md` (§5.4).
- Tests: new `tests/test_population.py` (§5.5).

**Out of scope / deferred (see §7):**
- Any point computation (FAF-vs-DAFT bands, POP_HMZ tally). Documented only.
- Binning lookup grids (Tables 1–6) and pathogenic-variants list structuring —
  `daft_method` records *which* method; the method's detailed inputs beyond the
  calculator's four are not modeled.
- Wiring `PopulationEvidence` into `EvidenceItem.data` as a typed union — it stays
  loosely coupled and documented as the `population_frequency` payload, exactly
  like `Case`.
- Reconciliation with the formal VA-Spec Cohort Allele Frequency Study Result.
- Removing/altering `WorkflowParameters.pop_frq_points` — it stays; it carries the
  scored *result*, this entity carries the *evidence behind it*.

## 5. Content changes, item by item

### 5.1 New model: `src/svcv4_model/population.py`

```python
"""SVCv4 Population (POP) evidence — the payload behind a population_frequency
Evidence Item: population-database frequency evidence about the variant.

Covers the two POP evidence codes, both benignity-only:
- POP_FRQ: the variant's Filtering Allele Frequency (FAF) vs the MDE's Disease
  Allele Frequency Threshold (DAFT).
- POP_HMZ: homozygous/hemizygous occurrences in an unselected population database.

Curation-level counterpart to the formal VA-Spec Cohort Allele Frequency Study
Result; the two reconcile in a later phase. Like Case, every field is optional;
scoring (see docs/workflows/hod/pop.md) is documented, not computed here.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.case import TriState


class DaftMethod(StrEnum):
    """How the Disease Allele Frequency Threshold was derived (SM 3).

    VCEP_CURATED is the preferred source (an expert-consensus threshold);
    the other three are derivation methods when no curated threshold exists.
    """

    VCEP_CURATED = "VCEP_CURATED"
    CALCULATOR = "CALCULATOR"
    BINNING = "BINNING"
    PATHOGENIC_VARIANTS = "PATHOGENIC_VARIANTS"


class DaftCalculatorInputs(BaseModel):
    """The four quantitative inputs to the DAFT calculator method (SM 3).

    The fifth calculator input, inheritance pattern, is the shared
    ``WorkflowParameters.moi`` and is not re-captured here.
    """

    model_config = ConfigDict(extra="forbid")

    prevalence_denominator: int | None = Field(
        default=None,
        description="X in a phenotype prevalence of '1 in X'; use the smallest reasonable X.",
    )
    penetrance: float | None = Field(
        default=None, description="Expected penetrance (0-1); use the lowest reasonable estimate."
    )
    locus_heterogeneity: float | None = Field(
        default=None, description="Fraction of cases attributable to this locus (0-1)."
    )
    allelic_heterogeneity: float | None = Field(
        default=None, description="Fraction of disease alleles this variant could represent (0-1)."
    )


class PopulationEvidence(BaseModel):
    """Population-database frequency evidence for the VBC (POP_FRQ + POP_HMZ).

    Permissive superset: every field is optional. The payload behind a
    ``population_frequency`` Evidence Item; a curation-level counterpart to the
    VA-Spec Cohort Allele Frequency Study Result.
    """

    model_config = ConfigDict(extra="forbid")

    # POP_FRQ
    faf: float | None = Field(
        default=None,
        description=(
            "Filtering Allele Frequency (population-max, lower-95%-CI-bound AF), e.g. from gnomAD."
        ),
    )
    faf_source: str | None = Field(
        default=None, description="Source/version of the FAF, e.g. 'gnomAD v4.1.1'."
    )
    daft: float | None = Field(
        default=None,
        description=(
            "Disease Allele Frequency Threshold: the MDE-specific ceiling "
            "the FAF is compared against."
        ),
    )
    daft_method: DaftMethod | None = Field(
        default=None, description="How the DAFT was obtained/derived (see DaftMethod)."
    )
    daft_calculator_inputs: DaftCalculatorInputs | None = Field(
        default=None,
        description=(
            "The calculator method's inputs, when daft_method is CALCULATOR "
            "(optional, for reproducibility)."
        ),
    )

    # POP_HMZ
    homozygote_count: int | None = Field(
        default=None,
        description="Number of homozygous occurrences of the VBC in the population database.",
    )
    hemizygote_count: int | None = Field(
        default=None, description="Number of hemizygous occurrences (X-linked) of the VBC."
    )
    hmz_eligible: TriState | None = Field(
        default=None,
        description=(
            "Whether the MDE's penetrance + severity make affected individuals implausible in the "
            "population database, so occurrences count as benignity evidence (SM 3, Table 7)."
        ),
    )
```

### 5.2 Export (`src/svcv4_model/__init__.py`)

Add `DaftCalculatorInputs`, `DaftMethod`, `PopulationEvidence` to the imports and
`__all__`, alphabetically, mirroring the other models/enums. `export_schemas.py`
emits a schema file per public **BaseModel** class in `__all__` — so
`PopulationEvidence.schema.json` and `DaftCalculatorInputs.schema.json` are
written; `DaftMethod` (a `StrEnum`) gets no file of its own, inlined as `$defs`.

**Note on the Vbc/Mde precedent (§3.5):** we follow Vbc/Mde *conceptually* (a
curation-level counterpart to a formal VA-Spec entity) but **diverge on export** —
`Vbc`/`Mde` are deliberately kept out of `__all__` (no schema file), whereas
`PopulationEvidence` is exported like `Case` (a top-level payload) and
`DaftCalculatorInputs` is exported like the `Case` nested helpers (`Age`,
`CaseTesting`, …). That divergence is intentional, not an oversight.

### 5.3 Regenerate JSON Schemas

Run `uv run python scripts/export_schemas.py` and commit the new
`schemas/json/*.schema.json` files. `export_case_views.py` and
`docs/workflows/case-model.md` are **unaffected** (Case-only). The CI drift gate
(`git diff --quiet -- schemas/json docs/workflows/case-model.md`) covers the new
schema files.

### 5.4 Docs

- **`docs/workflows/hod/pop.md`** — replace the `!!! note "Not yet modeled here"`
  with modeled content: the field list (`PopulationEvidence`), the POP_FRQ band
  table (§3.1) and POP_HMZ rule (§3.3) as *documented scoring* (state clearly the
  model captures inputs and does not compute points), and a link to
  [SM 3](https://docs.google.com/document/d/1XON2eq4HSM-guWlqitEnb8PghY0quNbA7_1WmmxvLj8/edit).
  Update the stale "POP_HMZ source not read yet" line.
- **`docs/reference/concepts.md`** — Cohort Allele Frequency and DAFT entries flip
  from "Not yet modeled" to modeled, pointing at `PopulationEvidence`
  (`faf`/`daft`/`daft_method`/`daft_calculator_inputs`); keep the VA-Spec profile
  link and note the curation-level-counterpart relationship.
- **`docs/reference/known-gaps.md`** — remove the "Cohort Allele Frequency
  representation" and "Disease Allele Frequency Threshold (DAFT)" model-gap rows;
  update the "Full POP modeling" content-gap row (now largely done, HMZ/FRQ inputs
  modeled; point computation still deferred).
- **`docs/reference/spec-alignment.md`** — SM 3 row coverage → "Modeled (inputs;
  scoring documented, not computed)"; keep the SM 3 link-out.
- **`docs/getting-started/capturing-basic-evidence.md`** — the line noting the
  model "currently only carries the result, `pop_frq_points`, not the raw
  evidence" gains a forward pointer to `PopulationEvidence`.

### 5.5 Tests: `tests/test_population.py`

- Round-trip: a maximal `PopulationEvidence` (all fields incl. nested
  `DaftCalculatorInputs` and a `DaftMethod`) survives `model_dump(mode="json")` →
  `model_validate`.
- Permissive: empty `PopulationEvidence()` validates; `extra="forbid"` rejects an
  unknown field.
- Enum: each `DaftMethod` value round-trips; `hmz_eligible` accepts each
  `TriState`.
- Importable from the package root (mirrors `test_case_is_importable_from_package_root`).

## 6. Quality gates

- `uv run pytest -q` — green (new `tests/test_population.py`, no regressions).
- Drift gate (exact CI command):
  `uv run python scripts/export_schemas.py && uv run python scripts/export_case_views.py && git diff --quiet -- schemas/json docs/workflows/case-model.md` → clean after committing the new schema file(s).
- `uv run mkdocs build --strict` — passes (new SM link-out is external; internal
  links resolve).
- `uv run ruff check` and `uv run ruff format --check .` — clean (both run in CI;
  `ruff` uses `line-length = 100`, so keep field descriptions wrapped with
  parenthesized concatenation as shown in §5.1).
- `grep -n "Not yet modeled" docs/reference/concepts.md` no longer matches the
  Cohort Allele Frequency or DAFT sections.

## 7. Follow-up backlog (explicitly not this pass)

1. **POP scoring computation** — FAF-vs-DAFT band lookup and POP_HMZ tally — with
   the rest of the deferred rule/method enforcement (`validate_case`).
2. **Binning lookup grids (Tables 1–6)** and **pathogenic-variants list**
   structuring, if curators need the full derivation captured structurally.
3. **Reconcile `PopulationEvidence` with the formal VA-Spec Cohort Allele
   Frequency Study Result** (and, more broadly, wire typed payloads into
   `EvidenceItem.data`).
4. Remaining known-gaps items (the two `CLN_AFF` sub-fields; PFD; `CLN_CCS` when
   SVCv4 defines evidence concepts for it).

## 8. Delivery

Branch `feat/pop-daft-modeling` (off `docs/review-followup` / PR #23; rebases onto
`main` once #23 merges). Single PR. CI: pytest, the schema/docs drift gate (new
schema files), and `mkdocs build --strict`.
