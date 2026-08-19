import os
import unittest
from pathlib import Path

from ordivon_atlas.atlas import Atlas, HealthState

ROOT = Path(__file__).resolve().parents[1]
OWNER = "research-owner:human"
NORMATIVE = "research-owner:ordivon-normative"
EXPECTED_AUTHORITY = "sha256:035eaa334ffdfe3ae44236f966176a36ffd772ee8c2e4c4454733ab9699ef392"
EXPECTED_TRANSPORT = "cc966bf99458949b59c433a5f7bc8fafe3d692b7"

@unittest.skipUnless(os.environ.get("ORDIVON_ATLAS_HUMAN_LIVE_TESTS") == "1", "set ORDIVON_ATLAS_HUMAN_LIVE_TESTS=1 for Human owner publication parity")
class HumanLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        full = Atlas.from_registry(ROOT / "config/sources.json")
        specs = [x for x in full.sources if x.ownerResearchRef in (OWNER, NORMATIVE)]
        cls.atlas = Atlas(specs)
        cls.projection = cls.atlas.build()
        cls.owners = {x["ownerResearchRef"]: x for x in cls.projection["owners"]}
        cls.results = [x for x in cls.projection["results"] if x["ownerResearchRef"] == OWNER]
        cls.closure = [x for x in cls.projection["closure"] if x["ownerResearchRef"] == OWNER]
        cls.negative = [x for x in cls.projection["negativeAndLineage"] if x["ownerResearchRef"] == OWNER]
        cls.recovery = next(x for x in cls.projection["currentRecovery"] if x["ownerResearchRef"] == OWNER)

    def test_human_is_current_and_owner_native_recoverable(self):
        h = self.owners[OWNER]
        self.assertEqual(h["projectionCurrentness"], HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(h["authorityVersionRef"], EXPECTED_AUTHORITY)
        self.assertEqual(h["sourceTransportRevision"], EXPECTED_TRANSPORT)
        self.assertEqual(self.recovery["locator"], "research/core/HUMAN-RESEARCH-CORE.md")
        self.assertEqual(self.recovery["targetRole"], "OWNER_RESEARCH_CORPUS")

    def test_human_and_normative_are_distinct_current_authorities(self):
        h = self.owners[OWNER]; n = self.owners[NORMATIVE]
        self.assertEqual(h["projectionCurrentness"], HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(n["projectionCurrentness"], HealthState.CURRENT_TO_SOURCE)
        self.assertNotEqual(h["authorityRef"], n["authorityRef"])
        self.assertNotEqual(h["authorityVersionRef"], n["authorityVersionRef"])

    def test_human_high_control_result_parity(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(len(by), 30)
        self.assertEqual(by["result:human:hf0-hf23-frozen-current"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(by["result:human:hf24-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(by["result:human:hd11-hd16-stage-complete-history"]["standing"], ["HISTORICAL_PRESERVED", "STAGE_COMPLETE"])
        self.assertEqual(by["result:human:next-deep-route-unknown"]["epistemicVerdict"], "UNDERDETERMINED")
        self.assertEqual(by["result:human:whole-human-exhaustion-not-claimed"]["epistemicVerdict"], "UNDERDETERMINED")
        self.assertEqual(by["result:human:hoc0-hoc10-frozen-current"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(by["result:human:hoc11-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(by["result:human:generic-operational-core-sufficiency-falsified"]["standing"], ["FALSIFIED", "HISTORICAL_PRESERVED"])
        self.assertEqual(by["result:human:one-person-vector-universal-profile-rejected"]["standing"], ["HISTORICAL_PRESERVED", "REJECTED"])

    def test_hf14_hf18_overlay_does_not_leak_normative_authority(self):
        by = {x["resultRef"]: x for x in self.results}
        row = by["result:human:hf14-hf18-normative-owner-overlay-current"]
        self.assertEqual(row["standing"], ["CURRENT"])
        self.assertIn("Ordivon Normative", row["evidenceScope"])
        self.assertIn("Human compatibility surface != generic normative authority", row["evidenceScope"])
        owner = by["result:human:owner-boundary-current"]
        self.assertIn("does not own generic normative validity", owner["evidenceScope"])

    def test_human_closure_remains_bounded(self):
        by = {(x["researchRef"], x["scope"]): x["status"] for x in self.closure}
        self.assertEqual(len(self.closure), 16)
        self.assertEqual(by[("research:human:core-current-20260819", "HF24")], "UNKNOWN_NOT_ADMITTED")
        self.assertEqual(by[("research:human:core-current-20260819", "WHOLE_HUMAN_FOUNDATION_EXHAUSTION")], "NOT_ESTABLISHED")
        self.assertEqual(by[("research:human:deep-domain-current-20260819", "NEXT_HUMAN_DEEP_ROUTE")], "UNKNOWN")
        self.assertEqual(by[("research:human:deep-domain-current-20260819", "WHOLE_HUMAN_EXHAUSTION")], "NOT_CLAIMED")
        self.assertEqual(by[("research:human:deep-domain-current-20260819", "HD11_HD16_HF24_PROMOTION")], "CLOSED_NOT_ADMITTED")
        self.assertEqual(by[("research:human:operational-current-20260819", "WHOLE_HUMAN_OPERATIONAL_CLOSURE")], "NOT_ESTABLISHED")

    def test_hoc10_falsification_and_negative_history_are_discoverable(self):
        text = " | ".join(x["summary"] for x in self.negative)
        self.assertIn("GenericOperationalCoreSufficiency(HOC0-HOC9) was falsified", text)
        self.assertIn("No HOC11 by symmetry", text)
        self.assertIn("Deep != Primitive", text)
        self.assertIn("No HF24 by numeric succession", text)

if __name__ == "__main__":
    unittest.main()
