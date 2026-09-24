# Specialization & the assessment registry

Every scored branch of a workflow is an **assessment**. Its stable name is the
`methodType` carried on the `specifiedBy` (`Method`) of an evidence-line
`Statement`. The baseline SVCv4 framework registers each assessment once, with a
baseline configuration; a **specialization** (for a gene, VCEP, or disease area)
reuses the *same* `methodType` but registers its own **configuration** under a
distinct, namespaced id.

## The two identifiers

| Field | Purpose | Example |
|---|---|---|
| `specifiedBy.methodType` | *What kind of rule this is* — stable across baseline and every specialization; this is what makes results **comparable**. | `insilico-predictor-assessment` |
| `specifiedBy.id` | *Which configured ruleset actually ran* — namespaced + versioned; this is what makes results **reproducible**. | `svc:MIS_PRD_INIT_INSILICO:4.0` |

The id scheme is **`svc:<CODE>:<version>` (baseline) or `svc-<scope>:<CODE>:<version>`**. Scope is `baseline`
or a specialization scope (e.g. `gene-MYH7`, `vcep-cardiomyopathy`). All scopes
live under the `svc` registry umbrella.

## Worked example — same evidence, two configurations

A missense VBC in *MYH7* with an in-silico predictor **raw score of 0.91**. The
subcode is the tool-agnostic `MIS_PRD_INIT_INSILICO` — the predictor tool (REVEL,
here) is selected in the ruleset's params, not baked into the code. The baseline
calibration reaches `+4.0` only at `≥ 0.932`, so 0.91 lands in the next band down;
the *MYH7* specialization was re-calibrated for the gene and reaches `+4.0` at
`≥ 0.90`. Same evidence item, same assessment — different configured threshold,
different score.

=== "Baseline"

    ```jsonc
    {
      "type": "Statement",
      "code": "MIS_PRD_INIT_INSILICO",
      "specifiedBy": {
        "id": "svc:MIS_PRD_INIT_INSILICO:4.0",
        "methodType": "insilico-predictor-assessment",
        "version": "4.0"
      },
      "score": 3.0,
      "direction": "supports",
      "outcome": "MIS_PRD_INIT_INSILICO_+3",
      "hasEvidenceItems": [
        { "type": "DataItem", "subtype": "computational_prediction",
          "value": { "predictor": "REVEL", "raw_score": 0.91 } }
      ]
    }
    ```

=== "MYH7 specialization"

    ```jsonc
    {
      "type": "Statement",
      "code": "MIS_PRD_INIT_INSILICO",
      "specifiedBy": {
        "id": "svc-gene-MYH7:MIS_PRD_INIT_INSILICO:4.0",
        "methodType": "insilico-predictor-assessment",
        "version": "4.0"
      },
      "score": 4.0,
      "direction": "supports",
      "outcome": "MIS_PRD_INIT_INSILICO_+4",
      "hasEvidenceItems": [
        { "type": "DataItem", "subtype": "computational_prediction",
          "value": { "predictor": "REVEL(MYH7-recalibrated)", "raw_score": 0.91 } }
      ]
    }
    ```

Both lines share `methodType` (a reader can compare them as the same kind of
assessment); their `specifiedBy.id` differs, and each id resolves in the registry
to the exact configuration — including the calibration thresholds — that produced
the score.

## What a specialization may reconfigure

The registry records, per assessment type, which **parameters** a configuration
may set. A specialization overrides those parameters within the compliance limits
of the SVCv4 framework; it does **not** mint new codes. Examples:

| Assessment (`methodType`) | Reconfigurable parameters |
|---|---|
| `insilico-predictor-assessment` | selectable tools · per-tool bands/points |
| `exon-relevance-assessment` | tier multipliers · only_positive · mechanism-classification types & weights |
| `informative-variants-assessment` | point values · relatedness rule · added granularity |
| `population-frequency-assessment` | fold thresholds & point tiers |

## The configuration model

A code is only a name; the numbers behind it live in the ruleset's typed
**configuration** (`svcv4_model.config`). Each assessment family has its own
config shape — an initial-points code carries score→points bands, an adjuster
carries a multiplier matrix — but all share the same rule: the baseline stores
the values, a specialization overrides them in its own namespace.

### In-silico predictor initial points

The model is a dictionary keyed by predictor tool — each an ordered list of
`(points, score-interval)` **bands**, transcribed from SM 6, Figure 2. A code
behaves like a small **API**: `evaluate(tool, score)` takes a configured tool and
a numeric score and returns the one point value of the band the score lands in.
The *conditions* are enforced — an unconfigured tool raises `UnknownTool`, and a
score outside the tool's covered domain raises `ScoreOutOfRange`.

```python
class ScoreBand:                       # one calibration row
    points: float
    min | max: float | None            # None = unbounded (−∞ / +∞)
    min_incl | max_incl: bool          # default [min, max): lower-incl, upper-excl

class InsilicoPredictorConfig:         # the configuration behind the code
    selectable_tools: list[str]        # menu the analyst may choose from
    per_tool_bands: dict[str, list[ScoreBand]]
    selected_tool: str | None          # the choice on an instance
    def evaluate(tool, score) -> float  # UnknownTool / ScoreOutOfRange
    def domain(tool) -> (min, max)      # the covered range
```

Each tool's bands are **contiguous and cover 100%** of its `[min, max]` domain —
adjacent bands meet exactly (a boundary value belongs to the higher band), with
no gaps or overlaps. This is checked on construction, so a specialization that
leaves a hole is rejected. The baseline `svc:MIS_PRD_INIT_INSILICO:4.0` carries
all seven ClinGen-approved tools (four reach `−3.0`, three reach `−4.0`; ESM1b's
scale is inverted, so its intervals run the other way). For example REVEL, whose
bands tile the whole real line:

| points | interval | points | interval |
|--:|---|--:|---|
| −4 | [−∞, 0.017) | +1 | [0.644, 0.773) |
| −3 | [0.017, 0.053) | +2 | [0.773, 0.879) |
| −2 | [0.053, 0.184) | +3 | [0.879, 0.932) |
| −1 | [0.184, 0.291) | +4 | [0.932, +∞) |
| 0 | [0.291, 0.644) | | |

A specialization stores the **same** shape under its namespaced id, overriding
only what it needs — e.g. `svc-gene-MYH7:MIS_PRD_INIT_INSILICO:4.0` narrows
`selectable_tools` to `["REVEL"]`, pins `selected_tool`, and re-thresholds
REVEL's bands so `+4.0` begins at `≥ 0.900`. The config validates the same way
in either namespace, so a reader can diff two configurations field-for-field.

### Exon relevance

The `*_PRD_EXON_REL` codes output a **multiplier**, not points, so their model is
a tier → fraction matrix (SM 6, Figure 2, right box), optionally combined with a
gene-disease **mechanism-classification** weight. Like the predictor code it is an
API — `evaluate` takes the initial points plus the tier (and, when a mechanism
type is configured, the mechanism type + classification) and returns the factor.

```python
class RelevanceTier:                   # one row of the matrix
    tier: str                          # "All" | "Most" | "Few"
    multiplier: float                  # 1.0 | 0.5 | 0.0

class MechanismBand:                    # one mechanism-classification TYPE (e.g. "LOF")
    mechanism_type: str
    classifications: list[MechanismClassification]   # each a value + 0–100% weight

class ExonRelevanceConfig:
    tier_multipliers: list[RelevanceTier]
    only_positive: bool                # weight positive initial points only
    mechanism_bands: list[MechanismBand]
    def evaluate(initial_points, tier=None, mechanism_type=None, mechanism_class=None) -> float
```

| tier | multiplier | exon(s) present in… |
|---|--:|---|
| All | 1.0 | all clinically-relevant transcripts |
| Most | 0.5 | most clinically-relevant transcripts |
| Few | 0.0 | few / no clinically-relevant transcripts |

`evaluate` applies these conditions in order:

- **`only_positive`** — if set and `initial_points ≤ 0`, return `1.0` (no impact:
  benign/neutral points pass through untouched); no tier or mechanism needed.
- otherwise the **tier** is required and gives the tier fraction;
- if a **mechanism type** is configured, the `mechanism_type` + `mechanism_class`
  are required and the result is `tier_fraction × mechanism_weight`.

Each subcode also **introspects** its valid inputs — `tiers()`,
`mechanism_types()`, and `classifications(mechanism_type)` — so a caller can
discover the allowed tiers and the allowed classification values for a type.

The four families share the tier matrix. Baseline **missense** configures **no
mechanism** (its predictors already capture mechanism); **null / in-frame /
splice** each configure a **`LOF`** mechanism type (the gene-disease
molecular-mechanism cross-reference), whose classifications are **Established**
(100%), **Likely** (50%), **Suspected** (25%), and **Uncertain or Not LOF** (0%).

A mechanism band is a **reusable component**: define it once and pass it into any
number of exon-relevance configs (the null/in-frame/splice families share one
`LOF` band today), or pass a different band to a family whose weights must
differ. A specialization may re-weight the tiers, set `only_positive`, or add /
re-weight mechanism types.

```python
LOF = mechanism_band("LOF", ("Established", 1.0), ("Likely", 0.5),
                     ("Suspected", 0.25), ("Uncertain or Not LOF", 0.0))
cfg = ExonRelevanceConfig(tier_multipliers=..., mechanism_bands=[LOF])
```

### Informative variants

The `*_INF` codes (SM 19) score by **scoring groups** — each variant joins the
first group whose criteria it meets, and each group scores `count × points` plus a
one-time *definitive* bonus:

```python
class InfGroup:                         # one scoring group
    name: str
    clinical: significant | not_significant | any    # P/LP vs B/LB
    aa: same | distinct | any                        # amino-acid change vs the VBC
    grantham: non_negative | positive | any          # sign of VBC−INF (distinct-AA)
    points_per_variant · definitive_bonus · definitive_classification  # Path or Benign

class InformativeVariantsConfig:
    groups: list[InfGroup]              # ← per-family, ordered (the modifiable axis)
    cap_min = -8.0; cap_max = 8.0; min_star_rating = 3   # expert panel / 3-star
    motif_points = 0.0                                   # SM 7 motif award (MIS = 2.0)
    def evaluate(variants, vbc_grantham=None, motif_qualifying=False) -> float | None
    def classify(variant, vbc_grantham=None) -> str | None
```

An informative variant is a **distinct, ranked-classified variant at the same
codon** as the VBC but a different nucleotide change (equivalent transcript). Each
supplies its `classification`, `aa` (same/distinct), raw `grantham` score, and
`star_rating`; the VBC's Grantham is passed to `evaluate` as `vbc_grantham`.
Duplicate classifications of one variant collapse to the highest-ranked, most
clinically-significant call. **No qualifying variants → `evaluate` returns `None`
and the code reads `*_INF_ND`.**

**Missense** (`MIS_INF`) has the SM 19 five-group model:

| group | direction | pts/variant | definitive bonus |
|---|---|--:|--:|
| a) clin-sig, same AA | P/LP | +2 | +2 (Path) |
| b) clin-sig, distinct AA, VBC−INF ≥ 0 | P/LP | +1 | +1 (Path) |
| c) not-sig, distinct AA, VBC−INF > 0 | B/LB | −1 | −1 (Benign) |
| d) not-sig, same AA | B/LB | −2 | −2 (Benign) |
| e) all other | — | 0 | 0 |

Each group scores `count × points_per_variant`, plus its `definitive_bonus` once if
it holds at least one **definitive** (Path / Benign) call; group sums add, cap ±8.

**Motif variants** (SM 7): a VBC in a robustly-defined deleterious motif — the
Gly-X-Y motif of collagen triple-helical domains, or functional Cys/His in a C2H2
DNA-binding domain — awards `motif_points` (MIS = **+2**) **once** via
`evaluate(..., motif_qualifying=True)`, acting as a virtual group-b Pathogenic
variant. It applies only when there are **no** clinically-significant informative
variants (it substitutes for a missing one) and is **suppressed by any benign**
informative variant at the codon.

`NUL_INF` / `CDS_INF` / `SPL_INF` carry **provisional** clinically-significant /
not-significant groups (no motif) pending each pathway's own rules (see
[variant-impact pathways](variant-impact-pathways.md)). A specialization re-weights
a group, sets `motif_points`, or swaps in its own groups.

## In the model

The registry lives in `svcv4_model.assessment`:
`AssessmentType` (the pattern) and `Ruleset` (a pathway node),
with `make_ruleset_id` / `parse_ruleset_id` / `resolve` / `children` helpers. Baseline rulesets are seeded for the whole method tree; specializations override
individual nodes by id.

## Top-level wiring

The whole method is a single root ruleset — `svc:SVCV4:4.0` — that composes two evidence categories — **HOD** (`svc:HOD:4.0`, rolling up POP + CLN + LOC) and **PFD** (`svc:PFD:4.0`, the selected variant-impact outcome across MIS/NUL/CDS/SPL). HOD + PRD roll up to the final `score`/`outcome`. The **top-level classification `Statement`** carries `specifiedBy.id = svc:SVCV4:4.0` (the applied SVCv4 method); each **evidence-line `Statement`** carries `specifiedBy.id` = its own ruleset node (e.g. `svc:MIS_PRD_EXON_REL:4.0`). A specialization swaps the method root's version and/or individual node ids without changing any `methodType`.
