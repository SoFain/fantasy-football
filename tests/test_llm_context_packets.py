from __future__ import annotations

import json
import unittest

from src import llm_context_packets, materialize_llm_packets
from src.materialize_llm_packets import SourceTableStatus


class FakeJob:
    def __init__(self, rows=None):
        self.rows = rows or []

    def result(self):
        return self.rows


class FakeClient:
    project = "test-project"

    def __init__(self, rows=None):
        self.rows = rows or []
        self.query_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return FakeJob(self.rows)


class LlmContextPacketTests(unittest.TestCase):
    def test_packet_query_uses_packet_view_and_parameters(self):
        sql, job_config = llm_context_packets.build_player_context_packet_query(
            project_id="test-project",
            dataset_id="test_dataset",
            player_name="A.J. Brown",
            scoring_profile_id="ppr",
        )

        self.assertIn("llm_player_context_packet", sql)
        for raw_table in DISALLOWED_TABLES:
            self.assertNotIn(raw_table, sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "ppr")
        self.assertEqual(params["normalized_name"], "ajbrown")

    def test_search_limit_is_clamped(self):
        _, job_config = llm_context_packets.build_search_context_packets_query(
            project_id="test-project",
            dataset_id="test_dataset",
            query="Brock",
            limit=1000,
        )

        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["limit"], llm_context_packets.MAX_LIMIT)

    def test_ranked_query_filters_profile_context(self):
        sql, job_config = llm_context_packets.build_ranked_context_packets_query(
            project_id="test-project",
            dataset_id="test_dataset",
            position="QB",
            scoring_profile_id="half_ppr",
            league_type_id="dynasty",
            roster_format_id="superflex",
        )

        self.assertIn("@position", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["position"], "QB")
        self.assertEqual(params["scoring_profile_id"], "half_ppr")
        self.assertEqual(params["league_type_id"], "dynasty")
        self.assertEqual(params["roster_format_id"], "superflex")

    def test_missing_packet_returns_clean_response(self):
        client = FakeClient(rows=[])

        result = llm_context_packets.get_player_context_packet(
            player_name="Missing Player",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertFalse(result["found"])
        self.assertIn("packet_not_found", result["missing_data_flags"])
        self.assertIn("No LLM player context packet found", result["packet_text"])

    def test_normalize_packet_returns_required_top_level_keys_and_bounds_text(self):
        long_text = "x" * 9000
        row = {
            "packet_id": "packet-1",
            "model_run_id": "run-1",
            "ranking_version": "rank-v1",
            "player_id_internal": "pid-1",
            "source_player_key": "gsis-1",
            "display_name": "Example Player",
            "position": "WR",
            "team": "PIT",
            "scoring_profile_id": "ppr",
            "league_type_id": "redraft",
            "roster_format_id": "one_qb",
            "as_of_season": 2026,
            "as_of_week": 1,
            "packet_json": json.dumps({"identity": {"display_name": "Example Player"}}),
            "packet_text": long_text,
            "token_estimate": None,
            "source_freshness_json": "{}",
            "missing_data_flags": "[]",
        }

        result = llm_context_packets.normalize_packet_for_llm(row)

        self.assertTrue(result["found"])
        self.assertLessEqual(len(result["packet_text"]), llm_context_packets.PACKET_TEXT_LIMIT)
        for key in llm_context_packets.REQUIRED_PACKET_KEYS:
            self.assertIn(key, result["packet_json"])

    def test_materializer_sql_uses_allowed_sources_only(self):
        status = {
            table_name: SourceTableStatus(False, frozenset())
            for table_name in materialize_llm_packets.OPTIONAL_CONTEXT_TABLES
        }

        sql = materialize_llm_packets.build_llm_packets_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=status,
        )

        self.assertIn("mart_llm_player_context_packet", sql)
        self.assertIn("compat_player_profiles_current", sql)
        self.assertIn("compat_trade_player_history", sql)
        self.assertIn("model_runs", sql)
        for raw_table in DISALLOWED_TABLES:
            self.assertNotIn(raw_table, sql)

    def test_unsafe_dataset_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            materialize_llm_packets.build_llm_packets_sql(
                project_id="test-project",
                dataset_id="bad.dataset",
            )


DISALLOWED_TABLES = (
    "weekly_metrics",
    "play_by_play",
    "player_rosters",
    "player_contracts",
    "depth_charts",
    "team_descriptions",
    "ngs_passing",
    "ngs_rushing",
    "ngs_receiving",
    "ftn_charting",
    "weekly_snap_counts",
    "injury_reports",
)


if __name__ == "__main__":
    unittest.main()
