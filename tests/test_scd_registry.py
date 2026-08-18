import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCD = "research-owner:semantics-of-computational-descriptions"
CP = "research-owner:computational-possibility"

class SCDRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / "config/sources.json").read_text())["sources"]
        cls.by_owner = {x["ownerResearchRef"]: x for x in cls.sources}

    def test_scd_is_an_independent_eighth_source(self):
        self.assertEqual(len(self.sources), 8)
        self.assertIn(SCD, self.by_owner)
        self.assertIn(CP, self.by_owner)
        self.assertEqual(len(self.by_owner), len(self.sources))

    def test_shared_repository_does_not_merge_scd_and_cp(self):
        scd = self.by_owner[SCD]
        cp = self.by_owner[CP]
        self.assertEqual(scd["repo"], cp["repo"])
        self.assertEqual(scd["remote"], cp["remote"])
        self.assertNotEqual(scd["authorityRef"], cp["authorityRef"])
        self.assertNotEqual(scd["corpusRoot"], cp["corpusRoot"])
        self.assertNotEqual(scd["ref"], cp["ref"])

    def test_scd_source_is_owner_native_research_ref(self):
        scd = self.by_owner[SCD]
        self.assertEqual(scd["corpusRoot"], "research/core/semantics-of-computational-descriptions")
        self.assertEqual(scd["ref"], "refs/heads/research/scd-applied-dogfood-20260818")
        self.assertEqual(scd["authorityRef"], "authority:ordivon:research-owner:semantics-of-computational-descriptions")

if __name__ == "__main__":
    unittest.main()
