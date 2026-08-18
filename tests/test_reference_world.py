from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "reference/foundational-disciplines-v0.json"


class ExternalReferenceFoundationalDisciplinesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = json.loads(MODEL.read_text())
        cls.nodes = cls.model["nodes"]
        cls.relations = cls.model["relations"]
        cls.sources = cls.model["sources"]
        cls.by_ref = {n["refId"]: n for n in cls.nodes}

    def test_contract_is_open_world_non_authoritative_and_coverage_free(self) -> None:
        self.assertEqual(self.model["truthRole"], "NON_AUTHORITATIVE_EXTERNAL_REFERENCE")
        self.assertTrue(self.model["openWorld"])
        self.assertEqual(self.model["ordivonCrosswalks"], [])
        self.assertEqual(self.model["coverageAssessments"], [])
        self.assertIn("never DOES_NOT_EXIST", self.model["semantics"]["NOT_REPRESENTED"])

    def test_six_seed_roots_do_not_close_foundational_census(self) -> None:
        roots = {n["label"] for n in self.nodes if n["kind"] == "DISCIPLINE"}
        self.assertEqual(roots, {"Mathematics", "Philosophy", "Physics", "Biology", "Chemistry", "Engineering"})
        scope = self.model["scope"]
        self.assertEqual(set(scope["seedWave0"]), roots)
        self.assertEqual(scope["censusState"], "OPEN_NOT_EXHAUSTIVE")
        self.assertEqual(scope["foundationalDomainCount"], "UNKNOWN_UNTIL_CENSUS")
        self.assertIn("MUST NOT", scope["seedPurpose"])
        self.assertNotIn("deferred", scope)

    def test_every_node_and_relation_is_source_qualified(self) -> None:
        for node in self.nodes:
            self.assertTrue(node["sourceEvidence"], node["refId"])
            for ev in node["sourceEvidence"]:
                self.assertIn(ev["sourceRef"], self.sources)
        for rel in self.relations:
            self.assertTrue(rel["sourceEvidence"], (rel["fromRef"], rel["toRef"]))
            for ev in rel["sourceEvidence"]:
                self.assertIn(ev["sourceRef"], self.sources)

    def test_wikipedia_outline_membership_never_mints_subclass_semantics(self) -> None:
        self.assertFalse(any(r["relationType"] == "SUBCLASS_OF" for r in self.relations))
        for rel in self.relations:
            if rel["relationType"] == "TOPICAL_MEMBER_OF":
                self.assertEqual(rel["basis"], "SOURCE_DERIVED_WEAK")

    def test_reference_identity_has_no_duplicate_normalized_labels(self) -> None:
        normalized: dict[str, list[str]] = {}
        for node in self.nodes:
            key = " ".join(node["label"].lower().replace("/", " ").split())
            normalized.setdefault(key, []).append(node["refId"])
        duplicates = {k: v for k, v in normalized.items() if len(v) > 1}
        self.assertEqual(duplicates, {}, f"duplicate reference identities: {duplicates}")

    def test_cross_domain_spaces_are_multi_parent_not_forced_into_one_tree(self) -> None:
        overlaps = [n for n in self.nodes if n["kind"] == "OVERLAP_SPACE"]
        self.assertGreaterEqual(len(overlaps), 8)
        for node in overlaps:
            self.assertGreaterEqual(len(node["domainRefs"]), 2, node["refId"])
            rel_targets = {r["toRef"] for r in self.relations if r["fromRef"] == node["refId"] and r["relationType"] == "OVERLAPS_DOMAIN"}
            self.assertEqual(rel_targets, set(node["domainRefs"]))

    def test_all_relation_endpoints_exist_and_reference_model_is_bounded(self) -> None:
        refs = set(self.by_ref)
        for rel in self.relations:
            self.assertIn(rel["fromRef"], refs)
            self.assertIn(rel["toRef"], refs)
        self.assertGreaterEqual(len(self.nodes), 60)
        self.assertLessEqual(len(self.nodes), 150)

    def test_foundational_census_is_open_and_strictly_broader_than_seed_wave(self) -> None:
        census = json.loads((ROOT / "reference/foundational-domain-census-v0.json").read_text())
        self.assertEqual(census["state"], "OPEN_NOT_EXHAUSTIVE")
        self.assertEqual(census["rootCount"], "UNKNOWN")
        candidates = {c for family in census["families"] for c in family["candidates"]}
        self.assertGreater(len(candidates), 30)
        for expected in ("Astronomy and astrophysics", "Earth science / geoscience", "Atmospheric science and meteorology", "Oceanography", "Linguistics", "Cognitive science", "Statistics and probability"):
            self.assertIn(expected, candidates)
        self.assertEqual(census["admissionPolicy"]["censusClosure"], "NOT_ALLOWED_IN_V0")



if __name__ == "__main__":
    unittest.main()
