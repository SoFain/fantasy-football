from __future__ import annotations

import math
import unittest
from unittest.mock import patch

from src import backtesting


class FakeRow(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


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
        self.insert_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return FakeJob(self.rows)

    def insert_rows_json(self, table_id, rows):
        self.insert_calls.append((table_id, rows))
        return []


def projection_row(**overrides):
    row = {
        "model_run_id": "run_1",
        "player_id_internal": "pid_1",
        "source_player_key": "00-001",
        "display_name": "A.J. Brown",
        "position": "WR",
        "team": "PHI",
        "season": 2024,
        "week": 3,
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "projection_horizon": "weekly",
        "projected_points": 18.0,
        "projected_floor": 10.0,
        "projected_ceiling": 25.0,
        "rank_source": "test",
        "source_freshness_json": "{}",
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


def actual_row(**overrides):
    row = {
        "player_id_internal": "pid_1",
        "source_player_key": "00-001",
        "display_name": "A.J. Brown",
        "position": "WR",
        "team": "PHI",
        "season": 2024,
        "week": 3,
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "actual_points": 20.0,
        "source_freshness_json": "{}",
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return row


class BacktestingTests(unittest.TestCase):
    def test_absolute_squared_rank_boom_bust_and_range_math(self):
        projections = [
            projection_row(player_id_internal="pid_1", display_name="A.J. Brown", projected_points=18.0),
            projection_row(
                player_id_internal="pid_2",
                source_player_key="00-002",
                display_name="Bench WR",
                projected_points=10.0,
                projected_floor=6.0,
                projected_ceiling=14.0,
            ),
        ]
        actuals = [
            actual_row(player_id_internal="pid_1", display_name="A.J. Brown", actual_points=20.0),
            actual_row(
                player_id_internal="pid_2",
                source_player_key="00-002",
                display_name="Bench WR",
                actual_points=8.0,
            ),
        ]

        result = backtesting.evaluate_player_week_predictions(projections, actuals, backtest_run_id="bt_1")
        row = next(item for item in result["rows"] if item["player_id_internal"] == "pid_1")

        self.assertEqual(row["absolute_error"], 2.0)
        self.assertEqual(row["squared_error"], 4.0)
        self.assertEqual(row["rank_error_overall"], 0)
        self.assertEqual(row["rank_error_position"], 0)
        self.assertTrue(row["actual_inside_range"])
        self.assertFalse(row["projected_boom_flag"])
        self.assertTrue(row["actual_boom_flag"])
        self.assertFalse(row["projected_bust_flag"])

    def test_summary_metrics_mae_rmse_and_precision(self):
        evaluation = backtesting.evaluate_player_week_predictions(
            [
                projection_row(player_id_internal="pid_1", projected_points=18.0),
                projection_row(
                    player_id_internal="pid_2",
                    source_player_key="00-002",
                    projected_points=22.0,
                    projected_floor=12.0,
                    projected_ceiling=18.0,
                ),
            ],
            [
                actual_row(player_id_internal="pid_1", actual_points=20.0),
                actual_row(player_id_internal="pid_2", source_player_key="00-002", actual_points=10.0),
            ],
            backtest_run_id="bt_1",
        )

        summaries = backtesting.compute_summary_metrics(evaluation["rows"])
        overall = next(row for row in summaries if row["position"] is None and row["season"] is None)

        self.assertEqual(overall["player_count"], 2)
        self.assertEqual(overall["mae"], 7.0)
        self.assertEqual(overall["rmse"], round(math.sqrt((4 + 144) / 2), 4))
        self.assertEqual(overall["boom_precision"], 0.0)
        self.assertEqual(overall["range_calibration_rate"], 0.5)

    def test_calibration_bins_are_created(self):
        evaluation = backtesting.evaluate_player_week_predictions(
            [projection_row(projected_points=18.0)],
            [actual_row(actual_points=20.0)],
            backtest_run_id="bt_1",
        )

        bins = backtesting.compute_calibration_bins(evaluation["rows"])

        self.assertTrue(any(row["bin_name"] == "15_to_20" and row["position"] == "WR" for row in bins))
        self.assertTrue(any(row["bin_name"] == "15_to_20" and row["position"] is None for row in bins))

    def test_missing_projection_and_actual_rows_are_clean(self):
        missing_projection = backtesting.evaluate_player_week_predictions([], [actual_row()], backtest_run_id="bt_1")
        missing_actual = backtesting.evaluate_player_week_predictions([projection_row()], [], backtest_run_id="bt_1")

        self.assertTrue(missing_projection["missing_projection_rows"])
        self.assertEqual(missing_actual["missing_actual_rows"], 1)
        self.assertEqual(missing_actual["rows"], [])

    def test_backtest_run_lifecycle_uses_parameterized_updates(self):
        client = FakeClient()

        backtest_run_id = backtesting.create_backtest_run(
            client=client,
            dataset_id="test_dataset",
            backtest_run_id="bt_1",
            model_run_id="run_1",
            projection_horizon="weekly",
            season_start=2024,
            season_end=2024,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
        )
        backtesting.mark_backtest_run_complete("bt_1", client=client, dataset_id="test_dataset", notes="done")
        backtesting.mark_backtest_run_failed("bt_1", "primary failure", client=client, dataset_id="test_dataset")

        self.assertEqual(backtest_run_id, "bt_1")
        self.assertEqual(client.insert_calls[0][0], "test-project.test_dataset.backtest_runs")
        failed_sql, failed_config = client.query_calls[-1]
        self.assertIn("error_message = @error_message", failed_sql)
        params = {param.name: param.value for param in failed_config.query_parameters}
        self.assertEqual(params["error_message"], "primary failure")

    def test_write_backtest_results_refuses_rows_without_backtest_run_id(self):
        with self.assertRaisesRegex(ValueError, "missing backtest_run_id"):
            backtesting.write_backtest_results(
                player_week_rows=[{"model_run_id": "run_1"}],
                summary_rows=[],
                calibration_rows=[],
                dry_run=True,
            )

    def test_load_projection_query_is_parameterized_and_curated(self):
        client = FakeClient()

        backtesting.load_projection_rows(
            client=client,
            dataset_id="test_dataset",
            model_run_id="run_1",
            horizon="weekly",
            season_start=2024,
            season_end=2024,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
        )

        sql, job_config = client.query_calls[0]
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertIn("projections_player_weekly", sql)
        self.assertNotIn("weekly_metrics", sql)
        self.assertNotIn("play_by_play", sql)
        self.assertEqual(params["model_run_id"], "run_1")
        self.assertEqual(params["season_start"], 2024)

    def test_load_actual_query_uses_fantasy_points_mart(self):
        client = FakeClient()

        backtesting.load_actual_rows(
            client=client,
            dataset_id="test_dataset",
            season_start=2024,
            season_end=2024,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
        )

        sql, job_config = client.query_calls[0]
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertIn("analytics_player_fantasy_points_by_profile", sql)
        self.assertNotIn("weekly_metrics", sql)
        self.assertEqual(params["scoring_profile_id"], "ppr")

    def test_run_backtest_dry_run_reports_missing_inputs(self):
        with patch("src.backtesting.load_projection_rows", return_value=[]), patch(
            "src.backtesting.load_actual_rows", return_value=[]
        ):
            result = backtesting.run_backtest(
                client=FakeClient(),
                dataset_id="test_dataset",
                horizon="weekly",
                season_start=2024,
                season_end=2024,
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
                dry_run=True,
            )

        self.assertEqual(result["status"], "failed")
        self.assertIn("missing_projection_rows", result["missing_data_flags"])
        self.assertIn("missing_actual_rows", result["missing_data_flags"])

    def test_run_backtest_can_compare_against_market_baseline(self):
        with patch("src.backtesting.load_projection_rows", return_value=[projection_row(projected_points=18.0)]), patch(
            "src.backtesting.load_actual_rows",
            return_value=[actual_row(actual_points=20.0, actual_rank_overall=1, actual_rank_position=1)],
        ), patch(
            "src.market_consensus.get_current_market_baseline",
            return_value=[
                {
                    "source_id": "manual_ecr",
                    "snapshot_id": "snap_1",
                    "player_id_internal": "pid_1",
                    "display_name": "A.J. Brown",
                    "position": "WR",
                    "season": 2024,
                    "week": 3,
                    "scoring_profile_id": "ppr",
                    "league_type_id": "redraft",
                    "roster_format_id": "one_qb",
                    "rank_overall": 5,
                    "rank_position": 2,
                    "projected_points": 14.0,
                    "baseline_type": "projection",
                }
            ],
        ):
            result = backtesting.run_backtest(
                client=FakeClient(),
                dataset_id="test_dataset",
                horizon="weekly",
                season_start=2024,
                season_end=2024,
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
                market_source_id="manual_ecr",
                dry_run=True,
            )

        self.assertEqual(result["market_rows"], 1)
        self.assertEqual(result["rows"][0]["market_absolute_error"], 6.0)
        self.assertTrue(result["rows"][0]["model_better_than_market"])
        overall = next(row for row in result["summary"] if row["position"] is None and row["season"] is None)
        self.assertEqual(overall["market_source_id"], "manual_ecr")
        self.assertEqual(overall["model_vs_market_mae_delta"], -4.0)


if __name__ == "__main__":
    unittest.main()
