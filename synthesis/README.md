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
- [`2026-08-18-19-media-reconstruction/`](2026-08-18-19-media-reconstruction/) — Media-specific anti-rediscovery synthesis covering the Studio→Media owner inversion, Derived-vs-Foundation compression, Web/Game boundary corrections, OMPC formation/dogfood and stable-owner Phase-1 closure.
- [`2026-08-19-runtime-operational-realization/`](2026-08-19-runtime-operational-realization/) — Runtime C1–C10 high-value synthesis and anti-rediscovery guard, source-fenced to the current Runtime programme-saturation owner publication without duplicating the owner corpus.
- [`2026-08-19-generalization-and-epistemic-space/`](2026-08-19-generalization-and-epistemic-space/) — preserves the full chain from domain-general capability-formation conjecture through destructive prior-art absorption and theory non-admission, surviving distinctions, bottom-up Research reconstruction, and the deliberately uncollapsed civilization/problem-space opening.
- [`research-methodology-observation/`](research-methodology-observation/) — M0 manual, non-authoritative projection of mature Research Methodology Observation: recurrent mechanisms, failure ecology, bounded interactions, evidence episodes, coverage/bias, source fences and projection health. Practice guidance and owner truth remain pointer-only.
- [`research-process-lineage/`](research-process-lineage/) — manual Research Episode / Decision-Falsification traces. The collection includes research-understanding, Broad Computing Search A–F, Computational Possibility formation/currentness/repair, Media owner-inversion/OMPC formation, Runtime C1–C10 correction/saturation, and the 2026-08-19 generalization→theory-rejection→epistemic-opening episode.

## Relationship to generated Atlas

The normal `generated/` Atlas is source-fenced and regenerable from owner authority publications. `synthesis/` is intentionally curated and Git-durable.

Future Atlas search/indexing may expose these documents as **synthesis references** or process-lineage references, but must not project them as owner-current semantic results unless an owner publication explicitly admits the underlying claim.

If Atlas later gains a first-class generated Research Episode model, the manual `research-process-lineage/` collection is dogfood/migration evidence, not an automatic schema definition.

- [`2026-08-19-rsi-pal-action-governance/`](2026-08-19-rsi-pal-action-governance/) — hostile cross-owner synthesis from effective-research-constitution reconstruction through Standing→Action, hidden action premises, structural uncertainty, causal reach/gain, gain conversion, recursive governance, constitutional escape, plural grounding and procedural finality; closes with the deliberately selected Agenda Power / Option-Space Governance frontier.
- [`2026-08-19-theory-to-engineering-revision-commitment/`](2026-08-19-theory-to-engineering-revision-commitment/) — closes the later theory→engineering / finite-intelligence derivation after second contraction: four-case destructive dogfood, prospective triage protocol repair, prior-art/theory subtraction, deletion testing and the final `NO_NEW_CONTRACT / NO_NEW_SCHEMA / NO_NEW_OWNER` engineering closeout.
- [`2026-08-19-interlocus-reunderstanding/`](2026-08-19-interlocus-reunderstanding/) — source-fenced reconstruction of the Network→Interlocus referent shift, locus/no-Foundation result, hostile Core-Law repair to C1–C7, Capability Path and Counterfactual Repair engineering contracts, consumer-value narrowing, and the no-third-action-contract selection boundary.
- [`2026-08-19-rsi-pal-option-pressure-capability/`](2026-08-19-rsi-pal-option-pressure-capability/) — continuation of the RSI/PAL agenda frontier through hostile Option-Space reconstruction, destructive prior-art deletion of both Option-Space Governance and Pressure Formation as universal theories, preservation of bounded diagnostic distinctions, a ten-region RSI capability topology, owner-native readiness audit, and explicit non-admission of any new experiment beyond the existing prospective F14/F17 field line.
