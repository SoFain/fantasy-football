from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from src.compat_flags import USE_PIGSKIN_PACKET_QA_UI, compat_flag_enabled
from src.pigskin_packet_qa_ui import (
    build_pigskin_packet_qa_requests,
    run_pigskin_packet_qa_lookup,
    summarize_pigskin_packet_qa_result,
)


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")


class PigskinPacketQaUiTests(unittest.TestCase):
    def test_qa_ui_flag_defaults_false(self):
        self.assertFalse(compat_flag_enabled(USE_PIGSKIN_PACKET_QA_UI, {}))
        self.assertTrue(compat_flag_enabled(USE_PIGSKIN_PACKET_QA_UI, {USE_PIGSKIN_PACKET_QA_UI: "true"}))

    def test_app_hides_qa_ui_behind_default_off_flag(self):
        self.assertIn("def use_pigskin_packet_qa_ui()", APP_SOURCE)
        self.assertIn("if use_pigskin_packet_qa_ui():", APP_SOURCE)
        self.assertIn("render_pigskin_packet_qa_panel()", APP_SOURCE)
        self.assertNotIn("USE_PIGSKIN_PACKET_QA_UI=true", APP_SOURCE)

    def test_app_qa_ui_has_no_arbitrary_sql_or_llm_call_path(self):
        panel_start = APP_SOURCE.index("def render_pigskin_packet_qa_panel():")
        panel_end = APP_SOURCE.index("@st.cache_data", panel_start)
        panel_source = APP_SOURCE[panel_start:panel_end]

        self.assertNotIn("sql_query", panel_source)
        self.assertNotIn("raw_sql", panel_source)
        self.assertNotIn("create_gemini_model", panel_source)
        self.assertNotIn("generate_content", panel_source)
        self.assertNotIn("run_subprocess_live", panel_source)
        self.assertIn("run_pigskin_packet_qa_lookup", panel_source)
        self.assertIn("Historical team", panel_source)
        self.assertIn("Current team", panel_source)
        self.assertIn("Blocked metrics are unavailable, not zero", panel_source)

    def test_build_requests_splits_historical_and_current_context(self):
        request = build_pigskin_packet_qa_requests(
            {
                "season": 2025,
                "week": 4,
                "player_name": "Tyreek Hill",
                "player_id_internal": "00-0033040",
                "team": "MIA",
                "position": "WR",
                "league_id": "league-1",
                "include_available_players": True,
                "limit": 5,
            }
        )

        self.assertEqual(request["status"], "ok")
        self.assertEqual(request["packet_request"]["team"], "MIA")
        self.assertEqual(request["packet_request"]["position"], "WR")
        self.assertNotIn("team", request["current_roster_request"])
        self.assertNotIn("position", request["current_roster_request"])
        self.assertEqual(request["current_roster_request"]["league_id"], "league-1")
        self.assertTrue(request["current_roster_request"]["include_available_players"])

    def test_build_requests_rejects_sql_like_input(self):
        request = build_pigskin_packet_qa_requests({"season": 2025, "player_name": "Patrick Mahomes", "sql": "select 1"})

        self.assertEqual(request["status"], "validation_error")
        self.assertEqual(request["blocked_reason"], "arbitrary_sql_not_allowed")
        self.assertEqual(request["unsafe_args"], ["sql"])

    def test_run_lookup_uses_deterministic_helper(self):
        helper_result = {
            "status": "ok",
            "historical_team": "KC",
            "current_team": "KC",
            "current_roster_source": "sleeper_players_current",
            "blocked_metrics": ["route_share"],
            "warnings": ["Historical nflverse packet context only."],
        }
        with patch(
            "src.pigskin_packet_qa_ui.build_historical_packet_current_roster_context",
            return_value=helper_result,
        ) as helper:
            summary = run_pigskin_packet_qa_lookup(
                {
                    "season": 2025,
                    "week": 15,
                    "player_name": "Patrick Mahomes",
                    "player_id_internal": "00-0033873",
                    "limit": 5,
                }
            )

        helper.assert_called_once()
        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["historical_team"], "KC")
        self.assertEqual(summary["current_team"], "KC")
        self.assertEqual(summary["current_roster_source"], "sleeper_players_current")
        self.assertIn("route_share", summary["blocked_metrics"])

    def test_tyreek_current_team_null_is_not_filled_from_historical_team(self):
        summary = summarize_pigskin_packet_qa_result(
            {
                "status": "ok",
                "historical_team": "MIA",
                "current_team": None,
                "current_roster_source": "sleeper_players_current",
                "warnings": ["Packet team is historical_team. It is never current_team."],
            }
        )

        self.assertEqual(summary["historical_team"], "MIA")
        self.assertIsNone(summary["current_team"])
        self.assertIn("Packet team is historical_team", summary["warnings"][0])

    def test_ambiguity_candidates_are_preserved(self):
        summary = summarize_pigskin_packet_qa_result(
            {
                "status": "needs_identity_confirmation",
                "blocked_reason": "packet_ambiguous",
                "historical_candidates": [
                    {"display_name": "T.Hill", "historical_team": "MIA"},
                    {"display_name": "T.Hill", "historical_team": "NO"},
                ],
            }
        )

        self.assertEqual(summary["status"], "needs_identity_confirmation")
        self.assertEqual(summary["blocked_reason"], "packet_ambiguous")
        self.assertEqual(len(summary["historical_candidates"]), 2)

    def test_week_22_and_blocked_metric_policy_are_visible(self):
        summary = summarize_pigskin_packet_qa_result(
            {
                "status": "not_found",
                "blocked_reason": "historical_packet_unavailable",
                "warnings": ["Postseason packet rows are excluded by the regular-season cutoff rule."],
                "blocked_metrics": ["route_share"],
            }
        )

        self.assertEqual(summary["blocked_reason"], "historical_packet_unavailable")
        self.assertIn("Postseason packet rows", summary["warnings"][0])
        self.assertEqual(summary["blocked_metric_policy"], "Blocked metrics are unavailable, not zero.")
        self.assertEqual(summary["blocked_metrics"], ["route_share"])


if __name__ == "__main__":
    unittest.main()
