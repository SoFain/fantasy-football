from __future__ import annotations

import json
import unittest

from src import segment_packets


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


def fraud_row(**overrides):
    row = {
        "player_id_internal": "pid_1",
        "source_player_key": "00-001",
        "display_name": "Box Score Bob",
        "position": "WR",
        "team": "PIT",
        "opponent": "BAL",
        "season": 2025,
        "week": 7,
        "model_run_id": "run_1",
        "ranking_version": "rank_v1",
        "pigskin_rank_overall": 88,
        "pigskin_rank_position": 34,
        "pigskin_tier": "WR4",
        "market_value": 8000.0,
        "market_value_rank_position": 12,
        "actual_points_recent": 24.0,
        "expected_points_recent": 11.0,
        "points_over_expected_recent": 13.0,
        "usage_score": 28.0,
        "role_stability_score": 34.0,
        "td_dependency_score": 70.0,
        "efficiency_outlier_score": 86.0,
        "rank_vs_value_gap": 22.0,
        "source_fraud_score": 70.0,
        "fraud_label": "Thin role, loud box score",
        "fraud_case": "The box score was louder than the actual role.",
        "what_would_change_mind": "More targets would help.",
        "skill_player_opportunities": 7.0,
        "target_share": 0.12,
        "wopr": 0.25,
        "offense_pct": 0.44,
        "touchdowns": 2,
        "role_fragility_score": 66.0,
        "asset_missing_data_flags": "[]",
        "profile_missing_data_flags": "[]",
    }
    row.update(overrides)
    return FakeRow(row)


def breakout_row(**overrides):
    row = {
        "player_id_internal": "pid_2",
        "source_player_key": "00-002",
        "sleeper_player_id": "202",
        "display_name": "Sneaky Steve",
        "position": "RB",
        "team": "LAC",
        "opponent": "DEN",
        "season": 2025,
        "week": 7,
        "scoring_profile_id": "ppr",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "model_run_id": "run_1",
        "ranking_version": "rank_v1",
        "pigskin_rank_overall": 132,
        "pigskin_rank_position": 44,
        "pigskin_tier": "stash",
        "fantasy_points_per_game": 7.0,
        "snap_share_last_3": 0.54,
        "target_share_last_3": 0.14,
        "rush_share_last_3": 0.31,
        "targets_last_3": 9.0,
        "carries_last_3": 28.0,
        "high_value_touches_last_3": 5.0,
        "usage_trend_score": 74.0,
        "role_growth_score": 80.0,
        "underperformance_signal": 64.0,
        "rostered_rate": 22.0,
        "availability_score": 78.0,
        "matchup_score": 61.0,
        "market_discount_score": 40.0,
        "source_breakout_score": 75.0,
        "candidate_reason": "Role growth is ahead of roster rate.",
        "counterargument": "The sample is small.",
        "snark_hook": "The market is late.",
        "source_freshness_json": json.dumps({"refreshed_at": "2026-06-16T00:00:00Z"}),
        "missing_data_flags": "[]",
    }
    row.update(overrides)
    return FakeRow(row)


class SegmentPacketTests(unittest.TestCase):
    def test_fraud_score_deterministic(self):
        row = fraud_row()

        first = segment_packets.calculate_fraud_score(row)
        second = segment_packets.calculate_fraud_score(row)

        self.assertEqual(first, second)
        self.assertGreater(first, 0)

    def test_breakout_score_deterministic(self):
        row = breakout_row()

        first = segment_packets.calculate_breakout_score(row)
        second = segment_packets.calculate_breakout_score(row)

        self.assertEqual(first, second)
        self.assertGreater(first, 0)

    def test_fraud_packet_contains_required_sections_and_bounded_text(self):
        client = FakeClient(rows=[fraud_row()])

        packets = segment_packets.build_fraud_watch_packets(
            season=2025,
            week=7,
            model_run_id="run_1",
            client=client,
            dataset_id="test_dataset",
        )

        packet = packets[0]
        for key in segment_packets.FRAUD_PACKET_KEYS:
            self.assertIn(key, packet["packet"])
        self.assertLessEqual(len(packet["packet_text"]), segment_packets.PACKET_TEXT_MAX_CHARS)

    def test_breakout_packet_contains_required_sections_and_bounded_text(self):
        client = FakeClient(rows=[breakout_row()])

        packets = segment_packets.build_sleeper_breakout_packets(
            season=2025,
            week=7,
            model_run_id="run_1",
            client=client,
            dataset_id="test_dataset",
        )

        packet = packets[0]
        for key in segment_packets.BREAKOUT_PACKET_KEYS:
            self.assertIn(key, packet["packet"])
        self.assertLessEqual(len(packet["packet_text"]), segment_packets.PACKET_TEXT_MAX_CHARS)

    def test_no_raw_source_table_references_in_helper_queries(self):
        fraud_sql, _ = segment_packets.build_fraud_watch_source_query(
            project_id="test-project",
            dataset_id="test_dataset",
            season=2025,
            week=7,
        )
        breakout_sql, _ = segment_packets.build_sleeper_breakout_source_query(
            project_id="test-project",
            dataset_id="test_dataset",
            season=2025,
            week=7,
        )
        combined = fraud_sql + breakout_sql

        self.assertIn("analytics_fraud_watch", combined)
        self.assertIn("compat_sleeper_watch_candidates", combined)
        self.assertNotIn("weekly_metrics", combined)
        self.assertNotIn("play_by_play", combined)
        self.assertNotIn("sleeper_roster_players", combined)
        self.assertNotIn("market_values", combined)

    def test_missing_expected_points_creates_fraud_missing_flag(self):
        client = FakeClient(rows=[fraud_row(expected_points_recent=None)])

        packet = segment_packets.build_fraud_watch_packets(
            model_run_id="run_1",
            client=client,
            dataset_id="test_dataset",
        )[0]

        self.assertIn("missing_expected_points", json.loads(packet["missing_data_flags"]))

    def test_missing_rostered_rate_creates_breakout_missing_flag(self):
        client = FakeClient(rows=[breakout_row(rostered_rate=None)])

        packet = segment_packets.build_sleeper_breakout_packets(
            model_run_id="run_1",
            client=client,
            dataset_id="test_dataset",
        )[0]

        self.assertIn("missing_rostered_rate", json.loads(packet["missing_data_flags"]))

    def test_fraud_rank_value_gap_increases_score(self):
        low_gap = segment_packets.calculate_fraud_score(fraud_row(rank_vs_value_gap=0.0))
        high_gap = segment_packets.calculate_fraud_score(fraud_row(rank_vs_value_gap=40.0))

        self.assertGreater(high_gap, low_gap)

    def test_breakout_role_growth_increases_score(self):
        low_growth = segment_packets.calculate_breakout_score(breakout_row(role_growth_score=0.0))
        high_growth = segment_packets.calculate_breakout_score(breakout_row(role_growth_score=90.0))

        self.assertGreater(high_growth, low_growth)

    def test_save_get_functions_use_packet_tables(self):
        client = FakeClient(query_results=[
            [],
            [FakeRow({"packet_id": "packet_1", "packet_json": json.dumps({"identity": {}})})],
        ])
        packets = [segment_packets._build_fraud_packet(
            fraud_row(),
            scoring_profile_id="ppr",
            league_type_id="redraft",
            roster_format_id="one_qb",
            model_run_id="run_1",
        )]

        ids = segment_packets.save_fraud_watch_packets(packets, client=client, dataset_id="test_dataset")
        self.assertEqual(ids, [packets[0]["packet_id"]])
        self.assertTrue(any(call[0].endswith(".fraud_watch_packets") for call in client.insert_calls))

        fetched = segment_packets.get_fraud_watch_packets(client=client, dataset_id="test_dataset")
        self.assertEqual(fetched[0]["packet_id"], "packet_1")

    def test_max_limit_enforced(self):
        _, job_config = segment_packets.build_sleeper_breakout_source_query(
            project_id="test-project",
            dataset_id="test_dataset",
            limit=9999,
        )
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["limit"], segment_packets.MAX_PACKET_LIMIT)

    def test_unsafe_dataset_rejected(self):
        with self.assertRaises(ValueError):
            segment_packets.build_fraud_watch_source_query(
                project_id="test-project",
                dataset_id="bad.dataset",
            )


if __name__ == "__main__":
    unittest.main()
