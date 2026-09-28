import unittest
import pandas as pd
from scripts.refresh_current_season_stats import validate_source
from src.public_rankings_feed import _attach_player_context


class SourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame([dict(player_id="p1", season=2026, week=2, season_type="REG", team="BUF", game_id="g1")])

    def test_valid_source(self):
        validate_source(self.frame, 2026)

    def test_preserves_upstream_team_rows_without_player_id(self):
        validate_source(self.frame.assign(player_id=None), 2026)

    def test_rejects_empty_wrong_season_duplicate_and_null(self):
        for frame in [self.frame.iloc[:0], self.frame.assign(season=2025), pd.concat([self.frame, self.frame]), self.frame.assign(game_id=None), self.frame.assign(week=23)]:
            with self.subTest(frame=frame.to_dict("records")), self.assertRaises(ValueError):
                validate_source(frame, 2026)

    def test_current_stats_preserve_preseason_metrics_and_unknowns(self):
        current = dict(season=2026, through_week=2, games=2, stats={"targets": 13})
        default = dict(season=2026, through_week=None, games=None, stats={})
        context = {"p1": {"metrics": {"games": 17}, "current_season": current}, "__current_season_default__": default}
        player = {}
        _attach_player_context(player, context, "p1")
        self.assertEqual(player["metrics"]["games"], 17)
        self.assertEqual(player["current_season"], current)
        absent = {}
        _attach_player_context(absent, context, "unknown")
        self.assertIsNone(absent["current_season"]["games"])
