#!/usr/bin/env python3
"""E1 finite-transformer micro-world generator/evaluator.

NO model calls. NO efficacy outcomes. This module supports preregistration and mechanics
validation only. Fresh random finite-state permutation systems make exact target strategies
runtime-generated rather than training-data objects.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import json
import random
from typing import Iterable

N_STATES = 8
N_PRIMITIVES = 6
TARGET_MIN_LEN = 4
MAX_PROGRAM_LEN = 4
N_DECOYS = 3


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_bytes(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    """Return b∘a: apply a, then b."""
    return tuple(b[a[i]] for i in range(len(a)))


def program_transform(primitives: dict[str, tuple[int, ...]], program: Iterable[str]) -> tuple[int, ...]:
    cur = tuple(range(N_STATES))
    for name in program:
        cur = compose(cur, primitives[name])
    return cur


def random_token(rng: random.Random, prefix: str, length: int = 6) -> str:
    alphabet = "bcdfghjklmnpqrstvwxyz"
    return prefix + "_" + "".join(rng.choice(alphabet) for _ in range(length))


def unique_tokens(rng: random.Random, prefix: str, n: int, length: int = 6) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    while len(out) < n:
        token = random_token(rng, prefix, length)
        if token in seen:
            continue
        seen.add(token)
        out.append(token)
    return tuple(out)


def random_permutation(rng: random.Random) -> tuple[int, ...]:
    a = list(range(N_STATES))
    rng.shuffle(a)
    return tuple(a)


def shortest_programs(primitives: dict[str, tuple[int, ...]], max_len: int) -> dict[tuple[int, ...], list[tuple[str, ...]]]:
    # Exact enumeration is tiny here: 1+6+36+216+1296 = 1555 programs through depth 4.
    # Keeping every shortest representation makes the uniqueness certificate proof-grade.
    names = tuple(primitives)
    best: dict[tuple[int, ...], list[tuple[str, ...]]] = {tuple(range(N_STATES)): [()]}
    for depth in range(1, max_len + 1):
        for prog in itertools.product(names, repeat=depth):
            tf = program_transform(primitives, prog)
            existing = best.get(tf)
            if existing is None:
                best[tf] = [prog]
            elif len(existing[0]) == depth:
                existing.append(prog)
    return best


@dataclass(frozen=True)
class E1Instance:
    schema: str
    seed: str
    state_labels: tuple[str, ...]
    primitive_order: tuple[str, ...]
    primitives: dict[str, tuple[int, ...]]
    target_transform: tuple[int, ...]
    selected_skill_name: str
    selected_skill_program: tuple[str, ...]
    selected_skill_canary: str
    decoy_skills: tuple[tuple[str, tuple[str, ...]], ...]
    instance_digest: str

    def public_base(self) -> dict:
        # Selected skill identity/program/canary and decoys are intentionally absent.
        return {
            "schema": "ordivon.c3.e1-public-base.v1",
            "state_labels": list(self.state_labels),
            "primitives": {
                name: {
                    self.state_labels[i]: self.state_labels[out]
                    for i, out in enumerate(self.primitives[name])
                }
                for name in self.primitive_order
            },
            "target_transform": {
                self.state_labels[i]: self.state_labels[out]
                for i, out in enumerate(self.target_transform)
            },
            "max_program_len": MAX_PROGRAM_LEN,
            "required_output": "JSON array of primitive names only",
        }

    def use_payload(self) -> dict:
        # The private canary is never provider-visible; it exists only for closure auditing.
        return {
            "schema": "ordivon.c3.e1-selected-skill.v1",
            "skill_name": self.selected_skill_name,
            "program": list(self.selected_skill_program),
        }

    def suppress_payload(self) -> dict:
        return {"schema": "ordivon.c3.e1-suppress.v1", "selected_skill": None}


def _instance_without_digest(seed: str, rng: random.Random) -> dict:
    state_labels = unique_tokens(rng, "s", N_STATES)
    primitive_order = unique_tokens(rng, "p", N_PRIMITIVES)
    primitives = {name: random_permutation(rng) for name in primitive_order}
    best = shortest_programs(primitives, TARGET_MIN_LEN)

    candidates = [
        (tf, progs[0])
        for tf, progs in best.items()
        if len(progs[0]) == TARGET_MIN_LEN and len(progs) == 1
    ]
    if len(candidates) < 1 + N_DECOYS:
        raise ValueError("insufficient unique length-4 transformations")
    rng.shuffle(candidates)
    target_tf, target_prog = candidates[0]
    skill_names = unique_tokens(rng, "skill", 1 + N_DECOYS)
    selected_skill_name = skill_names[0]
    decoys = []
    for idx, (_, prog) in enumerate(candidates[1:1 + N_DECOYS], start=1):
        decoys.append((skill_names[idx], prog))
    return {
        "schema": "ordivon.c3.e1-instance.v1",
        "seed": seed,
        "state_labels": state_labels,
        "primitive_order": primitive_order,
        "primitives": primitives,
        "target_transform": target_tf,
        "selected_skill_name": selected_skill_name,
        "selected_skill_program": target_prog,
        "selected_skill_canary": "E1CANARY_" + sha256_bytes((seed + "|carrier").encode())[:24],
        "decoy_skills": tuple(decoys),
    }


def generate_instance(seed: str, max_attempts: int = 1000) -> E1Instance:
    for attempt in range(max_attempts):
        material = f"{seed}|attempt={attempt}"
        rng = random.Random(int.from_bytes(hashlib.sha256(material.encode()).digest(), "big"))
        try:
            d = _instance_without_digest(seed, rng)
        except ValueError:
            continue
        digest = sha256_bytes(canonical_bytes(d))
        return E1Instance(**d, instance_digest=digest)
    raise RuntimeError("failed to generate qualifying instance")


def hidden_receipt(instance: E1Instance) -> dict:
    # Deterministic external selector. Actor never receives this object in SUPPRESS.
    library = [(instance.selected_skill_name, instance.selected_skill_program), *instance.decoy_skills]
    matches = []
    for name, program in library:
        if program_transform(instance.primitives, program) == instance.target_transform:
            matches.append((name, program))
    if matches != [(instance.selected_skill_name, instance.selected_skill_program)]:
        raise AssertionError(f"selector is not unique: {matches}")
    receipt = {
        "schema": "ordivon.c3.e1-receipt.v1",
        "instance_digest": instance.instance_digest,
        "selected_skill_name": instance.selected_skill_name,
        "selected_program_digest": sha256_bytes(canonical_bytes(instance.selected_skill_program)),
        "selector": "exact-extensional-match-over-full-finite-domain",
    }
    receipt["receipt_digest"] = sha256_bytes(canonical_bytes(receipt))
    return receipt


def blocked_treatment_assignment(instance_digests: list[str], treatment_master: str) -> dict[str, str]:
    if len(instance_digests) % 2:
        raise ValueError("blocked assignment requires an even number of instances")
    if len(set(instance_digests)) != len(instance_digests):
        raise ValueError("instance digests must be unique")
    ranked = sorted(
        instance_digests,
        key=lambda d: hashlib.sha256(f"{treatment_master}|E1-TREATMENT|{d}".encode()).hexdigest(),
    )
    half = len(ranked) // 2
    return {d: ("USE" if i < half else "SUPPRESS") for i, d in enumerate(ranked)}


def arm_request(instance: E1Instance, arm: str) -> dict:
    if arm not in {"USE", "SUPPRESS"}:
        raise ValueError(arm)
    request = {
        "schema": "ordivon.c3.e1-agent-request.v1",
        "base": instance.public_base(),
        "skill_context": instance.use_payload() if arm == "USE" else instance.suppress_payload(),
        "memory": [],
        "prior_transcript": None,
        "persistent_state": None,
    }
    return request


def completion_schema(instance: E1Instance) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "program": {
                "type": "array",
                "items": {"type": "string", "enum": list(instance.primitive_order)},
                "minItems": 0,
                "maxItems": MAX_PROGRAM_LEN,
            }
        },
        "required": ["program"],
    }


def actor_user_payload(instance: E1Instance, arm: str) -> dict:
    return {
        "schema": "ordivon.c3.e1-actor-prompt.v1",
        "instruction": (
            "Construct a primitive program of length at most 4 whose full finite-domain "
            "transformer exactly equals target_transform. Use only the public primitive names. "
            "If skill_context contains a reusable strategy, you may use it. Submit only the "
            "structured program result through the available conclusion action; do not request "
            "additional information."
        ),
        "instance": arm_request(instance, arm),
    }


def actor_user_content(instance: E1Instance, arm: str) -> str:
    return canonical_bytes(actor_user_payload(instance, arm)).decode("utf-8")


def audit_suppress_provider_surface(instance: E1Instance) -> dict:
    content = actor_user_content(instance, "SUPPRESS")
    schema_blob = canonical_bytes(completion_schema(instance)).decode("utf-8")
    combined = content + "\n" + schema_blob
    ordered_program_json = json.dumps(list(instance.selected_skill_program), separators=(",", ":"))
    leaks = {
        "selected_skill_name": instance.selected_skill_name in combined,
        "selected_skill_canary": instance.selected_skill_canary in combined,
        "ordered_program": ordered_program_json in combined.replace(" ", ""),
    }
    return {
        "closed": not any(leaks.values()),
        "leaks": leaks,
        "user_content_digest": sha256_bytes(content.encode()),
        "completion_schema_digest": sha256_bytes(schema_blob.encode()),
    }


def execution_order(instance_digests: list[str], execution_order_master: str) -> list[str]:
    if len(set(instance_digests)) != len(instance_digests):
        raise ValueError("instance digests must be unique")
    return sorted(
        instance_digests,
        key=lambda d: hashlib.sha256(
            f"{execution_order_master}|E1-RUN-ORDER|{d}".encode()
        ).hexdigest(),
    )


def audit_suppress_carrier_closure(instance: E1Instance, request: dict) -> dict:
    blob = canonical_bytes(request).decode("utf-8")
    forbidden = [
        instance.selected_skill_name,
        instance.selected_skill_canary,
        *instance.selected_skill_program,
    ]
    # Primitive names necessarily appear in the public base, so raw program-token absence
    # cannot be required. Instead ensure no ordered selected program sequence or skill identity
    # appears in a hidden carrier field. The complete request has no memory/transcript state.
    ordered_program_json = json.dumps(list(instance.selected_skill_program), separators=(",", ":"))
    identity_leaks = [x for x in [instance.selected_skill_name, instance.selected_skill_canary] if x in blob]
    ordered_sequence_leak = ordered_program_json in blob.replace(" ", "")
    closed = not identity_leaks and not ordered_sequence_leak and request["memory"] == [] and request["prior_transcript"] is None and request["persistent_state"] is None
    return {
        "closed": closed,
        "identity_leaks": identity_leaks,
        "ordered_sequence_leak": ordered_sequence_leak,
        "request_digest": sha256_bytes(canonical_bytes(request)),
    }


def evaluate_program(instance: E1Instance, program: list[str]) -> dict:
    valid_tokens = all(p in instance.primitives for p in program)
    within_budget = len(program) <= MAX_PROGRAM_LEN
    if not valid_tokens or not within_budget:
        equivalent = False
    else:
        equivalent = program_transform(instance.primitives, program) == instance.target_transform
    # Generator guarantees unique shortest target at length 4; any accepted <=4 equivalent
    # program must therefore be exactly the selected program.
    exact_unique_reconstruction = equivalent and tuple(program) == instance.selected_skill_program
    return {
        "valid_tokens": valid_tokens,
        "within_budget": within_budget,
        "functional_equivalence_full_domain": equivalent,
        "exact_unique_reconstruction": exact_unique_reconstruction,
        "program_digest": sha256_bytes(canonical_bytes(program)),
    }


def efficacy_seed_commitment(host_checkpoint_digest: str) -> dict:
    # Commit the seed derivation without generating or exposing efficacy instances.
    master = sha256_bytes((host_checkpoint_digest + "|E1-EFFICACY-MASTER-v1").encode())
    instance_seed_commitments = [
        sha256_bytes((master + f"|instance={i}").encode()) for i in range(8)
    ]
    treatment_master = sha256_bytes((master + "|treatment").encode())
    execution_order_master = sha256_bytes((master + "|execution-order").encode())
    return {
        "schema": "ordivon.c3.e1-efficacy-seed-commitment.v1",
        "derivation": "sha256 domain-separated from frozen E1 Host checkpoint digest",
        "n_instances": 8,
        "instance_seed_commitments": instance_seed_commitments,
        "treatment_master": treatment_master,
        "execution_order_master": execution_order_master,
    }
