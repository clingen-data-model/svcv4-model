# Reference Scorer — Classification band (SM 1) — Design

**Goal:** Add `reference_classify(points)` — the reference (NON-AUTHORITATIVE) mapping from a
Bayesian point total to an SVCv4 pathogenicity category (P / LP / VUS / LB / B) plus the VUS
subclass (low / mid / high). CSpec is authoritative. This is **Increment 1** of the
case-aggregation subsystem — a pure function with no dependency on any `ScoreResult`; every later
aggregation increment feeds its summed total into this band.

**Architecture:** New module `src/svcv4_model/scoring/classification.py`. Pure, total function.
NOT re-exported from the root `svcv4_model/__init__.py` (leaks no schema). Imports the existing
`VariantClassification` model enum; defines a new `VusSubclass` enum **in the scoring package**
(so it stays out of the JSON-Schema surface).

**Tech Stack:** Python 3.11+, `uv`, ruff (LL 100), pytest, mkdocs strict.

**Source:** SM 1 (`SM01-glossary.txt` L6–14), "Definitions of Pathogenicity Descriptors" — the
band is stated in-text with exact inclusive/exclusive boundaries (no image gap).

---

## The band (verbatim from SM 1)

| Category | Points | Posterior prob. |
|---|---|---|
| **Benign (B)** | `≤ −4.0` | < 1% |
| **Likely Benign (LB)** | `> −4.0` and `≤ −1.0` | 1% – <10% |
| **VUS-low** | `> −1.0` and `< +2.0` | 10% – <34% |
| **VUS-mid** | `≥ +2.0` and `< +4.0` | 34% – <66% |
| **VUS-high** | `≥ +4.0` and `< +6.0` | 66% – <90% |
| **Likely Pathogenic (LP)** | `≥ +6.0` and `< +10.0` | >90% – <99% |
| **Pathogenic (P)** | `≥ +10.0` | >99% |

The **six boundary values** and their resolved category (the whole point of this increment):

| Point | Category | Rule |
|---|---|---|
| `−4.0` | **B** | B is `≤ −4.0` (inclusive) |
| `−1.0` | **LB** | LB is `≤ −1.0` (inclusive) |
| `+2.0` | **VUS-mid** | VUS-mid is `≥ +2.0` (inclusive) |
| `+4.0` | **VUS-high** | VUS-high is `≥ +4.0` (inclusive) |
| `+6.0` | **LP** | LP is `≥ +6.0` (inclusive) |
| `+10.0` | **P** | P is `≥ +10.0` (inclusive) |

So the benign-side boundaries `−4.0` / `−1.0` fall to the **more-benign** side (B, LB); the
positive boundaries `+2 / +4 / +6 / +10` fall to the **more-pathogenic** side. The two open
boundaries are `−4.0 → −1.0` (LB is the half-open `(−4.0, −1.0]`) and `−1.0 → +2.0` (VUS-low is
`(−1.0, +2.0)`).

## API

```python
class VusSubclass(StrEnum):
    LOW = "VUS-low"
    MID = "VUS-mid"
    HIGH = "VUS-high"


class Classification(NamedTuple):
    category: VariantClassification              # P / LP / VUS / LB / B
    vus_subclass: VusSubclass | None             # set iff category is VUS, else None


def reference_classify(points: float) -> Classification: ...
```

- `NamedTuple` gives both tuple ergonomics (`cat, sub = reference_classify(p)`) and named access
  (`reference_classify(p).category`), matching the option approved during scoping.
- `vus_subclass` is populated **only** when `category is VariantClassification.VUS`; `None` for the
  four non-VUS categories.
- `points` is a plain `float` (the summed Bayesian total a later increment produces). The function
  is **total** — every real number maps to exactly one band; there is no `_ND` / None return (that
  concept belongs to the per-code scorers, not the final band).

## Implementation (single descending cascade)

```python
def reference_classify(points: float) -> Classification:
    if points >= 10.0:
        return Classification(VariantClassification.PATHOGENIC, None)
    if points >= 6.0:
        return Classification(VariantClassification.LIKELY_PATHOGENIC, None)
    if points >= 4.0:
        return Classification(VariantClassification.VUS, VusSubclass.HIGH)
    if points >= 2.0:
        return Classification(VariantClassification.VUS, VusSubclass.MID)
    if points > -1.0:
        return Classification(VariantClassification.VUS, VusSubclass.LOW)
    if points > -4.0:
        return Classification(VariantClassification.LIKELY_BENIGN, None)
    return Classification(VariantClassification.BENIGN, None)
```

Boundary trace (proves the cascade matches the table): `−1.0` fails `> −1.0` → tests `> −4.0` →
**LB** ✓; `−4.0` fails `> −4.0` → **B** ✓; `+1.99…` fails `≥ 2.0`, passes `> −1.0` → **VUS-low**
✓; `+2.0` → **VUS-mid** ✓; `+4.0` → **VUS-high** ✓; `+6.0` → **LP** ✓; `+10.0` → **P** ✓.

## Error handling / edge cases

- Extreme values: `+50 → P`, `−50 → B` (the band is open-ended on both ends — SM 1 P is
  `≥ +10.0`, B is `≤ −4.0`; there is **no clamp here** — a later cross-code increment will settle
  the global-sum-clamp question, which is a separate WG gap and out of scope for this pure band).
- `points` is assumed finite. `float('nan')` would fall through every comparison to the final
  `return BENIGN`; `nan` is not a real score and no scorer produces it, so this is a documented
  non-goal (not guarded here).

## Testing (TDD)

`tests/test_classification_band.py`:

1. **Mid-band representatives** — `+12 → P`; `+8 → LP`; `+5 → (VUS, HIGH)`; `+3 → (VUS, MID)`;
   `0 → (VUS, LOW)`; `−2 → LB`; `−6 → B`.
2. **Every boundary (the core of the increment)** — `−4.0 → B`, `−1.0 → LB`, `+2.0 → (VUS,MID)`,
   `+4.0 → (VUS,HIGH)`, `+6.0 → LP`, `+10.0 → P`; and the across-boundary neighbours `−4.0+ε → LB`,
   `−1.0+ε → (VUS,LOW)`, `+1.99 → (VUS,LOW)`, `+3.99 → (VUS,MID)`, `+5.99 → (VUS,HIGH)`,
   `+9.99 → LP` (use `9.999` etc.).
3. **VUS subclass discipline** — every VUS result has a non-None subclass; every non-VUS result
   has `vus_subclass is None`.
4. **NamedTuple ergonomics** — `cat, sub = reference_classify(3.0)` unpacks; `.category` /
   `.vus_subclass` accessors work.

## Docs

- `docs/reference/scoring.md`: add a short "Classification band" section — `reference_classify`
  maps a summed point total to the SM 1 category + VUS subclass (`≤−4 B / (−4,−1] LB /
  (−1,+2) VUS-low / [2,4) VUS-mid / [4,6) VUS-high / [6,10) LP / ≥10 P`); note it is the capstone
  the aggregation increments feed, and that the global-sum clamp is a separate open question.
- `docs/reference/known-gaps.md`: add a Working-Group-follow-up row — the **global sum clamp** is
  unspecified/contradictory (SM 1 makes P open-ended `≥+10`, but the GA4GH JSON `scale` caps at
  `10.0` / `−8.0`); `reference_classify` itself does not clamp (faithful to SM 1); the clamp
  decision belongs to the future cross-code-combination increment.

## Quality gates

`uv run pytest -q`; `uv run ruff check .` (LL 100); drift gate (`export_schemas.py` then
`git diff --quiet -- schemas/json docs/workflows/case-model.md` — must stay clean; `VusSubclass`
lives in the non-re-exported scoring package); `uv run mkdocs build --strict`; no scorer schema
leaked; clean tree.

## Non-goals / deferred

- **Any summing** (POP/LOC subtotals, CLN cross-proband, cross-code combination) — later
  increments; this function only maps an already-summed total.
- **The global-sum clamp** — a WG gap, settled in the cross-code increment.
- **`validate_case`** applicability enforcement — a separate increment.
