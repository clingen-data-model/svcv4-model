# Workflow explainer graphics — manifest

Home for the **per-workflow explainer graphics** used in the docsite and the
20-minute presentation
([plan](../../../plans/2026-09-18-svcv4-model-presentation.md)).

**Why a manifest, not just images:** the originals are **living claude.ai
artifacts** (HTML). This folder is the durable index that maps each workflow to its
source artifact. When a graphic is used in the deck or a site page, export a **PNG
still** into this folder using the filename in the table below, so the site/deck
reference a stable local asset rather than a remote artifact.

**Naming convention:** `<code-or-workflow>-<kind>.png`
(e.g. `nul-start-here.png`, `cln-aff-section.png`, `sm14-decision-tree.png`).

> These artifacts predate the plain-language / VA-Spec-`1.1.0` reconciliation.
> Before using one in front of the (non-VA-literate) audience, check it doesn't
> lead with `EvidenceLine`/`Statement` class vocabulary or v3 criteria codes — see
> the presentation plan's two hard constraints.

## Workflow "start here" explainers

| Workflow | Source artifact | Export filename |
|---|---|---|
| NUL (nonsense / NMD LoF) | https://claude.ai/code/artifact/5351845c-90d0-479e-843e-c7441bf998e6 | `nul-start-here.png` |
| CDS (LoF escaping NMD) | https://claude.ai/code/artifact/c293b562-7d93-4754-97a5-c77521bbdd19 | `cds-start-here.png` |
| MIS (missense) | https://claude.ai/code/artifact/504f73de-b6f0-45a6-8963-780a09aec384 | `mis-start-here.png` |
| POP_FRQ (population frequency) | https://claude.ai/code/artifact/82425a0a-092a-4407-8e80-19315591164f | `pop-frq-start-here.png` |

## Workflow decision trees

| Item | Source artifact | Export filename |
|---|---|---|
| PFD decision trees (7, Mermaid retrofit) | https://claude.ai/code/artifact/a7840f87-226b-4716-b27d-a4f5327a201a | `pfd-decision-trees.png` |
| SM 14 (exon duplication) decision tree | https://claude.ai/code/artifact/bd467295-53ea-41b7-a054-26471fed4468 | `sm14-decision-tree.png` |

## Per-code section prototypes (format templates)

PFD: MIS `9ad8b145` · CDS `41962b64` · NUL `fee4bb17` · SPL `66774a8f`.
HOD: POP_FRQ `ca288bfd` · CLN_AFF `7be28785` · CLN_DNV `34fed231` · CLN_UAF
`9f3e2a8d` · CLN_CCS `77a08e6c` · LOC_PHE `c96aa759` · LOC_SEG `14555caa`.
(All at `https://claude.ai/code/artifact/<id>`.)

## Deck slots

The presentation marks `[EXPLAINER: <workflow>]` at **slides 8, 11, and 13**. Pick
the workflow that matches the slide-13 worked example so the human decision-tree
view and the computed record sit side by side.

---

*Larry: if the graphics you meant are a different set (or live elsewhere), tell me
which and I'll rewrite this manifest. To pull a still: open the artifact, screenshot
it, and save it here under the export filename above.*
