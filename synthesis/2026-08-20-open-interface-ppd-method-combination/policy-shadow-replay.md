# Policy-Shadow Replay — owner-local PPD method

This is an executable search pattern, not a new generic PPD ontology entry.

## Setup

At historical episode `t`, Reality interaction produced measurements:

`O_t = (P_t, S_t)`

where:

- `P_t` = channels/features actually coupled to the decision policy;
- `S_t` = measurements physically acquired and retained but excluded from the policy.

The historical action/standing is:

`a_0 = pi_0(P_t)`.

A source-fenced replay first freezes a bounded shadow-analysis/replay rule `R` before hidden outcome reveal, then computes:

`a_1 = R(P_t, S_t)`.

Hidden/held-out Reality adjudicates whether `a_1` improves claim challenge, pursuit routing or later validation relative to `a_0`.

## What it discriminates

A positive shadow replay establishes that additional Reality measurement was not required for the scoped historical distinction:

`NeedNewMeasurement != NeedNewPolicyCoupling`.

It can route repair toward representation/search/pursuit/policy coupling before new physical acquisition.

A negative replay does **not** prove a new modality is necessary; it only excludes the frozen replay family over the retained shadow channels.

## Required receipts

1. evidence that `S_t` was physically measured before the historical decision;
2. evidence that `S_t` was retained;
3. evidence that `S_t` was not policy-coupled for the target decision;
4. pre-reveal freeze of replay family/thresholds;
5. hidden/held-out claim or outcome adjudication;
6. false-escalation burden on ordinary episodes;
7. action/resource cost kept separate from epistemic closure.

## Cooper calibration

Late-stage medicinal-chemistry diversification supplies a direct case:

- UPLC-MS was policy-coupled;
- low-field NMR was acquired and retained for future reference but explicitly excluded from pass/fail decisions;
- the published unexpected cyclization passed the UPLC-MS policy but was later recognized by human NMR inspection;
- a pre-frozen model-free retained-NMR replay compressed seven incumbent-success claims to three follow-up candidates while retaining the single published miss.

Thus the useful standing is:

`PolicyExcludedRetainedMeasurement -> ReopenShadowChannel -> BoundedPursuitSet`.

## Guards

- `PhysicallyMeasured != Retained != PolicyCoupled`.
- `ShadowReplayPositive != ProspectiveOnlinePolicyBenefit`: replay may ignore latency, action feedback, contemporaneous availability and intervention-induced state changes.
- `ReplayFailure != NewSensorNecessary`: only the frozen replay family was tested.
- `PursuitCandidate != ExactIdentification`.
- `KnownPositiveRetention != Precision`: unadjudicated follow-up candidates cannot be called false positives.
- If historical actions altered later observations, replay is not a causal substitute for re-running the closed loop.

## PPD role

Policy-Shadow Replay changes the **policy-coupling coordinate** of the epistemic configuration while holding the historical physical measurement cut fixed. It should be considered before bespoke new acquisition whenever source-fenced shadow measurements already exist.
