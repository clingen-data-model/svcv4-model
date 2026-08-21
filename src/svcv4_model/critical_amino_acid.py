"""SVCv4 Determining Critical Amino Acids shared submodule (SM 7).

Guidance for when an analyst may add a small amount of evidence for a VBC that lies in a
critical residue or domain, on top of the in-silico predictor score (most commonly
MIS_PRD_). For critical domains, SM 7 makes no specific point recommendation (adding
evidence risks double-counting the strengthened in-silico predictors), though experienced
analysts may add robustly-supported evidence. For critical residues (e.g. the Gly-X-Y motif
glycine in collagens; Cys-Cys bridge cysteines in FBN1/NOTCH3; C2H2 zinc-finger cys/his in
GLI3), an analyst may add up to +2.0 points, only if the residue's functional role is
well-established and the PRD+INF combination has not already reached its maximum cap. This
submodule captures the analyst's inputs; the scoring is documented, not computed. SM 7 has
no parent code of its own — its points add to whichever _PRD_ applies.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class CriticalityKind(StrEnum):
    """Whether the VBC affects a critical single residue or a critical domain (SM 7)."""

    CRITICAL_RESIDUE = "CRITICAL_RESIDUE"
    CRITICAL_DOMAIN = "CRITICAL_DOMAIN"


class CriticalAminoAcidEvidence(BaseModel):
    """SM 7 critical-residue / critical-domain inputs for a PFD predictive step.

    Standalone curation-level payload (the SM 18/19/20 pattern); permissive superset. The
    up-to-+2.0 residue cap, the two gating conditions, and the +6.0-on-prediction-alone
    caution are documented, not computed. SM 7 has no parent code; the additional points
    add to whichever ``_PRD_`` applies (most commonly ``MIS_PRD_``).
    """

    model_config = ConfigDict(extra="forbid")

    criticality_kind: CriticalityKind | None = Field(
        default=None, description="Whether the VBC affects a critical residue or a critical domain."
    )
    motif_or_domain_name: str | None = Field(
        default=None,
        description="The named motif / domain / residue role (e.g. Gly-X-Y triple-helix glycine).",
    )
    function_role_established: bool | None = Field(
        default=None,
        description="The residue's/domain's involvement in protein function is well-established.",
    )
    additional_points: float | None = Field(
        default=None,
        description="Additional points on top of the in-silico score (up to +2.0 for a residue).",
    )
    max_score_not_reached: bool | None = Field(
        default=None,
        description="The _PRD_ + _INF_ combination has not already reached its maximum cap.",
    )
    observed_in_affected: bool | None = Field(
        default=None,
        description="The variant has been observed in an individual affected with the MDE.",
    )
    double_counting_considered: bool | None = Field(
        default=None,
        description="The analyst confirmed this does not double-count the in-silico predictor.",
    )
