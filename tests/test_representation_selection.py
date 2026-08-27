from __future__ import annotations

import unittest

from ordivon_atlas.representation_selection import (
    RepresentationSelectionError,
    select_representation,
)


class RepresentationSelectionTests(unittest.TestCase):
    def base(self):
        return {
            "kind": "ordivon.atlas-representation-selection-request-v0",
            "operationRef": "consumer:test",
            "requiredDistinctions": ["identity", "currentness"],
            "costMetric": "bytes",
            "profiles": [
                {"id": "RAW", "preserves": ["identity"], "measuredCost": 100},
                {"id": "CAPSULE", "preserves": ["identity", "currentness"], "measuredCost": 200},
                {"id": "FULL", "preserves": ["identity", "currentness", "history"], "measuredCost": 900},
            ],
        }

    def test_selects_cheapest_adequate_not_cheapest_overall(self):
        result = select_representation(self.base())
        self.assertEqual(result["selectedProfileId"], "CAPSULE")
        self.assertFalse(result["claims"]["semanticRequirementsInferred"])
        self.assertFalse(result["claims"]["executionAdmissionGranted"])

    def test_budget_fails_closed(self):
        request = self.base()
        request["maxCost"] = 150
        result = select_representation(request)
        self.assertEqual(result["disposition"], "NO_ADEQUATE_PROFILE")
        self.assertIsNone(result["selectedProfileId"])

    def test_cost_can_beat_semantically_smaller_profile_when_both_are_adequate(self):
        request = self.base()
        request["profiles"][1]["measuredCost"] = 950
        result = select_representation(request)
        self.assertEqual(result["selectedProfileId"], "FULL")

    def test_equal_cost_prefers_less_excess(self):
        request = self.base()
        request["profiles"][2]["measuredCost"] = 200
        result = select_representation(request)
        self.assertEqual(result["selectedProfileId"], "CAPSULE")

    def test_duplicate_requirement_fails_closed(self):
        request = self.base()
        request["requiredDistinctions"] = ["identity", "identity"]
        with self.assertRaisesRegex(RepresentationSelectionError, "duplicate"):
            select_representation(request)


if __name__ == "__main__":
    unittest.main()
