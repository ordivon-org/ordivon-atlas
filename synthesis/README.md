# Atlas Synthesis Layer

## Status

- truthRole: `non-authoritative-cross-owner-synthesis`
- authorityRole: `none`
- purpose: human/Agent discovery, compression, prior-result lookup, anti-rediscovery, and manually curated process lineage

This directory contains **manually curated synthesis** that helps a human or Agent understand relationships across Ordivon research owners and recover selected high-value research transitions that would otherwise remain trapped in conversations or scattered provenance.

It is deliberately distinct from owner-native research authority and from generated Atlas projections.

## Core law

`Synthesis != OwnerTruth`

A synthesis document may summarize, compare, compress, explain, or reconstruct a bounded research transition. It does not acquire the right to change an owner's current semantic truth merely by being stored in Atlas.

When a synthesis makes an owner-specific claim, the authoritative source remains the owner corpus/publication. When the source owner advances, the synthesis may become stale and must be revalidated rather than silently treated as current.

## Why this layer exists

Owner-native research and Git history preserve detailed truth and provenance, but two high-value forms can otherwise be repeatedly lost or rediscovered:

1. **cross-owner semantic compression** — what several owners jointly taught us and how the pieces fit;
2. **research-process lineage** — why an earlier position was reasonable, what falsified/repaired it, what survived, and how current standing was reached.

This layer therefore preserves, selectively:

- distinctions that recur across projects;
- explanatory maps useful to humans and fresh Agents;
- research-method lessons already supported by durable owner/Computer material;
- Human-facing learning/consumption guidance;
- explicit prior-result pointers that should be checked before opening a fresh research route;
- bounded manually curated Research Episode / Decision-Falsification traces when the transition itself has durable recovery value.

It should reduce repeated rediscovery without becoming a second mutable truth store or a conversation archive.

## Admission rule

Before adding a synthesis item, classify it as one of:

1. `ALREADY_DURABLE` — already represented in an authoritative owner corpus or Computer Knowledge; store a pointer/summary, not a competing copy.
2. `NEW_CROSS_OWNER_SYNTHESIS` — a genuinely new relation or compression across already-durable results; may be recorded here with source pointers.
3. `HUMAN_CONSUMPTION_GUIDE` — guidance about what humans should internalize, retrieve, or delegate; non-authoritative unless separately admitted by the relevant owner.
4. `CONVERSATION_ONLY_EXPLANATION` — useful prose with no durable semantic delta; preserve only when it materially improves discovery/comprehension.
5. `MANUAL_PROCESS_LINEAGE` — a source-fenced compression of an epistemically load-bearing transition such as admission->supersession, falsification->repair, historically-valid->currently-stale, or destructive decision evidence. Do not use this class for ordinary logs/tool chatter.

## Current collections

- [`2026-08-18-19-research-understanding/`](2026-08-18-19-research-understanding/) — manual assimilation of the research-understanding conversation: worldview, owner topology, Agent/work realization, research-method/significance compression, Human–Ordivon learning map, anti-rediscovery, and an explicit assimilation manifest.
- [`research-process-lineage/`](research-process-lineage/) — manual Research Episode / Decision-Falsification traces. The initial collection links the research-understanding conversation, Broad Computing Search A–F, and the Computational Possibility formation/currentness/repair cycle.

## Relationship to generated Atlas

The normal `generated/` Atlas is source-fenced and regenerable from owner authority publications. `synthesis/` is intentionally curated and Git-durable.

Future Atlas search/indexing may expose these documents as **synthesis references** or process-lineage references, but must not project them as owner-current semantic results unless an owner publication explicitly admits the underlying claim.

If Atlas later gains a first-class generated Research Episode model, the manual `research-process-lineage/` collection is dogfood/migration evidence, not an automatic schema definition.
