# PVS-PKP2 — mapping

How [`source.md`](source.md) maps onto the model. Illustrative; scoring is CSpec's.

## Anchor (SPOQ)

- **VBC:** PKP2 `c.1481C>A` (p.Ser494Ter) in an alternate transcript (deep intronic
  `c.1379-2006C>A` in MANE Select), CAID CA384368604 → `Proposition.subject`.
- **MDE:** arrhythmogenic right ventricular cardiomyopathy, MONDO:0016587.
- **MOI:** AD. LoF is an established mechanism.

## Workflows

| Workflow | Why | Encoded |
|---|---|---|
| *(none countable)* | The single proband has only **suspected** ARVC (no clinical diagnosis), so is **not** counted under CLN_AFF — and therefore not under LOC_PHE either. | — |

No `case-*.json`: there is no countable clinical case.

## Evidence → lines (`classification.json`)

- `POP_FRQ` — prevalence 1/1000, penetrance 0.30 → `pop_frq_points 0`.
- `NUL` — nonsense `p.Ser494Ter`, but in an exon **absent from the clinically
  relevant transcript**; LoF variants there are not classified P/LP, so LoF weight
  is uncertain.

Net: a genuine **VUS** driven by transcript context, with no clinical support.

## Open questions

1. Is transcript-context handled as a `NUL`/`CDS` line, or a separate concept?
