import os
import unittest
from pathlib import Path

from ordivon_atlas.atlas import Atlas, HealthState

ROOT = Path(__file__).resolve().parents[1]
OWNER = "research-owner:semantics-of-computational-descriptions"
CP = "research-owner:computational-possibility"
EXPECTED_AUTHORITY = "sha256:3319f37f081908e545c708f79e489c3b2a1c54cb03453fa2ebe32bc6e72cbd4f"

@unittest.skipUnless(os.environ.get("ORDIVON_ATLAS_SCD_LIVE_TESTS") == "1", "set ORDIVON_ATLAS_SCD_LIVE_TESTS=1 for SCD owner publication parity")
class SCDLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = Atlas.from_registry(ROOT / "config/sources.json")
        cls.projection = cls.atlas.build()
        cls.owners = {x["ownerResearchRef"]: x for x in cls.projection["owners"]}
        cls.results = [x for x in cls.projection["results"] if x["ownerResearchRef"] == OWNER]
        cls.closure = [x for x in cls.projection["closure"] if x["ownerResearchRef"] == OWNER]
        cls.negative = [x for x in cls.projection["negativeAndLineage"] if x["ownerResearchRef"] == OWNER]
        cls.recovery = next(x for x in cls.projection["currentRecovery"] if x["ownerResearchRef"] == OWNER)

    def test_scd_and_cp_are_distinct_current_owners_in_same_repo(self):
        self.assertEqual(self.owners[OWNER]["projectionCurrentness"], HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(self.owners[CP]["projectionCurrentness"], HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(self.owners[OWNER]["authorityVersionRef"], EXPECTED_AUTHORITY)
        self.assertNotEqual(self.owners[OWNER]["authorityVersionRef"], self.owners[CP]["authorityVersionRef"])
        self.assertNotEqual(self.owners[OWNER]["sourceTransportRevision"], self.owners[CP]["sourceTransportRevision"])

    def test_scd_recovery_is_owner_native(self):
        self.assertEqual(self.recovery["locator"], "research/core/semantics-of-computational-descriptions/README.md")
        self.assertEqual(self.recovery["targetRole"], "OWNER_RESEARCH_CORPUS")

    def test_scd_high_control_result_parity(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(len(by), 16)
        self.assertEqual(by["result:scd:scdf-frozen-set-current"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(by["result:scd:scdf-open-set-current"]["standing"], ["CURRENT"])
        self.assertEqual(by["result:scd:scdf-open-set-current"]["epistemicVerdict"], "ESTABLISHED_IN_SCOPE")
        self.assertEqual(by["result:scd:whole-s-exhaustive-complete-unknown"]["epistemicVerdict"], "UNDERDETERMINED")
        self.assertEqual(by["result:scd:research-order-unknown"]["epistemicVerdict"], "UNDERDETERMINED")
        self.assertEqual(by["result:scd:g1-g4-independent-formal-gaps-rejected"]["epistemicVerdict"], "FALSIFIED_IN_SCOPE")
        self.assertEqual(by["result:scd:g1-g4-independent-formal-gaps-rejected"]["standing"], ["CURRENT"])
        self.assertEqual(by["result:scd:g5-not-authorized"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(by["result:scd:consumer-dogfood-foundation-promotion-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])

    def test_scd_closure_does_not_upgrade_unknowns(self):
        by = {(x["researchRef"], x["scope"]): x["status"] for x in self.closure}
        core = "research:scd:core-current-20260819"
        self.assertEqual(by[(core, "FOUNDATION0")], "NONE")
        self.assertEqual(by[(core, "INDIVIDUAL_OPEN_SET")], "SCDF2_SCDF4_SCDF5")
        self.assertEqual(by[(core, "WHOLE_S_EXHAUSTIVE_COMPLETE")], "UNKNOWN")
        self.assertEqual(by[(core, "RESEARCH_ORDER_SCDF")], "UNKNOWN")
        self.assertEqual(by[("research:scd:formalization-gap-campaign-v0-1-20260818", "G1_G4_INDEPENDENT_MISSING_FORMAL_THEORY")], "REJECTED")
        self.assertEqual(by[("research:scd:applied-consumer-dogfood-a1-a8-20260818", "FOUNDATION_LEVEL_PROMOTION_FROM_A1_A8")], "NOT_ADMITTED")

    def test_negative_formal_gap_and_nonpromotion_lineage_is_discoverable(self):
        text = " | ".join(x["summary"] for x in self.negative)
        for phrase in ("G1 multi-framework coordination", "G2 owner-typed currentness", "G3 universal DescriptionIdentity", "G4 universal correspondence composition", "Do not create G5", "No consumer-success-to-Foundation promotion"):
            self.assertIn(phrase, text)

if __name__ == "__main__":
    unittest.main()
