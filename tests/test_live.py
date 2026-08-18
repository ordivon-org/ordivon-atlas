from __future__ import annotations

import os
import unittest

from ordivon_atlas.atlas import Atlas, HealthState, compare_projected_version, load_registry


LIVE = os.environ.get("ORDIVON_ATLAS_LIVE_TESTS") == "1"
RUNTIME_V1 = "sha256:a39e5ec16ed955bc02b1e11db6f120f5f812e093324a6a3171d368f710a8665b"
RUNTIME_V2 = "sha256:e2eb5a6d46c50390ec4b666cd6faba5528ff42b2c9e1bfb75cb45b6c0c4177ed"
RUNTIME_V3 = "sha256:350d042df3c01399cf9314c6954f0c3f4c45bdeb660aa275556e098a77ec62eb"
RUNTIME_V4 = "sha256:227cc7e253de5fa10be7cbecdfd2e7d84724b507c4a0504836fc63996ac53497"
RUNTIME_V5 = "sha256:e06cac5f69942068fabe80dc5da22fc1fb566d3004ce4951df545534fda289d9"
NETWORK_V1 = "sha256:bfadaaaad3b01f9c4388e4e4a75e77c782c2c3111849e5c4598052ec740ee79f"
NETWORK_V2 = "sha256:dbdbb759b2b86b898a343cbb81646b283c589676989e919537f1a6cbc2b1df91"
HOST_V1 = "sha256:4fc9dee669927882337649d19c144d0938ecf3307c461bffd84eedb8fdc27df4"
GAME_V1 = "sha256:b0e16e2cd6fe40685d7b96f94d78ef89bd55ed7f92db4de1408e33d2539bb2f0"


@unittest.skipUnless(LIVE, "set ORDIVON_ATLAS_LIVE_TESTS=1 for live remote acceptance")
class LiveSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.specs = load_registry("config/sources.json")
        cls.by_owner = {spec.ownerResearchRef: spec for spec in cls.specs}

    def test_network_repaired_publication_is_current_and_recoverable(self) -> None:
        spec = self.by_owner["research-owner:network"]
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(obs.authorityVersionRef, NETWORK_V2)
        self.assertEqual(compare_projected_version(NETWORK_V1, obs), HealthState.SOURCE_ADVANCED_STALE)
        self.assertEqual((obs.currentRecovery or {}).get("targetRole"), "OWNER_RESEARCH_CORPUS")

    def test_runtime_repaired_publication_is_current(self) -> None:
        spec = self.by_owner["research-owner:runtime"]
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(obs.authorityVersionRef, RUNTIME_V5)
        for old in (RUNTIME_V1, RUNTIME_V2, RUNTIME_V3, RUNTIME_V4):
            self.assertEqual(compare_projected_version(old, obs), HealthState.SOURCE_ADVANCED_STALE)

    def test_runtime_history_preserves_v1_v2_v3_and_current(self) -> None:
        spec = self.by_owner["research-owner:runtime"]
        projection = Atlas([spec]).build()
        self.assertEqual(projection["projectionHealth"][0]["health"], HealthState.CURRENT_TO_SOURCE)
        versions = {row.get("authorityVersionRef"): row.get("currentness") for row in projection["history"]}
        for old in (RUNTIME_V1, RUNTIME_V2, RUNTIME_V3, RUNTIME_V4):
            self.assertEqual(versions[old], "HISTORICAL_NOT_CURRENT")
        self.assertEqual(versions[RUNTIME_V5], "CURRENT_VERIFIED")

    def test_live_heterogeneous_result_standing_is_per_result(self) -> None:
        projection = Atlas(self.specs).build()
        self.assertTrue(all(row["health"] == HealthState.CURRENT_TO_SOURCE for row in projection["projectionHealth"]))
        rows = {row["resultRef"]: row for row in projection["results"]}
        ef27 = rows["result:runtime:ef27-historical-superseded"]
        self.assertEqual(ef27["classificationHealth"], "EXPLICIT")
        self.assertEqual(ef27["standing"], ["HISTORICAL_PRESERVED", "SUPERSEDED", "WITHDRAWN"])
        self.assertNotIn("CURRENT", ef27["standing"])
        ndf6 = rows["result:network:ndf6-not-admitted"]
        self.assertEqual(ndf6["classificationHealth"], "EXPLICIT")
        self.assertEqual(ndf6["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertNotIn("FROZEN", ndf6["standing"])
        self.assertTrue(all(row["classificationHealth"] == "EXPLICIT" for row in rows.values()))

    def test_rollout_host_and_game_are_current_with_negative_history_intact(self) -> None:
        projection = Atlas(self.specs).build()
        owners = {row["ownerResearchRef"]: row for row in projection["owners"]}
        self.assertEqual(owners["research-owner:host"]["authorityVersionRef"], HOST_V1)
        self.assertEqual(owners["research-owner:host"]["projectionHealth"], HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(owners["research-owner:game"]["authorityVersionRef"], GAME_V1)
        self.assertEqual(owners["research-owner:game"]["projectionHealth"], HealthState.CURRENT_TO_SOURCE)
        rows = {row["resultRef"]: row for row in projection["results"]}
        self.assertEqual(rows["result:host:hdf44-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(rows["result:host:generic-coordination-owner-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(rows["result:game:gdf3-authoritative-case-determination-current"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(rows["result:game:gdf3-game-feel-historical-cancelled"]["standing"], ["ABANDONED", "HISTORICAL_PRESERVED"])
        self.assertEqual(rows["result:game:c1-strong-survivor-unadmitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertNotEqual(
            rows["result:game:gdf3-authoritative-case-determination-current"]["resultRef"],
            rows["result:game:gdf3-game-feel-historical-cancelled"]["resultRef"],
        )


if __name__ == "__main__":
    unittest.main()
