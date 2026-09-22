import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.build_sleeper_current_player_context import build_context_rows, load_players

ROOT = Path(__file__).resolve().parents[1]
VIEW_SQL = (ROOT / "bigquery" / "views" / "v_rb_fable_v1_current_context_review.sql").read_text()


class SleeperContextRowsTest(unittest.TestCase):
    def test_build_context_rows_extracts_required_fields(self):
        fetched_at = datetime(2026, 7, 10, tzinfo=timezone.utc)
        players = {
            "4034": {
                "full_name": "Christian McCaffrey", "first_name": "Christian", "last_name": "McCaffrey",
                "search_full_name": "christianmccaffrey", "gsis_id": " 00-0033280", "team": "SF",
                "position": "RB", "fantasy_positions": ["RB"], "status": "Active", "injury_status": None,
                "depth_chart_position": "RB", "depth_chart_order": 1, "years_exp": 9, "age": 30, "active": True,
            },
            "bad": "not-a-dict",
        }
        rows = build_context_rows(players, fetched_at=fetched_at)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["sleeper_player_id"], "4034")
        self.assertEqual(row["gsis_id"], "00-0033280")  # whitespace stripped
        self.assertEqual(row["depth_chart_order"], 1)
        self.assertEqual(len(row["raw_payload_hash"]), 64)
        self.assertTrue(row["fetched_at"].startswith("2026-07-10"))

    def test_cache_is_preferred_over_network(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            cache.write_text(json.dumps({
                "fetched_at": "2026-07-10T00:00:00+00:00",
                "source_url": "https://api.sleeper.app/v1/players/nfl",
                "players": {"1": {"full_name": "Test Back", "position": "RB"}},
            }), encoding="utf-8")
            players, fetched_at, origin = load_players(cache, refresh=False)
            self.assertEqual(origin, "cache")
            self.assertEqual(list(players), ["1"])
            self.assertEqual(fetched_at.year, 2026)


class ContextReviewSqlTest(unittest.TestCase):
    def test_required_context_flags_present(self):
        for flag in (
            "FABLE_SCORE_TRUSTED", "STALE_TEAM_CONTEXT", "CURRENT_TEAM_MISMATCH",
            "CURRENT_ROLE_REVIEW_REQUIRED", "NO_QUALIFIED_FABLE_ROW", "SLEEPER_ID_MISSING",
            "SLEEPER_DEPTH_CHART_WARNING", "INJURY_STATUS_WARNING", "MANUAL_REVIEW_REQUIRED",
        ):
            self.assertIn(flag, VIEW_SQL)

    def test_join_priority_and_identity_methods(self):
        for method in ("STANDARD_BOARD_SLEEPER_ID", "SLEEPER_GSIS_BRIDGE", "NORMALIZED_NAME_TEAM_FALLBACK", "NO_SLEEPER_MATCH"):
            self.assertIn(method, VIEW_SQL)

    def test_review_only_and_no_formula_or_leakage_contamination(self):
        # The view must not recompute or alter the Fable score and must stay off 2026 outcomes.
        self.assertNotIn("2026", VIEW_SQL)
        self.assertNotIn("rb_fable_01_score +", VIEW_SQL)
        self.assertNotIn("* rb_fable_01_score", VIEW_SQL)
        self.assertIn("season = 2025", VIEW_SQL)
        self.assertIn("evidence layer", VIEW_SQL.lower())


if __name__ == "__main__":
    unittest.main()
