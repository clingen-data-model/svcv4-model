# Statement & Proposition

The [`Statement`][svcv4_model.Statement] is the canonical entry point
into the Classification Model. It carries:

- a **[`Proposition`][svcv4_model.Proposition]** (the SPOQ-structured
  assertion about a VBC and an MDE);
- the **`final_score`** for the curation;
- the **`score_classification`** — a categorical position on the
  Benign ↔ Pathogenic spectrum;
- a **`method`** reference identifying the applied SVCv4 specification
  version (baseline SVCv4 or a VCEP-specialised version, resolving
  into CSpec); and
- the collection of **`evidence_lines`** whose scores compose into the
  final score.

```text
Statement
 ├── proposition: Proposition  (SPOQ: Subject, Predicate, Object, Qualifier(s))
 ├── method: Method            (applied SVCv4 specification version → CSpec)
 ├── final_score: float
 ├── score_classification: VariantPathogenicityClassification
 ├── strength_direction?: str
 ├── contribution?: float
 └── evidence_lines: list[EvidenceLine]
```

## Proposition (SPOQ)

A **Proposition** is structured as four slots:

- **S**ubject — the **[`VBC`][svcv4_model.VBC]** (Variant Being
  Considered), expressed today as a placeholder dict that will be
  typed as a GA4GH VRS `Variation` in a follow-up.
- **P**redicate — the asserted relationship (default
  `is_causal_for`).
- **O**bject — the **[`MDE`][svcv4_model.MDE]** (Mendelian Disease
  Entity), typed via a CURIE (MONDO / OMIM / Orphanet).
- **Q**ualifier(s) — additional contextual qualifiers (mode of
  inheritance, population, tissue, etc.) — open shape today; will be
  constrained by the SVCv4 community profile.

## What the Statement's method identifies

The `method` slot at the Statement level is **not** the same as the
`method` slot on an Evidence Line.

- **At the Statement** it identifies the **applied SVCv4 specification
  version** — baseline SVCv4 or a specific VCEP specialisation
  selected via gene-disease-MOI scoping.
- **At an Evidence Line** it identifies the **specific CSpec method or
  rule** whose invocation produced that Evidence Line's score.

Both kinds of `Method` reference resolve into CSpec, which holds the
authoritative definitions.

## See also

- [Evidence Lines & Evidence Items](evidence-lines-and-items.md)
- [What this project is — and isn't](../overview/scope.md)
- Model reference: [`Statement`][svcv4_model.Statement],
  [`Proposition`][svcv4_model.Proposition].
