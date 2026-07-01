from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from src import pigskin_context_qa as qa


def packet_result(**packet_overrides):
    packet = {
        "display_name": "T.Hill",
        "player_id_internal": "00-0032764",
        "sleeper_player_id": "1166",
        "historical_team": "MIA",
        "historical_position": "WR",
        "as_of_season": 2025,
        "as_of_week": 18,
        "packet_version": "pigskin_packet_v0",
        "feature_run_id": "feature_2025",
        "source_metric_version": "nflverse_advanced_metrics_v0",
        "source_freshness": {"advanced_metrics": {"max_week": 18}},
        "missing_data_flags": {"blocked_metric_flags": ["route_share"]},
        "blocked_metrics": ["route_share"],
        "warnings": ["packet warning"],
    }
    packet.update(packet_overrides)
    return {
        "status": "ok",
        "found": True,
        "source": "compat_pigskin_player_context_current",
        "warnings": ["historical packet warning"],
        "packet": packet,
        "packets": [packet],
    }


def current_result(**context_overrides):
    context = {
        "player_id_internal": "00-0032764",
        "sleeper_player_id": "1166",
        "display_name": "Tyreek Hill",
        "position": "WR",
        "current_team": "MIA",
        "current_roster_status": "active",
        "current_roster_source": "sleeper_players_current",
        "current_roster_as_of": "2026-06-30T00:00:00Z",
        "source_freshness_json": {"sleeper_players_current_snapshot_at": "2026-06-30T00:00:00Z"},
        "missing_data_flags": {"flags": []},
    }
    context.update(context_overrides)
    return {
        "status": "ok",
        "found": True,
        "source": "pigskin_current_roster_lookup",
        "warnings": ["current roster warning"],
        "current_roster_context": context,
        "candidate_count": 1,
        "needs_identity_confirmation": False,
    }


class PigskinContextQaTests(unittest.TestCase):
    def test_rejects_arbitrary_sql_keys_before_any_helper_call(self):
        with patch.object(qa, "retrieve_historical_pigskin_packets") as retrieve, patch.object(
            qa,
            "lookup_current_roster_context",
        ) as lookup:
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "sql_query": "SELECT * FROM raw_nflverse_pbp"},
                {"sleeper_player_id": "1166"},
            )

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "arbitrary_sql_not_allowed")
        self.assertIn("packet_request.sql_query", result["unsafe_args"])
        retrieve.assert_not_called()
        lookup.assert_not_called()

    def test_rejects_arbitrary_sql_key_in_current_roster_request(self):
        with patch.object(qa, "retrieve_historical_pigskin_packets") as retrieve:
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025},
                {"sleeper_player_id": "1166", "raw_sql": "SELECT 1"},
            )

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "arbitrary_sql_not_allowed")
        self.assertIn("current_roster_request.raw_sql", result["unsafe_args"])
        retrieve.assert_not_called()

    def test_rejects_missing_historical_season_or_window(self):
        result = qa.build_historical_packet_current_roster_context(
            {"player_id_internal": "00-0032764"},
            {"sleeper_player_id": "1166"},
        )

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "missing_historical_season_window")

    def test_rejects_missing_current_roster_identity_before_packet_lookup(self):
        with patch.object(qa, "retrieve_historical_pigskin_packets") as retrieve, patch.object(
            qa,
            "lookup_current_roster_context",
        ) as lookup:
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"team": "MIA", "position": "WR"},
            )

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "missing_current_roster_identity")
        retrieve.assert_not_called()
        lookup.assert_not_called()

    def test_packet_retrieval_is_called_with_explicit_historical_bounds(self):
        with patch.object(
            qa,
            "retrieve_historical_pigskin_packets",
            return_value=packet_result(),
        ) as retrieve, patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(),
        ) as lookup:
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "week": 18, "player_id_internal": "00-0032764"},
                {"sleeper_player_id": "1166"},
                client="client",
                dataset_id="dataset",
            )

        self.assertEqual(result["status"], "ok")
        retrieve.assert_called_once_with(
            client="client",
            dataset_id="dataset",
            season=2025,
            week=18,
            player_id_internal="00-0032764",
        )
        lookup.assert_called_once_with(
            client="client",
            dataset_id="dataset",
            sleeper_player_id="1166",
        )

    def test_current_lookup_is_called_with_bounded_identity_input(self):
        with patch.object(qa, "retrieve_historical_pigskin_packets", return_value=packet_result()), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(),
        ) as lookup:
            qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"player_id_internal": "00-0032764", "limit": 5},
            )

        lookup.assert_called_once()
        self.assertEqual(lookup.call_args.kwargs["player_id_internal"], "00-0032764")
        self.assertEqual(lookup.call_args.kwargs["limit"], 5)

    def test_merge_is_called_only_when_both_results_are_deterministic(self):
        merge_result = {"status": "ok", "historical_context": {}, "warnings": []}
        with patch.object(qa, "retrieve_historical_pigskin_packets", return_value=packet_result()), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(),
        ), patch.object(
            qa,
            "merge_historical_packet_with_current_roster",
            Mock(return_value=merge_result),
        ) as merge:
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"sleeper_player_id": "1166"},
            )

        self.assertFalse(result["merge_blocked"])
        merge.assert_called_once()

    def test_ambiguous_packet_result_returns_candidates_and_does_not_merge(self):
        ambiguous_packet = {
            "status": "ambiguous",
            "found": False,
            "warnings": ["ambiguous packet"],
            "candidates": [
                {"display_name": "T.Hill", "historical_team": "MIA"},
                {"display_name": "T.Hill", "historical_team": "NO"},
            ],
        }
        with patch.object(
            qa,
            "retrieve_historical_pigskin_packets",
            return_value=ambiguous_packet,
        ), patch.object(
            qa,
            "lookup_current_roster_context",
        ) as lookup, patch.object(
            qa,
            "merge_historical_packet_with_current_roster",
        ) as merge:
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_name": "T.Hill"},
                {"sleeper_player_id": "1166"},
            )

        self.assertEqual(result["status"], "needs_identity_confirmation")
        self.assertEqual(result["blocked_reason"], "packet_ambiguous")
        self.assertEqual(len(result["historical_candidates"]), 2)
        lookup.assert_not_called()
        merge.assert_not_called()

    def test_ambiguous_current_roster_result_returns_candidates_and_does_not_merge(self):
        ambiguous_current = {
            "status": "ambiguous",
            "found": False,
            "warnings": ["ambiguous current roster"],
            "needs_identity_confirmation": True,
            "candidates": [
                {"display_name": "Tyreek Hill", "current_team": "MIA"},
                {"display_name": "Taysom Hill", "current_team": "NO"},
            ],
        }
        with patch.object(qa, "retrieve_historical_pigskin_packets", return_value=packet_result()), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=ambiguous_current,
        ), patch.object(
            qa,
            "merge_historical_packet_with_current_roster",
        ) as merge:
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"player_name": "T.Hill", "limit": 10},
            )

        self.assertEqual(result["status"], "needs_identity_confirmation")
        self.assertEqual(result["blocked_reason"], "current_roster_ambiguous")
        self.assertEqual(len(result["current_roster_candidates"]), 2)
        merge.assert_not_called()

    def test_missing_current_roster_merges_as_unavailable_without_packet_team_inference(self):
        with patch.object(qa, "retrieve_historical_pigskin_packets", return_value=packet_result()), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value={
                "status": "not_found",
                "found": False,
                "source": "pigskin_current_roster_lookup",
                "warnings": ["No approved current roster source matched."],
            },
        ):
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"sleeper_player_id": "999999"},
            )

        self.assertEqual(result["status"], "current_roster_unavailable")
        self.assertEqual(result["historical_team"], "MIA")
        self.assertIsNone(result["current_team"])
        self.assertIn("not inferred from packet team", " ".join(result["warnings"]))

    def test_tyreek_hill_historical_miami_packet_keeps_current_context_separate(self):
        with patch.object(
            qa,
            "retrieve_historical_pigskin_packets",
            return_value=packet_result(display_name="T.Hill", historical_team="MIA"),
        ), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(current_team="LV", current_roster_status="active"),
        ):
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "week": 18, "player_id_internal": "00-0032764", "team": "MIA"},
                {"sleeper_player_id": "1166"},
            )

        self.assertEqual(result["historical_team"], "MIA")
        self.assertEqual(result["current_team"], "LV")
        self.assertTrue(result["team_mismatch"])
        self.assertEqual(result["merged_context"]["historical_context"]["historical_team"], "MIA")
        self.assertEqual(result["merged_context"]["current_roster_context"]["current_team"], "LV")

    def test_current_team_is_sourced_only_from_current_roster_result(self):
        with patch.object(
            qa,
            "retrieve_historical_pigskin_packets",
            return_value=packet_result(current_team="MIA"),
        ), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(current_team="BAL"),
        ):
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"sleeper_player_id": "1166"},
            )

        self.assertEqual(result["historical_team"], "MIA")
        self.assertEqual(result["current_team"], "BAL")
        self.assertNotIn("current_team", result["merged_context"]["historical_context"])

    def test_historical_team_is_sourced_only_from_packet_result(self):
        with patch.object(
            qa,
            "retrieve_historical_pigskin_packets",
            return_value=packet_result(historical_team="MIA"),
        ), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(current_team="KC"),
        ):
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"sleeper_player_id": "1166"},
            )

        self.assertEqual(result["merged_context"]["historical_context"]["historical_team"], "MIA")
        self.assertEqual(result["merged_context"]["current_roster_context"]["current_team"], "KC")

    def test_available_player_status_is_preserved_from_current_roster_source(self):
        with patch.object(qa, "retrieve_historical_pigskin_packets", return_value=packet_result()), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(
                current_team=None,
                current_roster_status="available",
                fantasy_availability="available",
                free_agent=True,
                current_roster_source="sleeper_available_players",
            ),
        ):
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"sleeper_player_id": "1166", "league_id": "123", "include_available_players": True},
            )

        self.assertIsNone(result["current_team"])
        self.assertEqual(result["current_roster_status"], "available")
        self.assertEqual(result["current_roster_source"], "sleeper_available_players")

    def test_team_mismatch_produces_provenance_and_warning(self):
        with patch.object(qa, "retrieve_historical_pigskin_packets", return_value=packet_result()), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(current_team="KC"),
        ):
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"sleeper_player_id": "1166"},
            )

        self.assertTrue(result["team_mismatch"])
        self.assertEqual(result["provenance"]["historical_source"], "compat_pigskin_player_context_current")
        self.assertEqual(result["provenance"]["current_roster_source"], "sleeper_players_current")
        self.assertIn("Historical team and current roster team differ", " ".join(result["warnings"]))

    def test_blocked_metrics_remain_unavailable(self):
        with patch.object(
            qa,
            "retrieve_historical_pigskin_packets",
            return_value=packet_result(blocked_metrics=["route_share", "pressure_rate"]),
        ), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(),
        ):
            result = qa.build_historical_packet_current_roster_context(
                {"season": 2025, "player_id_internal": "00-0032764"},
                {"sleeper_player_id": "1166"},
            )

        self.assertEqual(result["blocked_metrics"], ["route_share", "pressure_rate"])
        self.assertEqual(result["source_freshness"], {"advanced_metrics": {"max_week": 18}})
        self.assertEqual(result["missing_data_flags"], {"blocked_metric_flags": ["route_share"]})

    def test_week_22_context_is_preserved_when_postseason_requested(self):
        with patch.object(
            qa,
            "retrieve_historical_pigskin_packets",
            return_value=packet_result(as_of_week=22),
        ), patch.object(
            qa,
            "lookup_current_roster_context",
            return_value=current_result(),
        ):
            result = qa.build_historical_packet_current_roster_context(
                {
                    "season": 2025,
                    "week": 22,
                    "include_postseason": True,
                    "player_id_internal": "00-0032764",
                },
                {"sleeper_player_id": "1166"},
            )

        self.assertEqual(result["packet_as_of_week"], 22)
        self.assertEqual(result["packet_result"]["packet"]["as_of_week"], 22)
        self.assertIn("Week 22", result["merged_context"]["postseason_policy"])

    def test_no_sleeper_api_pigskin_llm_bigquery_write_or_tool_registration_exists(self):
        source = Path("src/pigskin_context_qa.py").read_text(encoding="utf-8").lower()

        self.assertNotIn("requests.", source)
        self.assertNotIn("ingest_sleeper", source)
        self.assertNotIn("google.generativeai", source)
        self.assertNotIn("execute_pigskin_context_tool", source)
        self.assertNotIn("function_declarations", source)
        self.assertNotIn("get_pigskin_context_tool_declarations", source)
        self.assertNotIn(".query(", source)
        self.assertNotIn("load_table", source)
        self.assertNotIn("insert_rows", source)


if __name__ == "__main__":
    unittest.main()
