# PVS-v5-MYH7 — mapping

How each value captured in [`source.md`](source.md) lands in our models. This is
the reviewable interpretation step; no JSON is encoded yet. Model shapes are
from `src/svcv4_model/` (Case model in `case.py`, classification stack in
`statement.py` / `proposition.py` / `evidence_line.py` / `evidence_item.py` /
`inputs.py`). Scores/classifications are **illustrative** — the arithmetic is
CSpec/Method-model territory, out of scope here.

## 1. The classification anchor (SPOQ)

The variant and disease define the Proposition that everything else scores.

| Source | Value | Target | Field |
|---|---|---|---|
| Gene / Variant / Protein | MYH7 · `c.4909G>A` · p.Ala1637Thr | `Proposition.subject` = **VBC** | `VBC.label`; `VBC.variation` (VRS placeholder) |
| CAID | `CA015454` | VBC identifier | `VBC.variation` (ClinGen Allele ID) |
| Transcript | `NM_000257.4` | Case-level `vbc.gene` | `Gene.symbol="MYH7"`, `Gene.transcript` |
| Disease + ontology id | hypertrophic cardiomyopathy · MONDO:0005045 | `Proposition.object` = **MDE** | `MDE.curie`, `MDE.label` |
| Predicate | (implied) | `Proposition.predicate` | `is_causal_for` (default) |
| MOI | AD | `WorkflowParameters.moi` | `MOI.AD` |
| LoF not an established mechanism | — | `Proposition.qualifiers` / `Method` context | gates LoF-based (PVS1-type) evidence **off** for this MDE |

## 2. Population frequency → POP workflow

The four frequency parameters are the inputs a POP calculation consumes to
produce a single capped points value.

| Source | Value | Target | Field |
|---|---|---|---|
| Prevalence Estimate | 1 in 200 | POP input | `EvidenceItem.data` (type `population_frequency`) |
| Allelic Heterogeneity | 0.05 | POP input | `EvidenceItem.data` |
| Genetic (Locus) Heterogeneity | 0.40 | POP input | `EvidenceItem.data` |
| Penetrance | 0.40 | POP input **and** case attribute | `EvidenceItem.data`; also `Case.age_matched_penetrance = LT_80` (0.40 < 0.80) |
| (computed) | POP_FRQ score | raw POP score — see note below | uncapped; gates CLN_AFF/CLN_DNV applicability at ≤ -3.0 |
| (computed, capped) | POP points | `WorkflowParameters.pop_frq_points` (ge=-1.0) | rolls up as a POP `EvidenceLine.score`; **actual value is CSpec math** |
| cardiodb / gnomAD links | URLs | provenance | `EvidenceItem.references` |

> **Model note (from review).** The tab's "≤ -3.0" gate operates on the raw
> **POP_FRQ score**, which is *uncapped* and can reach -3 or below. That is not
> the same value as `WorkflowParameters.pop_frq_points`, which is constrained
> `ge=-1.0` (the capped contribution that rolls up as a score).
>
> **Decision (deferred).** The raw POP_FRQ score will be modeled later, together
> with the POP_FRQ evidence-line method that derives the point value from the raw
> score and the DAF Threshold. For now we carry only `pop_frq_points` (the capped
> value) and use it as an input Evidence Data item feeding the CLN evidence
> methods (`CLN_AFF`, `CLN_DNV`). The `-3.0` gate is therefore documented here but
> not yet enforced in `case_applicability.yaml`.

## 3. Variant impact → Predictive & Functional Data (PFD)

These describe the variant's **molecular effect**, so they sit in the **PFD**
Evidence Category — not in CLN. Each datum is an `EvidenceItem` captured under a
PFD concept; the score its workflow produces is CSpec's, not ours. The
comparator allele (ClinVar 525029) rides along as an Evidence Item of the MIS
workflow — the workflow is about the amino-acid *residue*, so "other alleles at
this residue and their classifications" are its natural inputs (no per-item
subject tag needed).

| Source | Value | PFD concept | Field / notes |
|---|---|---|---|
| No predicted splicing impact | — | **Splicing (SPL)** — predictive | `EvidenceItem.data = {splice_impact: none}` |
| REVEL score | 0.577 | **Single-amino-acid change (MIS)** — predictive | `EvidenceItem.data = {tool: REVEL, score: 0.577}` |
| Other missense in codon → VUS | ClinVar 525029 | **Single-amino-acid change (MIS)** — same-residue evidence | `EvidenceItem` about the other allele; `references = ["ClinVar:525029"]`. Comparator is a **VUS**, not pathogenic, so classic PM5 weight likely does not apply — capture as context; scoring is CSpec's. |

PFD also houses **functional / experimental** evidence (assays, e.g.
`FNC_ASY`). REVEL and the same-codon observation are the **predictive** branch of
the same category; a wet-lab assay would be the **experimental** branch.

## 4. Clinical (probands) → CLN_AFF workflow

The three probands become three `Case` instances under the affecteds workflow,
each distinguished by how specific its phenotype is to the MDE.

| Proband | phenotype | `Case.pheno_specificity_for_mde` | Workflow |
|---|---|---|---|
| unspecified cardiomyopathy | unspecified CM | `CONSISTENT` | `CLN_AFF` |
| hypertrophic cardiomyopathy | HCM (= MDE) | `SPECIFIC` | `CLN_AFF` |
| dilated cardiomyopathy | DCM | `INCONSISTENT` | `CLN_AFF` |

Each `Case` also carries `age_matched_penetrance = LT_80` (from penetrance 0.40)
and `phenotypes: [{code, name}]`. The three cases roll up into one `CLN_AFF`
`EvidenceLine`. *(Specificity assignments above are a first-pass reading — worth
confirming against the SVCv4 phenotype-specificity definitions.)*

## 5. The tab's "reminder" notes → applicability rules

Both notes are encodable in `schemas/applicability/case_applicability.yaml` as
gating rules, which is exactly why MYH7 is a good baseline example.

| Note | Encodes as |
|---|---|
| affecteds & de novo NOT applicable if POP_FRQ score ≤ -3.0 | `CLN_AFF` / `CLN_DNV` applicability gated on the **raw POP_FRQ score** (below threshold → `x`) — see the model note in §2 |
| Locus specificity needs probands counted under affected cases | `LOC_PHE` requires `CLN_AFF` cases present (conditional applicability) |

## Workflows this entry exercises

`POP` · `CLN_AFF` · `LOC_PHE` · **PFD** (MIS, SPL). A multi-category anchor
(HOD + PFD), which is why it's the first PVS entry.

## Open questions for review

1. **Phenotype specificity** — ✅ **Resolved (confirmed).** The SPECIFIC /
   CONSISTENT / INCONSISTENT assignments in §4 are correct.
2. **POP threshold scale** — ✅ **Resolved.** The "≤ -3.0" gate applies to the
   raw **POP_FRQ score** (uncapped), which is distinct from `pop_frq_points`
   (ge=-1.0). See the model note in §2 — the raw score is not yet represented in
   the model and is a gap to close when encoding POP.
3. **Evidence subject (VBC vs. another entity)** — ✅ **Resolved.** Same-codon
   (PM5-type) support is not a CLN line; it belongs to **PFD → Single-amino-acid
   change (MIS)**. The MIS workflow is scoped to the amino-acid residue, so the
   non-VBC allele (ClinVar 525029) is captured as one of that workflow's Evidence
   Items, and the workflow's score rolls up to the VBC's Statement. No per-item
   subject tag is needed — the workflow's scope already declares what it is
   about. (Caveat: the comparator is a VUS, so its weight is likely minimal.)
