import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SECURITY="research-owner:security"

class SecurityRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=json.loads((ROOT/"config/sources.json").read_text())["sources"]
        cls.frontier=json.loads((ROOT/"config/owner-frontier.json").read_text())["entries"]

    def test_security_is_unique_registered_owner(self):
        self.assertEqual(sum(1 for r in self.sources if r["ownerResearchRef"]==SECURITY),1)

    def test_security_uses_remote_exact_main_and_owner_native_recovery_carrier(self):
        r=next(r for r in self.sources if r["ownerResearchRef"]==SECURITY)
        self.assertEqual(r["authorityRef"],"authority:ordivon:research-owner:security")
        self.assertEqual(r["corpusRoot"],"research/security")
        self.assertEqual(r["ref"],"refs/heads/main")
        self.assertEqual(r["remote"],"git@github.com:zycxfyh/ordivon-security.git")
        self.assertIn("https://github.com/zycxfyh/ordivon-security.git",r["remoteFallbacks"])

    def test_security_frontier_candidate_is_retired(self):
        self.assertNotIn("project:security",{r["subjectRef"] for r in self.frontier})
        self.assertNotIn("/root/projects/ordivon-security",{r["repo"] for r in self.frontier})

if __name__=="__main__": unittest.main()
