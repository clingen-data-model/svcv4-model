# Workflow scoring-map — design decisions & context

**Date captured:** 2026-09-01
**Artifact:** `docs/reference/scoring-map.md` (branch `docs/scoring-map`, not yet merged)
**Status:** Living reference. `CLN_AFF` is fully worked as the **template**; the rest of the
codes/workflows will follow the same rules.

This preserves the decisions made while iterating on the scoring-map with Larry, so the pattern can
be replicated to every other code without re-deriving them.

## What the scoring-map is

A complete reference of **every place a score is produced** across the SVCv4 workflows + Summary
Table — one node per unique scoring point, aligned to **GA4GH GKS VA-Spec** so it can drive an
auditable, reproducible classification. Hierarchy mirrors the Summary Table:
**Evidence Category → Concept → Evidence Code → cell → aggregation → roll-up.**

## Core decisions (apply to ALL codes)

1. **One code per *cell* (scoring opportunity).** A `method.code` is minted for each cell — one
   distinct scoring opportunity = a single point value (or a *range*, for roll-up/parent codes). A
   **cell, not a point value, is the unit of a code.** Case signatures that resolve to the same
   cell share the code and group their cases in that code's `evidenceItems`. **Distinct cells keep
   distinct codes even when their point values coincide** (e.g. two `+1.5` biallelic cells stay
   separate). Cells collapse only when they are literally the same opportunity / not distinctly
   reachable (see HOM, NON, ALT, UAF below).

2. **Code = identity, score = outcome, shown separately.** A code is `CLN_AFF`; a node's score is
   `CLN_AFF (score: +1.0)` — **never** the compacted `CLN_AFF_+1`. **No code ends in a number** (the
   `_+N` suffix is a score, not the code).

3. **Proposed code naming:** `CLN_AFF_<TABLE>_<ROW>_<COL>`. Only `CLN_AFF` is an official svcv4
   code; the suffixed cell codes are *proposed* (svcv4 doesn't name the cells). Locked abbreviations:
   `TABLE`=`MONO`/`BIAL`; biallelic `ROW`=`RARE`(co-occ <0.0001)/`UNCM`(0.0001–0.01)/`INCP`
   (incomplete); `COL`=`CTP` confirmed-trans P/LP · `ATP` assumed-trans P/LP · `CTV` confirmed-trans
   VUS · `HOM` homozygous · `NON` none.

4. **GKS VA-Spec `EvidenceLine` alignment.** Every scored node is an `EvidenceLine` JSON object —
   any object with a `score` has `"type": "EvidenceLine"`, a `method` `{code, label}`, and a
   `score`. A **non-leaf** node has an **`evidenceLines`** array (children, summed and **capped per
   svcv4 rules**). A **leaf** node (a cell code) has an **`evidenceItems`** array — each item
   `{id, type, references (when available), data}`, where `data` holds the attributes required for
   that leaf's `method.code`. The array appears at two levels: `evidenceLines` (children) and
   `evidenceItems` (the cases for one cell — **multiple probands of the same cell sit in that one
   leaf's `evidenceItems`**).

5. **Provenance/audit reuses existing schema — no new fields.** On the `EvidenceItem`:
   `id` (stable id), `type` (`clinical_observation`), `references` (PMIDs/CURIEs/URLs — the source),
   `data` (a `Case`). `EvidenceItem.description` is available for a free-text source locator.
   `case.id`/`case.family_id` identify proband/family.

## `CLN_AFF` model (the worked template)

- **Roll-up:** `CLN_AFF` = `CLN_AFF_MONO` + `CLN_AFF_BIAL` (a sum of both table subtotals). MOI
  sets which are populated: AD/XLD → mono only; AR → biallelic only; **XLR** → mono (affected
  males) + biallelic (affected females); **semidominant** → mono (hets) + biallelic. Range **≥ 0**
  (floor 0, no upper cap). Per-cell scores are unaffected by MOI — only which subtotals are
  non-empty changes. (Earlier "xor / one table only" framing was corrected to this.)
- **Aggregation:** a leaf's score = `n × per-case` (`n` = `len(evidenceItems)`); a non-leaf's score
  = capped Σ of its `evidenceLines`.

### Monoallelic (Table 1) — 6 cells
`MONO_SPEC_THOR` +1.0 · `MONO_SPEC_LIM` +0.5 · `MONO_CONS_THOR` +0.5 · `MONO_CONS_LIM` +0.25 ·
`MONO_ALT` +0.0 (→CLN_ALT) · `MONO_UAF` +0.0 (→CLN_UAF).

### Biallelic (Table 2) — 14 cells (NON kept merged)
`BIAL_{RARE,UNCM,INCP}_{CTP,ATP,CTV}` (9), `BIAL_THOR_HOM` +1.0, `BIAL_INCP_HOM` +0.5, `BIAL_NON`
+0.0, `BIAL_ALT` +0.0, `BIAL_UAF` +0.0. SM 4 Table 2 is a 5×5 grid (25 positions) → 14 reachable
codes because:
- **HOM · RARE = UNCM** — co-occurrence (of two het variants) is undefined for a homozygote, so
  `RARE×HOM` and `UNCM×HOM` are the same cell → `THOR_HOM`; only thoroughness distinguishes HOM.
- **NON row-invariant** — a het with no valid in-trans 2nd variant scores 0 regardless of row →
  one code (decided: **NON stays merged**; its sub-signatures no-2nd/cis/unknown-phase/assumed-VUS/
  benign-2nd all resolve to the same +0.0 cell).
- **ALT / NOT-CONSISTENT rows column-invariant** — a P/LP alternate cause, or an inconsistent
  phenotype, overrides every column to 0 → one code each (`ALT`, `UAF`).

### `THOR` / `LIM` / `INCP` semantics
**`THOR` (thorough) is the same condition in both tables:** `covers_all_genes_relevant_to_mde`=TRUE
**and** `non_genetic_etiology_excluded`=TRUE **and** no VUS additional variant. (P/LP additional
variant is *not* part of THOR — it's the `_ALT` exit.) **MONO `LIM`** = the plain negation of THOR.
**BIAL `INCP`** = the same negation **plus** a biallelic-only trigger: THOR holds but
`compound_het_variant.co_occurrence_likelihood` is unestablished (neither `LT_0_0001` nor
`BETWEEN_0_0001_0_01`). So on the THOR attributes `LIM = INCP`; `INCP ⊋ LIM` (adds the co-occurrence
dimension mono lacks).

## Data items each `CLN_AFF` cell reads (real attribute names)

Routing/aggregation (common): `moi`, `case.sex`, `case.id`, `case.family_id`. Cell-discriminating:
`case.pheno_specificity_for_mde`, `case.testing.covers_all_genes_relevant_to_mde`,
`case.testing.non_genetic_etiology_excluded`, `case.additional_variants[].classification`,
`case.vbc_zygosity`, `case.compound_het_variant.{classification, phase_confidence,
co_occurrence_likelihood}`. (`moi`/`pop_frq_points` are top-level workflow params; proband fields
under `case.*`.)

## Three JSON organization approaches (contrasted in the doc; not yet locked)

All produce the same total; differ in where the per-case score and per-cell subtotal live:
1. **cases as `evidenceItems` under one cell-code leaf** (leaf score = n × per-case). Fewest nodes;
   per-cell subtotal explicit; cases are data, not scored lines. *(the primary shape used)*
2. **per-case leaves under a cell-code aggregate** — every case is its own scored `EvidenceLine`;
   per-cell subtotal preserved; deepest tree; cell code appears at two levels.
3. **per-case leaves flat under `CLN_AFF_MONO`** — every case its own scored line; no per-cell
   subtotal node. **DECISION STILL OPEN — pick a canonical approach before replicating.**

## Practice-set examples caveat

The `examples/practice-variant-set/*/classification.json` CLN_AFF targets (`CLN_AFF_+1`, etc.) are
**cross-proband illustrative placeholders** (e.g. MYH7's `+1.0` aggregates 3 probands, labelled
"illustrative"), and omit discriminating attributes (`non_genetic_etiology_excluded`,
`co_occurrence_likelihood`) — so they don't round-trip through the cell model yet. **Larry will
reconcile the examples to the finalized codes later.** Also: example `method.code` uses `svcv4:`
prefix; the scoring-map uses bare codes (prefix TBD).

## Next steps

- Lock the canonical JSON approach (1/2/3).
- Replicate the `CLN_AFF` template (cells + code-minting rule + data items + EvidenceLine tree) to
  every other code: CLN_DNV/ALTV/ALTG/UAF/CCS, POP_FRQ/HMZ, LOC_PHE/SEG/LOC, and the PFD parent +
  `_PRD`/`_SPA`/`_FXN`/`_INF` codes — producing an **absolute reference list of every svcv4 +
  proposed code**.
