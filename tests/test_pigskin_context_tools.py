from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from src import pigskin_context_tools as tools


class FakeJob:
    def __init__(self, rows):
        self._rows = rows

    def result(self):
        return self._rows


class FakeClient:
    project = "fantasy-football-498121"

    def __init__(self, rows=None):
        self.rows = rows or []
        self.calls = []

    def query(self, sql, job_config=None):
        self.calls.append((sql, job_config))
        return FakeJob(self.rows)


class PigskinContextToolTests(unittest.TestCase):
    def test_declarations_do_not_expose_sql_or_raw_tables(self):
        declarations = tools.get_pigskin_context_tool_declarations()
        names = {declaration["name"] for declaration in declarations}
        rendered = json.dumps(declarations)

        self.assertNotIn("execute_bigquery_sql", names)
        self.assertNotIn("sql_query", rendered)
        self.assertNotIn("weekly_metrics", rendered)
        self.assertNotIn("play_by_play", rendered)

    def test_unknown_tool_is_rejected(self):
        with self.assertRaises(ValueError):
            tools.execute_pigskin_context_tool("execute_bigquery_sql", {"sql_query": "SELECT 1"})

    def test_rankings_slice_uses_parameters_and_byte_cap(self):
        client = FakeClient(
            rows=[
                {
                    "player_name": "Brock Purdy",
                    "position": "QB",
                    "pigskin_rank": 2,
                    "model_run_id": "run_123",
                }
            ]
        )
        result = tools.get_rankings_slice_tool(
            position="QB'; DROP TABLE nope",
            season=2026,
            limit=250,
            client=client,
            dataset_id="fantasy_football_brain",
        )

        sql, job_config = client.calls[0]
        self.assertIn("analytics_pigskin_rankings", sql)
        self.assertNotIn("DROP TABLE", sql)
        self.assertEqual(job_config.maximum_bytes_billed, tools.DEFAULT_MAX_BYTES_BILLED)
        self.assertEqual(
            {param.name: param.value for param in job_config.query_parameters}["limit"],
            tools.MAX_RANKINGS_LIMIT,
        )
        self.assertEqual(result["row_count"], 1)

    def test_bad_dataset_identifier_is_rejected(self):
        client = FakeClient()

        with self.assertRaises(ValueError):
            tools.get_fraud_watch_candidates_tool(
                client=client,
                dataset_id="fantasy_football_brain;DROP",
            )

    def test_search_players_uses_packet_helper_and_caps_limit(self):
        with patch.object(
            tools,
            "search_player_context_packets",
            return_value=[
                {
                    "player_id_internal": "player_1",
                    "source_player_key": "sleeper_1",
                    "display_name": "Brian Thomas Jr.",
                    "position": "WR",
                    "team": "JAX",
                    "model_run_id": "run_1",
                    "ranking_version": "v1",
                    "as_of_season": 2026,
                    "as_of_week": 1,
                    "missing_data_flags": [],
                }
            ],
        ) as mocked_search:
            result = tools.search_players_tool(query="Brian Thomas", limit=500)

        self.assertEqual(result["row_count"], 1)
        self.assertEqual(result["limit"], tools.MAX_SEARCH_LIMIT)
        mocked_search.assert_called_once()

    def test_compare_players_caps_input_list(self):
        def fake_packet(**kwargs):
            return {
                "found": True,
                "display_name": kwargs["player_name"],
                "position": "WR",
                "team": "FAKE",
                "model_run_id": "run_1",
                "ranking_version": "v1",
                "packet_json": {
                    "ranking_context": {"pigskin_rank_position": 1, "pigskin_tier": "QB1"},
                    "usage_summary": {},
                    "efficiency_summary": {},
                },
                "missing_data_flags": [],
            }

        with patch.object(tools, "get_player_context_packet_tool", side_effect=fake_packet):
            result = tools.compare_players_tool(
                player_names=["a", "b", "c", "d", "e", "f", "g"]
            )

        self.assertEqual(result["row_count"], tools.MAX_COMPARE_PLAYERS)


if __name__ == "__main__":
    unittest.main()
