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

SVCv4 separates evidence *type* from *weight*: a code names the evidence
**type** (e.g. `CLN_AFF`, `MIS`, `SPL`) and does **not** bake the points into the
code itself. The points a line carries are recorded separately as the Evidence
Line's `score`, so the same code can carry different scores across curations.

The Classification Model carries the code as an opaque string on the
Evidence Line (`code` slot), the numeric weight in `score`, and any qualitative
label split across the `strength` and `direction` slots when present.

## See also

- [Collecting the evidence](../collecting/index.md)
