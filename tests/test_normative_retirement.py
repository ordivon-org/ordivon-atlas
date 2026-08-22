from __future__ import annotations

import json
import os
import re
import subprocess
import unittest
from pathlib import Path


RUN = os.environ.get("ORDIVON_ATLAS_NORMATIVE_RETIREMENT_TESTS") == "1"
ROOT = Path(__file__).resolve().parents[1]
OWNER = "research-owner:ordivon-normative"
NETWORK = "research-owner:network"


@unittest.skipUnless(RUN, "set ORDIVON_ATLAS_NORMATIVE_RETIREMENT_TESTS=1 for Normative first-lookup retirement proof")
class NormativeFirstLookupRetirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads((ROOT / "evidence/BOOTSTRAP-NORMATIVE-PARITY-SPEC-20260818.json").read_text())
        cls.atlas = json.loads((ROOT / "generated/atlas.json").read_text())
        cls.registry = json.loads((ROOT / "config/sources.json").read_text())
        cls.owner = next(row for row in cls.atlas["owners"] if row["ownerResearchRef"] == OWNER)
        cls.network = next(row for row in cls.atlas["owners"] if row["ownerResearchRef"] == NETWORK)
        cls.health = next(row for row in cls.atlas["projectionHealth"] if row["ownerResearchRef"] == OWNER)
        cls.recovery = next(row for row in cls.atlas["currentRecovery"] if row["ownerResearchRef"] == OWNER)
        cls.network_recovery = next(row for row in cls.atlas["currentRecovery"] if row["ownerResearchRef"] == NETWORK)
        cls.results = {row["resultRef"]: row for row in cls.atlas["results"] if row["ownerResearchRef"] == OWNER}
        cls.history = [row for row in cls.atlas["history"] if row["ownerResearchRef"] == OWNER]
        cls.closure = [row for row in cls.atlas["closure"] if row["ownerResearchRef"] == OWNER]
        cls.lineage = [row for row in cls.atlas["negativeAndLineage"] if row["ownerResearchRef"] == OWNER]
        cls.source = next(row for row in cls.registry["sources"] if row["ownerResearchRef"] == OWNER)
        cls.network_source = next(row for row in cls.registry["sources"] if row["ownerResearchRef"] == NETWORK)

    def test_bootstrap_capsules_are_not_execution_inputs(self) -> None:
        policy = self.spec["bootstrapExecutionPolicy"]
        self.assertFalse(policy["bootstrapUsedAtExecution"])
        self.assertNotIn("Ordivon_Host", globals())
        self.assertNotEqual(self.owner["authorityVersionRef"], self.spec["authority"]["authorityVersionRef"])
        self.assertNotEqual(self.owner["sourceTransportRevision"], self.spec["authority"]["sourceTransportRevision"])
        self.assertEqual(self.health["health"], "CURRENT_TO_SOURCE")
        historical = {row.get("authorityVersionRef"): row.get("currentness") for row in self.history}
        self.assertEqual(historical[self.spec["authority"]["authorityVersionRef"]], "HISTORICAL_NOT_CURRENT")

    def test_owner_native_recovery_resolves_to_normative_not_network(self) -> None:
        expected = self.spec["authority"]["recovery"]
        self.assertEqual(expected["locator"], "owners/ordivon-normative/README.md")
        self.assertEqual(self.recovery["targetRole"], "OWNER_RESEARCH_CORPUS")
        self.assertEqual(self.recovery["locator"], "README.md")
        self.assertEqual(self.network_recovery["locator"], "README.md")
        self.assertNotEqual(self.source["repo"], self.network_source["repo"])
        self.assertNotEqual(self.owner["sourceTransportRevision"], self.network["sourceTransportRevision"])
        self.assertNotEqual(self.owner["authorityVersionRef"], self.network["authorityVersionRef"])
        revision = self.owner["sourceTransportRevision"]
        locator = self.recovery["locator"]
        proc = subprocess.run(["git", "-C", self.source["repo"], "cat-file", "-e", f"{revision}:{locator}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        body = subprocess.check_output(["git", "-C", self.source["repo"], "show", f"{revision}:{locator}"], text=True)
        self.assertIn("Ordivon Normative", body)
        self.assertRegex(body, r"Numbered Foundation count:\s+\*\*0\*\*")
        self.assertNotIn("owners/network/README.md", locator)

    def test_all_frozen_high_control_results_survive_as_historical_subset(self) -> None:
        # The bootstrap parity spec freezes the high-control surface at retirement time.
        # Later owner-authoritative Phase-II results may extend the current owner, but
        # every frozen result must remain present with the same semantic classification.
        self.assertTrue(set(self.spec["results"]).issubset(self.results))
        for result_ref, expected in self.spec["results"].items():
            row = self.results[result_ref]
            self.assertEqual(row["classificationHealth"], "EXPLICIT", result_ref)
            self.assertEqual(row["standing"], expected["standing"], result_ref)
            self.assertEqual(row["epistemicVerdict"], expected["verdict"], result_ref)
            self.assertEqual(row["authorityVersionRef"], self.owner["authorityVersionRef"])
            self.assertEqual(row["sourceTransportRevision"], self.owner["sourceTransportRevision"])

    def test_zero_numbered_foundations_and_non_numbered_architecture_survive(self) -> None:
        zero = self.results["result:normative:numbered-foundation-count-zero-current-frozen"]
        self.assertEqual(zero["standing"], ["CURRENT", "FROZEN"])
        for ref in (
            "result:normative:anchor-interface-current-frozen",
            "result:normative:generator-admission-structure-current-frozen",
            "result:normative:derivation-transition-semantics-current-frozen",
        ):
            self.assertEqual(self.results[ref]["standing"], ["CURRENT", "FROZEN"])
        self.assertFalse(any(re.search(r"result:normative:onf\d", ref) for ref in self.results))
        self.assertEqual(self.results["result:normative:onf-numbered-series-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(self.results["result:normative:phr-numbered-foundation-series-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])

    def test_current_owner_boundaries_and_non_admissions_survive(self) -> None:
        for ref in (
            "result:normative:universal-normativity-owner-not-admitted",
            "result:normative:generic-institution-governance-owner-not-admitted",
            "result:normative:generic-reasons-value-owner-not-admitted",
            "result:normative:generic-control-regulation-not-owned-here",
        ):
            self.assertEqual(self.results[ref]["standing"], ["CURRENT", "NOT_ADMITTED"])
            self.assertEqual(self.results[ref]["epistemicVerdict"], "ESTABLISHED_IN_SCOPE")

    def test_phr1_origin_is_historical_and_phr2_to_phr4_do_not_reenter_current_owner(self) -> None:
        self.assertEqual(self.results["result:normative:phr1-historical-origin-preserved"]["standing"], ["HISTORICAL_PRESERVED"])
        refs = set(self.results)
        self.assertFalse(any(ref.startswith("result:normative:phr2") or ref.startswith("result:normative:phr3") or ref.startswith("result:normative:phr4") for ref in refs))
        corpus = "\n".join(row.get("summary", "") for row in self.lineage)
        self.assertIn("PHR1 is the historical origin", corpus)
        self.assertIn("PHR2-PHR4 are deliberately outside", corpus)

    def test_closure_and_lineage_parity_survive_without_host_lookup(self) -> None:
        actual = {(row["scope"], row["status"]) for row in self.closure}
        expected = {(row["scope"], row["status"]) for row in self.spec["closure"]}
        # Retirement parity is a preservation floor, not a ceiling on later owner work.
        self.assertTrue(expected.issubset(actual))
        corpus = "\n".join(row.get("summary", "") for row in self.lineage)
        for needle in self.spec["lineageContains"]:
            self.assertIn(needle, corpus)
        self.assertEqual(self.spec["retirementScope"], "NORMATIVE_LEGACY_LIVE_NAVIGATION_ROLE_ONLY")
        self.assertEqual(self.spec["historicalRetention"], "REQUIRED")


if __name__ == "__main__":
    unittest.main()
