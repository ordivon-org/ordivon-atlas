#!/usr/bin/env python3
"""Mechanical hidden-channel firewall audit for the WR/WP-I/WP-G/WA benchmark.

Stdlib-only. This is a controller integrity harness, not a physical benchmark.
It checks explicit forbidden tokens/keys and estimates whether any single metadata
feature predicts hidden arm/A-B above a configured tolerance.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HIDDEN_ARMS = ("WR", "WP-I", "WP-G", "WA")
HIDDEN_AB = ("A", "B")

DENIED_KEY_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"world|condition|arm_name|hidden_arm",
        r"owner.*seed|random.*seed|assignment",
        r"actuator.*(side|axis|coord)|motor.*(side|axis|coord)",
        r"nuisance|clamp.*preload|cable.*flex|contact.*state",
        r"camera|rgb.?d|depth|active.*geometry",
        r"fixture.*serial|cartridge.*serial",
        r"owner.*(left|right)|raw.*(left|right)|branch.*(left|right)",
    )
]

DENIED_VALUE_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"\bWR\b|\bWP-I\b|\bWP-G\b|\bWA\b",
        r"\bleft\b|\bright\b|\bLHS\b|\bRHS\b",
        r"world[_:/-]?(wr|wp|wa)",
        r"condition[_:/-]?[ab]\b",
        r"seed[_:= -]?\d+",
        r"fixture[_:/-]?(wr|wp|wa|a|b)[-_]?\d*",
    )
]

SAFE_KEYS = {
    "episode_id",
    "relative_time_ms",
    "budget_remaining",
    "channel_id",
    "measurement",
    "status",
    "action",
    "receipt_id",
    "error_code",
}


@dataclass(frozen=True)
class Episode:
    hidden_arm: str
    hidden_ab: str
    transcript: dict[str, Any]


def flatten(prefix: str, obj: Any) -> Iterable[tuple[str, str]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            yield from flatten(key, v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(f"{prefix}[{i}]", v)
    else:
        yield prefix, str(obj)


def explicit_leaks(transcript: dict[str, Any]) -> list[str]:
    leaks: list[str] = []
    for key, value in flatten("", transcript):
        if any(p.search(key) for p in DENIED_KEY_PATTERNS):
            leaks.append(f"denied-key:{key}")
        if any(p.search(value) for p in DENIED_VALUE_PATTERNS):
            leaks.append(f"denied-value:{key}={value}")
        # Unknown metadata keys are not automatically a leak, but flag obviously
        # non-contract top-level-ish fields for review.
        root = key.split(".", 1)[0].split("[", 1)[0]
        if root and root not in SAFE_KEYS and root not in {"events", "metadata"}:
            if root.startswith("debug_") or root.startswith("owner_"):
                leaks.append(f"suspicious-key:{key}")
    return sorted(set(leaks))


def categorical_signature(transcript: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in flatten("", transcript):
        # Exclude actual scientific measurement values. We want metadata-only leakage.
        if "measurement" in key.lower():
            continue
        s = value
        if len(s) > 80:
            s = s[:80]
        out[key] = s
    return out


def best_single_feature_accuracy(episodes: list[Episode], target: str) -> tuple[float, str]:
    """Deterministic train/test decision-stump audit over categorical metadata.

    For each feature, learn majority target label per feature value on first 2/3 and
    score on last 1/3. Unknown values fall back to global train majority.
    """
    if len(episodes) < 12:
        return 0.0, "insufficient-data"
    train_n = (2 * len(episodes)) // 3
    train = episodes[:train_n]
    test = episodes[train_n:]
    target_fn = (lambda e: e.hidden_arm) if target == "arm" else (lambda e: e.hidden_ab)
    global_majority = Counter(target_fn(e) for e in train).most_common(1)[0][0]

    feature_names = sorted({k for e in episodes for k in categorical_signature(e.transcript)})
    best = (0.0, "none")
    for feature in feature_names:
        by_value: dict[str, Counter[str]] = defaultdict(Counter)
        for e in train:
            sig = categorical_signature(e.transcript)
            if feature in sig:
                by_value[sig[feature]][target_fn(e)] += 1
        mapping = {v: c.most_common(1)[0][0] for v, c in by_value.items()}
        correct = 0
        for e in test:
            sig = categorical_signature(e.transcript)
            pred = mapping.get(sig.get(feature, "__MISSING__"), global_majority)
            correct += pred == target_fn(e)
        acc = correct / max(1, len(test))
        if acc > best[0]:
            best = (acc, feature)
    return best


def synthetic_episodes(n: int, leaky: bool, seed: int) -> list[Episode]:
    rng = random.Random(seed)
    episodes: list[Episode] = []
    # Cycle labels to avoid class imbalance artifacts.
    for i in range(n):
        arm = HIDDEN_ARMS[i % len(HIDDEN_ARMS)]
        ab = HIDDEN_AB[(i // len(HIDDEN_ARMS)) % 2]
        rng.random()  # deterministic perturbation to avoid a trivial pure index pattern
        t: dict[str, Any] = {
            "episode_id": f"ep_{rng.getrandbits(64):016x}",
            "relative_time_ms": i % 17,
            "budget_remaining": 100 - (i % 11),
            "channel_id": f"ch_{rng.randrange(4)}",
            "measurement": round(rng.gauss(0.0, 1.0), 6),
            "status": "ok" if i % 13 else "retryable",
            "action": "read_old" if i % 3 else "repeat_probe",
            "receipt_id": f"rcpt_{rng.getrandbits(48):012x}",
            "error_code": "NONE" if i % 19 else "E_RETRY",
            "metadata": {"protocol_version": "v0", "transport": "local"},
        }
        if leaky:
            # Intentional leaks of several types: direct labels, correlated serial,
            # actuator semantics, and error metadata.
            t["metadata"]["hidden_arm"] = arm
            t["metadata"]["fixture_serial"] = f"fixture-{arm}-{ab}-{i%5}"
            t["metadata"]["actuator_side"] = "left" if ab == "A" else "right"
            if i % 19 == 0:
                t["debug_owner_seed"] = f"seed={seed+i} condition_{ab}"
        episodes.append(Episode(arm, ab, t))
    rng.shuffle(episodes)
    return episodes


def audit(episodes: list[Episode], arm_tolerance: float, ab_tolerance: float) -> dict[str, Any]:
    explicit: list[dict[str, Any]] = []
    for idx, e in enumerate(episodes):
        leaks = explicit_leaks(e.transcript)
        if leaks:
            explicit.append({"index": idx, "leaks": leaks[:20]})
    arm_acc, arm_feature = best_single_feature_accuracy(episodes, "arm")
    ab_acc, ab_feature = best_single_feature_accuracy(episodes, "ab")
    passed = not explicit and arm_acc <= arm_tolerance and ab_acc <= ab_tolerance
    return {
        "passed": passed,
        "episodes": len(episodes),
        "explicit_leak_episode_count": len(explicit),
        "explicit_examples": explicit[:5],
        "metadata_classifier": {
            "arm_best_accuracy": round(arm_acc, 6),
            "arm_best_feature": arm_feature,
            "arm_tolerance": arm_tolerance,
            "ab_best_accuracy": round(ab_acc, 6),
            "ab_best_feature": ab_feature,
            "ab_tolerance": ab_tolerance,
        },
    }


def selftest() -> int:
    # Chance is 0.25 for arm and 0.5 for A/B. Tolerances are intentionally loose
    # for a small synthetic test; real preregistration must use confidence bounds.
    clean = audit(synthetic_episodes(800, False, 20260820), 0.38, 0.63)
    leaky = audit(synthetic_episodes(800, True, 20260820), 0.38, 0.63)
    result = {"clean": clean, "intentionally_leaky": leaky}
    print(json.dumps(result, indent=2, sort_keys=True))
    if not clean["passed"]:
        return 2
    if leaky["passed"]:
        return 3
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--input", type=Path, help="JSONL with hidden_arm, hidden_ab, transcript")
    p.add_argument("--arm-tolerance", type=float, default=0.38)
    p.add_argument("--ab-tolerance", type=float, default=0.63)
    args = p.parse_args()
    if args.selftest:
        return selftest()
    if not args.input:
        p.error("--input or --selftest required")
    episodes: list[Episode] = []
    for line in args.input.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        episodes.append(Episode(row["hidden_arm"], row["hidden_ab"], row["transcript"]))
    result = audit(episodes, args.arm_tolerance, args.ab_tolerance)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
