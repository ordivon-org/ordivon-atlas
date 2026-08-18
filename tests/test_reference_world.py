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



if __name__ == "__main__":
    unittest.main()
