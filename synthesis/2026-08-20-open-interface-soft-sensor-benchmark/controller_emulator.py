#!/usr/bin/env python3
"""Owner-only semantic controller emulator for WR/WP-I/WP-G/WA.

This is not a physical simulator and not an agent benchmark. It mechanically
checks state transitions, budget/repair commitment, transcript scrubbing and
hash-chained immutable receipts before physical hardware exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
from dataclasses import dataclass, field
from typing import Any

STATES = ("S0_FREEZE", "S1_ARM", "S2_EXPOSURE", "S3_DIAGNOSTIC", "S4_COMMIT", "S5_ADJUDICATE")
ARMS = ("WR", "WP-I", "WP-G", "WA")
REPAIRS = (
    "reanalyze_existing_history",
    "ground_or_randomize_nuisance",
    "materialize_existing_closure",
    "author_new_measurement_operator",
    "reject_target_distinction",
)

AGENT_ALLOWED_EVENT_KEYS = {
    "episode_id", "relative_time_ms", "budget_remaining", "channel_id",
    "measurement", "status", "action", "receipt_id", "error_code", "metadata",
}
HIDDEN_KEYS = {
    "hidden_arm", "hidden_ab", "owner_seed", "owner_randomization_seed",
    "actuator_side", "actuator_coordinate", "motor_axis", "nuisance_state",
    "clamp_preload", "cable_flex", "active_camera", "active_geometry",
    "fixture_serial", "cartridge_serial", "owner_left_channel", "owner_right_channel",
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


@dataclass
class ReceiptChain:
    previous: str = "sha256:" + "0" * 64
    receipts: list[dict[str, Any]] = field(default_factory=list)

    def append(self, kind: str, body: dict[str, Any]) -> dict[str, Any]:
        # Freeze the receipt body by canonical round-trip so later mutation of a
        # caller-owned event cannot invalidate the already-issued digest.
        frozen_body = json.loads(canonical(body).decode())
        core = {"kind": kind, "previous": self.previous, "body": frozen_body}
        rid = digest(core)
        rec = {**core, "receipt_id": rid}
        self.receipts.append(rec)
        self.previous = rid
        return rec


@dataclass
class Controller:
    total_budget: int = 100
    state: str = "S0_FREEZE"
    budget: int = 100
    episode_id: str | None = None
    hidden_arm: str | None = None
    hidden_ab: str | None = None
    repair_commitment: str | None = None
    chain: ReceiptChain = field(default_factory=ReceiptChain)
    frozen_hashes: dict[str, str] = field(default_factory=dict)

    def freeze(self, artifacts: dict[str, Any]) -> dict[str, Any]:
        if self.state != "S0_FREEZE":
            raise RuntimeError("freeze only allowed in S0")
        self.frozen_hashes = {k: digest(v) for k, v in sorted(artifacts.items())}
        r = self.chain.append("freeze", {"artifact_hashes": self.frozen_hashes, "budget": self.total_budget})
        self.state = "S1_ARM"
        return r

    def arm(self, hidden_arm: str, hidden_ab: str, owner_seed: int) -> dict[str, Any]:
        if self.state != "S1_ARM":
            raise RuntimeError("arm only allowed in S1")
        if hidden_arm not in ARMS or hidden_ab not in {"A", "B"}:
            raise ValueError("invalid hidden condition")
        # opaque public id is not derived from labels/seed
        self.episode_id = "ep_" + secrets.token_hex(12)
        self.hidden_arm, self.hidden_ab = hidden_arm, hidden_ab
        r = self.chain.append("owner_arm", {
            "episode_id": self.episode_id,
            "hidden_arm": hidden_arm,
            "hidden_ab": hidden_ab,
            "owner_seed": owner_seed,
        })
        self.state = "S2_EXPOSURE"
        return r

    def expose(self, measurement: float = 0.0) -> dict[str, Any]:
        if self.state != "S2_EXPOSURE":
            raise RuntimeError("exposure only allowed in S2")
        self.state = "S3_DIAGNOSTIC"
        return self._public_event("initial_exposure", measurement=measurement)

    def diagnostic(self, action: str, cost: int, measurement: float | None = None) -> dict[str, Any]:
        if self.state != "S3_DIAGNOSTIC":
            raise RuntimeError("diagnostics only allowed in S3")
        if cost < 0 or cost > self.budget:
            raise RuntimeError("budget exceeded")
        self.budget -= cost
        return self._public_event(action, measurement=measurement)

    def commit_repair(self, repair: str, cost: int) -> dict[str, Any]:
        if self.state != "S3_DIAGNOSTIC":
            raise RuntimeError("repair commitment only allowed after diagnostics")
        if self.repair_commitment is not None:
            raise RuntimeError("only one primary repair commitment allowed")
        if repair not in REPAIRS:
            raise ValueError("unknown repair")
        if cost < 0 or cost > self.budget:
            raise RuntimeError("budget exceeded")
        self.budget -= cost
        self.repair_commitment = repair
        self.state = "S4_COMMIT"
        r = self.chain.append("repair_commitment", {
            "episode_id": self.episode_id,
            "repair": repair,
            "cost": cost,
            "budget_remaining": self.budget,
        })
        return self._scrub_receipt(r)

    def adjudicate(self, owner_result: dict[str, Any]) -> dict[str, Any]:
        if self.state != "S4_COMMIT":
            raise RuntimeError("adjudication only allowed after repair commitment")
        # owner_result is owner-only; public result exposes pass/fail and generic code only.
        owner = self.chain.append("owner_adjudication", {
            "episode_id": self.episode_id,
            "hidden_arm": self.hidden_arm,
            "hidden_ab": self.hidden_ab,
            "repair": self.repair_commitment,
            "owner_result": owner_result,
        })
        self.state = "S5_ADJUDICATE"
        return {
            "episode_id": self.episode_id,
            "relative_time_ms": 0,
            "budget_remaining": self.budget,
            "status": "complete",
            "action": "adjudication",
            "receipt_id": owner["receipt_id"],
            "error_code": "NONE",
            "metadata": {"protocol_version": "v0", "result": "pass" if owner_result.get("pass") else "fail"},
        }

    def inject_hostile_error(self) -> dict[str, Any]:
        """Deliberately forbidden transcript for firewall negative testing."""
        return {
            "episode_id": self.episode_id,
            "relative_time_ms": 1,
            "budget_remaining": self.budget,
            "status": "error",
            "action": "read_old",
            "receipt_id": "rcpt_hostile",
            "error_code": "E_DEBUG",
            "metadata": {
                "hidden_arm": self.hidden_arm,
                "actuator_side": "left" if self.hidden_ab == "A" else "right",
                "fixture_serial": f"fixture-{self.hidden_arm}-{self.hidden_ab}",
            },
            "debug_owner_seed": f"seed=42 condition_{self.hidden_ab}",
        }

    def _public_event(self, action: str, measurement: float | None) -> dict[str, Any]:
        event = {
            "episode_id": self.episode_id,
            "relative_time_ms": 0,
            "budget_remaining": self.budget,
            "channel_id": "ch_opaque_0",
            "measurement": measurement,
            "status": "ok",
            "action": action,
            "error_code": "NONE",
            "metadata": {"protocol_version": "v0", "transport": "local"},
        }
        r = self.chain.append("agent_event", event)
        event["receipt_id"] = r["receipt_id"]
        return event

    @staticmethod
    def _scrub_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
        body = receipt["body"]
        return {
            "episode_id": body["episode_id"],
            "relative_time_ms": 0,
            "budget_remaining": body["budget_remaining"],
            "status": "committed",
            "action": "commit_repair",
            "receipt_id": receipt["receipt_id"],
            "error_code": "NONE",
            "metadata": {"protocol_version": "v0", "repair": body["repair"]},
        }


def selftest() -> dict[str, Any]:
    transcripts: list[dict[str, Any]] = []
    hostile: list[dict[str, Any]] = []
    for i, arm in enumerate(ARMS):
        c = Controller(total_budget=100, budget=100)
        c.freeze({"H0": {"v": 0}, "I0": {"v": 0}, "G0": {"v": 0}})
        c.arm(arm, "A" if i % 2 == 0 else "B", 1000 + i)
        transcripts.append(c.expose(measurement=0.1 * i))
        transcripts.append(c.diagnostic("repeat_probe", 5, measurement=0.2 * i))
        repair = {
            "WR": "reanalyze_existing_history",
            "WP-I": "materialize_existing_closure",
            "WP-G": "author_new_measurement_operator",
            "WA": "ground_or_randomize_nuisance",
        }[arm]
        transcripts.append(c.commit_repair(repair, 40))
        transcripts.append(c.adjudicate({"pass": True, "owner_detail": arm}))
        hostile.append(c.inject_hostile_error())
        # Ensure one-primary-repair invariant.
        second_commit_blocked = False
        try:
            c.commit_repair(repair, 1)
        except RuntimeError:
            second_commit_blocked = True
        assert second_commit_blocked
        # Verify owner chain is tamper-evident by recomputing every receipt.
        prev = "sha256:" + "0" * 64
        for rec in c.chain.receipts:
            assert rec["previous"] == prev
            core = {"kind": rec["kind"], "previous": rec["previous"], "body": rec["body"]}
            assert rec["receipt_id"] == digest(core)
            prev = rec["receipt_id"]
    return {"clean_transcripts": transcripts, "hostile_transcripts": hostile, "passed": True}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), indent=2, sort_keys=True))
        return 0
    p.error("--selftest required for current non-agent emulator")


if __name__ == "__main__":
    raise SystemExit(main())
