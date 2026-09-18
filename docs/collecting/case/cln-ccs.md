# Case-control (CLN_CCS)

**CLN_CCS** is the one member of this family that is **not a per-proband `Case`.**
It collects a **variant-specific case-control study** — a single study-level
result comparing the VBC's frequency in phenotyped cases against controls — so its
evidence lives in a standalone payload, not in the Case superset. It is kept here,
in the Part-3 sequence, because it belongs to the same "case & segregation"
family; the distinction is the point.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../reference/glossary.md)).

## What is collected

A single `CaseControlStudyEvidence` payload:

- **`odds_ratio`** with **`ci_lower`** / **`ci_upper`** — the VBC's enrichment in
  cases vs. controls, and the confidence interval around it.
- **`case_cohort_size`** (SM 4 recommends ≥ 100 unrelated cases),
  **`case_variant_count`** (≥ 5 observations of the VBC in cases), and
  **`control_cohort_size`**.
- **`controls_matched`** and **`ascertainment_bias_considered`** — the robustness
  flags SM 4 requires for the study to count.

## Why it stands apart

It is a **study-level datum, not a `Case`** — the same reason
[`PopulationEvidence`](../population.md) is standalone. It also carries an
**exclusivity rule**: when `CLN_CCS` is applied (scored, regardless of the point
value), all other CLN codes become **not applicable except `CLN_DNV`** (SM 4 L25).
Scoring — `OR > 5.0` → `CLN_CCS_+4.0`, a CI including 1.0 → no points, `OR ≤ 1.0`
→ benignity — is documented, not computed here.

## Reference

- Inputs catalog: evidence data structures.
- Scoring and exclusivity: the `CLN_CCS` note on
  [Clinical Observations (CLN)](../../workflows/hod/cln/index.md).
