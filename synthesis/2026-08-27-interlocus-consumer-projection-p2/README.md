# Interlocus Consumer Projection P2 — Cost, Protocol Assimilation, and Validator Disposition

## Truth-role boundary

This collection is a **non-authoritative cross-owner engineering/consumer synthesis**. It does not change Interlocus NDF/NCT/Foundation standing, does not define MCP/A2A/SPIFFE/Kubernetes semantics, does not grant execution admission, and does not move selector authority from Harness/consumer owners into Atlas.

## P2 result

The remaining frontier was not solved by introducing a universal `flat -> epoch -> path -> full graph` hierarchy. J1 already showed why: richer structure can change a weaker Agent's error geometry, but representation cost and benefit are consumer/workload relative. The correct reusable primitive is therefore smaller:

`caller declares required distinctions + caller supplies measured profile cost -> Atlas mechanically selects minimum-cost adequate profile`

Atlas now exposes `select-representation REQUEST.json`. It performs no semantic requirement inference and no currentness verification. `NO_ADEQUATE_PROFILE` is a valid fail-closed result.

## Natural currentness consumer measurement

The P1 `check-owner` change itself supplied a real natural consumer pressure case: owner-scoped currentness needed identity/currentness/recovery fences but not the entire authority publication. The benchmark in this directory measures compact scoped, expanded scoped, and whole-registry observation as real executable read workflows. See `natural-currentness-benchmark.json`.

This is not an LLM benchmark. It measures mechanical read cost (wall time and output bytes) for a real Atlas consumer path. J1 remains the finite-Agent behavior evidence.

Measured medians over three read-only runs on 2026-08-27:

| Workflow | Median wall time | Median stdout |
|---|---:|---:|
| `check-owner Interlocus` | 4,831.675 ms | 827 B |
| `check-owner Interlocus --include-publication` | 5,302.884 ms | 27,429 B |
| whole-registry `check` | 40,987.072 ms | 334,495 B |

Derived mechanical reductions for the compact scoped path:

- vs expanded same-owner publication: **96.9849% fewer output bytes**;
- vs whole-registry observation: **99.7528% fewer output bytes**;
- whole-registry median wall time was about **8.48×** the compact scoped median in this run environment.

The time ratio is environment/network dependent and is not a protocol law. The output-size result is specific to the current owner publications. Both are consumer evidence, not semantic authority.

## Prospective fresh-Agent dogfood

A real supported Harness run then tested the P2 surface as a fresh consumer rather than as a repository test. Source fences:

- Atlas: `1a8920e549617d5b88b45c34763e143416f35814`;
- Interlocus: `3ee823f8f3ce83722a0abe25960cf04f3db6fb4d`;
- Harness: `6b35b4e1778fc8d8b012178eccc56b02af2fadf9`;
- Runtime Job: `job-01a043fa-1131-7bc0-b62c-74dfa54133a2`;
- retained stdout digest: `sha256:fa47ea9d709fbca70f7a60205dad510a1549a6c065c952fd8d717e3021dd4f37`.

The DeepSeek v4 Flash consumer performed the existing Harness-supported sequence `fresh query authorship -> bounded Atlas first-look -> caller-side candidate selection -> exact candidate inspection -> caller adjudication`. It authored four lexical query variants itself; neither Atlas nor the application generated a semantic translation. P2 was selected at rank 1 with bounded score 64 and exact inspection stayed within 7,566 projected bytes.

Final caller adjudication:

- decision: `consume_prior`;
- coverage: `substantial`;
- semantic equivalence established: `false`;
- novelty established: `false`;
- research admission granted: `false`.

Measured usage:

- Provider model calls: **3**;
- total Provider tokens: **9,642** (`2,323 + 2,534 + 4,785`);
- owner reads: **3**;
- domain Tool calls from the model: **0**;
- conclusion/tool corrections: **0 / 0**;
- outer command elapsed time: **19,758 ms**.

This supplies the prospective natural-consumer evidence that the earlier Interlocus closeout lacked. It does **not** prove universal model benefit or production-service necessity. Its narrower result is that a fresh finite consumer can recover the P2 currentness/assimilation/validator conclusions through the bounded Atlas path without Atlas minting semantic equivalence, novelty or research admission. Full structured evidence is retained in `natural-fresh-agent-dogfood.json`.

## J1 representation-cost evidence

Source fence: `ordivon-computing@90b7bc351495323b4d0cab7636470e90cd7fd384`, `research/experiments/joint-capability-j1-adversarial-interlocus-v0/J1-CLOSEOUT.md`.

Adaptive N2 mechanism ablation reported:

| Arm | Valid | Safety errors | Mean total tokens |
|---|---:|---:|---:|
| RAW_CONTROL | 10/10 | 1 | 2228.1 |
| GENERIC_FENCE_ONLY | 10/10 | 2 | 2462.4 |
| EPOCH_STRUCTURE_ONLY | 9/10 | 0 | 2846.0 |
| FULL_INTERLOCUS | 10/10 | 0 | 2830.5 |

This is important negative evidence against a global complexity ladder: in that small adaptive sample, epoch-only was not cheaper in total tokens than full Interlocus. Therefore Atlas must not hard-code `semantic minimality => measured cost minimality`. Costs remain caller/consumer measurements.

## External protocol assimilation

Current external systems repeatedly preserve distinctions already representable by Interlocus without requiring an Ordivon replacement protocol.

### MCP

Official stable specification revision `2025-11-25` separates lifecycle/capability negotiation from optional server features. Servers expose Resources, Prompts, and Tools; tool lists can change and resources are application-driven context. MCP is therefore a strong concrete consumer of capability advertisement/discovery and dynamic surface projection, but a tool/resource descriptor does not by itself establish owner truth, serviceability, permission, or successful effect.

Sources:
- https://modelcontextprotocol.io/specification/2025-11-25
- https://modelcontextprotocol.io/specification/2025-11-25/basic/index
- https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- https://modelcontextprotocol.io/specification/2025-11-25/server/resources

The current draft changelog also moves more cross-call state into explicit server-minted handles and calls for deterministic tool-list ordering, reinforcing explicit identity/state rather than hidden connection-local semantics.

### A2A

A2A specification `1.0.0` exposes Agent Cards for identity/capabilities/skills/interfaces/security requirements, while Task is the stateful work unit and Artifact is task output. Messages are not guaranteed durable critical-delivery carriers. This maps cleanly to: descriptor/offer projection != task lifecycle != durable output/effect. Interlocus can consume Agent Card relation/binding/currentness questions without annexing Host/Runtime/task authority.

Source:
- https://github.com/a2aproject/A2A/blob/main/docs/specification.md

### SPIFFE

SPIFFE v1.15.x defines trust-domain-scoped workload identity, SVIDs, Workload API and federation bundle exchange. It is a strong identity/authentication realization family. A valid SVID establishes cryptographically verifiable identity under a trust domain; it does not establish that the identified workload currently offers a requested capability, is healthy, reachable, permitted, or serviceable.

Sources:
- https://spiffe.io/docs/latest/spiffe-specs/spiffe/
- https://spiffe.io/docs/latest/spiffe-specs/spiffe-id/
- https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/
- https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/

### Kubernetes Service / EndpointSlice

Kubernetes Service deliberately decouples a stable service abstraction from changing backend Pods. EndpointSlices represent current backend endpoint sets and are updated as Pods change; the older Endpoints API is deprecated in current Kubernetes documentation. This is a direct conventional realization of stable consumer identity with dynamic realizations/current projections.

Sources:
- https://kubernetes.io/docs/concepts/services-networking/service/
- https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/

## Assimilation conclusion

The external comparison supports **assimilation rather than replacement**:

- MCP/A2A descriptors can project into Interlocus capability/reference views;
- SPIFFE can supply identity/authentication evidence;
- Kubernetes EndpointSlices can supply dynamic realization/currentness evidence;
- external protocol-native task/effect/security semantics remain externally owned;
- no descriptor or identity credential is promoted to serviceability without the required owner bridges.

`Descriptor != VerifiedCapability != Reachability != Permission != Serviceability != Effect`

## Capability Path validator disposition

The 2026-08-19 validator prototype still has a valid structural role: `NoWitness -> NoCrossRoleConclusion`. P2 adds repeated modern consumers where descriptor, identity, binding/currentness and execution/task roles must not be conflated. However, this does **not** justify a production daemon/API or an automatic cross-owner reasoner.

Disposition:

`REMATERIALIZE_EXACT_PURE_REFERENCE_LIBRARY; DO_NOT_ADMIT_PRODUCTION_SERVICE`

The exact historical v0 prototype should be copied into the standalone Interlocus physical home with provenance preserved, tests rerun, and status kept reference-only. No new semantic fields should be invented merely to model MCP/A2A/SPIFFE/Kubernetes.
