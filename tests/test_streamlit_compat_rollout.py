from __future__ import annotations

import re
import unittest
from pathlib import Path

from src.compat_flags import (
    COMPAT_FLAG_NAMES,
    USE_COMPAT_PLAYER_PROFILES,
    USE_COMPAT_SLEEPER_WATCH,
    USE_COMPAT_TRADE_ASSETS,
    USE_COMPAT_TRADE_PLAYER_HISTORY,
    USE_COMPAT_VIEWER_TEAM_CONTEXT,
    compat_flag_enabled,
)
from src.player_profiles import build_player_profiles_list_query


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")

RAW_SOURCE_TERMS = (
    "weekly_metrics",
    "play_by_play",
    "ngs_passing",
    "ngs_rushing",
    "ngs_receiving",
    "ftn_charting",
    "weekly_snap_counts",
    "injury_reports",
    "player_rosters",
    "player_contracts",
    "depth_charts",
    "market_values",
    "sleeper_viewer_team_snapshots",
    "sleeper_roster_players",
    "sleeper_lineups",
    "sleeper_available_players",
)


class StreamlitCompatRolloutTests(unittest.TestCase):
    def test_flags_default_false(self):
        empty_env = {}

        for flag_name in COMPAT_FLAG_NAMES:
            self.assertFalse(compat_flag_enabled(flag_name, empty_env))

    def test_flags_enable_from_env(self):
        for flag_name in COMPAT_FLAG_NAMES:
            self.assertTrue(compat_flag_enabled(flag_name, {flag_name: "true"}))
            self.assertTrue(compat_flag_enabled(flag_name, {flag_name: "1"}))
            self.assertFalse(compat_flag_enabled(flag_name, {flag_name: "false"}))

    def test_app_has_default_off_compat_branches(self):
        expected = {
            USE_COMPAT_PLAYER_PROFILES: ("use_compat_player_profiles()", "fetch_compat_player_profiles_data"),
            USE_COMPAT_SLEEPER_WATCH: ("use_compat_sleeper_watch()", "fetch_compat_sleeper_watch_candidates_data"),
            USE_COMPAT_TRADE_ASSETS: ("use_compat_trade_assets()", "load_compat_trade_assets"),
            USE_COMPAT_TRADE_PLAYER_HISTORY: ("use_compat_trade_player_history()", "query_compat_trade_player_history"),
            USE_COMPAT_VIEWER_TEAM_CONTEXT: ("use_compat_viewer_team_context()", "get_compat_sleeper_viewer_team_context"),
        }

        for flag_name, snippets in expected.items():
            self.assertIn(flag_name, APP_SOURCE)
            for snippet in snippets:
                self.assertIn(snippet, APP_SOURCE)

    def test_legacy_paths_remain_available(self):
        legacy_terms = (
            "market_values",
            "weekly_metrics",
            "player_rosters",
            "sleeper_viewer_team_snapshots",
        )

        for term in legacy_terms:
            self.assertIn(term, APP_SOURCE)

    def test_compat_helper_functions_do_not_reference_raw_sources(self):
        helper_names = (
            "fetch_compat_player_profiles_data",
            "fetch_compat_sleeper_watch_candidates_data",
            "load_compat_trade_assets",
            "query_compat_trade_player_history",
            "get_compat_sleeper_viewer_team_context",
        )

        for helper_name in helper_names:
            body = self._top_level_function_body(helper_name)
            for raw_term in RAW_SOURCE_TERMS:
                self.assertNotIn(raw_term, body, f"{helper_name} references {raw_term}")

    def test_missing_compat_data_messages_are_clean(self):
        self.assertIn("compatibility data is unavailable or empty", APP_SOURCE)
        self.assertIn("compatibility context is unavailable", APP_SOURCE)
        self.assertIn("No legacy viewer-team context was mixed into this flagged path.", APP_SOURCE)

    def test_trade_history_staging_marker_is_visible(self):
        self.assertIn("Trade player history source: compat_trade_player_history", APP_SOURCE)
        self.assertIn("render_compat_metadata(hist", APP_SOURCE)

    def test_player_profiles_list_query_uses_compat_view(self):
        sql, job_config = build_player_profiles_list_query(
            project_id="fantasy-football-498121",
            dataset_id="fantasy_football_brain",
            limit=50,
        )

        self.assertIn("compat_player_profiles_current", sql)
        for raw_term in RAW_SOURCE_TERMS:
            self.assertNotIn(raw_term, sql)
        self.assertEqual(
            {param.name: param.value for param in job_config.query_parameters}["limit"],
            50,
        )

    def _top_level_function_body(self, function_name: str) -> str:
        match = re.search(
            rf"^def {re.escape(function_name)}\(.*?^def ",
            APP_SOURCE,
            flags=re.DOTALL | re.MULTILINE,
        )
        if match:
            return match.group(0)[:-4]
        match = re.search(
            rf"^def {re.escape(function_name)}\(.*\Z",
            APP_SOURCE,
            flags=re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(match, f"{function_name} not found")
        return match.group(0)


if __name__ == "__main__":
    unittest.main()
