from __future__ import annotations

import unittest

import pandas as pd

from src import trade_history


class FakeJob:
    def __init__(self, rows=None, dataframe=None):
        self.rows = rows or []
        self.dataframe = dataframe if dataframe is not None else pd.DataFrame()

    def result(self):
        return self

    def __iter__(self):
        return iter(self.rows)

    def to_dataframe(self):
        return self.dataframe


class FakeClient:
    project = "test-project"

    def __init__(self, job):
        self.job = job
        self.query_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return self.job


class TradeHistoryHelperTests(unittest.TestCase):
    def test_history_query_uses_compat_view_and_parameters(self):
        sql, job_config = trade_history.build_trade_player_history_query(
            project_id="test-project",
            dataset_id="test_dataset",
            player_name="A.J. Brown",
            scoring_profile_id="ppr",
        )

        self.assertIn("compat_trade_player_history", sql)
        self.assertNotIn("weekly_metrics", sql)
        self.assertIn("@scoring_profile_id", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "ppr")
        self.assertEqual(params["normalized_name"], "ajbrown")

    def test_history_query_clamps_limit(self):
        _, high_config = trade_history.build_trade_player_history_query(
            project_id="test-project",
            dataset_id="test_dataset",
            player_id_internal="pid-1",
            limit=1000,
        )
        _, low_config = trade_history.build_trade_player_history_query(
            project_id="test-project",
            dataset_id="test_dataset",
            player_id_internal="pid-1",
            limit=0,
        )

        high_params = {param.name: param.value for param in high_config.query_parameters}
        low_params = {param.name: param.value for param in low_config.query_parameters}
        self.assertEqual(high_params["limit"], trade_history.MAX_HISTORY_LIMIT)
        self.assertEqual(low_params["limit"], 1)

    def test_lookup_query_supports_id_and_name_fallback(self):
        sql, job_config = trade_history.build_trade_player_lookup_query(
            project_id="test-project",
            dataset_id="test_dataset",
            lookup="Brock Purdy",
        )

        self.assertIn("player_id_internal = @lookup", sql)
        self.assertIn("source_player_key = @lookup", sql)
        self.assertIn("normalized_name = @normalized_lookup", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["lookup"], "Brock Purdy")
        self.assertEqual(params["normalized_lookup"], "brockpurdy")

    def test_get_trade_player_history_returns_empty_dataframe_cleanly(self):
        client = FakeClient(FakeJob(dataframe=pd.DataFrame()))

        result = trade_history.get_trade_player_history(
            player_name="Missing Player",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertTrue(result.empty)
        sql, job_config = client.query_calls[0]
        self.assertIn("compat_trade_player_history", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["normalized_name"], "missingplayer")

    def test_lookup_returns_empty_list_for_blank_input(self):
        self.assertEqual(trade_history.resolve_trade_player_lookup("   "), [])

    def test_unsafe_dataset_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            trade_history.build_trade_player_history_query(
                project_id="test-project",
                dataset_id="bad.dataset",
                player_id_internal="pid-1",
            )


if __name__ == "__main__":
    unittest.main()
