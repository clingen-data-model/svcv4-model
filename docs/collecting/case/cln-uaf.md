# Unaffected (CLN_UAF)

**CLN_UAF** collects evidence from **unaffected individuals who carry the VBC** —
benignity evidence, since a truly pathogenic, penetrant variant is not expected in
people who don't have the disease. It uses the [Case superset](index.md); this
page names the portion it turns on.

Throughout: **the variant = the VBC**; **the disease/condition = the MDE**
([Glossary](../../reference/glossary.md)).

## What is collected

- **`age_matched_penetrance`** (`R`) — the crux of the assessment: an unaffected
  carrier only counts against pathogenicity if they are old enough that the
  disease would be expected to have appeared (`<80%`, `80–100%`, `near 100%`).
- **`vbc_zygosity`** (`R`) and, where relevant, **`compound_het_variant`** — how
  the unaffected individual carries the VBC.
- **`family_id`** — to match the individual back to affected relatives when the
  observation comes from within a studied family.

Parameters: **`moi`** is required; **`pop_frq_points`** is **not applicable**
(`X`) — unlike the pathogenic counting codes, `CLN_UAF` is a benignity code and is
not POP-gated.

## Reference

- Applicability column and per-workflow JSON: [Case model & applicability](../../workflows/case-model.md).
- Full workflow and scoring: [Unaffected (CLN_UAF)](../../workflows/hod/cln/cln-uaf.md).
