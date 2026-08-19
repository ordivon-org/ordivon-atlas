# M0 Projection Health

## Materialization observation

```text
projectionStage = M0_MANUAL_CURATED
truthRole = manual-curated-methodology-observation-projection
authorityRole = none
AtlasBase = d1dc3e49f44cbe69c8eff554921af6ac46b0c784
AtlasRemoteMainAtMaterialization = d1dc3e49f44cbe69c8eff554921af6ac46b0c784
MethodologyObservation = task:ordivon-research-methodology-observation-20260819@37
ProjectionDesign = task:ordivon-atlas-research-methodology-observation-projection-design-20260819@3
PracticeGuidance = task:ordivon-human-agent-research-practice-guidance-20260819@6
ProcessLineageRequirement = task:ordivon-atlas-research-process-lineage-requirement-20260819@6
OperatingDiscipline = task:ordivon-research-operating-discipline-v0-20260819@5
```

At materialization, the Atlas remote `main` matched the exact design/source fence. No concurrent source advancement had to be reconciled.

## M0 health interpretation

M0 has no daemon or generated currentness engine. Health is therefore explicit/manual:

- `CURRENT_TO_MATERIALIZATION_SOURCES` — all primary source fences above match the materialized content.
- `SOURCE_ADVANCED_REVIEW_REQUIRED` — one or more primary methodology/design sources advanced; M0 remains historical but needs review before being presented as current observation.
- `BROKEN_SOURCE_POINTER` — a referenced artifact/task/path cannot be recovered.
- `BOUNDARY_VIOLATION` — M0 copied practice rules or owner truth as if methodology observation owned them.

Current state at creation:

```text
CURRENT_TO_MATERIALIZATION_SOURCES
```

## What does not stale automatically

A linked owner can advance while a historical episode remains valid evidence that a research transition occurred. Owner advancement does **not** automatically invalidate the methodology episode.

However, M0 must not infer the owner's new current standing from its historical pointer. If a current owner claim matters, resolve owner currentness independently.

## M1 reopen gate

M1 generated/source-fenced methodology projection remains `NOT_ADMITTED`.

Reopen only after repeated real use demonstrates a material failure in manual:

1. source recovery;
2. stale-observation detection;
3. interaction querying;
4. evidence-episode discovery;
5. coverage/bias auditing;

that existing `synthesis/` + Process Lineage + owner Atlas views cannot solve without repeated ambiguity or loss.

A desire for symmetry, automation, a database or a cleaner schema is not a reopen condition.
