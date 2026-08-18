import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = "research-owner:media"

class MediaRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / "config/sources.json").read_text())["sources"]
        cls.by_owner = {x["ownerResearchRef"]: x for x in cls.sources}

    def test_media_is_tenth_independent_source(self):
        self.assertEqual(len(self.sources), 10)
        self.assertEqual(len(self.by_owner), 10)
        self.assertIn(MEDIA, self.by_owner)

    def test_media_uses_dedicated_authority_transport_ref(self):
        m = self.by_owner[MEDIA]
        self.assertEqual(m["authorityRef"], "authority:ordivon:research-owner:media")
        self.assertEqual(m["corpusRoot"], "research/media")
        self.assertEqual(m["ref"], "refs/heads/research/media-authority-publication-20260819")
        self.assertEqual(m["remote"], "https://github.com/zycxfyh/ordivon-media.git")
        self.assertEqual(m["repo"], "/root/projects/ordivon-media")

    def test_media_identity_is_not_studio_or_web_or_game(self):
        m = self.by_owner[MEDIA]
        self.assertNotIn("studio", m["ownerResearchRef"])
        self.assertNotIn("web", m["ownerResearchRef"])
        self.assertNotIn("game", m["ownerResearchRef"])

if __name__ == "__main__":
    unittest.main()
