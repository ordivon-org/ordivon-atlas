# Interlocus Engineering Consequences and Action Boundary

## 1. Practical audit result: mostly no refactor

Read-only consumption across Runtime, Workstation/egress, Finance, Harness and Research System found that current owner implementations already preserve many Interlocus distinctions:

- configured identity can persist while current usability is UNKNOWN/UNAVAILABLE;
- Finance can fail closed on `EGRESS_NOT_CURRENT` rather than treating configured egress as usable;
- Runtime execution success does not imply domain semantic completion;
- Harness route membership/admission is use-contract-relative;
- Host `READY` continuity does not imply current action admission.

Result:

`InterlocusReframing != TheoryDrivenRefactorMandate`.

The first engineering value was a **diagnostic/warrant grammar**, not a new state store.

## 2. Capability Path Explanation v0

A cross-domain contract survived Finance, Research-System and Harness fixtures plus stale/conflict/rebinding attacks.

Minimal structure:

- `TargetUseRef`;
- `SourceFactRef[]` with owner-native immutable source/currentness fences;
- `JustificationEdge[]` with exact relation-contract authority;
- structural `ExplanationAssessment` (`EXPLAINED / INCOMPLETE / CONFLICTED / INVALIDATED`).

The internal shape is a well-founded **warrant DAG**, not necessarily a linear path and not the domain topology graph.

Key rules:

- native standing remains owner-specific; do not normalize everything into one global UP/DOWN enum;
- source summaries are display-only; authority stays with exact refs/fences;
- branch-local failure is not automatically target failure;
- blocker promotion requires necessity/choice/quantifier witness;
- stale source/policy fences invalidate present-tense explanation without rewriting historical facts;
- unresolved conflict remains conflict;
- observed blockers are not a minimal repair set without closure.

The reusable invariant is:

> trace the exact warranted route from owner facts to a target-relative consumer use decision without minting new truth.

## 3. Explanation is strictly weaker than repair

The dogfood established:

`ObservedFailure != TargetBlocker != RequiredConditionChange != NecessaryIntervention != SufficientIntervention != MinimalRepair != PreferredAction`.

A good diagnosis may legitimately leave repair `UNDERDETERMINED`.

## 4. Counterfactual Repair Explanation v0

Repair reasoning was separated into a stronger read-only contract.

Critical type separation:

`ActualSourceFact != CounterfactualEffect != ActualPostExecutionFact`.

A hypothetical effect imported from an intervention model must never be presented as a current fact.

Repair claims are target-preserving:

`TargetRevision != TargetRepair`.

Weakening/changing the target to make an intervention succeed is renegotiation/migration unless target continuity/equivalence is explicitly witnessed.

Five cut-relative closure surfaces were retained:

- R — realization/alternative closure;
- E — intervention-effect outcome closure;
- D — post-intervention dependency/currentness closure;
- C — continuation closure for persistence claims;
- I — intervention-universe/comparison closure for necessity/minimality.

The model-relative modalities include:

- `MAY_RESTORE_UNDER_EFFECT_CONTRACT`;
- `SUFFICIENT_AT_POSTSTATE_UNDER_EFFECT_CONTRACT`;
- `ROBUST_OVER_CONTINUATION_UNDER_EFFECT_CONTRACT`;
- stronger necessity/minimality claims only when the required universe/order closure exists.

Multi-action plans require joint plan/order/effect or independence/composition witnesses. Individual intervention claims cannot be freely composed.

## 5. Counterfactual warrant is not execution

The required staged architecture is:

`Diagnose -> Capability Path Explanation -> Counterfactual Repair Explanation -> external action/admission -> execution -> observe effects -> refresh source facts -> fresh Capability Path Explanation/current standing`.

Important non-collapses:

`CounterfactualSufficiency != ActionPermission`.

`CounterfactualSufficiency != ExecutionOccurrence`.

`ExecutionSuccess != ActualEffect`.

`ActualEffect != RestoredStanding`.

A repair warrant valid at `t0` does not automatically remain executable at `t1`. Race-safe execution requires owner-native revision guard / lease / compare-and-act / transaction or equivalent precondition fencing where the action contract demands it.

## 6. Consumer-value dogfood narrowed the practical claim

A fixed 14-claim rubric across Finance/Research/Harness showed that simple owner-native facts and direct consumer verdicts often need no Interlocus projection.

The supported practical value is **not** primarily fewer source reads. Authoritative owner facts still need to be consulted.

The stronger result is:

> reduce unconstrained semantic joining after the source reads.

A bounded caller-supplied validator/projector turned this into a mechanically checkable guardrail:

`NoWitness -> NoCrossRoleConclusion`.

Reference prototype closeout:

- commit `3e05f5372a2995544ad5081f9f85308aa2b3a7f1`;
- local ref `refs/ordivon/research/interlocus-capability-explanation-validator-v0-20260819`;
- `19/19` focused hostile/positive tests passed.

This remains reference-level evidence only. No production service/API was admitted.

## 7. Interlocus × Harness × Normative deletion result

A possible third `ActionAdmissionExplanation` contract was tested and rejected as redundant.

Present-tense `ExecutePlanNow(P)` can be expressed as another Capability Path target use, drawing on current repair, protected-constraint, Normative, selection and execution-authority facts.

The remaining irreducible problem is **selection among multiple sufficient/admissible repairs**, which is selector/Harness/consumer-owned and depends on external objective/risk/preference plus Normative constraints.

Final chain:

`SufficientRepair != Permitted != Preferred != Selected != CurrentlyExecutable != Executed != RestoredStanding`.

Also:

`Required != Capable`.

`NoPreferenceEvidence != RandomSelectionPermission`.

`NormativeConflict != HarnessChoiceProblem`.

No generic Interlocus ActionLease, selector, optimizer or autonomous repair executor was admitted.

## Engineering reopen condition

Do not materialize a broader Interlocus service merely because the contracts are reusable. Reopen production work only after repeated real workflows provide prospective evidence that a tool reduces Agent/operator error, decision friction or repeated equivalent implementation burden.
