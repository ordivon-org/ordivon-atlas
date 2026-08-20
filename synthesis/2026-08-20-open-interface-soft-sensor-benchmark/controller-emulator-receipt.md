# Controller / Ledger Emulator Receipt — 2026-08-20

Status: non-agent semantic implementation self-tests passed. No physical receipt implied.

## Bugs found and repaired during owner-only self-test

1. Receipt immutability bug: an emitted event dictionary was inserted into the receipt chain by reference and later mutated with `receipt_id`, invalidating recomputation of the prior hash. Repair: canonical JSON round-trip freezes every receipt body at issuance.
2. Firewall audit-unit bug: metadata classifier originally included agent-authored repair/action fields. A correct repair can legitimately predict hidden world after scientific evidence, so this produced a false leakage alarm. Repair: explicit denylist still scans the complete transcript, but statistical side-channel prediction excludes scientific measurements and endogenous agent behavior such as action/repair/budget/status.

Preserve the distinction:

`WorldPredictabilityFromAgentBehavior != HiddenMetadataLeakage`.

## Controller test

The emulator enforces `S0 freeze -> S1 arm -> S2 exposure -> S3 diagnostics -> S4 one-primary-repair commitment -> S5 adjudication`, budget accounting and a hash-chained owner receipt history.

After fixes, 120 repetitions over each of four hidden arms produced 1,920 clean agent-facing events. Firewall audit:

- explicit leak episodes: 0;
- best held-out non-scientific metadata hidden-arm accuracy: 0.25 (chance for four arms);
- best A/B accuracy: 0.5;
- clean controller PASS.

A hostile error path containing owner seed, hidden arm, actuator side and condition-correlated fixture serial was generated for 480 episodes:

- explicit leak episodes: 480/480;
- hidden-arm accuracy: 1.0 via fixture serial;
- A/B accuracy: 1.0 via owner-seed/side metadata;
- hostile controller FAIL as required.

Runtime passing job: `job-01a01ef4-8b0c-75c0-a279-04c417c0b7b9`; stdout digest `sha256:79195da6d38b376152543482c9b3726d5ad732f2805851d3ac666b7303842291`.

## WP-I C0 validator

Frozen `wp_i_templates.json` contains `offset_path_v0` with bounded offset, width and serpentine parameters plus fixed auxiliary readout contract.

Self-test:

- nonzero in-range offset candidate: VALID member of frozen C0 family;
- zero offset: INVALID by frozen parameter constraint;
- after-event unknown template: INVALID (`template_not_in_frozen_C0`).

This is a membership/source-fence receipt only, not proof of physical usefulness.

## WP-G operator gate

`operator_artifact_schema.json` separates pre-physical states from physical-only states.

Self-test:

- complete candidate may reach `digest_frozen`;
- attempt to jump to `registry_admitted` without external physical receipt is mechanically rejected with `physical_receipt_required`.

Thus the software implementation cannot silently convert semantic validation into a fabricated physical success.
