# Variant-impact pathways

The [PFD variant-impact router](specialization.md#the-configuration-model) selects
one of four families — **MIS · NUL · CDS · SPL** — from the VBC's molecular
consequence. But a family is never reached directly: the VBC enters through one of
**ten variant-type pathways**, each of which branches internally before it resolves
to a family. **That pathway — the entry type _and_ the branch taken — is what
shapes the subcodes**, not the family alone.

This matters most for `NUL` and especially `CDS`, which are **multi-origin**: a
`CDS` total can come from a rescue-Met nonsense, a no-NMD frameshift, an in-frame
indel, a no-NSD stop-lost extension, a potential alt-start, an in-frame exon
deletion, or a tandem exon duplication — each with different biology. So
subcodes that depend on the variant's nature — the predictive initial points, and
above all the **informative variants** (`x_INF`, SM 19) — must be resolved **per
pathway**, not with a single family-level rule.

!!! note "Scope"

    This page maps the pathways and their branches (from SM 6, 8–16) as the
    foundation for per-pathway subcode design. Family assignments per branch are
    read from the `svcv4_model` variant-type modules; the per-pathway **INF** rules
    are noted where the SM text implies them and flagged **TBD** where a
    branch-specific diagram is still needed. Scoring is illustrative; CSpec is
    authoritative.

## The shared pipeline

Every family runs the same skeleton; the pathway parameterises each step:

```
x_PRD_INIT (initial points)  ─×─  SM 18 mechanism/exon matrix  ──▶  x_PRD
        +  x_FXN (functional, SM 20)   ──cap──▶  x_PRD_FXN (combination cap)
        +  x_INF (informative variants, SM 19)   ──▶  x_ parent total (capped)
```

- `x_PRD_INIT` — the initial predictive points; the **spectrum** differs per
  pathway (in-silico predictor, protein-impact, alt-start, mechanism, splice).
- SM 18 matrix — exon relevance × (for null/in-frame/splice) the LOF mechanism
  classification; applied to **positive** points only.
- `x_INF` — **the SM 19 informative-variants rules, which are variant-type
  dependent** (see [below](#informative-variants-are-pathway-shaped)).

## The map

| entry type (SM) | consequence | family | internal branches | informative keys on |
|---|---|---|---|---|
| **Missense** (SM 6) | `MISSENSE` | **MIS** *(+ SPL sub-path)* | in-silico predictor; MIS-vs-SPL compare | same/distinct **AA** + **Grantham** ✅ |
| **Canonical splice** (SM 11) | `SPLICE` | **SPL** | 5 splice paths: NMD / FS-no-NMD / no-FS / uncertain / unlikely | similar **splice effect** — TBD |
| **Intronic / synonymous** (SM 12) | `INTRONIC` · `SYNONYMOUS` | **SPL** | same 5 splice paths (field-identical to SM 11) | similar **splice effect** — TBD |
| **Nonsense** (SM 8) | `NONSENSE` | **NUL** \| **CDS** | `NMD_NO_RESCUE`→NUL · `NMD_WITH_RESCUE`→CDS · `NO_NMD`→CDS | **same exon** premature termination — TBD |
| **Frameshift** (SM 9) | `FRAMESHIFT` | **NUL** \| **CDS** | +`NON_STOP_DECAY`→NUL · +`PROTEIN_EXTENSION`→CDS (5 total) | same exon / similar consequence — TBD |
| **In-frame indel** (SM 10) | `INFRAME_INDEL` | **CDS** | `SIMPLE_SEQUENCE_REPEAT` · `NON_REPEAT` | in-frame length change — TBD |
| **Start-lost** (SM 15) | `START_LOST` | **NUL** \| **CDS** | `NO_ALT_START`→NUL · `ALT_START_UNPROVEN`→CDS · `ALT_START_FUNCTIONAL`→CDS *(fixed −1, benign-only)* | branch-restricted — TBD |
| **Stop-lost** (SM 16) | `STOP_LOST` | **NUL** \| **CDS** | `NSD_PREDICTED`→NUL · `NO_NSD`→CDS | extension length / similar variants — TBD |
| **Exon deletion** (SM 13) | `EXON_DELETION` | **NUL** \| **CDS** | `WHOLE_GENE`→NUL *(mechanism-only)* · `SUBGENIC_NMD`→NUL · `SUBGENIC_NO_NMD`→CDS · start-codon ×3 (alt-start logic) | **whole-gene deletion** (distinct breakpoints ok) — TBD |
| **Exon duplication** (SM 14) | `EXON_DUPLICATION` | **NUL** \| **CDS** | `TANDEM_*` / `GAIN_*` × NMD × terminal-exon (6) · `WHOLE_GENE_NA`→NA | **tandem duplication** — TBD |

## Families in detail

### MIS — missense (SM 6)

The only entry into `MIS`. Amino-acid effect path (`MIS_PRD` = in-silico predictor
× exon relevance) + `MIS_FXN` + `MIS_INF`. A splice sub-path (`SPL_`) is assessed in
parallel and the higher of MIS-vs-SPL is applied. `MIS_INF` is fully modeled — the
[five-branch diagram](specialization.md#informative-variants) keyed on same/distinct
amino-acid change and the Grantham relation to the VBC.

### SPL — splice (SM 11, SM 12)

Two entries, **field-identical**: canonical `±1,2` GT/AG donor/acceptor variants
(SM 11) and intronic/synonymous variants assessed for splicing potential (SM 12).
Both resolve through the same five splice-prediction paths (`NMD_PREDICTED`,
`FRAMESHIFT_NO_NMD`, `SPLICE_NO_FRAMESHIFT`, `UNCERTAIN`, `UNLIKELY`) into
`SPL_PRD` → `SPL_SPA` (splice assay) → `SPL_FXN` → `SPL_INF`. Because both entries
share the pathway, they can share a single `SPL_INF` rule set.

### NUL / CDS — seven branch-resolved entries

`NUL` (loss of function) and `CDS` (coding-sequence change / altered protein) are
**not entered directly** — seven variant types branch into one or the other:

| entry | → NUL branch(es) | → CDS branch(es) |
|---|---|---|
| Nonsense (SM 8) | `NMD_NO_RESCUE` | `NMD_WITH_RESCUE`, `NO_NMD` |
| Frameshift (SM 9) | `NMD_NO_RESCUE`, `NON_STOP_DECAY` | `NMD_WITH_RESCUE`, `NO_NMD`, `PROTEIN_EXTENSION` |
| In-frame indel (SM 10) | — | `SIMPLE_SEQUENCE_REPEAT`, `NON_REPEAT` |
| Start-lost (SM 15) | `NO_ALT_START` | `ALT_START_UNPROVEN`, `ALT_START_FUNCTIONAL` |
| Stop-lost (SM 16) | `NSD_PREDICTED` | `NO_NSD` |
| Exon deletion (SM 13) | `WHOLE_GENE`, `SUBGENIC_NMD`, `START_CODON_NO_ALT_START` | `SUBGENIC_NO_NMD`, `START_CODON_ALT_START_*` |
| Exon duplication (SM 14) | `TANDEM_NMD`, `GAIN_NMD` | `TANDEM_NO_NMD`, `TANDEM_TERMINAL_EXON`, `GAIN_NO_NMD`, `GAIN_TERMINAL_EXON` |

(Branch→family assignments are read from the variant-type module docstrings and
follow the NMD / alt-start / non-stop-decay logic; they should be confirmed
against SM 8–16.)

## Informative variants are pathway-shaped

This is the crux. `x_INF` (SM 19) is where the pathway's characteristics most
directly change the rule for *what counts as an informative variant*:

| family | informative-variant characteristic | status |
|---|---|---|
| `MIS_INF` | same vs distinct amino-acid change + Grantham(inf) ≤/≥ VBC | ✅ **modeled** (five-branch path config) |
| `SPL_INF` | similar splice effect (a nearby splice-site change with the same predicted consequence) | ⏳ provisional generic paths |
| `NUL_INF` | a distinct P/LP LoF variant in the **same exon** — with the SM 19 *distinct-evidence* caveat (it must not rest on the same `x_PRD`-only evidence as the VBC) | ⏳ provisional generic paths |
| `CDS_INF` | **branch-dependent** — differs across in-frame indel, rescue-Met, extension, alt-start, tandem-dup origins | ⏳ provisional generic paths |

Notes that already fall out of the pathway map:

- **`CDS_INF` cannot be one rule.** Its informative characteristics depend on how
  the VBC reached `CDS`; the config will likely carry **branch-scoped path sets**,
  reusing schedules where branches agree.
- **Start-lost `ALT_START_FUNCTIONAL`** awards a fixed −1 and **restricts INF (and
  FXN) to benignity** — a pathway that turns off part of the shared pipeline.
- The two **splice** entries (SM 11, SM 12) share a pathway, so one `SPL_INF` rule
  set serves both.

## Status and next steps

**Modeled today:** the PFD router + family tree; the `MIS` configs (`MIS_PRD_INIT_INSILICO`,
`MIS_PRD_EXON_REL`, and the five-branch `MIS_INF`). `NUL_INF` / `CDS_INF` / `SPL_INF`
carry **provisional generic** P/LP + B/LB paths — explicitly placeholders.

**Next:** capture each pathway's own `x_INF` rules (as the missense diagram was
supplied), branch-scoped where needed; then extend the same treatment to the
`x_PRD_INIT` spectra. This page is the reference those configs are built against.
