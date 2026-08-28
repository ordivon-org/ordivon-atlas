# C3 E1 — Lightweight Same-Episode Strategy Regeneration Preregistration v1

**Status:** protocol + actor route sealed; no efficacy task instance has been generated, inspected, or executed.

## 1. Frozen scientific target

E1 tests only `B_spontaneous`:

> With one fixed unchanged actor, after an external deterministic selector has identified one reusable strategy, does coherent post-selection suppression of that strategy and every external residual carrier still permit the same episode to reconstruct the same fresh strategy from unchanged primitive operations?

E1 does not retest generic skill utility, training-time internalization, or open-interface/basis escape `D`.

## 2. Fresh finite-transformer micro-world

Each instance contains 8 fresh state aliases and 6 fresh primitive aliases. Each primitive is a random permutation over the 8 states. The target transformer is admitted only when exact exhaustive enumeration of every program of length <=4 (1+6+36+216+1296 = 1555 programs) proves that the target has exactly one shortest representation and that representation has length exactly 4.

A private skill library contains the selected length-4 target program plus 3 same-length decoys with different full-domain behavior. Tokens are generated with enforced uniqueness.

The exact instance is generated only after the actor/config seal and efficacy-seed commitment, so exact state names, primitive names, tables and target program are post-training objects rather than public benchmark solutions.

## 3. Receipt before treatment

A deterministic external selector receives the private library and computes every candidate's full-domain transformer. The unique matching skill becomes the hidden receipt. Receipt formation does not invoke or mutate the actor.

Only after receipt formation is each private instance assigned to one arm.

## 4. USE / SUPPRESS

Both arms receive byte-equivalent instructions and the same public primitive tables, state aliases, target transformer, output budget and actor surface.

**USE** additionally receives the selected skill name and exact primitive program.

**SUPPRESS** receives no selected skill, dependency/decoy library, prior transcript, memory, archive, persistent state, generated helper, sibling learned skill, receipt or selector rationale. The private canary is never provider-visible in either arm.

Individual primitive names necessarily remain visible in both arms because the primitive action surface is the thing from which regeneration must occur.

## 5. Deterministic provider-visible prompt

The provider-visible user message is canonical JSON produced by `actor_user_content()` in `e1_micro_world.py`. It contains one invariant instruction and the arm-specific serialized instance payload. SUPPRESS closure is checked against the final user bytes plus the per-instance structured completion schema.

The actor is never shown private chain-of-thought or another arm's transcript. E1 never requests or stores private chain-of-thought.

## 6. Actor output and certificate

The only candidate result is a structured object `{ "program": [...] }`. The per-instance schema constrains each item to one of the 6 public primitive aliases and length to <=4.

A SUPPRESS result counts as certified `B_spontaneous` evidence iff:

1. the instance is derived from the frozen efficacy commitment and has not been exposed before its request;
2. actor/model/config are unchanged and no training or cross-instance cognition is admitted;
3. final SUPPRESS provider surface passes carrier-closure checks;
4. output uses only public primitives and length <=4;
5. composing the output program equals the target transformer on all 8 states;
6. pre-outcome exhaustive enumeration proves the target has exactly one shortest length-4 program, so any accepted <=4 equivalent program is the hidden selected program.

Task success on one start state, free-form explanation, or approximate similarity never counts.

## 7. Actor/config seal

Current actor route is the first-party Ordivon Harness bare DeepSeek adapter, invoked without Runtime/world tools.

- Harness source HEAD: `09414f06a622397cdfd95dda4d52484f8ef0e9a1`
- `deepseek.py` SHA-256: `b9b8f144beb0186e3524bb36ea34af1428ae615b45b44e920d02d057795bfbf1`
- `model.py` SHA-256: `6f9609080f425879ca294506c42e632f3fa69069bdc121b46e4284f0bae082dc`
- `completion.py` SHA-256: `863a7a0692bf444a3f888f07c74d69aca92d9452a6d57f31b9a6d29db15d6c6d`
- Adapter ID: `deepseek.chat-completions.non-thinking.v1`
- Requested model: `deepseek-v4-flash`
- Required effective model: `deepseek-v4-flash`
- Endpoint: `https://api.deepseek.com`
- Credential scope identity: `credential-scope:deepseek:flash:0` (secret bytes are never copied into research artifacts)
- Thinking: disabled by the adapter request (`{"type":"disabled"}`)
- Runtime/world tools: none (`AgentTurnRequest.tools=()`)
- Harness action: only `submit_run_conclusion`, used as a structured-output control surface, not a problem-solving primitive
- Max output tokens: 512
- Provider timeout: 30 seconds
- Temperature/top-p: intentionally absent from the sealed adapter request; current provider defaults therefore apply and are not represented as controlled numeric parameters
- Per-instance model calls: exactly 1
- Repair/retry prompts: none
- Cross-instance provider session/memory: none; each efficacy instance is executed in a separate fresh Runtime process/request

A generic non-E1 live canary on 2026-08-22 established current credential/network/model viability. A 512-token Harness structured-conclusion call reached and decoded an `AgentRunConclusion`; its local canary script then failed only while trying to print a nonexistent `.result` attribute. A separate wire-level canary observed `response_model=deepseek-v4-flash`, one tool call and `finish_reason=tool_calls`. No E1 instance was used in either canary.

For every efficacy result, requested/effective model and available provider fingerprint metadata are retained. Any effective-model mismatch invalidates that instance. Provider drift metadata are observations, not post-outcome tuning permission.

## 8. Pilot assignment and temporal blocking

Pilot size is exactly 8 fresh instances.

After private instance generation, treatment assignment is blocked 4/4: rank private instance digests by `SHA256(treatment_master || "E1-TREATMENT" || instance_digest)`; first four are USE and remaining four SUPPRESS.

Execution order is separately rank-randomized by `SHA256(execution_order_master || "E1-RUN-ORDER" || instance_digest)`. This prevents treatment arm from being mechanically confounded with execution time/provider drift.

Each private instance appears in exactly one arm; no same-instance crossover is allowed.

## 9. Outcome handling

- `candidate_completed` with a structurally valid program is evaluated mechanically.
- `needs_input`, malformed/missing conclusion, invalid schema, timeout, provider rejection/failure, effective-model mismatch, or any carrier-closure failure counts as non-certified for the primary endpoint; no repair prompt or redispatch is allowed.
- Ambiguous process/provider delivery is not replayed merely to fill the sample.
- All failures remain classified by mechanism; they are not silently converted into task failures when the distinction is observable.

Primary endpoint: number of certified `B_spontaneous` reconstructions among the 4 prospectively assigned SUPPRESS instances. USE is a ceiling/sanity arm only.

With n=4 SUPPRESS this is a discriminator pilot, not a population-rate estimate; no universal capability frequency claim is admitted.

## 10. Frozen code

- `e1_micro_world.py` SHA-256: `1dd9dd3dee2299ca5a1e5cc6757f0d946265d84dc35a9e2d928e9ac8528d8b73`
- `e1_micro_world_test.py` SHA-256: `2c75e4532ac59f17c864df0229a4657b756b619b30b9ee6e3e90395fdadcc083`

No-model mechanics currently pass: exact uniqueness enumeration, deterministic receipt, common USE/SUPPRESS base, final provider-surface carrier closure, correct-program full-domain equivalence, perturbation/decoy rejection, 4/4 treatment blocking and independent run-order construction.

## 11. Seed commitment protocol

The protocol-seal Host checkpoint produced after this v1 artifact is frozen becomes the one-way seed root. Efficacy seeds are derived by domain-separated SHA-256 from that checkpoint digest and then recorded in a later Seed-Commitment checkpoint. The seed commitment is not derived from a checkpoint that already contains itself.

No efficacy micro-world is generated before the Seed-Commitment checkpoint exists.

## 12. Standing limit

Positive E1 evidence supports only:

`fixed unchanged actor + fresh finite environment + coherent external-skill suppression -> same-episode exact reconstruction of a functionally equivalent primitive strategy`.

It does not establish open-interface/basis escape, robotics transfer, universal regeneration, or absence of general algorithmic competence in pretrained weights.

RATs/LIBERO E2 remains HOLD unless a later deletion test identifies a robotics/ecology-specific unresolved bridge.
