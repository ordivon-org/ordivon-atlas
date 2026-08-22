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

    def test_scd_remains_an_independent_registered_source(self):
        self.assertEqual(len(self.sources), 10)
        self.assertIn(SCD, self.by_owner)
        self.assertIn(CP, self.by_owner)
        self.assertEqual(len(self.by_owner), len(self.sources))

    def test_standalone_repositories_preserve_scd_cp_semantic_distinction(self):
        scd = self.by_owner[SCD]
        cp = self.by_owner[CP]
        self.assertNotEqual(scd["repo"], cp["repo"])
        self.assertNotEqual(scd["remote"], cp["remote"])
        self.assertNotEqual(scd["authorityRef"], cp["authorityRef"])
        self.assertEqual(scd["corpusRoot"], "")
        self.assertEqual(cp["corpusRoot"], "")
        self.assertEqual(scd["ref"], "refs/heads/main")
        self.assertEqual(cp["ref"], "refs/heads/main")

    def test_scd_source_is_owner_native_research_ref(self):
        scd = self.by_owner[SCD]
        self.assertEqual(scd["corpusRoot"], "")
        self.assertEqual(scd["ref"], "refs/heads/main")
        self.assertEqual(scd["repo"], "/root/projects/ordivon-scd")
        self.assertEqual(scd["authorityRef"], "authority:ordivon:research-owner:semantics-of-computational-descriptions")

if __name__ == "__main__":
    unittest.main()
