#!/usr/bin/env python3
"""Frozen model-free R1 pursuit harness for the Cooper medchem fixture.

The analysis family and thresholds were frozen before SUMMARY_NMR reveal in
commit 91e0d93decdb66a6b37382f206b59557169d6c6b. This script operates only on
the blinded R1 peak-summary payload and never contains the owner anomaly key.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

BASE = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE / "cooper-r1-summary-blinded-v0.1.json"

TOL_PPM = 0.10
BIN_WIDTH = 0.25
PPM_LO = -2.0
PPM_HI = 20.0
TOP_K = 3
MIN_TOPK_ROUTES = 2


def mad(values: list[float]) -> float:
    med = statistics.median(values)
    return statistics.median([abs(v - med) for v in values])


def robust_count_score(n: int, peers: list[int]) -> float:
    med = statistics.median(peers)
    return abs(n - med) / max(mad([float(x) for x in peers]), 1.0)


def peakset_distance(a: list[float], b: list[float], tol: float = TOL_PPM) -> float:
    used = [False] * len(b)
    matches = 0
    for v in a:
        best = None
        best_d = None
        for j, w in enumerate(b):
            if used[j]:
                continue
            d = abs(v - w)
            if d <= tol and (best_d is None or d < best_d):
                best, best_d = j, d
        if best is not None:
            used[best] = True
            matches += 1
    if not a and not b:
        return 0.0
    if not a or not b:
        return 1.0
    precision = matches / len(a)
    recall = matches / len(b)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return 1.0 - f1


def occupancy(values: list[float]) -> list[int]:
    n_bins = int((PPM_HI - PPM_LO) / BIN_WIDTH)
    out = [0] * n_bins
    for v in values:
        if PPM_LO <= v < PPM_HI:
            idx = min(n_bins - 1, int((v - PPM_LO) / BIN_WIDTH))
            out[idx] = 1
    return out


def hamming(a: list[int], b: list[int]) -> float:
    return sum(x != y for x, y in zip(a, b)) / len(a)


def centroid(items: list[list[int]]) -> list[int]:
    return [1 if sum(row[i] for row in items) / len(items) >= 0.5 else 0 for i in range(len(items[0]))]


def ranks(scores: dict[str, float]) -> tuple[dict[str, int], list[str]]:
    order = sorted(scores, key=lambda k: (-scores[k], k))
    return {k: i + 1 for i, k in enumerate(order)}, order


def evaluate(path: Path = DEFAULT_INPUT) -> dict:
    payload = json.loads(path.read_text())
    rows = {r["opaque_id"]: r for r in payload["samples"]}
    peaks = {oid: sorted(set(round(float(v), 4) for v in r["peaks_ppm"] if PPM_LO <= float(v) <= PPM_HI)) for oid, r in rows.items()}
    reagent = {oid: rows[oid]["intended_chemistry"]["reagent"] for oid in rows}

    a1: dict[str, float] = {}
    a2: dict[str, float] = {}
    a3: dict[str, float] = {}
    occ = {oid: occupancy(vals) for oid, vals in peaks.items()}
    a4: dict[str, float] = {}

    for oid, vals in peaks.items():
        same_ids = [x for x in peaks if x != oid and reagent[x] == reagent[oid]]
        global_ids = [x for x in peaks if x != oid]

        same_counts = [len(peaks[x]) for x in same_ids]
        global_counts = [len(peaks[x]) for x in global_ids]
        a1[oid] = max(robust_count_score(len(vals), same_counts), robust_count_score(len(vals), global_counts))

        a2[oid] = min(peakset_distance(vals, peaks[x]) for x in same_ids)
        a3[oid] = min(peakset_distance(vals, peaks[x]) for x in global_ids)

        same_occ = [occ[x] for x in same_ids]
        global_occ = [occ[x] for x in global_ids]
        a4[oid] = max(hamming(occ[oid], centroid(same_occ)), hamming(occ[oid], centroid(global_occ)))

    methods = {"A1": a1, "A2": a2, "A3": a3, "A4": a4}
    method_ranks: dict[str, dict[str, int]] = {}
    orders: dict[str, list[str]] = {}
    for name, scores in methods.items():
        method_ranks[name], orders[name] = ranks(scores)

    topk_counts = {oid: sum(method_ranks[m][oid] <= TOP_K for m in methods) for oid in rows}
    broad_candidates = sorted([oid for oid, n in topk_counts.items() if n >= MIN_TOPK_ROUTES])

    claim_universe = sorted([oid for oid, r in rows.items() if bool(r["R0_MS_PASS"])])
    claim_candidates = sorted([oid for oid in broad_candidates if oid in claim_universe])

    avg_rank = {oid: sum(method_ranks[m][oid] for m in methods) / len(methods) for oid in rows}
    rank_union = sorted(avg_rank, key=lambda x: (avg_rank[x], x))

    return {
        "fixture_id": payload["fixture_id"],
        "analysis_freeze_commit": "91e0d93decdb66a6b37382f206b59557169d6c6b",
        "input_source_fence": payload["source_fence"],
        "frozen_parameters": {
            "peak_match_tolerance_ppm": TOL_PPM,
            "occupancy_bin_width_ppm": BIN_WIDTH,
            "occupancy_range_ppm": [PPM_LO, PPM_HI],
            "top_k": TOP_K,
            "minimum_topk_routes": MIN_TOPK_ROUTES,
        },
        "peak_counts": {oid: len(peaks[oid]) for oid in sorted(peaks)},
        "scores": {name: {oid: round(score, 8) for oid, score in sorted(vals.items())} for name, vals in methods.items()},
        "orders": orders,
        "top3_route_count": topk_counts,
        "rank_union": rank_union,
        "broad_candidate_set": broad_candidates,
        "claim_relative_universe_R0_MS_PASS": claim_universe,
        "claim_relative_candidate_set": claim_candidates,
        "routing_metrics": {
            "broad_candidate_fraction": len(broad_candidates) / len(rows),
            "claim_relative_followup_fraction": len(claim_candidates) / len(claim_universe),
            "claim_relative_compression_fraction": 1.0 - len(claim_candidates) / len(claim_universe),
        },
        "guards": [
            "No owner anomaly key is present in this participant-side harness.",
            "Candidate status is pursuit routing, not exact structural identification.",
            "R0_MS_PASS restriction is claim-relative: only incumbent successful-product claims are being challenged.",
            "No A1-A4 threshold or weight is tuned after R1 reveal.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(args.input)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
