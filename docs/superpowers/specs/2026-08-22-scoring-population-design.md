# Reference scorer — Population (POP, SM 3) — design

**Date:** 2026-08-22
**Status:** Draft (design) — for user review
**Branch:** `feat/scoring-population` (off `main`)
**Scope:** the FIRST HOD (Human Observational Data) scorer — POP_FRQ + POP_HMZ. Establishes the
`scoring/hod/` subpackage.

## Goal

Add `reference_score_population` (SM 3): the two benignity-only population codes — **POP_FRQ**
(FAF-vs-DAFT fold bands) and **POP_HMZ** (homozygote/hemizygote occurrences). Non-authoritative;
CSpec authoritative. First scorer outside `pfd/` — creates `scoring/hod/`.

## The two codes (both benignity-only, ≤ 0)

### POP_FRQ — FAF/DAFT fold bands (SM 3 L28, verified vs the FBN1 golden fixture)

`fold = faf / daft`, then:

| fold | POP_FRQ |
|---|---|
| `< 1.5×` | `0.0` |
| `1.5× .. < 5×` | `−1.0` |
| `5× .. < 15×` | `−3.0` |
| `≥ 15×` | `−6.0` |

**Boundary assumption (flagged):** SM 3 states the bands with strict `>`/`<` for the 1.5× and
5× edges but the top band as **inclusive** ("0.001770 or more" → −6.0, i.e. `≥ 15×`). SM 3 leaves
the exact `1.5×` and `5×` points unassigned (gaps). The reference scorer makes **each band's
lower edge inclusive** (`fold ≥ 1.5 → −1`, `≥ 5 → −3`, `≥ 15 → −6`) — the deterministic reading
consistent with the golden fixture's inclusive top. Recorded in `provenance`.

`_ND` when `faf is None` or `daft is None` or `daft <= 0` (no fold computable). A computed `0.0`
(fold < 1.5) **is** recorded — SM 3 L5: "nearly every variant … should have a score of 0, −1.0,
−3.0, or −6.0", so `POP_FRQ_0.0` is a real coded value, not an absence. (SM 3 L5: a variant
**absent** from all databases is still assessable → enter `faf = 0.0` (→ `POP_FRQ_0.0`); a `None`
`faf` means "not evaluated" → `_ND`. Noted in provenance.)

### POP_HMZ — eligible occurrences from the 2nd (SM 3 Table 7)

A per-observation benignity weight per **eligible** occurrence, counted **only from the 2nd** (the
1st is free), and only when `hmz_eligible == TriState.TRUE` (the MDE's penetrance + severity make
affected individuals implausible in the database).

**Eligible-occurrence count** depends on the **MOI**:

- **AD / AR / SD** (and `None`): homozygotes only → `homozygote_count`.
- **X-linked (XLD / XLR)**: homozygotes **or** hemizygotes → `homozygote_count + hemizygote_count`.

**Per-observation weight** also depends on the MOI (SM 3 **Table 7**, L105–122):

| MOI | weight / eligible observation |
|---|---|
| **AD** (Autosomal Dominant, homozygous) | **`−1.0`** |
| **AR / SD / XLD / XLR** | `−0.5` |

`points = weight × max(eligible_count − 1, 0)`, `weight = −1.0 if moi == MOI.AD else −0.5`.

**⚠️ Source contradiction (flagged, encoded to Table 7):** SM 3 **prose L93** says "for an
autosomal dominant **or** autosomal recessive pattern … **−0.5 pts** per homozygous occurrence",
but **Table 7** (the explicit "Evidence Point Values" table) assigns **AD → −1.0** (AR/SD/X-linked
−0.5). The reference scorer follows **Table 7** (the point-value authority) and flags this in
`provenance`. The already-merged `docs/workflows/hod/pop.md` currently follows the (incorrect)
prose reading — this increment **corrects it** — and the contradiction is logged as a WG
follow-up. The SM 3 worked example (AR, 3 homozygous → `−1.0` = −0.5 × 2) is consistent with
Table 7's AR row.

`_ND` when `hmz_eligible != TRUE` (criterion not applicable) or when no relevant count is
captured. A computed `0.0` (eligible, ≤ 1 occurrence) **is** recorded. No SM 3 floor/cap on
POP_HMZ (unbounded steps).

## `reference_score_population` — `scoring/hod/population.py`

`reference_score_population(evidence: PopulationEvidence, *, moi: MOI | None) -> ScoreResult`.
`moi` is a **required keyword** (consumed only by POP_HMZ for X-linked hemizygote counting; pass
explicit `None` when unknown → homozygotes only), mirroring the PFD `gene_disease_validity`
pattern. Two module-private helpers `_pop_frq_points(faf, daft)` and `_pop_hmz_points(evidence,
moi)` (each returns `float | None`).

- `sub_code_points`: `POP_FRQ` and/or `POP_HMZ` (each omitted when `_ND`).
- `held_combined`: empty (POP has no held intermediates).
- **`parent_code = "POP"`** — a grouping label, NOT an SVCv4 parent code (POP_FRQ/POP_HMZ are
  independent case-level codes); noted in `provenance`.
- **`parent_total`** = the sum of the recorded sub-codes (`POP_FRQ + POP_HMZ`), or `None` when
  both are `_ND`. A convenience subtotal — no SM 3 combined cap; the real cross-code sum happens
  in the later case-aggregation increment.
- `provenance`: the fold + band for POP_FRQ, the eligible count + MOI basis for POP_HMZ, the
  boundary-assumption note, and the "POP is a grouping label" note.

Exported from `svcv4_model.scoring` (sorted `__all__`; `reference_score_population` sorts after
`reference_score_nonsense`, before `reference_score_start_lost`). A new `scoring/hod/__init__.py`
(empty package marker, mirroring `scoring/pfd/`).

## Tests (TDD) — `tests/test_population_scoring.py`

**POP_FRQ (the FBN1 golden fixture, DAFT 0.000118 — SM 3 L28):**
- FAF 0.000100 (< 0.000177) → `POP_FRQ 0.0`
- FAF 0.000300 (0.000177 .. 0.000590) → `−1.0`
- FAF 0.001000 (0.000590 .. 0.001770) → `−3.0`
- FAF 0.001770 (= 15×, inclusive) → `−6.0`; FAF 0.002000 → `−6.0`
- boundary assumption: FAF 0.000177 (= 1.5×) → `−1.0`; FAF 0.000590 (= 5×) → `−3.0`
- `daft` None / `faf` None / `daft` 0 → `POP_FRQ` omitted (`_ND`)

**POP_HMZ:**
- AR, `hmz_eligible=TRUE`, `homozygote_count=3` → `POP_HMZ −1.0` (SM 3 example: −0.5 × 2)
- **AD**, `hmz_eligible=TRUE`, `homozygote_count=3` → `POP_HMZ −2.0` (Table 7 AD weight −1.0 × 2)
- XLR, `hmz_eligible=TRUE`, `homozygote_count=1`, `hemizygote_count=2` → `−1.0` (hemi counts; −0.5 × 2)
- AD, `hmz_eligible=TRUE`, `homozygote_count=1`, `hemizygote_count=5` → `0.0` (hemi ignored; 1 free)
- `hmz_eligible=FALSE` → `POP_HMZ` omitted; `hmz_eligible=TRUE` no counts → omitted

**Combined / DTO:** FAF −6 + POP_HMZ −1 → `parent_code "POP"`, `parent_total −7.0`; empty evidence
→ both `_ND`, `parent_total None`.

## Docs

- `docs/reference/scoring.md`: add a Population (SM 3) line — the first HOD scorer, the two
  benignity codes, the FAF/DAFT fold bands (flag the boundary assumption), POP_HMZ 2nd-occurrence
  counting (MOI-dependent, AD −1.0 / else −0.5), and the `parent_code="POP"` grouping-label
  convention.
- **Correct `docs/workflows/hod/pop.md`**: its POP_HMZ paragraph currently says a uniform "−0.5
  points per eligible occurrence" (the SM 3 prose reading) — fix it to the Table 7 reading (AD
  −1.0 / AR/SD/X-linked −0.5) and note the prose-vs-Table-7 conflict.
- **Add a `known-gaps.md` "Working Group follow-ups" row** for the SM 3 prose-L93-vs-Table-7
  POP_HMZ contradiction (encoded to Table 7, flagged) — same treatment as the SM 18 Figure-1 and
  SM 6 blue/violet items.

## Quality gates

`pytest`, `ruff`, drift gate (no schema — scoring stays out of root `__all__`),
`mkdocs build --strict`, clean tree. All existing scorers untouched.

## Out of scope

The DAFT derivation (calculator / binning / pathogenic-variants) — `daft` is consumed raw (the
analyst supplies the threshold). LOC/CLN scorers; case aggregation; classification band;
`validate_case`.
