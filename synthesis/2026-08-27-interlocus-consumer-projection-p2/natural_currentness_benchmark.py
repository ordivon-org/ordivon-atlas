#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(label: str, args: list[str], repeats: int = 3) -> dict:
    rows = []
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    for _ in range(repeats):
        started = time.perf_counter()
        proc = subprocess.run([sys.executable, "-m", "ordivon_atlas", *args], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120)
        elapsed_ms = (time.perf_counter() - started) * 1000
        rows.append({"exitCode": proc.returncode, "stdoutBytes": len(proc.stdout), "stderrBytes": len(proc.stderr), "elapsedMs": round(elapsed_ms, 3)})
    return {
        "label": label,
        "args": args,
        "runs": rows,
        "medianStdoutBytes": statistics.median(row["stdoutBytes"] for row in rows),
        "medianElapsedMs": round(statistics.median(row["elapsedMs"] for row in rows), 3),
        "allExitZero": all(row["exitCode"] == 0 for row in rows),
    }

def main() -> int:
    workflows = [
        run("owner-scoped-compact", ["check-owner", "Interlocus"]),
        run("owner-scoped-expanded", ["check-owner", "Interlocus", "--include-publication"]),
        run("whole-registry", ["check"]),
    ]
    result = {
        "kind": "ordivon.atlas-natural-currentness-consumer-benchmark-v0",
        "date": "2026-08-27",
        "repeats": 3,
        "workflows": workflows,
        "claims": {
            "semanticCorrectnessMeasured": False,
            "llmBehaviorMeasured": False,
            "mechanicalReadCostMeasured": True,
            "executionAdmissionGranted": False
        },
        "truthRole": "read-only-mechanical-consumer-measurement"
    }
    compact = workflows[0]["medianStdoutBytes"]
    expanded = workflows[1]["medianStdoutBytes"]
    whole = workflows[2]["medianStdoutBytes"]
    result["derived"] = {
        "compactVsExpandedByteReductionFraction": None if not expanded else round(1 - compact / expanded, 6),
        "compactVsWholeRegistryByteReductionFraction": None if not whole else round(1 - compact / whole, 6)
    }
    out = Path(__file__).with_name("natural-currentness-benchmark.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all(item["allExitZero"] for item in workflows) else 2

if __name__ == "__main__":
    raise SystemExit(main())
