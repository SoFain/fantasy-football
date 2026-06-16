from __future__ import annotations

import unittest

from google.api_core.exceptions import NotFound

from src import materialize_sleeper_watch, sleeper_watch
from src.materialize_sleeper_watch import SourceTableStatus


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

    def __init__(self, rows=None, exc=None):
        self.rows = rows or []
        self.exc = exc
        self.query_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        if self.exc:
            raise self.exc
        return FakeJob(self.rows)


class SleeperWatchHelperTests(unittest.TestCase):
    def test_candidates_query_uses_compat_view_and_parameters(self):
        sql, job_config = sleeper_watch.build_sleeper_watch_candidates_query(
            project_id="test-project",
            dataset_id="test_dataset",
            league_id="123",
            position="WR",
            scoring_profile_id="ppr",
        )

        self.assertIn("compat_sleeper_watch_candidates", sql)
        self.assertNotIn("weekly_metrics", sql)
        self.assertNotIn("sleeper_rosters", sql)
        self.assertNotIn("sleeper_roster_players", sql)
        self.assertIn("@league_id", sql)
        self.assertIn("@position", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["league_id"], "123")
        self.assertEqual(params["position"], "WR")
        self.assertEqual(params["scoring_profile_id"], "ppr")

    def test_candidates_query_clamps_limit(self):
        _, job_config = sleeper_watch.build_sleeper_watch_candidates_query(
            project_id="test-project",
            dataset_id="test_dataset",
            limit=9999,
        )

        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["limit"], sleeper_watch.MAX_LIMIT)
        self.assertEqual(job_config.maximum_bytes_billed, sleeper_watch.DEFAULT_MAX_BYTES_BILLED)

    def test_missing_compat_view_returns_empty_list(self):
        client = FakeClient(exc=NotFound("missing"))

        result = sleeper_watch.get_sleeper_watch_candidates(
            client=client,
            dataset_id="test_dataset",
        )

        self.assertEqual(result, [])

    def test_streamer_candidates_require_candidate_scores(self):
        sql, _ = sleeper_watch.build_sleeper_watch_candidates_query(
            project_id="test-project",
            dataset_id="test_dataset",
            score_mode="streamer",
        )

        self.assertIn("streamer_score IS NOT NULL", sql)
        self.assertIn("waiver_candidate_flag", sql)

    def test_breakout_candidates_order_by_breakout_score(self):
        sql, _ = sleeper_watch.build_sleeper_watch_candidates_query(
            project_id="test-project",
            dataset_id="test_dataset",
            score_mode="breakout",
        )

        self.assertIn("breakout_score IS NOT NULL", sql)
        self.assertIn("ORDER BY breakout_score DESC", sql)

    def test_unsafe_dataset_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            sleeper_watch.build_sleeper_watch_candidates_query(
                project_id="test-project",
                dataset_id="bad.dataset",
            )


class SleeperWatchMaterializerTests(unittest.TestCase):
    def _source_status(self, **overrides):
        status = {
            table_name: SourceTableStatus(False)
            for table_name in materialize_sleeper_watch.SOURCE_TABLES
        }
        status.update(overrides)
        return status

    def test_materializer_sql_builds_controlled_sleeper_mart(self):
        source_status = self._source_status(
            analytics_player_weekly_truth=SourceTableStatus(True, row_count=100),
            analytics_player_fantasy_points_by_profile=SourceTableStatus(True),
            analytics_pigskin_rankings=SourceTableStatus(True),
            analytics_fraud_watch=SourceTableStatus(True),
            analytics_game_environment=SourceTableStatus(True),
            dim_players_current=SourceTableStatus(True),
            player_identity_bridge=SourceTableStatus(True),
            sleeper_rosters=SourceTableStatus(True),
            sleeper_roster_players=SourceTableStatus(True),
            sleeper_available_players=SourceTableStatus(True),
            sleeper_players_current=SourceTableStatus(True),
            realtime_player_news=SourceTableStatus(True),
        )

        sql = materialize_sleeper_watch.build_sleeper_watch_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("mart_sleeper_watch_candidates", sql)
        self.assertIn("INSERT INTO", sql)
        self.assertIn("FROM `test-project.test_dataset.sleeper_roster_players`", sql)
        self.assertIn("analytics_player_weekly_truth", sql)
        self.assertIn("analytics_player_fantasy_points_by_profile", sql)
        self.assertIn("analytics_pigskin_rankings", sql)
        self.assertIn("missing_data_flags", sql)

    def test_materializer_sql_handles_missing_sleeper_snapshots_with_flags(self):
        source_status = self._source_status(
            analytics_player_weekly_truth=SourceTableStatus(True, row_count=100),
            sleeper_rosters=SourceTableStatus(False),
            sleeper_roster_players=SourceTableStatus(False),
            sleeper_available_players=SourceTableStatus(False),
        )

        sql = materialize_sleeper_watch.build_sleeper_watch_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("missing_sleeper_rosters_source", sql)
        self.assertIn("missing_sleeper_roster_players_source", sql)
        self.assertNotIn("FROM `test-project.test_dataset.sleeper_roster_players`", sql)

    def test_materializer_sql_has_global_league_path(self):
        source_status = self._source_status(
            analytics_player_weekly_truth=SourceTableStatus(True, row_count=100),
        )

        sql = materialize_sleeper_watch.build_sleeper_watch_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("@league_id", sql)
        self.assertIn("GLOBAL", sql)


if __name__ == "__main__":
    unittest.main()
