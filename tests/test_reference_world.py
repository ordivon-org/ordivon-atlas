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


    def test_round1_census_is_multi_view_open_and_non_admitting(self) -> None:
        round1 = json.loads((ROOT / "reference/foundational-census-round1-20260819.json").read_text())
        self.assertEqual(round1["state"], "OPEN_NOT_EXHAUSTIVE")
        self.assertEqual(round1["truthRole"], "NON_AUTHORITATIVE_MULTI_VIEW_CENSUS")
        self.assertEqual(round1["closure"], "NOT_CLAIMED")
        self.assertGreaterEqual(len(round1["sources"]), 5)
        self.assertGreaterEqual(len(round1["candidates"]), 30)
        self.assertTrue(all(c["admission"] == "CENSUS_ONLY_NOT_CANONICAL_ROOT" for c in round1["candidates"]))

    def test_round1_forbids_majority_vote_absence_and_broad_parent_ontology(self) -> None:
        round1 = json.loads((ROOT / "reference/foundational-census-round1-20260819.json").read_text())
        forbidden = " | ".join(round1["method"]["forbidden"])
        self.assertIn("Majority vote", forbidden)
        self.assertIn("Absence", forbidden)
        self.assertIn("broad parent", forbidden)
        allowed = set(round1["method"]["signalSemantics"])
        for candidate in round1["candidates"]:
            self.assertTrue(set(candidate["sourceSignals"]).issubset(set(round1["sources"])))
            self.assertTrue(set(candidate["sourceSignals"].values()).issubset(allowed))

    def test_round1_expands_far_beyond_original_six_seeds(self) -> None:
        round1 = json.loads((ROOT / "reference/foundational-census-round1-20260819.json").read_text())
        names = {c["candidate"] for c in round1["candidates"]}
        required = {
            "Statistics and probability",
            "Logic",
            "Computer and information sciences",
            "Astronomy and astrophysics",
            "Earth science / geoscience",
            "Atmospheric science and meteorology",
            "Oceanography",
            "Neuroscience",
            "Cognitive science",
            "Linguistics",
            "History",
            "Measurement, metrology and standards",
        }
        self.assertTrue(required.issubset(names), required - names)

    def test_round1_preserves_known_classification_pressure_zones(self) -> None:
        round1 = json.loads((ROOT / "reference/foundational-census-round1-20260819.json").read_text())
        by_name = {c["candidate"]: c for c in round1["candidates"]}
        for name in ("Neuroscience", "Cognitive science", "Physical geography"):
            self.assertIn("DIVERGENT", set(by_name[name]["sourceSignals"].values()), name)
        self.assertIn("FOUNDATIONAL", by_name["Engineering science and technology"]["provisionalRole"])
        self.assertIn("APPLIED_PROFESSIONAL", by_name["Medicine and health sciences"]["provisionalRole"])

    def test_round1_does_not_prematurely_admit_later_social_political_roots(self) -> None:
        round1 = json.loads((ROOT / "reference/foundational-census-round1-20260819.json").read_text())
        names = {c["candidate"] for c in round1["candidates"]}
        for later in ("Political science", "Law", "Public administration", "Governance"):
            self.assertNotIn(later, names)


    def test_round1_probe_families_are_nonexclusive_and_not_roots(self) -> None:
        topo = json.loads((ROOT / "reference/foundational-census-round1-families-20260819.json").read_text())
        self.assertEqual(topo["truthRole"], "NON_AUTHORITATIVE_PROBE_TOPOLOGY")
        self.assertIn("MUST NOT", topo["rootSemantics"])
        self.assertEqual(topo["closure"], "NOT_CLAIMED")
        memberships = {}
        for family in topo["families"]:
            self.assertEqual(family["status"], "PROVISIONAL_NONEXCLUSIVE")
            for member in family["members"]:
                memberships.setdefault(member, 0)
                memberships[member] += 1
        self.assertGreaterEqual(sum(1 for count in memberships.values() if count > 1), 10)
        for expected in ("Neuroscience", "Philosophy", "Information theory", "Geophysics"):
            self.assertGreater(memberships.get(expected, 0), 1, expected)


    def test_round2a_normalization_separates_identity_role_and_root_admission(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2a-normalization-20260819.json").read_text())
        self.assertEqual(r2["truthRole"], "NON_AUTHORITATIVE_REFERENCE_NORMALIZATION")
        self.assertEqual(r2["state"], "ROUND2A_COMPLETE_CENSUS_OPEN")
        self.assertEqual(r2["closure"], "ROUND2A_COMPLETE_GLOBAL_CENSUS_OPEN")
        self.assertTrue(all(s["rootAdmission"] == "NOT_ADMITTED" for s in r2["normalizedSpaces"]))
        self.assertTrue(all(s["identityStatus"] == "PROVISIONALLY_NORMALIZED" for s in r2["normalizedSpaces"]))
        self.assertIn("MAJOR_DOMAIN_CANDIDATE != CANONICAL_ROOT", r2["policies"]["negativeRule"])

    def test_round2a_pressure_zones_preserve_multi_domain_topology(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2a-normalization-20260819.json").read_text())
        by = {s["spaceRef"]: s for s in r2["normalizedSpaces"]}
        for ref in ("norm:logic", "norm:information-theory", "norm:cognitive-science", "norm:neuroscience", "norm:linguistics", "norm:measurement"):
            self.assertGreaterEqual(len(by[ref]["placements"]), 2, ref)
        self.assertIn("METHODOLOGICAL_AXIS", by["norm:logic"]["roleClasses"])
        self.assertIn("BRIDGE_DOMAIN", by["norm:cognitive-science"]["roleClasses"])
        self.assertIn("METHODOLOGICAL_AXIS", by["norm:measurement"]["roleClasses"])

    def test_round2a_cognitive_science_is_not_reduced_to_psychology(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2a-normalization-20260819.json").read_text())
        by = {s["spaceRef"]: s for s in r2["normalizedSpaces"]}
        cog = by["norm:cognitive-science"]
        self.assertIn("psychology", cog["placements"])
        self.assertIn("neuroscience", cog["placements"])
        self.assertIn("linguistics", cog["placements"])
        self.assertIn("artificial-intelligence", cog["placements"])
        self.assertNotEqual(cog["placements"], ["psychology"])

    def test_round2a_metrology_is_cross_domain_method_axis(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2a-normalization-20260819.json").read_text())
        by = {s["spaceRef"]: s for s in r2["normalizedSpaces"]}
        met = by["norm:measurement"]
        self.assertIn("METHODOLOGICAL_AXIS", met["roleClasses"])
        self.assertIn("EPISTEMIC_INFRASTRUCTURE", met["roleClasses"])
        for domain in ("physics", "chemistry", "biology", "engineering"):
            self.assertIn(domain, met["placements"])
        self.assertEqual(met["rootAdmission"], "NOT_ADMITTED")

    def test_round2a_space_earth_roles_do_not_flatten_to_physics(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2a-normalization-20260819.json").read_text())
        by = {s["spaceRef"]: s for s in r2["normalizedSpaces"]}
        self.assertIn("MAJOR_DOMAIN_CANDIDATE", by["norm:astronomy"]["roleClasses"])
        self.assertIn("MAJOR_DOMAIN_CANDIDATE", by["norm:earth-science"]["roleClasses"])
        self.assertIn("MAJOR_SUBSPACE", by["norm:cosmology"]["roleClasses"])
        self.assertNotIn("MAJOR_DOMAIN_CANDIDATE", by["norm:cosmology"]["roleClasses"])
        self.assertIn("BRIDGE_DOMAIN", by["norm:climate-science"]["roleClasses"])

    def test_round2a_relations_reference_existing_normalized_spaces(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2a-normalization-20260819.json").read_text())
        refs = {s["spaceRef"] for s in r2["normalizedSpaces"]}
        for rel in r2["relations"]:
            self.assertIn(rel["from"], refs)
            self.assertIn(rel["to"], refs)


    def test_round2b_all_spaces_are_normalized_without_root_admission(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        self.assertEqual(r2["state"], "ROUND2B_COMPLETE_CENSUS_OPEN")
        self.assertEqual(r2["closure"], "ROUND2B_COMPLETE_GLOBAL_CENSUS_OPEN")
        self.assertTrue(all(x["identityStatus"] == "PROVISIONALLY_NORMALIZED" for x in r2["normalizedSpaces"]))
        self.assertTrue(all(x["rootAdmission"] == "NOT_ADMITTED" for x in r2["normalizedSpaces"]))

    def test_round2b_materials_is_interdisciplinary_bridge_not_single_parent(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r2["normalizedSpaces"]}
        m = by["norm:materials"]
        self.assertIn("BRIDGE_DOMAIN", m["roleClasses"])
        for d in ("physics", "chemistry", "biology", "engineering"):
            self.assertIn(d, m["placements"])
        self.assertGreaterEqual(len(m["placements"]), 4)

    def test_round2b_biology_preserves_scale_process_system_axes(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r2["normalizedSpaces"]}
        self.assertIn("MULTISCALE_LIFE_DOMAIN", by["norm:biology"]["roleClasses"])
        self.assertIn("LOWER_SCALE_LIFE_DOMAIN", by["norm:molecular-cellular-biology"]["roleClasses"])
        self.assertIn("SYSTEM_DOMAIN", by["norm:organismal-biology"]["roleClasses"])
        self.assertIn("PROCESS_AXIS", by["norm:evolutionary-biology"]["roleClasses"])
        self.assertIn("SYSTEM_DOMAIN", by["norm:ecology"]["roleClasses"])
        self.assertEqual(by["norm:biological-research-infrastructure"]["roleClasses"], ["EPISTEMIC_INFRASTRUCTURE"])

    def test_round2b_engineering_is_intervention_domain_with_crosscutting_methods(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r2["normalizedSpaces"]}
        eng = by["norm:engineering"]
        self.assertIn("INTERVENTION_DOMAIN_CANDIDATE", eng["roleClasses"])
        self.assertNotIn("FOUNDATIONAL_DOMAIN_CANDIDATE", eng["roleClasses"])
        self.assertIn("METHODOLOGICAL_AXIS", by["norm:design"]["roleClasses"])
        self.assertIn("INTEGRATIVE_METHOD_AXIS", by["norm:systems-engineering"]["roleClasses"])
        self.assertIn("REALIZATION_DOMAIN", by["norm:manufacturing"]["roleClasses"])

    def test_round2b_philosophy_and_history_remain_distinct_epistemic_domains(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r2["normalizedSpaces"]}
        self.assertIn("FOUNDATIONAL_CONCEPTUAL_DOMAIN_CANDIDATE", by["norm:philosophy"]["roleClasses"])
        self.assertIn("HISTORICAL_INTERPRETIVE_DOMAIN_CANDIDATE", by["norm:history"]["roleClasses"])
        self.assertNotEqual(by["norm:philosophy"]["roleClasses"], by["norm:history"]["roleClasses"])
        self.assertIn("COMPOSITE_HISTORICAL_SYMBOLIC_DOMAIN", by["norm:classics"]["roleClasses"])
        self.assertIn("CONCEPTUAL_ART_BRIDGE", by["norm:aesthetics"]["roleClasses"])

    def test_round2b_biomedical_and_agricultural_boundaries_do_not_wholesale_foundationalize(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r2["normalizedSpaces"]}
        self.assertIn("FOUNDATIONAL_BRIDGE", by["norm:basic-biomedical-science"]["roleClasses"])
        self.assertIn("APPLIED_PROFESSIONAL_DOMAIN", by["norm:medicine-health"]["roleClasses"])
        self.assertNotIn("FOUNDATIONAL_DOMAIN_CANDIDATE", by["norm:medicine-health"]["roleClasses"])
        self.assertIn("APPLIED_INTERVENTION_SYSTEM_DOMAIN", by["norm:agriculture"]["roleClasses"])
        self.assertIn("BRIDGE_DOMAIN", by["norm:soil-science"]["roleClasses"])

    def test_round2b_negative_controls_reject_administrative_taxonomy_as_ontology(self) -> None:
        r2 = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        claims = " | ".join(x["claim"] for x in r2["negativeFindings"])
        self.assertIn("Emerging Frontiers", claims)
        self.assertIn("NIH institute boundaries", claims)
        self.assertIn("accreditation", claims)
        self.assertIn("Composite humanities fields", claims)

    def test_round2b_relations_resolve_against_round2a_plus_round2b_identities(self) -> None:
        r2a = json.loads((ROOT / "reference/foundational-census-round2a-normalization-20260819.json").read_text())
        r2b = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r2a["normalizedSpaces"] + r2b["normalizedSpaces"]}
        for rel in r2b["relations"]:
            self.assertIn(rel["from"], refs, rel)
            self.assertIn(rel["to"], refs, rel)


    def test_whole_audit_grammar_repair_covers_all_observed_round2ab_roles(self) -> None:
        audit = json.loads((ROOT / "reference/foundational-whole-topology-audit-20260819.json").read_text())
        self.assertEqual(audit["unknownRoleClasses"], [])
        self.assertTrue(audit.get("repairs"))
        self.assertEqual(audit["repairs"][-1]["status"], "APPLIED")

    def test_round2c_residual_normalization_keeps_roots_closed(self) -> None:
        r2c = json.loads((ROOT / "reference/foundational-census-round2c-residual-normalization-20260819.json").read_text())
        self.assertEqual(r2c["state"], "ROUND2C_COMPLETE_CENSUS_OPEN")
        self.assertTrue(all(x["rootAdmission"] == "NOT_ADMITTED" for x in r2c["normalizedSpaces"]))
        self.assertEqual(len(r2c["repairs"]), 4)

    def test_round2c_splits_probability_from_statistics(self) -> None:
        r2c = json.loads((ROOT / "reference/foundational-census-round2c-residual-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r2c["normalizedSpaces"]}
        self.assertIn("norm:probability", by)
        self.assertIn("norm:statistics", by)
        self.assertNotEqual(by["norm:probability"]["roleClasses"], by["norm:statistics"]["roleClasses"])
        self.assertIn("INFERENTIAL_METHOD_AXIS", by["norm:statistics"]["roleClasses"])

    def test_round2c_splits_dynamics_systems_control_and_systems_engineering(self) -> None:
        r2a = json.loads((ROOT / "reference/foundational-census-round2a-normalization-20260819.json").read_text())
        r2b = json.loads((ROOT / "reference/foundational-census-round2b-normalization-20260819.json").read_text())
        r2c = json.loads((ROOT / "reference/foundational-census-round2c-residual-normalization-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r2a["normalizedSpaces"] + r2b["normalizedSpaces"] + r2c["normalizedSpaces"]}
        for ref in ("norm:dynamical-systems", "norm:systems-theory-control", "norm:systems-engineering"):
            self.assertIn(ref, refs)
        self.assertEqual(len({"norm:dynamical-systems", "norm:systems-theory-control", "norm:systems-engineering"}), 3)

    def test_round2c_splits_genetics_and_genomics(self) -> None:
        r2c = json.loads((ROOT / "reference/foundational-census-round2c-residual-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r2c["normalizedSpaces"]}
        self.assertIn("INHERITANCE_PROCESS_DOMAIN", by["norm:genetics"]["roleClasses"])
        self.assertIn("DATA_INTENSIVE_LIFE_DOMAIN", by["norm:genomics"]["roleClasses"])
        self.assertIn("computation", by["norm:genomics"]["placements"])

    def test_round2c_splits_information_science_from_librarianship(self) -> None:
        r2c = json.loads((ROOT / "reference/foundational-census-round2c-residual-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r2c["normalizedSpaces"]}
        self.assertIn("MAJOR_DOMAIN_CANDIDATE", by["norm:information-science"]["roleClasses"])
        self.assertIn("APPLIED_PROFESSIONAL_DOMAIN", by["norm:librarianship"]["roleClasses"])
        self.assertIn("EPISTEMIC_INFRASTRUCTURE", by["norm:librarianship"]["roleClasses"])

    def test_round2c_relations_resolve_across_all_round2_identities(self) -> None:
        rounds = [json.loads((ROOT / name).read_text()) for name in (
            "reference/foundational-census-round2a-normalization-20260819.json",
            "reference/foundational-census-round2b-normalization-20260819.json",
            "reference/foundational-census-round2c-residual-normalization-20260819.json",
        )]
        refs = {x["spaceRef"] for r in rounds for x in r["normalizedSpaces"]}
        for rel in rounds[2]["relations"]:
            self.assertIn(rel["from"], refs, rel)
            self.assertIn(rel["to"], refs, rel)


    def test_whole_audit_v2_closes_high_value_normalization_but_not_breadth(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v2-20260819.json").read_text())
        self.assertEqual(a["state"], "CORE_NORMALIZATION_COMPLETE_BREADTH_CENSUS_OPEN")
        self.assertEqual(a["counts"]["round1HighValueUnresolved"], 0)
        self.assertGreater(a["counts"]["broadBreadthResidual"], 0)
        self.assertEqual(a["counts"]["canonicalRootAdmissions"], 0)
        self.assertEqual(a["coverageCrosswalkReadiness"], "NOT_READY")

    def test_whole_audit_v2_rejects_single_root_tree_and_uses_major_regions(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v2-20260819.json").read_text())
        nav = a["navigationModel"]
        self.assertEqual(nav["singleRootTree"], "REJECTED")
        self.assertEqual(nav["preferredAnchorTerm"], "CANONICAL_MAJOR_REGION")
        self.assertEqual(nav["canonicalMajorRegionAdmissions"], [])
        self.assertEqual(nav["admissionCriteriaStatus"], "DRAFT_REQUIRED_BEFORE_ADMISSION")

    def test_whole_audit_v2_topology_grammar_is_total_over_all_current_roles(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v2-20260819.json").read_text())
        grammar = a["topologyGrammar"]
        self.assertEqual(grammar["status"], "SUPPORTED_AND_TOTAL_OVER_CURRENT_ROLES")
        self.assertEqual(set(grammar["archetypes"]), {"DOMAIN", "MAJOR_SUBSPACE", "BRIDGE", "AXIS", "INFRASTRUCTURE", "APPLIED_TRANSLATIONAL", "COMPOSITE"})
        observed = {role for x in a["spaceArchetypes"] for role in x["roleClasses"]}
        self.assertEqual(observed, set(grammar["roleToArchetype"]))
        self.assertTrue(all(x["archetypes"] for x in a["spaceArchetypes"]))

    def test_whole_audit_v2_has_no_identity_or_relation_integrity_defects(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v2-20260819.json").read_text())
        self.assertEqual(a["identityCollisions"], {})
        self.assertEqual(a["brokenRelations"], [])
        self.assertEqual(a["counts"]["identityLabelCollisions"], 0)
        self.assertEqual(a["counts"]["brokenRelations"], 0)

    def test_whole_audit_v2_preserves_material_breadth_residuals(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v2-20260819.json").read_text())
        residual = {x["candidate"] for x in a["breadthResidualCandidates"]}
        for expected in ("Planetary science", "Biochemistry", "Microbiology", "Developmental biology", "Physiology", "Philosophy of mind and cognition", "Software engineering", "Philology", "Food science"):
            self.assertIn(expected, residual)
        self.assertEqual(a["canonicalMajorRegionReadiness"], "NOT_READY_BREADTH_RESIDUALS_AND_CRITERIA_PENDING")



if __name__ == "__main__":
    unittest.main()
