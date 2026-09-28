from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATION = REPO_ROOT / "bigquery" / "migrations" / "0027__nflverse_historical_feature_warehouse.sql"
CONTRACTS_DIR = REPO_ROOT / "bigquery" / "contracts"
VALIDATIONS_DIR = REPO_ROOT / "bigquery" / "validations"

RAW_CONTRACTS = [
    "raw_nflverse_pbp",
    "raw_nflverse_weekly",
    "raw_nflverse_rosters",
    "raw_nflverse_rosters_weekly",
    "raw_nflverse_players",
    "raw_nflverse_ff_playerids",
    "raw_nflverse_schedules",
    "raw_nflverse_teams",
    "raw_nflverse_team_stats",
    "raw_nflverse_injuries",
    "raw_nflverse_depth_charts",
    "raw_nflverse_snap_counts",
    "raw_nflverse_participation",
    "raw_nflverse_ngs_passing",
    "raw_nflverse_ngs_rushing",
    "raw_nflverse_ngs_receiving",
    "raw_nflverse_ftn_charting",
    "raw_nflverse_draft_picks",
]

STAGING_CONTRACTS = [
    "stg_player_identity",
    "stg_game_context",
    "stg_player_week_stats",
    "stg_team_week_stats",
    "stg_play_player_events",
    "stg_participation_context",
]

FEATURE_CONTRACTS = [
    "player_week_advanced_metrics",
    "player_recent_advanced_metrics_current",
    "team_week_context_metrics",
    "qb_week_environment_metrics",
    "player_role_usage_metrics_current",
    "pigskin_player_context_packet_current",
    "compat_pigskin_player_context_current",
]


def sql_without_comments(sql: str) -> str:
    return "\n".join(line for line in sql.splitlines() if not line.strip().startswith("--"))


class NflverseHistoricalContractTests(unittest.TestCase):
    def test_migration_exists_and_is_additive(self):
        self.assertTrue(MIGRATION.exists(), MIGRATION)
        sql = sql_without_comments(MIGRATION.read_text(encoding="utf-8")).lower()

        self.assertIn("create table if not exists", sql)
        self.assertIn("raw_nflverse_pbp", sql)
        self.assertIn("stg_player_identity", sql)
        self.assertIn("player_week_advanced_metrics", sql)
        self.assertIn("compat_pigskin_player_context_current", sql)
        self.assertNotRegex(sql, r"\b(drop|delete|truncate|insert|merge)\b")
        self.assertNotRegex(sql, r"\balter\s+table\b")

    def test_raw_contracts_exist_and_are_not_safe_surfaces(self):
        for name in RAW_CONTRACTS:
            path = CONTRACTS_DIR / f"{name}.md"
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("source_loader", text)
            self.assertIn("source_refresh_id", text)
            self.assertIn("row_hash", text)
            self.assertIn("not pigskin safe", text)
            self.assertIn("not ui safe", text)

    def test_staging_and_feature_contracts_exist(self):
        for name in STAGING_CONTRACTS + FEATURE_CONTRACTS:
            path = CONTRACTS_DIR / f"{name}.md"
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("purpose", text)
            self.assertIn("safety", text)

    def test_required_validation_files_exist(self):
        expected = {
            "179_raw_nflverse_tables_exist.sql",
            "180_raw_nflverse_load_metadata.sql",
            "181_raw_nflverse_season_week_coverage.sql",
            "182_stg_nflverse_tables_exist.sql",
            "183_stg_player_identity_grain.sql",
            "184_stg_game_context_grain.sql",
            "185_stg_player_week_stats_grain.sql",
            "186_stg_team_week_stats_grain.sql",
            "187_stg_play_player_events_grain.sql",
            "188_stg_participation_context_sanity.sql",
            "189_player_identity_coverage.sql",
            "190_advanced_metrics_tables_exist.sql",
            "191_player_week_advanced_metrics_grain.sql",
            "192_advanced_metrics_range_sanity.sql",
            "193_advanced_metrics_denominator_flags.sql",
            "194_rolling_window_consistency.sql",
            "195_source_freshness_present.sql",
            "196_missing_flags_present.sql",
            "197_compat_pigskin_context_exists.sql",
            "198_compat_pigskin_context_no_raw_dependencies.sql",
            "199_no_route_metrics_without_source.sql",
            "200_no_pressure_metrics_without_source.sql",
        }
        actual = {path.name for path in VALIDATIONS_DIR.glob("*.sql")}
        self.assertTrue(expected.issubset(actual), expected - actual)

    def test_route_and_pressure_metrics_are_blocked_until_true_sources(self):
        participation = (CONTRACTS_DIR / "stg_participation_context.md").read_text(encoding="utf-8").lower()
        role = (CONTRACTS_DIR / "player_role_usage_metrics_current.md").read_text(encoding="utf-8").lower()
        ftn = (CONTRACTS_DIR / "raw_nflverse_ftn_charting.md").read_text(encoding="utf-8").lower()
        validation_route = (VALIDATIONS_DIR / "199_no_route_metrics_without_source.sql").read_text(encoding="utf-8").lower()
        validation_pressure = (VALIDATIONS_DIR / "200_no_pressure_metrics_without_source.sql").read_text(encoding="utf-8").lower()

        self.assertIn("true route source", participation)
        self.assertIn("true route source", role)
        self.assertIn("true pressure source", ftn)
        self.assertIn("route_share is not null", validation_route)
        self.assertIn("pressure", validation_pressure)


if __name__ == "__main__":
    unittest.main()
