# Case model

A **Case** is the case-level payload a curator captures from the literature to
represent a single human clinical (CLN) observation supporting (or opposing)
variant pathogenicity. It is the structured `data` behind a
`clinical_observation` Evidence Item.

The model is a permissive **superset**: every attribute is optional on the type.
Which attributes are required (`r`), optional (`o`), conditional (`c`), or not
applicable (`x`) depends on the CLN workflow — `CLN_AFF` (Affected), `CLN_DNV`
(De Novo), `CLN_ALTV` (Alternative Variant), `CLN_ALTG` (Alternative Gene), and
`CLN_UAF` (Unaffected). `CLN_ALTV` + `CLN_ALTG` generalize to `CLN_ALT`.

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

**Legend:** <span class="appl-r">required (r)</span> &nbsp;·&nbsp; <span class="appl-c">conditional (c)</span> &nbsp;·&nbsp; <span class="appl-o">optional (o)</span> &nbsp;·&nbsp; <span class="appl-x">not applicable (x)</span>

### Superset matrix

Every Case attribute across the five CLN workflows, with the nested structure preserved. Conditional rules are summarized in **Notes**.

| Attribute | Affected<br>`CLN_AFF` | De novo<br>`CLN_DNV` | Alternate Variant<br>`CLN_ALTV` | Alternate Gene<br>`CLN_ALTG` | Unaffected<br>`CLN_UAF` | Notes |
|---|---|---|---|---|---|---|
| `moi` | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | AD, AR, XLD, XLR, SD — ALTV does not yet support AR/XLR |
| `pop_frq_points` | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | must be >= -1.0 |
| `case_proband_info` | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `sex` | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | M/F/U/T |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `age` | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | age + unit, or an age range; general or disease-specific |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `phenotypes` | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | 0..many |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ `name` | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ `code` | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-o">o</span> | HPO identifier when possible |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `pheno_specificity_for_gene` | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | SPECIFIC, CONSISTENT, INCONSISTENT — curator makes the PHENO SPECIFICITY call; rule coordination is out of scope |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `pheno_severity` | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-c">c</span> | <span class="appl-x">x</span> | BIALLELIC<expected not applicable to ALT Gene; ALTV rule is more nuanced than ALTG — CLN_ALTG excludes `BIALLELIC_LT_EXPECTED` |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `age_matched_penetrance` | <span class="appl-o">o</span> | <span class="appl-o">o</span> | <span class="appl-x">x</span> | <span class="appl-c">c</span> | <span class="appl-r">r</span> | <80%, 80-100%, near 100% — only applicable at all for ALT Gene among the conditional workflows |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `confirmed_parental_relationship` | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `all_relevant_genes_tested` | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> |  |
| `vbc` | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `id` | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `zygosity` | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | the only variant_type element needed for case-level VBC assessment |
| `compound_het_variant` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | AFF only; otherwise use additional_variant — biallelic disease eval with a het VBC |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `id` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `zygosity` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | fixed = `HET` (CLN_AFF) |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `phase_in_ref_to_vbc` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | fixed = `TRANS` (CLN_AFF) |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `phase_confidence` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `classification` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> |  |
| `additional_variant_exists` | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> |  |
| `additional_variants` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | compound-het additional variants are NOT supported — requires `additional_variant_exists == TRUE` |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `id` | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `gene` | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ `symbol` | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | gene symbol; follows the gene's applicability |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ `mde_associated_gene` | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | required if gene is different from VBC gene |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `zygosity` | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | HOM / HET / HEMI |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `phase_in_ref_to_vbc` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | only if same gene as VBC |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `phase_confidence` | <span class="appl-c">c</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-x">x</span> | only if phase is captured |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ `classification` | <span class="appl-r">r</span> | <span class="appl-x">x</span> | <span class="appl-r">r</span> | <span class="appl-r">r</span> | <span class="appl-x">x</span> | must be P-LP if ALTV or ALTG use case |

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
    <span class="j-key appl-c">"phase_confidence"</span>: <span class="j-str">"high"</span>,
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
      <span class="j-key appl-c">"phase_confidence"</span>: <span class="j-str">"low"</span>,
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
<summary>Alternate Variant <code>CLN_ALTV</code></summary>
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
      <span class="j-key appl-r">"phase_confidence"</span>: <span class="j-str">"low"</span>,
      <span class="j-key appl-r">"classification"</span>: <span class="j-str">"LP"</span>
    }
  ]
}
</pre>
</details>

<details class="appl-detail">
<summary>Alternate Gene <code>CLN_ALTG</code></summary>
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
