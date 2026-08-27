from __future__ import annotations

from typing import Any


class RepresentationSelectionError(ValueError):
    pass


def _fail(message: str) -> None:
    raise RepresentationSelectionError(message)


def _nonempty_string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        _fail(f"{where} must be a non-empty trimmed string")
    return value


def _string_set(value: Any, where: str, *, allow_empty: bool = False) -> set[str]:
    if not isinstance(value, list):
        _fail(f"{where} must be an array")
    result: set[str] = set()
    for index, item in enumerate(value):
        text = _nonempty_string(item, f"{where}[{index}]")
        if text in result:
            _fail(f"{where} contains duplicate value: {text}")
        result.add(text)
    if not allow_empty and not result:
        _fail(f"{where} must not be empty")
    return result


def select_representation(request: dict[str, Any]) -> dict[str, Any]:
    """Choose the cheapest caller-declared adequate representation.

    Atlas does not infer which distinctions are semantically required, whether a
    profile is truthful/current, or what a consumer can understand. The caller
    supplies those commitments and measured costs; this function performs only a
    bounded mechanical minimum-cost selection and fails closed when no candidate
    satisfies the declared operation.
    """
    if not isinstance(request, dict):
        _fail("request must be an object")
    allowed = {
        "kind",
        "operationRef",
        "requiredDistinctions",
        "profiles",
        "costMetric",
        "maxCost",
        "consumerConstraintRef",
    }
    extra = set(request) - allowed
    if extra:
        _fail(f"request contains unsupported fields: {sorted(extra)}")
    if request.get("kind") != "ordivon.atlas-representation-selection-request-v0":
        _fail("kind must be ordivon.atlas-representation-selection-request-v0")
    operation_ref = _nonempty_string(request.get("operationRef"), "operationRef")
    required = _string_set(request.get("requiredDistinctions"), "requiredDistinctions")
    metric = _nonempty_string(request.get("costMetric"), "costMetric")
    constraint_ref = request.get("consumerConstraintRef")
    if constraint_ref is not None:
        constraint_ref = _nonempty_string(constraint_ref, "consumerConstraintRef")
    max_cost = request.get("maxCost")
    if max_cost is not None and (not isinstance(max_cost, (int, float)) or isinstance(max_cost, bool) or max_cost < 0):
        _fail("maxCost must be a non-negative number")

    profiles = request.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        _fail("profiles must be a non-empty array")
    seen: set[str] = set()
    evaluated: list[dict[str, Any]] = []
    candidates: list[tuple[float, int, str, dict[str, Any]]] = []
    for index, raw in enumerate(profiles):
        where = f"profiles[{index}]"
        if not isinstance(raw, dict):
            _fail(f"{where} must be an object")
        extra = set(raw) - {"id", "preserves", "measuredCost", "evidenceRefs", "truthRole"}
        if extra:
            _fail(f"{where} contains unsupported fields: {sorted(extra)}")
        pid = _nonempty_string(raw.get("id"), f"{where}.id")
        if pid in seen:
            _fail(f"duplicate profile id: {pid}")
        seen.add(pid)
        preserves = _string_set(raw.get("preserves"), f"{where}.preserves", allow_empty=True)
        cost = raw.get("measuredCost")
        if not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0:
            _fail(f"{where}.measuredCost must be a non-negative number")
        evidence_refs = raw.get("evidenceRefs", [])
        if not isinstance(evidence_refs, list):
            _fail(f"{where}.evidenceRefs must be an array")
        for j, ref in enumerate(evidence_refs):
            _nonempty_string(ref, f"{where}.evidenceRefs[{j}]")
        truth_role = raw.get("truthRole", "caller-declared-profile")
        _nonempty_string(truth_role, f"{where}.truthRole")
        missing = sorted(required - preserves)
        budget_ok = max_cost is None or cost <= max_cost
        adequate = not missing and budget_ok
        row = {
            "id": pid,
            "measuredCost": cost,
            "missingDistinctions": missing,
            "withinMaxCost": budget_ok,
            "adequate": adequate,
            "extraDistinctionCount": len(preserves - required),
            "evidenceRefs": list(evidence_refs),
            "truthRole": truth_role,
        }
        evaluated.append(row)
        if adequate:
            candidates.append((float(cost), len(preserves - required), pid, row))

    if candidates:
        _, _, selected_id, selected_row = min(candidates, key=lambda item: (item[0], item[1], item[2]))
        disposition = "SELECTED_CALLER_DECLARED_ADEQUATE_PROFILE"
    else:
        selected_id = None
        selected_row = None
        disposition = "NO_ADEQUATE_PROFILE"

    return {
        "kind": "ordivon.atlas-representation-selection-v0",
        "operationRef": operation_ref,
        "requiredDistinctions": sorted(required),
        "costMetric": metric,
        "maxCost": max_cost,
        "consumerConstraintRef": constraint_ref,
        "selectionPolicy": "MIN_MEASURED_COST_THEN_MIN_EXCESS_THEN_ID",
        "disposition": disposition,
        "selectedProfileId": selected_id,
        "selectedProfile": selected_row,
        "evaluatedProfiles": evaluated,
        "claims": {
            "semanticRequirementsInferred": False,
            "profileTruthVerified": False,
            "profileCurrentnessVerified": False,
            "consumerCapacityInferred": False,
            "executionAdmissionGranted": False,
            "ownerTruthMinted": False,
        },
        "truthRole": "non-authoritative-mechanical-consumer-projection-selection",
    }
