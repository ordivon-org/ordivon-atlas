import os
import unittest
from dataclasses import replace
from pathlib import Path

from ordivon_atlas.atlas import Atlas, HealthState

ROOT = Path(__file__).resolve().parents[1]
OWNER = "research-owner:media"
EXPECTED_AUTHORITY = "sha256:e26649a077eacfd0964e0d6ace7a3454d27c60ebcc96251dbb9b1861d867823e"
HISTORICAL_AUTHORITY = "sha256:d73f350556c6a66ecf58750dba88ce34839334fdf2920d8cb6dcdfff59fd3c33"
HISTORICAL_TRANSPORT = "c3b39f1a2093a9aae5338abebb8224de2a5b7a06"


@unittest.skipUnless(
    os.environ.get("ORDIVON_ATLAS_MEDIA_LIVE_TESTS") == "1",
    "set ORDIVON_ATLAS_MEDIA_LIVE_TESTS=1 for Media owner publication parity",
)
class MediaLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        full = Atlas.from_registry(ROOT / "config/sources.json")
        spec = next(x for x in full.sources if x.ownerResearchRef == OWNER)
        if remote := os.environ.get("ORDIVON_ATLAS_MEDIA_LIVE_REMOTE"):
            spec = replace(spec, remote=remote, remoteFallbacks=[])
        cls.projection = Atlas([spec]).build()
        cls.owner = cls.projection["owners"][0]
        cls.results = cls.projection["results"]
        cls.closure = cls.projection["closure"]
        cls.negative = cls.projection["negativeAndLineage"]
        cls.recovery = cls.projection["currentRecovery"][0]

    def test_media_is_current_and_owner_native_recoverable(self):
        self.assertEqual(
            self.owner["projectionCurrentness"],
            HealthState.CURRENT_TO_SOURCE,
        )
        self.assertEqual(self.owner["authorityVersionRef"], EXPECTED_AUTHORITY)
        self.assertNotEqual(self.owner["authorityVersionRef"], HISTORICAL_AUTHORITY)
        self.assertRegex(self.owner["sourceTransportRevision"], r"^[0-9a-f]{40}$")
        self.assertNotEqual(
            self.owner["sourceTransportRevision"],
            HISTORICAL_TRANSPORT,
        )
        self.assertEqual(self.recovery["locator"], "research/media/README.md")
        self.assertEqual(self.recovery["targetRole"], "OWNER_RESEARCH_CORPUS")

    def test_media_high_control_foundation_and_closure_parity(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(len(by), 20)
        self.assertEqual(
            by["result:media:mf0-mf9-current-frozen"]["standing"],
            ["CURRENT", "FROZEN"],
        )
        self.assertEqual(
            by["result:media:mf10-not-admitted"]["standing"],
            ["CURRENT", "NOT_ADMITTED"],
        )
        self.assertEqual(
            by["result:media:foundations-closure-strong"]["standing"],
            ["CURRENT"],
        )
        self.assertEqual(
            by["result:media:absolute-whole-exhaustion-not-claimed"][
                "epistemicVerdict"
            ],
            "ESTABLISHED_IN_SCOPE",
        )
        self.assertEqual(
            by["result:media:next-route-unknown"]["epistemicVerdict"],
            "UNDERDETERMINED",
        )

    def test_destructive_falsification_and_decanonicalized_roadmap_survive(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(
            by["result:media:primitive-candidate-reductions-current"][
                "epistemicVerdict"
            ],
            "FALSIFIED_IN_SCOPE",
        )
        self.assertEqual(
            by["result:media:mf10-mf19-roadmap-decanonicalized"][
                "epistemicVerdict"
            ],
            "FALSIFIED_IN_SCOPE",
        )
        text = " | ".join(x["summary"] for x in self.negative)
        self.assertIn("Round C blind fresh-continent rescan", text)
        self.assertIn("MF10-MF19 historical roadmap is de-canonicalized", text)

    def test_ompc_reference_contract_does_not_promote_implementation(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(
            by["result:media:ompc-v0-current"]["standing"],
            ["CURRENT"],
        )
        self.assertEqual(
            by["result:media:ompc-six-role-baseline-current"]["standing"],
            ["CURRENT", "FROZEN"],
        )
        self.assertEqual(
            by["result:media:ompc-eleven-invariants-current"]["standing"],
            ["CURRENT"],
        )
        self.assertEqual(
            by["result:media:shared-implementation-not-admitted"]["standing"],
            ["CURRENT", "NOT_ADMITTED"],
        )

    def test_phase1_closeout_does_not_invent_a_next_phase(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(
            by["result:media:phase1-owner-closure-current"]["standing"],
            ["CURRENT", "FROZEN"],
        )
        self.assertEqual(
            by["result:media:studio-retained-capability-plane"]["standing"],
            ["CURRENT"],
        )
        cb = {
            (x["researchRef"], x["scope"]): x["status"]
            for x in self.closure
        }
        phase = "research:media:phase1-ompc-current-20260819"
        self.assertEqual(
            cb[(phase, "MEDIA_CONSTRUCTION_PHASE1_M0_M4")],
            "CLOSED_STABLE_OWNER",
        )
        self.assertEqual(
            cb[(phase, "OMPC_V0_REFERENCE_CONTRACT")],
            "CURRENT_BASELINE",
        )
        self.assertNotIn((phase, "NEXT_CONSTRUCTION_PHASE"), cb)

    def test_media_history_boundary_keeps_consumers_and_owners_separate(self):
        by = {x["resultRef"]: x for x in self.results}
        self.assertEqual(
            by["result:media:m7-historical-consumer-research"]["standing"],
            ["CURRENT"],
        )
        self.assertEqual(
            by["result:media:art-expression-adjacent-not-core"]["standing"],
            ["CURRENT"],
        )
        firewall = by["result:media:cross-owner-authority-firewall-current"]
        self.assertEqual(firewall["standing"], ["CURRENT"])
        self.assertIn("authority transfer", firewall["evidenceScope"])


if __name__ == "__main__":
    unittest.main()
