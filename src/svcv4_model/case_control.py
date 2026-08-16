"""SVCv4 CLN_CCS evidence — the payload behind a case_control Evidence Item.

A variant-specific case-control study result: the odds ratio of the VBC's
frequency in phenotyped cases vs controls, plus the cohort sizes and robustness
attributes SVCv4 (Supplementary Material 4) requires. A study-level datum,
distinct from the per-proband ``Case`` observations — so it is a standalone
curation-level payload like ``PopulationEvidence``, not part of ``Case``.

Scoring (see docs/workflows/hod/cln/index.md) is documented, not computed.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CaseControlStudyEvidence(BaseModel):
    """CLN_CCS case-control study inputs for a VBC.

    Permissive superset (every field optional). Captured; the scoring
    (OR > 5.0 → +4.0; CI including 1.0 → no points; OR ≤ 1.0 → benignity) and
    the exclusivity rule (other CLN codes NA except CLN_DNV) are documented,
    not computed.
    """

    model_config = ConfigDict(extra="forbid")

    odds_ratio: float | None = Field(
        default=None, description="Odds ratio for the VBC's enrichment in cases vs controls."
    )
    ci_lower: float | None = Field(
        default=None, description="Lower bound of the confidence interval around the OR."
    )
    ci_upper: float | None = Field(
        default=None, description="Upper bound of the confidence interval around the OR."
    )
    case_cohort_size: int | None = Field(
        default=None,
        description="Number of unrelated cases in the cohort (SM 4 recommends >= 100).",
    )
    case_variant_count: int | None = Field(
        default=None,
        description="Observations of the VBC in the case cohort (SM 4 recommends >= 5).",
    )
    control_cohort_size: int | None = Field(
        default=None, description="Number of individuals in the control cohort."
    )
    controls_matched: bool | None = Field(
        default=None,
        description=(
            "Whether cases and controls were matched (ancestry, sequencing platform, QC) per SM 4."
        ),
    )
    ascertainment_bias_considered: bool | None = Field(
        default=None,
        description="Whether ascertainment bias was considered (SM 4).",
    )
