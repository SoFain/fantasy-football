from __future__ import annotations

from pathlib import Path
import unittest

from src import pigskin_current_roster_merge as merge


def historical_packet(**overrides):
    packet = {
        "display_name": "T.Hill",
        "player_id_internal": "00-0032764",
        "historical_team": "MIA",
        "historical_position": "WR",
        "as_of_season": 2025,
        "as_of_week": 18,
        "packet_version": "pigskin_packet_v0",
        "feature_run_id": "feature_2025",
        "source_metric_version": "nflverse_advanced_metrics_v0",
        "source_freshness": {"metrics": {"max_week": 18}},
        "missing_data_flags": {"blocked_metric_flags": ["route_share"]},
        "blocked_metrics": ["route_share"],
        "blocked_metric_policy": "blocked metrics are unavailable, not zero",
        "warnings": ["packet warning"],
        "created_at": "2026-06-30T00:00:00Z",
    }
    packet.update(overrides)
    return {"status": "ok", "found": True, "packet": packet, "warnings": ["result warning"]}


def current_payload(**overrides):
    payload = {
        "player_id_internal": "00-0032764",
        "sleeper_player_id": "1166",
        "display_name": "Tyreek Hill",
        "position": "WR",
        "current_team": "MIA",
        "roster_status": "active",
        "current_roster_source": "sleeper_players_current",
        "snapshot_id": "snap-1",
        "current_roster_as_of": "2026-06-30T01:00:00Z",
    }
    payload.update(overrides)
    return payload


class PigskinCurrentRosterMergeTests(unittest.TestCase):
    def test_historical_team_and_current_team_are_separate_fields(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(),
            current_payload(current_team="KC"),
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["historical_team"], "MIA")
        self.assertEqual(result["current_team"], "KC")
        self.assertTrue(result["team_mismatch"])
        self.assertEqual(result["historical_context"]["historical_team"], "MIA")
        self.assertEqual(result["current_roster_context"]["current_team"], "KC")

    def test_current_team_comes_only_from_current_roster_payload(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(),
            current_payload(current_team="BAL"),
        )

        self.assertEqual(result["current_team"], "BAL")
        self.assertNotEqual(result["current_team"], result["historical_team"])

    def test_packet_current_team_is_stripped_and_not_promoted(self):
        packet_result = historical_packet(current_team="MIA")
        result = merge.merge_historical_packet_with_current_roster(packet_result, None)

        self.assertEqual(result["status"], "current_roster_unavailable")
        self.assertEqual(result["historical_team"], "MIA")
        self.assertIsNone(result["current_team"])
        self.assertNotIn("current_team", result["historical_context"])

    def test_free_agent_current_status_is_preserved_from_current_source(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(),
            current_payload(current_team=None, roster_status="free_agent", free_agent=True),
        )

        self.assertEqual(result["status"], "ok")
        self.assertIsNone(result["current_team"])
        self.assertEqual(result["current_roster_status"], "free_agent")
        self.assertTrue(result["current_roster_context"]["free_agent"])
        self.assertIn("historical packet shows prior usage only", " ".join(result["warnings"]))

    def test_missing_current_roster_does_not_infer_team_from_packet(self):
        result = merge.merge_historical_packet_with_current_roster(historical_packet(), None)

        self.assertEqual(result["status"], "current_roster_unavailable")
        self.assertEqual(result["historical_team"], "MIA")
        self.assertIsNone(result["current_team"])
        self.assertIn("not inferred from packet team", " ".join(result["warnings"]))

    def test_tyreek_hill_2025_miami_packet_plus_current_free_agent_payload(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(display_name="T.Hill", historical_team="MIA"),
            current_payload(
                display_name="Tyreek Hill",
                current_team=None,
                roster_status="free_agent",
                free_agent=True,
                current_roster_source="sleeper_players_current",
            ),
        )

        self.assertEqual(result["historical_team"], "MIA")
        self.assertIsNone(result["current_team"])
        self.assertEqual(result["current_roster_status"], "free_agent")
        self.assertEqual(result["current_roster_source"], "sleeper_players_current")
        self.assertEqual(result["provenance"]["historical_source"], "compat_pigskin_player_context_current")
        self.assertEqual(result["provenance"]["current_roster_source"], "sleeper_players_current")

    def test_identity_mismatch_returns_needs_confirmation(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(),
            current_payload(player_id_internal="00-9999999"),
        )

        self.assertEqual(result["status"], "needs_identity_confirmation")
        self.assertTrue(result["needs_identity_confirmation"])
        self.assertIn("identity does not match", " ".join(result["warnings"]))

    def test_ambiguous_packet_result_is_not_merged(self):
        result = merge.merge_historical_packet_with_current_roster(
            {
                "status": "ambiguous",
                "candidates": [
                    {"display_name": "T.Hill", "historical_team": "MIA"},
                    {"display_name": "T.Hill", "historical_team": "NO"},
                ],
                "warnings": ["ambiguous"],
            },
            current_payload(),
        )

        self.assertEqual(result["status"], "needs_identity_confirmation")
        self.assertTrue(result["needs_identity_confirmation"])
        self.assertEqual(len(result["historical_candidates"]), 2)
        self.assertIsNone(result["current_roster_context"])

    def test_current_roster_multiple_candidates_requires_confirmation(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(),
            {
                "status": "ambiguous",
                "candidates": [
                    {"display_name": "Tyreek Hill", "current_team": "MIA"},
                    {"display_name": "Taysom Hill", "current_team": "NO"},
                ],
            },
        )

        self.assertEqual(result["status"], "needs_identity_confirmation")
        self.assertTrue(result["needs_identity_confirmation"])
        self.assertEqual(len(result["current_roster_candidates"]), 2)

    def test_blocked_metrics_remain_unavailable(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(blocked_metrics=["route_share"]),
            current_payload(),
        )

        self.assertEqual(result["blocked_metrics"], ["route_share"])
        self.assertEqual(result["blocked_metric_policy"], merge.BLOCKED_METRIC_POLICY)

    def test_packet_warnings_and_source_freshness_are_preserved(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(),
            current_payload(warnings=["current stale warning"]),
        )

        self.assertIn("packet warning", result["packet_warnings"])
        self.assertIn("current stale warning", result["warnings"])
        self.assertEqual(result["source_freshness"], {"metrics": {"max_week": 18}})
        self.assertEqual(result["missing_data_flags"], {"blocked_metric_flags": ["route_share"]})

    def test_week_22_postseason_context_is_preserved(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(as_of_week=22),
            current_payload(),
        )

        self.assertEqual(result["packet_as_of_week"], 22)
        self.assertIn("Week 22", result["postseason_policy"])

    def test_no_current_roster_payload_keeps_status_unavailable(self):
        result = merge.merge_historical_packet_with_current_roster(historical_packet(), {})

        self.assertEqual(result["status"], "current_roster_unavailable")
        self.assertIsNone(result["current_roster_context"])
        self.assertIsNone(result["current_team"])

    def test_arbitrary_sql_is_rejected(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(),
            {"sql_query": "SELECT * FROM sleeper_players_current"},
        )

        self.assertEqual(result["status"], "validation_error")
        self.assertEqual(result["blocked_reason"], "arbitrary_sql_not_allowed")
        self.assertIn("sql_query", result["unsafe_args"])

    def test_weak_identity_returns_warning_not_current_guess(self):
        result = merge.merge_historical_packet_with_current_roster(
            historical_packet(),
            {"display_name": "Tyreek Hill", "current_team": "MIA", "source": "manual_fixture"},
        )

        self.assertEqual(result["status"], "ok")
        self.assertIn("lacks a stable ID match", " ".join(result["warnings"]))

    def test_no_sleeper_api_llm_bigquery_write_or_pigskin_call_path_exists(self):
        source = Path("src/pigskin_current_roster_merge.py").read_text(encoding="utf-8").lower()

        self.assertNotIn("sleeper_get", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("google.generativeai", source)
        self.assertNotIn("execute_pigskin_context_tool", source)
        self.assertNotIn(".query(", source)
        self.assertNotIn("load_table", source)
        self.assertNotIn("insert_rows", source)


if __name__ == "__main__":
    unittest.main()
