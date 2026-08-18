import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUMAN = "research-owner:human"
NORMATIVE = "research-owner:ordivon-normative"

class HumanRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / "config/sources.json").read_text())["sources"]
        cls.by_owner = {x["ownerResearchRef"]: x for x in cls.sources}

    def test_human_is_ninth_independent_source(self):
        self.assertEqual(len(self.sources), 9)
        self.assertEqual(len(self.by_owner), 9)
        self.assertIn(HUMAN, self.by_owner)

    def test_human_uses_owner_native_repair_ref_and_core_root(self):
        h = self.by_owner[HUMAN]
        self.assertEqual(h["authorityRef"], "authority:ordivon:research-owner:human")
        self.assertEqual(h["corpusRoot"], "research/core")
        self.assertEqual(h["ref"], "refs/heads/repair/human-research-core-materialization-20260818")
        self.assertEqual(h["repo"], "/root/projects/ordivon-human")

    def test_human_and_normative_are_not_authority_conflated(self):
        h = self.by_owner[HUMAN]
        n = self.by_owner[NORMATIVE]
        self.assertNotEqual(h["authorityRef"], n["authorityRef"])
        self.assertNotEqual(h["ownerResearchRef"], n["ownerResearchRef"])
        self.assertNotEqual(h["repo"], n["repo"])

if __name__ == "__main__":
    unittest.main()
