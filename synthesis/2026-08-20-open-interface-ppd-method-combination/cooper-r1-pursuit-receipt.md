# Cooper R1 Claim-Relative Pursuit Receipt — 2026-08-20

Status: executable harness PASS.

## Freeze and source boundary

The analysis family was committed before `SUMMARY_NMR.json` reveal at:

`91e0d93decdb66a6b37382f206b59557169d6c6b`

Revealed retained-NMR peak summary:

`sha256:07dbf1347192572c8a935f51433afd413c597518b344eed2fae69092fce24ec3`

Participant-side input is `cooper-r1-summary-blinded-v0.1.json`; the owner key linking opaque IDs to source experiment IDs/published outcomes is absent from the harness and participant payload.

Runtime harness job:

`job-01a01f4a-9fcc-7c91-9612-5ebfd4a63b4c`

## Frozen A1-A4 routing result

Broad `top-3 in >=2 routes` candidate set:

- `case_lumen`
- `case_orbit`
- `case_reed`
- `case_slate`

R0 incumbent-success claim universe (`MS_PASS=true`):

- `case_ember`
- `case_kite`
- `case_lumen`
- `case_nova`
- `case_orbit`
- `case_slate`
- `case_wren`

Claim-relative follow-up set:

- `case_lumen`
- `case_orbit`
- `case_slate`

Therefore:

- complete cohort: 10 cases;
- broad pursuit set: 4/10;
- incumbent successful-product claims: 7;
- claim-relative follow-up: 3/7 = 0.428571;
- claim-relative compression: 4/7 = 0.571429.

## Owner-side known-positive adjudication

The owner-side published-miss key is deliberately not written into participant artifacts. Under that key, the single known published miss is retained by the claim-relative follow-up set and is top-3 in two independent frozen A1-A4 routes.

This supports **known-positive retention 1/1** for the published miss under the frozen routing rule.

It does **not** support a precision claim of 1/3. The other two follow-up candidates are not yet independently adjudicated and must not be called false positives merely because the paper highlighted one anomaly.

## Scientific standing

The result is not exact product identification. It is a bounded pursuit result:

`PolicyExcludedRetainedMeasurement -> ReopenRetainedMeasurement -> BoundedCandidateSet`

with no new physical measurement.

Preserve:

- `PhysicallyMeasured != Retained != PolicyCoupled`;
- `RetainedDataReanalysisCanImprovePursuitRecallWithoutHighPrecision`;
- `PursuitUniverseShouldBeClaimRelative`;
- `BroadAnomalyRanking != ClaimTargetedEscalation`;
- `PursuitCandidate != ExactIdentification`;
- `EncounterGateRecall != EncounterGatePrecision`.

No frozen A1-A4 threshold, binning rule, matching tolerance or rank-combination rule was changed after R1 reveal.
