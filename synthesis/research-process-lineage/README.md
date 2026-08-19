# Research Process Lineage — Manual Curated Layer

## Status

- truthRole: `manual-curated-research-process-memory`
- authorityRole: `none`
- parentLayer: [`synthesis/`](../README.md)
- purpose: preserve epistemically load-bearing research transitions that are lost when only final results/current publications are retained
- implementationStatus: `MANUAL_V0`

This directory is the manual precursor/dogfood surface for a possible future first-class `ResearchEpisode` / `DecisionFalsificationTrace` capability in Ordivon Atlas + Research System.

It exists because:

`ResearchResult != AllResearchValue`.

The final answer to a research programme often omits why an earlier view was reasonable, what hostile case changed it, which distinction survived falsification, why a route was not admitted, or how a historically correct operational decision later became stale.

## Core boundary

`ProcessLineage != OwnerTruth`

`Conversation != SemanticAuthority`

`Newer != AutomaticallyMoreAuthoritative`

These records are manually compressed from owner corpora, Host continuity, Git history, existing Atlas synthesis, and conversation-derived working history. They do not replace any of those sources.

When an owner-specific claim conflicts with an owner-current publication, the owner-current publication wins. The process record should then be repaired or marked stale while preserving the historically correct earlier state when applicable.

## What belongs here

A process episode is worth preserving when the transition itself changes future research/recovery behavior. Typical load-bearing fields are:

`Question -> InitialPosition -> Rival/Alternative -> Trigger/NewEvidence -> Investigation/HostileCase -> Falsification -> Revision -> SurvivingInsight -> Result -> SupersededClaim -> CurrentStanding -> ProvenanceRefs`.

Not every field must be present. The record should preserve only the minimum causal/epistemic structure needed to answer:

- What did we believe or assume before?
- Why was that position reasonable at the time?
- What challenged it?
- What evidence or falsifier changed the standing?
- What was revised or rejected?
- What survived the change?
- What is current now?
- Where are the exact authoritative bytes/tasks/results?

## What does not belong here

Do not store by default:

- verbatim conversation transcripts;
- every command/tool call;
- ordinary debug logs;
- chain-of-thought or private reasoning;
- implementation chronology with no epistemic consequence;
- duplicated owner theory;
- timestamp-only changelogs;
- retrospective stories that erase the actual historical standing.

A destructive/engineering action may enter only when the decision procedure itself carries durable methodological/currentness value.

## Current collection

The manual collection currently preserves nine high-value 2026-08-18/19 episodes:

1. [`episodes/2026-08-18-19-research-understanding-and-anti-rediscovery.md`](episodes/2026-08-18-19-research-understanding-and-anti-rediscovery.md) — why cross-owner semantic compression and anti-rediscovery needed a durable Atlas synthesis layer rather than remaining conversation-only.
2. [`episodes/2026-08-18-computing-whole-referent-search-a-f.md`](episodes/2026-08-18-computing-whole-referent-search-a-f.md) — how the provisional broad Computing / Programming-Systems umbrella was tested and decomposed into two independent semantic owner lines instead of being declared as a single owner from the start.
3. [`episodes/2026-08-18-19-computational-possibility-formation-currentness-and-repair.md`](episodes/2026-08-18-19-computational-possibility-formation-currentness-and-repair.md) — how owner line T / Algorithmics / AlgF0 became current Computational Possibility, why zero Foundation survived, and how project formation, currentness repair, destructive testing, Git integration, artifact restoration, and Atlas admission completed the cycle.
4. [`episodes/2026-08-18-19-media-owner-inversion-and-ompc-formation.md`](episodes/2026-08-18-19-media-owner-inversion-and-ompc-formation.md) — how Studio-first project intuition was inverted into Media ownership, why major candidate concepts remained Derived rather than MF10, how Web/Game boundaries were corrected, and how Host/Studio/Web/Finance dogfood formed OMPC before construction deliberately stopped.
5. [`episodes/2026-08-18-19-runtime-operational-realization-c1-c10.md`](episodes/2026-08-18-19-runtime-operational-realization-c1-c10.md) — how Runtime post-Foundation dogfood corrected recency/retry/lineage shortcuts, exported Standing/Currentness, established typed support/composition/orthogonality/lifecycle results, and deliberately stopped at C10 saturation rather than continuing by inertia.
6. [`episodes/2026-08-19-generalization-theory-rejection-and-epistemic-opening.md`](episodes/2026-08-19-generalization-theory-rejection-and-epistemic-opening.md) — how one generalized intuition became a candidate theory, was destructively absorbed/rejected without losing its useful distinctions, then changed Ordivon's model of Research and opened a deeper civilization-relative problem-space inquiry that the Human explicitly prevented from collapsing too early.
7. [`episodes/2026-08-19-rsi-pal-standing-action-governance.md`](episodes/2026-08-19-rsi-pal-standing-action-governance.md) — how standing/action admission, hidden consequence premises, structural uncertainty, causal reach/gain, conversion-rule governance, plural grounding and procedural finality were hostilely reconstructed before the parent route closed on Agenda Power / Option-Space Governance.
8. [`episodes/2026-08-19-theory-to-engineering-expansion-contraction-and-rejection.md`](episodes/2026-08-19-theory-to-engineering-expansion-contraction-and-rejection.md) — how a theory-to-engineering question expanded into a broad finite-intelligence candidate, was contracted and destructively dogfooded, gained prospective falsifiability, then lost independent-theory and new-layer standing through prior-art subtraction, deletion tests and a no-duplication audit.
9. [`episodes/2026-08-19-network-to-interlocus-reunderstanding-and-engineering-contraction.md`](episodes/2026-08-19-network-to-interlocus-reunderstanding-and-engineering-contraction.md) — how the historical Network owner was re-read as Interlocus, locus/Core-Law assumptions were hostilely repaired, engineering value contracted to source-fenced explanation/repair warrants, and a proposed action-admission layer was deleted back into existing owner boundaries.

See [`LINEAGE-OVERVIEW.md`](LINEAGE-OVERVIEW.md) for the existing Computing/CP combined continuity and [`SOURCE-INDEX.md`](SOURCE-INDEX.md) for durable source pointers. Individual owner-specific episodes are self-contained where they are not part of that Computing continuity.

## Relationship to the existing Research Understanding collection

The existing [`../2026-08-18-19-research-understanding/`](../2026-08-18-19-research-understanding/) collection preserves **what the portfolio jointly taught us**: worldview compression, research-method synthesis, Human–Ordivon learning map, and anti-rediscovery rules.

This directory preserves **how some of those understandings were reached or repaired**.

Therefore:

`ResearchUnderstandingSynthesis != ResearchProcessLineage`

but both belong under the non-authoritative Atlas `synthesis/` layer.

## Future migration rule

If Atlas later gains a first-class source-fenced Research Episode model, these files are dogfood/migration seeds, not an automatically canonical schema. The future model must earn its shape from multiple real owner episodes rather than encode this manual markdown structure by inertia.
