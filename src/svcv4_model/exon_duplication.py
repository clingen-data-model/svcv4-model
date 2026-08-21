"""SVCv4 Single/Multi-Exon Duplication/Gain variants workflow (SM 14).

Duplications/gains of one or more exons (up to but excluding a whole gene) resolve to a
NUL_ or CDS_ parent code via one of six scored branches (plus a documented whole-gene NA
outcome) selected by a decision tree over three axes: molecularly proven tandem vs an
unproven copy-number gain, NMD predicted, and whether a terminal (first/last) exon/UTR is
included. Tandem-proven variants accrue more points than gains (only ~80% of subgenic
gains are actually tandem). The scored branches run the shared pipeline — predictive (PRD)
adjusted by the SM 18 mechanism/exon matrix, functional (FXN, SM 20; not considered on the
gain paths), informative (INF, SM 19), parent total. This module captures the analyst's
inputs; the scoring is documented, not computed.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from svcv4_model.functional import FunctionalAssayEvidence
from svcv4_model.informative import InformativeVariantsEvidence
from svcv4_model.mechanism import MechanismExonRelevanceEvidence
from svcv4_model.pfd import PfdParentCode


class ExonDuplicationOutcome(StrEnum):
    """Which of the six scored duplication/gain branches (or whole-gene NA) applies (SM 14)."""

    TANDEM_NMD = "TANDEM_NMD"
    TANDEM_NO_NMD = "TANDEM_NO_NMD"
    TANDEM_TERMINAL_EXON = "TANDEM_TERMINAL_EXON"
    GAIN_NMD = "GAIN_NMD"
    GAIN_NO_NMD = "GAIN_NO_NMD"
    GAIN_TERMINAL_EXON = "GAIN_TERMINAL_EXON"
    WHOLE_GENE_NA = "WHOLE_GENE_NA"


class ExonDuplicationPredictiveEvidence(BaseModel):
    """The duplication/gain predictive (PRD) step of a branch (SM 14).

    Tandem NMD starts at +6.0; gain NMD at +4.0; the tandem/gain no-NMD branches derive
    initial points from the fraction of ORF duplicated (upper orange) or protein disrupted
    (violet) or the criticality of the duplicated amino acids; the terminal-exon branches
    award no initial points (SM 18 not applicable). Positive points are reduced by the
    SM 18 matrix on the branches that award them.
    """

    model_config = ConfigDict(extra="forbid")

    basis: str | None = Field(
        default=None,
        description="Predictive basis (e.g. tandem NMD; % ORF duplicated; critical domain).",
    )
    initial_points: float | None = Field(
        default=None, description="Initial PRD points before the SM 18 adjustment."
    )
    molecularly_tandem: bool | None = Field(
        default=None,
        description="VBC molecularly proven tandem (vs an unproven copy-number gain).",
    )
    nmd_predicted: bool | None = Field(
        default=None,
        description="Introduced PTC >50 bp upstream of the last exon-intron boundary predicts NMD.",
    )
    includes_terminal_exon_or_utr: bool | None = Field(
        default=None,
        description="Duplication includes the first exon, last exon, or either UTR.",
    )
    orf_fraction_duplicated: float | None = Field(
        default=None,
        description="Fraction of ORF duplicated / protein disrupted (the >50%..<10% table).",
    )
    duplicated_domain_critical: bool | None = Field(
        default=None,
        description="Duplicated amino acids alter a proven critical disease-relevant domain.",
    )
    adjusted_points: float | None = Field(
        default=None, description="Coded PRD points after the SM 18 adjustment."
    )


class ExonDuplicationAssessment(BaseModel):
    """A single/multi-exon duplication/gain (NUL_/CDS_) assessment (SM 14).

    One entity for all six scored branches plus the whole-gene NA outcome, parameterized by
    ``prediction_outcome``; reuses the SM 18/19/20 submodules and the shared ``PfdParentCode``
    (NUL/CDS). Permissive superset; the per-branch pipeline and its caps are documented, not
    computed. ``functional`` is left unset on the gain paths (blue/violet/green), where SM 14
    codes functional data as NA.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_outcome: ExonDuplicationOutcome | None = Field(
        default=None, description="Which of the six scored branches (or whole-gene NA) applies."
    )
    parent_code: PfdParentCode | None = Field(
        default=None, description="The resolved parent code (NUL or CDS per branch)."
    )
    predictive: ExonDuplicationPredictiveEvidence | None = Field(
        default=None, description="The PRD predictive step."
    )
    mechanism_exon_relevance: MechanismExonRelevanceEvidence | None = Field(
        default=None, description="SM 18 molecular-mechanism & exon-relevance inputs."
    )
    functional: FunctionalAssayEvidence | None = Field(
        default=None, description="SM 20 functional-assay evidence (FXN); NA on the gain paths."
    )
    informative: InformativeVariantsEvidence | None = Field(
        default=None, description="SM 19 informative-variants evidence (INF)."
    )
    prd_points: float | None = Field(default=None, description="Coded PRD point value.")
    fxn_points: float | None = Field(default=None, description="Coded FXN point value.")
    inf_points: float | None = Field(default=None, description="Coded INF point value.")
    prd_fxn_combined: float | None = Field(
        default=None, description="Held PRD + FXN combined value (no distinct code)."
    )
    parent_total: float | None = Field(
        default=None, description="Capped parent-code total for this branch."
    )
