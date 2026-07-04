from __future__ import annotations

import unittest

import pandas as pd

from src.fantasy_scoring import get_gng_keeper_scoring_profile
from src.materialize_fantasy_points import build_fantasy_point_rows


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


if __name__ == "__main__":
    unittest.main()
