import os
import unittest
from unittest.mock import patch

from src import nflverse_advanced_metrics as metrics


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
            return FakeQueryJob([], affected_rows=10)
        if "bounded_row_count" in sql:
            return FakeQueryJob(
                [
                    {
                        "bounded_row_count": 10,
                        "rows_2014": 10,
                        "min_season": 2014,
                        "max_season": 2014,
                        "min_week": 1,
                        "max_week": 21,
                        "metric_version_count": 1,
                        "feature_run_id_count": 1,
                        "missing_source_freshness_rows": 0,
                        "missing_flags_rows": 0,
                        "duplicate_key_count": 0,
                    }
                ]
            )
        if "source_layer" in sql and "field_name" in sql:
            return FakeQueryJob(
                [
                    {
                        "field_name": "stg_play_player_events.red_zone_flag",
                        "source_layer": "staging",
                        "source_rows": 10,
                        "non_null_count": 10,
                        "true_count": 0,
                        "source_exists": True,
                        "v0_status": "blocked",
                    },
                    {
                        "field_name": "stg_play_player_events.target",
                        "source_layer": "staging",
                        "source_rows": 10,
                        "non_null_count": 10,
                        "true_count": 8,
                        "source_exists": True,
                        "v0_status": "safe",
                    },
                ]
            )
        if "base_rows_available" in sql:
            return FakeQueryJob(
                [
                    {
                        "planned_row_count": 0,
                        "source_row_count": 0,
                        "duplicate_key_count": 0,
                        "base_rows_available": 0,
                        "missing_base_rows": 1,
                    }
                ]
            )
        return FakeQueryJob(
            [
                {
                    "planned_row_count": 10,
                    "source_row_count": 12,
                    "duplicate_key_count": 0,
                    "missing_identity_count": 2,
                    "missing_team_context_count": 0,
                    "red_zone_high_value_metrics_blocked_count": 10,
                }
            ]
        )


class NflverseAdvancedMetricsTests(unittest.TestCase):
    def _args(self, *extra):
        return metrics.parse_args(["--season-start", "2014", "--season-end", "2014", *extra])

    def test_cli_defaults_to_no_write_and_base_targets(self):
        args = self._args()
        summary = metrics.build_summary(args, client_factory=FakeClient)

        self.assertTrue(summary["dry_run"])
        self.assertFalse(summary["wrote"])
        self.assertEqual(summary["selected_targets"], list(metrics.BASE_TARGETS))

    def test_write_fails_closed(self):
        args = self._args("--write")

        with self.assertRaisesRegex(metrics.AdvancedMetricsPlanError, metrics.ADVANCED_METRICS_GATE):
            metrics.build_summary(args, client_factory=FakeClient)

    def test_authorized_write_uses_merge_for_base_target(self):
        args = self._args(
            "--write",
            "--target",
            "team_week_context_metrics",
            "--metric-version",
            "nflverse_adv_metrics_v0_2014_001",
        )
        client = FakeClient()

        with patch.dict(os.environ, {metrics.ADVANCED_METRICS_GATE: "true"}, clear=False):
            summary = metrics.build_summary(args, client_factory=lambda: client)

        self.assertFalse(summary["dry_run"])
        self.assertTrue(summary["wrote"])
        self.assertEqual(summary["phase"], "29.10")
        merge_sql = next(sql for sql in client.queries if "MERGE " in sql)
        self.assertIn(".team_week_context_metrics` AS T", merge_sql)
        self.assertIn("stg_team_week_stats", merge_sql)
        self.assertNotIn("raw_nflverse_", merge_sql)
        self.assertNotIn("pigskin_player_context_packet_current", merge_sql)

    def test_write_rejects_current_targets_even_with_gate(self):
        args = self._args("--write", "--target", "player_recent_advanced_metrics_current")

        with patch.dict(os.environ, {metrics.ADVANCED_METRICS_GATE: "true"}, clear=False):
            with self.assertRaisesRegex(metrics.AdvancedMetricsPlanError, "base advanced metric targets"):
                metrics.build_summary(args, client_factory=FakeClient)

    def test_all_feature_targets_are_registered(self):
        self.assertEqual(
            set(metrics.TARGETS),
            {
                "player_week_advanced_metrics",
                "team_week_context_metrics",
                "qb_week_environment_metrics",
                "player_recent_advanced_metrics_current",
                "player_role_usage_metrics_current",
            },
        )

    def test_base_generated_sql_uses_staging_tables_only(self):
        for target in metrics.BASE_TARGETS:
            plan = metrics.build_target_plan(target, "project", "dataset", 2014, 2014, None, None)
            sql = f"{plan.sql}\n{plan.diagnostic_sql}"
            self.assertIn("stg_", sql)
            for blocked in ("raw_nflverse_", "play_by_play", "weekly_metrics", "pigskin_player_context_packet_current"):
                self.assertNotIn(blocked, sql)
            for write_token in ("INSERT ", "MERGE ", "DELETE ", "TRUNCATE"):
                self.assertNotIn(write_token, sql.upper())

    def test_player_week_sql_contains_wopr_and_denominator_handling(self):
        plan = metrics.build_target_plan("player_week_advanced_metrics", "project", "dataset", 2014, 2014, None, None)

        self.assertIn("1.5 * SAFE_DIVIDE", plan.sql)
        self.assertIn("0.7 * LEAST(1.0, GREATEST(0.0, SAFE_DIVIDE", plan.sql)
        self.assertIn("NULLIF(t.team_targets, 0)", plan.sql)
        self.assertIn("NULLIF(t.team_air_yards, 0)", plan.sql)
        self.assertIn("LEAST(1.0, GREATEST(0.0, SAFE_DIVIDE", plan.sql)
        self.assertIn("red_zone_high_value_metrics_blocked", plan.sql)

    def test_blocked_metric_list_keeps_route_and_red_zone_metrics_blocked(self):
        args = self._args("--target", "player_week_advanced_metrics")
        summary = metrics.build_summary(args, client_factory=FakeClient)

        self.assertIn("route_share", summary["blocked_metrics"])
        self.assertIn("red_zone_touches", summary["blocked_metrics"])
        self.assertIn("touchdown_rates", summary["blocked_metrics"])
        self.assertEqual(summary["target_summaries"][0]["recommended_write_readiness"], "ready with warnings")

    def test_team_week_sql_flags_pass_rate_over_expected_unavailable(self):
        plan = metrics.build_target_plan("team_week_context_metrics", "project", "dataset", 2014, 2014, None, None)

        self.assertIn("CAST(NULL AS FLOAT64) AS pass_rate_over_expected", plan.sql)
        self.assertIn("pass_rate_over_expected_unavailable", plan.sql)

    def test_current_placeholders_require_base_rows(self):
        args = self._args("--target", "player_recent_advanced_metrics_current")
        summary = metrics.build_summary(args, client_factory=FakeClient)

        self.assertEqual(summary["target_summaries"][0]["recommended_write_readiness"], "blocked")
        self.assertIn("requires player_week_advanced_metrics", summary["target_summaries"][0]["planned_sql"])

    def test_merge_sql_uses_base_grain_and_no_destructive_tokens(self):
        plan = metrics.build_target_plan(
            "player_week_advanced_metrics",
            "project",
            "dataset",
            2014,
            2014,
            None,
            None,
            "nflverse_adv_metrics_v0_2014_001",
        )
        merge_sql = metrics.build_merge_sql(plan, "project", "dataset")

        self.assertIn("MERGE `project.dataset.player_week_advanced_metrics`", merge_sql)
        for key in metrics.TARGET_GRAINS["player_week_advanced_metrics"]:
            self.assertIn(f"T.`{key}` = S.`{key}`", merge_sql)
            self.assertIn(f"T.`{key}` IS NULL AND S.`{key}` IS NULL", merge_sql)
        self.assertNotIn("TRUNCATE", merge_sql.upper())
        self.assertNotIn("DELETE ", merge_sql.upper())
        self.assertNotIn("pigskin_player_context_packet_current", merge_sql)

    def test_dry_run_output_contains_row_counts_and_coverage_warnings(self):
        args = self._args("--all-targets")
        summary = metrics.build_summary(args, client_factory=FakeClient)

        self.assertEqual(summary["target_summaries"][0]["planned_row_count"], 10)
        self.assertIn("metric_availability_matrix", summary)
        self.assertTrue(summary["source_field_audit"])
        self.assertTrue(summary["target_summaries"][0]["warnings"])


if __name__ == "__main__":
    unittest.main()
