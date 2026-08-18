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


    def test_ordivon_internal_lenses_cannot_mint_external_reference_truth(self) -> None:
        lenses = json.loads((ROOT / "reference/ordivon-theory-lenses-for-reference-cartography-20260819.json").read_text())
        self.assertEqual(lenses["truthRole"], "INTERNAL_ANALYTIC_LENS_NOT_EXTERNAL_EVIDENCE")
        self.assertIn("MUST NOT", lenses["rule"])
        self.assertIn("INTERNAL_ORDIVON_THEORY != EXTERNAL_EVIDENCE", lenses["derivedControls"])
        self.assertGreaterEqual(len(lenses["lenses"]), 6)

    def test_round3a_closes_bounded_breadth_residual_set_without_world_closure(self) -> None:
        r3 = json.loads((ROOT / "reference/foundational-census-round3a-breadth-normalization-20260819.json").read_text())
        self.assertEqual(r3["state"], "ROUND3A_COMPLETE_BREADTH_RESIDUAL_SET_ZERO_FOR_V0_CENSUS")
        self.assertEqual(len(r3["normalizedSpaces"]), 17)
        self.assertTrue(all(x["rootAdmission"] == "NOT_ADMITTED" for x in r3["normalizedSpaces"]))
        self.assertIn("OPEN_WORLD", r3["closure"])

    def test_round3a_engineering_residuals_are_explicit_but_subordinate(self) -> None:
        r3 = json.loads((ROOT / "reference/foundational-census-round3a-breadth-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r3["normalizedSpaces"]}
        refs = [
            "norm:mechanical-engineering", "norm:electrical-electronic-engineering", "norm:civil-structural-engineering",
            "norm:chemical-engineering", "norm:computer-engineering", "norm:software-engineering", "norm:control-engineering",
            "norm:environmental-engineering", "norm:energy-engineering"
        ]
        for ref in refs:
            self.assertIn(ref, by)
            self.assertEqual(by[ref]["rootAdmission"], "NOT_ADMITTED")
            self.assertTrue(any("ENGINEERING" in role or "INTERVENTION" in role or "REALIZATION" in role or "CONTROL" in role for role in by[ref]["roleClasses"]), ref)

    def test_round3a_residuals_preserve_process_bridge_and_composite_roles(self) -> None:
        r3 = json.loads((ROOT / "reference/foundational-census-round3a-breadth-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r3["normalizedSpaces"]}
        self.assertIn("BRIDGE_DOMAIN", by["norm:biochemistry"]["roleClasses"])
        self.assertIn("PROCESS_AXIS", by["norm:developmental-biology"]["roleClasses"])
        self.assertIn("FUNCTION_AXIS", by["norm:physiology"]["roleClasses"])
        self.assertIn("CONCEPTUAL_BRIDGE", by["norm:philosophy-of-mind"]["roleClasses"])
        self.assertIn("TEXTUAL_METHOD_AXIS", by["norm:philology"]["roleClasses"])
        self.assertIn("COMPOSITE_DOMAIN", by["norm:food-science"]["roleClasses"])

    def test_round3b_major_region_is_projection_not_reference_identity(self) -> None:
        c = json.loads((ROOT / "reference/canonical-major-region-projection-contract-v0-20260819.json").read_text())
        distinction = c["coreDistinction"]
        self.assertIn("CANONICAL_MAJOR_REGION != REFERENCE_IDENTITY", distinction["law"])
        self.assertEqual(c["truthRole"], "NON_AUTHORITATIVE_NAVIGATION_PROJECTION_CONTRACT")
        self.assertEqual(c["externalReferenceTruthRole"], "NONE")
        self.assertEqual(c["admissionState"], "CONTRACT_DRAFT_SUPPORTED_NO_REGIONS_ADMITTED")

    def test_round3b_major_region_contract_forbids_institutional_and_graph_self_admission(self) -> None:
        c = json.loads((ROOT / "reference/canonical-major-region-projection-contract-v0-20260819.json").read_text())
        negative = " | ".join(c["negativeCriteria"])
        for phrase in ("university department", "Professional society", "publication volume", "Graph degree", "deep, useful"):
            self.assertIn(phrase, negative)
        gates = {g["gate"] for g in c["admissionGates"]}
        self.assertEqual(gates, {"G1_REFERENCE_SUPPORT", "G2_NAVIGATION_DELETION_HARM", "G3_SCOPE_COHERENCE", "G4_TOPOLOGY_PRESERVATION", "G5_NON_AUTHORITY", "G6_OPEN_WORLD", "G7_STABILITY"})

    def test_round3b_dogfood_admits_only_multi_identity_navigation_projections_after_bounded_tests(self) -> None:
        d = json.loads((ROOT / "reference/canonical-major-region-admission-dogfood-20260819.json").read_text())
        self.assertEqual(d["state"], "BOUNDED_NAVIGATION_AND_PERTURBATION_DOGFOOD_COMPLETE")
        self.assertEqual(len(d["admittedRegions"]), 6)
        self.assertEqual(d["deferredRegions"], ["candidate-region:historical-symbolic"])
        self.assertEqual(len(d["rejectedOrNotAdmitted"]), 6)
        by = {x["candidateRef"]: x for x in d["results"]}
        for ref in d["admittedRegions"]:
            self.assertEqual(by[ref]["admission"], "ADMITTED_NAVIGATION_PROJECTION_V0")
            self.assertEqual(by[ref]["gateResults"]["G2_NAVIGATION_DELETION_HARM"], "PASS_BOUNDED_FIXTURES")
            self.assertEqual(by[ref]["gateResults"]["G7_STABILITY"], "PASS_BOUNDED_PERTURBATION")
        self.assertEqual(by["candidate-region:historical-symbolic"]["admission"], "DEFERRED")
        for ref in d["rejectedOrNotAdmitted"]:
            self.assertEqual(by[ref]["admission"], "REJECTED_OR_NOT_ADMITTED")

    def test_major_region_projection_set_is_non_authoritative_nonexclusive_and_open_world(self) -> None:
        pset = json.loads((ROOT / "reference/canonical-major-regions-v0-20260819.json").read_text())
        self.assertEqual(pset["truthRole"], "NON_AUTHORITATIVE_NAVIGATION_PROJECTION")
        self.assertTrue(pset["openWorld"])
        self.assertEqual(pset["closureClaim"], "NONE")
        self.assertEqual(pset["coverageCrosswalk"], "NOT_STARTED")
        self.assertEqual(len(pset["regions"]), 6)
        for region in pset["regions"]:
            self.assertEqual(region["kind"], "CANONICAL_MAJOR_REGION_PROJECTION")
            self.assertEqual(region["membershipSemantics"], "NON_EXCLUSIVE")
            self.assertEqual(region["closureClaim"], "NONE")
            self.assertGreaterEqual(len(region["memberRefs"]), 5)
            self.assertEqual(len(region["anchorRefs"]), 3)

    def test_major_region_navigation_fixtures_show_bounded_deletion_harm(self) -> None:
        d = json.loads((ROOT / "reference/canonical-major-region-admission-dogfood-20260819.json").read_text())
        self.assertGreaterEqual(len(d["navigationFixtures"]), 10)
        for f in d["navigationFixtures"]:
            self.assertEqual(f["result"], "PASS")
            self.assertGreaterEqual(f["deletionCostIncrease"], 2)

    def test_historical_symbolic_region_is_deferred_for_later_social_cultural_boundary(self) -> None:
        pset = json.loads((ROOT / "reference/canonical-major-regions-v0-20260819.json").read_text())
        self.assertEqual(len(pset["deferred"]), 1)
        self.assertIn("social/cultural", pset["deferred"][0]["reason"])
        labels = {r["label"] for r in pset["regions"]}
        self.assertNotIn("Historical, Linguistic & Interpretive", labels)

    def test_round3a_relations_resolve_across_all_normalized_rounds(self) -> None:
        paths = [
            "reference/foundational-census-round2a-normalization-20260819.json",
            "reference/foundational-census-round2b-normalization-20260819.json",
            "reference/foundational-census-round2c-residual-normalization-20260819.json",
            "reference/foundational-census-round3a-breadth-normalization-20260819.json",
        ]
        rounds = [json.loads((ROOT / p).read_text()) for p in paths]
        refs = {x["spaceRef"] for r in rounds for x in r["normalizedSpaces"]}
        for rel in rounds[-1]["relations"]:
            self.assertIn(rel["from"], refs, rel)
            self.assertIn(rel["to"], refs, rel)


    def test_whole_audit_v3_closes_bounded_v0_residual_not_open_world_census(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v3-20260819.json").read_text())
        self.assertEqual(a["state"], "V0_BOUNDED_BREADTH_NORMALIZED_OPEN_WORLD_CENSUS_CONTINUES")
        self.assertEqual(a["counts"]["v0BreadthResidual"], 0)
        self.assertEqual(a["censusSemantics"]["openWorldCensusStatus"], "OPEN_NOT_EXHAUSTIVE")
        self.assertIn("!=", a["censusSemantics"]["law"])

    def test_whole_audit_v3_graph_integrity_and_major_region_projection_counts(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v3-20260819.json").read_text())
        self.assertEqual(a["counts"]["normalizedSpaces"], 71)
        self.assertEqual(a["counts"]["relations"], 74)
        self.assertEqual(a["counts"]["identityLabelCollisions"], 0)
        self.assertEqual(a["counts"]["brokenRelations"], 0)
        self.assertEqual(a["counts"]["canonicalMajorRegionProjections"], 6)
        self.assertEqual(a["counts"]["deferredMajorRegionCandidates"], 1)

    def test_whole_audit_v3_keeps_internal_lenses_and_major_regions_non_authoritative(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v3-20260819.json").read_text())
        self.assertEqual(a["ordivonTheoryUse"]["status"], "ADMITTED_AS_INTERNAL_ANALYTIC_LENSES_ONLY")
        self.assertIn("cannot count as external", a["ordivonTheoryUse"]["firewall"])
        self.assertIn("CANONICAL_MAJOR_REGION != REFERENCE_IDENTITY", a["majorRegionProjection"]["law"])
        self.assertEqual(a["majorRegionProjection"]["closureClaim"], "NONE")
        self.assertEqual(a["majorRegionProjection"]["membershipSemantics"], "NON_EXCLUSIVE")

    def test_whole_audit_v3_only_enables_bounded_crosswalk_pilot(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v3-20260819.json").read_text())
        self.assertEqual(a["coverageCrosswalkReadiness"], "READY_FOR_BOUNDED_PILOT_NOT_GLOBAL_COVERAGE_SCORE")
        self.assertIn("do not publish scalar global coverage percentages", a["next"])


    def test_crosswalk_contract_forbids_scalar_and_region_coverage_truth(self) -> None:
        c = json.loads((ROOT / "reference/coverage-crosswalk-contract-v0-20260819.json").read_text())
        self.assertIn("NO_GLOBAL_SCALAR_COVERAGE_PERCENT", c["laws"])
        self.assertIn("REGION_VIEW != COVERAGE_TRUTH", c["laws"])
        self.assertIn("REGION_MEMBER_COVERAGE DOES NOT TRANSFER TO REGION", c["laws"])
        self.assertIn("MUST NOT be averaged", c["dimensionRule"])

    def test_crosswalk_owner_snapshot_is_source_fenced_and_excludes_unpublished_owners(self) -> None:
        s = json.loads((ROOT / "reference/coverage-crosswalk-owner-authority-snapshot-20260819.json").read_text())
        self.assertEqual(len(s["owners"]), 7)
        self.assertEqual(s["atlasSource"]["mainRevision"], "e5c9c2b4c09f6f906496fdcf31d01747398e16db")
        self.assertIn("fullyCurrent=true", s["atlasSource"]["refreshResult"])
        for o in s["owners"]:
            self.assertTrue(o["authorityVersionRef"].startswith("sha256:"))
            self.assertTrue(o["sourceTransportRevision"])
            self.assertTrue(o["recoveryDigest"].startswith("sha256:"))
        excluded = {x["owner"] for x in s["excludedCurrentnessCases"]}
        for name in ("Semantics of Computational Descriptions", "Human", "Finance", "Media", "Harness"):
            self.assertIn(name, excluded)

    def test_crosswalk_v02_uses_identity_level_mappings_only(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-2-20260819.json").read_text())
        self.assertEqual(p["globalScalarCoverage"], "FORBIDDEN")
        self.assertEqual(len(p["mappings"]), 9)
        for v in p["regionCoverageViews"]:
            self.assertEqual(v["aggregateCoverageTruth"], "FORBIDDEN")
            self.assertIn("no region coverage truth", v["note"])

    def test_crosswalk_v02_network_maps_to_networking_not_information_theory(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-2-20260819.json").read_text())
        by = {x["mappingRef"]: x for x in p["mappings"]}
        n = by["crosswalk:network->networking-communication"]
        self.assertEqual(n["externalRef"], "norm:networking-communication")
        self.assertEqual(n["relation"], "DIRECT_PARTIAL_COVERAGE")
        cases = " | ".join(x["case"] for x in p["nonCoverageCases"])
        self.assertIn("does not count as Information Theory coverage", cases)

    def test_crosswalk_v02_runtime_bridge_does_not_wholesale_cover_os(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-2-20260819.json").read_text())
        by = {x["mappingRef"]: x for x in p["mappings"]}
        self.assertEqual(by["crosswalk:runtime->systems-fundamentals"]["relation"], "BRIDGE_COVERAGE")
        self.assertEqual(by["crosswalk:runtime->operating-systems"]["relation"], "BRIDGE_COVERAGE")
        self.assertIn("does not count as whole-field", " | ".join(x["case"] for x in p["nonCoverageCases"]))

    def test_crosswalk_v02_philosophy_navigation_false_positive_is_repaired(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-2-20260819.json").read_text())
        by = {x["regionRef"]: x for x in nav["regions"]}
        self.assertIn("navigation-region:philosophical-conceptual", by)
        self.assertNotIn("norm:philosophy", by["navigation-region:mind-language"]["memberRefs"])
        self.assertIn("norm:philosophy-of-mind", by["navigation-region:mind-language"]["memberRefs"])
        self.assertIn("norm:philosophy-of-mind", by["navigation-region:philosophical-conceptual"]["memberRefs"])

    def test_round4a_computing_systems_gap_is_externally_repaired(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round4a-crosswalk-induced-repair-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        for ref in ("norm:networking-communication", "norm:operating-systems", "norm:parallel-distributed-computing", "norm:systems-fundamentals", "norm:foundations-programming-languages"):
            self.assertIn(ref, refs)
        self.assertIn("OWNER_THEORY_DOES_NOT_MINT_THE_REPAIR", r["laws"])
        self.assertIn("EXTERNAL_SOURCE_VERIFICATION_REQUIRED_BEFORE_REFERENCE_REPAIR", r["laws"])

    def test_round4a_philosophy_is_normalized_beyond_mind(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round4a-crosswalk-induced-repair-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        for ref in ("norm:metaphysics", "norm:epistemology", "norm:ethics-value-theory", "norm:philosophy-of-science", "norm:philosophy-of-language"):
            self.assertIn(ref, refs)

    def test_major_regions_v02_split_formal_from_computer_systems(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-2-20260819.json").read_text())
        by = {x["regionRef"]: x for x in nav["regions"]}
        self.assertEqual(len(nav["regions"]), 8)
        self.assertIn("navigation-region:formal-inferential", by)
        self.assertIn("navigation-region:computation-computer-systems", by)
        self.assertIn("norm:networking-communication", by["navigation-region:computation-computer-systems"]["memberRefs"])
        self.assertIn("norm:operating-systems", by["navigation-region:computation-computer-systems"]["memberRefs"])
        self.assertEqual(nav["coverageCrosswalk"], "IDENTITY_LEVEL_ONLY")

    def test_major_regions_v02_repair_dogfood_passes_all_controls(self) -> None:
        d = json.loads((ROOT / "reference/canonical-major-regions-v0-2-dogfood-20260819.json").read_text())
        self.assertEqual(d["state"], "PASS")
        self.assertTrue(all(d["destructiveControls"].values()))
        self.assertTrue(all(x["result"] == "PASS" for x in d["regionResults"]))

    def test_whole_audit_v4_has_integrity_and_host_mapping_weak_without_novelty_claim(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v4-crosswalk-repair-20260819.json").read_text())
        self.assertEqual(a["counts"]["normalizedSpaces"], 81)
        self.assertEqual(a["counts"]["relations"], 92)
        self.assertEqual(a["counts"]["canonicalMajorRegionProjections"], 8)
        self.assertEqual(a["counts"]["identityLabelCollisions"], 0)
        self.assertEqual(a["counts"]["brokenRelations"], 0)
        self.assertEqual(a["counts"]["unresolvedReferenceOrNoveltyAmbiguities"], 0)
        self.assertEqual(a["counts"]["externalMappingWeakNoveltyNotEstablished"], 1)
        self.assertEqual(a["globalScalarCoverage"], "FORBIDDEN")
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-2-20260819.json").read_text())
        host = next(x for x in p["gapDispositions"] if x["gapRef"] == "gap:coordination-workflow-systems")
        self.assertEqual(host["currentStatus"], "EXTERNAL_MAPPING_WEAK_NOVELTY_NOT_ESTABLISHED")


    def test_crosswalk_v03_owner_snapshot_is_eight_owner_and_scd_source_fenced(self) -> None:
        snap = json.loads((ROOT / "reference/coverage-crosswalk-owner-authority-snapshot-v0-3-20260819.json").read_text())
        self.assertEqual(snap["atlasSource"]["mainRevision"], "c6fc241baee0b259c12d96064d00fb9eb1892b42")
        self.assertEqual(len(snap["owners"]), 8)
        by = {x["ownerResearchRef"]: x for x in snap["owners"]}
        scd = by["research-owner:semantics-of-computational-descriptions"]
        cp = by["research-owner:computational-possibility"]
        self.assertEqual(scd["authorityVersionRef"], "sha256:3319f37f081908e545c708f79e489c3b2a1c54cb03453fa2ebe32bc6e72cbd4f")
        self.assertEqual(scd["sourceTransportRevision"], "a35ee399fa0cf3dd24869d50f78ca05850ece0c4")
        self.assertEqual(scd["projectionCurrentness"], "CURRENT_TO_SOURCE")
        self.assertNotEqual(scd["authorityVersionRef"], cp["authorityVersionRef"])
        self.assertNotEqual(scd["sourceTransportRevision"], cp["sourceTransportRevision"])
        excluded = {x["owner"] for x in snap["excludedCurrentnessCases"]}
        self.assertNotIn("Semantics of Computational Descriptions", excluded)
        self.assertEqual(excluded, {"Human", "Finance", "Media", "Harness"})

    def test_round4b_repairs_formal_semantics_and_formal_methods_from_external_sources(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round4b-scd-crosswalk-repair-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        self.assertEqual(set(by), {"norm:formal-semantics", "norm:formal-methods"})
        for x in by.values():
            self.assertEqual(x["rootAdmission"], "NOT_ADMITTED")
            self.assertGreaterEqual(len(x["evidence"]), 3)
            self.assertGreaterEqual(len(x["placements"]), 5)
        self.assertIn("SEMANTIC_MODELING_AXIS", by["norm:formal-semantics"]["roleClasses"])
        self.assertIn("SPECIFICATION_VERIFICATION_AXIS", by["norm:formal-methods"]["roleClasses"])
        self.assertIn("SCD_PRESSURE_MAY_TRIGGER_SEARCH_NOT_IDENTITY", r["laws"])
        self.assertIn("MATURE_THEORY_SUBTRACTION_REDUCES_NOVELTY_PRESSURE", r["laws"])

    def test_round4b_does_not_mint_scd_named_external_identity(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round4b-scd-crosswalk-repair-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        self.assertFalse(any("scd" in ref or "ordivon" in ref for ref in refs))
        labels = " ".join(x["label"].lower() for x in r["normalizedSpaces"])
        self.assertNotIn("ordivon", labels)

    def test_crosswalk_v03_scd_is_multi_theory_bridge_not_whole_field_owner(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-3-20260819.json").read_text())
        self.assertEqual(p["globalScalarCoverage"], "FORBIDDEN")
        self.assertEqual(len(p["mappings"]), 11)
        self.assertEqual(p["scdDisposition"]["standing"], "EXTERNAL_MULTI_THEORY_BRIDGE_MAPPED_NOVELTY_NOT_ESTABLISHED")
        self.assertEqual(p["scdDisposition"]["directFieldEquivalence"], "NOT_CLAIMED")
        by = {x["mappingRef"]: x for x in p["mappings"]}
        for ref, ext in (("crosswalk:scd->formal-semantics", "norm:formal-semantics"), ("crosswalk:scd->formal-methods", "norm:formal-methods")):
            self.assertIn(ref, by)
            self.assertEqual(by[ref]["externalRef"], ext)
            self.assertEqual(by[ref]["relation"], "BRIDGE_COVERAGE")
            self.assertIn("FALSIFICATION_TESTED", by[ref]["facets"])

    def test_crosswalk_v03_scd_negative_gap_closeout_reduces_novelty_not_external_theory(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-3-20260819.json").read_text())
        self.assertIn("G1-G4", p["scdDisposition"]["negativeNoveltyEvidence"])
        self.assertIn("rejected", p["scdDisposition"]["negativeNoveltyEvidence"])
        cases = " | ".join(x["case"] + " :: " + x["reason"] for x in p["nonCoverageCases"])
        self.assertIn("G1-G4 negative formal-gap closeout", cases)
        self.assertIn("does not imply SCD has covered or falsified", cases)

    def test_crosswalk_v03_region_views_never_aggregate_scd_bridge_coverage(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-3-20260819.json").read_text())
        for view in p["regionCoverageViews"]:
            self.assertEqual(view["aggregateCoverageTruth"], "FORBIDDEN")
        formal = next(x for x in p["regionCoverageViews"] if x["regionRef"] == "navigation-region:formal-inferential")
        computing = next(x for x in p["regionCoverageViews"] if x["regionRef"] == "navigation-region:computation-computer-systems")
        formal_refs = {x["externalRef"] for x in formal["mappedMemberRefs"]}
        computing_refs = {x["externalRef"] for x in computing["mappedMemberRefs"]}
        self.assertIn("norm:formal-semantics", formal_refs & computing_refs)
        self.assertIn("norm:formal-methods", formal_refs & computing_refs)

    def test_major_regions_v03_keep_crosscutting_semantics_and_methods_non_anchor(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-3-20260819.json").read_text())
        self.assertEqual(len(nav["regions"]), 8)
        self.assertEqual(nav["coverageCrosswalk"], "IDENTITY_LEVEL_ONLY")
        by = {x["regionRef"]: x for x in nav["regions"]}
        for ref in ("norm:formal-semantics", "norm:formal-methods"):
            self.assertIn(ref, by["navigation-region:formal-inferential"]["memberRefs"])
            self.assertIn(ref, by["navigation-region:computation-computer-systems"]["memberRefs"])
            self.assertNotIn(ref, by["navigation-region:formal-inferential"]["anchorRefs"])
            self.assertNotIn(ref, by["navigation-region:computation-computer-systems"]["anchorRefs"])
        self.assertIn("norm:formal-methods", by["navigation-region:engineering-design"]["memberRefs"])

    def test_major_regions_v03_scd_perturbation_dogfood_passes(self) -> None:
        d = json.loads((ROOT / "reference/canonical-major-regions-v0-3-dogfood-20260819.json").read_text())
        self.assertEqual(d["state"], "PASS")
        self.assertTrue(all(d["destructiveControls"].values()))
        self.assertTrue(all(x["result"] == "PASS" for x in d["regionResults"]))
        self.assertTrue(d["destructiveControls"]["noNewMajorRegionCreatedForSCD"])
        self.assertTrue(d["destructiveControls"]["noSCDOwnerIdentityInReferenceGraph"])

    def test_whole_audit_v5_tracks_eight_owner_scd_crosswalk_without_novelty_promotion(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v5-scd-crosswalk-20260819.json").read_text())
        self.assertEqual(a["counts"]["normalizedSpaces"], 83)
        self.assertEqual(a["counts"]["relations"], 98)
        self.assertEqual(a["counts"]["currentOwnerAuthorityInputs"], 8)
        self.assertEqual(a["counts"]["crosswalkMappings"], 11)
        self.assertEqual(a["counts"]["canonicalMajorRegionProjections"], 8)
        self.assertEqual(a["counts"]["identityLabelCollisions"], 0)
        self.assertEqual(a["counts"]["brokenRelations"], 0)
        self.assertEqual(a["counts"]["externalMultiTheoryBridgeNoveltyNotEstablished"], 1)
        self.assertEqual(a["globalScalarCoverage"], "FORBIDDEN")
        self.assertIn("MATURE_THEORY_SUBTRACTION_PRECEDES_NOVELTY", a["laws"])


    def test_crosswalk_v04_owner_snapshot_is_nine_owner_and_human_source_fenced(self) -> None:
        snap = json.loads((ROOT / "reference/coverage-crosswalk-owner-authority-snapshot-v0-4-20260819.json").read_text())
        self.assertEqual(snap["atlasSource"]["mainRevision"], "86fbb686f5a1940dd6f5765bba3b01480aef6acf")
        self.assertEqual(snap["atlasSource"]["observationResult"], "9/9 CURRENT_TO_SOURCE")
        self.assertIn("PARALLEL_PER_OWNER", snap["atlasSource"]["observationMode"])
        self.assertEqual(len(snap["owners"]), 9)
        by = {x["ownerResearchRef"]: x for x in snap["owners"]}
        h = by["research-owner:human"]
        self.assertEqual(h["authorityVersionRef"], "sha256:035eaa334ffdfe3ae44236f966176a36ffd772ee8c2e4c4454733ab9699ef392")
        self.assertEqual(h["sourceTransportRevision"], "cc966bf99458949b59c433a5f7bc8fafe3d692b7")
        self.assertEqual(h["recoveryLocator"], "research/core/HUMAN-RESEARCH-CORE.md")
        self.assertEqual((h["resultCount"], h["closureCount"], h["negativeLineageCount"]), (30, 16, 12))
        self.assertEqual({x["owner"] for x in snap["excludedCurrentnessCases"]}, {"Finance", "Media", "Harness"})

    def test_round4c_repairs_three_human_pressure_coordinates_from_external_sources(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round4c-human-crosswalk-repair-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        self.assertEqual(set(by), {"norm:consciousness-science", "norm:affective-science", "norm:developmental-science"})
        self.assertEqual(len(r["relations"]), 12)
        for row in by.values():
            self.assertEqual(row["rootAdmission"], "NOT_ADMITTED")
            self.assertGreaterEqual(len(row["evidence"]), 2)
            self.assertGreaterEqual(len(row["placements"]), 6)
        self.assertIn("SUBJECTIVE_EXPERIENCE_RESEARCH_DOMAIN", by["norm:consciousness-science"]["roleClasses"])
        self.assertIn("AFFECT_EMOTION_PROCESS_DOMAIN", by["norm:affective-science"]["roleClasses"])
        self.assertIn("HUMAN_DEVELOPMENT_DOMAIN", by["norm:developmental-science"]["roleClasses"])
        self.assertIn("MATURE_FIELD_SUBTRACTION_PRECEDES_NOVELTY", r["laws"])

    def test_round4c_does_not_mint_human_owner_architecture_as_external_ontology(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round4c-human-crosswalk-repair-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        labels = " ".join(x["label"].lower() for x in r["normalizedSpaces"])
        self.assertFalse(any("ordivon" in ref or "hf" in ref or "hoc" in ref for ref in refs))
        self.assertNotIn("ordivon human", labels)
        self.assertIn("HUMAN_FOUNDATION != EXTERNAL_DISCIPLINE", r["laws"])
        self.assertIn("HOC != SCIENTIFIC_FIELD", r["laws"])
        self.assertIn("DEEP_DOMAIN != PRIMITIVE_OR_EXTERNAL_ROOT", r["laws"])

    def test_crosswalk_v04_human_has_ten_bounded_mappings_and_no_broad_biology_medicine_claim(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-4-20260819.json").read_text())
        human = [x for x in p["mappings"] if x["ownerResearchRef"] == "research-owner:human"]
        self.assertEqual(len(human), 10)
        self.assertEqual(len(p["mappings"]), 21)
        self.assertEqual(p["humanDisposition"]["standing"], "EXTERNAL_MULTI_DOMAIN_PARTIAL_MAPPED_NOVELTY_NOT_ESTABLISHED")
        self.assertEqual(p["humanDisposition"]["directFieldEquivalence"], "NOT_CLAIMED")
        external = {x["externalRef"] for x in human}
        self.assertEqual(external, {"norm:psychology", "norm:cognitive-science", "norm:consciousness-science", "norm:affective-science", "norm:developmental-science", "norm:linguistics", "norm:neuroscience", "norm:genetics", "norm:evolutionary-biology", "norm:physiology"})
        self.assertNotIn("norm:biology", external)
        self.assertNotIn("norm:medicine-health", external)
        by = {x["externalRef"]: x for x in human}
        for ref in ("norm:psychology", "norm:consciousness-science", "norm:affective-science"):
            self.assertEqual(by[ref]["relation"], "DIRECT_PARTIAL_COVERAGE")
        for ref in external - {"norm:psychology", "norm:consciousness-science", "norm:affective-science"}:
            self.assertEqual(by[ref]["relation"], "BRIDGE_COVERAGE")

    def test_crosswalk_v04_preserves_human_normative_and_operational_noncoverage(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-4-20260819.json").read_text())
        cases = " | ".join(x["case"] + " :: " + x["reason"] for x in p["nonCoverageCases"])
        self.assertIn("HF14-HF18", cases)
        self.assertIn("Ordivon Normative", cases)
        self.assertIn("HOC0-HOC10", cases)
        self.assertIn("No Human Science or Ordivon Human external identity", cases)
        self.assertIn("HD7/HD8/HD9 bridge mappings do not amount to Biology or Medicine coverage", cases)

    def test_major_regions_v04_keep_human_pressure_identities_nonanchor_and_no_new_region(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-4-20260819.json").read_text())
        self.assertEqual(len(nav["regions"]), 8)
        by = {x["regionRef"]: x for x in nav["regions"]}
        mind = by["navigation-region:mind-language"]
        life = by["navigation-region:life"]
        for ref in ("norm:consciousness-science", "norm:affective-science", "norm:developmental-science"):
            self.assertIn(ref, mind["memberRefs"])
            self.assertNotIn(ref, mind["anchorRefs"])
        self.assertIn("norm:developmental-science", life["memberRefs"])
        self.assertNotIn("norm:developmental-science", life["anchorRefs"])
        self.assertNotIn("norm:consciousness-science", life["memberRefs"])
        self.assertNotIn("norm:affective-science", life["memberRefs"])

    def test_major_regions_v04_human_perturbation_dogfood_passes(self) -> None:
        d = json.loads((ROOT / "reference/canonical-major-regions-v0-4-dogfood-20260819.json").read_text())
        self.assertEqual(d["state"], "PASS")
        self.assertTrue(all(d["destructiveControls"].values()))
        self.assertTrue(all(x["result"] == "PASS" for x in d["regionResults"]))
        self.assertTrue(d["destructiveControls"]["noNewMajorRegionCreatedForHuman"])
        self.assertTrue(d["destructiveControls"]["noHumanOwnerIdentityInReferenceGraph"])
        self.assertTrue(d["destructiveControls"]["developmentCrossesMindAndLife"])

    def test_crosswalk_v04_dense_human_mind_life_mapping_never_becomes_region_truth(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-4-20260819.json").read_text())
        self.assertEqual(p["globalScalarCoverage"], "FORBIDDEN")
        for view in p["regionCoverageViews"]:
            self.assertEqual(view["aggregateCoverageTruth"], "FORBIDDEN")
        mind = next(x for x in p["regionCoverageViews"] if x["regionRef"] == "navigation-region:mind-language")
        life = next(x for x in p["regionCoverageViews"] if x["regionRef"] == "navigation-region:life")
        self.assertGreaterEqual(len(mind["mappedMemberRefs"]), 7)
        self.assertGreaterEqual(len(life["mappedMemberRefs"]), 4)

    def test_whole_audit_v6_tracks_human_crosswalk_without_integrity_or_novelty_promotion(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v6-human-crosswalk-20260819.json").read_text())
        self.assertEqual(a["counts"]["normalizedSpaces"], 86)
        self.assertEqual(a["counts"]["relations"], 110)
        self.assertEqual(a["counts"]["multiPlacementSpaces"], 83)
        self.assertEqual(a["counts"]["multiRoleSpaces"], 83)
        self.assertEqual(a["counts"]["currentOwnerAuthorityInputs"], 9)
        self.assertEqual(a["counts"]["crosswalkMappings"], 21)
        self.assertEqual(a["counts"]["humanMappings"], 10)
        self.assertEqual(a["counts"]["canonicalMajorRegionProjections"], 8)
        self.assertEqual(a["counts"]["identityLabelCollisions"], 0)
        self.assertEqual(a["counts"]["brokenRelations"], 0)
        self.assertEqual(a["globalScalarCoverage"], "FORBIDDEN")
        self.assertIn("MATURE_KNOWLEDGE_SUBTRACTION_PRECEDES_NOVELTY", a["laws"])

    def test_open_resource_subtraction_pattern_is_heterogeneously_replicated_not_constitutional(self) -> None:
        m = json.loads((ROOT / "reference/open-resource-mature-knowledge-subtraction-pattern-v0-2-20260819.json").read_text())
        self.assertEqual(m["state"], "REPLICATED_ACROSS_TWO_HETEROGENEOUS_OWNERS_NOT_CONSTITUTIONAL")
        self.assertEqual({x["owner"] for x in m["witnesses"]}, {"research-owner:semantics-of-computational-descriptions", "research-owner:human"})
        modes = {x["mode"] for x in m["witnesses"]}
        self.assertIn("MATURE_FORMAL_THEORY_SUBTRACTION", modes)
        self.assertIn("MATURE_DISCIPLINARY_AND_EMPIRICAL_FIELD_SUBTRACTION", modes)
        self.assertIn("TWO_OWNER_REPLICATION != CONSTITUTIONAL_METHOD", m["safetyLaws"])
        self.assertIn("RESOURCE_COST != EPISTEMIC_VALUE", m["safetyLaws"])
        self.assertIn("INTERNAL_ARCHITECTURE != EXTERNAL_ONTOLOGY", m["safetyLaws"])


    def test_crosswalk_v05_owner_snapshot_is_ten_owner_and_media_source_fenced(self) -> None:
        snap = json.loads((ROOT / "reference/coverage-crosswalk-owner-authority-snapshot-v0-5-20260819.json").read_text())
        self.assertEqual(snap["atlasSource"]["mainRevision"], "5506abec4f755b1e72a6257a1babe33ca4180c3b")
        self.assertEqual(snap["atlasSource"]["observationResult"], "10/10 CURRENT_TO_SOURCE")
        self.assertEqual(len(snap["owners"]), 10)
        by = {x["ownerResearchRef"]: x for x in snap["owners"]}
        m = by["research-owner:media"]
        self.assertEqual(m["authorityVersionRef"], "sha256:d73f350556c6a66ecf58750dba88ce34839334fdf2920d8cb6dcdfff59fd3c33")
        self.assertEqual(m["sourceTransportRevision"], "c3b39f1a2093a9aae5338abebb8224de2a5b7a06")
        self.assertEqual(m["projectionCurrentness"], "CURRENT_TO_SOURCE")
        excluded = {x["owner"] for x in snap["excludedCurrentnessCases"]}
        self.assertEqual(excluded, {"Finance", "Harness"})

    def test_round4d_repairs_four_media_adjacent_external_identities(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round4d-media-crosswalk-repair-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        self.assertEqual(set(by), {"norm:communication-studies", "norm:media-studies", "norm:semiotics", "norm:human-computer-interaction"})
        for x in by.values():
            self.assertEqual(x["rootAdmission"], "NOT_ADMITTED")
            self.assertGreaterEqual(len(x["placements"]), 6)
            self.assertGreaterEqual(len(x["evidence"]), 2)
        self.assertIn("SIGNIFICATION_MEANING_AXIS", by["norm:semiotics"]["roleClasses"])
        self.assertIn("INTERDISCIPLINARY_COMPUTING_INTERACTION_DOMAIN", by["norm:human-computer-interaction"]["roleClasses"])
        self.assertIn("COMMUNICATION_STUDIES != MEDIA_STUDIES", r["laws"])
        self.assertIn("SOCIAL_CULTURAL_REGION_MAY_REMAIN_UNASSIGNED", r["laws"])

    def test_round4d_does_not_mint_ordivon_media_external_identity(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round4d-media-crosswalk-repair-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        self.assertFalse(any("ordivon" in ref or ref.startswith("norm:media-owner") for ref in refs))

    def test_crosswalk_v05_media_has_only_bounded_bridge_coverage(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-5-20260819.json").read_text())
        self.assertEqual(p["globalScalarCoverage"], "FORBIDDEN")
        self.assertEqual(len(p["mappings"]), 25)
        self.assertEqual(p["mediaDisposition"]["standing"], "EXTERNAL_MULTI_DOMAIN_MEDIATION_BRIDGE_MAPPED_NOVELTY_NOT_ESTABLISHED")
        self.assertEqual(p["mediaDisposition"]["directFieldEquivalence"], "NOT_CLAIMED")
        by = {x["mappingRef"]: x for x in p["mappings"]}
        for ref, ext in (
            ("crosswalk:media->communication-studies", "norm:communication-studies"),
            ("crosswalk:media->media-studies", "norm:media-studies"),
            ("crosswalk:media->semiotics", "norm:semiotics"),
            ("crosswalk:media->human-computer-interaction", "norm:human-computer-interaction"),
        ):
            self.assertEqual(by[ref]["externalRef"], ext)
            self.assertEqual(by[ref]["relation"], "BRIDGE_COVERAGE")
            self.assertIn("FALSIFICATION_TESTED", by[ref]["facets"])

    def test_media_crosswalk_preserves_art_studio_culture_and_hci_noncoverage(self) -> None:
        p = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-5-20260819.json").read_text())
        text = " | ".join(x["case"] + " :: " + x["reason"] for x in p["nonCoverageCases"])
        self.assertIn("does not absorb cultural/history/art authority", text)
        self.assertIn("does not count as whole HCI", text)
        self.assertIn("does not count as whole signification/meaning coverage", text)
        self.assertIn("does not count as whole communication coverage", text)

    def test_major_regions_v05_leave_communication_and_media_studies_unassigned(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-5-20260819.json").read_text())
        self.assertEqual(len(nav["regions"]), 8)
        members = {m for r in nav["regions"] for m in r["memberRefs"]}
        self.assertNotIn("norm:communication-studies", members)
        self.assertNotIn("norm:media-studies", members)
        pressure = {x["identityRef"] for x in nav["deferredNavigationPressure"]}
        self.assertEqual(pressure, {"norm:communication-studies", "norm:media-studies"})

    def test_major_regions_v05_keep_semiotics_and_hci_crosscutting_nonanchor(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-5-20260819.json").read_text())
        by = {x["regionRef"]: x for x in nav["regions"]}
        self.assertIn("norm:semiotics", by["navigation-region:philosophical-conceptual"]["memberRefs"])
        self.assertIn("norm:semiotics", by["navigation-region:mind-language"]["memberRefs"])
        self.assertIn("norm:human-computer-interaction", by["navigation-region:computation-computer-systems"]["memberRefs"])
        self.assertIn("norm:human-computer-interaction", by["navigation-region:engineering-design"]["memberRefs"])
        for r in nav["regions"]:
            self.assertNotIn("norm:semiotics", r["anchorRefs"])
            self.assertNotIn("norm:human-computer-interaction", r["anchorRefs"])

    def test_major_regions_v05_media_perturbation_dogfood_passes(self) -> None:
        d = json.loads((ROOT / "reference/canonical-major-regions-v0-5-dogfood-20260819.json").read_text())
        self.assertEqual(d["state"], "PASS")
        self.assertTrue(all(d["destructiveControls"].values()))
        self.assertTrue(all(x["result"] == "PASS" for x in d["regionResults"]))
        self.assertTrue(d["destructiveControls"]["communicationStudiesNotForcedIntoCurrentRegions"])
        self.assertTrue(d["destructiveControls"]["mediaStudiesNotForcedIntoCurrentRegions"])

    def test_mature_knowledge_subtraction_v03_is_candidate_method_not_constitution(self) -> None:
        m = json.loads((ROOT / "reference/open-resource-mature-knowledge-subtraction-pattern-v0-3-20260819.json").read_text())
        self.assertEqual(m["state"], "THREE_HETEROGENEOUS_OWNER_REPLICATION_METHOD_CANDIDATE_NOT_CONSTITUTIONAL")
        self.assertEqual(len(m["witnesses"]), 3)
        self.assertEqual({x["owner"] for x in m["witnesses"]}, {
            "research-owner:semantics-of-computational-descriptions",
            "research-owner:human",
            "research-owner:media",
        })
        self.assertGreaterEqual(len(m["whyNotConstitutional"]), 5)
        self.assertIn("METHOD_CANDIDATE != CONSTITUTION", m["laws"])
        self.assertIn("ABSENCE_OF_EXTERNAL_MATCH != NOVELTY", m["laws"])

    def test_whole_audit_v7_tracks_media_and_explicit_social_cultural_navigation_gap(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v7-media-crosswalk-20260819.json").read_text())
        self.assertEqual(a["counts"]["normalizedSpaces"], 90)
        self.assertEqual(a["counts"]["relations"], 120)
        self.assertEqual(a["counts"]["multiPlacementSpaces"], 87)
        self.assertEqual(a["counts"]["multiRoleSpaces"], 87)
        self.assertEqual(a["counts"]["currentOwnerAuthorityInputs"], 10)
        self.assertEqual(a["counts"]["crosswalkMappings"], 25)
        self.assertEqual(a["counts"]["canonicalMajorRegionProjections"], 8)
        self.assertEqual(a["counts"]["deferredSocialCulturalNavigationIdentities"], 2)
        self.assertEqual(a["counts"]["matureKnowledgeSubtractionWitnesses"], 3)
        self.assertEqual(a["counts"]["identityLabelCollisions"], 0)
        self.assertEqual(a["counts"]["brokenRelations"], 0)
        self.assertEqual(a["globalScalarCoverage"], "FORBIDDEN")
        self.assertIn("THREE_OWNER_REPLICATION != CONSTITUTION", a["laws"])


    def test_round5a_adds_eight_nonroot_social_cultural_boundary_identities(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5a-social-cultural-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        self.assertEqual(set(by), {
            "norm:anthropology", "norm:archaeology", "norm:sociology", "norm:education-research",
            "norm:geography", "norm:economics", "norm:political-science", "norm:legal-science",
        })
        self.assertEqual(len(r["relations"]), 28)
        for x in by.values():
            self.assertEqual(x["rootAdmission"], "NOT_ADMITTED")
            self.assertGreaterEqual(len(x["placements"]), 7)
            self.assertGreaterEqual(len(x["roleClasses"]), 3)

    def test_round5a_broad_classification_does_not_mint_ontology(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5a-social-cultural-normalization-20260819.json").read_text())
        self.assertIn("NOT_ONTOLOGY", " ".join(x["role"] for x in r["broadRecallSources"].values()))
        self.assertIn("BROAD_CLASSIFICATION_VIEW != ONTOLOGY_TRUTH", r["laws"])
        self.assertIn("SOCIAL_SCIENCES_BUCKET != CANONICAL_ROOT", r["laws"])

    def test_round5a_preserves_cross_natural_social_identity_boundaries(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5a-social-cultural-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        anth = by["norm:anthropology"]
        geo = by["norm:geography"]
        for p in ("human-biology", "archaeology", "culture", "linguistics", "society"):
            self.assertIn(p, anth["placements"])
        for p in ("earth-environment", "human-environment", "physical-geography", "society"):
            self.assertIn(p, geo["placements"])
        self.assertIn("ANTHROPOLOGY != SOCIOLOGY_SUBSPACE", r["laws"])
        self.assertIn("GEOGRAPHY != EARTH_SCIENCE_CHILD", r["laws"])

    def test_round5a_preserves_ordivon_owner_firewalls(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5a-social-cultural-normalization-20260819.json").read_text())
        self.assertIn("ECONOMICS != ORDIVON_FINANCE", r["laws"])
        self.assertIn("POLITICAL_SCIENCE != GENERIC_GOVERNANCE_OWNER", r["laws"])
        self.assertIn("LEGAL_SCIENCE != ORDIVON_NORMATIVE", r["laws"])
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        self.assertFalse(any("ordivon" in x for x in refs))

    def test_round5a_archaeology_is_explicit_and_relations_resolve(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5a-social-cultural-normalization-20260819.json").read_text())
        self.assertIn("norm:archaeology", {x["spaceRef"] for x in r["normalizedSpaces"]})
        paths = [
            "reference/foundational-census-round2a-normalization-20260819.json",
            "reference/foundational-census-round2b-normalization-20260819.json",
            "reference/foundational-census-round2c-residual-normalization-20260819.json",
            "reference/foundational-census-round3a-breadth-normalization-20260819.json",
            "reference/foundational-reference-round4a-crosswalk-induced-repair-20260819.json",
            "reference/foundational-reference-round4b-scd-crosswalk-repair-20260819.json",
            "reference/foundational-reference-round4c-human-crosswalk-repair-20260819.json",
            "reference/foundational-reference-round4d-media-crosswalk-repair-20260819.json",
            "reference/external-reference-round5a-social-cultural-normalization-20260819.json",
        ]
        rounds = [json.loads((ROOT / p).read_text()) for p in paths]
        refs = {x["spaceRef"] for rr in rounds for x in rr["normalizedSpaces"]}
        for rel in rounds[-1]["relations"]:
            self.assertIn(rel["from"], refs, rel)
            self.assertIn(rel["to"], refs, rel)

    def test_round5a_navigation_candidates_are_useful_but_not_admitted(self) -> None:
        d = json.loads((ROOT / "reference/social-cultural-major-region-pre-admission-dogfood-20260819.json").read_text())
        self.assertEqual(d["state"], "TWO_CANDIDATES_NAVIGATION_USEFUL_BUT_BREADTH_UNSTABLE_NO_ADMISSION")
        self.assertEqual(d["admittedRegions"], [])
        self.assertEqual(len(d["deferredRegions"]), 2)
        for c in d["candidates"]:
            self.assertEqual(c["gateResults"]["G2_NAVIGATION_DELETION_HARM"], "PASS_BOUNDED_FIXTURES")
            self.assertEqual(c["gateResults"]["G7_STABILITY"], "DEFERRED_BREADTH_PERTURBATION_GAPS")
            self.assertEqual(c["admission"], "DEFERRED")
            self.assertGreaterEqual(len(c["knownBreadthGaps"]), 4)
            self.assertTrue(all(x["result"] == "PASS" for x in c["navigationFixtures"]))

    def test_round5a_navigation_deletion_harm_does_not_override_stability(self) -> None:
        d = json.loads((ROOT / "reference/social-cultural-major-region-pre-admission-dogfood-20260819.json").read_text())
        self.assertIn("NAVIGATION_DELETION_HARM_PASS != STABILITY_PASS", d["laws"])
        self.assertIn("KNOWN_BREADTH_GAP_BLOCKS_MAJOR_REGION_ADMISSION", d["laws"])
        self.assertIn("IDENTITY_MAY_REMAIN_UNASSIGNED", d["laws"])

    def test_major_regions_v06_preserve_eight_regions_and_defer_social_cultural_candidates(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-6-20260819.json").read_text())
        self.assertEqual(len(nav["regions"]), 8)
        self.assertEqual(len(nav["deferredNavigationPressure"]), 2)
        self.assertEqual({x["candidateRef"] for x in nav["deferredNavigationPressure"]}, {
            "candidate-region:historical-cultural-interpretive",
            "candidate-region:social-institutional-collective",
        })
        self.assertTrue(all("DEFERRED" in x["status"] for x in nav["deferredNavigationPressure"]))
        self.assertEqual(nav["coverageCrosswalk"], "IDENTITY_LEVEL_ONLY")

    def test_whole_audit_v8_tracks_round5a_without_region_promotion(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v8-social-cultural-precensus-20260819.json").read_text())
        self.assertEqual(a["counts"]["normalizedSpaces"], 98)
        self.assertEqual(a["counts"]["relations"], 148)
        self.assertEqual(a["counts"]["multiPlacementSpaces"], 95)
        self.assertEqual(a["counts"]["multiRoleSpaces"], 95)
        self.assertEqual(a["counts"]["round5aNewIdentities"], 8)
        self.assertEqual(a["counts"]["round5aNewRelations"], 28)
        self.assertEqual(a["counts"]["socialCulturalNavigationCandidates"], 2)
        self.assertEqual(a["counts"]["round5aNewMajorRegionAdmissions"], 0)
        self.assertEqual(a["counts"]["explicitRound5bBreadthResiduals"], 10)
        self.assertEqual(a["counts"]["identityLabelCollisions"], 0)
        self.assertEqual(a["counts"]["brokenRelations"], 0)
        self.assertEqual(a["globalScalarCoverage"], "FORBIDDEN")


    def test_round5b_turns_ten_residual_pressures_into_thirteen_nonroot_identities(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5b-social-cultural-breadth-normalization-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        self.assertEqual(len(refs), 13)
        self.assertEqual(len(r["relations"]), 54)
        expected = {
            "norm:cultural-studies", "norm:literary-studies", "norm:art-history", "norm:heritage-studies",
            "norm:museology", "norm:demography", "norm:public-administration", "norm:public-policy",
            "norm:management-organization-studies", "norm:criminology", "norm:social-policy",
            "norm:social-work", "norm:human-geography",
        }
        self.assertEqual(refs, expected)
        self.assertTrue(all(x["rootAdmission"] == "NOT_ADMITTED" for x in r["normalizedSpaces"]))
        self.assertEqual(len(r["residualSplits"]), 3)
        self.assertIn("ROUND5A_RESIDUAL != ROUND5B_IDENTITY", r["laws"])
        self.assertIn("SLASH_JOINED_RESIDUAL_MAY_SPLIT", r["laws"])

    def test_round5b_evidence_driven_splits_remain_distinct(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5b-social-cultural-breadth-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        for a, b, law in (
            ("norm:heritage-studies", "norm:museology", "HERITAGE_STUDIES != MUSEOLOGY"),
            ("norm:public-administration", "norm:public-policy", "PUBLIC_ADMINISTRATION != PUBLIC_POLICY"),
            ("norm:social-policy", "norm:social-work", "SOCIAL_POLICY != SOCIAL_WORK"),
        ):
            self.assertIn(a, by); self.assertIn(b, by)
            self.assertNotEqual(by[a]["label"], by[b]["label"])
            self.assertIn(law, r["laws"])
        splits = {x["round5aResidual"]: set(x["round5bIdentities"]) for x in r["residualSplits"]}
        self.assertEqual(splits["Heritage / museum studies"], {"norm:heritage-studies", "norm:museology"})
        self.assertEqual(splits["Public administration / public policy"], {"norm:public-administration", "norm:public-policy"})
        self.assertEqual(splits["Social policy / social work"], {"norm:social-policy", "norm:social-work"})

    def test_round5b_human_geography_is_subspace_of_geography_not_all_geography(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5b-social-cultural-breadth-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        hg = by["norm:human-geography"]
        self.assertIn("MAJOR_GEOGRAPHY_SUBSPACE", hg["roleClasses"])
        self.assertIn("HUMAN_SPATIAL_DOMAIN", hg["roleClasses"])
        self.assertIn("HUMAN_GEOGRAPHY != ALL_GEOGRAPHY", r["laws"])
        self.assertIn({"from":"norm:human-geography","type":"MAJOR_SUBSPACE_OF","to":"norm:geography"}, r["relations"])

    def test_round5b_relations_resolve_across_all_normalized_rounds(self) -> None:
        paths = [
            "reference/foundational-census-round2a-normalization-20260819.json",
            "reference/foundational-census-round2b-normalization-20260819.json",
            "reference/foundational-census-round2c-residual-normalization-20260819.json",
            "reference/foundational-census-round3a-breadth-normalization-20260819.json",
            "reference/foundational-reference-round4a-crosswalk-induced-repair-20260819.json",
            "reference/foundational-reference-round4b-scd-crosswalk-repair-20260819.json",
            "reference/foundational-reference-round4c-human-crosswalk-repair-20260819.json",
            "reference/foundational-reference-round4d-media-crosswalk-repair-20260819.json",
            "reference/external-reference-round5a-social-cultural-normalization-20260819.json",
            "reference/external-reference-round5b-social-cultural-breadth-normalization-20260819.json",
        ]
        rounds = [json.loads((ROOT / p).read_text()) for p in paths]
        refs = {x["spaceRef"] for rr in rounds for x in rr["normalizedSpaces"]}
        for rel in rounds[-1]["relations"]:
            self.assertIn(rel["from"], refs, rel)
            self.assertIn(rel["to"], refs, rel)

    def test_round5b_navigation_candidates_pass_deletion_and_future_edge_perturbation(self) -> None:
        d = json.loads((ROOT / "reference/social-cultural-major-region-round5b-admission-dogfood-20260819.json").read_text())
        self.assertEqual(d["state"], "TWO_SOCIAL_CULTURAL_NAVIGATION_PROJECTIONS_ADMITTED_AFTER_ROUND5B")
        self.assertEqual(set(d["admittedRegions"]), {
            "candidate-region:historical-cultural-interpretive",
            "candidate-region:social-institutional-collective",
        })
        self.assertEqual(d["deferredRegions"], [])
        self.assertGreaterEqual(len(d["futureEdgePerturbations"]), 8)
        for c in d["candidates"]:
            self.assertEqual(c["gateResults"]["G2_NAVIGATION_DELETION_HARM"], "PASS_BOUNDED_FIXTURES")
            self.assertEqual(c["gateResults"]["G7_STABILITY"], "PASS_BOUNDED_PERTURBATION")
            self.assertEqual(c["admission"], "ADMITTED_NAVIGATION_PROJECTION_V1")
            self.assertTrue(all(x["result"] == "PASS" for x in c["navigationFixtures"]))
            self.assertTrue(all(x["result"] == "PASS" for x in c["futureEdgePerturbationFixtures"]))

    def test_round5b_social_cultural_region_admission_is_navigation_not_root(self) -> None:
        d = json.loads((ROOT / "reference/social-cultural-major-region-round5b-admission-dogfood-20260819.json").read_text())
        self.assertIn("MAJOR_REGION_ADMISSION_IS_VERSIONED_NAVIGATION_ONLY", d["laws"])
        self.assertIn("SOCIAL_CULTURAL_REGION != SOCIAL_SCIENCE_ROOT", d["laws"])
        self.assertIn("HISTORICAL_CULTURAL_REGION != HUMANITIES_ROOT", d["laws"])
        self.assertIn("REGION_COVERAGE_TRUTH_FORBIDDEN", d["laws"])

    def test_major_regions_v07_add_exactly_two_nonexclusive_social_cultural_projections(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-7-20260819.json").read_text())
        self.assertEqual(len(nav["regions"]), 10)
        self.assertEqual(nav["closureClaim"], "NONE")
        by = {x["regionRef"]: x for x in nav["regions"]}
        for ref in ("navigation-region:historical-cultural-interpretive", "navigation-region:social-institutional-collective"):
            self.assertIn(ref, by)
            self.assertEqual(by[ref]["kind"], "CANONICAL_MAJOR_REGION_PROJECTION")
            self.assertEqual(by[ref]["truthRole"], "NON_AUTHORITATIVE_NAVIGATION_PROJECTION")
            self.assertEqual(by[ref]["membershipSemantics"], "NON_EXCLUSIVE")
            self.assertEqual(by[ref]["closureClaim"], "NONE")
            self.assertEqual(by[ref]["admissionEvidence"]["status"], "ADMITTED_NAVIGATION_PROJECTION_V1")

    def test_major_regions_v07_geography_crosses_earth_and_social_navigation(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-7-20260819.json").read_text())
        by = {x["regionRef"]: x for x in nav["regions"]}
        self.assertIn("norm:geography", by["navigation-region:earth-planetary-space"]["memberRefs"])
        self.assertIn("norm:geography", by["navigation-region:social-institutional-collective"]["memberRefs"])
        self.assertIn("norm:human-geography", by["navigation-region:social-institutional-collective"]["memberRefs"])
        self.assertNotIn("norm:human-geography", by["navigation-region:earth-planetary-space"]["anchorRefs"])

    def test_crosswalk_v06_adds_regions_but_zero_new_owner_coverage_mappings(self) -> None:
        old = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-5-20260819.json").read_text())
        new = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-6-20260819.json").read_text())
        self.assertEqual(new["state"], "TEN_OWNER_CROSSWALK_REPROJECTED_ON_TEN_MAJOR_REGIONS_NO_NEW_COVERAGE_MAPPINGS")
        self.assertEqual(len(old["mappings"]), 25)
        self.assertEqual(len(new["mappings"]), 25)
        self.assertEqual(new["mappings"], old["mappings"])
        self.assertEqual(len(new["regionCoverageViews"]), 10)
        self.assertEqual(new["globalScalarCoverage"], "FORBIDDEN")
        self.assertTrue(all(x["aggregateCoverageTruth"] == "FORBIDDEN" for x in new["regionCoverageViews"]))

    def test_whole_audit_v9_tracks_round5b_region_growth_independent_of_coverage(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v9-social-cultural-round5b-20260819.json").read_text())
        counts = a["counts"]
        self.assertEqual(counts["normalizedSpaces"], 111)
        self.assertEqual(counts["relations"], 202)
        self.assertEqual(counts["multiPlacementSpaces"], 108)
        self.assertEqual(counts["multiRoleSpaces"], 108)
        self.assertEqual(counts["canonicalMajorRegionProjections"], 10)
        self.assertEqual(counts["round5bNewIdentities"], 13)
        self.assertEqual(counts["round5bNewRelations"], 54)
        self.assertEqual(counts["round5bResidualSplits"], 3)
        self.assertEqual(counts["round5bNewMajorRegionAdmissions"], 2)
        self.assertEqual(counts["currentOwnerAuthorityInputs"], 10)
        self.assertEqual(counts["crosswalkMappings"], 25)
        self.assertEqual(counts["crosswalkNewMappingsRound5b"], 0)
        self.assertEqual(counts["identityLabelCollisions"], 0)
        self.assertEqual(counts["brokenRelations"], 0)
        self.assertEqual(a["globalScalarCoverage"], "FORBIDDEN")
        self.assertIn("NEW_REGION != NEW_COVERAGE", a["laws"])
        self.assertIn("OPEN_WORLD_REMAINS_REOPENABLE", a["laws"])


    def test_round5c_normalizes_exact_nine_real_edge_identities(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5c-edge-normalization-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        self.assertEqual(refs, {
            "norm:area-regional-studies", "norm:musicology", "norm:performance-studies",
            "norm:international-studies-relations", "norm:development-studies", "norm:urban-studies",
            "norm:gender-sexuality-studies", "norm:science-technology-studies", "norm:folklore-studies",
        })
        self.assertEqual(len(r["relations"]), 54)
        self.assertTrue(all(x["rootAdmission"] == "NOT_ADMITTED" for x in r["normalizedSpaces"]))
        self.assertIn("EDGE_FIXTURE != PRECOMMITTED_ONTOLOGY", r["laws"])
        self.assertIn("IDENTITY_NORMALIZATION != REGION_OR_COVERAGE_ADMISSION", r["laws"])

    def test_round5c_area_studies_is_regional_interdisciplinary_mode(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5c-edge-normalization-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        area = by["norm:area-regional-studies"]
        self.assertIn("REGIONALLY_BOUNDED_INTERDISCIPLINARY_DOMAIN", area["roleClasses"])
        self.assertIn("AREA_KNOWLEDGE_INTEGRATION_MODE", area["roleClasses"])
        self.assertGreaterEqual(len(area["evidence"]), 3)
        self.assertIn("AREA_STUDIES_IS_REGIONAL_INTERDISCIPLINARY_MODE_NOT_OBJECT_ROOT", r["laws"])

    def test_round5c_edges_preserve_nonreduction_laws(self) -> None:
        r = json.loads((ROOT / "reference/external-reference-round5c-edge-normalization-20260819.json").read_text())
        for law in (
            "MUSICOLOGY != ART_HISTORY_SUBSPACE",
            "PERFORMANCE_STUDIES != MEDIA_STUDIES_SUBSPACE",
            "INTERNATIONAL_STUDIES != POLITICAL_SCIENCE_ONLY",
            "DEVELOPMENT_STUDIES != ECONOMICS_ONLY",
            "URBAN_STUDIES != HUMAN_GEOGRAPHY_ONLY",
            "WGSS_IS_INTERDISCIPLINARY_NOT_SOCIOLOGY_CHILD",
            "STS_IS_REFLEXIVE_CROSS_DOMAIN_NOT_ENGINEERING_CHILD",
            "FOLKLORE_STUDIES != ANTHROPOLOGY_CHILD",
        ):
            self.assertIn(law, r["laws"])

    def test_round5c_relations_resolve_across_whole_graph(self) -> None:
        paths = [
            "reference/foundational-census-round2a-normalization-20260819.json",
            "reference/foundational-census-round2b-normalization-20260819.json",
            "reference/foundational-census-round2c-residual-normalization-20260819.json",
            "reference/foundational-census-round3a-breadth-normalization-20260819.json",
            "reference/foundational-reference-round4a-crosswalk-induced-repair-20260819.json",
            "reference/foundational-reference-round4b-scd-crosswalk-repair-20260819.json",
            "reference/foundational-reference-round4c-human-crosswalk-repair-20260819.json",
            "reference/foundational-reference-round4d-media-crosswalk-repair-20260819.json",
            "reference/external-reference-round5a-social-cultural-normalization-20260819.json",
            "reference/external-reference-round5b-social-cultural-breadth-normalization-20260819.json",
            "reference/external-reference-round5c-edge-normalization-20260819.json",
        ]
        rounds = [json.loads((ROOT / p).read_text()) for p in paths]
        refs = {x["spaceRef"] for rr in rounds for x in rr["normalizedSpaces"]}
        for rel in rounds[-1]["relations"]:
            self.assertIn(rel["from"], refs, rel)
            self.assertIn(rel["to"], refs, rel)

    def test_major_regions_v08_absorb_all_round5c_edges_without_new_region_or_anchor(self) -> None:
        old = json.loads((ROOT / "reference/canonical-major-regions-v0-7-20260819.json").read_text())
        new = json.loads((ROOT / "reference/canonical-major-regions-v0-8-20260819.json").read_text())
        self.assertEqual(len(old["regions"]), 10)
        self.assertEqual(len(new["regions"]), 10)
        old_by = {x["regionRef"]: x for x in old["regions"]}
        new_by = {x["regionRef"]: x for x in new["regions"]}
        for ref in old_by:
            self.assertEqual(old_by[ref]["anchorRefs"], new_by[ref]["anchorRefs"])
        new_edges = {
            "norm:area-regional-studies", "norm:musicology", "norm:performance-studies",
            "norm:international-studies-relations", "norm:development-studies", "norm:urban-studies",
            "norm:gender-sexuality-studies", "norm:science-technology-studies", "norm:folklore-studies",
        }
        members = {m for r in new["regions"] for m in r["memberRefs"]}
        self.assertTrue(new_edges.issubset(members))
        anchors = {a for r in new["regions"] for a in r["anchorRefs"]}
        self.assertTrue(new_edges.isdisjoint(anchors))

    def test_round5c_sts_and_area_wgss_are_nonexclusive_cross_region_members(self) -> None:
        nav = json.loads((ROOT / "reference/canonical-major-regions-v0-8-20260819.json").read_text())
        by = {x["regionRef"]: x for x in nav["regions"]}
        self.assertIn("norm:science-technology-studies", by["navigation-region:social-institutional-collective"]["memberRefs"])
        self.assertIn("norm:science-technology-studies", by["navigation-region:philosophical-conceptual"]["memberRefs"])
        self.assertIn("norm:science-technology-studies", by["navigation-region:engineering-design"]["memberRefs"])
        self.assertIn("norm:area-regional-studies", by["navigation-region:historical-cultural-interpretive"]["memberRefs"])
        self.assertIn("norm:area-regional-studies", by["navigation-region:social-institutional-collective"]["memberRefs"])
        self.assertIn("norm:gender-sexuality-studies", by["navigation-region:historical-cultural-interpretive"]["memberRefs"])
        self.assertIn("norm:gender-sexuality-studies", by["navigation-region:social-institutional-collective"]["memberRefs"])

    def test_crosswalk_v07_round5c_reprojects_zero_new_coverage_mappings(self) -> None:
        old = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-6-20260819.json").read_text())
        new = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-7-20260819.json").read_text())
        self.assertEqual(new["state"], "TEN_OWNER_CROSSWALK_REPROJECTED_AFTER_ROUND5C_ZERO_NEW_COVERAGE_MAPPINGS")
        self.assertEqual(old["mappings"], new["mappings"])
        self.assertEqual(len(new["mappings"]), 25)
        self.assertEqual(len(new["regionCoverageViews"]), 10)
        self.assertTrue(all(x["aggregateCoverageTruth"] == "FORBIDDEN" for x in new["regionCoverageViews"]))
        self.assertEqual(new["globalScalarCoverage"], "FORBIDDEN")

    def test_topology_saturation_audit_recommends_pause_not_world_closure(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-topology-saturation-reopen-audit-v1-20260819.json").read_text())
        self.assertEqual(a["state"], "BREADTH_EXPANSION_PAUSE_RECOMMENDED_OPEN_WORLD_REOPENABLE")
        self.assertEqual(a["pauseDecision"], "PAUSE_CHECKLIST_BREADTH_EXPANSION")
        self.assertTrue(a["tests"]["allNineRealEdgesPlacedWithoutNewRegion"])
        self.assertTrue(a["tests"]["existingTenRegionAnchorsUnchanged"])
        self.assertEqual(a["tests"]["newMajorRegionsRequired"], 0)
        self.assertEqual(a["tests"]["newCoverageMappingsAuthorized"], 0)
        self.assertGreaterEqual(len(a["reopenTriggers"]), 5)
        self.assertIn("PAUSE_BREADTH != CLOSE_WORLD", a["laws"])
        self.assertIn("SATURATION_IN_NAVIGATION != ONTOLOGY_COMPLETION", a["laws"])
        self.assertIn("REOPEN_REQUIRES_STRUCTURAL_PRESSURE", a["laws"])

    def test_topology_saturation_reopen_requires_structural_not_single_item_pressure(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-topology-saturation-reopen-audit-v1-20260819.json").read_text())
        triggers = {x["trigger"] for x in a["reopenTriggers"]}
        self.assertIn("UNPLACEABLE_HIGH_VALUE_CLUSTER", triggers)
        self.assertIn("OWNER_CROSSWALK_REFERENCE_GAP", triggers)
        self.assertIn("MAJOR_REGION_DELETION_HARM_DEGRADES", triggers)
        non = " | ".join(a["nonTriggers"])
        self.assertIn("single newly discovered discipline", non)
        self.assertIn("catalog completeness", non)
        self.assertIn("project name", non)

    def test_whole_audit_v10_establishes_real_edge_navigation_saturation(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v10-round5c-saturation-20260819.json").read_text())
        c = a["counts"]
        self.assertEqual(c["normalizedSpaces"], 120)
        self.assertEqual(c["relations"], 256)
        self.assertEqual(c["multiPlacementSpaces"], 117)
        self.assertEqual(c["multiRoleSpaces"], 117)
        self.assertEqual(c["canonicalMajorRegionProjections"], 10)
        self.assertEqual(c["round5cNewIdentities"], 9)
        self.assertEqual(c["round5cNewRelations"], 54)
        self.assertEqual(c["round5cNewMajorRegions"], 0)
        self.assertEqual(c["currentOwnerAuthorityInputs"], 10)
        self.assertEqual(c["crosswalkMappings"], 25)
        self.assertEqual(c["crosswalkNewMappingsRound5c"], 0)
        self.assertEqual(c["identityLabelCollisions"], 0)
        self.assertEqual(c["brokenRelations"], 0)
        self.assertEqual(a["coverageReadiness"], "READY_TO_SHIFT_FROM_BREADTH_CARTOGRAPHY_TO_FRONTIER_COVERAGE_ANALYSIS")
        self.assertTrue(a["openWorld"])
        self.assertEqual(a["globalScalarCoverage"], "FORBIDDEN")


    def test_frontier_v1_counts_match_saturated_reference_graph(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-frontier-analysis-v1-20260819.json").read_text())
        c = a["counts"]
        self.assertEqual(c["normalizedIdentities"], 120)
        self.assertEqual(c["relations"], 256)
        self.assertEqual(c["currentOwnerAuthorityInputs"], 10)
        self.assertEqual(c["mappingRows"], 25)
        self.assertEqual(c["mappedUniqueIdentities"], 23)
        self.assertEqual(c["unmappedIdentities"], 97)
        self.assertEqual(c["unmappedMajorRegionAnchors"], 22)
        self.assertEqual(c["zeroDirectTouchMajorRegions"], 2)

    def test_frontier_v1_forbids_unmapped_to_untouched_lifting(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-frontier-analysis-v1-20260819.json").read_text())
        self.assertIn("UNMAPPED_IDENTITY != ORDIVON_UNTOUCHED", a["laws"])
        self.assertIn("ABSENT_OWNER_PUBLICATION != ABSENT_RESEARCH", a["laws"])
        self.assertIn("UNMAPPED_ANCHOR != REGION_UNCOVERED_TRUTH", a["laws"])
        self.assertIn("FRONTIER_DIAGNOSTIC != RESEARCH_ROADMAP", a["laws"])

    def test_frontier_v1_region_diagnostics_never_mint_region_coverage(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-frontier-analysis-v1-20260819.json").read_text())
        self.assertEqual(len(a["regionDiagnostics"]), 10)
        for r in a["regionDiagnostics"]:
            self.assertEqual(r["aggregateCoverageTruth"], "FORBIDDEN")
        zero = {r["regionRef"] for r in a["regionDiagnostics"] if r["mappedMemberCount"] == 0}
        self.assertEqual(zero, {"navigation-region:physical-material", "navigation-region:earth-planetary-space"})

    def test_frontier_v1_anchor_touch_is_navigation_diagnostic_only(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-frontier-analysis-v1-20260819.json").read_text())
        all_mapped = {r["regionRef"] for r in a["regionDiagnostics"] if r["anchorTouchState"] == "ALL_ANCHORS_HAVE_DIRECT_IDENTITY_MAPPING"}
        self.assertEqual(all_mapped, {"navigation-region:computation-computer-systems", "navigation-region:mind-language"})
        self.assertEqual(len(a["unmappedMajorRegionAnchors"]), 22)

    def test_frontier_v1_no_lift_examples_remain_unmapped(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-frontier-analysis-v1-20260819.json").read_text())
        refs = {x["externalRef"] for x in a["mappedNeighborNoLiftFrontiers"]}
        for ref in ("norm:philosophy", "norm:biology", "norm:foundations-programming-languages", "norm:software-engineering", "norm:sociology"):
            self.assertIn(ref, refs)
        self.assertIn("MAPPED_SUBSPACE != PARENT_FIELD_COVERAGE", a["laws"])
        self.assertIn("MAPPED_NEIGHBOR != COVERAGE", a["laws"])

    def test_frontier_v1_owner_states_separate_weak_scope_and_publication_absence(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-frontier-analysis-v1-20260819.json").read_text())
        rows = {(x.get("ownerResearchRef") or x.get("owner")): x for x in a["ownerFrontiers"]}
        self.assertEqual(rows["research-owner:host"]["state"], "EXTERNAL_MAPPING_WEAK_NOVELTY_NOT_ESTABLISHED")
        self.assertEqual(rows["research-owner:game"]["state"], "OUT_OF_FOUNDATIONAL_PILOT_SCOPE")
        self.assertEqual(rows["Finance"]["state"], "OWNER_CURRENTNESS_EXCLUDED")
        self.assertEqual(rows["Harness"]["state"], "OWNER_CURRENTNESS_EXCLUDED_ACTIVE_RESEARCH")

    def test_frontier_v1_graph_degree_cannot_rank_importance(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-frontier-analysis-v1-20260819.json").read_text())
        self.assertIn("GRAPH_DEGREE != IMPORTANCE", a["laws"])
        self.assertEqual(a["state"], "FRONTIER_BASELINE_ESTABLISHED_AFTER_BOUNDED_BREADTH_SATURATION")


    def test_frontier_state_contract_separates_fact_navigation_and_owner_states(self) -> None:
        c = json.loads((ROOT / "reference/external-reference-frontier-state-contract-v0-20260819.json").read_text())
        self.assertEqual(c["truthRole"], "NON_AUTHORITATIVE_FRONTIER_ANALYSIS_CONTRACT")
        self.assertEqual(set(c["identityFactStates"]), {"MAPPED_CURRENT_OWNER", "NO_DIRECT_MAPPING_CURRENT_TEN_OWNER_PILOT"})
        self.assertIn("UNMAPPED_MAJOR_REGION_ANCHOR", c["navigationPriorityOverlays"])
        self.assertIn("PUBLICATION_UNAVAILABLE", c["ownerFrontierStates"])
        self.assertIn("FRONTIER_PRIORITY != RESEARCH_VALUE_SCORE", c["laws"])
        self.assertIn("GLOBAL_SCALAR_COVERAGE_FORBIDDEN", c["laws"])

    def test_frontier_matrix_v0_is_exact_over_120_identities(self) -> None:
        m = json.loads((ROOT / "reference/external-reference-frontier-matrix-v0-20260819.json").read_text())
        self.assertEqual(len(m["rows"]), 120)
        self.assertEqual(m["counts"]["mappedIdentities"], 23)
        self.assertEqual(m["counts"]["noDirectMappingCurrentPilot"], 97)
        self.assertEqual(m["counts"]["unmappedMajorRegionAnchors"], 22)
        self.assertEqual(m["counts"]["unmappedNoRegionMembers"], 11)
        self.assertEqual(m["globalScalarCoverage"], "FORBIDDEN")
        self.assertEqual(len({r["externalRef"] for r in m["rows"]}), 120)

    def test_unassigned_identity_audit_repairs_navigation_without_reopen(self) -> None:
        a = json.loads((ROOT / "reference/external-reference-unassigned-identity-disposition-audit-v0-20260819.json").read_text())
        self.assertEqual(a["counts"], {"addToExistingRegions": 11, "breadthReopenTriggered": 0, "newMajorRegionRequired": 0, "remainRegionNeutral": 0, "unassignedIdentities": 11})
        self.assertTrue(all(r["disposition"] == "ADD_TO_EXISTING_REGIONS" for r in a["rows"]))
        self.assertTrue(all(r["regions"] for r in a["rows"]))
        self.assertIn("UNASSIGNED_IDENTITY != NEW_MAJOR_REGION", a["laws"])
        self.assertIn("NAVIGATION_MEMBERSHIP != COVERAGE", a["laws"])

    def test_major_regions_v09_repairs_navigation_debt_without_anchor_or_region_growth(self) -> None:
        old = json.loads((ROOT / "reference/canonical-major-regions-v0-8-20260819.json").read_text())
        new = json.loads((ROOT / "reference/canonical-major-regions-v0-9-20260819.json").read_text())
        self.assertEqual(len(old["regions"]), len(new["regions"]), 10)
        old_by = {r["regionRef"]: r for r in old["regions"]}
        new_by = {r["regionRef"]: r for r in new["regions"]}
        self.assertEqual(set(old_by), set(new_by))
        for ref in old_by:
            self.assertEqual(old_by[ref]["anchorRefs"], new_by[ref]["anchorRefs"])
            self.assertEqual(new_by[ref]["closureClaim"], "NONE")
            self.assertEqual(new_by[ref]["membershipSemantics"], "NON_EXCLUSIVE")
        self.assertEqual(new["navigationRepairRef"], "reference/external-reference-unassigned-identity-disposition-audit-v0-20260819.json")

    def test_crosswalk_v08_reprojection_adds_zero_mappings_and_removes_stale_untouched_field(self) -> None:
        old = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-7-20260819.json").read_text())
        new = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-8-20260819.json").read_text())
        self.assertEqual(len(old["mappings"]), len(new["mappings"]), 25)
        self.assertEqual(old["mappings"], new["mappings"])
        self.assertNotIn("explicitUntouchedIdentityCandidates", new)
        self.assertEqual(new["legacyUntouchedCandidateFieldDisposition"]["status"], "REMOVED_FROM_CURRENT_PROJECTION_AS_SEMANTICALLY_STALE")
        self.assertIn("!= ORDIVON_UNTOUCHED", new["currentFrontierSemantics"])
        self.assertEqual(new["globalScalarCoverage"], "FORBIDDEN")

    def test_frontier_matrix_v01_eliminates_no_region_debt_without_changing_mapping_facts(self) -> None:
        old = json.loads((ROOT / "reference/external-reference-frontier-matrix-v0-20260819.json").read_text())
        new = json.loads((ROOT / "reference/external-reference-frontier-matrix-v0-1-20260819.json").read_text())
        self.assertEqual(len(old["rows"]), len(new["rows"]), 120)
        self.assertEqual(old["counts"]["mappedIdentities"], new["counts"]["mappedIdentities"], 23)
        self.assertEqual(old["counts"]["noDirectMappingCurrentPilot"], new["counts"]["noDirectMappingCurrentPilot"], 97)
        self.assertEqual(old["counts"]["unmappedMajorRegionAnchors"], new["counts"]["unmappedMajorRegionAnchors"], 22)
        self.assertEqual(old["counts"]["unmappedNoRegionMembers"], 11)
        self.assertEqual(new["counts"]["unmappedNoRegionMembers"], 0)
        facts_old = {r["externalRef"]: (r["factState"], tuple(r["mappedOwners"]), tuple(r["mappingRefs"])) for r in old["rows"]}
        facts_new = {r["externalRef"]: (r["factState"], tuple(r["mappedOwners"]), tuple(r["mappingRefs"])) for r in new["rows"]}
        self.assertEqual(facts_old, facts_new)

    def test_frontier_priority_v01_is_nonscalar_inspection_overlay_not_research_value(self) -> None:
        p = json.loads((ROOT / "reference/external-reference-frontier-priority-v0-1-20260819.json").read_text())
        self.assertEqual(p["globalScalarPriority"], "FORBIDDEN")
        self.assertEqual(p["classes"]["CURRENTLY_MAPPED_COUNT"], 23)
        self.assertEqual(len(p["classes"]["NAVIGATION_FRONTIER_A"]), 22)
        self.assertEqual(len(p["classes"]["NAVIGATION_FRONTIER_B"]), 20)
        self.assertEqual(p["classes"]["NAVIGATION_FRONTIER_C_COUNT"], 55)
        self.assertIn("PRIORITY_CLASS != EPISTEMIC_IMPORTANCE", p["laws"])
        self.assertIn("NO_CURRENT_MAPPING != ABSENCE_OF_ORDIVON_RESEARCH", p["laws"])
        self.assertTrue(all(r["aggregateCoverageTruth"] == "FORBIDDEN" for r in p["regionPostures"]))

    def test_owner_frontier_status_separates_mapping_weak_out_of_scope_and_publication_unavailable(self) -> None:
        o = json.loads((ROOT / "reference/external-reference-owner-frontier-status-v0-20260819.json").read_text())
        by = {r["ownerResearchRef"]: r for r in o["rows"]}
        self.assertEqual(len(by), 12)
        self.assertEqual(by["research-owner:host"]["frontierState"], "CURRENT_EXTERNAL_MAPPING_WEAK")
        self.assertEqual(by["research-owner:host"]["noveltyStanding"], "NOVELTY_NOT_ESTABLISHED")
        self.assertEqual(by["research-owner:game"]["frontierState"], "CURRENT_OUT_OF_BOUNDED_REFERENCE_SCOPE")
        self.assertEqual(by["research-owner:finance"]["frontierState"], "PUBLICATION_UNAVAILABLE")
        self.assertEqual(by["research-owner:harness"]["frontierState"], "PUBLICATION_UNAVAILABLE")
        self.assertIn("PUBLICATION_UNAVAILABLE != UNTOUCHED", o["laws"])


    def test_whole_audit_v11_establishes_frontier_state_without_reopening_breadth(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v11-frontier-state-20260819.json").read_text())
        c = a["counts"]
        self.assertEqual(a["state"], "FRONTIER_STATE_MODEL_ESTABLISHED_BREADTH_PAUSE_MAINTAINED")
        self.assertEqual(c["normalizedSpaces"], 120)
        self.assertEqual(c["relations"], 256)
        self.assertEqual(c["canonicalMajorRegionProjections"], 10)
        self.assertEqual(c["crosswalkMappings"], 25)
        self.assertEqual(c["mappedUniqueIdentities"], 23)
        self.assertEqual(c["noDirectMappingCurrentPilot"], 97)
        self.assertEqual((c["navigationFrontierA"], c["navigationFrontierB"], c["navigationFrontierC"]), (22, 20, 55))
        self.assertEqual(c["unassignedBeforeRepair"], 11)
        self.assertEqual(c["unassignedAfterRepair"], 0)
        self.assertEqual(c["newMajorRegionsFromFrontierRepair"], 0)
        self.assertEqual(c["newCoverageMappingsFromFrontierRepair"], 0)
        self.assertEqual(a["breadthPosture"], "PAUSED_BY_BOUNDED_SATURATION_OPEN_WORLD_REOPENABLE")
        self.assertEqual(a["coveragePosture"], "IDENTITY_LEVEL_SOURCE_FENCED_NO_SCALAR")
        self.assertEqual(a["frontierPosture"], "RULE_BASED_NONSCALAR_INSPECTION_ONLY")
        self.assertIn("NAVIGATION_OVERLAY != RESEARCH_VALUE", a["laws"])


    def test_round6a_host_repair_adds_exact_two_external_nonroot_identities(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round6a-host-crosswalk-repair-20260819.json").read_text())
        by = {x["spaceRef"]: x for x in r["normalizedSpaces"]}
        self.assertEqual(set(by), {"norm:workflow-process-systems", "norm:provenance-information-lineage"})
        self.assertEqual(len(r["relations"]), 7)
        self.assertTrue(all(x["rootAdmission"] == "NOT_ADMITTED" for x in by.values()))
        self.assertGreaterEqual(len(by["norm:workflow-process-systems"]["evidence"]), 2)
        self.assertGreaterEqual(len(by["norm:provenance-information-lineage"]["evidence"]), 2)
        self.assertIn("WORKFLOW_PROCESS_SYSTEMS != HOST_OWNER", r["laws"])
        self.assertIn("PROVENANCE_LINEAGE != HOST_OWNER", r["laws"])
        self.assertIn("OWNER_SPECIFIC_RESIDUAL != NOVEL_FIELD", r["laws"])

    def test_round6a_does_not_mint_host_named_external_ontology(self) -> None:
        r = json.loads((ROOT / "reference/foundational-reference-round6a-host-crosswalk-repair-20260819.json").read_text())
        refs = {x["spaceRef"] for x in r["normalizedSpaces"]}
        self.assertFalse(any("host" in x or "ordivon" in x for x in refs))

    def test_host_subtraction_ledger_explains_surface_but_preserves_non_novel_residuals(self) -> None:
        l = json.loads((ROOT / "reference/host-external-mature-knowledge-subtraction-v0-20260819.json").read_text())
        self.assertIn("NOVELTY_NOT_ESTABLISHED", l["state"])
        self.assertEqual(len(l["subtractions"]), 3)
        self.assertEqual(len(l["residuals"]), 4)
        self.assertTrue(all(x["standing"] == "OWNER_SPECIFIC_RESIDUAL_NO_NOVELTY_INFERENCE" for x in l["residuals"]))
        self.assertIn("Do not re-admit Generic Coordination owner.", l["negativeConclusions"])

    def test_crosswalk_v09_replaces_host_weak_row_with_two_bridge_mappings_only(self) -> None:
        old = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-8-20260819.json").read_text())
        new = json.loads((ROOT / "reference/coverage-crosswalk-foundational-pilot-v0-9-20260819.json").read_text())
        self.assertEqual(len(old["mappings"]), 25)
        self.assertEqual(len(new["mappings"]), 26)
        refs = {x["mappingRef"]: x for x in new["mappings"]}
        self.assertNotIn("crosswalk:host->external-mapping-weak", refs)
        for ref, ext in (("crosswalk:host->workflow-process-systems", "norm:workflow-process-systems"), ("crosswalk:host->provenance-information-lineage", "norm:provenance-information-lineage")):
            self.assertEqual(refs[ref]["externalRef"], ext)
            self.assertEqual(refs[ref]["relation"], "BRIDGE_COVERAGE")
        self.assertEqual(new["hostDisposition"]["directFieldEquivalence"], "NOT_CLAIMED")
        self.assertIn("NOVELTY_NOT_ESTABLISHED", new["hostDisposition"]["standing"])

    def test_major_regions_v010_absorb_host_repair_without_region_or_anchor_growth(self) -> None:
        old = json.loads((ROOT / "reference/canonical-major-regions-v0-9-20260819.json").read_text())
        new = json.loads((ROOT / "reference/canonical-major-regions-v0-10-20260819.json").read_text())
        self.assertEqual(len(old["regions"]), len(new["regions"]), 10)
        ob = {r["regionRef"]: r for r in old["regions"]}; nb = {r["regionRef"]: r for r in new["regions"]}
        self.assertEqual(set(ob), set(nb))
        for ref in ob:
            self.assertEqual(ob[ref]["anchorRefs"], nb[ref]["anchorRefs"])
            self.assertEqual(nb[ref]["closureClaim"], "NONE")
        for ref in ("norm:workflow-process-systems", "norm:provenance-information-lineage"):
            self.assertFalse(any(ref in r["anchorRefs"] for r in new["regions"]))

    def test_major_regions_v010_host_repair_dogfood_passes(self) -> None:
        d = json.loads((ROOT / "reference/canonical-major-regions-v0-10-dogfood-20260819.json").read_text())
        self.assertEqual(d["state"], "PASS")
        self.assertTrue(all(d["destructiveControls"].values()))
        self.assertTrue(all(x["result"] == "PASS" for x in d["regionResults"]))

    def test_frontier_matrix_v02_changes_only_two_new_mapped_identities(self) -> None:
        old = json.loads((ROOT / "reference/external-reference-frontier-matrix-v0-1-20260819.json").read_text())
        new = json.loads((ROOT / "reference/external-reference-frontier-matrix-v0-2-20260819.json").read_text())
        self.assertEqual(new["counts"], {"currentMappings": 26, "identities": 122, "mappedIdentities": 25, "noDirectMappingCurrentPilot": 97, "unmappedCrossRegionMembers": 20, "unmappedMajorRegionAnchors": 22, "unmappedNoRegionMembers": 0, "unmappedSingleRegionMembers": 55})
        of = {r["externalRef"]: r["factState"] for r in old["rows"]}; nf = {r["externalRef"]: r["factState"] for r in new["rows"]}
        self.assertTrue(all(nf[k] == v for k, v in of.items()))
        self.assertEqual(nf["norm:workflow-process-systems"], "MAPPED_CURRENT_OWNER")
        self.assertEqual(nf["norm:provenance-information-lineage"], "MAPPED_CURRENT_OWNER")

    def test_owner_frontier_v01_resolves_host_weak_mapping_without_novelty(self) -> None:
        o = json.loads((ROOT / "reference/external-reference-owner-frontier-status-v0-1-20260819.json").read_text())
        h = next(r for r in o["rows"] if r["ownerResearchRef"] == "research-owner:host")
        self.assertEqual(h["frontierState"], "CURRENT_MAPPED")
        self.assertEqual(h["mappedExternalRefs"], ["norm:workflow-process-systems", "norm:provenance-information-lineage"])
        self.assertEqual(h["noveltyStanding"], "NOVELTY_NOT_ESTABLISHED")
        self.assertEqual(h["mappingQualification"], "BRIDGE_ONLY_NO_FIELD_EQUIVALENCE")
        self.assertIn("OWNER_SPECIFIC_RESIDUAL != NOVELTY", o["laws"])

    def test_frontier_priority_v02_preserves_prior_A_B_C_partition(self) -> None:
        p = json.loads((ROOT / "reference/external-reference-frontier-priority-v0-2-20260819.json").read_text())
        self.assertEqual(p["classes"]["CURRENTLY_MAPPED_COUNT"], 25)
        self.assertEqual(len(p["classes"]["NAVIGATION_FRONTIER_A"]), 22)
        self.assertEqual(len(p["classes"]["NAVIGATION_FRONTIER_B"]), 20)
        self.assertEqual(p["classes"]["NAVIGATION_FRONTIER_C_COUNT"], 55)
        self.assertEqual(p["classes"]["UNMAPPED_NO_REGION_COUNT"], 0)
        self.assertEqual(p["globalScalarPriority"], "FORBIDDEN")
        self.assertIn("HOST_REPAIR_DOES_NOT_REORDER_UNRELATED_FRONTIERS", p["laws"])

    def test_mature_knowledge_subtraction_v04_has_four_witnesses_but_is_not_constitution(self) -> None:
        m = json.loads((ROOT / "reference/open-resource-mature-knowledge-subtraction-pattern-v0-4-20260819.json").read_text())
        self.assertEqual(len(m["witnesses"]), 4)
        self.assertEqual(m["state"], "FOUR_HETEROGENEOUS_OWNER_REPLICATION_METHOD_CANDIDATE_NOT_CONSTITUTIONAL")
        self.assertEqual(m["truthRole"], "RESEARCH_METHOD_CANDIDATE_NOT_CONSTITUTION")
        self.assertIn("METHOD_CANDIDATE != CONSTITUTION", m["laws"])
        self.assertTrue(any(x["owner"] == "research-owner:host" for x in m["witnesses"]))

    def test_whole_audit_v12_tracks_host_repair_without_breadth_resume(self) -> None:
        a = json.loads((ROOT / "reference/foundational-whole-topology-audit-v12-host-crosswalk-repair-20260819.json").read_text())
        c = a["counts"]
        self.assertEqual((c["normalizedSpaces"], c["relations"], c["canonicalMajorRegionProjections"]), (122, 263, 10))
        self.assertEqual((c["crosswalkMappings"], c["mappedUniqueIdentities"], c["noDirectMappingCurrentPilot"]), (26, 25, 97))
        self.assertEqual((c["navigationFrontierA"], c["navigationFrontierB"], c["navigationFrontierC"]), (22, 20, 55))
        self.assertEqual(c["externalMappingWeakOwners"], 0)
        self.assertEqual(c["hostBridgeMappings"], 2)
        self.assertEqual(c["newMajorRegionsFromRound6A"], 0)
        self.assertEqual(a["repairTrigger"], "OWNER_CROSSWALK_REFERENCE_GAP")
        self.assertIn("BREADTH_PAUSE", a["state"])
        self.assertIn("NOVELTY_NOT_ESTABLISHED", a["hostPosture"])



if __name__ == "__main__":
    unittest.main()
