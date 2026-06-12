# Image manifest

Graphics used by the docs site. To update a figure, replace the file in place
(keep the filename); pages reference these stable names.

| File | Depicts | Used on |
|------|---------|---------|
| `summary-table.png` | The full SVCv4 Summary Table (Evidence Category → Concept → Code → Workflow → Score) | `overview/alignment.md`, `workflows/index.md` |
| `hod-workflows.png` | Human Observational Data section of the Summary Table, with its workflows (POP, CLN, LOC) | `workflows/hod/index.md` |
| `variant-impact-workflows.png` | Variant Impact / Predictive & Functional Data section of the Summary Table, with its workflows (MIS, CDS, NUL, SPL) | `workflows/pfd/index.md` |
| `points-bands.png` | The SVCv4 points-based classification bands (B / LB / VUS Low-Mid-High / LP / P score ranges) | `index.md` |

Source graphics are authored by the SVCv4 Standards group and kept locally
(under the git-ignored `tmp/`); only the published copies above are committed.

The **data-model diagram** (Statement → Proposition / Final Score → Evidence
Line(s) → Evidence Item(s)) on `getting-started/assertion-framework.md` is
authored **in-repo as Mermaid**, so it stays editable and version-controlled.
