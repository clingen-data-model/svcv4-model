# Docs-site reorganization — the "collecting & structuring the evidence" arc

**Date:** 2026-09-18
**Goal:** Retell the **"how the data is collected and structured"** story as one
clean, linear arc, replacing the scattered, redundant capture narrative that is
today spread across Getting Started, Workflows, and Reference.
**Status:** Proposal for Larry's sign-off. Human calls are tagged **[DECIDE]**.

**Decisions (resolved by Larry, 2026-09-18) — the [DECIDE] items below are now settled:**

1. **Tab label → "Collecting the evidence"** (replaces "Getting Started").
2. **Directory rename → do it:** `docs/getting-started/` → `docs/collecting/`
   (strict-gated; fix all inbound links in the same pass).
3. **Part-3 subsections → collapse** the six CLN/LOC pages behind
   `collecting/case/index.md`, driven from an in-page table (mirrors the PFD
   treatment) — not listed individually in the sidebar.
4. **CLN_CCS → standalone:** keep it framed as a standalone case-control study
   (`CaseControlStudyEvidence`), the explicit exception to the Case-model narrative.
5. **CLN_ALT → omitted** from the arc's named subsections (Larry's six stand; a
   light cross-link note is optional, not a subsection).
**Relationship to the other plans:** this is a *deeper cut into one specific arc*
of the broader
[docsite-simplification-plan](2026-09-18-docsite-simplification-plan.md). It does
**not** re-litigate that plan's cross-cutting moves (maturity labels, front-door
rewrite, VA-Spec 1.1.0 reconciliation, v3 criteria-code scrub, PFD/Examples nav
tiering). It *inherits* them and supplies the concrete target for the one thing
that plan left generic: "consolidate Getting Started." See §5 for how they run
together without conflict.

---

## 0. The maintainer's ask (quote — the arc must follow this progression)

Larry wants the data-collection story told cleanly, in this 4-part progression:

> 1. **Starting curation activities (NOT assessments).** First: defining the
>    classification, the VBC, the MDE, inheritance, gene, transcript, etc. — plus
>    other easily-captured evidence like gnomAD MAF, or computing the DAFT. These
>    are "starting curation activities," not assessments per se. Discuss how that
>    data would be organized **conceptually**, and how it would ultimately be
>    **structured** before sharing the final outcome.
> 2. **Population observations (POP).** Then the POP assessments — drill into
>    **POP_FRQ** and **POP_HMZ**. Important first steps because **POP_FRQ can be
>    gating for several downstream assessments.**
> 3. **Case & segregation data collection.** How cases are collected in a
>    structure that holds a **superset of all evidence needed for any Clinical
>    Observation (CLN) or Locus Specificity (LOC) assessment workflow.** First
>    explain the **value of the Case model** for applying case-level evidence,
>    THEN sub-sections for **CLN_AFF, CLN_UAF, CLN_DNV, CLN_CCS** and **LOC_SEG,
>    LOC_PHE** — each highlighting the **relevant portions of the applied Case
>    model** for that assessment.
> 4. **Variant Impact data collection.** Prediction, functional,
>    alteration/splicing, and informative-variant data collection, and how it is
>    **applied to the patterned assessments and workflows** in the Variant Impact
>    assessments.

**Framing guardrail (settled, do not contradict):** an **assessment** is a scored
line of evidence — a rule-level evaluation. The Part-1 items (VBC/MDE/gene/
transcript, gnomAD MAF, DAFT computation) are **inputs / curation activities**,
not assessments. The whole arc is about **collecting and structuring** the
evidence — the capture side — *underneath* the assessments, consistent with the
repo's stance that this model captures evidence while the (not-yet-built) method/
ruleset model scores it. Parts 2–4 describe the *evidence collected for* each
assessment family, not the scoring math.

---

## 1. Diagnosis — where "how data is collected" is scattered today

The capture story is currently told **three times, from three angles, with heavy
overlap and no single spine.** A reader cannot tell which telling is canonical.

### 1a. Getting Started narrates capture as a teaching sequence (7 pages)

`docs/getting-started/` walks capture once, gently, but the seven pages braid
together three different jobs (the "why," the entity backbone, and two worked
examples) and lean on the **retired separate `EvidenceLine` class**:

| Page | What it does | Problem |
|---|---|---|
| `show-your-work.md` | the "why" of structured evidence | good; but teaches `Statement → Evidence Line → Evidence Item` as distinct classes (retired shape) |
| `classification-inputs.md` | VBC / MDE / MOI / Gene / Transcript | **this is Part-1 material** — but it duplicates `reference/concepts.md`'s VBC/MDE/MOI/Gene sections |
| `assertion-framework.md` | Proposition (SPOQ) + Statement backbone | teaches the retired distinct `EvidenceLine` class; overlaps `reference/va-spec-profile.md` and `reference/model.md` |
| `capturing-basic-evidence.md` | a full `POP_FRQ` walkthrough (FAF, DAFT, scoring bands) | **this is Part-2 material** — but it **duplicates `workflows/hod/pop.md`** almost point-for-point (same FAF/DAFT explanation, same benignity bands) |
| `evidence-lines-and-items.md` | Evidence Item vs Evidence Line, field shapes | teaches the retired class; overlaps `reference/evidence-structures.md` |
| `rolling-up-scores.md` | Code → Concept → Category → Statement roll-up | overlaps `workflows/index.md` (same hierarchy) and is really scoring, not collection |
| `first-case.md` | a minimal `CLN_AFF` capture | **this is Part-3 material** — but it duplicates the per-workflow JSON already generated on `workflows/case-model.md` |

Net: the entity backbone is taught **three times** (`show-your-work` +
`assertion-framework` + `evidence-lines-and-items`), `POP_FRQ` capture **twice**
(`capturing-basic-evidence` + `workflows/hod/pop.md`), and the classification
inputs **twice** (`classification-inputs` + `reference/concepts.md`).

### 1b. Workflows narrates capture per-workflow

- `docs/workflows/case-model.md` — the Case superset + the generated
  applicability matrix + per-workflow JSON examples (**Part-3 artifact**).
- `docs/workflows/hod/pop.md` — POP capture + scoring tables (**Part-2**,
  duplicates `capturing-basic-evidence.md`).
- `docs/workflows/hod/cln/index.md`, `cln-aff.md`, `cln-dnv.md`, `cln-alt.md`,
  `cln-uaf.md`; `hod/loc/index.md`, `loc-phe.md`, `loc-seg.md` — per-code "what to
  capture" pages (**Part-3**).
- `docs/workflows/pfd/index.md` + 10 variant-type pages — PFD capture (**Part-4**).

### 1c. Reference narrates *structure* from the scoring side

- `docs/reference/evidence-structures.md` — the full Pydantic-model catalog
  ("the data structures that capture a curator's inputs") — this is the real
  **"how it's structured before sharing"** artifact, but it lives at the back.
- `docs/reference/scoring-map/structuring-case-evidence.md` + `index.md` — the
  GKS `EvidenceLine`-tree structuring (three approaches) — the other half of
  "how it's structured," told from the scoring map.
- `docs/reference/concepts.md` — VBC / MDE / Gene / MOI / Zygosity / Case /
  Cohort Allele Frequency / DAFT / Gene-Disease Validity (**duplicates
  Part-1/Part-3 conceptual content**).

**The cruft, precisely:** there is no single "collecting the evidence" spine.
Getting Started *teaches* it, Workflows *specifies* it per code, Reference
*catalogs* it — and the three overlap without a stated division of labor, so the
same facts (POP_FRQ, the VBC/MDE inputs, the entity backbone) are re-narrated in
each. A first reader meets the capture story in fragments and can't sequence them.

---

## 2. Proposed IA — one arc, a clear division of labor

**The fix is not "add more pages." It is:**

1. **Build one linear narrative arc** — *Collecting & structuring the evidence* —
   that tells Larry's 4-part story end to end. This **replaces** the 7-page
   Getting Started sequence (which is where the "cruft" concentrates).
2. **Declare a division of labor** so nothing is narrated twice:
   - **Arc (new)** = the *conceptual capture story* + "how it's structured before
     sharing" — narrative, sequential, one telling.
   - **Workflows** = the *per-code reference* (applicability tables, per-code
     detail) the arc links into.
   - **Reference** = the *structural catalogs* (`evidence-structures.md`,
     `scoring-map`, `model.md`, `concepts.md`, `glossary.md`) the arc links into.

   The arc **narrates and points**; Workflows and Reference **hold the detail**.
   Every duplicated telling collapses into a cross-link.

### Before → after nav

The **"Getting Started" tab is renamed and restructured** into the arc; the other
four tabs keep their top-level identity (and the simplification plan's own tiering
applies to them). Tabs stay at 5.

**Before (Getting Started tab):**

```
Getting Started:
  - Show your work: structured evidence      getting-started/show-your-work.md
  - The classification inputs                getting-started/classification-inputs.md
  - The assertion framework                  getting-started/assertion-framework.md
  - Capturing basic evidence                 getting-started/capturing-basic-evidence.md
  - Evidence Lines & Evidence Items          getting-started/evidence-lines-and-items.md
  - Rolling up Evidence Line scores          getting-started/rolling-up-scores.md
  - Capture your first case                  getting-started/first-case.md
```

**After (Collecting the evidence tab):**

```
Collecting the evidence:
  - Show your work: the shape it all rolls into   collecting/index.md          [Stable]
  - 1 · Starting curation activities              collecting/curation-activities.md   [Draft]
  - 2 · Population observations (POP)             collecting/population.md      [Draft]
  - 3 · Case & segregation data collection:
      - The Case model — one superset for CLN & LOC   collecting/case/index.md  [Stable]
      - Affected (CLN_AFF)                         collecting/case/cln-aff.md   [Draft]
      - Unaffected (CLN_UAF)                       collecting/case/cln-uaf.md   [Draft]
      - De novo (CLN_DNV)                          collecting/case/cln-dnv.md   [Draft]
      - Case-control (CLN_CCS)                     collecting/case/cln-ccs.md   [Draft]
      - Segregation (LOC_SEG)                      collecting/case/loc-seg.md   [Draft]
      - Phenotype specificity (LOC_PHE)            collecting/case/loc-phe.md   [Draft]
  - 4 · Variant Impact data collection            collecting/variant-impact.md [Draft]
```

> **[DECIDE] Tab label.** "Collecting the evidence" vs keeping "Getting Started"
> vs "Learn the model." Recommend **"Collecting the evidence"** — it names the
> arc's job and reads plainly for the broad audience. (The presentation plan's
> optional "Learn the model" doc-native path, if built, is a *different* teaching
> series and can sit alongside or fold its curator-workflow intro into
> `collecting/index.md`.)

> **[DECIDE] Directory rename.** `docs/getting-started/` → `docs/collecting/`.
> This churns links repo-wide; the `--strict` build is the gate. If the rename is
> unwanted, keep the `getting-started/` directory and only change filenames + nav
> labels. Recommend the rename for legibility.

The three subsection anchors (Parts 3's CLN/LOC pages) can be **collapsed behind
`collecting/case/index.md`** rather than listed in the sidebar, mirroring the
simplification plan's PFD treatment — driven from an in-page table. **[DECIDE]**

### How the arc relates to the other tabs (no duplication)

| The arc covers (narrative) | It links out to (detail) |
|---|---|
| Part 1 — VBC/MDE/MOI/gene/transcript, gnomAD MAF, DAFT *conceptually* | `reference/concepts.md` (definitions), `reference/evidence-structures.md#workflowparameters` (structure) |
| Part 2 — POP_FRQ / POP_HMZ capture + the POP_FRQ gate | `workflows/hod/pop.md` (scoring tables), `reference/evidence-structures.md#populationevidence` |
| Part 3 — value of the Case model + per-workflow field subsets | `workflows/case-model.md` (applicability matrix), `reference/scoring-map/structuring-case-evidence.md` (the EvidenceLine tree) |
| Part 4 — prediction/functional/splice/informative capture, one pipeline | `workflows/pfd/index.md` (per-variant-type pages), `reference/evidence-structures.md` (PFD assessments) |

---

## 3. Part-by-part page plan

### Arc index — `collecting/index.md` (merge of 4 GS pages)

**Merges** `show-your-work.md` + `assertion-framework.md` +
`evidence-lines-and-items.md` + `rolling-up-scores.md` into **one short primer**:
the "why" (show your work) and **the single recursive shape everything rolls into**
— a classification is a scored, directional claim, backed by **lines of evidence**,
backed by the **captured facts**, the same shape nesting at every level.

- **VA-Spec 1.1.0 reconciliation (inherited from the simplification plan §2a):**
  do **not** teach a distinct `EvidenceLine` class. Frame it as nested claims;
  keep class/property names (`Statement`, `hasEvidenceLines`, SPOQ, VRS) out of
  this narrative page — they belong only in `reference/va-spec-profile.md` /
  `reference/model.md`. This retires the three-times-taught two-class backbone.
- Keep the one nesting mermaid; drop the `rolling-up-scores.md` scoring detail
  (that is scoring, not collection — link to `workflows/index.md` and
  `reference/scoring.md`).
- Close with the 4-part roadmap so the reader knows the sequence they're entering.

### Part 1 — `collecting/curation-activities.md` (rewrite of `classification-inputs.md`)

**"Starting curation activities — not assessments."** The setup a curator does
before any assessment scores anything.

- **Conceptual organization:** the classification is anchored by VBC (variant),
  MDE (gene + phenotype pairing), inheritance (MOI), gene, transcript — set once,
  then steering every workflow. Plus the *easily-captured* evidence that needs no
  workflow branching: the gnomAD population frequency (FAF/MAF) and the **computed
  DAFT** (disease allele-frequency threshold, from prevalence / penetrance /
  locus + allelic heterogeneity). State plainly: **these are inputs, not
  assessments** — the DAFT is a *calculation*, the FAF a *lookup*.
- **How it is structured before sharing:** map each conceptual input to its model
  home — VBC/MDE/MOI + `pop_frq_points` + `gene_disease_validity` on
  `WorkflowParameters`; `Vbc` / `Mde` / `Gene` (symbol/id/transcript/
  `mde_associated_gene`); the FAF/DAFT + `DaftCalculatorInputs` on
  `PopulationEvidence`. Link to `reference/evidence-structures.md` for fields and
  `reference/concepts.md` for definitions (which this page **replaces as the
  narrative home**, so concepts.md becomes pure reference).
- Absorbs `classification-inputs.md`; folds the FAF/DAFT *concept* intro currently
  living in `capturing-basic-evidence.md` (the scoring bands move to Part 2 / the
  POP reference).

### Part 2 — `collecting/population.md` (merge of `capturing-basic-evidence.md`)

**"Population observations (POP)."**

- Drill into **POP_FRQ** (FAF vs DAFT fold-change → benignity-only points) and
  **POP_HMZ** (homozygote/hemizygote occurrences, counted from the 2nd, eligible
  only when penetrance/severity make affected individuals implausible).
- **Lead with the gating role Larry flags:** POP_FRQ is an important *first* step
  because it can **gate several downstream assessments** — the model carries its
  result as `WorkflowParameters.pop_frq_points` (required input to CLN_AFF,
  CLN_DNV, LOC_PHE, LOC_SEG; the scoring map's **POP_FRQ gate** zeroes CLN_AFF /
  CLN_DNV unless the VBC's POP_FRQ ∈ {0.0, −1.0}). Forward-reference Part 3 so the
  gate lands before the reader meets the codes it gates.
- **How it is structured before sharing:** `PopulationEvidence` (the payload
  behind a `population_frequency` Evidence Item).
- **De-duplication:** this page becomes the single *narrative* telling; the
  benignity-point tables and SM 3 prose-vs-Table-7 caveats stay only on
  `workflows/hod/pop.md` (the reference), linked. Today those tables live in both
  places — collapse to one.

### Part 3 — `collecting/case/` (the Case model + 6 subsections)

**"Case & segregation data collection."** This is the arc's centerpiece.

**`collecting/case/index.md` — the value of the Case model (first).** Explain
*why* a single, permissive **superset** entity holds all case-level evidence: one
`Case` (proband + `relatives[]`), shared across **every** CLN and LOC workflow,
with a declarative applicability matrix saying which fields each workflow needs.
The payoff — capture once, apply to many assessments; the same proband's data
feeds CLN_AFF, CLN_DNV, LOC_SEG without re-entry (`id` / `family_id` join them).
Note the `moi` / `pop_frq_points` / `gene_disease_validity` split onto
`WorkflowParameters` (not on `Case`). Link the **applicability matrix** on
`workflows/case-model.md` and the **EvidenceLine-tree structuring** (Approach 1
default) on `reference/scoring-map/structuring-case-evidence.md` as the "how it's
structured before sharing." Absorbs the worked example from `first-case.md`.

Then one subsection per assessment, **each anchored to the applied Case-model
fields** (from `schemas/applicability/case_applicability.yaml`, as surfaced on
`workflows/case-model.md`):

| Subsection | Applied Case-model portion (the fields that matter) | Params |
|---|---|---|
| **CLN_AFF** `case/cln-aff.md` | `sex`, `phenotypes`, `pheno_specificity_for_mde` (C), `testing.covers_all_genes_relevant_to_mde` (R) + `non_genetic_etiology_excluded` (O, SM 4), `vbc_exists`/`vbc_zygosity`; **biallelic:** `compound_het_variant` (+ `co_occurrence_likelihood`, SM 4); `additional_variant_exists`/`additional_variants` | `moi` R, `pop_frq_points` R (gated) |
| **CLN_UAF** `case/cln-uaf.md` | `age_matched_penetrance` (R), `vbc_zygosity`, `compound_het_variant`, `family_id` | `moi` R, `pop_frq_points` **X** |
| **CLN_DNV** `case/cln-dnv.md` | `confirmed_parental_relationship` (R), `pheno_specificity_for_mde` (C), `testing.covers_all_genes_relevant_to_mde` (R) | `moi` R, `pop_frq_points` R (gated) |
| **CLN_CCS** `case/cln-ccs.md` | **the exception — NOT a per-proband `Case`.** Study-level `CaseControlStudyEvidence`: `odds_ratio`, `ci_lower/upper`, `case_cohort_size`, `case_variant_count`, `control_cohort_size`, `controls_matched`, `ascertainment_bias_considered`. Note **CLN_CCS exclusivity** (silences other CLN codes except CLN_DNV) | standalone payload |
| **LOC_SEG** `case/loc-seg.md` | `relatives[]` (`CaseRelative`: `parent_of_proband`, `sex` if X-linked, `affected_w_mde`, `vbc_exists`, `vbc_zygosity`, `cmp_het_variant_exists`, `severe_phenotype`, `age`, `phenotypes`), `family_id`, `confirmed_parental_relationship`, `age_matched_penetrance` | `moi` R, `pop_frq_points` R |
| **LOC_PHE** `case/loc-phe.md` | `gene_specificity_for_phenotypes` (R), `testing.diagnostic_yield_for_phenotypes` (R), `additional_variants` | `moi` **X**, `pop_frq_points` R |

Each subsection: what evidence is collected, which superset fields it activates
(the table row above), and a link to that workflow's applicability column and
per-code reference under `workflows/hod/`. **CLN_ALT (ALTV/ALTG)** is not in
Larry's named list; keep it as a **cross-linked "also in the Case family"** note
(`pheno_severity`, `additional_variants` P/LP, `age_matched_penetrance`) pointing
to `workflows/hod/cln/cln-alt.md`, so the arc stays faithful to the six named
subsections without dropping a real workflow.

> **Note on CLN_CCS placement:** Larry groups it under "Case & segregation," but
> in the model it is a **standalone study payload, not a `Case`**. Keep it in the
> Part-3 sequence (as asked) while stating that distinction plainly — it is the
> one CLN code the Case superset does not realize.

### Part 4 — `collecting/variant-impact.md` (new; summarizes PFD capture)

**"Variant Impact data collection."** How predictive & functional evidence is
collected and **applied to one patterned pipeline** shared by all ten
variant-type workflows.

- The four data types Larry names, mapped to the captured structures:
  - **Prediction** — `_PRD` (`PfdPredictiveEvidence` + per-type predictive
    evidence; in-silico predictor + initial points).
  - **Functional** — `_FXN` (`FunctionalAssayEvidence` → `ProteinFunctionalAssay`
    OddsPath-calibrated + `AnimalModelEvidence`).
  - **Alteration / splicing** — `_SPA` (`SpliceAssayEvidence`) and the CDS
    alteration paths; the splice carve-out (RNA assays are `SPL_SPA`, not `_FXN`).
  - **Informative variants** — `_INF` (`InformativeVariantsEvidence` /
    `InformativeVariant`; distinct-only, star-rating + circularity gates).
- **The pattern (applied to the assessments/workflows):** every PFD workflow runs
  one pipeline — **predict → adjust for molecular mechanism / exon relevance
  (SM 18) → functional → informative → capped code total** — composed by the
  variant-agnostic `PfdCodeAssessment` scaffold and the four shared submodules
  (mechanism/exon-relevance SM 18, functional SM 20, informative SM 19, critical
  amino acids SM 7). Say plainly what an assessment is here: the scored `_PRD` /
  `_FXN` / `_INF` lines and the SM 18 multiplier (a factor, not points) are the
  assessments; this page covers the **evidence collected to feed them.**
- **How it is structured before sharing:** the per-variant-type assessment
  entities (`MissenseAssessment`, `NonsenseAssessment`, …) catalogued in
  `reference/evidence-structures.md`; link the 10 per-type pages under
  `workflows/pfd/` for the branch-by-branch detail (kept out of the arc to avoid
  re-narrating them).

---

## 4. Page disposition table (every data-collection page)

| Current page | Disposition | Target |
|---|---|---|
| `getting-started/show-your-work.md` | **Merge → arc index** | `collecting/index.md` (the "why"); drop retired-class framing |
| `getting-started/assertion-framework.md` | **Merge → arc index** | `collecting/index.md` (nesting backbone, VA-Spec 1.1.0 wording) |
| `getting-started/evidence-lines-and-items.md` | **Merge → arc index** | `collecting/index.md`; field detail → `reference/evidence-structures.md` |
| `getting-started/rolling-up-scores.md` | **Cut from arc / demote** | fold one paragraph into `collecting/index.md`; scoring detail already on `workflows/index.md` + `reference/scoring.md` |
| `getting-started/classification-inputs.md` | **Move + rewrite → Part 1** | `collecting/curation-activities.md` |
| `getting-started/capturing-basic-evidence.md` | **Move + merge → Part 2** | `collecting/population.md`; scoring tables stay only on `workflows/hod/pop.md` |
| `getting-started/first-case.md` | **Move → Part 3 index** | `collecting/case/index.md` (worked example) |
| `workflows/case-model.md` | **Keep** (the applicability-matrix artifact) | Part 3 links to it; mark `Stable` |
| `workflows/hod/pop.md` | **Keep** as POP reference | de-duped against Part 2; mark `Draft`/`Stable` |
| `workflows/hod/cln/*`, `workflows/hod/loc/*` | **Keep** as per-code reference | Part-3 subsections link in |
| `workflows/pfd/index.md` + 10 pages | **Keep** (per the simplification plan's PFD tiering) | Part 4 links in |
| `reference/evidence-structures.md` | **Keep** (the structural catalog) | every Part's "structured before sharing" links here |
| `reference/scoring-map/structuring-case-evidence.md` + `index.md` | **Keep** | Part-3 "structured before sharing" links here |
| `reference/concepts.md` | **Keep as pure reference** | Part 1 becomes the *narrative* home; concepts.md holds the definitions it links to (remove narrative overlap) |
| `reference/model.md`, `va-spec-profile.md`, `glossary.md` | **Keep** | class/property names live here, not in the arc |

No page is deleted; the merges collapse the 7 Getting Started pages into
**1 index + 1 (Part 1) + 1 (Part 2) + 1 Part-3 index + 6 Part-3 subsections + 1
(Part 4)**, and every previously-duplicated telling becomes a cross-link.

---

## 5. Coordination with the simplification plan (run together, no conflict)

This reorg **is the concrete realization** of the simplification plan's
"consolidate Getting Started 7 → 4" item — it supersedes that generic merge with
this specific 4-part arc. The two plans dovetail:

- **Maturity labels (simplification §3a):** apply the same
  `Stable`/`Draft`/`Placeholder` admonition to every new arc page (labels shown in
  the §2 nav). Same convention, no new mechanism.
- **VA-Spec 1.1.0 reconciliation (simplification §2a):** the arc index is exactly
  where the retired `EvidenceLine` class is currently taught three times —
  retiring it here **executes** that reconciliation for the highest-traffic pages.
  Class/property names stay in `reference/va-spec-profile.md` / `model.md`.
- **CSpec framing:** keep the "scoring lives in the method/ruleset model; CSpec is
  one early implementer, not the authority" wording the arc inherits — the arc
  describes *capture*, never asserts CSpec owns the standard.
- **v3 criteria-code scrub (simplification §2b):** the arc is new prose — write it
  v4-only from the start (no v3 code ↔ v4-process mappings). Principled v3/v4
  differences are fine; per-rule mappings are not.
- **PFD / Examples nav tiering (simplification §4):** unchanged. Part 4 links into
  the tiered PFD pages rather than re-listing them; the arc does not touch the
  Examples tab.
- **Never say "chaos":** frame the pre-arc state as *scattered / hard to sequence*,
  not "chaotic."

**Sequencing:** land the simplification plan's **Tier A** cross-cutting moves
first (maturity snippet, front-door rewrite, v3 scrub, PFD/Examples tiering), then
build this arc as the Getting-Started consolidation — the arc depends on the
maturity snippet and the VA-Spec wording being settled, and produces the
link-integrity churn `--strict` must catch.

---

## 6. Tiered execution checklist (`mkdocs build --strict` is the gate)

### Tier A — minimum clean cut (the arc's spine)

1. Create `docs/collecting/` (or rename `getting-started/` — **[DECIDE]** §2).
2. Write **`collecting/index.md`** — merge show-your-work + assertion-framework +
   evidence-lines-and-items; VA-Spec 1.1.0 wording (no retired `EvidenceLine`
   class); one nesting mermaid; 4-part roadmap. Mark `Stable`.
3. Write **`collecting/curation-activities.md`** (Part 1) from
   `classification-inputs.md` + the FAF/DAFT concept; end with "how it's
   structured" → `WorkflowParameters` / `Vbc`/`Mde`/`Gene` / `PopulationEvidence`.
4. Write **`collecting/population.md`** (Part 2) from `capturing-basic-evidence.md`;
   **lead with the POP_FRQ gate**; move the benignity tables out to
   `workflows/hod/pop.md` (de-dupe) and link.
5. Write **`collecting/case/index.md`** (Part 3 intro) — value of the Case model
   first; absorb `first-case.md`; link the applicability matrix + the
   EvidenceLine-tree structuring.
6. Update `mkdocs.yml` nav → the §2 "after" tree; add redirects/fix inbound links
   from Overview/Reference/Examples that pointed at `getting-started/*`.
7. `mkdocs build --strict` green (link integrity is the main risk of the moves).

### Tier B — the full arc

8. Write the six Part-3 subsections (`case/cln-aff|cln-uaf|cln-dnv|cln-ccs|
   loc-seg|loc-phe.md`), each anchored to its applied Case-model fields (§3 table);
   add the CLN_ALT cross-link note. Consider collapsing them behind
   `case/index.md` **[DECIDE]**.
9. Write **`collecting/variant-impact.md`** (Part 4) — the four data types →
   `_PRD`/`_FXN`/`_SPA`/`_INF`, the one shared pipeline, link the 10 PFD pages.
10. Trim the narrative overlap out of `reference/concepts.md` (make it pure
    definitions) and out of `workflows/hod/pop.md` (make it pure reference) now
    that the arc is the narrative home.
11. Apply maturity labels to every arc page; final `--strict` pass.

### `[DECIDE]` items for Larry

- **Tab label** — "Collecting the evidence" (recommended) vs "Getting Started" vs
  "Learn the model."
- **Directory rename** `getting-started/` → `collecting/` (recommended) vs keep
  path, change labels only.
- **Collapse Part-3 subsections** behind `case/index.md` (mirrors the PFD
  treatment) vs list all six in the sidebar.
- **CLN_CCS placement** — keep in the Part-3 sequence as asked, flagged as the
  non-`Case` exception (recommended) vs move it beside POP as another standalone
  study payload.
- **CLN_ALT** — cross-link note inside the arc (recommended) vs its own Part-3
  subsection (departs from Larry's named six).

---

## 7. Definition of done

- A reader meets the capture story **once**, in Larry's 4-part order, with each
  part ending in "how it's structured before sharing."
- No fact (POP_FRQ, VBC/MDE inputs, the entity backbone) is narrated in more than
  one place — duplicates are cross-links.
- The arc teaches **no retired `EvidenceLine` class** and **no v3 code mappings**.
- Every arc page carries a maturity label; `mkdocs build --strict` is green.
