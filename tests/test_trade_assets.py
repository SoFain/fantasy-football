from __future__ import annotations

import unittest

from src import materialize_trade_assets, trade_assets
from src.materialize_trade_assets import SourceTableStatus


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


class TradeAssetHelperTests(unittest.TestCase):
    def test_assets_query_uses_compat_view_and_parameters(self):
        sql, job_config = trade_assets.build_trade_assets_query(
            project_id="test-project",
            dataset_id="test_dataset",
            scoring_profile_id="ppr",
            position="WR",
            search="A.J. Brown",
        )

        self.assertIn("compat_trade_assets_current", sql)
        self.assertNotIn("market_values", sql)
        self.assertIn("@scoring_profile_id", sql)
        self.assertIn("@search", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "ppr")
        self.assertEqual(params["position"], "WR")
        self.assertEqual(params["search"], "A.J. Brown")
        self.assertEqual(params["normalized_search"], "ajbrown")

    def test_assets_query_clamps_limit(self):
        _, job_config = trade_assets.build_trade_assets_query(
            project_id="test-project",
            dataset_id="test_dataset",
            limit=9999,
        )

        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["limit"], trade_assets.MAX_LIMIT)
        self.assertEqual(job_config.maximum_bytes_billed, trade_assets.DEFAULT_MAX_BYTES_BILLED)

    def test_get_trade_asset_missing_returns_none(self):
        client = FakeClient(rows=[])

        result = trade_assets.get_trade_asset(
            player_name="Missing Player",
            client=client,
            dataset_id="test_dataset",
        )

        self.assertIsNone(result)
        sql, job_config = client.query_calls[0]
        self.assertIn("compat_trade_assets_current", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["normalized_name"], "missingplayer")

    def test_compare_trade_assets_rejects_too_many_players(self):
        with self.assertRaises(ValueError):
            trade_assets.compare_trade_assets([str(index) for index in range(20)])

    def test_compare_query_uses_array_parameters(self):
        sql, job_config = trade_assets.build_compare_trade_assets_query(
            project_id="test-project",
            dataset_id="test_dataset",
            lookups=["Brock Purdy", "A.J. Brown"],
        )

        self.assertIn("compat_trade_assets_current", sql)
        self.assertNotIn("market_values", sql)
        params = {
            param.name: getattr(param, "value", getattr(param, "values", None))
            for param in job_config.query_parameters
        }
        self.assertEqual(params["lookups"], ["Brock Purdy", "A.J. Brown"])
        self.assertEqual(params["normalized_lookups"], ["brockpurdy", "ajbrown"])

    def test_unsafe_dataset_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            trade_assets.build_trade_assets_query(
                project_id="test-project",
                dataset_id="bad.dataset",
            )


class TradeAssetMaterializerTests(unittest.TestCase):
    def _source_status(self, **overrides):
        status = {
            table_name: SourceTableStatus(False)
            for table_name in materialize_trade_assets.SOURCE_TABLES
        }
        status.update(overrides)
        return status

    def test_materializer_sql_builds_controlled_market_mart(self):
        source_status = self._source_status(
            market_values=SourceTableStatus(True, row_count=100),
            dim_players_current=SourceTableStatus(True),
            player_identity_bridge=SourceTableStatus(True),
            analytics_pigskin_rankings=SourceTableStatus(True),
            compat_trade_player_history=SourceTableStatus(True),
            analytics_fraud_watch=SourceTableStatus(True),
        )

        sql = materialize_trade_assets.build_trade_assets_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("mart_trade_assets_current", sql)
        self.assertIn("FROM `test-project.test_dataset.market_values`", sql)
        self.assertIn("player_identity_bridge", sql)
        self.assertIn("analytics_pigskin_rankings", sql)
        self.assertIn("compat_trade_player_history", sql)
        self.assertIn("missing_data_flags", sql)

    def test_materializer_sql_handles_missing_rankings_with_flags(self):
        source_status = self._source_status(
            market_values=SourceTableStatus(True, row_count=100),
            dim_players_current=SourceTableStatus(True),
            player_identity_bridge=SourceTableStatus(True),
            analytics_pigskin_rankings=SourceTableStatus(False),
        )

        sql = materialize_trade_assets.build_trade_assets_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("missing_pigskin_ranking_context", sql)
        self.assertIn("missing_rankings_source", sql)
        self.assertNotIn("FROM `test-project.test_dataset.analytics_pigskin_rankings`", sql)

    def test_materializer_sql_handles_missing_market_source(self):
        source_status = self._source_status(
            market_values=SourceTableStatus(False),
            dim_players_current=SourceTableStatus(True),
            player_identity_bridge=SourceTableStatus(True),
        )

        sql = materialize_trade_assets.build_trade_assets_sql(
            project_id="test-project",
            dataset_id="test_dataset",
            source_status=source_status,
        )

        self.assertIn("WHERE FALSE", sql)
        self.assertIn("missing_market_values_source", sql)
        self.assertNotIn("FROM `test-project.test_dataset.market_values`", sql)


if __name__ == "__main__":
    unittest.main()
