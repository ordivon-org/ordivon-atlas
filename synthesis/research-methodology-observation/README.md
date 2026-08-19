# Research Methodology Observation — M0 Manual Atlas Projection

## Status

- truthRole: `manual-curated-methodology-observation-projection`
- authorityRole: `none`
- parentLayer: [`synthesis/`](../README.md)
- materializationStage: `M0_MANUAL_CURATED`
- sourceFence: Atlas `d1dc3e49f44cbe69c8eff554921af6ac46b0c784`
- methodologyObservation: `task:ordivon-research-methodology-observation-20260819@37`
- projectionDesign: `task:ordivon-atlas-research-methodology-observation-projection-design-20260819@3`

This collection makes the mature Ordivon **Research Methodology Observation** corpus recoverable inside Atlas without turning methodology into a domain semantic owner, a workflow engine, or a second owner corpus.

Its object is observational:

> What recurrent mechanisms, failure families, interactions, evidence episodes, coverage limits and reopen conditions have actually been observed in Ordivon research practice?

It does **not** answer what a domain currently believes. It does **not** prescribe a mandatory research procedure. It does **not** mint engineering or external-effect authority.

## Boundary laws

```text
MethodologyObservation != OwnerTruth
MethodologyObservation != PracticeGuidance
MethodologyObservation != OperatingDiscipline
MethodologyObservation != ProcessLineage
MethodologyObservation != MethodologyEngine
AtlasSynthesis != SemanticAuthority
```

Owner-specific facts remain owned by owner-native authority publications. This collection uses exact owner/source pointers or source-fenced historical references when a domain example is needed.

Human–Agent practice guidance remains separate. The admitted First-Look Card v0.1 is linked through [`SOURCE-INDEX.md`](SOURCE-INDEX.md); P1–P6 are not copied here as empirical mechanism definitions.

Research Process Lineage also remains separate. [`../research-process-lineage/`](../research-process-lineage/) preserves transition narratives; this collection extracts recurring cross-episode mechanisms and failure patterns rather than duplicating those stories.

## M0 views

- [`MECHANISMS.md`](MECHANISMS.md) — ten mature interacting mechanism observations.
- [`FAILURE-ECOLOGY.md`](FAILURE-ECOLOGY.md) — ten mature failure families and their discriminants.
- [`INTERACTION-MAP.md`](INTERACTION-MAP.md) — bounded observational relations among mechanisms/failures.
- [`EVIDENCE-EPISODES.md`](EVIDENCE-EPISODES.md) — representative support, contrast, falsifier and boundary episodes.
- [`COVERAGE-AND-BIAS.md`](COVERAGE-AND-BIAS.md) — sampling, survivorship and workload-selection limits.
- [`SOURCE-INDEX.md`](SOURCE-INDEX.md) — exact tasks, artifact digests and historical source fences.
- [`PROJECTION-HEALTH.md`](PROJECTION-HEALTH.md) — current M0 source/currentness status and M1 reopen gate.

## Reading order

For first lookup, read this file, then `MECHANISMS.md` + `FAILURE-ECOLOGY.md`. Use `EVIDENCE-EPISODES.md` and `SOURCE-INDEX.md` only when the basis of an observation matters.

For a domain decision, leave this collection and resolve the current owner authority through Atlas/owner-native recovery. A methodology observation is never a substitute for owner currentness.

## M1 gate

Do **not** add a generated methodology schema, Atlas `SourceSpec`, database, service, MCP, owner registration or core projection changes merely because M0 exists.

M1 is admissible only if repeated real use exposes a material failure in at least one of:

- source recovery;
- stale-observation detection;
- mechanism/failure interaction querying;
- evidence-episode discovery;
- coverage/bias auditing;

and that failure cannot be handled cleanly by this curated layer + Process Lineage + existing owner Atlas views.
