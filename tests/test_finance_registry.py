import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINANCE = "research-owner:finance"


class FinanceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / "config/sources.json").read_text())["sources"]
        cls.by_owner = {x["ownerResearchRef"]: x for x in cls.sources}
        cls.frontier = json.loads((ROOT / "config/owner-frontier.json").read_text())["entries"]

    def test_finance_is_unique_registered_research_owner(self):
        self.assertEqual(len(self.by_owner), len(self.sources))
        self.assertEqual(sum(1 for x in self.sources if x["ownerResearchRef"] == FINANCE), 1)
        self.assertIn(FINANCE, self.by_owner)

    def test_finance_uses_exact_local_git_currentness_transport(self):
        f = self.by_owner[FINANCE]
        self.assertEqual(f["authorityRef"], "authority:ordivon:research-owner:finance")
        self.assertEqual(f["repo"], "/root/projects/ordivon-finance")
        self.assertEqual(f["ref"], "refs/heads/main")
        self.assertEqual(f["corpusRoot"], "research/finance")
        self.assertEqual(f["transportMode"], "local_git")
        self.assertIsNone(f["remote"])

    def test_finance_candidate_frontier_is_retired_after_admission(self):
        self.assertNotIn("project:finance", {x["subjectRef"] for x in self.frontier})
        self.assertNotIn("/root/projects/ordivon-finance", {x["repo"] for x in self.frontier})


if __name__ == "__main__":
    unittest.main()
