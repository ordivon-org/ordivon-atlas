# Cooper R2 Historical-Adjudication Contract v0.1

R2 is deliberately **not** represented as a symmetric prospective experiment menu.

The deposited high-field NMR and crystal-structure artifacts were produced in the historical human follow-up process. Their presence/absence can therefore be correlated with what humans chose to characterize after the autonomous run.

Preserve:

`ArchivedFollowupAvailability != ProspectivelyReachableMeasurementMenu`.

## Pre-reveal commitment

Before owner-side availability lookup, a participant must commit:

1. opaque case ID;
2. exact unresolved claim;
3. requested characterization class;
4. predicted contrast and how it would update the claim.

Only then may the owner check the frozen historical archive for that case.

## Admitted historical source

`NMR-CHARACTERISATION.zip` is source-fenced by md5 `a48f73833a0b35d1a2a7a658d4697797`. Its central directory was inspected without reading spectral values. It contains additional high-field ^1H/^13C NMR for only a subset of MEDCHEM compounds.

The case mapping is owner-side and must not be exposed before a committed request.

Nature also reports CCDC structures `2355749` and `2355750` and states that the unexpected cyclization was confirmed by single-crystal XRD. Exact CCDC-to-opaque-case mapping has **not** yet been independently source-fenced, so XRD is not currently an admitted participant reveal.

## Availability is not evidence

Possible responses are:

- `AVAILABLE` — the requested historical artifact exists and may be revealed;
- `UNAVAILABLE` — no artifact exists in the frozen archive;
- `NOT_ADMITTED` — source/case mapping is not sufficiently fenced.

`UNAVAILABLE` is a missing-follow-up receipt, not a negative scientific result. The benchmark must not let a participant scan availability across all cases as a hidden-label oracle.

Historical R2 can ground a case that was selected from R0/R1. It cannot establish the precision of the R1 selector across cases that never received comparable human follow-up.
