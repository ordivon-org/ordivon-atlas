from __future__ import annotations

import json
import unittest
from pathlib import Path


class InterlocusP2ConsumerEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / "synthesis" / "2026-08-27-interlocus-consumer-projection-p2" / "natural-fresh-agent-dogfood.json"
        self.value = json.loads(path.read_text(encoding="utf-8"))

    def test_fresh_agent_selected_p2_without_epistemic_inflation(self) -> None:
        self.assertEqual(self.value["retrieval"]["selectedRank"], 1)
        self.assertEqual(
            self.value["retrieval"]["selectedPath"],
            "synthesis/2026-08-27-interlocus-consumer-projection-p2/README.md",
        )
        self.assertEqual(self.value["adjudication"]["decision"], "consume_prior")
        self.assertEqual(self.value["adjudication"]["coverage"], "substantial")
        self.assertFalse(self.value["adjudication"]["semanticEquivalenceEstablished"])
        self.assertFalse(self.value["adjudication"]["noveltyEstablished"])
        self.assertFalse(self.value["adjudication"]["researchAdmissionGranted"])

    def test_usage_is_bounded_and_no_domain_tool_authority_was_used(self) -> None:
        usage = self.value["usage"]
        self.assertEqual(usage["providerModelCallCount"], 3)
        self.assertEqual(usage["totalTokens"], 9642)
        self.assertEqual(self.value["retrieval"]["ownerReadCount"], 3)
        self.assertEqual(usage["providerDomainToolCallCount"], 0)
        self.assertEqual(usage["conclusionCorrections"], 0)
        self.assertEqual(usage["toolCorrections"], 0)
        self.assertFalse(self.value["claims"]["productionServiceAdmissionGranted"])


if __name__ == "__main__":
    unittest.main()
