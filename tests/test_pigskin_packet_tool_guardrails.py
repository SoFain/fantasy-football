from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from src import pigskin_context_tools
from src import pigskin_context_qa as qa
from src import pigskin_packet_guardrails as guardrails


class PigskinPacketToolGuardrailTests(unittest.TestCase):
    def test_future_tool_exposure_defaults_disabled(self):
        self.assertFalse(guardrails.historical_packet_tool_enabled())
        self.assertEqual(guardrails.get_historical_packet_tool_declarations(), [])

    def test_enabled_declaration_is_safe_and_not_sql_based(self):
        declarations = guardrails.get_historical_packet_tool_declarations(enabled=True)
        rendered = repr(declarations).lower()

        self.assertEqual(declarations[0]["name"], "get_historical_pigskin_packet_context")
        self.assertIn("season", rendered)
        self.assertIn("season_start", rendered)
        self.assertIn("season_end", rendered)
        self.assertIn("include_postseason", rendered)
        self.assertIn("player_id_internal", rendered)
        self.assertIn("player_name", rendered)
        self.assertIn("anyof", rendered)
        self.assertIn("oneof", rendered)
        self.assertNotIn("sql", rendered)
        self.assertNotIn("raw_nflverse", rendered)
        self.assertNotIn("current_team", rendered)
        self.assertIn("completed-season evidence only", declarations[0]["description"])
        self.assertIn("Does not answer current roster", declarations[0]["description"])

    def test_model_visible_pigskin_tools_do_not_include_future_historical_packet_tool(self):
        names = {tool["name"] for tool in pigskin_context_tools.get_pigskin_context_tool_declarations()}

        self.assertNotIn("get_historical_pigskin_packet_context", names)

    def test_model_visible_pigskin_tools_include_future_tool_only_when_env_enabled(self):
        with patch.dict(os.environ, {"USE_PIGSKIN_HISTORICAL_PACKET_TOOL": "true"}):
            names = {tool["name"] for tool in pigskin_context_tools.get_pigskin_context_tool_declarations()}

        self.assertIn("get_historical_pigskin_packet_context", names)

    def test_dispatcher_executes_future_tool_only_when_env_enabled(self):
        args = {"season": 2025, "player_name": "Tyreek Hill"}
        with self.assertRaises(ValueError):
            pigskin_context_tools.execute_pigskin_context_tool(
                "get_historical_pigskin_packet_context",
                args,
            )

        with patch.dict(os.environ, {"USE_PIGSKIN_HISTORICAL_PACKET_TOOL": "true"}), patch.object(
            guardrails,
            "execute_historical_packet_context_lookup",
            return_value={"status": "ok", "found": True},
        ) as mocked_lookup:
            result = pigskin_context_tools.execute_pigskin_context_tool(
                "get_historical_pigskin_packet_context",
                args,
                client=object(),
                dataset_id="fantasy_football_brain",
            )

        mocked_lookup.assert_called_once()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["result"]["status"], "ok")

    def test_wrapper_rejects_missing_season_or_window(self):
        result = guardrails.execute_historical_packet_context_lookup({"player_name": "T.Hill"})

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "missing_historical_window")
        self.assertTrue(result["current_roster_status_source_required"])

    def test_wrapper_rejects_team_position_only_current_roster_identity(self):
        result = guardrails.execute_historical_packet_context_lookup(
            {"season": 2025, "team": "MIA", "position": "WR"}
        )

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "missing_current_roster_identity")
        self.assertTrue(result["current_roster_status_source_required"])

    def test_wrapper_rejects_arbitrary_sql_arg(self):
        result = guardrails.execute_historical_packet_context_lookup(
            {"season": 2025, "sql_query": "SELECT * FROM raw_nflverse_pbp"}
        )

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "arbitrary_sql_not_allowed")
        self.assertIn("sql_query", result["unsafe_args"])

    def test_wrapper_calls_retrieval_layer_not_bigquery_directly(self):
        qa_result = {
            "status": "ok",
            "found": True,
            "merged_context": {
                "historical_context": {
                    "display_name": "T.Hill",
                    "historical_team": "MIA",
                    "current_team": "MIA",
                    "blocked_metrics": ["route_share"],
                },
                "current_roster_context": {
                    "display_name": "Tyreek Hill",
                    "current_team": None,
                    "current_roster_source": "sleeper_players_current",
                },
            },
            "historical_team": "MIA",
            "current_team": None,
            "warnings": [],
        }

        with patch.object(qa, "build_historical_packet_current_roster_context", return_value=qa_result) as mocked_qa:
            result = guardrails.execute_historical_packet_context_lookup(
                {"season": 2025, "player_name": "T.Hill", "team": "MIA", "position": "WR"},
                client=object(),
                dataset_id="fantasy_football_brain",
            )

        mocked_qa.assert_called_once()
        packet_request, current_roster_request = mocked_qa.call_args.args[:2]
        self.assertEqual(packet_request["season"], 2025)
        self.assertEqual(packet_request["team"], "MIA")
        self.assertEqual(packet_request["position"], "WR")
        self.assertEqual(current_roster_request["player_name"], "T.Hill")
        self.assertNotIn("team", current_roster_request)
        self.assertNotIn("position", current_roster_request)
        self.assertEqual(result["merged_context"]["historical_context"]["historical_team"], "MIA")
        self.assertNotIn("current_team", result["merged_context"]["historical_context"])
        self.assertIsNone(result["current_team"])
        self.assertIn("Sleeper/current roster", result["current_roster_status_policy"])

    def test_wrapper_preserves_ambiguity_candidates(self):
        qa_result = {
            "status": "ambiguous",
            "found": False,
            "candidate_count": 2,
            "historical_candidates": [
                {"display_name": "T.Hill", "historical_team": "MIA", "historical_position": "WR"},
                {"display_name": "T.Hill", "historical_team": "NO", "historical_position": "TE"},
            ],
            "warnings": ["Player-name lookup matched multiple historical packet identities."],
        }

        with patch.object(qa, "build_historical_packet_current_roster_context", return_value=qa_result):
            result = guardrails.execute_historical_packet_context_lookup(
                {"season": 2025, "player_name": "Tyreek Hill"}
            )

        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["candidate_count"], 2)
        self.assertIn("historical_team", result["historical_candidates"][0])
        for candidate in result["historical_candidates"]:
            self.assertNotIn("current_team", candidate)

    def test_tyreek_hill_policy_does_not_produce_current_status(self):
        qa_result = {
            "status": "ok",
            "found": True,
            "merged_context": {
                "historical_context": {
                    "display_name": "T.Hill",
                    "historical_team": "MIA",
                    "as_of_season": 2025,
                    "as_of_week": 4,
                },
                "current_roster_context": {
                    "display_name": "Tyreek Hill",
                    "current_team": None,
                    "current_roster_status": "Active",
                    "current_roster_source": "sleeper_players_current",
                },
            },
            "historical_team": "MIA",
            "current_team": None,
            "current_roster_status": "Active",
            "warnings": [],
        }

        with patch.object(qa, "build_historical_packet_current_roster_context", return_value=qa_result):
            result = guardrails.execute_historical_packet_context_lookup(
                {"season": 2025, "player_name": "T.Hill", "team": "MIA", "position": "WR"}
            )

        rendered = repr(result).lower()
        self.assertIn("historical_team", rendered)
        self.assertNotIn("free agent", rendered)
        self.assertNotIn("'current_team': 'mia'", rendered)
        self.assertIsNone(result["current_team"])

    def test_blocked_metrics_remain_unavailable_not_zero(self):
        result = guardrails.enforce_historical_packet_result_guardrails(
            {
                "status": "ok",
                "packet": {
                    "historical_team": "SEA",
                    "blocked_metrics": ["route_share"],
                    "blocked_metric_policy": "blocked metrics are unavailable, not zero",
                },
                "warnings": [],
            }
        )

        self.assertEqual(result["packet"]["blocked_metrics"], ["route_share"])
        self.assertEqual(result["blocked_metric_policy"], guardrails.BLOCKED_METRIC_POLICY)

    def test_week_22_policy_requires_explicit_include_postseason(self):
        declarations = guardrails.get_historical_packet_tool_declarations(enabled=True)
        prompt = guardrails.PIGSKIN_HISTORICAL_PACKET_PROMPT_GUARDRAIL

        self.assertIn("include_postseason", repr(declarations))
        self.assertIn("Week 22 is postseason/historical", prompt)
        self.assertIn("unless explicitly requested", prompt)

    def test_no_sleeper_llm_or_prompt_call_path_exists(self):
        source = Path("src/pigskin_packet_guardrails.py").read_text(encoding="utf-8").lower()

        self.assertNotIn("ingest_sleeper", source)
        self.assertNotIn("google.generativeai", source)
        self.assertNotIn("send_message", source)

    def test_prompt_guardrail_text_preserves_historical_current_separation(self):
        prompt = guardrails.PIGSKIN_HISTORICAL_PACKET_PROMPT_GUARDRAIL
        app_text = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("completed-season evidence only", prompt)
        self.assertIn("Treat packet team as historical team", prompt)
        self.assertIn("Never describe packet team as current team", prompt)
        self.assertIn("Current roster/free-agent status must come from Sleeper/current roster source", guardrails.CURRENT_ROSTER_DEFERRAL_POLICY)
        self.assertIn("PIGSKIN_HISTORICAL_PACKET_PROMPT_GUARDRAIL", app_text)
        self.assertNotIn("call `get_historical_pigskin_packet_context`", prompt)


if __name__ == "__main__":
    unittest.main()
