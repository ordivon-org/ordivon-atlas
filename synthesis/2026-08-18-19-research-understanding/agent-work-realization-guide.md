# Agent Work / Cognition / Realization Guide

## Status

`CONVERSATION_ONLY_EXPLANATION` over `ALREADY_DURABLE` Host, Harness and Runtime results.

This file preserves an explanatory chain. It does not redefine Host, Harness, Runtime or domain-owner contracts.

## The central distinction

- **Host** protects long-lived **Work continuity**.
- **Harness** organizes one bounded **Agent cognition / Tool-interaction Run**.
- **Runtime** records and realizes concrete **physical execution**.
- **Domain owners** decide what resulting events/states mean in their domains.

A useful non-mandatory chain is:

`Task -> Run -> Intent -> ToolRequest -> Attempt -> Effect -> DomainResult -> Verification -> TaskCompletion`

Every arrow can fail, become unknown, or require a different owner.

## Why these identities must not collapse

A Task can outlive a model, conversation, process, machine, Harness Run and Runtime Attempt.

One Harness Run may invoke many Tool operations. One logical execution responsibility may have multiple physical Attempts. An external Effect can remain `UNKNOWN` even after a process/HTTP path terminates.

Therefore:

- `Task != Run`
- `Run != Attempt`
- `Intent != ToolRequest`
- `AttemptSuccess != EffectSuccess`
- `EffectSuccess != DomainSuccess`
- `HarnessRunCompleted != HostTaskCompleted`

## Success always has scope

A single unqualified `success=true` is usually too weak for Agent systems.

For example, all of the following may simultaneously be true or false independently:

- model response completed;
- Harness Run completed;
- Tool invocation was accepted;
- Runtime process exited 0;
- provider request was accepted;
- external Effect occurred;
- Finance order filled;
- user objective was satisfied;
- Host Task can close.

The safe question is not "did it succeed?" but:

> **Which owner's success, over which obligation?**

## UNKNOWN and recovery

External-effect ambiguity is a central case:

`no response != no effect`

If an admitted consequential request loses its response, recovery should preserve/reconcile the original consequence identity before considering a new attempt. Replaying the intent with a new identity can create a second payment/order/send/deployment/etc.

This supports the cross-owner law:

`Recovery != Replay`

and the Research-System/general rule:

`Recovery Never Mints Authority`.

## Structure control boundaries, not thought

Harness/Host/Runtime need durable identities and consequence-relevant control facts, but Ordivon should not force every reasoning turn into a permanent schema.

A useful division is:

- durable: identity, authority/source bindings, Tool contract identity, effect commitments, lifecycle/handoff facts;
- flexible: interpretation, exploration, hypothesis generation and transient cognition unless a later result requires explicit evidence/provenance.

## Durable upstreams

Detailed truth remains in Host, Harness and Runtime owner corpora. Cross-owner placement and engineering status are recorded in:

- `task:ordivon-research-results-classification-and-descent-20260818`
- `task:ordivon-research-to-engineering-reform-coverage-20260818`

This guide exists so a fresh human/Agent can reconstruct the responsibility model without re-reading all three corpora first.
