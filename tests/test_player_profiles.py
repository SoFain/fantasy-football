from __future__ import annotations

import unittest

from src import materialize_player_profiles, player_profiles
from src.materialize_player_profiles import SourceTableStatus


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

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        return FakeJob(self.rows)


class PlayerProfileHelperTests(unittest.TestCase):
    def test_profile_query_uses_compat_view_and_parameters(self):
        sql, job_config = player_profiles.build_player_profile_query(
            project_id="test-project",
            dataset_id="test_dataset",
            player_name="A.J. Brown",
            scoring_profile_id="ppr",
        )

        self.assertIn("compat_player_profiles_current", sql)
        for raw_table in (
            "player_rosters",
            "player_contracts",
            "depth_charts",
            "college_player_stats",
            "rookie_scouting_metrics",
        ):
            self.assertNotIn(raw_table, sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "ppr")
        self.assertEqual(params["normalized_name"], "ajbrown")

    def test_search_query_clamps_limit_and_filters_profile(self):
        _, job_config = player_profiles.build_player_profile_search_query(
            project_id="test-project",
            dataset_id="test_dataset",
            query="Brock",
            position="QB",
            team="SF",
            scoring_profile_id="half_ppr",
            limit=1000,
        )

        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["limit"], player_profiles.MAX_SEARCH_LIMIT)
        self.assertEqual(params["position"], "QB")
        self.assertEqual(params["team"], "SF")
        self.assertEqual(params["scoring_profile_id"], "half_ppr")

    def test_missing_profile_returns_none(self):
        client = FakeClient(rows=[])

        result = player_profiles.get_player_profile(
            player_name="Missing Player",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertIsNone(result)
        sql, _ = client.query_calls[0]
        self.assertIn("compat_player_profiles_current", sql)

    def test_search_blank_query_returns_empty_list(self):
        self.assertEqual(player_profiles.search_player_profiles("   "), [])

    def test_profile_select_contains_required_context_fields(self):
        sql, _ = player_profiles.build_player_profile_query(
            project_id="test-project",
            dataset_id="test_dataset",
            player_id_internal="pid-1",
        )

        for field in (
            "player_id_internal",
            "display_name",
            "fantasy_points_current_season",
            "targets_last_3",
            "epa_summary_json",
            "model_run_id",
            "pigskin_rank_position",
            "contract_summary_json",
            "missing_data_flags",
        ):
            self.assertIn(field, sql)

    def test_unsafe_dataset_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            player_profiles.build_player_profile_query(
                project_id="test-project",
                dataset_id="bad.dataset",
                player_id_internal="pid-1",
            )


class PlayerProfileMaterializerTests(unittest.TestCase):
    def test_materializer_sql_uses_mart_and_compat_sources(self):
        source_status = {
            table_name: SourceTableStatus(False, frozenset())
            for table_name in materialize_player_profiles.OPTIONAL_SOURCE_TABLES
        }

        sql = materialize_player_profiles.build_player_profiles_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("mart_player_profiles_current", sql)
        self.assertIn("analytics_player_fantasy_points_by_profile", sql)
        self.assertIn("analytics_player_weekly_truth", sql)
        self.assertIn("player_identity_bridge", sql)
        self.assertIn("dim_players_current", sql)
        self.assertIn("analytics_pigskin_rankings", sql)
        self.assertNotIn("FROM `test-project.test_dataset.player_rosters`", sql)
        self.assertNotIn("FROM `test-project.test_dataset.player_contracts`", sql)
        self.assertIn("missing_player_contracts_source", sql)

    def test_materializer_sql_includes_optional_source_when_available(self):
        source_status = {
            table_name: SourceTableStatus(False, frozenset())
            for table_name in materialize_player_profiles.OPTIONAL_SOURCE_TABLES
        }
        source_status["player_contracts"] = SourceTableStatus(
            True,
            frozenset({"gsis_id", "value", "apy", "guaranteed", "year_signed", "is_active"}),
        )

        sql = materialize_player_profiles.build_player_profiles_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("FROM `test-project.test_dataset.player_contracts`", sql)
        self.assertIn("contract_summary_json", sql)


if __name__ == "__main__":
    unittest.main()
