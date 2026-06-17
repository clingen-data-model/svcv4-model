# Case Model Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the SVCv4 `Case` model — a permissive superset Pydantic entity, a declarative applicability matrix, five derived per-workflow JSON Schemas, and docs — exactly as specified in `docs/superpowers/specs/2026-06-11-case-model-design.md`.

**Architecture:** A permissive superset `Case` model (all fields optional) lives in `src/svcv4_model/case.py` and is exported so the existing `scripts/export_schemas.py` auto-emits `schemas/json/Case.schema.json`. A single YAML matrix (`schemas/applicability/case_applicability.yaml`) is the source of truth for per-workflow applicability (`r/o/c/x`) and conditional rules; a loader reads it. A new generator (`scripts/export_case_views.py`) prunes the superset schema per workflow into `schemas/json/case/CLN_*.schema.json` and writes the docs applicability tables. CI runs both exporters before the drift check.

**Tech Stack:** Python 3.11–3.13, Pydantic v2, PyYAML, pytest, ruff, uv, MkDocs (mkdocstrings).

**Working branch:** `feat/case-model` (already created off `main`; PR #17 open). Commit after each task; the PR stays in sync via `git push`.

**Conventions (match the existing codebase):**
- Every model: `model_config = ConfigDict(extra="forbid")`.
- Enums subclass `(str, Enum)` so they serialize to their token strings.
- `from __future__ import annotations` at the top of every module.
- Rich `Field(description=...)` text; sheet's human strings become descriptions.
- Run everything through `uv run` (e.g. `uv run pytest`, `uv run ruff format .`).
- After writing code, run `uv run ruff format .` and `uv run ruff check . --fix` before committing.

---

## Chunk 1: Data model + superset schema

**File structure for this chunk:**
- Create `src/svcv4_model/case.py` — all enums + value types (`Age`, `Phenotype`) + sub-models + `Case` + `Workflow` enum.
- Modify `src/svcv4_model/__init__.py` — export the public `Case` API.
- Create `tests/test_case.py` — model round-trip + tri-state + forbid-extra tests.
- Regenerate `schemas/json/Case.schema.json` via the existing exporter.

### Task 1.1: Create the `case.py` enums and value types

**Files:**
- Create: `src/svcv4_model/case.py`
- Test: `tests/test_case.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_case.py`:

```python
"""Tests for the SVCv4 Case model."""

from __future__ import annotations

import pytest

from svcv4_model.case import (
    MOI,
    Age,
    AgeQualifier,
    AgeUnit,
    Phenotype,
    Sex,
    TriState,
)


def test_enums_serialize_to_tokens() -> None:
    assert MOI.AD.value == "AD"
    assert Sex.U.value == "U"
    assert TriState.UNKNOWN.value == "UNKNOWN"
    assert AgeUnit.MONTH.value == "MONTH"
    assert AgeQualifier.RANGE.value == "RANGE"


def test_age_accepts_point_and_range() -> None:
    point = Age(value=7, unit=AgeUnit.MONTH, qualifier=AgeQualifier.EXACT, raw="7 mo")
    rng = Age(min=5, max=10, unit=AgeUnit.MONTH, qualifier=AgeQualifier.RANGE, raw="5-10 months")
    assert point.value == 7
    assert rng.min == 5 and rng.max == 10


def test_phenotype_either_field_optional() -> None:
    coded = Phenotype(code="HP:0001250", name="Seizure")
    freetext = Phenotype(name="unusual gait")
    assert coded.code == "HP:0001250"
    assert freetext.code is None


def test_age_forbids_extra() -> None:
    with pytest.raises(ValueError):
        Age(value=1, unit=AgeUnit.YEAR, bogus="x")  # type: ignore[call-arg]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_case.py -v`
Expected: FAIL — `ModuleNotFoundError`/`ImportError` (`svcv4_model.case` does not exist).

- [ ] **Step 3: Write minimal implementation (enums + value types)**

Create `src/svcv4_model/case.py` with the header, enums, and value types:

```python
"""SVCv4 Case model — the case-level clinical-observation (CLN) evidence payload.

A ``Case`` is the structured payload behind a ``clinical_observation``
Evidence Item: the superset of all attributes a curator captures from the
literature to represent a single human clinical observation supporting (or
opposing) variant pathogenicity.

The model is intentionally **permissive** — every field is optional. Which
fields are required / optional / conditional / not-applicable per CLN
workflow is expressed by the declarative applicability matrix
(``schemas/applicability/case_applicability.yaml``), NOT by this type. See
``docs/superpowers/specs/2026-06-11-case-model-design.md``.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Workflow(str, Enum):
    """The five CLN evidence-assessment workflows.

    ``CLN_ALTV`` and ``CLN_ALTG`` generalize to ``CLN_ALT``; they are kept
    separate here because their applicability rules diverge.
    """

    CLN_AFF = "CLN_AFF"
    CLN_DNV = "CLN_DNV"
    CLN_ALTV = "CLN_ALTV"
    CLN_ALTG = "CLN_ALTG"
    CLN_UAF = "CLN_UAF"


class MOI(str, Enum):
    """Mode of inheritance. ALTV does not yet support AR/XLR."""

    AD = "AD"
    AR = "AR"
    XLD = "XLD"
    XLR = "XLR"
    SD = "SD"


class Sex(str, Enum):
    """Proband sex: Male / Female / Unknown / Trans."""

    M = "M"
    F = "F"
    U = "U"
    T = "T"


class PhenoSpecificity(str, Enum):
    """Phenotype specificity for the gene."""

    SPECIFIC = "SPECIFIC"
    CONSISTENT = "CONSISTENT"
    INCONSISTENT = "INCONSISTENT"


class PhenoSeverity(str, Enum):
    """Phenotype severity relative to expectation.

    ``BIALLELIC_LT_EXPECTED`` is not applicable to the ALT Gene workflow
    (see the applicability matrix's ``enum_exclude`` rule).
    """

    MONO_GT_OR_BIALLELIC_EQ_EXPECTED = "MONO_GT_OR_BIALLELIC_EQ_EXPECTED"
    MONO_EQ_EXPECTED = "MONO_EQ_EXPECTED"
    BIALLELIC_LT_EXPECTED = "BIALLELIC_LT_EXPECTED"


class AgeMatchedPenetrance(str, Enum):
    """Age-matched penetrance bands."""

    LT_80 = "LT_80"
    PCT_80_100 = "PCT_80_100"
    NEAR_100 = "NEAR_100"


class Zygosity(str, Enum):
    """Zygosity of a variant in the case."""

    HOM = "HOM"
    HET = "HET"
    HEMI = "HEMI"


class Phase(str, Enum):
    """Phase of a variant in reference to the VBC."""

    TRANS = "TRANS"
    CIS = "CIS"
    UNKNOWN = "UNKNOWN"


class AgeUnit(str, Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class AgeQualifier(str, Enum):
    """How to read an ``Age``: a point value, a bound, or a range."""

    EXACT = "EXACT"
    GT = "GT"
    LT = "LT"
    APPROX = "APPROX"
    RANGE = "RANGE"


class TriState(str, Enum):
    """Tri-state truth value.

    ``TRUE``/``FALSE`` — the curator established the value. ``UNKNOWN`` —
    the curator looked and could not determine it. A ``null`` field (absent)
    means the value was **not captured at all**; ``UNKNOWN`` and ``null`` are
    semantically distinct.
    """

    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class Age(BaseModel):
    """A structured age covering point values, bounds, and ranges."""

    model_config = ConfigDict(extra="forbid")

    value: float | None = Field(default=None, description="Point value (with EXACT/GT/LT/APPROX).")
    min: float | None = Field(default=None, description="Lower bound (with RANGE).")
    max: float | None = Field(default=None, description="Upper bound (with RANGE).")
    unit: AgeUnit | None = Field(default=None, description="Unit for value/min/max.")
    qualifier: AgeQualifier | None = Field(
        default=None, description="How to interpret the value(s)."
    )
    raw: str | None = Field(default=None, description="Original curator text, preserved verbatim.")


class Phenotype(BaseModel):
    """A phenotype as a ``{name, code}`` pair; either may stand alone."""

    model_config = ConfigDict(extra="forbid")

    code: str | None = Field(
        default=None,
        description="HPO id/code, preferred (e.g. `HP:0001250`).",
    )
    name: str | None = Field(
        default=None,
        description=(
            "Label of the coded entry when a code is given; otherwise a "
            "free-text term the curator could not confidently match to HPO."
        ),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_case.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Format, lint, commit**

```bash
uv run ruff format .
uv run ruff check . --fix
git add src/svcv4_model/case.py tests/test_case.py
git commit -m "feat: Case model enums and value types (Age, Phenotype)"
```

### Task 1.2: Add the sub-models and the `Case` aggregate

**Files:**
- Modify: `src/svcv4_model/case.py` (append sub-models + `Case`)
- Test: `tests/test_case.py` (append round-trip test)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_case.py`:

```python
from svcv4_model.case import (  # noqa: E402  (grouped here for the plan; merge with the import above)
    AdditionalVariant,
    Case,
    CaseProbandInfo,
    CaseVariant,
    CompoundHetVariant,
    Gene,
    Phase,
    Zygosity,
)


def _maximal_case() -> Case:
    return Case(
        moi=MOI.AR,
        pop_frq_points=-1.0,
        case_proband_info=CaseProbandInfo(
            sex=Sex.F,
            age=Age(value=7, unit=AgeUnit.MONTH, qualifier=AgeQualifier.EXACT, raw="7 mo"),
            phenotypes=[Phenotype(code="HP:0001250", name="Seizure")],
            pheno_specificity_for_gene=PhenoSpecificity.SPECIFIC,
            pheno_severity=PhenoSeverity.MONO_EQ_EXPECTED,
            age_matched_penetrance=AgeMatchedPenetrance.NEAR_100,
            confirmed_parental_relationship=TriState.UNKNOWN,
            all_relevant_genes_tested=TriState.TRUE,
        ),
        vbc=CaseVariant(id="clinvar:VCV000000001", zygosity=Zygosity.HET),
        compound_het_variant=CompoundHetVariant(
            id="clinvar:VCV000000002",
            zygosity=Zygosity.HET,
            phase_in_ref_to_vbc=Phase.TRANS,
            phase_confidence="high",
            classification="P",
        ),
        additional_variant_exists=TriState.TRUE,
        additional_variants=[
            AdditionalVariant(
                id="clinvar:VCV000000003",
                gene=Gene(symbol="ABCA4", mde_associated_gene="ABCA4"),
                zygosity=Zygosity.HOM,
                phase_in_ref_to_vbc=Phase.CIS,
                phase_confidence="low",
                classification="LP",
            )
        ],
    )


def test_case_round_trips_json() -> None:
    original = _maximal_case()
    payload = original.model_dump(mode="json")
    assert payload["additional_variant_exists"] == "TRUE"  # tri-state serializes to token
    rehydrated = Case.model_validate(payload)
    assert rehydrated == original


def test_case_is_permissive_when_empty() -> None:
    # The superset is permissive: an empty Case is valid (applicability is the matrix's job).
    assert Case().model_dump(exclude_none=True) == {"additional_variants": [], }


def test_case_forbids_extra() -> None:
    payload = _maximal_case().model_dump(mode="json")
    payload["unexpected"] = "x"
    with pytest.raises(ValueError):
        Case.model_validate(payload)


def test_pop_frq_points_floor() -> None:
    with pytest.raises(ValueError):
        Case(pop_frq_points=-1.5)
```

> Note for the implementer: merge the two `from svcv4_model.case import (...)` blocks in this file into one sorted import (ruff will flag the duplicate). The split above is only for readability in the plan.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_case.py -v`
Expected: FAIL — `ImportError` for `Case`/sub-models.

- [ ] **Step 3: Write minimal implementation (append to `case.py`)**

```python
class CaseProbandInfo(BaseModel):
    """Proband-level observations captured for the case."""

    model_config = ConfigDict(extra="forbid")

    sex: Sex | None = Field(default=None)
    age: Age | None = Field(default=None)
    phenotypes: list[Phenotype] = Field(
        default_factory=list,
        description="0..many phenotypes; capture at least what is relevant to the case.",
    )
    pheno_specificity_for_gene: PhenoSpecificity | None = Field(default=None)
    pheno_severity: PhenoSeverity | None = Field(default=None)
    age_matched_penetrance: AgeMatchedPenetrance | None = Field(default=None)
    confirmed_parental_relationship: TriState | None = Field(
        default=None, description="Whether the parental relationship was confirmed."
    )
    all_relevant_genes_tested: TriState | None = Field(
        default=None, description="Whether all relevant genes for the disorder were tested."
    )


class CaseVariant(BaseModel):
    """The VBC as referenced at the case level (id + case-level zygosity)."""

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None, description="Identifier for the variant being classified.")
    zygosity: Zygosity | None = Field(default=None)


class CompoundHetVariant(BaseModel):
    """The second variant in a biallelic AFF evaluation against a het VBC.

    Used only in the Affected workflow. Per the applicability matrix the
    ``zygosity`` is fixed to ``HET`` and ``phase_in_ref_to_vbc`` to ``TRANS``.
    """

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None)
    zygosity: Zygosity | None = Field(default=None, description="Fixed to HET in the AFF workflow.")
    phase_in_ref_to_vbc: Phase | None = Field(
        default=None, description="Fixed to TRANS in the AFF workflow."
    )
    phase_confidence: str | None = Field(default=None, description="Confidence in the phase call.")
    classification: str | None = Field(
        default=None, description="Variant classification (placeholder string this phase)."
    )


class Gene(BaseModel):
    """A gene reference; ``mde_associated_gene`` set when it differs from the VBC gene."""

    model_config = ConfigDict(extra="forbid")

    symbol: str | None = Field(default=None, description="Gene symbol.")
    mde_associated_gene: str | None = Field(
        default=None,
        description="MDE-associated gene, required when the gene differs from the VBC gene.",
    )


class AdditionalVariant(BaseModel):
    """An additional variant in the case (ALTV/ALTG, or AFF when present)."""

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None)
    gene: Gene | None = Field(default=None)
    zygosity: Zygosity | None = Field(default=None)
    phase_in_ref_to_vbc: Phase | None = Field(
        default=None, description="Captured only if the additional variant shares the VBC gene."
    )
    phase_confidence: str | None = Field(
        default=None, description="Captured only if phase is captured."
    )
    classification: str | None = Field(
        default=None,
        description="Variant classification; must be P/LP for the ALTV and ALTG workflows.",
    )


class Case(BaseModel):
    """Superset of case-level CLN-observation attributes (permissive)."""

    model_config = ConfigDict(extra="forbid")

    moi: MOI | None = Field(default=None, description="Mode of inheritance.")
    pop_frq_points: float | None = Field(
        default=None, ge=-1.0, description="Population-frequency points (must be >= -1.0)."
    )
    case_proband_info: CaseProbandInfo | None = Field(default=None)
    vbc: CaseVariant | None = Field(default=None, description="The variant being classified.")
    compound_het_variant: CompoundHetVariant | None = Field(default=None)
    additional_variant_exists: TriState | None = Field(
        default=None, description="Whether an additional variant exists in the case."
    )
    additional_variants: list[AdditionalVariant] = Field(
        default_factory=list,
        description="Additional variant(s); populated only if `additional_variant_exists` is TRUE.",
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_case.py -v`
Expected: PASS.

- [ ] **Step 5: Format, lint, commit**

```bash
uv run ruff format .
uv run ruff check . --fix
git add src/svcv4_model/case.py tests/test_case.py
git commit -m "feat: Case sub-models and superset aggregate"
```

### Task 1.3: Export the public `Case` API and regenerate the superset schema

**Files:**
- Modify: `src/svcv4_model/__init__.py`
- Test: `tests/test_case.py` (append import-surface test)
- Regenerate: `schemas/json/Case.schema.json`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_case.py`:

```python
def test_case_is_importable_from_package_root() -> None:
    import svcv4_model

    assert "Case" in svcv4_model.__all__
    assert svcv4_model.Case is Case
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_case.py::test_case_is_importable_from_package_root -v`
Expected: FAIL — `AttributeError`/`assert "Case" in __all__`.

- [ ] **Step 3: Implement — extend `__init__.py`**

Add the import and `__all__` entries. Export the public surface (the aggregate, the sub-models, the enums) but **NOT** the matrix loader (it is not a Pydantic model). Insert a `case` import block and extend `__all__`:

```python
from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    Age,
    AgeMatchedPenetrance,
    AgeQualifier,
    AgeUnit,
    Case,
    CaseProbandInfo,
    CaseVariant,
    CompoundHetVariant,
    Gene,
    Phase,
    Phenotype,
    PhenoSeverity,
    PhenoSpecificity,
    Sex,
    TriState,
    Workflow,
    Zygosity,
)
```

Add each of these names to `__all__` (keep it sorted to match the existing style).

> Why this matters: `scripts/export_schemas.py` iterates `svcv4_model.__all__` and emits a schema for every `BaseModel` subclass. Exporting `Case` (and its sub-models) makes `schemas/json/Case.schema.json` (and one file per sub-model) generate automatically. The enums are not `BaseModel`s, so they produce no files — that is fine.

- [ ] **Step 4: Run tests + regenerate schema + verify no unexpected drift**

```bash
uv run pytest -q
uv run python scripts/export_schemas.py
git status --porcelain schemas/json
```
Expected: tests PASS; new files appear under `schemas/json/` for `Case` and each sub-model (`Age`, `Phenotype`, `CaseProbandInfo`, `CaseVariant`, `CompoundHetVariant`, `Gene`, `AdditionalVariant`).

- [ ] **Step 5: Commit**

```bash
git add src/svcv4_model/__init__.py schemas/json
git commit -m "feat: export Case public API; regenerate superset JSON Schemas"
```

---

## Chunk 2: Applicability matrix + loader

**File structure for this chunk:**
- Modify `pyproject.toml` — add `pyyaml` runtime dependency.
- Create `schemas/applicability/case_applicability.yaml` — the matrix (source of truth).
- Create `src/svcv4_model/case_applicability.py` — loader (kept out of `__all__`).
- Create `tests/test_case_applicability.py` — matrix-shape + loader tests.

### Task 2.1: Add the PyYAML dependency

**Files:**
- Modify: `pyproject.toml:` (the `dependencies` array)

- [ ] **Step 1: Add the dependency**

In `pyproject.toml`, add `"pyyaml>=6,<7"` to the `dependencies` list (next to `pydantic`).

- [ ] **Step 2: Sync and verify import**

```bash
uv sync
uv run python -c "import yaml; print(yaml.__version__)"
```
Expected: prints a 6.x version.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "build: add PyYAML dependency for the applicability matrix loader"
```

### Task 2.2: Author the applicability matrix YAML

**Files:**
- Create: `schemas/applicability/case_applicability.yaml`

- [ ] **Step 1: Write the matrix**

Create `schemas/applicability/case_applicability.yaml`. Keys are dotted field paths into the `Case` model (array element fields use the array name as the parent, e.g. `additional_variants.id`). Applicability codes are `r`/`o`/`c`/`x`. Reproduce exactly:

```yaml
# Source of truth for Case attribute applicability across the five CLN workflows.
# Codes: r=required, o=optional, c=conditional (see `rule`), x=not applicable.
# Derived from the SVCv4 case-attributes sheet (tab 138412089).

moi:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: r }
  value: "AD, AR, XLD, XLR, SD"
  notes: "ALTV does not yet support AR/XLR"

pop_frq_points:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }
  notes: "must be >= -1.0"

case_proband_info:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: r }

case_proband_info.sex:
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: o, CLN_ALTG: o, CLN_UAF: o }
  value: "M/F/U/T"

case_proband_info.age:
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: o, CLN_ALTG: o, CLN_UAF: o }
  notes: "age + unit, or an age range; general or disease-specific"

case_proband_info.phenotypes:
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: o, CLN_ALTG: o, CLN_UAF: o }
  value: "0..many"

case_proband_info.phenotypes.name:
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: o, CLN_ALTG: o, CLN_UAF: o }

case_proband_info.phenotypes.code:
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: o, CLN_ALTG: o, CLN_UAF: o }
  notes: "HPO identifier when possible"

case_proband_info.pheno_specificity_for_gene:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }
  value: "SPECIFIC, CONSISTENT, INCONSISTENT"
  notes: "curator makes the PHENO SPECIFICITY call; rule coordination is out of scope"

case_proband_info.pheno_severity:
  applicability: { CLN_AFF: x, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: c, CLN_UAF: x }
  rule: { workflow: CLN_ALTG, effect: enum_exclude, value: BIALLELIC_LT_EXPECTED }
  notes: "BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG"

case_proband_info.age_matched_penetrance:
  applicability: { CLN_AFF: o, CLN_DNV: o, CLN_ALTV: x, CLN_ALTG: c, CLN_UAF: r }
  value: "<80%, 80-100%, near 100%"
  notes: "only applicable at all for ALT Gene among the conditional workflows"

case_proband_info.confirmed_parental_relationship:
  applicability: { CLN_AFF: x, CLN_DNV: r, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }

case_proband_info.all_relevant_genes_tested:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }

vbc:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: r }

vbc.id:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: r }

vbc.zygosity:
  applicability: { CLN_AFF: r, CLN_DNV: r, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: r }
  notes: "the only variant_type element needed for case-level VBC assessment"

compound_het_variant:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }
  rule: { requires: { context: "biallelic disease eval with a het VBC" } }
  notes: "AFF only; otherwise use additional_variant"

compound_het_variant.id:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }

compound_het_variant.zygosity:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }
  rule: { workflow: CLN_AFF, effect: fixed, value: HET }

compound_het_variant.phase_in_ref_to_vbc:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }
  rule: { workflow: CLN_AFF, effect: fixed, value: TRANS }

compound_het_variant.phase_confidence:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }

compound_het_variant.classification:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: x, CLN_ALTG: x, CLN_UAF: x }

additional_variant_exists:
  applicability: { CLN_AFF: r, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }

additional_variants:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }
  rule: { requires: { field: additional_variant_exists, equals: TRUE } }
  notes: "compound-het additional variants are NOT supported"

additional_variants.id:
  applicability: { CLN_AFF: r, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }

additional_variants.gene:
  applicability: { CLN_AFF: r, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }

additional_variants.gene.symbol:
  applicability: { CLN_AFF: r, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }
  notes: "gene symbol; follows the gene's applicability"

additional_variants.gene.mde_associated_gene:
  applicability: { CLN_AFF: r, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }
  notes: "required if gene is different from VBC gene"

additional_variants.zygosity:
  applicability: { CLN_AFF: r, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }
  value: "HOM / HET / HEMI"

additional_variants.phase_in_ref_to_vbc:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: x, CLN_UAF: x }
  notes: "only if same gene as VBC"

additional_variants.phase_confidence:
  applicability: { CLN_AFF: c, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: x, CLN_UAF: x }
  notes: "only if phase is captured"

additional_variants.classification:
  applicability: { CLN_AFF: r, CLN_DNV: x, CLN_ALTV: r, CLN_ALTG: r, CLN_UAF: x }
  notes: "must be P-LP if ALTV or ALTG use case"
```

- [ ] **Step 2: Sanity check it parses**

Run: `uv run python -c "import yaml; d=yaml.safe_load(open('schemas/applicability/case_applicability.yaml')); print(len(d), 'entries')"`
Expected: prints `32 entries`. (This count must equal the number of dotted-path keys; the matrix/model parity test in Task 2.4 is the real guard — this is just a quick smoke check.)

- [ ] **Step 3: Commit**

```bash
git add schemas/applicability/case_applicability.yaml
git commit -m "feat: case applicability matrix (source of truth)"
```

### Task 2.3: Implement the matrix loader

**Files:**
- Create: `src/svcv4_model/case_applicability.py`
- Test: `tests/test_case_applicability.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_case_applicability.py`:

```python
"""Tests for the Case applicability matrix and its loader."""

from __future__ import annotations

from svcv4_model.case import Workflow
from svcv4_model.case_applicability import (
    VALID_CODES,
    field_paths,
    load_matrix,
    workflow_codes,
)


def test_matrix_loads_and_codes_are_valid() -> None:
    matrix = load_matrix()
    assert "moi" in matrix
    for path, entry in matrix.items():
        codes = entry["applicability"]
        assert set(codes) == {w.value for w in Workflow}, f"{path} missing a workflow"
        for value in codes.values():
            assert value in VALID_CODES, f"{path} has invalid code {value!r}"


def test_every_field_applies_somewhere() -> None:
    # Each attribute must be r/o/c in at least one workflow (never x everywhere).
    for path, entry in load_matrix().items():
        assert set(entry["applicability"].values()) != {"x"}, f"{path} is x everywhere"


def test_workflow_codes_view() -> None:
    aff = workflow_codes(Workflow.CLN_AFF)
    assert aff["pop_frq_points"] == "r"
    assert aff["case_proband_info.pheno_severity"] == "x"
    assert aff["additional_variants"] == "c"


def test_field_paths_are_unique() -> None:
    paths = field_paths()
    assert len(paths) == len(set(paths))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_case_applicability.py -v`
Expected: FAIL — `ModuleNotFoundError` for `svcv4_model.case_applicability`.

- [ ] **Step 3: Implement the loader**

Create `src/svcv4_model/case_applicability.py`:

```python
"""Loader for the Case applicability matrix.

The matrix (``schemas/applicability/case_applicability.yaml``) is the single
source of truth for which Case attributes are required/optional/conditional/
not-applicable per CLN workflow, plus the conditional rules. This module reads
it; it deliberately exposes no Pydantic models and is NOT exported from the
package root, so the schema exporter does not pick it up.

This phase loads and serves the matrix as data. Rule *enforcement*
(``validate_case``) is a later phase.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from svcv4_model.case import Workflow

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MATRIX_PATH = REPO_ROOT / "schemas" / "applicability" / "case_applicability.yaml"

#: Legal applicability codes (token set is {r, o, c, x}; c* has been collapsed into c).
VALID_CODES: frozenset[str] = frozenset({"r", "o", "c", "x"})


@lru_cache(maxsize=1)
def load_matrix() -> dict[str, dict[str, Any]]:
    """Load and return the applicability matrix keyed by dotted field path."""
    data = yaml.safe_load(MATRIX_PATH.read_text())
    return dict(data)


def field_paths() -> list[str]:
    """Return all dotted field paths in matrix order."""
    return list(load_matrix().keys())


def workflow_codes(workflow: Workflow) -> dict[str, str]:
    """Return ``{field_path: code}`` for a single workflow."""
    return {
        path: entry["applicability"][workflow.value]
        for path, entry in load_matrix().items()
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_case_applicability.py -v`
Expected: PASS.

- [ ] **Step 5: Format, lint, commit**

```bash
uv run ruff format .
uv run ruff check . --fix
git add src/svcv4_model/case_applicability.py tests/test_case_applicability.py
git commit -m "feat: applicability matrix loader"
```

### Task 2.4: Cross-check the matrix against the model (no orphans, no gaps)

**Files:**
- Test: `tests/test_case_applicability.py` (append)

This guards the spec's §7 "matrix shape" requirement: every matrix path exists on the model, and every model field has a matrix entry.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_case_applicability.py`:

```python
from svcv4_model.case import Case
from pydantic import BaseModel


def _model_field_paths(model: type[BaseModel], prefix: str = "") -> set[str]:
    """Enumerate dotted field paths for a Pydantic model, descending into
    nested models and into list-of-model item types (arrays do not add a
    path segment; their item fields append to the array's path)."""
    paths: set[str] = set()
    for name, field in model.model_fields.items():
        path = f"{prefix}.{name}" if prefix else name
        paths.add(path)
        annotation = field.annotation
        nested = _nested_model(annotation)
        if nested is not None:
            paths |= _model_field_paths(nested, path)
    return paths


def _nested_model(annotation: object) -> type[BaseModel] | None:
    """Return the BaseModel hiding inside `X | None`, `list[X]`, etc., or None."""
    import typing

    args = typing.get_args(annotation)
    candidates = list(args) if args else [annotation]
    for candidate in candidates:
        origin = typing.get_origin(candidate)
        if origin in (list, set, tuple):
            for inner in typing.get_args(candidate):
                model = _nested_model(inner)
                if model is not None:
                    return model
        elif isinstance(candidate, type) and issubclass(candidate, BaseModel):
            return candidate
    return None


def test_matrix_and_model_paths_match_exactly() -> None:
    model_paths = _model_field_paths(Case)
    matrix_paths = set(field_paths())
    assert matrix_paths - model_paths == set(), "matrix has paths the model lacks (orphans)"
    assert model_paths - matrix_paths == set(), "model has fields the matrix lacks (gaps)"
```

- [ ] **Step 2: Run test**

Run: `uv run pytest tests/test_case_applicability.py::test_matrix_and_model_paths_match_exactly -v`
Expected: PASS. If it fails, the assertion message names the offending paths — reconcile the matrix (Task 2.2) or the model (Tasks 1.1–1.2) until both sets are equal. (Note: the `Age` sub-fields like `case_proband_info.age.value` are NOT in the matrix because the sheet treats `age` as one attribute; this test would flag them. Resolve by treating `Age` as a *leaf value type*: exclude its internal fields from `_model_field_paths`. See Step 3.)

- [ ] **Step 3: Refine — treat `Age` and `Phenotype` internals appropriately**

`Phenotype.name`/`.code` ARE in the matrix (the sheet lists them), so `Phenotype` must be descended into. `Age` is a single sheet attribute, so its internals must NOT be enumerated. Add an explicit leaf set to `_model_field_paths`:

```python
LEAF_VALUE_MODELS = {"Age"}  # value types whose internal fields are not matrix paths


def _model_field_paths(model: type[BaseModel], prefix: str = "") -> set[str]:
    paths: set[str] = set()
    for name, field in model.model_fields.items():
        path = f"{prefix}.{name}" if prefix else name
        paths.add(path)
        nested = _nested_model(field.annotation)
        if nested is not None and nested.__name__ not in LEAF_VALUE_MODELS:
            paths |= _model_field_paths(nested, path)
    return paths
```

Re-run Step 2; expected PASS.

- [ ] **Step 4: Commit**

```bash
uv run ruff format . && uv run ruff check . --fix
git add tests/test_case_applicability.py
git commit -m "test: matrix/model path parity (no orphans, no gaps)"
```

---

## Chunk 3: Per-workflow view exporter + CI

**File structure for this chunk:**
- Create `scripts/export_case_views.py` — prunes the superset schema per workflow → `schemas/json/case/CLN_*.schema.json`, and writes the docs tables into `docs/concepts/case-model.md` between markers.
- Modify `.github/workflows/ci.yml` — run the new exporter before the drift check; widen the drift path.
- Create `tests/test_case_views.py` — exporter-in-sync + per-workflow required/excluded tests.

### Task 3.1: Implement the per-workflow exporter

**Files:**
- Create: `scripts/export_case_views.py`

The exporter dereferences the superset `Case` JSON Schema into a standalone tree, then per workflow: removes `x` fields, sets `required[]` for `r` fields, applies `enum_exclude`/`fixed` rules, and annotates `requires` conditionals.

- [ ] **Step 1: Write the exporter**

Create `scripts/export_case_views.py`:

```python
"""Generate per-workflow Case schema views and docs tables from the matrix.

For each CLN workflow this prunes the superset ``Case`` JSON Schema:
  * fields marked ``x`` (not applicable) are removed,
  * fields marked ``r`` (required) are added to the object's ``required`` list,
  * ``enum_exclude`` rules drop a token from a field's enum,
  * ``fixed`` rules pin a field to a ``const``,
  * ``requires`` rules are recorded as an informational ``x-svcv4-conditional``
    annotation (NOT enforced this phase).

Outputs:
  * schemas/json/case/CLN_*.schema.json
  * the applicability tables inside docs/concepts/case-model.md (between the
    GENERATED markers)

Run from the repo root:  uv run python scripts/export_case_views.py
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from svcv4_model.case import Case, Workflow
from svcv4_model.case_applicability import load_matrix

REPO_ROOT = Path(__file__).resolve().parent.parent
CASE_SCHEMA_DIR = REPO_ROOT / "schemas" / "json" / "case"
DOCS_PAGE = REPO_ROOT / "docs" / "concepts" / "case-model.md"
GEN_BEGIN = "<!-- BEGIN GENERATED: applicability tables -->"
GEN_END = "<!-- END GENERATED: applicability tables -->"


def _flatten(node: Any) -> Any:
    """Collapse Pydantic v2 wrappers so leaf/object schemas are exposed directly.

    Pydantic v2 emits ``X | None`` as ``{"anyOf": [<X>, {"type": "null"}], ...}``
    and sometimes a single-``$ref`` field as ``{"allOf": [<X>], ...}``. We rewrite
    both to ``<X>`` (carrying over sibling keys like ``default``/``description``)
    so that nested objects expose ``properties`` and enum fields expose ``enum``
    at the top level — which is what ``_object_at``/``_apply_rule`` expect. Must
    run AFTER ``$ref`` inlining so the branch contents are concrete.
    """
    if isinstance(node, dict):
        for key in ("anyOf", "oneOf", "allOf"):
            if key in node and isinstance(node[key], list):
                branches = node[key]
                non_null = [b for b in branches if not (isinstance(b, dict) and b.get("type") == "null")]
                # Collapse {<X>, null} unions and single-branch allOf/anyOf wrappers,
                # but leave genuine multi-member unions (2+ non-null branches) intact.
                if len(non_null) == 1:
                    merged = dict(non_null[0])
                    for k, v in node.items():
                        if k != key:
                            merged.setdefault(k, v)
                    return _flatten(merged)
        return {k: _flatten(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_flatten(item) for item in node]
    return node


def _deref(schema: dict[str, Any]) -> dict[str, Any]:
    """Inline all ``$ref`` references, drop ``$defs``, then flatten wrappers.

    The Case models form a finite (non-recursive) tree, so naive inlining
    terminates.
    """
    defs = schema.get("$defs", {})

    def resolve(node: Any) -> Any:
        if isinstance(node, dict):
            if "$ref" in node:
                ref = node["$ref"].rsplit("/", 1)[-1]
                merged = {k: v for k, v in node.items() if k != "$ref"}
                target = copy.deepcopy(defs[ref])
                target.update(merged)
                return resolve(target)
            return {k: resolve(v) for k, v in node.items()}
        if isinstance(node, list):
            return [resolve(item) for item in node]
        return node

    root = {k: v for k, v in schema.items() if k != "$defs"}
    return _flatten(resolve(root))


def _object_at(node: dict[str, Any]) -> dict[str, Any] | None:
    """Return the object-with-properties node, descending through array ``items``."""
    if node.get("type") == "array" and isinstance(node.get("items"), dict):
        return _object_at(node["items"])
    if "properties" in node:
        return node
    return None


def _prune(node: dict[str, Any], path: str, codes: dict[str, str], rules: dict[str, dict]) -> None:
    """Recursively prune one object node in place for a single workflow."""
    obj = _object_at(node)
    if obj is None:
        return
    required: list[str] = []
    for name in list(obj["properties"].keys()):
        child_path = f"{path}.{name}" if path else name
        code = codes.get(child_path)
        prop = obj["properties"][name]
        if code == "x":
            del obj["properties"][name]
            continue
        _apply_rule(prop, child_path, rules)
        if code == "r":
            required.append(name)
        _prune(prop, child_path, codes, rules)
    if required:
        obj["required"] = required
    else:
        obj.pop("required", None)


def _apply_rule(prop: dict[str, Any], path: str, rules: dict[str, dict]) -> None:
    rule = rules.get(path)
    if not rule:
        return
    effect = rule.get("effect")
    target = _object_at(prop) or prop
    if effect == "enum_exclude" and "enum" in target:
        target["enum"] = [v for v in target["enum"] if v != rule["value"]]
    elif effect == "fixed":
        target.pop("enum", None)
        target["const"] = rule["value"]
    elif "requires" in rule:
        prop["x-svcv4-conditional"] = rule["requires"]


def build_workflow_schema(workflow: Workflow) -> dict[str, Any]:
    base = _deref(Case.model_json_schema())
    matrix = load_matrix()
    codes = {p: e["applicability"][workflow.value] for p, e in matrix.items()}
    rules = {p: e["rule"] for p, e in matrix.items() if "rule" in e}
    _prune(base, "", codes, rules)
    base["title"] = f"Case ({workflow.value})"
    base["$comment"] = (
        f"Derived view of the Case superset for the {workflow.value} workflow. "
        "Generated by scripts/export_case_views.py; do not edit by hand."
    )
    return base


def _table(workflow: Workflow) -> str:
    matrix = load_matrix()
    lines = [
        f"#### {workflow.value}",
        "",
        "| Attribute | Code | Value | Notes |",
        "|-----------|------|-------|-------|",
    ]
    for path, entry in matrix.items():
        code = entry["applicability"][workflow.value]
        value = str(entry.get("value", "")).replace("|", "\\|")
        notes = str(entry.get("notes", "")).replace("|", "\\|")
        lines.append(f"| `{path}` | {code} | {value} | {notes} |")
    return "\n".join(lines)


def write_docs_tables() -> None:
    body = "\n\n".join(_table(w) for w in Workflow)
    text = DOCS_PAGE.read_text()
    pre, _, rest = text.partition(GEN_BEGIN)
    _, _, post = rest.partition(GEN_END)
    new = f"{pre}{GEN_BEGIN}\n\n{body}\n\n{GEN_END}{post}"
    DOCS_PAGE.write_text(new)


def main() -> None:
    CASE_SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for workflow in Workflow:
        schema = build_workflow_schema(workflow)
        path = CASE_SCHEMA_DIR / f"{workflow.value}.schema.json"
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
        print(f"  - {path.relative_to(REPO_ROOT).as_posix()}")
    if DOCS_PAGE.exists():
        write_docs_tables()
        print(f"  - updated {DOCS_PAGE.relative_to(REPO_ROOT).as_posix()} (generated tables)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it (docs page may not exist yet — that's fine)**

Run: `uv run python scripts/export_case_views.py`
Expected: prints five `schemas/json/case/CLN_*.schema.json` paths. (The docs update is skipped until Chunk 4 creates the page.)

- [ ] **Step 3: Spot-check one derived schema**

Run: `uv run python -c "import json; s=json.load(open('schemas/json/case/CLN_DNV.schema.json')); print('compound_het_variant' in s['properties'], s.get('required'))"`
Expected: `False [...]` — `compound_het_variant` is removed for DNV (it is `x` there), and `required` lists DNV's `r` fields (e.g. `moi`, `pop_frq_points`, `case_proband_info`, `vbc`).

- [ ] **Step 4: Commit**

```bash
uv run ruff format . && uv run ruff check . --fix
git add scripts/export_case_views.py schemas/json/case
git commit -m "feat: per-workflow Case schema view exporter"
```

### Task 3.2: Test the exporter output (in sync + per-workflow facts)

**Files:**
- Create: `tests/test_case_views.py`

- [ ] **Step 1: Write the tests**

Create `tests/test_case_views.py`:

```python
"""Tests for the per-workflow Case schema views."""

from __future__ import annotations

import json
from pathlib import Path

from svcv4_model.case import Workflow
from svcv4_model.case_applicability import load_matrix

import scripts.export_case_views as exporter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CASE_SCHEMA_DIR = REPO_ROOT / "schemas" / "json" / "case"


def test_each_workflow_schema_exists() -> None:
    for workflow in Workflow:
        assert (CASE_SCHEMA_DIR / f"{workflow.value}.schema.json").exists()


def test_committed_schemas_match_generated() -> None:
    """Mirrors CI: regenerating must not change the committed per-workflow schemas."""
    for workflow in Workflow:
        committed = json.loads((CASE_SCHEMA_DIR / f"{workflow.value}.schema.json").read_text())
        generated = exporter.build_workflow_schema(workflow)
        assert committed == generated, f"{workflow.value} schema is stale; re-run the exporter"


def test_not_applicable_fields_are_removed() -> None:
    dnv = json.loads((CASE_SCHEMA_DIR / "CLN_DNV.schema.json").read_text())
    assert "compound_het_variant" not in dnv["properties"]
    assert "additional_variants" not in dnv["properties"]


def test_required_matches_matrix_top_level() -> None:
    matrix = load_matrix()
    for workflow in Workflow:
        schema = json.loads((CASE_SCHEMA_DIR / f"{workflow.value}.schema.json").read_text())
        expected = {
            path
            for path, entry in matrix.items()
            if "." not in path and entry["applicability"][workflow.value] == "r"
        }
        assert set(schema.get("required", [])) == expected, workflow.value


def test_fixed_rule_becomes_const() -> None:
    aff = json.loads((CASE_SCHEMA_DIR / "CLN_AFF.schema.json").read_text())
    che = aff["properties"]["compound_het_variant"]["properties"]
    assert che["zygosity"]["const"] == "HET"
    assert che["phase_in_ref_to_vbc"]["const"] == "TRANS"


def test_enum_exclude_drops_token_for_altg() -> None:
    altg = json.loads((CASE_SCHEMA_DIR / "CLN_ALTG.schema.json").read_text())
    severity = altg["properties"]["case_proband_info"]["properties"]["pheno_severity"]
    assert "BIALLELIC_LT_EXPECTED" not in severity["enum"]
```

- [ ] **Step 2: Run tests**

Run: `uv run pytest tests/test_case_views.py -v`
Expected: PASS. If `test_required_matches_matrix_top_level` fails, re-run `uv run python scripts/export_case_views.py` and commit the regenerated files.

> If importing `scripts.export_case_views` fails with `ModuleNotFoundError: scripts`, add an empty `scripts/__init__.py` (`git add` it) so the package is importable in tests, OR load it via `importlib.util` from its path. Prefer the `scripts/__init__.py` route for simplicity; confirm `ruff`/packaging config does not ship `scripts` as a wheel (it is dev-only; the existing `pyproject.toml` packages `src/` only).

- [ ] **Step 3: Commit**

```bash
git add tests/test_case_views.py scripts/__init__.py 2>/dev/null; git add tests/test_case_views.py
git commit -m "test: per-workflow Case schema views (in-sync + rule effects)"
```

### Task 3.3: Wire the exporter into CI

**Files:**
- Modify: `.github/workflows/ci.yml:46-53`

- [ ] **Step 1: Update the drift step**

Replace the "Export schemas and check no drift" step body so it runs BOTH exporters and widens the diff path to include the per-workflow schemas and the generated docs region:

```yaml
      - name: Export schemas and check no drift
        run: |
          uv run python scripts/export_schemas.py
          uv run python scripts/export_case_views.py
          if ! git diff --quiet -- schemas/json docs/concepts/case-model.md; then
            echo "::error::Generated schemas/docs are out of date. Run scripts/export_schemas.py and scripts/export_case_views.py and commit the result."
            git diff -- schemas/json docs/concepts/case-model.md
            exit 1
          fi
```

- [ ] **Step 2: Locally simulate the CI check**

```bash
uv run python scripts/export_schemas.py
uv run python scripts/export_case_views.py
git diff --quiet -- schemas/json docs/concepts/case-model.md && echo "CLEAN" || (echo "DRIFT"; git diff --stat -- schemas/json docs/concepts/case-model.md)
```
Expected: `CLEAN` (assuming everything generated so far is committed; the docs file may not exist until Chunk 4 — if so, `git diff` ignores the missing path and this still prints CLEAN).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: run export_case_views.py and guard per-workflow schema/docs drift"
```

---

## Chunk 4: Documentation

**File structure for this chunk:**
- Create `docs/concepts/case-model.md` — narrative + the GENERATED markers the exporter fills.
- Modify `mkdocs.yml` — add the page under the `Concepts` nav group.
- Modify `docs/model/index.md` — add a `::: svcv4_model.Case` stanza.

### Task 4.1: Create the docs page and generate its tables

**Files:**
- Create: `docs/concepts/case-model.md`
- Modify: `mkdocs.yml:66-71` (the `Concepts` list)
- Modify: `docs/model/index.md`

- [ ] **Step 1: Write the narrative page with generation markers**

Create `docs/concepts/case-model.md`:

```markdown
# Case model

A **Case** is the case-level payload a curator captures from the literature to
represent a single human clinical (CLN) observation supporting (or opposing)
variant pathogenicity. It is the structured `data` behind a
`clinical_observation` Evidence Item.

The model is a permissive **superset**: every attribute is optional on the type.
Which attributes are required (`r`), optional (`o`), conditional (`c`), or not
applicable (`x`) depends on the CLN workflow — `CLN_AFF` (Affected), `CLN_DNV`
(De Novo), `CLN_ALTV` (Alternative Variant), `CLN_ALTG` (Alternative Gene), and
`CLN_UAF` (Unaffected). `CLN_ALTV` + `CLN_ALTG` generalize to `CLN_ALT`.

Applicability and the conditional rules live in a single source of truth,
`schemas/applicability/case_applicability.yaml`. The per-workflow JSON Schemas
under `schemas/json/case/` and the tables below are generated from it; this
phase documents the conditional rules but does not enforce them.

See the [`Case` model reference][svcv4_model.Case] for field types. (This uses
mkdocstrings' autorefs cross-reference form, which resolves to the generated
anchor regardless of slug — more robust than a hand-written `#anchor`.)

## Applicability by workflow

<!-- BEGIN GENERATED: applicability tables -->
<!-- END GENERATED: applicability tables -->
```

- [ ] **Step 2: Generate the tables**

Run: `uv run python scripts/export_case_views.py`
Expected: prints the five schema paths plus "updated docs/concepts/case-model.md". Open the file and confirm five `#### CLN_*` tables now sit between the markers.

- [ ] **Step 3: Add to nav and model reference**

In `mkdocs.yml`, under `Concepts:` add the page. The existing Concepts list is
ordered conceptually (not alphabetically); place `Case model` deliberately —
after "Evidence Lines & Items" and before "Summary Table" reads well, since a
Case is the content of a clinical-observation Evidence Item:

```yaml
      - Case model: concepts/case-model.md
```

In `docs/model/index.md`, append:

```markdown

---

::: svcv4_model.Case
```

- [ ] **Step 4: Build the docs to verify no warnings**

Run: `uv sync --group docs --group dev && uv run mkdocs build --strict`
Expected: builds with no errors. (This mirrors `.github/workflows/docs.yml`; `mkdocs`/`mkdocs-material`/`mkdocstrings[python]` live in the `docs` dependency group, not `dev`, so they must be synced first.) If `--strict` flags the cross-reference, confirm the autorefs link `[\`Case\` model reference][svcv4_model.Case]` is used (Step 1) rather than a hand-written anchor.

- [ ] **Step 5: Commit**

```bash
git add docs/concepts/case-model.md mkdocs.yml docs/model/index.md
git commit -m "docs: Case model concept page + nav + model reference stanza"
```

### Task 4.2: Final full-suite verification + push

**Files:** none (verification only)

- [ ] **Step 1: Run the whole gate locally**

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/export_schemas.py
uv run python scripts/export_case_views.py
git diff --quiet -- schemas/json docs/concepts/case-model.md && echo "NO DRIFT" || echo "DRIFT — commit regenerated files"
uv run python scripts/validate_examples.py
```
Expected: ruff clean, all tests pass, `NO DRIFT`, examples validate.

- [ ] **Step 2: Push and confirm PR #17 is green**

```bash
git push origin feat/case-model
gh pr checks 17 --watch
```
Expected: all CI checks pass on PR #17.

- [ ] **Step 3: Hand back to the user**

Summarize what shipped (superset model, matrix, five per-workflow schemas, docs) and ask the user to review PR #17 before merge.

---

## Notes & references

- Spec: `docs/superpowers/specs/2026-06-11-case-model-design.md`
- Existing patterns followed: `scripts/export_schemas.py` (auto-discovery via `__all__`), `tests/test_model.py` (round-trip + forbid-extra style), `.github/workflows/ci.yml` (drift gate).
- Deferred by design (do NOT implement here): `validate_case` rule enforcement, case aggregation/counting, SVCv4 point mapping, worked example cases, tightening `classification`/`phase_confidence` to VA-Spec profile types.
- @superpowers:test-driven-development — every task is test-first.
- @superpowers:verification-before-completion — Task 4.2 must show green output before claiming done.
