from __future__ import annotations

import unittest
from pathlib import Path

from src import backtest_readers
from src.compat_flags import USE_BACKTEST_DASHBOARD, compat_flag_enabled


class FakeJob:
    def __init__(self, rows=None):
        self.rows = rows or []

    def result(self):
        return self.rows


class FakeClient:
    project = "test-project"

    def __init__(self, rows=None, query_results=None):
        self.rows = rows or []
        self.query_results = list(query_results or [])
        self.query_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        if self.query_results:
            return FakeJob(self.query_results.pop(0))
        return FakeJob(self.rows)


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


class BacktestReaderTests(unittest.TestCase):
    def test_feature_flag_defaults_false(self):
        self.assertFalse(compat_flag_enabled(USE_BACKTEST_DASHBOARD, {}))
        self.assertTrue(compat_flag_enabled(USE_BACKTEST_DASHBOARD, {USE_BACKTEST_DASHBOARD: "true"}))

    def test_list_runs_query_uses_parameters_and_output_table(self):
        sql, job_config = backtest_readers.build_list_backtest_runs_query(
            project_id="test-project",
            dataset_id="test_dataset",
            status="complete",
            limit=9999,
        )

        self.assertIn("backtest_runs", sql)
        self._assert_no_raw_source_terms(sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["status"], "complete")
        self.assertEqual(params["limit"], backtest_readers.MAX_LIMIT)
        self.assertEqual(job_config.maximum_bytes_billed, backtest_readers.DEFAULT_MAX_BYTES_BILLED)

    def test_summary_query_uses_parameterized_filters(self):
        sql, job_config = backtest_readers.build_backtest_summary_query(
            project_id="test-project",
            dataset_id="test_dataset",
            backtest_run_id="bt_1",
            scoring_profile_id="ppr",
            season=2024,
            week=3,
        )

        self.assertIn("backtest_result_summary", sql)
        self._assert_no_raw_source_terms(sql)
        self.assertIn("@backtest_run_id", sql)
        self.assertIn("@season", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["backtest_run_id"], "bt_1")
        self.assertEqual(params["season"], 2024)
        self.assertEqual(params["week"], 3)

    def test_player_errors_rejects_unknown_sort(self):
        with self.assertRaises(ValueError):
            backtest_readers.build_backtest_player_errors_query(
                project_id="test-project",
                dataset_id="test_dataset",
                backtest_run_id="bt_1",
                sort_by="drop_table_desc",
            )

    def test_player_errors_query_uses_closed_sort_enum(self):
        sql, job_config = backtest_readers.build_backtest_player_errors_query(
            project_id="test-project",
            dataset_id="test_dataset",
            backtest_run_id="bt_1",
            position="WR",
            sort_by="rank_error_desc",
            limit=1000,
        )

        self.assertIn("backtest_result_player_week", sql)
        self.assertIn("ORDER BY ABS(rank_error_overall) DESC", sql)
        self.assertNotIn("drop_table_desc", sql)
        self._assert_no_raw_source_terms(sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["position"], "WR")
        self.assertEqual(params["limit"], backtest_readers.MAX_LIMIT)

    def test_empty_reader_results_are_clean(self):
        client = FakeClient(rows=[])

        self.assertEqual(
            backtest_readers.list_backtest_runs(client=client, dataset_id="test_dataset"),
            [],
        )
        self.assertIsNone(
            backtest_readers.get_backtest_run("missing", client=client, dataset_id="test_dataset"),
        )

    def test_markdown_export_includes_key_metrics(self):
        run = {
            "backtest_run_id": "bt_1",
            "model_run_id": "model_1",
            "projection_horizon": "weekly",
            "scoring_profile_id": "ppr",
            "league_type_id": "redraft",
            "roster_format_id": "one_qb",
        }
        summary = {
            "backtest_run_id": "bt_1",
            "model_run_id": "model_1",
            "projection_horizon": "weekly",
            "scoring_profile_id": "ppr",
            "league_type_id": "redraft",
            "roster_format_id": "one_qb",
            "position": None,
            "season": None,
            "week": None,
            "player_count": 100,
            "mae": 2.2,
            "rmse": 3.1,
            "mean_bias": -0.4,
            "rank_mae_overall": 8.0,
            "top_12_hit_rate": 0.5,
            "top_24_hit_rate": 0.6,
            "boom_precision": 0.7,
            "bust_precision": 0.8,
            "range_calibration_rate": 0.55,
        }
        client = FakeClient(query_results=[[run], [summary]])

        markdown = backtest_readers.export_backtest_summary_markdown(
            "bt_1",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertIn("MAE", markdown)
        self.assertIn("RMSE", markdown)
        self.assertIn("top 24 hit rate", markdown)
        self.assertIn("calibration rate", markdown)

    def test_reader_query_builders_do_not_reference_raw_sources(self):
        builders = [
            backtest_readers.build_list_backtest_runs_query(
                project_id="test-project",
                dataset_id="test_dataset",
            )[0],
            backtest_readers.build_get_backtest_run_query(
                project_id="test-project",
                dataset_id="test_dataset",
                backtest_run_id="bt_1",
            )[0],
            backtest_readers.build_backtest_summary_query(
                project_id="test-project",
                dataset_id="test_dataset",
            )[0],
            backtest_readers.build_backtest_player_errors_query(
                project_id="test-project",
                dataset_id="test_dataset",
                backtest_run_id="bt_1",
            )[0],
            backtest_readers.build_backtest_calibration_query(
                project_id="test-project",
                dataset_id="test_dataset",
                backtest_run_id="bt_1",
            )[0],
            backtest_readers.build_backtest_leaderboard_query(
                project_id="test-project",
                dataset_id="test_dataset",
            )[0],
        ]

        for sql in builders:
            self._assert_no_raw_source_terms(sql)

    def test_app_compiles_with_default_off_backtest_tab(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("USE_BACKTEST_DASHBOARD", app_source)
        self.assertIn("use_backtest_dashboard()", app_source)
        self.assertIn("render_backtest_dashboard()", app_source)

    def _assert_no_raw_source_terms(self, sql: str):
        for raw_term in RAW_SOURCE_TERMS:
            self.assertNotIn(raw_term, sql)


if __name__ == "__main__":
    unittest.main()
