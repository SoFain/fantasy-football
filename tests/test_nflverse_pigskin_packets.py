import os
import unittest
from unittest.mock import patch

from src import nflverse_pigskin_packets as packets


class FakeQueryJob:
    def __init__(self, rows, affected_rows=None):
        self._rows = rows
        self.num_dml_affected_rows = affected_rows

    def result(self):
        return self._rows


class FakeClient:
    def __init__(self):
        self.queries = []

    def query(self, sql):
        self.queries.append(sql)
        if "MERGE " in sql:
            return FakeQueryJob([], affected_rows=482)
        if "bounded_row_count" in sql:
            return FakeQueryJob(
                [
                    {
                        "bounded_row_count": 482,
                        "min_source_season": 2014,
                        "max_source_season": 2014,
                        "min_as_of_week": 17,
                        "max_as_of_week": 21,
                        "packet_version_count": 1,
                        "source_metric_version_count": 1,
                        "missing_packet_json_count": 0,
                        "missing_packet_text_count": 0,
                        "missing_source_freshness_count": 0,
                        "missing_blocked_metric_flag_count": 0,
                        "rows_with_packet_warnings": 10,
                        "duplicate_packet_grain_count": 0,
                    }
                ]
            )
        if "GROUP BY position" in sql:
            return FakeQueryJob([{"position": "WR", "candidate_count": 1, "null_wopr_rows": 0}])
        if "table_name" in sql and "player_recent_advanced_metrics_current" in sql and "UNION ALL" in sql:
            return FakeQueryJob(
                [
                    {"table_name": "player_recent_advanced_metrics_current", "row_count": 1854},
                    {"table_name": "player_role_usage_metrics_current", "row_count": 1854},
                ]
            )
        if "candidate_count" in sql:
            return FakeQueryJob(
                [
                    {
                        "candidate_count": 1,
                        "qb_count": 0,
                        "rb_count": 0,
                        "wr_count": 1,
                        "te_count": 0,
                        "missing_identity_rows": 0,
                        "missing_source_freshness_rows": 0,
                        "missing_flags_rows": 0,
                    }
                ]
            )
        return FakeQueryJob(
            [
                {
                    "as_of_season": 2014,
                    "as_of_week": 17,
                    "player_id_internal": "00-0031234",
                    "player_name": "O.Beckham",
                    "position": "WR",
                    "team": "NYG",
                    "targets": 21.0,
                    "carries": 0.0,
                    "opportunities": 21.0,
                    "weighted_opportunity": 52.5,
                    "target_share": 0.42,
                    "carry_share": 0.0,
                    "opportunity_share": 0.31,
                    "snap_share": 0.92,
                    "air_yards_share": 0.62,
                    "wopr": 1.04,
                    "adot": 13.2,
                    "racr": 0.9,
                    "epa_total": 12.0,
                    "epa_per_opportunity": 0.57,
                    "success_rate": 0.62,
                    "cpoe": None,
                    "dropbacks": None,
                    "pass_attempts": None,
                    "epa_per_dropback": None,
                    "qb_cpoe": None,
                    "qb_adot": None,
                    "deep_attempt_rate": None,
                    "team_epa_per_play": 0.2,
                    "team_success_rate": 0.52,
                    "neutral_pass_rate": 0.55,
                    "opponent_epa_allowed": -0.1,
                    "role_source_freshness_json": "{}",
                    "recent_source_freshness_json": "{}",
                    "player_week_source_freshness_json": "{}",
                    "qb_source_freshness_json": None,
                    "team_source_freshness_json": "{}",
                    "role_missing_data_flags": "{}",
                    "recent_missing_data_flags": "{}",
                    "player_week_missing_data_flags": "{}",
                    "qb_missing_data_flags": None,
                    "team_missing_data_flags": "{}",
                }
            ]
        )


class NflversePigskinPacketsTests(unittest.TestCase):
    def _args(self, *extra):
        return packets.parse_args(["--season-start", "2014", "--season-end", "2014", *extra])

    def test_cli_defaults_to_no_write(self):
        args = self._args("--plan-only")
        summary = packets.build_summary(args, client_factory=FakeClient, run_diagnostics=False)

        self.assertTrue(summary["dry_run"])
        self.assertFalse(summary["wrote"])
        self.assertTrue(summary["write_supported"])
        self.assertEqual(summary["positions"], ["QB", "RB", "WR", "TE"])

    def test_write_fails_closed(self):
        args = self._args("--write")

        with self.assertRaisesRegex(packets.PigskinPacketPlanError, packets.PIGSKIN_PACKET_GATE):
            packets.build_summary(args, client_factory=FakeClient)

    def test_unrelated_gate_is_not_sufficient_for_phase_29_12_write(self):
        args = self._args("--write")

        with patch.dict(os.environ, {"ALLOW_ADVANCED_METRICS_MATERIALIZATION": "true"}, clear=False):
            with self.assertRaisesRegex(packets.PigskinPacketPlanError, packets.PIGSKIN_PACKET_GATE):
                packets.build_summary(args, client_factory=FakeClient)

    def test_authorized_write_uses_packet_table_merge_only(self):
        args = self._args(
            "--write",
            "--packet-version",
            "nflverse_pigskin_packet_v0_2014_001",
            "--source-metric-version",
            "nflverse_adv_metrics_v0_2014_001",
        )
        client = FakeClient()

        with patch.dict(os.environ, {packets.PIGSKIN_PACKET_GATE: "true"}, clear=False):
            summary = packets.build_summary(args, client_factory=lambda: client)

        self.assertTrue(summary["wrote"])
        self.assertEqual(summary["phase"], "29.12")
        merge_sql = next(query for query in client.queries if "MERGE " in query)
        self.assertIn(".pigskin_player_context_packet_current` AS T", merge_sql)
        self.assertIn("player_recent_advanced_metrics_current", merge_sql)
        self.assertIn("player_role_usage_metrics_current", merge_sql)
        self.assertNotIn("raw_nflverse_", merge_sql)
        self.assertNotIn("play_by_play", merge_sql)
        self.assertNotIn("weekly_metrics", merge_sql)
        self.assertNotIn("compat_pigskin_player_context_current", merge_sql)
        self.assertEqual(summary["write_result"]["post_write"]["bounded_row_count"], 482)

    def test_packet_sql_uses_safe_feature_sources_only(self):
        args = self._args("--position", "WR", "--limit", "10")
        plan = packets.build_plan(args)
        sql = f"{plan.sql}\n{plan.diagnostics_sql}"

        for table in packets.SAFE_SOURCE_TABLES:
            self.assertIn(table, sql)
        for blocked in packets.BLOCKED_DEPENDENCIES:
            self.assertNotIn(blocked, sql)
        for write_token in ("INSERT ", "MERGE ", "DELETE ", "TRUNCATE", "UPDATE "):
            self.assertNotIn(write_token, sql.upper())

    def test_merge_sql_uses_packet_grain_and_safe_sources(self):
        args = self._args("--packet-version", "packet_v", "--source-metric-version", "metric_v")
        merge_sql = packets.build_merge_sql(args)

        for key in packets.PACKET_GRAIN:
            self.assertIn(f"T.`{key}` = S.`{key}`", merge_sql)
            self.assertIn(f"T.`{key}` IS NULL AND S.`{key}` IS NULL", merge_sql)
        self.assertIn("MERGE `fantasy-football-498121.fantasy_football_brain.pigskin_player_context_packet_current`", merge_sql)
        self.assertNotIn("raw_nflverse_", merge_sql)
        self.assertNotIn("compat_pigskin_player_context_current", merge_sql)

    def test_player_universe_filter_is_fantasy_and_opportunity_based(self):
        args = self._args()
        sql = packets.build_packet_sql(args)

        self.assertIn("role.position IN ('QB', 'RB', 'WR', 'TE')", sql)
        self.assertIn("COALESCE(pw.targets, 0) > 0", sql)
        self.assertIn("COALESCE(pw.carries, 0) > 0", sql)
        self.assertIn("COALESCE(qb.dropbacks, 0) > 0", sql)

    def test_packet_json_includes_required_sections_and_blocked_metrics(self):
        row = {
            "player_id_internal": "00-0031234",
            "player_name": "O.Beckham",
            "position": "WR",
            "team": "NYG",
            "as_of_season": 2014,
            "as_of_week": 17,
            "targets": 21,
            "carries": 0,
            "weighted_opportunity": 52.5,
            "wopr": None,
            "air_yards_share": None,
            "snap_share": None,
            "player_week_missing_data_flags": '{"zero_player_opportunity_denominator": false}',
        }

        packet = packets.packet_json_for_row(row)

        for section in (
            "identity",
            "usage_summary",
            "receiving_air_yards",
            "efficiency_summary",
            "qb_context",
            "team_context",
            "blocked_metrics",
            "source_freshness",
            "warnings",
        ):
            self.assertIn(section, packet)
        self.assertIn("route_share", packet["blocked_metrics"])
        self.assertIn("missing WOPR or air yards share", packet["warnings"])
        self.assertIn("missing snap share", packet["warnings"])

    def test_build_summary_runs_read_only_queries_and_examples(self):
        args = self._args("--limit", "1")
        client = FakeClient()
        summary = packets.build_summary(args, client_factory=lambda: client)

        self.assertFalse(summary["wrote"])
        self.assertEqual(summary["diagnostics"]["candidate_count"], 1)
        self.assertEqual(summary["packet_examples"][0]["player_name"], "O.Beckham")
        self.assertTrue(client.queries)
        self.assertFalse(any("pigskin_player_context_packet_current" in query for query in client.queries))

    def test_player_name_filter_supports_initial_last_name_variant(self):
        args = self._args("--player-name", "Aaron Rodgers")
        sql = packets.build_packet_sql(args)

        self.assertIn("'arodgers'", sql)
        self.assertIn("'aaronrodgers'", sql)


if __name__ == "__main__":
    unittest.main()
