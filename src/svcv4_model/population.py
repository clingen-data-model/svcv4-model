"""SVCv4 Population (POP) evidence — the payload behind a population_frequency
Evidence Item: population-database frequency evidence about the variant.

Covers the two POP evidence codes, both benignity-only:

- ``POP_FRQ``: the variant's Filtering Allele Frequency (FAF) vs the MDE's
  Disease Allele Frequency Threshold (DAFT).
- ``POP_HMZ``: homozygous/hemizygous occurrences in an unselected population
  database.

Curation-level counterpart to the formal VA-Spec Cohort Allele Frequency Study
Result; the two reconcile in a later phase. Like ``Case``, every field is
optional; scoring (see ``docs/workflows/hod/pop.md``) is documented, not
computed here.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.case import TriState


class DaftMethod(StrEnum):
    """How the Disease Allele Frequency Threshold was derived (SM 3).

    ``VCEP_CURATED`` is the preferred source (an expert-consensus threshold);
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
        default=None,
        description="Expected penetrance (0-1); use the lowest reasonable estimate.",
    )
    locus_heterogeneity: float | None = Field(
        default=None,
        description="Fraction of cases attributable to this locus (0-1).",
    )
    allelic_heterogeneity: float | None = Field(
        default=None,
        description="Fraction of disease alleles this variant could represent (0-1).",
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
        default=None,
        description="Number of hemizygous occurrences (X-linked) of the VBC.",
    )
    hmz_eligible: TriState | None = Field(
        default=None,
        description=(
            "Whether the MDE's penetrance + severity make affected individuals implausible in the "
            "population database, so occurrences count as benignity evidence (SM 3, Table 7)."
        ),
    )
