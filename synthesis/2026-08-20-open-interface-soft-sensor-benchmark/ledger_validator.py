#!/usr/bin/env python3
"""Machine-checkable validators for WP-I C0 membership and WP-G operator artifacts."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent


def load(name: str) -> Any:
    return json.loads((BASE / name).read_text())


def sha256_obj(x: Any) -> str:
    b=json.dumps(x, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:"+hashlib.sha256(b).hexdigest()


def validate_param(spec: dict[str, Any], value: Any) -> bool:
    if spec["type"] == "number":
        if not isinstance(value, (int,float)) or isinstance(value,bool): return False
    elif spec["type"] == "integer":
        if not isinstance(value,int) or isinstance(value,bool): return False
    else: return False
    if value < spec["min"] or value > spec["max"]: return False
    if value in spec.get("forbid", []): return False
    return True


def validate_wp_i_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    ledger=load("wp_i_templates.json")
    templates={t["template_id"]:t for t in ledger["templates"]}
    tid=candidate.get("template_id")
    if tid not in templates: return {"valid":False,"reason":"template_not_in_frozen_C0"}
    t=templates[tid]
    params=candidate.get("parameters",{})
    if set(params)!=set(t["parameters"]): return {"valid":False,"reason":"parameter_set_mismatch"}
    for k,spec in t["parameters"].items():
        if not validate_param(spec, params[k]): return {"valid":False,"reason":f"invalid_parameter:{k}"}
    if candidate.get("readout_contract") != t["readout_contract"]:
        return {"valid":False,"reason":"readout_contract_mismatch"}
    return {
        "valid":True,
        "reason":"member_of_frozen_C0_template_family",
        "ledger_digest":sha256_obj(ledger),
        "candidate_digest":sha256_obj(candidate),
    }


def validate_operator_artifact(artifact: dict[str, Any], requested_state: str="digest_frozen") -> dict[str, Any]:
    schema=load("operator_artifact_schema.json")
    missing=[k for k in schema["required"] if k not in artifact]
    if missing: return {"valid":False,"reason":"missing_required","missing":missing}
    if requested_state in schema["physical_only_states"]:
        return {"valid":False,"reason":"physical_receipt_required","requested_state":requested_state}
    if requested_state not in schema["pre_physical_validation_states"]:
        return {"valid":False,"reason":"unknown_state"}
    return {"valid":True,"state":requested_state,"artifact_digest":sha256_obj(artifact),"schema_digest":sha256_obj(schema)}


def selftest() -> dict[str, Any]:
    good={"template_id":"offset_path_v0","parameters":{"offset_norm":0.35,"path_width_norm":0.1,"serpentine_turns":3},"readout_contract":"aux_resistance_scalar_v0"}
    zero={"template_id":"offset_path_v0","parameters":{"offset_norm":0.0,"path_width_norm":0.1,"serpentine_turns":3},"readout_contract":"aux_resistance_scalar_v0"}
    unknown={"template_id":"invented_after_event","parameters":{},"readout_contract":"x"}
    op={k:f"value_{k}" for k in load("operator_artifact_schema.json")["required"]}
    results={
        "wp_i_good":validate_wp_i_candidate(good),
        "wp_i_forbidden_zero":validate_wp_i_candidate(zero),
        "wp_i_unknown_template":validate_wp_i_candidate(unknown),
        "operator_digest_freeze":validate_operator_artifact(op,"digest_frozen"),
        "operator_fake_physical_admission":validate_operator_artifact(op,"registry_admitted"),
    }
    assert results["wp_i_good"]["valid"]
    assert not results["wp_i_forbidden_zero"]["valid"]
    assert not results["wp_i_unknown_template"]["valid"]
    assert results["operator_digest_freeze"]["valid"]
    assert not results["operator_fake_physical_admission"]["valid"]
    return results


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--selftest",action="store_true"); a=p.parse_args()
    if a.selftest:
        print(json.dumps(selftest(),indent=2,sort_keys=True)); return 0
    p.error("--selftest required")

if __name__=="__main__": raise SystemExit(main())
