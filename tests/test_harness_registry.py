import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = "research-owner:harness"
HOST = "research-owner:host"
RUNTIME = "research-owner:runtime"


class HarnessRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / "config/sources.json").read_text())["sources"]
        cls.by_owner = {x["ownerResearchRef"]: x for x in cls.sources}
        cls.frontier = json.loads((ROOT / "config/owner-frontier.json").read_text())["entries"]

    def test_harness_is_eleventh_independent_registered_research_owner(self):
        self.assertEqual(len(self.sources), 11)
        self.assertEqual(len(self.by_owner), 11)
        self.assertIn(HARNESS, self.by_owner)
        self.assertIn(HOST, self.by_owner)
        self.assertIn(RUNTIME, self.by_owner)

    def test_harness_uses_owner_native_main_research_authority(self):
        h = self.by_owner[HARNESS]
        self.assertEqual(h["authorityRef"], "authority:ordivon:research-owner:harness")
        self.assertEqual(h["corpusRoot"], "research")
        self.assertEqual(h["ref"], "refs/heads/main")
        self.assertEqual(h["repo"], "/root/projects/ordivon-harness")
        self.assertEqual(h["remote"], "git@github.com:zycxfyh/ordivon-harness.git")
        self.assertIn("https://github.com/zycxfyh/ordivon-harness.git", h["remoteFallbacks"])

    def test_harness_identity_does_not_collapse_into_host_or_runtime(self):
        h = self.by_owner[HARNESS]
        self.assertNotEqual(h["authorityRef"], self.by_owner[HOST]["authorityRef"])
        self.assertNotEqual(h["authorityRef"], self.by_owner[RUNTIME]["authorityRef"])
        self.assertNotEqual(h["repo"], self.by_owner[HOST]["repo"])
        self.assertNotEqual(h["repo"], self.by_owner[RUNTIME]["repo"])

    def test_harness_deferred_frontier_is_retired_after_source_admission(self):
        subjects = {entry["subjectRef"] for entry in self.frontier}
        repos = {entry["repo"] for entry in self.frontier}
        self.assertNotIn("project:harness", subjects)
        self.assertNotIn("/root/projects/ordivon-harness", repos)


if __name__ == "__main__":
    unittest.main()
