# Firewall Harness Receipt

Status: self-test executed successfully on 2026-08-20. The executable harness is `firewall_harness.py`.

The harness is deliberately stdlib-only because the current Runtime image lacks NumPy/pandas/scikit-learn. It performs two distinct checks:

1. explicit forbidden-key/value scanning, including direct hidden labels, side semantics, seeds, fixture labels and suspicious owner/debug metadata;
2. a metadata-only red-team decision-stump audit: for every categorical transcript feature, learn the majority hidden label per feature value on a deterministic training partition and report the best held-out prediction accuracy for hidden arm and A/B.

`--selftest` generates two synthetic corpora with matched outward scientific fields:

- `clean`: opaque IDs, scrubbed metadata and no hidden semantics;
- `intentionally_leaky`: direct hidden arm, condition-correlated fixture serial, left/right actuator semantics and seed/error leakage.

Pass expectation: clean must pass; intentionally-leaky must fail. These synthetic tolerances are only harness self-test thresholds and are not the future physical benchmark's preregistered firewall confidence bounds.

## Executed self-test receipt

Command: `python firewall_harness.py --selftest` through Ordivon Runtime.

- clean corpus: 800 episodes; explicit leak episode count = 0; best held-out metadata-only hidden-arm accuracy = 0.220974 (best feature `action`, tolerance 0.38); best A/B accuracy = 0.475655 (best feature `action`, tolerance 0.63); PASS.
- intentionally-leaky corpus: 800 episodes; explicit leak episode count = 800; best hidden-arm accuracy = 1.0 via `metadata.fixture_serial`; best A/B accuracy = 1.0 via `metadata.actuator_side`; FAIL as expected.

Runtime job: `job-01a01ef1-93dc-7a73-9615-407e5f0dfdb3`; stdout digest `sha256:680327a74d76ec71d2f87f62020227f5e735a00d49346222e60640b1237d15e4`.

This closes only the synthetic controller-integrity self-test. It does not certify a future real controller build, which must rerun the audit over complete actual transcripts including error paths.

## Audit-unit correction from controller integration

When integrated with the controller emulator, the first statistical audit falsely flagged clean output because it treated the agent's own repair choice as metadata. Since successful scientific behavior should become condition-dependent, this is not a hidden-channel leak. The statistical signature now excludes measurements and endogenous action/repair/budget/status fields, while the explicit denylist still scans the entire transcript. Re-run on 1,920 clean controller events gives arm accuracy 0.25 and A/B 0.5 with no explicit leaks; hostile error-path outputs remain fully detected.
