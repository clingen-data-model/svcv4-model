# PVS-v5-MYH7

MYH7 `c.4909G>A` (p.Ala1637Thr) · hypertrophic cardiomyopathy (MONDO:0005045).
First entry of the [Practice Variant Set](../README.md).

Source tab: [v5: MYH7 ↗](https://docs.google.com/spreadsheets/d/1cxgrH3EZKFLBkUvCRbYdm7evP_vSXApB9_UWgeDT6SI/edit?gid=1923098172#gid=1923098172)

## Files

| File | What it is |
|---|---|
| [`source.md`](source.md) | Verbatim transcription of the tab. |
| [`mapping.md`](mapping.md) | Field-by-field mapping of each source value onto the model, with resolved review questions. |
| [`case-CLN_AFF.json`](case-CLN_AFF.json) | The Affected-workflow submission (one proband) — `WorkflowParameters` (`vbc`/`mde`/`moi`/`pop_frq_points`) + a nested `case`. |
| [`classification.json`](classification.json) | The rolled-up `Statement` — POP_FRQ, CLN_AFF, MIS, and SPL evidence lines under one Proposition. |

## What is representative vs. complete

- **`case-CLN_AFF.json`** encodes the **hypertrophic-cardiomyopathy** proband
  (the `SPECIFIC` one). The unspecified-CM (`CONSISTENT`) and dilated-CM
  (`INCONSISTENT`) probands follow the same shape and are summarized inside the
  `CLN_AFF` evidence line of `classification.json`.
- **`POP`** has no Case-model workflow (not in the `Workflow` enum), so its
  inputs live as evidence data in the `POP_FRQ` line rather than a `case-*.json`.
- **`LOC_PHE`** is applicable (probands are counted) but is not scored here — the
  tab lacks the gene-specificity and diagnostic-yield inputs the method needs.
- Scores and classifications are **illustrative**; the arithmetic is CSpec's.

## Validate

These files are covered by CI. `scripts/validate_examples.py` validates
`classification.json` as a `Statement`, and `case-<WORKFLOW>.json` against the
matching `schemas/json/case/<WORKFLOW>.schema.json` plus `WorkflowParameters`:

```sh
uv run python scripts/validate_examples.py
```
