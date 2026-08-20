#!/usr/bin/env python3
"""Mechanical checks for the q_008 PPD method-combination calibration fixture.

This script does not generate scientific questions and does not claim prospective
performance. It verifies temporal source fences and evaluates frozen proposal
component coverage versus the documented future resolution.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
FIXTURE = BASE / "q008-fixture.json"

# Abstract proposal supports for calibration. Only evidence_graph_v1 is a real
# historically frozen generator output. Other entries are protocol-level
# generator classes and are marked as synthetic calibration controls.
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
        "note": "synthetic control representing genealogy + analysis multiverse",
    },
    "orthogonal_calibration": {
        "historically_frozen": False,
        "components": ["orthogonal_measurement_grounding"],
        "note": "synthetic control representing independent modality acquisition",
    },
}


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text())


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


def evaluate() -> dict:
    f = load_fixture()
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


def selftest() -> int:
    x = evaluate()
    assert x["passed_mechanical_fence"]
    assert GENERATORS["polarity_only_control"]["components"] == []
    assert GENERATORS["consensus_control"]["components"] == []
    assert set(x["historically_frozen_support_union"]) == {
        "retrieval_assumption_sensitivity",
        "orthogonal_measurement_grounding",
    }
    assert "improved_systematics_and_bayesian_model_averaging" in x["all_calibration_support_union"]
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
