# Open-Interface Soft-Sensor WR/WP-I/WP-G/WA Benchmark

Status: owner-only implementation/calibration. No autonomous challenge admitted.

Owner task: `task:open-interface-soft-sensor-wr-wp-wa-benchmark-implementation-20260820`
Theory source: `task:finite-intelligence-open-interface-formation-handoff-20260820@164`

## Purpose

Build a prospective physical benchmark in which the same outward failure can require different admissible repairs:

- `WR`: representation-limited; old raw history is sufficient, frozen summary is lossy; repair = reanalysis.
- `WP-I`: deployed-interface-limited; `q* ∉ I0` but `q* ∈ C0`; repair = materialize/recompose an already-reachable measurement coupling.
- `WP-G`: frozen-grammar-limited; every primitive in frozen `G0` preserves a mirror relation, so `q* ∉ Cl_G0(P0)`; repair = author and validate post-evidence `g*` that breaks the relation.
- `WA`: artifact/nuisance-limited; apparent A/B signal is nuisance-correlated and disappears under owner randomization; repair = grounding/rejection.

Do not collapse WP-I and WP-G. Do not claim ultimate metalanguage escape from WP-G.

## Prototype body

A fixed symmetric frame holds a replaceable fabric-faced elastomer/deformable cartridge. Two matched motorized normal-loading axes act at mirror positions `±x0` with force sensing. The cartridge has fixed conductive landing pads contacted by spring/pogo fixtures. A DIW print head may create conductive sensing paths terminating on those pads. Neutral-state geometry capture is allowed before arm; active-state imagery is denied to the agent.

Owner-only nuisance actuation may vary clamp preload, contact force, cable flex, order and calibration state.

## Calibration gate

No agent-visible run until all pass:

1. contact/readout repeatability;
2. physical mirror-null calibration across independent cartridges and nuisances;
3. controller/firewall leakage audit;
4. WR raw-history separability while frozen summary fails;
5. WA nuisance correlation then randomized removal;
6. owner asymmetric positive-control sensor reaches useful discrimination;
7. `WP-I C0` and `WP-G G0` source fences are frozen;
8. decoder, independent episode unit, `alpha`, `epsilon`, `eta`, replica count and physical budget are frozen.

## Discrimination receipts

For a frozen owner decoder on balanced held-out A/B episodes define:

`D_hat = 2 * (balanced_accuracy_hat - 0.5)`.

Old-interface tolerance is accepted only if an upper confidence bound satisfies `U(D_old) <= epsilon`. A candidate coupling is useful only if a lower confidence bound satisfies `L(D_q*) >= eta`, with a preregistered positive margin `eta - epsilon >= Delta_min`.

Structural mirror closure and finite-sample calibration are separate receipts.

## Lifecycle

`S0 owner calibration/freeze -> S1 hidden arm -> S2 initial exposure -> S3 bounded diagnostics -> S4 one primary repair commitment -> S5 blinded adjudication/persistence`.

Budget must allow bounded diagnostics plus any one correct full repair route, but not exhaustive completion of all full repair routes.

Persistence claims additionally require context reset, matched registry/no-registry ablation and shifted-family revalidation.
