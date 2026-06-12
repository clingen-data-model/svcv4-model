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

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Workflow(StrEnum):
    """The five CLN evidence-assessment workflows.

    ``CLN_ALTV`` and ``CLN_ALTG`` generalize to ``CLN_ALT``; they are kept
    separate here because their applicability rules diverge.
    """

    CLN_AFF = "CLN_AFF"
    CLN_DNV = "CLN_DNV"
    CLN_ALTV = "CLN_ALTV"
    CLN_ALTG = "CLN_ALTG"
    CLN_UAF = "CLN_UAF"


class MOI(StrEnum):
    """Mode of inheritance. ALTV does not yet support AR/XLR."""

    AD = "AD"
    AR = "AR"
    XLD = "XLD"
    XLR = "XLR"
    SD = "SD"


class Sex(StrEnum):
    """Proband sex: Male / Female / Unknown / Trans."""

    M = "M"
    F = "F"
    U = "U"
    T = "T"


class PhenoSpecificity(StrEnum):
    """Phenotype specificity for the gene."""

    SPECIFIC = "SPECIFIC"
    CONSISTENT = "CONSISTENT"
    INCONSISTENT = "INCONSISTENT"


class PhenoSeverity(StrEnum):
    """Phenotype severity relative to expectation.

    ``BIALLELIC_LT_EXPECTED`` is not applicable to the ALT Gene workflow
    (see the applicability matrix's ``enum_exclude`` rule).
    """

    MONO_GT_OR_BIALLELIC_EQ_EXPECTED = "MONO_GT_OR_BIALLELIC_EQ_EXPECTED"
    MONO_EQ_EXPECTED = "MONO_EQ_EXPECTED"
    BIALLELIC_LT_EXPECTED = "BIALLELIC_LT_EXPECTED"


class AgeMatchedPenetrance(StrEnum):
    """Age-matched penetrance bands."""

    LT_80 = "LT_80"
    PCT_80_100 = "PCT_80_100"
    NEAR_100 = "NEAR_100"


class Zygosity(StrEnum):
    """Zygosity of a variant in the case."""

    HOM = "HOM"
    HET = "HET"
    HEMI = "HEMI"


class Phase(StrEnum):
    """Phase of a variant in reference to the VBC."""

    TRANS = "TRANS"
    CIS = "CIS"
    UNKNOWN = "UNKNOWN"


class PhaseConfidence(StrEnum):
    """Confidence in a phase determination."""

    HIGH = "HIGH"
    MED = "MED"
    LOW = "LOW"


class AgeUnit(StrEnum):
    """Unit for an :class:`Age` value or bounds."""

    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class AgeQualifier(StrEnum):
    """How to read an :class:`Age`: a point value, a bound, or a range."""

    EXACT = "EXACT"
    GT = "GT"
    LT = "LT"
    APPROX = "APPROX"
    RANGE = "RANGE"


class TriState(StrEnum):
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

    id: str | None = Field(default=None, description="Identifier for the variant being considered.")
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
    phase_confidence: PhaseConfidence | None = Field(
        default=None, description="Confidence in the phase call."
    )
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
    phase_confidence: PhaseConfidence | None = Field(
        default=None, description="Captured only if phase is captured (HIGH / MED / LOW)."
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
    vbc: CaseVariant | None = Field(default=None, description="The variant being considered.")
    compound_het_variant: CompoundHetVariant | None = Field(default=None)
    additional_variant_exists: TriState | None = Field(
        default=None, description="Whether an additional variant exists in the case."
    )
    additional_variants: list[AdditionalVariant] = Field(
        default_factory=list,
        description="Additional variant(s); populated only if `additional_variant_exists` is TRUE.",
    )
