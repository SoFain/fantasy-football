from __future__ import annotations

import json
import unittest

from google.api_core.exceptions import NotFound

from src import materialize_viewer_team_context, viewer_team_context
from src.materialize_viewer_team_context import SourceTableStatus


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


class ViewerTeamContextHelperTests(unittest.TestCase):
    def test_context_query_uses_compat_view_and_parameters(self):
        sql, job_config = viewer_team_context.build_viewer_team_context_query(
            project_id="test-project",
            dataset_id="test_dataset",
            league_id="123",
            roster_id=4,
            scoring_profile_id="ppr",
        )

        self.assertIn("compat_viewer_team_context", sql)
        self.assertNotIn("sleeper_roster_players", sql)
        self.assertNotIn("sleeper_lineups", sql)
        self.assertNotIn("sleeper_available_players", sql)
        self.assertIn("@league_id", sql)
        self.assertIn("@roster_id", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["league_id"], "123")
        self.assertEqual(params["roster_id"], 4)
        self.assertEqual(params["scoring_profile_id"], "ppr")

    def test_missing_context_returns_unavailable_response(self):
        client = FakeClient(rows=[])

        result = viewer_team_context.get_viewer_team_context(
            "123",
            roster_id=4,
            client=client,
            dataset_id="test_dataset",
        )

        self.assertTrue(result["unavailable"])
        self.assertEqual(result["reason"], "viewer_team_context_not_materialized")
        self.assertIn("league_context", result["packet"])
        self.assertIn("viewer_team_context_not_materialized", result["missing_data_flags"])

    def test_missing_compat_view_returns_unavailable_response(self):
        client = FakeClient(exc=NotFound("missing"))

        result = viewer_team_context.get_viewer_team_context(
            "123",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertTrue(result["unavailable"])

    def test_packet_json_normalization_includes_required_keys(self):
        packet = viewer_team_context.normalize_packet_json(json.dumps({
            "league_context": {"league_id": "123"},
            "roster_rows": [{"display_name": "Player"}],
        }))

        for key in viewer_team_context.PACKET_KEYS:
            self.assertIn(key, packet)
        self.assertEqual(packet["league_context"]["league_id"], "123")

    def test_list_query_clamps_limit(self):
        _, job_config = viewer_team_context.build_list_viewer_team_contexts_query(
            project_id="test-project",
            dataset_id="test_dataset",
            limit=999,
        )

        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["limit"], viewer_team_context.MAX_LIMIT)
        self.assertEqual(job_config.maximum_bytes_billed, viewer_team_context.DEFAULT_MAX_BYTES_BILLED)

    def test_unsafe_dataset_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            viewer_team_context.build_viewer_team_context_query(
                project_id="test-project",
                dataset_id="bad.dataset",
                league_id="123",
            )


class ViewerTeamContextMaterializerTests(unittest.TestCase):
    def _source_status(self, **overrides):
        status = {
            table_name: SourceTableStatus(False)
            for table_name in materialize_viewer_team_context.SOURCE_TABLES
        }
        status.update(overrides)
        return status

    def test_materializer_sql_builds_packet_mart(self):
        source_status = self._source_status(
            sleeper_leagues=SourceTableStatus(True),
            sleeper_rosters=SourceTableStatus(True),
            sleeper_roster_players=SourceTableStatus(True),
            sleeper_lineups=SourceTableStatus(True),
            sleeper_available_players=SourceTableStatus(True),
            sleeper_players_current=SourceTableStatus(True),
            dim_players_current=SourceTableStatus(True),
            player_identity_bridge=SourceTableStatus(True),
            analytics_pigskin_rankings=SourceTableStatus(True),
            compat_trade_assets_current=SourceTableStatus(True),
            compat_sleeper_watch_candidates=SourceTableStatus(True),
            compat_player_profiles_current=SourceTableStatus(True),
            compat_trade_player_history=SourceTableStatus(True),
            llm_player_context_packet=SourceTableStatus(True),
        )

        sql = materialize_viewer_team_context.build_viewer_team_context_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("INSERT INTO `test-project.test_dataset.mart_viewer_team_context`", sql)
        self.assertIn("packet_json", sql)
        self.assertIn("packet_text", sql)
        self.assertIn("FROM `test-project.test_dataset.sleeper_roster_players`", sql)
        self.assertIn("FROM `test-project.test_dataset.sleeper_players_current`", sql)
        self.assertIn("compat_trade_assets_current", sql)
        self.assertIn("compat_sleeper_watch_candidates", sql)
        self.assertIn(str(materialize_viewer_team_context.PACKET_TEXT_MAX_CHARS), sql)

    def test_materializer_sql_handles_missing_available_snapshot_with_flags(self):
        source_status = self._source_status(
            sleeper_rosters=SourceTableStatus(True),
            sleeper_roster_players=SourceTableStatus(True),
            sleeper_available_players=SourceTableStatus(False),
            sleeper_players_current=SourceTableStatus(False),
            compat_sleeper_watch_candidates=SourceTableStatus(False),
        )

        sql = materialize_viewer_team_context.build_viewer_team_context_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("missing_sleeper_available_players_source", sql)
        self.assertIn("missing_sleeper_players_current_source", sql)
        self.assertIn("missing_sleeper_watch_source", sql)
        self.assertNotIn("FROM `test-project.test_dataset.sleeper_available_players`", sql)
        self.assertNotIn("FROM `test-project.test_dataset.sleeper_players_current`", sql)

    def test_materializer_sql_uses_delete_insert_not_table_replace(self):
        sql = materialize_viewer_team_context.build_viewer_team_context_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=self._source_status(),
        )

        self.assertIn("DELETE FROM", sql)
        self.assertIn("INSERT INTO", sql)
        self.assertNotIn("CREATE OR REPLACE TABLE", sql)


if __name__ == "__main__":
    unittest.main()
