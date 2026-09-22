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
| `exon-relevance-assessment` | tier multipliers · include_mechanism (with/without gene-disease mechanism) |
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
a tier → fraction matrix (SM 6, Figure 2, right box) rather than score bands.

```python
class RelevanceTier:                   # one row of the matrix
    tier: str                          # "All" | "Most" | "Few"
    multiplier: float                  # 1.0 | 0.5 | 0.0

class ExonRelevanceConfig:
    tier_multipliers: list[RelevanceTier]
    include_mechanism: bool            # fold in the gene-disease mechanism cross-reference
    def multiplier_for(tier) -> float
```

| tier | multiplier | exon(s) present in… |
|---|--:|---|
| All | 1.0 | all clinically-relevant transcripts |
| Most | 0.5 | most clinically-relevant transcripts |
| Few | 0.0 | few / no clinically-relevant transcripts |

`MIS_PRD = MIS_PRD_INIT × multiplier`. The four families share the matrix but
differ on `include_mechanism`: baseline **missense** leaves it `False` (its
predictors already capture mechanism), while **null / in-frame / splice** set it
`True`, folding the gene-disease molecular-mechanism cross-reference into this
node. A specialization may re-weight the tiers or flip the toggle.

## In the model

The registry lives in `svcv4_model.assessment`:
`AssessmentType` (the pattern) and `Ruleset` (a pathway node),
with `make_ruleset_id` / `parse_ruleset_id` / `resolve` / `children` helpers. Baseline rulesets are seeded for the whole method tree; specializations override
individual nodes by id.

## Top-level wiring

The whole method is a single root ruleset — `svc:SVCV4:4.0` — that composes two evidence categories — **HOD** (`svc:HOD:4.0`, rolling up POP + CLN + LOC) and **PFD** (`svc:PFD:4.0`, the selected variant-impact outcome across MIS/NUL/CDS/SPL). HOD + PRD roll up to the final `score`/`outcome`. The **top-level classification `Statement`** carries `specifiedBy.id = svc:SVCV4:4.0` (the applied SVCv4 method); each **evidence-line `Statement`** carries `specifiedBy.id` = its own ruleset node (e.g. `svc:MIS_PRD_EXON_REL:4.0`). A specialization swaps the method root's version and/or individual node ids without changing any `methodType`.
