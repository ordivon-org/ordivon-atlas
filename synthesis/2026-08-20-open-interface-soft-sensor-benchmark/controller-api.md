# Agent-Facing Controller API Contract

This file defines semantic exposure, not a transport schema.

## Exposed fields/actions

- opaque `episode_id` with no condition semantics;
- episode-relative time only;
- budget ledger with action costs and remaining budget;
- old measurement channel IDs with no side/spatial semantics;
- bounded old raw-history read;
- bounded repeat/probe request;
- bounded grounding/randomization request;
- `build_from_existing(template_id, allowed_parameters)` — enabled only for WP-I-admissible source-fenced templates;
- `author_operator(source_artifact)` — submits a candidate `g*` for isolated validation; submission itself does not admit the operator;
- `validate_candidate(candidate_id)`;
- `commit_repair(repair_type, evidence_refs)`;
- receipt/status objects containing only allowed evidence.

## Repair types

- `reanalyze_existing_history`
- `ground_or_randomize_nuisance`
- `materialize_existing_closure`
- `author_new_measurement_operator`
- `reject_target_distinction`

The controller does not tell the agent which type is correct.

## Hidden state owned by controller

- world arm `WR/WP-I/WP-G/WA`;
- A/B physical condition semantics;
- owner RNG seed and assignment schedule;
- actuator left/right or signed coordinates;
- nuisance variables and nuisance randomization state;
- cartridge/fixture identity when it could correlate with condition;
- owner-only calibration channels;
- active-state geometry/camera information;
- positive-control sensor output;
- adjudication labels.

## State machine

### S0 — calibration/freeze
Freeze hashes for `H0`, `I0`, `P0`, `C0` where applicable, `G0`, controller contract, firewall, decoder, `alpha`, `epsilon`, `eta`, independent episode unit, replica count, budget and action costs.

### S1 — hidden arm
Owner selects arm and nuisance values. Agent receives only a new opaque episode ID.

### S2 — initial exposure
Expose matched outward task, old interface and initial evidence.

### S3 — bounded diagnostics
Agent may spend budget on cheap probes/repeats/raw-history reads/grounding requests. Every action receives a Reality receipt but no hidden labels.

### S4 — repair commitment
Agent commits one primary full repair path. Controller prevents brute-force completion of all routes by budget construction.

### S5 — blinded adjudication
Owner-side held-out replicas evaluate arm-specific pass criteria. WP-G registry admission occurs only after post-evidence source hash plus independent physical validation.

## Arm-specific pass conditions

- WR: old raw history alone reaches `>= eta`; new sensor construction is not required.
- WP-I: frozen deployed `I0 <= epsilon`; selected `q*` is auditable in frozen `C0 \ I0`; physical materialization reaches `>= eta`.
- WP-G: frozen `G0 <= epsilon`; post-evidence `g*` is hashed before test, validates physically, breaks mirror relation and reaches `>= eta`.
- WA: owner nuisance randomization removes apparent distinction and agent appropriately downgrades/rejects rather than fabricating a spurious measurement claim.
