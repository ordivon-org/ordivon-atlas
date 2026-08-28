# C3 E1b — Corrected Structured Same-Episode Regeneration Preregistration v1

**Status:** apparatus correction validated; no E1b efficacy seed or task instance exists yet.

## Scientific semantics

E1b preserves E1 Pilot-1 scientific semantics exactly: 8 fresh states, 6 random permutation primitives, target with one exact unique shortest length-4 program proven by exhaustive enumeration through depth 4, hidden exact-extensional receipt before treatment, 3 decoys, carrier-closed SUPPRESS, identical primitive/public target surface, fixed unchanged actor, no training/memory, 4 USE / 4 SUPPRESS, independent run-order hashing, one Provider call per instance, no retries, and full-domain + unique-minimal regeneration certificate. Positive evidence remains limited to `B_spontaneous`; no open-interface/basis-escape claim is admitted.

Pilot-1's eight instances are permanently excluded and may not be reused.

## Sole apparatus correction

Pilot-1 passed a bare JSON schema to `DeepSeekTurnAdapter(completion_contract=...)`. Current Harness requires the caller completion contract wrapper:

```json
{
  "mode": "structured-result-v1",
  "resultKind": "c3-e1b-program",
  "resultSchema": { "...": "per-instance program schema" }
}
```

E1b therefore wraps the unchanged per-instance program schema in exactly this current Harness contract. No task/prompt difficulty or treatment semantics are changed.

Offline current-source assertion verifies that `structured_completion_result_schema(corrected_contract)` returns the intended result schema.

A generic non-E1 live canary on 2026-08-22 using the corrected wrapper completed with:

- `candidate_completed`;
- decoded structured result `{"ok": true}`;
- effective/provider model `deepseek-v4-flash`;
- `finish_reason=tool_calls`;
- zero Runtime tool calls;
- system fingerprint `a26a7955944dc5c60445bff77fac9c8e`.

Thus the corrected output apparatus is current-live before any E1b efficacy seed is derived.

## Actor seal

Unchanged from E1:

- Harness HEAD `09414f06a622397cdfd95dda4d52484f8ef0e9a1`
- `deepseek.py` SHA-256 `b9b8f144beb0186e3524bb36ea34af1428ae615b45b44e920d02d057795bfbf1`
- `model.py` SHA-256 `6f9609080f425879ca294506c42e632f3fa69069bdc121b46e4284f0bae082dc`
- `completion.py` SHA-256 `863a7a0692bf444a3f888f07c74d69aca92d9452a6d57f31b9a6d29db15d6c6d`
- adapter `deepseek.chat-completions.non-thinking.v1`
- model `deepseek-v4-flash`
- endpoint `https://api.deepseek.com`
- credential scope `credential-scope:deepseek:flash:0`
- thinking disabled
- no Runtime/world tools
- only Harness `submit_run_conclusion` control action
- max output tokens 512; timeout 30s
- provider default temperature/top-p because current adapter omits those fields
- exactly one request per instance, no redispatch/repair
- each instance in a fresh Runtime process/request

## Output contract

The corrected completion contract's `resultSchema` is generated per instance:

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "program": {
      "type": "array",
      "items": {"type": "string", "enum": ["six public primitive aliases"]},
      "minItems": 0,
      "maxItems": 4
    }
  },
  "required": ["program"]
}
```

Harness returns the canonical structured result in `AgentRunConclusion.summary`; E1b decodes that JSON only after candidate completion.

`needs_input`, missing/malformed conclusion, invalid/effective-model mismatch, timeout, Provider/adapter failure, carrier-closure failure or non-equivalent program remain non-certified with no repair prompt.

## Frozen code reused

Scientific generator: `e1_micro_world.py` SHA-256 `1dd9dd3dee2299ca5a1e5cc6757f0d946265d84dc35a9e2d928e9ac8528d8b73`.

No scientific generator change is admitted in E1b.

## New lineage requirement

This document must be checkpointed as an E1b Protocol Seal. Fresh E1b seeds are then derived solely from that new checkpoint digest. No Pilot-1 seed, instance, request or outcome is reused. A later Seed-Commitment and Execution Seal are required before the first E1b efficacy dispatch.
