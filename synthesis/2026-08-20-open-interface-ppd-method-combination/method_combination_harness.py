#!/usr/bin/env python3
"""Mechanical checks for PPD method-combination calibration fixtures.

This script does not generate scientific questions and does not claim prospective
performance. It verifies temporal fences, proposal-component coverage and a
multi-axis separator-receipt closure contract.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
FIXTURE = BASE / "q008-fixture.json"
RECEIPTS = BASE / "separator-receipts-v0.1.json"

GENERATORS = {
    "polarity_only_control": {
        "historically_frozen": False,
        "components": [],
        "note": "same-direction pre-cutoff claims do not trigger pure polarity search",
    },
    "consensus_control": {
        "historically_frozen": False,
        "components": [],
        "note": "cross-dataset agreement alone yields no separator",
    },
    "evidence_graph_v1": {
        "historically_frozen": True,
        "components": [
            "retrieval_assumption_sensitivity",
            "orthogonal_measurement_grounding",
        ],
        "note": "released q_008 asks for independent retrieval frameworks and independent data",
    },
    "genealogy_multiverse_calibration": {
        "historically_frozen": False,
        "components": [
            "improved_systematics_and_bayesian_model_averaging",
            "retrieval_assumption_sensitivity",
        ],
        "note": "retrospective synthetic control representing genealogy + analysis multiverse",
    },
    "orthogonal_calibration": {
        "historically_frozen": False,
        "components": ["orthogonal_measurement_grounding"],
        "note": "retrospective synthetic control representing independent modality acquisition",
    },
}

CHAIN = [
    "P_proposed",
    "X_exact_separator_executed",
    "D_discriminating_result_observed",
    "U_target_claim_updated",
    "R_target_claim_resolved",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def validate_temporal_fence(f: dict) -> list[str]:
    errors = []
    cutoff = f["source_fence"]["cutoff_year"]
    for e in f["pre_cutoff_evidence"]:
        if e["year"] > cutoff:
            errors.append(f"pre-cutoff evidence after cutoff: {e['bibcode']}")
    for e in f["future_adjudication"]:
        if e["year"] <= cutoff:
            errors.append(f"future evidence not after cutoff: {e['bibcode']}")
    pre_codes = {e["bibcode"] for e in f["pre_cutoff_evidence"]}
    future_codes = {e["bibcode"] for e in f["future_adjudication"]}
    if pre_codes & future_codes:
        errors.append("pre/future evidence overlap")
    return errors


def validate_receipt(r: dict) -> list[str]:
    errors = []
    # Closure bits must be prefix-monotone: X=>P, D=>X, U=>D, R=>U.
    for prev, cur in zip(CHAIN, CHAIN[1:]):
        if r.get(cur) and not r.get(prev):
            errors.append(f"{r.get('proposal_id')}: {cur}=true while {prev}=false")
    # Engagement is deliberately outside the closure chain and needs no implication.
    return errors


def evaluate_receipts() -> dict:
    data = load_json(RECEIPTS)
    errors = []
    cases = {}
    for case_id, case in data["cases"].items():
        rows = []
        for r in case["receipts"]:
            errors.extend(validate_receipt(r))
            closure_depth = sum(1 for k in CHAIN if r.get(k))
            rows.append({
                "proposal_id": r["proposal_id"],
                "closure_vector": {k: bool(r.get(k)) for k in CHAIN},
                "E_mechanism_engaged": bool(r.get("E_mechanism_engaged")),
                "closure_depth": closure_depth,
            })
        cases[case_id] = {
            "upstream_outcome": case["upstream_outcome"],
            "case_resolved": case["case_resolved"],
            "receipts": rows,
        }
    return {"errors": errors, "cases": cases}


def evaluate_components() -> dict:
    f = load_json(FIXTURE)
    errors = validate_temporal_fence(f)
    future_components = {e["resolution_component"] for e in f["future_adjudication"]}
    rows = {}
    ecology_union = set()
    frozen_union = set()
    for name, g in GENERATORS.items():
        comps = set(g["components"])
        ecology_union |= comps
        if g["historically_frozen"]:
            frozen_union |= comps
        rows[name] = {
            "historically_frozen": g["historically_frozen"],
            "component_hits": sorted(comps & future_components),
            "coverage": len(comps & future_components) / max(1, len(future_components)),
            "note": g["note"],
        }
    return {
        "passed_mechanical_fence": not errors,
        "errors": errors,
        "future_resolution_components": sorted(future_components),
        "generators": rows,
        "historically_frozen_support_union": sorted(frozen_union),
        "all_calibration_support_union": sorted(ecology_union),
        "guard": "synthetic calibration controls cannot be counted as historical prospective hits",
    }


def evaluate() -> dict:
    components = evaluate_components()
    receipts = evaluate_receipts()
    return {
        "component_calibration": components,
        "separator_receipts": receipts,
        "passed": components["passed_mechanical_fence"] and not receipts["errors"],
        "engagement_guard": "E_mechanism_engaged is not a closure-chain stage and may be true while X/D/U/R are false",
    }


def selftest() -> int:
    x = evaluate()
    assert x["passed"]
    c = x["component_calibration"]
    assert GENERATORS["polarity_only_control"]["components"] == []
    assert GENERATORS["consensus_control"]["components"] == []
    assert set(c["historically_frozen_support_union"]) == {
        "retrieval_assumption_sensitivity",
        "orthogonal_measurement_grounding",
    }
    q001 = {r["proposal_id"]: r for r in x["separator_receipts"]["cases"]["q_001"]["receipts"]}
    assert q001["q001-vertical-shear-common-model"]["E_mechanism_engaged"] is True
    assert q001["q001-vertical-shear-common-model"]["closure_vector"]["X_exact_separator_executed"] is False
    assert q001["q001-analysis-systematics-multiverse"]["closure_vector"]["U_target_claim_updated"] is True
    assert x["separator_receipts"]["cases"]["q_001"]["case_resolved"] is False
    assert x["separator_receipts"]["cases"]["q_008"]["case_resolved"] is True
    print(json.dumps(x, indent=2, sort_keys=True))
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        return selftest()
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
