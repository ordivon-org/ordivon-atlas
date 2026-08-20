# Hidden-Channel Firewall

The benchmark fails closed if any denied channel can reveal hidden arm or WP handedness.

## Denied to agent

- world/condition names or abbreviations;
- actuator side names, signed coordinates or controller axis labels;
- owner RNG seed, randomization schedule or assignment block;
- motor/debug logs containing side, absolute coordinates or hidden state;
- clamp preload, cable-flex/contact nuisance state except through admitted scientific measurements;
- active-state camera/RGB-D/depth/geometry;
- owner-only left/right branch sensor channels used for calibration;
- fixture/cartridge serials correlated with arm/condition;
- filenames, paths, database keys or object IDs containing hidden labels;
- absolute timestamps if they leak assignment order; use episode-relative time;
- unredacted exceptions, stack traces or tool metadata that contain forbidden values;
- operator sandbox filesystem/environment metadata that exposes hidden configuration.

## Allowed

- neutral-state geometry used only for registration/fabrication before condition activation;
- opaque channel identifiers without side semantics;
- symmetric aggregates admitted by `I0`;
- explicitly requested grounding interventions whose returned evidence is scrubbed;
- budget and mechanical success/failure receipts that do not encode hidden labels.

## Mechanical audit

Before agent trials:

1. generate test episodes in all hidden arms;
2. capture the complete candidate agent-facing transcript, including errors and metadata;
3. scan for denied values, label aliases, side names, coordinates, serials and path correlations;
4. train an owner red-team classifier using only metadata/non-scientific fields to predict hidden arm/A-B;
5. require metadata-only discrimination to remain within preregistered firewall tolerance;
6. intentionally trigger failures/timeouts to test error-path leakage;
7. repeat after every controller/tooling change.

A semantic denylist without this mechanical audit is insufficient.
