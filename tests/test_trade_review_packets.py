from __future__ import annotations

import json
import unittest

from src import trade_review_packets


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

    def __init__(self, rows=None, query_results=None):
        self.rows = rows or []
        self.query_results = list(query_results or [])
        self.query_calls = []
        self.insert_calls = []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        if self.query_results:
            return FakeJob(self.query_results.pop(0))
        return FakeJob(self.rows)

    def insert_rows_json(self, table_id, rows):
        self.insert_calls.append((table_id, rows))
        return []


def sample_asset(**overrides):
    row = {
        "player_id_internal": "gsis_1",
        "source_player_key": "00-001",
        "sleeper_player_id": "101",
        "gsis_id": "00-001",
        "display_name": "A.J. Brown",
        "market_player_name": "A.J. Brown",
        "normalized_name": "ajbrown",
        "position": "WR",
        "team": "PHI",
        "age": 28.0,
        "market_value": 26000.0,
        "risk_adjusted_trade_value": 25000.0,
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "model_run_id": "run_1",
        "ranking_version": "rank_v1",
        "pigskin_rank_overall": 18,
        "pigskin_rank_position": 7,
        "pigskin_tier": "WR1",
        "pigskin_risk_score": 12.0,
        "pigskin_breakout_score": 35.0,
        "pigskin_fraud_risk_score": 8.0,
        "recent_fantasy_points_per_game": 17.0,
        "recent_trend_label": "stable",
        "asset_source_freshness_json": json.dumps({
            "market_source_table": "market_values",
            "market_snapshot_date": "2026-06-13",
            "refreshed_at": "2026-06-16T00:00:00Z",
        }),
        "asset_missing_data_flags": "[]",
        "profile_missing_data_flags": "[]",
        "history_missing_data_flags": "[]",
    }
    row.update(overrides)
    return FakeRow(row)


class TradeReviewPacketTests(unittest.TestCase):
    def test_normalize_trade_side_handles_names_and_ids(self):
        result = trade_review_packets.normalize_trade_side([
            "A.J. Brown",
            {"player_id_internal": "gsis_2", "display_name": "Brock Purdy"},
        ])

        self.assertEqual(result[0]["lookup"], "A.J. Brown")
        self.assertEqual(result[0]["normalized_lookup"], "ajbrown")
        self.assertEqual(result[1]["lookup"], "gsis_2")

    def test_max_assets_per_side_enforced(self):
        with self.assertRaises(ValueError):
            trade_review_packets.normalize_trade_side([f"Player {index}" for index in range(10)])

    def test_unknown_asset_returns_clean_error(self):
        client = FakeClient(rows=[])

        with self.assertRaises(trade_review_packets.UnknownTradeAssetError) as exc:
            trade_review_packets.resolve_trade_assets(["Missing Player"], client=client, dataset_id="test_dataset")

        self.assertEqual(exc.exception.unknown_assets, ["Missing Player"])

    def test_resolve_query_uses_curated_compat_objects(self):
        sql, job_config = trade_review_packets.build_resolve_trade_assets_query(
            project_id="test-project",
            dataset_id="test_dataset",
            lookups=["A.J. Brown"],
            normalized_lookups=["ajbrown"],
        )

        self.assertIn("compat_trade_assets_current", sql)
        self.assertIn("compat_trade_player_history", sql)
        self.assertIn("compat_player_profiles_current", sql)
        self.assertNotIn("market_values", sql)
        self.assertNotIn("weekly_metrics", sql)
        self.assertNotIn("sleeper_roster_players", sql)
        params = {param.name: getattr(param, "value", getattr(param, "values", None)) for param in job_config.query_parameters}
        self.assertEqual(params["scoring_profile_id"], "ppr")

    def test_value_formula_is_deterministic(self):
        asset = sample_asset()
        context = {"league_type_id": "redraft", "roster_format_id": "one_qb", "scoring_profile_id": "ppr"}

        first = trade_review_packets.calculate_trade_asset_value(asset, context)
        second = trade_review_packets.calculate_trade_asset_value(asset, context)

        self.assertEqual(first, second)
        self.assertGreater(first["value"], 0)

    def test_dynasty_changes_age_weighting(self):
        young = sample_asset(age=22.0, position="WR")
        old = sample_asset(age=31.0, position="WR")
        dynasty_context = {"league_type_id": "dynasty", "roster_format_id": "one_qb", "scoring_profile_id": "ppr"}

        young_value = trade_review_packets.calculate_trade_asset_value(young, dynasty_context)
        old_value = trade_review_packets.calculate_trade_asset_value(old, dynasty_context)

        self.assertGreater(young_value["dynasty_value"], old_value["dynasty_value"])

    def test_superflex_can_alter_qb_value(self):
        qb = sample_asset(display_name="Brock Purdy", normalized_name="brockpurdy", position="QB", pigskin_rank_position=10)
        one_qb = trade_review_packets.calculate_trade_asset_value(qb, {"league_type_id": "redraft", "roster_format_id": "one_qb"})
        superflex = trade_review_packets.calculate_trade_asset_value(qb, {"league_type_id": "redraft", "roster_format_id": "superflex"})

        self.assertGreater(superflex["value"], one_qb["value"])

    def test_side_winner_calculation(self):
        side_a = [sample_asset(display_name="A.J. Brown", market_value=26000.0)]
        side_b = [sample_asset(display_name="Depth WR", market_value=4000.0, pigskin_rank_overall=180, pigskin_rank_position=70)]

        result = trade_review_packets.compare_trade_sides(side_a, side_b, {"league_type_id": "redraft", "roster_format_id": "one_qb"})

        self.assertEqual(result["recommended_winner"], "side_a")
        self.assertGreater(result["value_delta"], 0)

    def test_packet_includes_required_sections_and_bounded_text(self):
        rows = [
            sample_asset(display_name="A.J. Brown", normalized_name="ajbrown", market_value=26000.0),
            sample_asset(
                player_id_internal="gsis_2",
                display_name="Brock Purdy",
                market_player_name="Brock Purdy",
                normalized_name="brockpurdy",
                position="QB",
                market_value=16000.0,
                pigskin_rank_overall=70,
                pigskin_rank_position=12,
            ),
        ]
        client = FakeClient(rows=rows)

        packet = trade_review_packets.build_trade_review_packet(
            ["A.J. Brown"],
            ["Brock Purdy"],
            client=client,
            dataset_id="test_dataset",
        )

        for key in trade_review_packets.PACKET_KEYS:
            self.assertIn(key, packet["packet"])
        self.assertLessEqual(len(packet["packet_text"]), trade_review_packets.PACKET_TEXT_MAX_CHARS)
        self.assertIn("packet_json", packet)
        self.assertNotIn("market_values", packet["packet_json"])
        self.assertNotIn("weekly_metrics", packet["packet_json"])

    def test_save_get_functions_use_packet_tables(self):
        packet_row = FakeRow({"trade_review_id": "trade_review_1", "packet_json": json.dumps({"verdict": {}})})
        player_row = FakeRow({"trade_review_id": "trade_review_1", "side": "A", "display_name": "A.J. Brown"})
        client = FakeClient(query_results=[[packet_row], [player_row]])
        packet = {
            "trade_review_id": "trade_review_1",
            "request_row": {"trade_review_id": "trade_review_1"},
            "packet_row": {"trade_review_id": "trade_review_1"},
            "player_rows": [{"trade_review_id": "trade_review_1", "side": "A"}],
        }

        trade_review_packets.save_trade_review_packet(packet, client=client, dataset_id="test_dataset")
        saved_tables = [table_id for table_id, _ in client.insert_calls]
        self.assertTrue(any(table_id.endswith(".trade_review_requests") for table_id in saved_tables))
        self.assertTrue(any(table_id.endswith(".trade_review_packets") for table_id in saved_tables))
        self.assertTrue(any(table_id.endswith(".trade_review_packet_players") for table_id in saved_tables))

        fetched = trade_review_packets.get_trade_review_packet("trade_review_1", client=client, dataset_id="test_dataset")
        self.assertEqual(fetched["trade_review_id"], "trade_review_1")
        self.assertEqual(fetched["player_rows"][0]["display_name"], "A.J. Brown")

    def test_unsafe_dataset_rejected(self):
        with self.assertRaises(ValueError):
            trade_review_packets.build_resolve_trade_assets_query(
                project_id="test-project",
                dataset_id="bad.dataset",
                lookups=["A.J. Brown"],
                normalized_lookups=["ajbrown"],
            )


if __name__ == "__main__":
    unittest.main()
