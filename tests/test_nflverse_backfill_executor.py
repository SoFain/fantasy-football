from __future__ import annotations

import os
import sys
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone
from contextlib import redirect_stderr, redirect_stdout
import io
from unittest.mock import patch

import pandas as pd

from src import nflverse_backfill as backfill
from src.nflverse_backfill_plan import SOURCE_FAMILY_REGISTRY


@dataclass(frozen=True)
class Field:
    name: str
    field_type: str = "STRING"


class NflverseBackfillExecutorTests(unittest.TestCase):
    def test_write_without_gate_fails_before_loader_call(self):
        with patch.dict(os.environ, {"ALLOW_NFLVERSE_HISTORICAL_BACKFILL": ""}, clear=False):
            with patch("src.nflverse_backfill._call_loader", side_effect=AssertionError("loader called")):
                with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                    code = backfill.main(
                        [
                            "--preset",
                            "core_historical",
                            "--season-start",
                            "2014",
                            "--season-end",
                            "2014",
                            "--write",
                        ]
                    )

        self.assertEqual(code, 2)

    def test_dry_run_does_not_import_or_call_nflreadpy(self):
        sys.modules.pop("nflreadpy", None)
        with patch("src.nflverse_backfill._call_loader", side_effect=AssertionError("loader called")):
            with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                code = backfill.main(
                    [
                        "--preset",
                        "core_historical",
                        "--season-start",
                        "2014",
                        "--season-end",
                        "2014",
                        "--dry-run",
                    ]
                )

        self.assertEqual(code, 0)
        self.assertNotIn("nflreadpy", sys.modules)

    def test_registry_maps_only_to_raw_nflverse_targets(self):
        for family in SOURCE_FAMILY_REGISTRY.values():
            with self.subTest(family=family.source_family):
                self.assertTrue(family.target_table.startswith("raw_nflverse_"))

    def test_no_legacy_source_table_is_write_target(self):
        targets = {family.target_table for family in SOURCE_FAMILY_REGISTRY.values()}
        self.assertFalse(targets & backfill.LEGACY_WRITE_TARGETS)

    def test_metadata_fields_are_added_and_extra_columns_ignored(self):
        family = SOURCE_FAMILY_REGISTRY["weekly"]
        source_df = pd.DataFrame(
            [
                {
                    "season": 2014,
                    "week": 1,
                    "player_id": "00-abc",
                    "recent_team": "PHI",
                    "player_name": "Example Player",
                    "extra_source_column": "drop me",
                }
            ]
        )
        schema = [
            Field("season", "INTEGER"),
            Field("week", "INTEGER"),
            Field("player_id"),
            Field("team"),
            Field("player_name"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
            Field("raw_payload_json"),
            Field("missing_target_column"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2014,
            season_end=2014,
        )

        row = prepared.dataframe.iloc[0].to_dict()
        self.assertEqual(row["source_system"], "nflverse")
        self.assertEqual(row["source_loader"], "nflreadpy.load_player_stats")
        self.assertEqual(row["team"], "PHI")
        self.assertEqual(row["source_season"], 2014)
        self.assertEqual(row["source_week"], 1)
        self.assertTrue(row["row_hash"])
        self.assertIn("raw_payload_json", row)
        self.assertNotIn("extra_source_column", prepared.dataframe.columns)
        self.assertIn("missing_target_column", prepared.dataframe.columns)
        self.assertIsNone(row["missing_target_column"])

    def test_row_hash_excludes_loaded_at(self):
        family = SOURCE_FAMILY_REGISTRY["weekly"]
        base = pd.Series(
            {
                "season": 2014,
                "week": 1,
                "player_id": "00-abc",
                "team": "PHI",
                "loaded_at": "one",
                "row_hash": "ignore",
            }
        )
        changed = base.copy()
        changed["loaded_at"] = "two"

        hash_one = backfill._row_hash(base, family, ["season", "week", "player_id", "team", "loaded_at", "row_hash"])
        hash_two = backfill._row_hash(changed, family, ["season", "week", "player_id", "team", "loaded_at", "row_hash"])
        self.assertEqual(hash_one, hash_two)

    def test_static_source_handles_source_season_as_null(self):
        family = SOURCE_FAMILY_REGISTRY["teams"]
        source_df = pd.DataFrame([{"team_abbr": "PHI", "team_name": "Philadelphia Eagles"}])
        schema = [
            Field("team"),
            Field("team_name"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2014,
            season_end=2014,
        )

        row = prepared.dataframe.iloc[0].to_dict()
        self.assertEqual(row["team"], "PHI")
        self.assertTrue(pd.isna(row["source_season"]))

    def test_duplicate_source_keys_are_deduped_before_merge(self):
        family = SOURCE_FAMILY_REGISTRY["weekly"]
        source_df = pd.DataFrame(
            [
                {"season": 2014, "week": 1, "player_id": "00-abc", "recent_team": "PHI", "targets": 1},
                {"season": 2014, "week": 1, "player_id": "00-abc", "recent_team": "PHI", "targets": 2},
            ]
        )
        schema = [
            Field("season", "INTEGER"),
            Field("week", "INTEGER"),
            Field("player_id"),
            Field("team"),
            Field("targets", "FLOAT"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2014,
            season_end=2014,
        )

        self.assertEqual(prepared.prepared_row_count, 1)
        self.assertEqual(prepared.skipped_row_count, 1)
        self.assertIn("Deduped 1 source rows", " ".join(prepared.warnings))

    def test_ff_playerids_wide_schema_maps_to_contract_fields(self):
        family = SOURCE_FAMILY_REGISTRY["ff_playerids"]
        source_df = pd.DataFrame(
            [
                {
                    "gsis_id": "00-abc",
                    "nfl_id": "123",
                    "pfr_id": "PfrEx00",
                    "name": "Example Player",
                    "position": "WR",
                    "team": "PHI",
                    "sleeper_id": 111,
                    "mfl_id": "222",
                    "fantasy_data_id": "333",
                }
            ]
        )
        schema = [
            Field("nflverse_player_id"),
            Field("gsis_id"),
            Field("sleeper_player_id"),
            Field("fantasy_player_id"),
            Field("platform"),
            Field("platform_player_id"),
            Field("player_name"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
            Field("raw_payload_json"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2014,
            season_end=2014,
        )

        self.assertEqual(prepared.fetched_row_count, 1)
        self.assertEqual(prepared.prepared_row_count, 3)
        self.assertEqual(set(prepared.dataframe["platform"]), {"sleeper", "mfl", "fantasy_data"})
        self.assertTrue(prepared.dataframe["platform_player_id"].notna().all())
        self.assertTrue(prepared.dataframe["row_hash"].notna().all())

    def test_rosters_schema_maps_to_contract_fields(self):
        family = SOURCE_FAMILY_REGISTRY["rosters"]
        source_df = pd.DataFrame(
            [
                {
                    "season": 2014,
                    "team": "PHI",
                    "position": "WR",
                    "status": "ACT",
                    "full_name": "Example Player",
                    "gsis_id": "00-abc",
                    "week": 1,
                }
            ]
        )
        schema = [
            Field("season", "INTEGER"),
            Field("player_id"),
            Field("gsis_id"),
            Field("player_name"),
            Field("team"),
            Field("position"),
            Field("status"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2014,
            season_end=2014,
        )

        row = prepared.dataframe.iloc[0].to_dict()
        self.assertEqual(prepared.prepared_row_count, 1)
        self.assertEqual(row["player_id"], "00-abc")
        self.assertEqual(row["gsis_id"], "00-abc")
        self.assertEqual(row["player_name"], "Example Player")

    def test_rosters_weekly_schema_maps_to_contract_fields(self):
        family = SOURCE_FAMILY_REGISTRY["rosters_weekly"]
        source_df = pd.DataFrame(
            [
                {
                    "season": 2014,
                    "week": 2,
                    "team": "PHI",
                    "position": "RB",
                    "status_description_abbr": "ACT",
                    "full_name": "Weekly Player",
                    "gsis_id": "00-def",
                }
            ]
        )
        schema = [
            Field("season", "INTEGER"),
            Field("week", "INTEGER"),
            Field("player_id"),
            Field("gsis_id"),
            Field("player_name"),
            Field("team"),
            Field("position"),
            Field("status"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2014,
            season_end=2014,
        )

        row = prepared.dataframe.iloc[0].to_dict()
        self.assertEqual(prepared.prepared_row_count, 1)
        self.assertEqual(row["week"], 2)
        self.assertEqual(row["player_id"], "00-def")
        self.assertEqual(row["status"], "ACT")

    def test_snap_counts_schema_maps_to_contract_fields(self):
        family = SOURCE_FAMILY_REGISTRY["snap_counts"]
        source_df = pd.DataFrame(
            [
                {
                    "season": 2014,
                    "week": 1,
                    "game_id": "2014_01_PHI_WAS",
                    "pfr_player_id": "PfrEx00",
                    "player": "Snap Player",
                    "position": "WR",
                    "team": "PHI",
                    "offense_snaps": 40,
                    "offense_pct": 0.8,
                    "defense_snaps": 0,
                    "st_snaps": 2,
                }
            ]
        )
        schema = [
            Field("season", "INTEGER"),
            Field("week", "INTEGER"),
            Field("game_id"),
            Field("player_id"),
            Field("gsis_id"),
            Field("player_name"),
            Field("team"),
            Field("position"),
            Field("offense_snaps", "FLOAT"),
            Field("offense_pct", "FLOAT"),
            Field("defense_snaps", "FLOAT"),
            Field("st_snaps", "FLOAT"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2014,
            season_end=2014,
        )

        row = prepared.dataframe.iloc[0].to_dict()
        self.assertEqual(prepared.prepared_row_count, 1)
        self.assertEqual(row["player_id"], "PfrEx00")
        self.assertEqual(row["player_name"], "Snap Player")
        self.assertEqual(row["offense_snaps"], 40)

    def test_injuries_schema_maps_to_contract_fields(self):
        family = SOURCE_FAMILY_REGISTRY["injuries"]
        source_df = pd.DataFrame(
            [
                {
                    "season": 2025,
                    "week": 1,
                    "team": "MIA",
                    "gsis_id": "00-abc",
                    "full_name": "Injured Player",
                    "position": "WR",
                    "report_primary_injury": "Knee",
                    "report_status": "Questionable",
                    "practice_status": "Limited Participation in Practice",
                },
                {
                    "season": 2025,
                    "week": 1,
                    "team": "MIA",
                    "gsis_id": "00-def",
                    "full_name": "Practice Only",
                    "position": "RB",
                    "practice_primary_injury": "Rest",
                    "practice_status": "Did Not Participate In Practice",
                }
            ]
        )
        schema = [
            Field("season", "INTEGER"),
            Field("week", "INTEGER"),
            Field("team"),
            Field("gsis_id"),
            Field("player_name"),
            Field("position"),
            Field("report_status"),
            Field("practice_status"),
            Field("game_status"),
            Field("injury_notes"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
            Field("raw_payload_json"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2025,
            season_end=2025,
        )

        row = prepared.dataframe.iloc[0].to_dict()
        self.assertEqual(prepared.prepared_row_count, 2)
        self.assertEqual(row["player_name"], "Injured Player")
        self.assertEqual(row["game_status"], "Questionable")
        self.assertEqual(row["injury_notes"], "Knee")
        practice_row = prepared.dataframe.iloc[1].to_dict()
        self.assertIsNone(practice_row["report_status"])
        self.assertEqual(practice_row["injury_notes"], "Rest")

    def test_depth_chart_current_snapshot_lacks_historical_keys(self):
        family = SOURCE_FAMILY_REGISTRY["depth_charts"]
        source_df = pd.DataFrame(
            [
                {
                    "dt": "2026-03-14T07:32:09Z",
                    "team": "MIA",
                    "gsis_id": "00-def",
                    "player_name": "Depth Player",
                    "pos_abb": "WR",
                    "pos_rank": 2,
                }
            ]
        )
        schema = [
            Field("season", "INTEGER"),
            Field("week", "INTEGER"),
            Field("team"),
            Field("gsis_id"),
            Field("player_name"),
            Field("position"),
            Field("depth_rank", "INTEGER"),
            Field("depth_role"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
            Field("raw_payload_json"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2025,
            season_end=2025,
        )

        self.assertEqual(prepared.prepared_row_count, 0)
        self.assertIn("season=1", " ".join(prepared.warnings))
        self.assertIn("week=1", " ".join(prepared.warnings))

    def test_live_loader_dispatch_supports_injury_and_depth_families(self):
        class FakeNfl:
            @staticmethod
            def load_injuries(seasons):
                return pd.DataFrame([{"season": seasons[0], "week": 1}])

            @staticmethod
            def load_depth_charts(seasons):
                return pd.DataFrame([{"dt": "2026-03-14T07:32:09Z"}])

        with patch.dict(sys.modules, {"nflreadpy": FakeNfl}):
            injuries = backfill._call_loader(SOURCE_FAMILY_REGISTRY["injuries"], [2025])
            depth = backfill._call_loader(SOURCE_FAMILY_REGISTRY["depth_charts"], [2025])

        self.assertEqual(len(injuries), 1)
        self.assertEqual(len(depth), 1)

    def test_live_loader_dispatch_supports_ngs_fallback_families(self):
        calls = []

        class FakeNfl:
            @staticmethod
            def load_nextgen_stats(seasons, stat_type="passing"):
                calls.append((tuple(seasons), stat_type))
                return pd.DataFrame([{"season": seasons[0], "stat_type": stat_type}])

        with patch.dict(sys.modules, {"nflreadpy": FakeNfl}):
            passing = backfill._call_loader(SOURCE_FAMILY_REGISTRY["ngs_passing"], [2025])
            rushing = backfill._call_loader(SOURCE_FAMILY_REGISTRY["ngs_rushing"], [2025])
            receiving = backfill._call_loader(SOURCE_FAMILY_REGISTRY["ngs_receiving"], [2025])

        self.assertEqual(len(passing), 1)
        self.assertEqual(len(rushing), 1)
        self.assertEqual(len(receiving), 1)
        self.assertEqual(calls, [((2025,), "passing"), ((2025,), "rushing"), ((2025,), "receiving")])

    def test_weekly_missing_key_diagnostic_classifies_missing_player_id(self):
        family = SOURCE_FAMILY_REGISTRY["weekly"]
        source_df = pd.DataFrame(
            [
                {"season": 2014, "week": 1, "player_id": None, "team": "PHI", "position": None},
                {"season": 2014, "week": 1, "player_id": "00-abc", "team": "PHI", "position": "WR"},
            ]
        )
        schema = [
            Field("season", "INTEGER"),
            Field("week", "INTEGER"),
            Field("player_id"),
            Field("team"),
            Field("position"),
            Field("source_system"),
            Field("source_loader"),
            Field("source_version"),
            Field("source_season", "INTEGER"),
            Field("source_week", "INTEGER"),
            Field("source_refresh_id"),
            Field("loaded_at", "TIMESTAMP"),
            Field("loaded_by"),
            Field("row_hash"),
        ]

        prepared = backfill.prepare_rows(
            source_df,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="1.0",
            loaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            loaded_by="tester",
            season_start=2014,
            season_end=2014,
        )

        warnings = " ".join(prepared.warnings)
        self.assertEqual(prepared.prepared_row_count, 1)
        self.assertIn("player_id=1", warnings)
        self.assertIn("non-player or aggregate rows", warnings)

    def test_schema_inspection_does_not_write_bigquery_rows(self):
        args = backfill.parse_args(
            [
                "--inspect-source-schema",
                "--source-family",
                "snap_counts",
                "--season-start",
                "2014",
                "--season-end",
                "2014",
            ]
        )
        selected = backfill._selected_families(args)
        source_df = pd.DataFrame(
            [{"season": 2014, "week": 1, "game_id": "g", "pfr_player_id": "p", "team": "PHI"}]
        )
        with patch("src.nflverse_backfill._call_loader", return_value=source_df):
            with patch("src.nflverse_backfill._load_temp_and_merge", side_effect=AssertionError("write called")):
                summary = backfill.inspect_source_schema(args, selected)

        self.assertFalse(summary["wrote"])
        self.assertTrue(summary["inspect_source_schema"])
        self.assertEqual(summary["schema_summaries"][0]["fetched_row_count"], 1)

    def test_merge_sql_uses_natural_keys_and_no_broad_destructive_sql(self):
        family = SOURCE_FAMILY_REGISTRY["pbp"]
        columns = [
            "season",
            "week",
            "game_id",
            "play_id",
            "row_hash",
            "source_refresh_id",
            "loaded_at",
        ]
        sql = backfill.build_merge_sql(
            project="p",
            dataset="d",
            target_table=family.target_table,
            temp_table="tmp",
            columns=columns,
            key_fields=family.natural_key_fields,
        ).lower()

        for key in family.natural_key_fields:
            self.assertIn(f"target.`{key}` = source.`{key}`", sql)
            self.assertIn(f"target.`{key}` is null and source.`{key}` is null", sql)
        self.assertIn("merge `p.d.raw_nflverse_pbp`", sql)
        self.assertNotIn("truncate", sql)
        self.assertNotIn("delete", sql)
        self.assertNotIn("drop table", sql)
        self.assertNotIn("play_by_play", sql)

    def test_merge_sql_does_not_reference_staging_feature_or_packet_targets(self):
        sql = backfill.build_merge_sql(
            project="p",
            dataset="d",
            target_table="raw_nflverse_weekly",
            temp_table="tmp",
            columns=["season", "week", "player_id", "team", "row_hash"],
            key_fields=["season", "week", "player_id", "team"],
        ).lower()

        self.assertNotIn("stg_", sql)
        self.assertNotIn("player_week_advanced_metrics", sql)
        self.assertNotIn("pigskin_player_context_packet_current", sql)
        self.assertNotIn("cloud_run", sql)
        self.assertNotIn("scheduler", sql)

    def test_fail_closed_message_names_gate(self):
        with patch.dict(os.environ, {"ALLOW_NFLVERSE_HISTORICAL_BACKFILL": ""}, clear=False):
            with self.assertRaisesRegex(
                backfill.BackfillError,
                "ALLOW_NFLVERSE_HISTORICAL_BACKFILL must be true",
            ):
                args = backfill.parse_args(
                    [
                        "--source-family",
                        "weekly",
                        "--season-start",
                        "2014",
                        "--season-end",
                        "2014",
                        "--write",
                    ]
                )
                selected = backfill._selected_families(args)
                backfill._validate_write_request(args, selected)

    def test_2014_core_smoke_command_can_be_planned_without_loader_call(self):
        with patch("src.nflverse_backfill._call_loader", side_effect=AssertionError("loader called")):
            summary = backfill.dry_run_summary(
                backfill.parse_args(
                    [
                        "--preset",
                        "core_historical",
                        "--season-start",
                        "2014",
                        "--season-end",
                        "2014",
                        "--dry-run",
                    ]
                ),
                list(backfill.PRESETS["core_historical"]),
            )

        self.assertFalse(summary["wrote"])
        self.assertTrue(summary["dry_run"])
        self.assertIn("pbp", summary["source_families_attempted"])


if __name__ == "__main__":
    unittest.main()
