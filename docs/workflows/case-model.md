# Case model

A **Case** is the case-level payload a curator captures from the literature to
represent a single human clinical (CLN) observation supporting (or opposing)
variant pathogenicity. It is the structured `data` behind a
`clinical_observation` Evidence Item.

The model is a permissive **superset**: every attribute is optional on the type.
Which attributes are required (`R`), optional (`O`), conditional (`C`), or not
applicable (`X`) depends on the CLN workflow — `CLN_AFF` (Affected), `CLN_DNV`
(De novo), `CLN_ALTV` (Alternative Cause-Variant), `CLN_ALTG` (Alternative
Cause-Gene), and `CLN_UAF` (Unaffected). `CLN_ALTV` + `CLN_ALTG` are subtypes of
`CLN_ALT` (Alternative Cause).

Applicability and the conditional rules live in a single source of truth,
`schemas/applicability/case_applicability.yaml`. The per-workflow JSON Schemas
under `schemas/json/case/` and the tables below are generated from it; this
phase documents the conditional rules but does not enforce them.

See the [`Case` model reference][svcv4_model.Case] for field types.

This is the **structured backbone** of the
[Clinical Observations](clinical-observations.md) workflows: each CLN workflow
page describes *what evidence to capture*, and the per-workflow tables below say
exactly which fields apply. Terminology follows the
[Glossary](../reference/glossary.md) — "the variant" is the **VBC**, "the
disease/condition" is the **MDE**.

## Applicability by workflow

<!-- BEGIN GENERATED: applicability tables -->

**Legend:** <span class="appl-r">required (R)</span> &nbsp;·&nbsp; <span class="appl-c">conditional (C)</span> &nbsp;·&nbsp; <span class="appl-o">optional (O)</span> &nbsp;·&nbsp; <span class="appl-x">not applicable (X)</span>

### Superset matrix

Every Case attribute across the five CLN workflows, with the nested structure preserved. Conditional rules are summarized in **Notes**.

<div class="appl-matrix" markdown="1">

| AFF | DNV | ALTV | ALTG | UAF | Property | Notes |
|---|---|---|---|---|---|---|
| <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | `moi` | AD, AR, XLD, XLR, SD — ALTV does not yet support AR/XLR |
| <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | `pop_frq_points` | must be >= -1.0 |
| <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | `case_proband_info` |  |
| <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `sex` | M/F/U/T |
| <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `age` | age + unit, or an age range; general or disease-specific |
| <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `phenotypes` | 0..many |
| <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ `name` |  |
| <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-o">O</span> | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ `code` | HPO identifier when possible |
| <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `pheno_specificity_for_gene` | SPECIFIC, CONSISTENT, INCONSISTENT — curator makes the PHENO SPECIFICITY call; rule coordination is out of scope |
| <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-c">C</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `pheno_severity` | BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG — CLN_ALTG excludes `BIALLELIC_LT_EXPECTED` |
| <span class="appl-o">O</span> | <span class="appl-o">O</span> | <span class="appl-x">X</span> | <span class="appl-c">C</span> | <span class="appl-r">R</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `age_matched_penetrance` | <80%, 80-100%, near 100% — only applicable at all for ALT Gene among the conditional workflows |
| <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `confirmed_parental_relationship` |  |
| <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `all_relevant_genes_tested` |  |
| <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | `vbc` |  |
| <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `id` |  |
| <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `zygosity` | the only variant_type element needed for case-level VBC assessment |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | `compound_het_variant` | AFF only; otherwise use additional_variant — biallelic disease eval with a het VBC |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `id` |  |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `zygosity` | fixed = `HET` (CLN_AFF) |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `phase_in_ref_to_vbc` | fixed = `TRANS` (CLN_AFF) |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `phase_confidence` |  |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `classification` |  |
| <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | `additional_variant_exists` |  |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | `additional_variants` | compound-het additional variants are NOT supported — requires `additional_variant_exists == TRUE` |
| <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `id` |  |
| <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `gene` |  |
| <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ `symbol` | gene symbol; follows the gene's applicability |
| <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ `mde_associated_gene` | required if gene is different from VBC gene |
| <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `zygosity` | HOM / HET / HEMI |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `phase_in_ref_to_vbc` | only if same gene as VBC |
| <span class="appl-c">C</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `phase_confidence` | only if phase is captured |
| <span class="appl-r">R</span> | <span class="appl-x">X</span> | <span class="appl-r">R</span> | <span class="appl-r">R</span> | <span class="appl-x">X</span> | &nbsp;&nbsp;&nbsp;&nbsp;↳ `classification` | must be P-LP if ALTV or ALTG use case |

</div>

### Per-workflow structures

Expand a workflow to see only its applicable fields as a JSON example with mock data — **bold** = required, <span class="appl-c">underlined</span> = conditional, *italic* = optional; not-applicable fields are omitted.

<details class="appl-detail">
<summary>Affected <code>CLN_AFF</code></summary>
<pre class="appl-json">
{
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case_proband_info"</span>: {
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-r">"pheno_specificity_for_gene"</span>: <span class="j-str">"SPECIFIC"</span>,
    <span class="j-key appl-o">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"all_relevant_genes_tested"</span>: <span class="j-str">"TRUE"</span>
  },
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HET"</span>
  },
  <span class="j-key appl-c">"compound_het_variant"</span>: {
    <span class="j-key appl-c">"id"</span>: <span class="j-str">"clinvar:VCV000000002"</span>,
    <span class="j-key appl-c">"zygosity"</span>: <span class="j-str">"HET"</span>,
    <span class="j-key appl-c">"phase_in_ref_to_vbc"</span>: <span class="j-str">"TRANS"</span>,
    <span class="j-key appl-c">"phase_confidence"</span>: <span class="j-str">"HIGH"</span>,
    <span class="j-key appl-c">"classification"</span>: <span class="j-str">"P"</span>
  },
  <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
  <span class="j-key appl-c">"additional_variants"</span>: [
    {
      <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
      <span class="j-key appl-r">"gene"</span>: {
        <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
        <span class="j-key appl-r">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>
      },
      <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
      <span class="j-key appl-c">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
      <span class="j-key appl-c">"phase_confidence"</span>: <span class="j-str">"LOW"</span>,
      <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
    }
  ]
}
</pre>
</details>

<details class="appl-detail">
<summary>De novo <code>CLN_DNV</code></summary>
<pre class="appl-json">
{
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"pop_frq_points"</span>: <span class="j-num">0</span>,
  <span class="j-key appl-r">"case_proband_info"</span>: {
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-r">"pheno_specificity_for_gene"</span>: <span class="j-str">"SPECIFIC"</span>,
    <span class="j-key appl-o">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>,
    <span class="j-key appl-r">"confirmed_parental_relationship"</span>: <span class="j-str">"TRUE"</span>,
    <span class="j-key appl-r">"all_relevant_genes_tested"</span>: <span class="j-str">"TRUE"</span>
  },
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HET"</span>
  }
}
</pre>
</details>

<details class="appl-detail">
<summary>Alternative Cause-Variant <code>CLN_ALTV</code></summary>
<pre class="appl-json">
{
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case_proband_info"</span>: {
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-r">"pheno_severity"</span>: <span class="j-str">"MONO_EQ_EXPECTED"</span>
  },
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HET"</span>
  },
  <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
  <span class="j-key appl-r">"additional_variants"</span>: [
    {
      <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
      <span class="j-key appl-r">"gene"</span>: {
        <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
        <span class="j-key appl-r">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>
      },
      <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
      <span class="j-key appl-r">"phase_in_ref_to_vbc"</span>: <span class="j-str">"CIS"</span>,
      <span class="j-key appl-r">"phase_confidence"</span>: <span class="j-str">"LOW"</span>,
      <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
    }
  ]
}
</pre>
</details>

<details class="appl-detail">
<summary>Alternative Cause-Gene <code>CLN_ALTG</code></summary>
<pre class="appl-json">
{
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case_proband_info"</span>: {
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-c">"pheno_severity"</span>: <span class="j-str">"MONO_EQ_EXPECTED"</span>,
    <span class="j-key appl-c">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>
  },
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HET"</span>
  },
  <span class="j-key appl-r">"additional_variant_exists"</span>: <span class="j-str">"..."</span>,
  <span class="j-key appl-r">"additional_variants"</span>: [
    {
      <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000003"</span>,
      <span class="j-key appl-r">"gene"</span>: {
        <span class="j-key appl-r">"symbol"</span>: <span class="j-str">"ABCA4"</span>,
        <span class="j-key appl-r">"mde_associated_gene"</span>: <span class="j-str">"ABCA4"</span>
      },
      <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HOM"</span>,
      <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
    }
  ]
}
</pre>
</details>

<details class="appl-detail">
<summary>Unaffected <code>CLN_UAF</code></summary>
<pre class="appl-json">
{
  <span class="j-key appl-r">"moi"</span>: <span class="j-str">"AD"</span>,
  <span class="j-key appl-r">"case_proband_info"</span>: {
    <span class="j-key appl-o">"sex"</span>: <span class="j-str">"F"</span>,
    <span class="j-key appl-o">"age"</span>: { <span class="j-key">"value"</span>: <span class="j-num">7</span>, <span class="j-key">"unit"</span>: <span class="j-str">"MONTH"</span>, <span class="j-key">"qualifier"</span>: <span class="j-str">"EXACT"</span>, <span class="j-key">"raw"</span>: <span class="j-str">"7 mo"</span> },
    <span class="j-key appl-o">"phenotypes"</span>: [
      {
        <span class="j-key appl-o">"name"</span>: <span class="j-str">"Seizure"</span>,
        <span class="j-key appl-o">"code"</span>: <span class="j-str">"HP:0001250"</span>
      }
    ],
    <span class="j-key appl-r">"age_matched_penetrance"</span>: <span class="j-str">"NEAR_100"</span>
  },
  <span class="j-key appl-r">"vbc"</span>: {
    <span class="j-key appl-r">"id"</span>: <span class="j-str">"clinvar:VCV000000001"</span>,
    <span class="j-key appl-r">"zygosity"</span>: <span class="j-str">"HET"</span>
  }
}
</pre>
</details>

<!-- END GENERATED: applicability tables -->
