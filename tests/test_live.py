from __future__ import annotations

import unittest

from ordivon_atlas.atlas import Atlas, HealthState, compare_projected_version, load_registry


class LiveSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.specs = load_registry("config/sources.json")
        cls.atlas = Atlas(cls.specs)
        cls.by_owner = {spec.ownerResearchRef: spec for spec in cls.specs}

    def test_network_is_current_and_recoverable(self) -> None:
        obs = self.atlas.observe(self.by_owner["research-owner:network"])
        self.assertEqual(obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(obs.authorityVersionRef, "sha256:bfadaaaad3b01f9c4388e4e4a75e77c782c2c3111849e5c4598052ec740ee79f")
        self.assertEqual((obs.currentRecovery or {}).get("targetRole"), "OWNER_RESEARCH_CORPUS")

    def test_runtime_v2_is_current_and_v1_is_stale(self) -> None:
        obs = self.atlas.observe(self.by_owner["research-owner:runtime"])
        self.assertEqual(obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(obs.authorityVersionRef, "sha256:e2eb5a6d46c50390ec4b666cd6faba5528ff42b2c9e1bfb75cb45b6c0c4177ed")
        old = "sha256:a39e5ec16ed955bc02b1e11db6f120f5f812e093324a6a3171d368f710a8665b"
        self.assertEqual(compare_projected_version(old, obs), HealthState.SOURCE_ADVANCED_STALE)

    def test_generated_history_keeps_runtime_v1_and_v2(self) -> None:
        projection = self.atlas.build()
        versions = {row.get("authorityVersionRef"): row.get("currentness") for row in projection["history"] if row.get("ownerResearchRef") == "research-owner:runtime"}
        self.assertEqual(versions["sha256:a39e5ec16ed955bc02b1e11db6f120f5f812e093324a6a3171d368f710a8665b"], "HISTORICAL_NOT_CURRENT")
        self.assertEqual(versions["sha256:e2eb5a6d46c50390ec4b666cd6faba5528ff42b2c9e1bfb75cb45b6c0c4177ed"], "CURRENT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
