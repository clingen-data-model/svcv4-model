# 3 · Case & segregation data collection

This is the arc's centerpiece. Every clinical-observation (CLN) and
locus-specificity (LOC) assessment draws on **case-level evidence** — what was
seen in probands and their relatives — and SVCv4 collects all of it in **one
structure**: the `Case`.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../reference/glossary.md)).

## The value of the Case model

A **Case** is the structured payload behind a `clinical_observation` Evidence
Item: the case-level evidence a curator captures from the literature to represent
a single human observation supporting (or opposing) variant pathogenicity.

The model is a permissive **superset** — one `Case` (a proband plus
`relatives[]`) holds *all* the fields any CLN or LOC assessment could need, and
**every field is optional on the type.** Which fields are required (`R`), optional
(`O`), conditional (`C`), or not applicable (`X`) is not baked into the type; it
is declared, per workflow, by an external **applicability matrix**
(`schemas/applicability/case_applicability.yaml`).

The payoff is **capture once, apply to many**:

- The same proband's data feeds `CLN_AFF`, `CLN_DNV`, and `LOC_SEG` without
  re-entry — `id` joins the individual across workflows and `family_id` joins the
  family.
- A single, permissive shape means a producing system builds and validates *one*
  entity, and the matrix — not a proliferation of per-workflow types — decides
  what each assessment consumes.
- The inputs that steer the workflows (`moi`, `pop_frq_points`,
  `gene_disease_validity`) are deliberately kept **out** of `Case` and carried on
  `WorkflowParameters`, so the Case stays a pure record of what was observed.

## A minimal worked example (CLN_AFF)

The busiest common workflow — **Affected (`CLN_AFF`)** — shows the shape. A
handful of fields are required; the rest are optional or not applicable for this
workflow. A minimal capture:

```json
{
  "moi": "AD",
  "pop_frq_points": 0,
  "vbc": { "id": "clinvar:VCV000000001" },
  "case": {
    "id": "proband-1",
    "family_id": "FAM-1",
    "sex": "F",
    "phenotypes": [{ "code": "HP:0001250", "name": "Seizure" }],
    "pheno_specificity_for_mde": "SPECIFIC",
    "testing": { "covers_all_genes_relevant_to_mde": "TRUE" },
    "vbc_exists": "TRUE",
    "vbc_zygosity": "HET"
  }
}
```

In prose: *a female proband with a seizure phenotype specific to the MDE; testing
covered all genes relevant to the MDE; the VBC is present and heterozygous, under
autosomal-dominant inheritance.* Note the split — `moi`, `pop_frq_points`, and
`vbc` are `WorkflowParameters` submitted **alongside** the `case`, while `sex`,
`phenotypes`, `testing`, and the rest are `Case` fields.

!!! note "This is a teaching example"

    Field names follow the current [Case model](../../workflows/case-model.md);
    they track the SVCv4 Standards, which are not yet finalized.

## How it is structured before sharing

- The [Case model & applicability](../../workflows/case-model.md) page carries
  the **generated applicability matrix** (every field × seven workflows) and a
  per-workflow JSON example drawn from real practice-set data.
- The [structuring case evidence](../../reference/scoring-map/structuring-case-evidence.md)
  page shows how those captured cases are arranged in the nested
  evidence-line tree (Approach 1 is the default).
- The `Case` and `CaseRelative` model classes give every field and type.

## The assessments this evidence feeds

Each assessment below activates a **different portion of the same Case superset**.
Follow a row for what that assessment collects and which fields it turns on; each
subsection links to its applicability column and per-code reference under
`workflows/hod/`.

| Assessment | What it collects | Applied Case-model portion |
|---|---|---|
| **[Affected — CLN_AFF](cln-aff.md)** | Affected probands carrying the VBC | `sex`, `phenotypes`, `pheno_specificity_for_mde`, `testing.covers_all_genes_relevant_to_mde` (+ `non_genetic_etiology_excluded`), `vbc_exists` / `vbc_zygosity`; biallelic: `compound_het_variant`, `additional_variants`. Params: `moi` R, `pop_frq_points` R (gated) |
| **[Unaffected — CLN_UAF](cln-uaf.md)** | Unaffected individuals carrying the VBC | `age_matched_penetrance`, `vbc_zygosity`, `compound_het_variant`, `family_id`. Params: `moi` R, `pop_frq_points` **X** |
| **[De novo — CLN_DNV](cln-dnv.md)** | Confirmed de-novo occurrences | `confirmed_parental_relationship`, `pheno_specificity_for_mde`, `testing.covers_all_genes_relevant_to_mde`. Params: `moi` R, `pop_frq_points` R (gated) |
| **[Case-control — CLN_CCS](cln-ccs.md)** | A variant-specific case-control study | **The exception — not a per-proband `Case`.** Study-level `CaseControlStudyEvidence` |
| **[Segregation — LOC_SEG](loc-seg.md)** | Co-segregation across a family | `relatives[]` (`CaseRelative`), `family_id`, `confirmed_parental_relationship`, `age_matched_penetrance`. Params: `moi` R, `pop_frq_points` R |
| **[Phenotype specificity — LOC_PHE](loc-phe.md)** | How specifically the locus tracks with phenotype | `gene_specificity_for_phenotypes`, `testing.diagnostic_yield_for_phenotypes`, `additional_variants`. Params: `moi` **X**, `pop_frq_points` R |

!!! note "Also in the Case family — CLN_ALT"

    SVCv4 also defines **CLN_ALT** (Alternative Cause, as `CLN_ALTV` /
    `CLN_ALTG`) — affected individuals whose disease has an alternate genetic
    cause. It uses the same Case superset (notably `pheno_severity`,
    `additional_variants` restricted to P/LP, and `age_matched_penetrance`) but
    is not one of the six named subsections here; see
    [Alternative Cause (CLN_ALT)](../../workflows/hod/cln/cln-alt.md) for its
    workflow and applicability.

## Next

After the case evidence, the final family is variant-impact evidence. Continue to
**[4 · Variant Impact data collection](../variant-impact.md)**.
