from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from ordivon_atlas.first_look import inspect_prior_result_candidate, prior_result_first_look


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

    def test_inspect_curated_candidate_is_bound_to_first_look_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            content = "result consumer benefit graph full standing\nValue != Consumption != RealizedBenefit\n"
            path = synthesis / "prior.md"
            path.write_text(content, encoding="utf-8")
            inspected = inspect_prior_result_candidate(
                "result consumer benefit graph",
                "synthesis/prior.md",
                "$file",
                repository_root=root,
            )
            self.assertEqual(inspected["candidate"]["sourceClass"], "curated-synthesis")
            self.assertEqual(inspected["content"]["text"], content)
            self.assertEqual(inspected["contentBytes"], len(content.encode("utf-8")))
            self.assertTrue(inspected["contentDigest"].startswith("sha256:"))
            self.assertFalse(inspected["claims"]["semanticEquivalenceInferred"])
            self.assertFalse(inspected["claims"]["researchAdmissionGranted"])

    def test_inspect_generated_candidate_returns_exact_row(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root / "generated"
            generated.mkdir()
            row = {
                "owner": "research-owner:fixture",
                "title": "result consumer benefit graph",
                "currentness": "CURRENT_VERIFIED",
            }
            (generated / "results.json").write_text(
                json.dumps([row]), encoding="utf-8"
            )
            first = prior_result_first_look(
                "result consumer benefit graph", repository_root=root
            )
            candidate = first["candidates"][0]
            inspected = inspect_prior_result_candidate(
                "result consumer benefit graph",
                candidate["path"],
                candidate["locator"],
                repository_root=root,
            )
            self.assertEqual(inspected["content"]["json"], row)
            self.assertEqual(inspected["candidate"]["path"], "generated/results.json")

    def test_inspect_rejects_existing_file_not_returned_by_first_look(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            (synthesis / "matching.md").write_text(
                "result consumer benefit graph", encoding="utf-8"
            )
            (synthesis / "secret.md").write_text("unrelated", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bounded first-look result"):
                inspect_prior_result_candidate(
                    "result consumer benefit graph",
                    "synthesis/secret.md",
                    "$file",
                    repository_root=root,
                )

    def test_limit_is_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "limit"):
            prior_result_first_look("query", limit=0)


if __name__ == "__main__":
    unittest.main()
