# Execution Receipt — 2026-08-20

Status: first mechanical calibration run PASS.

Runtime job: `job-01a01f30-1d82-7313-806a-4b9df4fa9559`

Stdout digest: `sha256:d8441568959bf9fdb0aeefa11d34fd68418612fde644d83281092198c43876d9`

## Mechanical fence

- pre-cutoff evidence years <= 2020: PASS
- future adjudication years > 2020: PASS
- no bibcode overlap between pre/future sets: PASS

## Component calibration

Documented future resolution components:

1. improved systematics + Bayesian model averaging;
2. retrieval-assumption sensitivity / independent retrieval framework;
3. independent high-resolution spectroscopic grounding.

Results:

- `polarity_only_control`: 0/3 component coverage. The pre-cutoff water claims had the same direction, so an opposite-polarity-only tension trigger has no route to q_008.
- `consensus_control`: 0/3. Treating cross-dataset same-direction evidence as sufficient corroboration creates no separator.
- historical `evidence_graph_v1`: 2/3 conservative component coverage. Its frozen q_008 explicitly requested independent retrieval frameworks and independent data; this maps to retrieval-assumption sensitivity and orthogonal grounding.
- `genealogy_multiverse_calibration`: 2/3, but this is a retrospective synthetic method control, not a historical prospective result.
- `orthogonal_calibration`: 1/3, also retrospective synthetic control.
- all calibration controls union: 3/3.

## Standing

The only historical prospective hit counted here is the released `evidence_graph_v1` q_008 output. Synthetic controls exist only to test method-combination semantics.

The useful local result is:

`IndependentDatasets != IndependentInferenceAssumptions`.

A proposal generator that searches only outcome disagreement can miss correlated inferential error shared across physically different datasets. Evidence genealogy plus analysis/retrieval multiverse plus orthogonal validation can expand reachable discriminator support without requiring local hardware.

This is calibration, not a claim that the present Ordivon/LLM generator would have discovered q_008 under a clean 2020 information boundary.
