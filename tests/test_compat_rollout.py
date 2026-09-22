from __future__ import annotations

import unittest
from pathlib import Path

from src import compat_rollout, trade_history
from src.compat_flags import (
    USE_COMPAT_PLAYER_PROFILES,
    USE_COMPAT_SLEEPER_WATCH,
    USE_COMPAT_TRADE_ASSETS,
    USE_COMPAT_TRADE_PLAYER_HISTORY,
    USE_COMPAT_VIEWER_TEAM_CONTEXT,
    compat_flag_enabled,
)


class FakeField:
    def __init__(self, name):
        self.name = name


class FakeTable:
    def __init__(self, schema, num_rows=10, table_type="VIEW"):
        self.schema = [FakeField(name) for name in schema]
        self.num_rows = num_rows
        self.table_type = table_type


class FakeJob:
    def __init__(self, rows):
        self.rows = rows

    def result(self):
        return self

    def __iter__(self):
        return iter(self.rows)

    def to_dataframe(self):
        return self.rows


class FakeClient:
    project = "test-project"

    def __init__(self, tables=None, query_results=None):
        self.tables = tables or {}
        self.query_results = list(query_results or [])
        self.query_calls = []
        self.get_table_calls = []

    def get_table(self, table_id):
        self.get_table_calls.append(table_id)
        if table_id not in self.tables:
            raise RuntimeError("table not found")
        return self.tables[table_id]

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        rows = self.query_results.pop(0) if self.query_results else []
        return FakeJob(rows)


def table_for_flag(flag_name, *, num_rows=10, missing_columns=()):
    spec = compat_rollout.COMPAT_FLAG_SPECS[flag_name]
    columns = [column for column in spec.required_columns if column not in set(missing_columns)]
    return FakeTable(columns, num_rows=num_rows)


class CompatRolloutTests(unittest.TestCase):
    def test_readiness_checker_maps_flags_correctly(self):
        flags = compat_rollout.list_compat_flags()
        mapping = {item["flag_name"]: item["object_name"] for item in flags}

        self.assertEqual(mapping[USE_COMPAT_TRADE_PLAYER_HISTORY], "compat_trade_player_history")
        self.assertEqual(mapping[USE_COMPAT_TRADE_ASSETS], "compat_trade_assets_current")
        self.assertEqual(mapping[USE_COMPAT_PLAYER_PROFILES], "compat_player_profiles_current")
        self.assertEqual(mapping[USE_COMPAT_SLEEPER_WATCH], "compat_sleeper_watch_candidates")
        self.assertEqual(mapping[USE_COMPAT_VIEWER_TEAM_CONTEXT], "compat_viewer_team_context")

    def test_unknown_flag_rejected(self):
        with self.assertRaises(ValueError):
            compat_rollout.check_compat_object_exists(
                "USE_COMPAT_NOT_REAL",
                client=FakeClient(),
                dataset_id="test_dataset",
            )

    def test_row_count_check_handles_missing_table(self):
        result = compat_rollout.check_compat_row_count(
            USE_COMPAT_TRADE_PLAYER_HISTORY,
            client=FakeClient(),
            dataset_id="test_dataset",
        )

        self.assertFalse(result["passed"])
        self.assertIsNone(result["row_count"])

    def test_required_column_check_reports_missing_columns(self):
        table_id = "test-project.test_dataset.compat_trade_player_history"
        client = FakeClient(
            tables={
                table_id: table_for_flag(
                    USE_COMPAT_TRADE_PLAYER_HISTORY,
                    missing_columns=("source_freshness_json",),
                )
            }
        )

        result = compat_rollout.check_compat_required_columns(
            USE_COMPAT_TRADE_PLAYER_HISTORY,
            client=client,
            dataset_id="test_dataset",
        )

        self.assertFalse(result["passed"])
        self.assertEqual(result["missing_columns"], ["source_freshness_json"])

    def test_missing_data_rate_uses_bounded_query(self):
        table_id = "test-project.test_dataset.compat_trade_player_history"
        client = FakeClient(
            tables={table_id: table_for_flag(USE_COMPAT_TRADE_PLAYER_HISTORY)},
            query_results=[
                [
                    {
                        "sampled_rows": 100,
                        "source_freshness_missing_rows": 0,
                        "missing_flags_missing_rows": 0,
                    }
                ]
            ],
        )

        result = compat_rollout.check_compat_missing_data_rate(
            USE_COMPAT_TRADE_PLAYER_HISTORY,
            client=client,
            dataset_id="test_dataset",
            sample_limit=999999,
        )

        self.assertTrue(result["passed"])
        sql, job_config = client.query_calls[0]
        self.assertIn("LIMIT @sample_limit", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["sample_limit"], 10000)

    def test_validation_results_discovers_matching_files(self):
        result = compat_rollout.check_compat_validation_results(
            USE_COMPAT_TRADE_PLAYER_HISTORY,
            validations_dir=Path("bigquery/validations"),
        )

        self.assertTrue(result["passed"])
        self.assertGreaterEqual(result["validation_file_count"], 1)

    def test_recommendation_order_picks_trade_history_first(self):
        tables = {}
        query_results = []
        for flag_name in compat_rollout.ROLLOUT_ORDER:
            spec = compat_rollout.COMPAT_FLAG_SPECS[flag_name]
            tables[f"test-project.test_dataset.{spec.object_name}"] = table_for_flag(flag_name)
            query_results.append(
                [
                    {
                        "sampled_rows": 10,
                        "source_freshness_missing_rows": 0,
                        "missing_flags_missing_rows": 0,
                    }
                ]
            )
        client = FakeClient(tables=tables, query_results=query_results)

        result = compat_rollout.recommend_next_flag_to_enable(
            client=client,
            dataset_id="test_dataset",
        )

        self.assertEqual(result["recommended_flag"], USE_COMPAT_TRADE_PLAYER_HISTORY)

    def test_default_candidate_flags_remain_false(self):
        for flag_name in compat_rollout.ROLLOUT_ORDER:
            self.assertFalse(compat_flag_enabled(flag_name, {}))

    def test_trade_history_helper_uses_compat_table_with_mock_client(self):
        client = FakeClient(query_results=[[]])

        trade_history.get_trade_player_history(
            player_name="Test Player",
            client=client,
            dataset_id="test_dataset",
        )

        sql, job_config = client.query_calls[0]
        self.assertIn("compat_trade_player_history", sql)
        self.assertNotIn("weekly_metrics", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["player_name"], "Test Player")


if __name__ == "__main__":
    unittest.main()
