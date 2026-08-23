from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from ordivon_atlas.first_look import prior_result_first_look


class PriorResultFirstLookTests(unittest.TestCase):
    def test_generated_and_synthesis_candidates_are_bounded_and_non_authoritative(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root / "generated"
            synthesis = root / "synthesis" / "research"
            generated.mkdir()
            synthesis.mkdir(parents=True)
            (generated / "results.json").write_text(
                json.dumps(
                    [
                        {
                            "owner": "research-owner:fixture",
                            "title": "result consumer benefit graph",
                            "currentness": "CURRENT_VERIFIED",
                            "summary": "prior result connected consumers to realized benefit",
                        },
                        {
                            "owner": "research-owner:other",
                            "title": "unrelated topic",
                            "currentness": "CURRENT_VERIFIED",
                        },
                    ]
                ),
                encoding="utf-8",
            )
            (generated / "projection-health.json").write_text(
                json.dumps([{"health": "CURRENT_TO_SOURCE"}]), encoding="utf-8"
            )
            (synthesis / "anti-rediscovery.md").write_text(
                "A result-to-consumer-to-benefit graph was discussed as anti-rediscovery context.",
                encoding="utf-8",
            )
            result = prior_result_first_look(
                "result consumer benefit graph",
                repository_root=root,
                generated_dir="generated",
                limit=2,
            )
            self.assertEqual(result["candidateCount"], 2)
            self.assertFalse(result["claims"]["semanticEquivalenceInferred"])
            self.assertFalse(result["claims"]["researchAdmissionGranted"])
            self.assertEqual(
                result["claims"]["noveltyStanding"],
                "UNKNOWN_CALLER_MUST_ADJUDICATE",
            )
            self.assertEqual(result["projectionHealth"]["currentness"], "CURRENT_VERIFIED")
            classes = {item["sourceClass"] for item in result["candidates"]}
            self.assertIn("generated-owner-projection", classes)
            self.assertIn("curated-synthesis", classes)

    def test_synthesis_remains_available_when_generated_health_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            (synthesis / "prior.md").write_text(
                "finite intelligence consequence feedback revision",
                encoding="utf-8",
            )
            result = prior_result_first_look(
                "consequence feedback",
                repository_root=root,
                generated_dir="generated",
            )
            self.assertEqual(result["candidateCount"], 1)
            self.assertEqual(result["candidates"][0]["sourceClass"], "curated-synthesis")
            self.assertEqual(
                result["projectionHealth"]["currentness"],
                "UNKNOWN_NO_GENERATED_PROJECTION_HEALTH",
            )

    def test_chinese_query_uses_bounded_cjk_terms(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            (synthesis / "中文.md").write_text(
                "研究消费与现实后果之间需要持续反馈。",
                encoding="utf-8",
            )
            result = prior_result_first_look(
                "研究消费 现实后果",
                repository_root=root,
            )
            self.assertEqual(result["candidateCount"], 1)
            self.assertTrue(result["queryTerms"])
            self.assertFalse(result["claims"]["ownerTruthMinted"])

    def test_limit_is_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "limit"):
            prior_result_first_look("query", limit=0)


if __name__ == "__main__":
    unittest.main()
