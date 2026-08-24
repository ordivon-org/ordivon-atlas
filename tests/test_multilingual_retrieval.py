from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from ordivon_atlas.first_look import (
    inspect_prior_result_candidate,
    prior_result_first_look_many,
    retrieval_authoring_context,
    retrieval_coordinate_profile,
    retrieval_representation_profile,
)


class MultilingualRetrievalTests(unittest.TestCase):
    def test_representation_profile_is_mechanical_not_semantic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            (synthesis / "a.md").write_text("Research engineering consequence", encoding="utf-8")
            (synthesis / "b.md").write_text("研究 research", encoding="utf-8")
            value = retrieval_representation_profile(repository_root=root)
            self.assertEqual(value["curatedSynthesisCorpus"]["markdownFileCount"], 2)
            self.assertEqual(value["curatedSynthesisCorpus"]["dominantObservedScript"], "latin")
            self.assertFalse(value["retrieval"]["crossLanguageTranslationByAtlas"])
            self.assertFalse(value["retrieval"]["semanticSimilarityByAtlas"])
            self.assertFalse(value["claims"]["callerIntentTranslated"])
            self.assertFalse(value["claims"]["queryVariantGenerated"])

    def test_coordinate_profile_is_source_ordered_and_task_neutral(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "synthesis" / "research-process-lineage" / "SOURCE-INDEX.md"
            source.parent.mkdir(parents=True)
            text = """# Index\n\n## Episode A\n\nKey retrieval aliases / pressure terms:\n\n- alpha / first\n- alpha second\n\n## Episode B\n\nKey retrieval aliases / pressure terms:\n\n- beta / first\n"""
            source.write_text(text, encoding="utf-8")
            value = retrieval_coordinate_profile(repository_root=root)
            self.assertEqual(
                value["coordinates"],
                [
                    {"sectionHeading": "Episode A", "retrievalAlias": "alpha / first"},
                    {"sectionHeading": "Episode B", "retrievalAlias": "beta / first"},
                ],
            )
            self.assertEqual(
                value["source"]["contentDigest"],
                "sha256:" + hashlib.sha256(text.encode()).hexdigest(),
            )
            self.assertFalse(value["selection"]["taskConditioned"])
            self.assertFalse(value["selection"]["semanticRankingPerformed"])
            self.assertFalse(value["claims"]["coordinatesSemanticallyEquivalentToIntent"])

    def test_many_deduplicates_and_preserves_best_variant_for_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            (synthesis / "one.md").write_text(
                "# Theory to Engineering\n\nResearch engineering capability consequences translation gap.\n",
                encoding="utf-8",
            )
            (synthesis / "two.md").write_text("Research only adjacent history.", encoding="utf-8")
            result = prior_result_first_look_many(
                ["研究成果无法工程化", "research engineering capability consequences"],
                repository_root=root,
                limit=4,
            )
            self.assertGreaterEqual(result["candidateCount"], 1)
            top = result["candidates"][0]
            self.assertEqual(top["path"], "synthesis/one.md")
            self.assertEqual(top["bestVariantIndex"], 1)
            self.assertEqual(top["matchedVariantIndexes"], [1])
            self.assertFalse(result["claims"]["queryVariantsSemanticallyEquivalent"])
            inspect_query = result["queryVariants"][top["bestVariantIndex"]]
            inspected = inspect_prior_result_candidate(
                inspect_query,
                top["path"],
                top["locator"],
                repository_root=root,
                limit=32,
            )
            self.assertEqual(inspected["candidate"]["path"], top["path"])
            self.assertFalse(inspected["claims"]["semanticEquivalenceInferred"])


    def test_authoring_context_composes_owner_facts_without_query_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthesis = root / "synthesis"
            synthesis.mkdir()
            (synthesis / "one.md").write_text("Research engineering", encoding="utf-8")
            source = synthesis / "research-process-lineage" / "SOURCE-INDEX.md"
            source.parent.mkdir(parents=True)
            source.write_text(
                "## Episode A\n\nKey retrieval aliases / pressure terms:\n\n- theory to engineering\n",
                encoding="utf-8",
            )
            value = retrieval_authoring_context(repository_root=root)
            self.assertEqual(
                value["kind"], "ordivon.atlas-retrieval-authoring-context-experimental"
            )
            self.assertEqual(value["coordinateProfile"]["coordinates"][0]["retrievalAlias"], "theory to engineering")
            self.assertFalse(value["claims"]["callerIntentTranslated"])
            self.assertFalse(value["claims"]["queryVariantGenerated"])
            self.assertFalse(value["claims"]["semanticEquivalenceInferred"])

    def test_many_rejects_unbounded_variant_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "1 to 4"):
            prior_result_first_look_many([])
        with self.assertRaisesRegex(ValueError, "1 to 4"):
            prior_result_first_look_many(["a", "b", "c", "d", "e"])


if __name__ == "__main__":
    unittest.main()
