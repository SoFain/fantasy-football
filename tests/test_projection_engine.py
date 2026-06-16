from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from src import projection_engine


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


def feature_row(**overrides):
    row = {
        "player_id_internal": "pid_1",
        "source_player_key": "00-001",
        "display_name": "A.J. Brown",
        "position": "WR",
        "team": "PHI",
        "opponent": "DAL",
        "season": 2025,
        "week": 7,
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "recent_points_per_game": 16.0,
        "profile_fantasy_points_per_game": 15.5,
        "fantasy_points_last_3": 18.0,
        "fantasy_points_last_5": 15.0,
        "fantasy_points_last_8": 14.0,
        "snap_share_last_3": 0.86,
        "target_share_last_3": 0.27,
        "rush_share_last_3": 0.0,
        "high_value_touches_last_3": 24.0,
        "red_zone_opportunities_last_3": 4.0,
        "role_quality_score": 82.0,
        "role_fragility_score": 18.0,
        "total_epa_recent": 8.5,
        "age": 28.0,
        "rookie_year": 2019,
        "active_status": "active",
        "market_value": 26000,
        "pigskin_rank_overall": 18,
        "pigskin_rank_position": 7,
        "pigskin_tier": "front-line starter",
        "pigskin_projection": 17.0,
        "pigskin_confidence": 82.0,
        "fraud_risk_score": 12.0,
        "breakout_score": 30.0,
        "game_environment_json": "{}",
        "source_freshness_json": json.dumps({"source": "compat"}),
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return FakeRow(row)


class ProjectionEngineTests(unittest.TestCase):
    def test_weekly_projection_formula_deterministic(self):
        row = feature_row()

        first = projection_engine.calculate_weekly_projection(row)
        second = projection_engine.calculate_weekly_projection(row)

        self.assertEqual(first, second)
        self.assertGreater(first["projected_points_mean"], 0)

    def test_ros_projection_formula_deterministic(self):
        row = feature_row()

        first = projection_engine.calculate_ros_projection(row, {"as_of_week": 7})
        second = projection_engine.calculate_ros_projection(row, {"as_of_week": 7})

        self.assertEqual(first, second)
        self.assertEqual(first["remaining_games"], 10)

    def test_dynasty_projection_formula_deterministic(self):
        row = feature_row(league_type_id="dynasty")

        first = projection_engine.calculate_dynasty_projection(row)
        second = projection_engine.calculate_dynasty_projection(row)

        self.assertEqual(first, second)
        self.assertGreater(first["total_dynasty_value"], 0)

    def test_no_output_rows_without_model_run_id(self):
        client = FakeClient(rows=[feature_row()])

        with self.assertRaises(ValueError):
            projection_engine.build_weekly_projection_rows(
                season=2025,
                week=7,
                client=client,
                dataset_id="test_dataset",
            )

    def test_ranking_generation_assigns_overall_and_position_ranks(self):
        rows = [
            projection_engine._weekly_projection_row(
                feature_row(display_name="WR One", position="WR", recent_points_per_game=18.0),
                season=2025,
                week=7,
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
                model_run_id="run_1",
            ),
            projection_engine._weekly_projection_row(
                feature_row(display_name="WR Two", position="WR", recent_points_per_game=12.0),
                season=2025,
                week=7,
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
                model_run_id="run_1",
            ),
        ]

        rankings = projection_engine.build_projection_rankings(rows)

        self.assertEqual(rankings[0]["rank_overall"], 1)
        self.assertEqual(rankings[0]["rank_position"], 1)
        self.assertEqual(rankings[1]["rank_position"], 2)

    def test_superflex_roster_format_affects_qb_placeholder(self):
        qb = feature_row(position="QB", roster_format_id="one_qb", recent_points_per_game=18.0)
        one_qb = projection_engine.calculate_weekly_projection(qb)["projected_points_mean"]
        superflex = projection_engine.calculate_weekly_projection(
            feature_row(position="QB", roster_format_id="superflex", recent_points_per_game=18.0)
        )["projected_points_mean"]

        self.assertGreater(superflex, one_qb)

    def test_dynasty_league_type_changes_age_value_weighting(self):
        redraft = projection_engine.calculate_dynasty_projection(feature_row(league_type_id="redraft"))
        dynasty = projection_engine.calculate_dynasty_projection(feature_row(league_type_id="dynasty"))

        self.assertGreater(dynasty["total_dynasty_value"], redraft["total_dynasty_value"])

    def test_scoring_profile_changes_output(self):
        ppr = projection_engine.calculate_weekly_projection(feature_row(scoring_profile_id="ppr"))
        standard = projection_engine.calculate_weekly_projection(feature_row(scoring_profile_id="standard"))

        self.assertGreater(ppr["projected_points_mean"], standard["projected_points_mean"])

    def test_missing_inputs_create_flags_not_crashes(self):
        result = projection_engine.calculate_weekly_projection(
            feature_row(player_id_internal=None, recent_points_per_game=None, fantasy_points_last_3=None, game_environment_json=None)
        )

        self.assertIn("missing_player_id_internal", result["missing_data_flags"])
        self.assertIn("missing_recent_points", result["missing_data_flags"])
        self.assertIn("missing_game_environment", result["missing_data_flags"])

    def test_projection_rows_write_through_mocked_bigquery_client(self):
        client = FakeClient()
        rows = [
            projection_engine._weekly_projection_row(
                feature_row(),
                season=2025,
                week=7,
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
                model_run_id="run_1",
            )
        ]

        result = projection_engine.write_projection_rows(rows, horizon="weekly", client=client, dataset_id="test_dataset")

        self.assertEqual(result["projection_rows"], 1)
        self.assertTrue(any(call[0].endswith(".projections_player_weekly") for call in client.insert_calls))
        self.assertTrue(any(call[0].endswith(".projection_rankings_current") for call in client.insert_calls))

    def test_model_run_lifecycle_success(self):
        client = FakeClient(rows=[feature_row()])
        with patch("src.projection_engine.create_projection_model_run") as create_run, patch(
            "src.projection_engine.mark_model_run_complete"
        ) as mark_complete:
            create_run.return_value = {
                "model_run_id": "run_1",
                "feature_config_version_id": "baseline_weekly_v1",
                "source_freshness_snapshot_id": "freshness_1",
            }

            result = projection_engine.run_projection(
                horizon="weekly",
                season=2025,
                week=7,
                client=client,
                dataset_id="test_dataset",
                dry_run=False,
            )

        self.assertEqual(result["model_run_id"], "run_1")
        mark_complete.assert_called_once()

    def test_model_run_lifecycle_failure_marks_failed_and_reraises(self):
        client = FakeClient(rows=[feature_row()])
        with patch("src.projection_engine.create_projection_model_run") as create_run, patch(
            "src.projection_engine.write_projection_rows"
        ) as write_rows, patch("src.projection_engine.mark_model_run_failed") as mark_failed:
            create_run.return_value = {
                "model_run_id": "run_1",
                "feature_config_version_id": "baseline_weekly_v1",
                "source_freshness_snapshot_id": "freshness_1",
            }
            write_rows.side_effect = RuntimeError("write failed")

            with self.assertRaises(RuntimeError):
                projection_engine.run_projection(
                    horizon="weekly",
                    season=2025,
                    week=7,
                    client=client,
                    dataset_id="test_dataset",
                    dry_run=False,
                )

        mark_failed.assert_called_once()
        self.assertIn("write failed", mark_failed.call_args.args[1])

    def test_projection_query_uses_curated_sources_only(self):
        sql, _ = projection_engine.build_projection_feature_query(
            project_id="test-project",
            dataset_id="test_dataset",
            season=2025,
            week=7,
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
        )

        self.assertIn("compat_trade_player_history", sql)
        self.assertIn("compat_player_profiles_current", sql)
        self.assertIn("compat_trade_assets_current", sql)
        self.assertNotIn("weekly_metrics", sql)
        self.assertNotIn("play_by_play", sql)
        self.assertNotIn("sleeper_roster_players", sql)

    def test_unsafe_dataset_rejected(self):
        with self.assertRaises(ValueError):
            projection_engine.build_projection_feature_query(
                project_id="test-project",
                dataset_id="bad.dataset",
                season=2025,
                week=7,
                scoring_profile_id="ppr",
                league_type_id="redraft",
                roster_format_id="one_qb",
            )


if __name__ == "__main__":
    unittest.main()
