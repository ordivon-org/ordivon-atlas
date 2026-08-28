from __future__ import annotations

import unittest
from pathlib import Path

from ordivon_atlas.atlas import SourceObservation
from ordivon_atlas.cli import _owner_observation_payload


class OwnerCurrentnessCliTests(unittest.TestCase):
    def observation(self) -> SourceObservation:
        return SourceObservation(
            ownerResearchRef="research-owner:network",
            authorityRef="authority:ordivon:research-owner:network",
            transportRevision="a" * 40,
            authorityVersionRef="sha256:" + "b" * 64,
            health="CURRENT_TO_SOURCE",
            reason=None,
            currentRecovery={"targetRole": "OWNER_RESEARCH_CORPUS", "locator": "README.md"},
            publication={"kind": "large-owner-publication", "statements": [1, 2, 3]},
            publicationPath="authority/publications/example.json",
        )

    def test_default_owner_currentness_payload_is_bounded(self) -> None:
        payload = _owner_observation_payload(
            self.observation(), "Interlocus", ["interlocus", "network"], include_publication=False
        )
        self.assertNotIn("publication", payload)
        self.assertFalse(payload["publicationIncluded"])
        self.assertEqual(payload["health"], "CURRENT_TO_SOURCE")
        self.assertEqual(payload["currentRecovery"]["locator"], "README.md")

    def test_owner_publication_is_explicit_opt_in(self) -> None:
        payload = _owner_observation_payload(
            self.observation(), "Interlocus", ["interlocus", "network"], include_publication=True
        )
        self.assertEqual(payload["publication"]["kind"], "large-owner-publication")
        self.assertTrue(payload["publicationIncluded"])

    def test_generic_representation_selector_is_retired(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertFalse((root / "src/ordivon_atlas/representation_selection.py").exists())
        cli = (root / "src/ordivon_atlas/cli.py").read_text(encoding="utf-8")
        self.assertNotIn("select-representation", cli)



if __name__ == "__main__":
    unittest.main()
