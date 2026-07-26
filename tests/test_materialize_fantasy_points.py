from __future__ import annotations

import unittest

import pandas as pd

from src.fantasy_scoring import get_gng_keeper_scoring_profile
from src.materialize_fantasy_points import (
    build_fantasy_point_rows,
    build_historical_nflverse_stat_sql,
    validate_complete_scoring_source,
)


class MaterializeFantasyPointsTests(unittest.TestCase):
    def test_gng_keeper_rows_apply_position_reception_bonus(self):
        stat_frame = pd.DataFrame([
            {
                "source_player_key": "te-1",
                "player_display_name": "Test Tight End",
                "team": "KC",
                "opponent": "LV",
                "position": "TE",
                "season": 2025,
                "week": 4,
                "receptions": 1,
            },
            {
                "source_player_key": "wr-1",
                "player_display_name": "Test Wideout",
                "team": "MIA",
                "opponent": "NE",
                "position": "WR",
                "season": 2025,
                "week": 4,
                "receptions": 1,
            },
            {
                "source_player_key": "rb-1",
                "player_display_name": "Test Back",
                "team": "ATL",
                "opponent": "CAR",
                "position": "RB",
                "season": 2025,
                "week": 4,
                "receptions": 1,
            },
        ])

        rows = build_fantasy_point_rows(
            stat_frame,
            {"gng_keeper": get_gng_keeper_scoring_profile()},
            source_table="analytics_player_weekly_truth",
        )

        points_by_key = {row["source_player_key"]: row["reception_points"] for row in rows}
        self.assertAlmostEqual(points_by_key["te-1"], 0.3)
        self.assertAlmostEqual(points_by_key["wr-1"], 0.2)
        self.assertAlmostEqual(points_by_key["rb-1"], 0.1)
        self.assertEqual({row["scoring_profile_id"] for row in rows}, {"gng_keeper"})

    def test_historical_nflverse_sql_uses_raw_payload_required_fields(self):
        sql, parameters = build_historical_nflverse_stat_sql(
            "project",
            "dataset",
            season_start=2015,
            season_end=2024,
            week_start=1,
            week_end=18,
            positions=("QB", "RB"),
        )

        self.assertIn("raw_nflverse_weekly", sql)
        self.assertIn("stg_player_week_stats", sql)
        self.assertIn("$.passing_interceptions", sql)
        self.assertIn("$.rushing_2pt_conversions", sql)
        self.assertIn("$.receiving_fumbles_lost", sql)
        self.assertIn("$.sacks_suffered", sql)
        self.assertIn("JSON_VALUE(w.raw_payload_json, '$.season_type') = 'REG'", sql)
        self.assertNotIn("analytics_player_weekly_truth", sql)
        parameter_names = {parameter.name for parameter in parameters}
        self.assertEqual(parameter_names, {"season_start", "season_end", "positions", "week_start", "week_end"})

    def test_historical_source_validation_fails_for_missing_required_stats(self):
        frame = pd.DataFrame([
            {
                "passing_yards": 100,
                "passing_tds": 1,
                "rushing_yards": 10,
                "rushing_tds": 0,
                "receptions": 3,
                "receiving_yards": 20,
                "receiving_tds": 0,
            }
        ])

        result = validate_complete_scoring_source(frame, scoring_profile_ids=("ppr",))

        self.assertFalse(result["complete"])
        self.assertIn("interceptions", result["missing_field_counts"])
        self.assertIn("fumbles_lost", result["missing_field_counts"])

    def test_historical_source_validation_requires_gng_supplemental_stats(self):
        frame = pd.DataFrame([
            {
                "passing_yards": 100,
                "passing_tds": 1,
                "interceptions": 0,
                "passing_2pt_conversions": 0,
                "rushing_yards": 10,
                "rushing_tds": 0,
                "rushing_2pt_conversions": 0,
                "receptions": 3,
                "receiving_yards": 20,
                "receiving_tds": 0,
                "receiving_2pt_conversions": 0,
                "fumbles_lost": 0,
                "return_tds": 0,
            }
        ])

        result = validate_complete_scoring_source(frame, scoring_profile_ids=("gng_keeper",))

        self.assertFalse(result["complete"])
        self.assertIn("sacks_taken", result["missing_field_counts"])
        self.assertIn("rushing_first_downs", result["missing_field_counts"])


if __name__ == "__main__":
    unittest.main()
