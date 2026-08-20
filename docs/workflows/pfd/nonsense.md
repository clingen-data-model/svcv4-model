# Nonsense variants (`NUL_` / `CDS_`)

**Nonsense variants** introduce a premature termination codon (PTC). SVCv4
(Supplementary Material 8) routes each VBC down **one** of three branches, selected
by whether **NMD** is predicted and whether an alternative-Met **rescue** codon has
evidence. Each branch resolves to a parent code — `NUL_` or `CDS_` — via the same
pipeline: **PRD** (predictive) → **FXN** (functional, SM 20) → **INF** (informative,
SM 19) → the capped parent total. Modeled as one `NonsenseAssessment`
(`prediction_outcome` = `NonsensePredictionOutcome`); each step is **documented, not
computed**.

!!! note "Modeled here — inputs captured"

    Both models (`NonsenseAssessment`, `NonsensePredictiveEvidence`) capture the
    analyst's inputs; the scoring is documented, not computed.

| Branch (`prediction_outcome`) | NMD? | Rescue? | Parent code | PRD initial | Parent total |
|---|---|---|---|---|---|
| `NMD_NO_RESCUE` (yellow) | yes | no | `NUL_` | `+6.0` | `−8.0 to +10.0` |
| `NMD_WITH_RESCUE` (orange) | yes | yes | `CDS_` | `−1.0 to +6.0` | `−8.0 to +10.0` |
| `NO_NMD` (violet) | no | — | `CDS_` | `0.0 to +6.0` | `−8.0 to +10.0` |

The parent code reuses `PfdParentCode` (`NUL` / `CDS`) and **follows from**
`prediction_outcome` (yellow → `NUL`; orange/violet → `CDS`) — `parent_code` records
that resolved code and should be kept consistent with the branch.

## Predictive (`*_PRD_`)

The **yellow** branch awards a fixed **+6.0** for a predicted NMD event. The
**orange** and **violet** branches instead read initial points from a table keyed on
the **fraction of protein lost** (`protein_fraction_reduced`) — and, as an
alternative axis, the **criticality of the deleted amino acids**, which leans on
Critical Amino Acids and is **deferred** (see the cross-reference note below). The
`alternative_met_rescue` flag records the rescue-codon evidence that distinguishes
the orange branch. Positive initial points are then reduced by the
[Molecular Mechanism & Exon Relevance](index.md#molecular-mechanism-exon-relevance-modeled-inputs)
matrix (SM 18); the result is coded `*_PRD_` per the branch's range above.

## Functional (`*_FXN_`) and informative (`*_INF_`)

`FXN` reuses the generic [Functional Assays](index.md#functional-assays-modeled-inputs)
module (`FunctionalAssayEvidence`), coded `−8.0 to +8.0` — for the yellow branch the
functional data must confirm **loss of transcript/protein** (validating NMD), not a
truncated-protein effect. `INF` reuses the generic
[Informative Variants](index.md#informative-variants-modeled-inputs) module
(`InformativeVariantsEvidence`, SM 19): same-exon PTC (nonsense/frameshift) variants
(+2.0 first P / +1.0 first LP / +1.0 each additional; negatives for B/LB), coded
`−8.0 to +8.0`. The **position** eligibility differs subtly per branch: same-exon
same-NMD (yellow); a P/LP PTC between the VBC and the alternate start (orange); a PTC
downstream of the VBC (violet) — a documented eligibility rule, not separate fields.

## Held combined value and the parent total

Per SM 8, the model records **both** the separate coded values and the one held
`PRD + FXN` combined value (`prd_fxn_combined`, no distinct code). Note the held cap
is **`+10.0` for yellow** but **`+9.0` for orange/violet**, even though all three
*parent* totals cap at `+10.0`. The parent total (`parent_total`) is coded
`NUL_ −8.0 to +10.0` (yellow) or `CDS_ −8.0 to +10.0` (orange/violet).

**Gain-of-function** truncation effects (when NMD is not induced) are explicitly out
of scope in SM 8 and are not modeled here.

!!! note "SM 7 vs SM 11 cross-reference"

    SM 8's text cites "Supplementary Material 11" for Determining Critical Amino
    Acids, but in this project's [Spec coverage](../../reference/spec-alignment.md)
    Critical Amino Acids is **SM 7** (SM 11 is Canonical Splice Variants). Treat
    **SM 7** as the canonical reference; the critical-domain criticality axis is
    deferred to that increment.
