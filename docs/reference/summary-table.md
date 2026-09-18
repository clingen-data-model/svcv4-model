# The Summary Table

Curators and scientists engage with SVCv4 through a **Summary Table**
that organises evidence lines top-down, from Evidence Category through
Evidence Concept and Evidence Code to the workflows and scores that roll
up into the table — see the [Workflows overview](../workflows/index.md)
for the full hierarchy.

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

## SVCv4 code shape

SVCv4 separates evidence *type* from *weight* in its codes: a code names the
evidence **type** and a suffix gives the **points** — `<EvidenceCode>_+<points>`
form, e.g. `CLN_AFF_+1`, `CLN_AFF_+2` — rather than baking the strength into the
code itself.

The Classification Model carries the code as an opaque string on the
Evidence Line (`code` slot). Strength labels travel separately in the
`strength_direction` slot when present.

## See also

- [Collecting the evidence](../collecting/index.md)
- [ClinGen CSpec interop](cspec-interop.md) — where workflows live.
