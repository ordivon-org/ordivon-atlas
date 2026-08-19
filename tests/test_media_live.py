import os
import unittest
from pathlib import Path

from ordivon_atlas.atlas import Atlas, HealthState

ROOT = Path(__file__).resolve().parents[1]
OWNER = "research-owner:media"
EXPECTED_AUTHORITY = "sha256:d73f350556c6a66ecf58750dba88ce34839334fdf2920d8cb6dcdfff59fd3c33"
EXPECTED_TRANSPORT = "c3b39f1a2093a9aae5338abebb8224de2a5b7a06"

@unittest.skipUnless(os.environ.get("ORDIVON_ATLAS_MEDIA_LIVE_TESTS") == "1", "set ORDIVON_ATLAS_MEDIA_LIVE_TESTS=1 for Media owner publication parity")
class MediaLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        full = Atlas.from_registry(ROOT / "config/sources.json")
        spec = next(x for x in full.sources if x.ownerResearchRef == OWNER)
        cls.projection = Atlas([spec]).build()
        cls.owner = cls.projection["owners"][0]
        cls.results = cls.projection["results"]
        cls.closure = cls.projection["closure"]
        cls.negative = cls.projection["negativeAndLineage"]
        cls.recovery = cls.projection["currentRecovery"][0]

    def test_media_is_current_and_owner_native_recoverable(self):
        self.assertEqual(self.owner["projectionCurrentness"], HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(self.owner["authorityVersionRef"], EXPECTED_AUTHORITY)
        self.assertEqual(self.owner["sourceTransportRevision"], EXPECTED_TRANSPORT)
        self.assertEqual(self.recovery["locator"], "research/media/README.md")
        self.assertEqual(self.recovery["targetRole"], "OWNER_RESEARCH_CORPUS")

    def test_media_high_control_foundation_and_closure_parity(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(len(by), 31)
        self.assertEqual(by["result:media:mf0-mf9-frozen-current"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(by["result:media:mf10-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(by["result:media:foundations-current-research-closure-strong"]["standing"], ["CURRENT"])
        self.assertEqual(by["result:media:absolute-whole-exhaustion-not-claimed"]["epistemicVerdict"], "UNDERDETERMINED")
        self.assertEqual(by["result:media:next-foundation-unknown"]["epistemicVerdict"], "UNDERDETERMINED")
        self.assertEqual(by["result:media:next-route-unknown"]["epistemicVerdict"], "UNDERDETERMINED")

    def test_round_c_falsification_and_superseded_roadmap_survive(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(by["result:media:round-c-checklist-closure-assumption-falsified"]["standing"], ["FALSIFIED", "HISTORICAL_PRESERVED"])
        self.assertEqual(by["result:media:round-c-checklist-closure-assumption-falsified"]["epistemicVerdict"], "FALSIFIED_IN_SCOPE")
        self.assertEqual(by["result:media:mf10-mf19-roadmap-historical-superseded"]["standing"], ["HISTORICAL_PRESERVED", "SUPERSEDED"])
        text = " | ".join(x["summary"] for x in self.negative)
        self.assertIn("Round C falsified checklist-completion closure", text)
        self.assertIn("Do not resurrect de-canonicalized MF10", text)

    def test_ompc_reference_contract_does_not_promote_implementation(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(by["result:media:ompc-v0-reference-contract-current"]["standing"], ["CURRENT"])
        self.assertEqual(by["result:media:ompc-six-roles-current"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(by["result:media:shared-implementation-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(by["result:media:universal-media-framework-engine-runtime-sdk-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])

    def test_phase1_closeout_does_not_admit_phase2(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(by["result:media:phase1-closed-current"]["standing"], ["CURRENT", "STAGE_COMPLETE"])
        self.assertEqual(by["result:media:stable-owner-consumer-pressure-posture-current"]["standing"], ["CURRENT"])
        self.assertEqual(by["result:media:next-construction-phase-pressure-triggered-not-scheduled"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        cb = {(x["researchRef"], x["scope"]): x["status"] for x in self.closure}
        self.assertEqual(cb[("research:media:phase1-project-formation-closeout-20260819", "MEDIA_CONSTRUCTION_PHASE1_M0_M4")], "CLOSED")
        self.assertEqual(cb[("research:media:phase1-project-formation-closeout-20260819", "NEXT_CONSTRUCTION_PHASE")], "PRESSURE_TRIGGERED_NOT_SCHEDULED")

    def test_media_history_boundary_keeps_m7_art_and_source_owners_separate(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(by["result:media:m7-production-consumer-history"]["standing"], ["HISTORICAL_PRESERVED"])
        self.assertEqual(by["result:media:art-expression-studio-adjacent-not-core"]["standing"], ["CURRENT"])
        self.assertEqual(by["result:media:cross-owner-bridges-current"]["standing"], ["CURRENT"])
        self.assertIn("does not transfer authority", by["result:media:cross-owner-bridges-current"]["evidenceScope"])

if __name__ == "__main__":
    unittest.main()
