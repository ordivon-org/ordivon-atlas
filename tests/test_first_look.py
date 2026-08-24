from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ordivon_atlas.first_look import (
    inspect_prior_result_candidate,
    prior_result_first_look,
)


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
            self.assertEqual(inspected["content"]["sectionCount"], 1)
            self.assertEqual(inspected["content"]["sections"][0]["text"], content)
            self.assertEqual(
                inspected["content"]["projection"],
                "query-relative-exact-markdown-sections",
            )
            self.assertFalse(inspected["content"]["projectionTruncated"])
            self.assertTrue(inspected["content"]["fullContentAvailableViaRawEscape"])
            self.assertEqual(inspected["contentBytes"], len(content.encode("utf-8")))
            self.assertTrue(inspected["contentDigest"].startswith("sha256:"))
            self.assertFalse(inspected["claims"]["semanticEquivalenceInferred"])
            self.assertFalse(inspected["claims"]["researchAdmissionGranted"])

    def test_inspect_curated_candidate_projects_only_query_matching_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            content = (
                "# Prior result\n\n"
                "## Unrelated\n\nThis section discusses weather only.\n\n"
                "## Consumption\n\nValue != Consumption != RealizedBenefit.\n\n"
                "## Another unrelated\n\nNo matching vocabulary here.\n"
            )
            (synthesis / "prior.md").write_text(content, encoding="utf-8")
            inspected = inspect_prior_result_candidate(
                "consumption benefit",
                "synthesis/prior.md",
                "$file",
                repository_root=root,
            )
            sections = inspected["content"]["sections"]
            self.assertEqual([section["heading"] for section in sections], ["Consumption"])
            self.assertEqual(
                sections[0]["text"],
                "## Consumption\n\nValue != Consumption != RealizedBenefit.\n\n",
            )
            self.assertLess(
                inspected["content"]["projectedBytes"],
                inspected["contentBytes"],
            )

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

    def test_inspection_projection_can_be_caller_bounded_below_owner_maximum(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            text = "# Target\n\n" + ("needle alpha beta gamma\n" * 150) + "\n## Second\n\n" + ("needle delta\n" * 150)
            path = synthesis / "target.md"
            path.write_text(text, encoding="utf-8")
            first = prior_result_first_look(
                "needle", repository_root=root, generated_dir="generated", limit=8
            )
            candidate = first["candidates"][0]
            inspected = inspect_prior_result_candidate(
                "needle",
                candidate["path"],
                candidate["locator"],
                repository_root=root,
                generated_dir="generated",
                limit=8,
                max_projection_bytes=4096,
            )
            content = inspected["content"]
            self.assertEqual(content["projectionByteLimit"], 4096)
            self.assertLessEqual(content["projectedBytes"], 4096)
            self.assertTrue(content["fullContentAvailableViaRawEscape"])
            self.assertTrue(content["projectionTruncated"])
            with self.assertRaisesRegex(ValueError, "max projection bytes"):
                inspect_prior_result_candidate(
                    "needle",
                    candidate["path"],
                    candidate["locator"],
                    repository_root=root,
                    generated_dir="generated",
                    limit=8,
                    max_projection_bytes=12_289,
                )

    def test_repository_ppd_consumption_anchor_precedes_adjacent_pressure_projections(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for query in (
            "PPD proactive pressure discovery",
            "proactive pressure discovery",
            "pressure discovery representation generator countermodel",
            "主动压力发现 表征 生成器",
        ):
            result = prior_result_first_look(
                query, repository_root=root, generated_dir="generated", limit=5
            )
            self.assertGreaterEqual(result["candidateCount"], 1)
            self.assertEqual(
                result["candidates"][0]["path"],
                "synthesis/proactive-pressure-discovery-ppd/README.md",
            )

    def test_repository_ppd_anchor_projects_generic_scope_under_current_inspect_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        query = "PPD proactive pressure discovery"
        first = prior_result_first_look(
            query, repository_root=root, generated_dir="generated", limit=5
        )
        candidate = first["candidates"][0]
        inspected = inspect_prior_result_candidate(
            query, candidate["path"], candidate["locator"],
            repository_root=root, generated_dir="generated", limit=5
        )
        self.assertEqual(
            inspected["content"]["projection"],
            "query-relative-exact-markdown-sections",
        )
        projected = "\n".join(
            section["text"] for section in inspected["content"]["sections"]
        )
        self.assertIn("non-authoritative-source-preserving-consumption-anchor", projected)
        self.assertIn("task:proactive-pressure-discovery-open-research-20260820@59", projected)
        self.assertIn("new discriminating pressure", projected)
        self.assertIn("hypothesis, candidate or generator spaces", projected)
        self.assertTrue(inspected["content"]["fullContentAvailableViaRawEscape"])

    def test_repository_ppd_chinese_alias_inspection_reaches_generic_semantics(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for query in (
            "主动压力发现 表征 生成器",
            "主动判别压力 搜索几何",
        ):
            first = prior_result_first_look(
                query, repository_root=root, generated_dir="generated", limit=5
            )
            candidate = first["candidates"][0]
            self.assertEqual(
                candidate["path"],
                "synthesis/proactive-pressure-discovery-ppd/README.md",
            )
            inspected = inspect_prior_result_candidate(
                query, candidate["path"], candidate["locator"],
                repository_root=root, generated_dir="generated", limit=5
            )
            headings = [
                section["heading"] for section in inspected["content"]["sections"]
            ]
            self.assertIn("Generic referent / 通用指称", headings)
            projected = "\n".join(
                section["text"] for section in inspected["content"]["sections"]
            )
            self.assertIn("new discriminating pressure", projected)
            self.assertIn("hypothesis, candidate or generator spaces", projected)

    def test_repository_ppd_anchor_excludes_self_calibration_from_first_object(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (
            root / "synthesis" / "proactive-pressure-discovery-ppd" / "README.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("Consumption calibration", text)
        self.assertNotIn("representation experiments recorded", text)

    def test_repository_ppd_anchor_does_not_displace_adjacent_owner_specific_queries(self) -> None:
        root = Path(__file__).resolve().parents[1]
        rsi = prior_result_first_look(
            "RSI option pressure capability",
            repository_root=root, generated_dir="generated", limit=5
        )
        self.assertTrue(rsi["candidates"])
        self.assertIn("rsi-pal-option-pressure-capability", rsi["candidates"][0]["path"])
        self.assertNotEqual(
            rsi["candidates"][0]["path"],
            "synthesis/proactive-pressure-discovery-ppd/README.md",
        )
        open_interface = prior_result_first_look(
            "open interface comparability transformation language",
            repository_root=root, generated_dir="generated", limit=5
        )
        self.assertTrue(open_interface["candidates"])
        self.assertIn("finite-intelligence-open-interface-formation", open_interface["candidates"][0]["path"])
        self.assertNotEqual(
            open_interface["candidates"][0]["path"],
            "synthesis/proactive-pressure-discovery-ppd/README.md",
        )


if __name__ == "__main__":
    unittest.main()
