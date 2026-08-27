import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class FourOwnerPhysicalSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = json.loads((ROOT / "config/sources.json").read_text())["sources"]
        cls.by = {x["ownerResearchRef"]: x for x in rows}

    def test_four_owners_have_standalone_current_physical_homes(self):
        expected = {
            "research-owner:semantics-of-computational-descriptions": "ordivon-scd",
            "research-owner:computational-possibility": "ordivon-computational-possibility",
            "research-owner:ordivon-normative": "ordivon-normative",
            "research-owner:network": "ordivon-interlocus",
        }
        repos = set()
        for owner, repo_name in expected.items():
            row = self.by[owner]
            self.assertEqual(row["repo"], f"/root/projects/{repo_name}")
            self.assertEqual(row["remote"], f"git@github.com:zycxfyh/{repo_name}.git")
            self.assertEqual(row["corpusRoot"], "")
            self.assertEqual(row["ref"], "refs/heads/main")
            repos.add(row["repo"])
        self.assertEqual(len(repos), 4)

    def test_interlocus_physical_rename_does_not_rename_semantic_owner(self):
        row = self.by["research-owner:network"]
        self.assertEqual(row["authorityRef"], "authority:ordivon:research-owner:network")
        self.assertTrue(row["repo"].endswith("/ordivon-interlocus"))

    def test_readme_first_contact_matches_current_interlocus_physical_home(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("standalone current physical home `ordivon-interlocus`", readme)
        self.assertNotIn("lives inside the shared `ordivon-research` durability repository", readme)

if __name__ == "__main__":
    unittest.main()
