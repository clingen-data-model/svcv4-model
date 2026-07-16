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
    """The evidence-assessment workflows.

    Five clinical (``CLN_*``) workflows plus two locus-based (``LOC_*``)
    workflows. ``CLN_ALTV`` and ``CLN_ALTG`` generalize to ``CLN_ALT``; they
    are kept separate here because their applicability rules diverge.
    """

    CLN_AFF = "CLN_AFF"
    CLN_DNV = "CLN_DNV"
    CLN_ALTV = "CLN_ALTV"
    CLN_ALTG = "CLN_ALTG"
    CLN_UAF = "CLN_UAF"
    LOC_PHE = "LOC_PHE"
    LOC_SEG = "LOC_SEG"


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


class CaseTesting(BaseModel):
    """Genetic testing performed for the proband/case."""

    model_config = ConfigDict(extra="forbid")

    method: str | None = Field(
        default=None,
        description="Test method(s), e.g. Sanger, Exome, Genome, Cyto; CSV allowed for multiple.",
    )
    diagnostic_yield_for_phenotypes: str | None = Field(
        default=None,
        description=(
            "Diagnostic yield for the phenotype(s), e.g. `100%`, `50%`. Supporting "
            "evidence is captured as notes only this phase, not as structured values."
        ),
    )
    covers_all_genes_relevant_to_mde: TriState | None = Field(
        default=None,
        description="Whether the test covered all genes relevant to the MDE.",
    )


class CaseRelative(BaseModel):
    """A relative of the proband, captured for segregation (LOC_SEG)."""

    model_config = ConfigDict(extra="forbid")

    parent_of_proband: TriState | None = Field(
        default=None, description="Whether this relative is a parent of the proband."
    )
    sex: Sex | None = Field(default=None, description="Relative sex; required if X-linked.")
    age: Age | None = Field(default=None)
    phenotypes: list[Phenotype] = Field(
        default_factory=list, description="0..many phenotypes for the relative."
    )
    affected_w_mde: TriState | None = Field(
        default=None, description="Whether the relative is affected with the MDE."
    )
    severe_phenotype: TriState | None = Field(
        default=None,
        description=(
            "Whether the relative has a severe phenotype. Required for semi-dominant "
            "and X-linked when affected. Distinct from `pheno_severity`."
        ),
    )
    vbc_exists: TriState | None = Field(
        default=None, description="Whether the VBC is present in the relative."
    )
    vbc_zygosity: Zygosity | None = Field(
        default=None, description="Zygosity of the VBC in the relative."
    )
    cmp_het_variant_exists: TriState | None = Field(
        default=None, description="Whether a compound-het variant exists in the relative."
    )


class Gene(BaseModel):
    """A gene reference (symbol/id/transcript); ``mde_associated_gene`` flags
    whether it is the MDE-associated gene (set when it differs from the VBC gene).
    """

    model_config = ConfigDict(extra="forbid")

    symbol: str | None = Field(default=None, description="Gene symbol.")
    id: str | None = Field(default=None, description="Gene identifier (e.g. HGNC / NCBI id).")
    mde_associated_gene: str | None = Field(
        default=None,
        description="MDE-associated gene, required when the gene differs from the VBC gene.",
    )
    transcript: str | None = Field(
        default=None, description="Transcript reference (e.g. RefSeq accession)."
    )


class Vbc(BaseModel):
    """Variant Being Considered — the curation-level reference to the variant
    under evaluation, shared across workflows as a parameter (id + gene).

    Curation-level counterpart to the formal VA-Spec ``inputs.VBC``; the two
    reconcile in a later phase.
    """

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None, description="Identifier for the variant being considered.")
    gene: Gene | None = Field(default=None, description="The gene the VBC is in.")


class Mde(BaseModel):
    """Mendelian Disease Entity — the curation-level disease reference the VBC is
    assessed against, shared across workflows as a parameter.

    Curation-level counterpart to the formal VA-Spec ``inputs.MDE``.
    """

    model_config = ConfigDict(extra="forbid")

    curie: str | None = Field(
        default=None, description="Disease CURIE (e.g. `MONDO:0007254`, `OMIM:114480`)."
    )
    label: str | None = Field(default=None, description="Human-readable disease label.")


class CompoundHetVariant(BaseModel):
    """The second variant in a biallelic evaluation against a het VBC.

    Included only when ``vbc_zygosity`` is ``HET`` and there is another variant
    in the same gene that is also HET and in *trans*. Because those conditions
    are the inclusion criteria, zygosity (HET) and phase (TRANS) are implied and
    are not captured here.
    """

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(default=None)
    phase_confidence: PhaseConfidence | None = Field(
        default=None, description="Confidence that the variant is in trans with the VBC."
    )
    classification: str | None = Field(
        default=None, description="Variant classification (placeholder string this phase)."
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
    """The case data structure: a reusable, permissive superset of the case-level
    information a curator captures for a single human observation.

    A ``Case`` is shared across the workflows that consume case information to
    determine applicability and score human-observation evidence. Every field is
    optional here; which fields are required/optional/conditional/not-applicable
    per workflow is expressed by the applicability matrix, not by this type.

    ``moi`` and ``pop_frq_points`` are **not** part of the Case — they are
    workflow parameters (see :class:`WorkflowParameters`).
    """

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(
        default=None, description="Proband identifier, used to match individuals across workflows."
    )
    family_id: str | None = Field(
        default=None, description="Family identifier, used to match relatives across workflows."
    )
    sex: Sex | None = Field(default=None)
    age: Age | None = Field(default=None)
    phenotypes: list[Phenotype] = Field(
        default_factory=list,
        description="0..many phenotypes; capture at least what is relevant to the case.",
    )
    pheno_specificity_for_mde: PhenoSpecificity | None = Field(
        default=None,
        description="How closely the phenotype(s) match what is expected for the MDE.",
    )
    gene_specificity_for_phenotypes: str | None = Field(
        default=None,
        description=(
            "How specific the phenotype(s) are to the gene, e.g. `100%`, `50%` "
            "(roughly the inverse of the number of genes causing the phenotype(s))."
        ),
    )
    testing: CaseTesting | None = Field(default=None)
    pheno_severity: PhenoSeverity | None = Field(default=None)
    age_matched_penetrance: AgeMatchedPenetrance | None = Field(default=None)
    confirmed_parental_relationship: TriState | None = Field(
        default=None, description="Whether the parental relationship was confirmed."
    )
    vbc_exists: TriState | None = Field(
        default=None, description="Whether the VBC is present in the proband."
    )
    vbc_zygosity: Zygosity | None = Field(
        default=None, description="Zygosity of the VBC in the proband."
    )
    compound_het_variant: CompoundHetVariant | None = Field(default=None)
    additional_variant_exists: TriState | None = Field(
        default=None, description="Whether an additional variant exists in the case."
    )
    additional_variants: list[AdditionalVariant] = Field(
        default_factory=list,
        description="Additional variant(s); populated only if `additional_variant_exists` is TRUE.",
    )
    relatives: list[CaseRelative] = Field(
        default_factory=list,
        description="0..many relatives; captured singularly or in bulk for segregation.",
    )


class WorkflowParameters(BaseModel):
    """Parameters required by the workflows but not part of the Case data
    structure. These feed the (forthcoming) workflow matrix that determines
    applicability and scoring; they are captured alongside a Case, not within it.
    """

    model_config = ConfigDict(extra="forbid")

    vbc: Vbc | None = Field(default=None, description="The variant being considered.")
    mde: Mde | None = Field(default=None, description="The disease the VBC is assessed against.")
    moi: MOI | None = Field(default=None, description="Mode of inheritance.")
    pop_frq_points: float | None = Field(
        default=None, ge=-1.0, description="Population-frequency points (must be >= -1.0)."
    )
