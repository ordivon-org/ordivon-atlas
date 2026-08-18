# Atlas Synthesis Layer

## Status

- truthRole: `non-authoritative-cross-owner-synthesis`
- authorityRole: `none`
- purpose: human/Agent discovery, compression, prior-result lookup, and anti-rediscovery

This directory contains **manually curated synthesis** that helps a human or Agent understand relationships across Ordivon research owners.

It is deliberately distinct from owner-native research authority and from generated Atlas projections.

## Core law

`Synthesis != OwnerTruth`

A synthesis document may summarize, compare, compress, or explain owner results. It does not acquire the right to change an owner's current semantic truth merely by being stored in Atlas.

When a synthesis makes an owner-specific claim, the authoritative source remains the owner corpus/publication. When the source owner advances, the synthesis may become stale and must be revalidated rather than silently treated as current.

## Why this layer exists

Owner-native research and Git history preserve detailed truth and provenance, but high-value cross-owner understanding can otherwise remain trapped in conversations or be repeatedly rediscovered.

This layer exists to preserve the **semantic compression itself**:

- what several owners jointly taught us;
- distinctions that recur across projects;
- explanatory maps useful to humans and fresh Agents;
- research-method lessons already supported by durable owner/Computer material;
- Human-facing learning/consumption guidance;
- explicit prior-result pointers that should be checked before opening a fresh research route.

It should reduce repeated rediscovery without becoming a second mutable truth store.

## Admission rule

Before adding a synthesis item, classify it as one of:

1. `ALREADY_DURABLE` — already represented in an authoritative owner corpus or Computer Knowledge; store a pointer/summary, not a competing copy.
2. `NEW_CROSS_OWNER_SYNTHESIS` — a genuinely new relation or compression across already-durable results; may be recorded here with source pointers.
3. `HUMAN_CONSUMPTION_GUIDE` — guidance about what humans should internalize, retrieve, or delegate; non-authoritative unless separately admitted by the relevant owner.
4. `CONVERSATION_ONLY_EXPLANATION` — useful prose with no durable semantic delta; preserve only when it materially improves discovery/comprehension.

## Current collections

- [`2026-08-18-19-research-understanding/`](2026-08-18-19-research-understanding/) — manual assimilation of the research-understanding conversation: unified worldview, research-method compression, Human–Ordivon learning map, and anti-rediscovery rules.

## Relationship to generated Atlas

The normal `generated/` Atlas is source-fenced and regenerable from owner authority publications. `synthesis/` is intentionally curated and Git-durable.

Future Atlas search/indexing may expose these documents as **synthesis references**, but must not project them as owner-current semantic results unless an owner publication explicitly admits the underlying claim.
