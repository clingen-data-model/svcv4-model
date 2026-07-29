# The classification inputs

Before any workflow captures evidence, a classification is anchored by a small,
fixed set of inputs. These don't change per Evidence Code — they're set once per
classification and then steer how every workflow applies and scores evidence,
all the way up to the final **Variant Pathogenicity Statement**.

Throughout: **the variant = the VBC** (Variant Being Classified) and **the
disease/condition = the MDE** (Mendelian Disease Entity). See the
[Glossary](../reference/glossary.md) and [Core concepts](../reference/concepts.md)
for full definitions — this page introduces why each one matters.

## VBC — the variant being classified

The single variant under evaluation. It's what every workflow is gathering
evidence *about*, and it's the Proposition's subject (`subjectVariant`) in the
final Statement — see [The assertion framework](assertion-framework.md).

## MDE — the disease being assessed

The disease/condition the VBC is being classified *against*. An MDE is a
gene + phenotype pairing, not just a gene: a single gene can be associated with
more than one MDE (different inheritance patterns, different mechanisms, or
both), so classification is always made with respect to one specific MDE, not
a gene in general. This becomes the Proposition's object (`objectCondition` /
`objectConditionSet`).

## MOI — mode of inheritance

Whether the VBC's relationship to the MDE is monoallelic (AD), biallelic (AR),
X-linked (XLD/XLR), or semi-dominant (SD). MOI isn't just descriptive metadata —
it actively **controls which path a workflow follows**: it selects which
scoring table `CLN_AFF` uses (monoallelic vs. biallelic), it's not applicable
at all to `LOC_PHE` but required for `LOC_SEG`, and it will similarly gate
future POP/PFD workflows. Get MOI wrong and every downstream workflow's
applicability and scoring can be wrong.

## Gene & Transcript

The gene the VBC sits in, and — increasingly, as more workflows come online —
the specific transcript evidence is being evaluated against (e.g. MANE Select).
Usually the VBC's gene *is* the MDE-associated gene, but not always: when a
curator is weighing an alternate cause of disease (`CLN_ALT`), the gene
carrying the alternate variant may differ from the VBC's own gene, which is why
the model carries an explicit `mde_associated_gene` distinction rather than
assuming a 1:1 gene ↔ variant ↔ disease relationship.

## How these fit together

`VBC`, `MDE`, and `MOI` are **`WorkflowParameters`** — shared inputs submitted
alongside a `Case`, not fields of the `Case` itself (see
[Capture your first case](first-case.md) for where this split shows up in
practice). Together with `Gene`/`Transcript`, they're the constants a
classification carries into *every* workflow it touches — currently the five
CLN workflows and the two LOC workflows, and the same inputs will anchor POP
and PFD once those are modeled. They feed directly into the Proposition's SPOQ
(subject = VBC, object = MDE, with MOI as a qualifier) described next in
[The assertion framework](assertion-framework.md).

## See also

- [The assertion framework](assertion-framework.md) — how VBC/MDE become a Proposition and Statement.
- [Core concepts](../reference/concepts.md) — full reference detail on each of these, plus Zygosity/Phase and the Case model itself.
- [Capture your first case](first-case.md) — a concrete worked example using these inputs.
