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
RUNTIME_V6 = "sha256:9c67d1b4094ce85a2465579430bb1a941f1923457087fb74cde0642d7b9a51b3"
NETWORK_V1 = "sha256:bfadaaaad3b01f9c4388e4e4a75e77c782c2c3111849e5c4598052ec740ee79f"
NETWORK_V2 = "sha256:dbdbb759b2b86b898a343cbb81646b283c589676989e919537f1a6cbc2b1df91"
NETWORK_V3 = "sha256:31d78dd22ca73b95fc9a1107ad6a38e884859e94247263d14b916cef67e78e2a"
NETWORK_V4 = "sha256:61800d2c8679cf37c9b22bd1d38ff420c706b95bdf7e8b590820430e8729c557"
HOST_V1 = "sha256:4fc9dee669927882337649d19c144d0938ecf3307c461bffd84eedb8fdc27df4"
GAME_V1 = "sha256:b0e16e2cd6fe40685d7b96f94d78ef89bd55ed7f92db4de1408e33d2539bb2f0"
WORLD_V1 = "sha256:76f3ebc35cc72a67e65cacbcb899d8ccf0919059577c97191c85dc9aed9ede8f"
WORLD_V2 = "sha256:5e560a45711b33c7202390b0ec0c1cba5db37694759ce2d00122a499881f4878"
NORMATIVE_V1 = "sha256:6558bc84bb52a3a0ffbff0f683a36d46c28efc0f2ba531d4458bd5aa16a4a56e"
NORMATIVE_V2 = "sha256:91fe75c4827585487a5aadb8c55816b6628cda314bdbb79bdbe2554246a7b579"
NORMATIVE_V3 = "sha256:d0a1149b8c0278e5ca53122e9bc053c45ed64c0831e7cdb2616981361e6be9f3"
NORMATIVE_V4 = "sha256:f05ee2de3ebdf2b47fae3951f652a0e38089d328e0bdeeca563553407b78a78c"


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
        self.assertEqual(obs.authorityVersionRef, NETWORK_V4)
        for old in (NETWORK_V1, NETWORK_V2, NETWORK_V3):
            self.assertEqual(compare_projected_version(old, obs), HealthState.SOURCE_ADVANCED_STALE)
        self.assertEqual((obs.currentRecovery or {}).get("targetRole"), "OWNER_RESEARCH_CORPUS")

    def test_runtime_repaired_publication_is_current(self) -> None:
        spec = self.by_owner["research-owner:runtime"]
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(obs.authorityVersionRef, RUNTIME_V6)
        for old in (RUNTIME_V1, RUNTIME_V2, RUNTIME_V3, RUNTIME_V4, RUNTIME_V5):
            self.assertEqual(compare_projected_version(old, obs), HealthState.SOURCE_ADVANCED_STALE)

    def test_runtime_history_preserves_v1_v2_v3_and_current(self) -> None:
        spec = self.by_owner["research-owner:runtime"]
        projection = Atlas([spec]).build()
        self.assertEqual(projection["projectionHealth"][0]["health"], HealthState.CURRENT_TO_SOURCE)
        versions = {row.get("authorityVersionRef"): row.get("currentness") for row in projection["history"]}
        for old in (RUNTIME_V1, RUNTIME_V2, RUNTIME_V3, RUNTIME_V4, RUNTIME_V5):
            self.assertEqual(versions[old], "HISTORICAL_NOT_CURRENT")
        self.assertEqual(versions[RUNTIME_V6], "CURRENT_VERIFIED")

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

    def test_world_currentness_preserves_nonfoundation_nonadmission_and_open_closure(self) -> None:
        spec = self.by_owner["research-owner:world"]
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(obs.authorityVersionRef, WORLD_V2)
        self.assertEqual(compare_projected_version(WORLD_V1, obs), HealthState.SOURCE_ADVANCED_STALE)
        self.assertEqual((obs.currentRecovery or {}).get("locator"), "docs/research/world/README.md")
        projection = Atlas([spec]).build()
        rows = {row["resultRef"]: row for row in projection["results"]}
        self.assertTrue(all(row["classificationHealth"] == "EXPLICIT" for row in rows.values()))
        self.assertEqual(rows["result:world:wdf0-meta-foundation-current-frozen"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(rows["result:world:wdf2-counterfactual-deep-history-nonfoundation"]["standing"], ["HISTORICAL_PRESERVED"])
        self.assertEqual(rows["result:world:wdf3-categorial-deep-history-nonfoundation"]["standing"], ["HISTORICAL_PRESERVED"])
        self.assertEqual(rows["result:world:wdf2-o-historical-superseded-not-admitted"]["standing"], ["HISTORICAL_PRESERVED", "NOT_ADMITTED", "SUPERSEDED"])
        self.assertEqual(rows["result:world:wdf6-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(rows["result:world:tsaf1-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(rows["result:world:tsaf1-not-admitted"]["epistemicVerdict"], "UNDERDETERMINED")
        self.assertEqual(rows["result:world:whole-world-closure-not-established"]["standing"], ["CURRENT"])
        self.assertEqual(rows["result:world:next-world-route-unknown"]["epistemicVerdict"], "UNDERDETERMINED")
        self.assertEqual(rows["result:world:minimal-world-2-boundary-current"]["standing"], ["CURRENT"])
        self.assertEqual(rows["result:world:minimal-world-2-boundary-current"]["epistemicVerdict"], "ESTABLISHED_IN_SCOPE")
        self.assertEqual(rows["result:world:replacement-readiness-verdict-retired"]["epistemicVerdict"], "REJECTED_FOR_PRODUCTION")
        self.assertEqual(rows["result:world:legacy-flat-auto-upgrader-retired"]["epistemicVerdict"], "REJECTED_FOR_PRODUCTION")

    def test_standalone_network_and_normative_preserve_distinct_semantic_authority(self) -> None:
        network_spec = self.by_owner["research-owner:network"]
        normative_spec = self.by_owner["research-owner:ordivon-normative"]
        network_obs = Atlas([network_spec]).observe(network_spec)
        normative_obs = Atlas([normative_spec]).observe(normative_spec)
        self.assertEqual(network_obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(normative_obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertNotEqual(network_spec.repo, normative_spec.repo)
        self.assertNotEqual(network_obs.transportRevision, normative_obs.transportRevision)
        self.assertEqual(network_obs.authorityVersionRef, NETWORK_V4)
        self.assertEqual(normative_obs.authorityVersionRef, NORMATIVE_V4)
        for old in (NORMATIVE_V1, NORMATIVE_V2, NORMATIVE_V3):
            self.assertEqual(compare_projected_version(old, normative_obs), HealthState.SOURCE_ADVANCED_STALE)
        self.assertNotEqual(network_obs.authorityVersionRef, normative_obs.authorityVersionRef)
        self.assertEqual(compare_projected_version(NETWORK_V4, network_obs), HealthState.CURRENT_TO_SOURCE)
        self.assertEqual((network_obs.currentRecovery or {}).get("locator"), "README.md")
        self.assertEqual((normative_obs.currentRecovery or {}).get("locator"), "README.md")
        projection = Atlas([network_spec, normative_spec]).build()
        rows = {row["resultRef"]: row for row in projection["results"]}
        self.assertTrue(all(row["classificationHealth"] == "EXPLICIT" for row in rows.values()))
        self.assertEqual(rows["result:normative:numbered-foundation-count-zero-current-frozen"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(rows["result:normative:onf-numbered-series-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(rows["result:normative:phr-numbered-foundation-series-not-admitted"]["standing"], ["CURRENT", "NOT_ADMITTED"])
        self.assertEqual(rows["result:normative:phr1-historical-origin-preserved"]["standing"], ["HISTORICAL_PRESERVED"])
        self.assertFalse(any(ref.startswith("result:normative:phr2") or ref.startswith("result:normative:phr3") or ref.startswith("result:normative:phr4") for ref in rows))


if __name__ == "__main__":
    unittest.main()
