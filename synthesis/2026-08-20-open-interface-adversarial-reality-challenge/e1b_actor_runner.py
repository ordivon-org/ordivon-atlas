#!/usr/bin/env python3
"""Frozen one-shot actor runner for C3 E1b.

Run under the current Ordivon Harness project environment. One invocation with --index
performs at most one Provider call. Private programs/results are never printed to stdout.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from anc_canonical import canonical_digest
from ordivon_harness.ordivon.deepseek import DeepSeekSettings, DeepSeekTurnAdapter
from ordivon_harness.ordivon.model import AgentTurnRequest

BASE = Path(__file__).resolve().parent
PRIVATE = BASE / "e1b-efficacy-private"
RESULTS = BASE / "e1b-efficacy-results"
MANIFEST_PATH = BASE / "E1B-EFFICACY-PUBLIC-MANIFEST.json"
E1_PATH = BASE / "e1_micro_world.py"
HARNESS_ROOT = Path("/var/lib/ordivon/runtime/workspaces/e1b-harness-frozen-actor-20260828")

EXPECTED = {
    "manifest_sha256": "7043285a7ce1e18d450a0c5d42bdfd994dbf3e9433ee76070c911b5410caef26",
    "e1_sha256": "1dd9dd3dee2299ca5a1e5cc6757f0d946265d84dc35a9e2d928e9ac8528d8b73",
    "harness_head": "09414f06a622397cdfd95dda4d52484f8ef0e9a1",
    "deepseek_sha256": "b9b8f144beb0186e3524bb36ea34af1428ae615b45b44e920d02d057795bfbf1",
    "model_sha256": "6f9609080f425879ca294506c42e632f3fa69069bdc121b46e4284f0bae082dc",
    "completion_sha256": "863a7a0692bf444a3f888f07c74d69aca92d9452a6d57f31b9a6d29db15d6c6d",
    "adapter_id": "deepseek.chat-completions.non-thinking.v1",
    "model": "deepseek-v4-flash",
    "base_url": "https://api.deepseek.com",
    "credential_scope_id": "credential-scope:deepseek:flash:0",
    "max_output_tokens": 512,
    "timeout_seconds": 30.0,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_e1():
    spec = importlib.util.spec_from_file_location("e1_frozen_runner", E1_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_manifest() -> dict[str, Any]:
    if sha256_file(MANIFEST_PATH) != EXPECTED["manifest_sha256"]:
        raise RuntimeError("E1b public manifest digest mismatch")
    value = json.loads(MANIFEST_PATH.read_text())
    if value.get("n_instances") != 8 or value.get("use_count") != 4 or value.get("suppress_count") != 4:
        raise RuntimeError("E1b public manifest cardinality mismatch")
    return value


def check_source_fence() -> None:
    if sha256_file(E1_PATH) != EXPECTED["e1_sha256"]:
        raise RuntimeError("E1 generator digest mismatch")
    head = subprocess.check_output(
        ["git", "-C", str(HARNESS_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != EXPECTED["harness_head"]:
        raise RuntimeError("Harness HEAD mismatch")
    paths = {
        "deepseek_sha256": HARNESS_ROOT / "src/ordivon_harness/ordivon/deepseek.py",
        "model_sha256": HARNESS_ROOT / "src/ordivon_harness/ordivon/model.py",
        "completion_sha256": HARNESS_ROOT / "src/ordivon_harness/completion.py",
    }
    for key, path in paths.items():
        if sha256_file(path) != EXPECTED[key]:
            raise RuntimeError(f"Harness source digest mismatch: {key}")


def settings() -> DeepSeekSettings:
    value = DeepSeekSettings.from_secret_file(
        max_output_tokens=EXPECTED["max_output_tokens"],
        timeout_seconds=EXPECTED["timeout_seconds"],
    )
    if (
        value.model != EXPECTED["model"]
        or value.base_url != EXPECTED["base_url"]
        or value.credential_scope_id != EXPECTED["credential_scope_id"]
    ):
        raise RuntimeError("DeepSeek settings differ from E1 actor seal")
    return value


def row_by_index(manifest: dict[str, Any], index: int) -> dict[str, Any]:
    matches = [row for row in manifest["rows"] if row["index"] == index]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one manifest row for index {index}")
    return matches[0]


def load_private(index: int, row: dict[str, Any], e1) -> dict[str, Any]:
    path = PRIVATE / f"instance-{index:02d}.json"
    if not path.is_file():
        raise RuntimeError(f"private instance missing: {index}")
    if sha256_file(path) != row["private_file_sha256"]:
        raise RuntimeError(f"private instance digest mismatch: {index}")
    value = json.loads(path.read_text())
    inst = value["instance"]
    if inst["instance_digest"] != row["instance_digest"]:
        raise RuntimeError("private/public instance identity mismatch")
    arm = row["arm"]
    content = value[f"actor_user_{arm}"]
    if e1.sha256_bytes(content.encode()) != row["actor_user_digest"]:
        raise RuntimeError("actor user content digest mismatch")
    schema = value["completion_schema"]
    if e1.sha256_bytes(e1.canonical_bytes(schema)) != row["completion_schema_digest"]:
        raise RuntimeError("completion schema digest mismatch")
    if arm == "SUPPRESS":
        # Rehydrate E1Instance only for deterministic closure/evaluation mechanics.
        instance = e1.E1Instance(
            schema=inst["schema"], seed=inst["seed"],
            state_labels=tuple(inst["state_labels"]),
            primitive_order=tuple(inst["primitive_order"]),
            primitives={k: tuple(v) for k, v in inst["primitives"].items()},
            target_transform=tuple(inst["target_transform"]),
            selected_skill_name=inst["selected_skill_name"],
            selected_skill_program=tuple(inst["selected_skill_program"]),
            selected_skill_canary=inst["selected_skill_canary"],
            decoy_skills=tuple((name, tuple(program)) for name, program in inst["decoy_skills"]),
            instance_digest=inst["instance_digest"],
        )
        if not e1.audit_suppress_provider_surface(instance)["closed"]:
            raise RuntimeError("SUPPRESS provider surface no longer carrier-closed")
    return value


def rehydrate_instance(value: dict[str, Any], e1):
    inst = value["instance"]
    return e1.E1Instance(
        schema=inst["schema"], seed=inst["seed"],
        state_labels=tuple(inst["state_labels"]),
        primitive_order=tuple(inst["primitive_order"]),
        primitives={k: tuple(v) for k, v in inst["primitives"].items()},
        target_transform=tuple(inst["target_transform"]),
        selected_skill_name=inst["selected_skill_name"],
        selected_skill_program=tuple(inst["selected_skill_program"]),
        selected_skill_canary=inst["selected_skill_canary"],
        decoy_skills=tuple((name, tuple(program)) for name, program in inst["decoy_skills"]),
        instance_digest=inst["instance_digest"],
    )


def preflight() -> dict[str, Any]:
    check_source_fence()
    manifest = load_manifest()
    e1 = load_e1()
    s = settings()
    for row in manifest["rows"]:
        load_private(row["index"], row, e1)
    if DeepSeekTurnAdapter.adapter_id != EXPECTED["adapter_id"]:
        raise RuntimeError("adapter ID mismatch")
    return {
        "status": "E1B_ACTOR_PREFLIGHT_PASS",
        "instances": 8,
        "use": 4,
        "suppress": 4,
        "model": s.model,
        "adapter": DeepSeekTurnAdapter.adapter_id,
        "manifest_sha256": EXPECTED["manifest_sha256"],
    }


def run_one(index: int) -> dict[str, Any]:
    check_source_fence()
    manifest = load_manifest()
    e1 = load_e1()
    row = row_by_index(manifest, index)
    private = load_private(index, row, e1)
    instance = rehydrate_instance(private, e1)
    arm = row["arm"]
    content = private[f"actor_user_{arm}"]
    completion_schema = private["completion_schema"]
    s = settings()
    completion_contract = {
        "mode": "structured-result-v1",
        "resultKind": "c3-e1b-program",
        "resultSchema": completion_schema,
    }
    adapter = DeepSeekTurnAdapter(s, completion_contract=completion_contract)
    request = AgentTurnRequest(
        harness_run_id=f"harness-run:c3-e1b:{index:02d}",
        turn_id=f"turn:c3-e1b:{index:02d}:1",
        sequence=1,
        assignment_id=f"assignment:c3-e1b:{index:02d}",
        context_digest=canonical_digest({
            "e1b": "efficacy-context-v1",
            "instanceDigest": row["instance_digest"],
            "actorUserDigest": row["actor_user_digest"],
        }),
        tool_catalog_digest=canonical_digest({
            "e1b": "no-runtime-tools-v1",
            "harnessAction": "submit_run_conclusion",
        }),
        messages=({"role": "user", "content": content},),
        tools=(),
        remaining_budget={"modelCalls": 1, "toolCalls": 0, "totalTokens": 16_384},
    )
    provider_request_digest = adapter.provider_request_digest(request)
    record: dict[str, Any] = {
        "schema": "ordivon.c3.e1b-actor-result.v1",
        "index": index,
        "arm": arm,
        "instance_digest": row["instance_digest"],
        "actor_user_digest": row["actor_user_digest"],
        "completion_schema_digest": row["completion_schema_digest"],
        "provider_request_digest": provider_request_digest,
        "requested_model": EXPECTED["model"],
        "adapter_id": EXPECTED["adapter_id"],
        "provider_dispatched": False,
        "certified": False,
    }
    try:
        record["provider_dispatched"] = True
        result = adapter.invoke(request)
        record.update({
            "effective_model": result.effective_model_id or result.model_id,
            "finish_reason": result.finish_reason,
            "usage": result.usage,
            "raw_response_digest": result.raw_response_digest,
            "runtime_tool_call_count": len(result.tool_calls),
            "content_digest": (
                hashlib.sha256(result.content.encode()).hexdigest()
                if isinstance(result.content, str) else None
            ),
            "conclusion_present": result.conclusion is not None,
        })
        if (result.effective_model_id or result.model_id) != EXPECTED["model"]:
            record["disposition"] = "invalid_effective_model"
        elif result.tool_calls:
            record["disposition"] = "invalid_runtime_tool_call"
        elif result.conclusion is None:
            record["disposition"] = "missing_conclusion"
        elif result.conclusion.status != "candidate_completed":
            record["disposition"] = "needs_input"
            record["conclusion_status"] = result.conclusion.status
        else:
            record["conclusion_status"] = result.conclusion.status
            try:
                value = json.loads(result.conclusion.summary)
                program = value.get("program") if isinstance(value, dict) else None
                if not isinstance(program, list) or any(not isinstance(x, str) for x in program):
                    record["disposition"] = "malformed_program"
                else:
                    evaluation = e1.evaluate_program(instance, program)
                    record["program"] = program
                    record["evaluation"] = evaluation
                    record["disposition"] = (
                        "certified_reconstruction"
                        if evaluation["exact_unique_reconstruction"]
                        else "non_reconstruction"
                    )
                    record["certified"] = bool(evaluation["exact_unique_reconstruction"])
            except Exception as exc:
                record["disposition"] = "malformed_conclusion"
                record["parse_error_type"] = type(exc).__name__
    except Exception as exc:
        # Frozen no-retry policy: preserve the first failure classification and stop.
        record["disposition"] = "provider_or_adapter_failure"
        record["error_type"] = type(exc).__name__
        record["error_digest"] = hashlib.sha256(str(exc).encode()).hexdigest()
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"result-{index:02d}.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    out.chmod(0o600)
    return {
        "index": index,
        "arm": arm,
        "result_file_sha256": sha256_file(out),
        "delivery_recorded": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--index", type=int)
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(), sort_keys=True))
        return
    if args.index is None or not 0 <= args.index < 8:
        raise SystemExit("--index 0..7 required")
    print(json.dumps(run_one(args.index), sort_keys=True))


if __name__ == "__main__":
    main()
