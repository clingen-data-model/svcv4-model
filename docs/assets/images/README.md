# Image manifest

Graphics used by the docs site. To update a figure, replace the file in place
(keep the filename); pages reference these stable names.

| File | Depicts | Used on |
|------|---------|---------|
| `summary-table.png` | The full SVCv4 Summary Table (Evidence Category → Concept → Code → Workflow → Score) | `overview/alignment.md`, `workflows/index.md` |
| `hod-workflows.png` | Human Observational Data section of the Summary Table, with its workflows (POP, CLN, LOC) | `workflows/human-observational-data.md` |
| `variant-impact-workflows.png` | Variant Impact (Predictive & Functional) section of the Summary Table, with its workflows (MIS, CDS, NUL, SPL) | `workflows/variant-impact.md` |

Source graphics are authored by the SVCv4 Standards group and kept locally
(under the git-ignored `tmp/`); only the published copies above are committed.

Two conceptual diagrams are authored **in-repo as Mermaid** rather than images,
so they stay editable and version-controlled:

- the **data-model diagram** (Statement → Proposition / Final Score → Evidence
  Line(s) → Evidence Item(s)) on `getting-started/assertion-framework.md`, and
- the **points-based classification rubric** rendered as a table on `index.md`.
