from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path


RUN = os.environ.get("ORDIVON_ATLAS_BOOTSTRAP_RETIREMENT_TESTS") == "1"
ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(RUN, "set ORDIVON_ATLAS_BOOTSTRAP_RETIREMENT_TESTS=1 for destructive first-lookup retirement proof")
class BootstrapFirstLookupRetirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads((ROOT / "evidence/BOOTSTRAP-FOUR-OWNER-PARITY-SPEC-20260818.json").read_text())
        cls.atlas = json.loads((ROOT / "generated/atlas.json").read_text())
        cls.registry = json.loads((ROOT / "config/sources.json").read_text())
        cls.owners = {row["ownerResearchRef"]: row for row in cls.atlas["owners"]}
        cls.health = {row["ownerResearchRef"]: row for row in cls.atlas["projectionHealth"]}
        cls.recovery = {row["ownerResearchRef"]: row for row in cls.atlas["currentRecovery"]}
        cls.results = {row["resultRef"]: row for row in cls.atlas["results"]}
        cls.sources = {row["ownerResearchRef"]: row for row in cls.registry["sources"]}

    def test_execution_inputs_exclude_bootstrap_authority(self) -> None:
        policy = self.spec["bootstrapExecutionPolicy"]
        self.assertFalse(policy["bootstrapUsedAtExecution"])
        self.assertNotIn("Ordivon_Host", globals())
        self.assertEqual(set(self.spec["scopeOwners"]), set(self.owners))
        for owner in self.spec["scopeOwners"]:
            self.assertEqual(self.health[owner]["health"], "CURRENT_TO_SOURCE")

    def test_owner_native_current_recovery_resolves_at_exact_source_fence(self) -> None:
        for owner, expected in self.spec["recovery"].items():
            row = self.recovery[owner]
            self.assertEqual(row["targetRole"], expected["targetRole"])
            self.assertEqual(row["locator"], expected["locator"])
            self.assertEqual(row["targetRole"], "OWNER_RESEARCH_CORPUS")
            self.assertNotIn("task:", row["locator"])
            self.assertNotIn("handoff", row["locator"].lower())
            source = self.sources[owner]
            revision = self.owners[owner]["sourceTransportRevision"]
            proc = subprocess.run(
                ["git", "-C", source["repo"], "cat-file", "-e", f"{revision}:{row['locator']}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, f"{owner} recovery missing at {revision}: {row['locator']}\n{proc.stderr}")
            body = subprocess.check_output(
                ["git", "-C", source["repo"], "show", f"{revision}:{row['locator']}"],
                text=True,
            )
            self.assertTrue(body.strip(), owner)

    def test_high_control_result_parity_without_bootstrap_reads(self) -> None:
        for result_ref, expected in self.spec["results"].items():
            self.assertIn(result_ref, self.results)
            row = self.results[result_ref]
            self.assertEqual(row["classificationHealth"], "EXPLICIT", result_ref)
            self.assertEqual(row["standing"], expected["standing"], result_ref)
            self.assertEqual(row["epistemicVerdict"], expected["verdict"], result_ref)
            self.assertIsNotNone(row["authorityVersionRef"], result_ref)
            self.assertIsNotNone(row["sourceTransportRevision"], result_ref)

    def test_closure_parity_without_bootstrap_reads(self) -> None:
        actual = {
            (row["ownerResearchRef"], row["scope"], row["status"])
            for row in self.atlas["closure"]
        }
        for expected in self.spec["closure"]:
            key = (expected["ownerResearchRef"], expected["scope"], expected["status"])
            self.assertIn(key, actual)

    def test_negative_and_repair_lineage_parity_without_bootstrap_reads(self) -> None:
        by_owner: dict[str, list[str]] = {}
        for row in self.atlas["negativeAndLineage"]:
            by_owner.setdefault(row["ownerResearchRef"], []).append(row.get("summary", ""))
        for owner, needles in self.spec["lineageContains"].items():
            corpus = "\n".join(by_owner.get(owner, []))
            for needle in needles:
                self.assertIn(needle, corpus, f"missing lineage for {owner}: {needle}")

    def test_game_gdf3_collision_survives_first_lookup_retirement(self) -> None:
        collision = self.spec["collisionAssertions"][0]
        refs = collision["distinctResultRefs"]
        self.assertEqual(len(refs), 2)
        self.assertNotEqual(refs[0], refs[1])
        self.assertIn("gdf3", refs[0].lower())
        self.assertIn("gdf3", refs[1].lower())
        for ref in refs:
            self.assertIn(ref, self.results)
        current = self.results[refs[0]]
        historical = self.results[refs[1]]
        self.assertEqual(current["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(historical["standing"], ["ABANDONED", "HISTORICAL_PRESERVED"])
        self.assertNotEqual(current["standing"], historical["standing"])

    def test_no_obsolete_host_handoff_is_needed_for_current_recovery(self) -> None:
        for row in self.atlas["currentRecovery"]:
            self.assertEqual(row["targetRole"], "OWNER_RESEARCH_CORPUS")
            self.assertFalse(row["locator"].startswith("task:"))
            self.assertFalse("handoff" in row["locator"].lower())
        self.assertEqual(self.spec["retirementScope"], "LIVE_NAVIGATION_ROLE_ONLY_FOR_FOUR_COVERED_OWNERS")
        self.assertEqual(self.spec["historicalRetention"], "REQUIRED")


if __name__ == "__main__":
    unittest.main()
