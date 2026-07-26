from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import re

from src import nflverse_backfill_plan as plan


REQUIRED_SOURCE_FAMILIES = {
    "pbp",
    "weekly",
    "rosters",
    "rosters_weekly",
    "players",
    "ff_playerids",
    "schedules",
    "teams",
    "team_stats",
    "injuries",
    "depth_charts",
    "snap_counts",
    "participation",
    "ngs_passing",
    "ngs_rushing",
    "ngs_receiving",
    "ftn_charting",
    "draft_picks",
}


class FakeInspector:
    def __init__(self):
        self.calls = []

    def inspect(self, family, season_start, season_end):
        self.calls.append((family.source_family, season_start, season_end))
        return plan.TableInspection(
            table_exists=True,
            current_row_count=0,
            existing_coverage={"covered_seasons": [], "coverage_row_limit": 25},
            warnings=(),
        )


class NflverseBackfillPlanTests(unittest.TestCase):
    def test_registry_contains_required_source_families(self):
        self.assertEqual(REQUIRED_SOURCE_FAMILIES, set(plan.SOURCE_FAMILY_REGISTRY))

    def test_registry_entries_have_required_fields(self):
        for family in plan.SOURCE_FAMILY_REGISTRY.values():
            with self.subTest(family=family.source_family):
                self.assertTrue(family.target_table.startswith("raw_nflverse_"))
                self.assertTrue(family.loader)
                self.assertTrue(family.natural_key_fields)
                self.assertIn("source_refresh_id", family.required_metadata_fields)
                self.assertIn("row_hash", family.required_metadata_fields)
                self.assertTrue(family.future_authorization_gate)

    def test_registry_import_does_not_call_or_import_nflreadpy(self):
        self.assertFalse(hasattr(plan, "nflreadpy"))
        self.assertNotIn("nflreadpy", getattr(plan, "__dict__", {}))

    def test_plan_only_build_output_is_dry_run(self):
        out = plan.build_plan(
            preset="core_historical",
            season_start=2014,
            season_end=2015,
            inspect_bigquery=False,
        )

        self.assertTrue(out["dry_run"])
        self.assertEqual(out["mode"], "historical_backfill")
        self.assertEqual(out["season_start"], 2014)
        self.assertEqual(out["season_end"], 2015)
        self.assertIn("source_family_plans", out)
        self.assertIn("global_warnings", out)
        self.assertIn("blocked_sources", out)
        self.assertIn("next_required_phase", out)

    def test_historical_plan_includes_target_seasons(self):
        out = plan.build_plan(
            source_families=["pbp"],
            season_start=2014,
            season_end=2016,
            inspect_bigquery=False,
        )

        pbp = out["source_family_plans"][0]
        self.assertEqual(pbp["source_family"], "pbp")
        self.assertEqual(pbp["target_seasons"], [2014, 2015, 2016])

    def test_weekly_refresh_requires_week_bounds(self):
        with self.assertRaisesRegex(plan.PlanError, "weekly_refresh mode requires explicit"):
            plan.build_plan(
                preset="core_historical",
                mode="weekly_refresh",
                season_start=2026,
                season_end=2026,
                inspect_bigquery=False,
            )

    def test_non_plan_cli_execution_fails_closed(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = plan.main(["--preset", "core_historical", "--season-start", "2014", "--season-end", "2025"])

        self.assertEqual(code, 2)
        self.assertIn("Live execution is not implemented in Phase 29.5", stderr.getvalue())
        self.assertIn("ALLOW_NFLVERSE_HISTORICAL_BACKFILL", stderr.getvalue())

    def test_future_gates_are_documented_but_not_set(self):
        out = plan.build_plan(
            source_families=["weekly"],
            season_start=2025,
            season_end=2025,
            inspect_bigquery=False,
        )

        self.assertEqual(
            out["source_family_plans"][0]["future_authorization_gate"],
            "ALLOW_NFLVERSE_HISTORICAL_BACKFILL",
        )
        self.assertIsNone(__import__("os").environ.get("ALLOW_NFLVERSE_HISTORICAL_BACKFILL"))

    def test_required_table_mappings(self):
        self.assertEqual(plan.SOURCE_FAMILY_REGISTRY["pbp"].target_table, "raw_nflverse_pbp")
        self.assertEqual(plan.SOURCE_FAMILY_REGISTRY["weekly"].target_table, "raw_nflverse_weekly")
        self.assertEqual(plan.SOURCE_FAMILY_REGISTRY["schedules"].target_table, "raw_nflverse_schedules")

    def test_limited_range_sources_warn(self):
        out = plan.build_plan(
            source_families=["ngs_passing", "ftn_charting"],
            season_start=2014,
            season_end=2025,
            inspect_bigquery=False,
        )

        by_family = {item["source_family"]: item for item in out["source_family_plans"]}
        self.assertIn("2016+", " ".join(by_family["ngs_passing"]["warnings"]))
        self.assertIn("2022+", " ".join(by_family["ftn_charting"]["warnings"]))
        self.assertEqual(by_family["ngs_passing"]["target_seasons"][0], 2016)
        self.assertEqual(by_family["ftn_charting"]["target_seasons"][0], 2022)

    def test_participation_warns_about_route_source(self):
        out = plan.build_plan(
            source_families=["participation"],
            season_start=2025,
            season_end=2025,
            inspect_bigquery=False,
        )

        warnings = " ".join(out["source_family_plans"][0]["warnings"]).lower()
        self.assertIn("true route source", warnings)

    def test_output_uses_fake_read_only_inspector(self):
        inspector = FakeInspector()
        out = plan.build_plan(
            source_families=["pbp", "weekly"],
            season_start=2025,
            season_end=2025,
            inspector=inspector,
        )

        self.assertEqual([call[0] for call in inspector.calls], ["pbp", "weekly"])
        self.assertTrue(all(item["table_exists"] for item in out["source_family_plans"]))
        self.assertEqual(out["source_family_plans"][0]["current_row_count"], 0)

    def test_planner_does_not_reference_legacy_tables_as_write_targets(self):
        forbidden_targets = {
            "play_by_play",
            "weekly_metrics",
            "ngs_passing",
            "ngs_rushing",
            "ngs_receiving",
            "ftn_charting",
            "weekly_snap_counts",
            "injury_reports",
            "depth_charts",
        }
        targets = {family.target_table for family in plan.SOURCE_FAMILY_REGISTRY.values()}
        self.assertFalse(targets & forbidden_targets)

    def test_planner_source_has_no_mutating_bigquery_or_job_calls(self):
        source = Path(plan.__file__).read_text(encoding="utf-8").lower()
        for token in [
            "load_table_from_dataframe",
            "insert_rows",
            "insert_rows_json",
            "create_table(",
            "delete_table",
            "cloud_run_jobs",
            "scheduler",
        ]:
            self.assertNotIn(token, source)
        self.assertNotRegex(source, re.compile(r"\b(import|from)\s+nflreadpy\b"))
        self.assertNotRegex(source, re.compile(r"nflreadpy\.load_\w+\("))

    def test_cli_plan_only_prints_plan(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = plan.main(
                [
                    "--plan-only",
                    "--preset",
                    "core_historical",
                    "--season-start",
                    "2014",
                    "--season-end",
                    "2014",
                    "--skip-bigquery-inspection",
                ]
            )

        self.assertEqual(code, 0)
        self.assertIn("nflverse backfill plan", stdout.getvalue())
        self.assertIn("raw_nflverse_pbp", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
