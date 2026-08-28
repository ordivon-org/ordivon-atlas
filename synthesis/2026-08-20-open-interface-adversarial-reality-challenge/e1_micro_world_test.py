#!/usr/bin/env python3
"""No-model mechanics smoke for E1 preregistration."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("e1", HERE / "e1_micro_world.py")
e1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = e1
spec.loader.exec_module(e1)


def main():
    mechanics_seed = "E1-MECHANICS-v1-20260822"
    inst = e1.generate_instance(mechanics_seed)
    receipt = e1.hidden_receipt(inst)

    # Generator qualification: selected program is the unique shortest length-4 solution.
    best = e1.shortest_programs(inst.primitives, e1.TARGET_MIN_LEN)
    progs = best[inst.target_transform]
    assert len(progs) == 1
    assert len(progs[0]) == e1.TARGET_MIN_LEN
    assert progs[0] == inst.selected_skill_program

    # Receipt is deterministic and uniquely selects the target skill among decoys.
    receipt2 = e1.hidden_receipt(inst)
    assert receipt == receipt2

    use_req = e1.arm_request(inst, "USE")
    sup_req = e1.arm_request(inst, "SUPPRESS")
    assert use_req["base"] == sup_req["base"]
    assert use_req["skill_context"]["program"] == list(inst.selected_skill_program)
    assert sup_req["skill_context"]["selected_skill"] is None

    closure = e1.audit_suppress_carrier_closure(inst, sup_req)
    assert closure["closed"] is True
    provider_closure = e1.audit_suppress_provider_surface(inst)
    assert provider_closure["closed"] is True
    use_user = e1.actor_user_payload(inst, "USE")
    sup_user = e1.actor_user_payload(inst, "SUPPRESS")
    assert use_user["instruction"] == sup_user["instruction"]
    assert use_user["instance"]["base"] == sup_user["instance"]["base"]
    assert inst.selected_skill_canary not in e1.actor_user_content(inst, "USE")
    schema = e1.completion_schema(inst)
    assert schema["properties"]["program"]["maxItems"] == 4
    assert set(schema["properties"]["program"]["items"]["enum"]) == set(inst.primitive_order)

    # Hidden correct program must certify on the full domain.
    good = e1.evaluate_program(inst, list(inst.selected_skill_program))
    assert good["functional_equivalence_full_domain"] is True
    assert good["exact_unique_reconstruction"] is True

    # Single-token perturbation must fail.
    wrong = list(inst.selected_skill_program)
    alternatives = [p for p in inst.primitive_order if p != wrong[-1]]
    wrong[-1] = alternatives[0]
    bad = e1.evaluate_program(inst, wrong)
    assert bad["exact_unique_reconstruction"] is False

    # An unrelated decoy program must fail the target equivalence certificate.
    decoy = list(inst.decoy_skills[0][1])
    decoy_eval = e1.evaluate_program(inst, decoy)
    assert decoy_eval["functional_equivalence_full_domain"] is False

    # Seed commitment is generated without constructing efficacy task instances.
    commitment = e1.efficacy_seed_commitment(
        "sha256:66e89fffad760c3dd32ee0517717a261df510602ece2a6ea3b8d11458973bc4c"
    )
    assert commitment["n_instances"] == 8
    assert len(set(commitment["instance_seed_commitments"])) == 8
    dummy_digests = [e1.sha256_bytes(f"dummy-{i}".encode()) for i in range(8)]
    assignment = e1.blocked_treatment_assignment(dummy_digests, commitment["treatment_master"])
    assert list(assignment.values()).count("USE") == 4
    assert list(assignment.values()).count("SUPPRESS") == 4
    run_order = e1.execution_order(dummy_digests, commitment["execution_order_master"])
    assert sorted(run_order) == sorted(dummy_digests)

    out = {
        "status": "E1_NO_MODEL_MECHANICS_PASS",
        "mechanics_instance_digest": inst.instance_digest,
        "receipt_digest": receipt["receipt_digest"],
        "selected_program_length": len(inst.selected_skill_program),
        "unique_shortest_programs": len(progs),
        "use_suppress_common_base": use_req["base"] == sup_req["base"],
        "suppress_carrier_closed": closure["closed"],
        "correct_program_full_domain_equivalent": good["functional_equivalence_full_domain"],
        "perturbed_program_rejected": not bad["exact_unique_reconstruction"],
        "decoy_program_rejected": not decoy_eval["functional_equivalence_full_domain"],
        "efficacy_seed_commitment": commitment,
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
