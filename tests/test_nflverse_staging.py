import os
import unittest
from unittest.mock import patch

from src import nflverse_staging as staging


class FakeQueryJob:
    def __init__(self, row, affected_rows=None):
        self._row = row
        self.num_dml_affected_rows = affected_rows

    def result(self):
        if self._row is None:
            return []
        return [self._row]


class FakeClient:
    def __init__(self):
        self.queries = []

    def query(self, sql):
        self.queries.append(sql)
        if "MERGE " in sql:
            return FakeQueryJob(None, affected_rows=10)
        if "bounded_row_count" in sql:
            return FakeQueryJob(
                {
                    "bounded_row_count": 10,
                    "rows_2014": 10,
                    "min_season": 2014,
                    "max_season": 2014,
                    "missing_source_freshness_rows": 0,
                    "missing_flags_rows": 0,
                    "duplicate_key_count": 0,
                }
            )
        return FakeQueryJob(
            {
                "planned_row_count": 10,
                "source_row_count": 12,
                "duplicate_key_count": 0,
                "missing_identity_count": 2,
            }
        )


class NflverseStagingTests(unittest.TestCase):
    def _args(self, *extra):
        return staging.parse_args(["--season-start", "2014", "--season-end", "2014", *extra])

    def test_all_six_staging_targets_are_registered(self):
        self.assertEqual(
            set(staging.TARGETS),
            {
                "stg_player_identity",
                "stg_game_context",
                "stg_player_week_stats",
                "stg_team_week_stats",
                "stg_play_player_events",
                "stg_participation_context",
            },
        )

    def test_cli_defaults_to_no_write_and_all_targets(self):
        args = self._args()
        summary = staging.build_summary(args, client_factory=FakeClient)

        self.assertTrue(summary["dry_run"])
        self.assertFalse(summary["wrote"])
        self.assertEqual(set(summary["selected_staging_targets"]), set(staging.TARGETS))

    def test_live_write_fails_closed(self):
        args = self._args("--write")

        with self.assertRaisesRegex(staging.StagingPlanError, staging.STAGING_MATERIALIZATION_GATE):
            staging.build_summary(args, client_factory=FakeClient)

    def test_unrelated_gates_do_not_authorize_write(self):
        args = self._args("--write")

        with patch.dict(os.environ, {"ALLOW_NFLVERSE_HISTORICAL_BACKFILL": "true"}, clear=False):
            with self.assertRaisesRegex(staging.StagingPlanError, staging.STAGING_MATERIALIZATION_GATE):
                staging.build_summary(args, client_factory=FakeClient)

    def test_authorized_write_uses_merge_for_selected_staging_target(self):
        args = self._args("--write", "--target", "stg_game_context")
        client = FakeClient()

        with patch.dict(os.environ, {staging.STAGING_MATERIALIZATION_GATE: "true"}, clear=False):
            summary = staging.build_summary(args, client_factory=lambda: client)

        self.assertFalse(summary["dry_run"])
        self.assertTrue(summary["wrote"])
        self.assertEqual(summary["phase"], "29.8")
        merge_sql = next(sql for sql in client.queries if "MERGE " in sql)
        self.assertIn(".stg_game_context` AS T", merge_sql)
        self.assertIn("raw_nflverse_schedules", merge_sql)
        self.assertNotIn("player_week_advanced_metrics", merge_sql)
        self.assertNotIn("pigskin_player_context_packet_current", merge_sql)

    def test_generated_sql_uses_raw_nflverse_sources_and_not_legacy_or_feature_tables(self):
        blocked_names = set(staging.LEGACY_TABLES) | set(staging.FEATURE_TABLES)
        for target in staging.TARGETS:
            plan = staging.build_target_plan(target, "project", "dataset", 2014, 2014, None, None)
            sql = f"{plan.sql}\n{plan.diagnostic_sql}"
            self.assertIn("raw_nflverse_", sql)
            for blocked in blocked_names:
                self.assertNotIn(f".{blocked}`", sql)
                self.assertNotIn(f"`{blocked}`", sql)
            self.assertNotIn("INSERT ", sql.upper())
            self.assertNotIn("MERGE ", sql.upper())
            self.assertNotIn("DELETE ", sql.upper())

    def test_participation_keeps_route_share_null_without_true_route_source(self):
        plan = staging.build_target_plan("stg_participation_context", "project", "dataset", 2014, 2014, None, None)

        self.assertIn("FALSE AS has_true_route_source", plan.sql)
        self.assertIn("CAST(NULL AS FLOAT64) AS route_share", plan.sql)
        self.assertIn("s.player_id = i.pfr_id", plan.sql)
        self.assertIn("raw_pfr_player_id", plan.sql)

    def test_identity_sql_does_not_force_ambiguous_name_only_joins(self):
        plan = staging.build_target_plan("stg_player_identity", "project", "dataset", 2014, 2014, None, None)

        self.assertNotIn("player_name = ", plan.sql)
        self.assertNotIn("rw.player_name = ", plan.sql)
        self.assertIn("no_name_only_join", plan.sql)

    def test_dry_run_summary_contains_counts_and_warnings(self):
        args = self._args("--target", "stg_participation_context")
        client = FakeClient()
        summary = staging.build_summary(args, client_factory=lambda: client)
        target = summary["target_summaries"][0]

        self.assertEqual(target["planned_row_count"], 10)
        self.assertEqual(target["source_row_count"], 12)
        self.assertEqual(target["duplicate_key_count"], 0)
        self.assertIn("warnings", target)
        self.assertEqual(target["recommended_write_readiness"], "ready with warnings")
        self.assertEqual(len(client.queries), 1)

    def test_plan_only_target_selection_is_no_write(self):
        args = self._args("--plan-only", "--target", "stg_game_context")
        summary = staging.build_summary(args, client_factory=FakeClient)

        self.assertTrue(summary["dry_run"])
        self.assertFalse(summary["wrote"])
        self.assertEqual(summary["selected_staging_targets"], ["stg_game_context"])

    def test_merge_sql_uses_null_safe_contract_grain(self):
        plan = staging.build_target_plan("stg_participation_context", "project", "dataset", 2014, 2014, None, None)
        merge_sql = staging.build_merge_sql(plan, "project", "dataset")

        self.assertIn("MERGE `project.dataset.stg_participation_context`", merge_sql)
        for key in staging.TARGET_GRAINS["stg_participation_context"]:
            self.assertIn(f"T.`{key}` = S.`{key}`", merge_sql)
            self.assertIn(f"T.`{key}` IS NULL AND S.`{key}` IS NULL", merge_sql)
        self.assertNotIn("trade_player_scores", merge_sql)
        self.assertNotIn("player_week_advanced_metrics", merge_sql)
        self.assertNotIn("DELETE ", merge_sql.upper())
        self.assertNotIn("TRUNCATE", merge_sql.upper())


if __name__ == "__main__":
    unittest.main()
