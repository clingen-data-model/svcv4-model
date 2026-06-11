# The Summary Table

Curators and scientists engage with SVCv4 through a **Summary Table**
that organises evidence lines top-down as a three-level hierarchy:

- **Evidence Categories** — broad partitions, e.g. *Human Observational
  Data*, *Variant Impact Data*.
- **Evidence Concepts** — groupings within a Category.
- **Evidence Codes** — the concrete codes a curator works against.

Beneath the Summary Table, **workflows** (defined in CSpec) hang off
each Evidence Code and produce the scores that roll up into the
table.

## Evidence Codes are jumping-off points

Each Evidence Code is the **jumping-off point** for a workflow.

For a given (VBC, MDE) curation:

1. The curator captures Evidence Items under an Evidence Code.
2. Those items are provided to the workflow associated with that
   Evidence Code, defined and evaluated in CSpec under the chosen
   specification version.
3. The workflow produces a score (and optional strength).
4. The result lands back in the Classification Model as an Evidence
   Line — recording the method code, the evidence used, and the score
   produced.

## v3 to v4 code shape

SVCv4 separates evidence *type* from *weight* in its codes:

- **v3** baked strength into the code: `PS4`, `PS4_Moderate`,
  `PS4_Supporting`.
- **v4** uses `<EvidenceCode>_+<points>` form: e.g. `CLN_AFF_+1`,
  `CLN_AFF_+2`.

The Classification Model carries the code as an opaque string on the
Evidence Line (`code` slot). Strength labels travel separately in the
`strength_direction` slot when present.

## See also

- [Evidence Lines & Items](evidence-lines-and-items.md)
- [ClinGen CSpec interop](../cspec-interop.md) — where workflows live.
