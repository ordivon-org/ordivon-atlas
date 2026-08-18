from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path


RUN = os.environ.get("ORDIVON_ATLAS_WORLD_RETIREMENT_TESTS") == "1"
ROOT = Path(__file__).resolve().parents[1]
OWNER = "research-owner:world"


@unittest.skipUnless(RUN, "set ORDIVON_ATLAS_WORLD_RETIREMENT_TESTS=1 for World first-lookup retirement proof")
class WorldFirstLookupRetirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads((ROOT / "evidence/BOOTSTRAP-WORLD-PARITY-SPEC-20260818.json").read_text())
        cls.atlas = json.loads((ROOT / "generated/atlas.json").read_text())
        cls.registry = json.loads((ROOT / "config/sources.json").read_text())
        cls.owner = next(row for row in cls.atlas["owners"] if row["ownerResearchRef"] == OWNER)
        cls.health = next(row for row in cls.atlas["projectionHealth"] if row["ownerResearchRef"] == OWNER)
        cls.recovery = next(row for row in cls.atlas["currentRecovery"] if row["ownerResearchRef"] == OWNER)
        cls.results = {row["resultRef"]: row for row in cls.atlas["results"] if row["ownerResearchRef"] == OWNER}
        cls.closure = [row for row in cls.atlas["closure"] if row["ownerResearchRef"] == OWNER]
        cls.lineage = [row for row in cls.atlas["negativeAndLineage"] if row["ownerResearchRef"] == OWNER]
        cls.source = next(row for row in cls.registry["sources"] if row["ownerResearchRef"] == OWNER)

    def test_bootstrap_sources_are_not_execution_inputs(self) -> None:
        policy = self.spec["bootstrapExecutionPolicy"]
        self.assertFalse(policy["bootstrapUsedAtExecution"])
        self.assertNotIn("Ordivon_Host", globals())
        self.assertEqual(self.owner["authorityVersionRef"], self.spec["authority"]["authorityVersionRef"])
        self.assertEqual(self.owner["sourceTransportRevision"], self.spec["authority"]["sourceTransportRevision"])
        self.assertEqual(self.health["health"], "CURRENT_TO_SOURCE")

    def test_owner_native_recovery_resolves_at_exact_world_fence(self) -> None:
        expected = self.spec["authority"]["recovery"]
        self.assertEqual(self.recovery["targetRole"], expected["targetRole"])
        self.assertEqual(self.recovery["locator"], expected["locator"])
        self.assertEqual(self.recovery["targetRole"], "OWNER_RESEARCH_CORPUS")
        self.assertNotIn("task:", self.recovery["locator"])
        self.assertNotIn("handoff", self.recovery["locator"].lower())
        revision = self.owner["sourceTransportRevision"]
        locator = self.recovery["locator"]
        proc = subprocess.run(
            ["git", "-C", self.source["repo"], "cat-file", "-e", f"{revision}:{locator}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        body = subprocess.check_output(["git", "-C", self.source["repo"], "show", f"{revision}:{locator}"], text=True)
        self.assertIn("World / Reality Research", body)
        self.assertIn("WholeWorldClosure", body)
        self.assertIn("WDF6", body)

    def test_all_high_control_world_results_match_frozen_parity_spec(self) -> None:
        self.assertEqual(set(self.results), set(self.spec["results"]))
        for result_ref, expected in self.spec["results"].items():
            row = self.results[result_ref]
            self.assertEqual(row["classificationHealth"], "EXPLICIT", result_ref)
            self.assertEqual(row["standing"], expected["standing"], result_ref)
            self.assertEqual(row["epistemicVerdict"], expected["verdict"], result_ref)
            self.assertEqual(row["authorityVersionRef"], self.spec["authority"]["authorityVersionRef"])
            self.assertEqual(row["sourceTransportRevision"], self.spec["authority"]["sourceTransportRevision"])

    def test_world_closure_matrix_matches_legacy_high_control_state(self) -> None:
        actual = {(row["scope"], row["status"]) for row in self.closure}
        expected = {(row["scope"], row["status"]) for row in self.spec["closure"]}
        self.assertEqual(actual, expected)
        self.assertIn(("WHOLE_WORLD", "NOT_ESTABLISHED"), actual)
        self.assertIn(("TEMPORAL_WHOLE_DOMAIN", "NOT_ESTABLISHED"), actual)
        self.assertIn(("TEMPORAL_PROJECT", "NOT_ESTABLISHED"), actual)

    def test_world_negative_repair_lineage_matches_without_bootstrap_reads(self) -> None:
        corpus = "\n".join(row.get("summary", "") for row in self.lineage)
        for needle in self.spec["lineageContains"]:
            self.assertIn(needle, corpus)

    def test_deep_research_is_not_promoted_and_next_slots_do_not_self_admit(self) -> None:
        self.assertEqual(self.results["result:world:wdf2-counterfactual-deep-history-nonfoundation"]["standing"], ["HISTORICAL_PRESERVED"])
        self.assertEqual(self.results["result:world:wdf3-categorial-deep-history-nonfoundation"]["standing"], ["HISTORICAL_PRESERVED"])
        self.assertNotIn("FROZEN", self.results["result:world:wdf2-counterfactual-deep-history-nonfoundation"]["standing"])
        self.assertNotIn("FROZEN", self.results["result:world:wdf3-categorial-deep-history-nonfoundation"]["standing"])
        self.assertEqual(self.results["result:world:wdf6-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(self.results["result:world:tsaf1-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(self.results["result:world:next-world-route-unknown"]["epistemicVerdict"], "UNDERDETERMINED")

    def test_blocked_world_to_workstation_transfer_is_not_recovered_as_current_truth(self) -> None:
        world_projection = {
            "owner": self.owner,
            "health": self.health,
            "recovery": self.recovery,
            "results": list(self.results.values()),
            "closure": self.closure,
            "lineage": self.lineage,
        }
        text = json.dumps(world_projection, ensure_ascii=False).lower()
        self.assertNotIn("workstation", text)
        self.assertFalse(self.spec["negativeFalsifiers"].get("worldToWorkstationCurrentTransferClaimMustBeAbsent") is False)
        self.assertEqual(self.spec["retirementScope"], "WORLD_LEGACY_LIVE_NAVIGATION_ROLE_ONLY")
        self.assertEqual(self.spec["historicalRetention"], "REQUIRED")


if __name__ == "__main__":
    unittest.main()
