from __future__ import annotations

import copy
import json
import unittest

from src.fantasy_scoring import (
    build_scoring_profile_from_sleeper_settings,
    calculate_fantasy_breakdown,
    calculate_fantasy_points,
    get_default_scoring_profile,
    normalize_stat_row,
)


class FantasyScoringTests(unittest.TestCase):
    def sample_stat_row(self):
        return {
            "passing_yards": 250,
            "passing_tds": 2,
            "interceptions": 1,
            "rushing_yards": 20,
            "rushing_tds": 1,
            "receptions": 5,
            "receiving_yards": 60,
            "receiving_tds": 1,
            "fumbles_lost": 1,
        }

    def test_standard_scoring_calculation(self):
        points = calculate_fantasy_points(
            self.sample_stat_row(),
            get_default_scoring_profile("standard"),
        )

        self.assertAlmostEqual(points, 34.0)

    def test_half_ppr_scoring_calculation(self):
        points = calculate_fantasy_points(
            self.sample_stat_row(),
            get_default_scoring_profile("half_ppr"),
        )

        self.assertAlmostEqual(points, 36.5)

    def test_ppr_scoring_calculation(self):
        points = calculate_fantasy_points(
            self.sample_stat_row(),
            get_default_scoring_profile("ppr"),
        )

        self.assertAlmostEqual(points, 39.0)

    def test_legacy_profile_keys_are_supported(self):
        points = calculate_fantasy_points(
            {"receptions": 4, "receiving_yards": 40},
            {
                "scoring_profile_id": "legacy_half_ppr",
                "settings": {
                    "reception": 0.5,
                    "receiving_td": 6,
                    "passing_td": 4,
                    "rushing_td": 6,
                },
            },
        )

        self.assertAlmostEqual(points, 6.0)

    def test_custom_sleeper_scoring_mapping(self):
        profile = build_scoring_profile_from_sleeper_settings({
            "pass_yd": 0.05,
            "pass_td": 6,
            "pass_int": -3,
            "rush_yd": 0.1,
            "rush_td": 6,
            "rec": 1,
            "rec_yd": 0.1,
            "rec_td": 6,
            "mystery_bonus": 2,
        })

        self.assertEqual(profile["settings"]["passing_yards"], 0.05)
        self.assertEqual(profile["settings"]["passing_tds"], 6.0)
        self.assertEqual(profile["settings"]["interceptions"], -3.0)
        self.assertEqual(profile["settings"]["receptions"], 1.0)
        self.assertEqual(profile["unmapped_settings"], {"mystery_bonus": 2})

    def test_missing_stat_fields_default_to_zero(self):
        normalized = normalize_stat_row({"receptions": 3})

        self.assertEqual(normalized["passing_yards"], 0.0)
        self.assertEqual(normalized["receiving_yards"], 0.0)
        self.assertEqual(normalized["receptions"], 3.0)

    def test_missing_fields_recorded_in_missing_data_flags(self):
        normalized = normalize_stat_row({"receptions": 3})

        self.assertIn("missing_passing_yards", normalized["missing_data_flags"])
        self.assertIn("missing_receiving_yards", normalized["missing_data_flags"])
        self.assertNotIn("missing_receptions", normalized["missing_data_flags"])

    def test_scoring_breakdown_includes_components(self):
        breakdown = calculate_fantasy_breakdown(
            self.sample_stat_row(),
            get_default_scoring_profile("ppr"),
        )

        for key in (
            "passing_points",
            "rushing_points",
            "receiving_points",
            "reception_points",
            "turnover_points",
            "bonus_points",
            "kicker_points",
            "dst_points",
            "total_fantasy_points",
        ):
            self.assertIn(key, breakdown)

    def test_ppr_ordering_for_receptions(self):
        row = self.sample_stat_row()
        standard = calculate_fantasy_points(row, get_default_scoring_profile("standard"))
        half_ppr = calculate_fantasy_points(row, get_default_scoring_profile("half_ppr"))
        ppr = calculate_fantasy_points(row, get_default_scoring_profile("ppr"))

        self.assertGreaterEqual(ppr, half_ppr)
        self.assertGreaterEqual(half_ppr, standard)

    def test_input_stat_row_is_not_mutated(self):
        row = self.sample_stat_row()
        original = copy.deepcopy(row)

        calculate_fantasy_breakdown(row, get_default_scoring_profile("ppr"))

        self.assertEqual(row, original)

    def test_breakdown_can_be_json_serialized(self):
        breakdown = calculate_fantasy_breakdown(
            self.sample_stat_row(),
            get_default_scoring_profile("ppr"),
        )

        json.dumps(breakdown, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
