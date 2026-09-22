from __future__ import annotations

import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

import pandas as pd
from google.cloud import bigquery

from src.load import coerce_dataframe_to_existing_schema, load_df_to_partitioned_table
from src.pipeline import build_pipeline_plan, run_pipeline, validate_pipeline_request


class FakeLoadJob:
    def result(self):
        return None


class FakeBigQueryClient:
    project = "fantasy-football-498121"

    def __init__(self, schema):
        self.schema = schema
        self.loaded_df = None
        self.loaded_table_id = None
        self.job_config = None

    def get_table(self, _table_id):
        table = Mock()
        table.schema = self.schema
        return table

    def load_table_from_dataframe(self, df, table_id, job_config):
        self.loaded_df = df
        self.loaded_table_id = table_id
        self.job_config = job_config
        return FakeLoadJob()


class PipelinePlanTests(unittest.TestCase):
    def test_plan_only_is_non_mutating_and_season_bounded(self):
        plan = build_pipeline_plan(
            seasons=[2025],
            write_disposition="WRITE_APPEND",
            dataset_name="fantasy_football_brain",
        )

        self.assertEqual(plan["source_library"], "nflreadpy")
        self.assertEqual(plan["seasons"], [2025])
        self.assertEqual(plan["bounded_by"], "season")
        self.assertFalse(plan["week_bound_supported"])
        self.assertFalse(plan["will_extract"])
        self.assertFalse(plan["will_write_bigquery"])
        self.assertFalse(plan["will_materialize"])
        self.assertTrue(plan["live_run_behavior"]["will_extract"])
        self.assertTrue(plan["live_run_behavior"]["will_write_bigquery"])
        self.assertTrue(plan["live_run_behavior"]["will_materialize"])
        self.assertFalse(plan["destructive_risk"]["raw_load_truncate"])
        self.assertTrue(plan["destructive_risk"]["derived_create_or_replace"])
        self.assertIn("play_by_play", plan["raw_tables_to_load"])
        self.assertIn("weekly_metrics", plan["raw_tables_to_load"])
        self.assertIn("analytics_player_weekly_truth", plan["derived_tables_to_materialize"])
        self.assertIn("analytics_fraud_watch", plan["derived_tables_to_materialize"])
        self.assertEqual(plan["schema_aware_append"]["enabled_for_write_disposition"], "WRITE_APPEND")
        self.assertIn(
            "lateral_sack_player_id",
            plan["schema_aware_append"]["known_player_id_string_fields"],
        )
        self.assertIn("--seasons 2025", plan["recommended_modern_restore_command"])
        self.assertIn("WRITE_APPEND", plan["recommended_modern_restore_command"])
        self.assertIn("--ingest-only", plan["recommended_modern_restore_command"])

    def test_ingest_only_plan_skips_materialization(self):
        plan = build_pipeline_plan(
            seasons=[2025],
            write_disposition="WRITE_APPEND",
            ingest_only=True,
        )

        self.assertTrue(plan["ingest_only"])
        self.assertFalse(plan["live_run_behavior"]["will_materialize"])
        self.assertFalse(plan["destructive_risk"]["derived_create_or_replace"])

    def test_truncate_disposition_is_flagged(self):
        plan = build_pipeline_plan(seasons=[2025], write_disposition="WRITE_TRUNCATE")

        self.assertTrue(plan["destructive_risk"]["raw_load_truncate"])

    def test_unbounded_live_run_is_rejected_without_full_refresh(self):
        errors = validate_pipeline_request(
            seasons=[2020, 2021, 2022],
            seasons_were_explicit=False,
            write_disposition="WRITE_APPEND",
        )

        self.assertIn("Explicit --seasons is required unless --allow-full-refresh is set.", errors)

    def test_bounded_live_run_is_accepted(self):
        errors = validate_pipeline_request(
            seasons=[2025],
            seasons_were_explicit=True,
            write_disposition="WRITE_APPEND",
        )

        self.assertEqual(errors, [])

    def test_week_bounds_are_rejected_until_supported(self):
        errors = validate_pipeline_request(
            seasons=[2025],
            seasons_were_explicit=True,
            write_disposition="WRITE_APPEND",
            week_start=1,
            week_end=2,
        )

        self.assertIn("Week bounds are not supported by this nflreadpy ingestion path yet.", errors)

    def test_truncate_requires_full_refresh_authorization(self):
        errors = validate_pipeline_request(
            seasons=[2025],
            seasons_were_explicit=True,
            write_disposition="WRITE_TRUNCATE",
        )

        self.assertIn("WRITE_TRUNCATE requires --allow-full-refresh.", errors)

    @patch("src.pipeline.materialize_all")
    @patch("src.pipeline.load_df_to_partitioned_table")
    @patch("src.pipeline.create_dataset_if_not_exists", return_value="project.dataset")
    @patch("src.pipeline.get_bigquery_client", return_value=Mock())
    def test_ingest_only_run_skips_materialization(self, *_mocks):
        season_df = pd.DataFrame({"season": [2025]})

        patches = [
            patch("src.pipeline.get_pbp_data", return_value=season_df),
            patch("src.pipeline.get_weekly_data", return_value=season_df),
            patch("src.pipeline.get_team_data", return_value=season_df),
            patch("src.pipeline.get_draft_picks_data", return_value=season_df),
            patch("src.pipeline.get_players_data", return_value=season_df),
            patch("src.pipeline.get_contracts_data", return_value=season_df),
            patch("src.pipeline.get_ngs_passing_data", return_value=season_df),
            patch("src.pipeline.get_ngs_rushing_data", return_value=season_df),
            patch("src.pipeline.get_ngs_receiving_data", return_value=season_df),
            patch("src.pipeline.get_ftn_charting_data", return_value=season_df),
            patch("src.pipeline.get_snap_counts_data", return_value=season_df),
            patch("src.pipeline.get_injury_reports_data", return_value=season_df),
            patch("src.pipeline.get_depth_charts_data", return_value=season_df),
            patch("src.pipeline.transform_pbp_data", return_value=season_df),
            patch("src.pipeline.transform_weekly_data", return_value=season_df),
            patch("src.pipeline.transform_team_data", return_value=season_df),
            patch("src.pipeline.transform_draft_picks_data", return_value=season_df),
            patch("src.pipeline.transform_players_data", return_value=season_df),
            patch("src.pipeline.transform_contracts_data", return_value=season_df),
            patch("src.pipeline.transform_standard_seasonal_data", return_value=season_df),
            patch("src.pipeline.transform_depth_charts_data", return_value=season_df),
        ]

        with ExitStack() as stack:
            for mock_patch in patches:
                stack.enter_context(mock_patch)
            run_pipeline(
                seasons=[2025],
                write_disposition="WRITE_APPEND",
                dataset_name="fantasy_football_brain",
                ingest_only=True,
            )

        from src import pipeline

        pipeline.materialize_all.assert_not_called()

    def test_lateral_sack_player_id_integer_source_coerces_to_target_string(self):
        df = pd.DataFrame(
            {
                "season": [2025, 2025],
                "lateral_sack_player_id": [12345, None],
                "passing_yards": [250.5, 101.0],
            }
        )
        schema = [
            bigquery.SchemaField("season", "INTEGER"),
            bigquery.SchemaField("lateral_sack_player_id", "STRING"),
            bigquery.SchemaField("passing_yards", "FLOAT"),
        ]

        out, report = coerce_dataframe_to_existing_schema(
            df,
            table_name="play_by_play",
            write_disposition="WRITE_APPEND",
            existing_schema=schema,
        )

        self.assertEqual(out["lateral_sack_player_id"].astype(object).tolist()[0], "12345")
        self.assertTrue(pd.isna(out["lateral_sack_player_id"].iloc[1]))
        self.assertTrue(pd.api.types.is_float_dtype(out["passing_yards"]))
        self.assertEqual(report["safe_to_proceed"], True)
        self.assertEqual(report["fields_coerced"][0]["field"], "lateral_sack_player_id")

    def test_any_player_id_target_string_field_coerces_to_string(self):
        df = pd.DataFrame({"season": [2025], "custom_player_id": [9876]})
        schema = [
            bigquery.SchemaField("season", "INTEGER"),
            bigquery.SchemaField("custom_player_id", "STRING"),
        ]

        out, report = coerce_dataframe_to_existing_schema(
            df,
            table_name="play_by_play",
            write_disposition="WRITE_APPEND",
            existing_schema=schema,
        )

        self.assertEqual(out["custom_player_id"].astype(object).tolist(), ["9876"])
        self.assertTrue(report["fields_coerced"][0]["player_id_like"])

    def test_numeric_stat_columns_remain_numeric_when_target_is_numeric(self):
        df = pd.DataFrame({"season": [2025], "passing_yards": [275]})
        schema = [
            bigquery.SchemaField("season", "INTEGER"),
            bigquery.SchemaField("passing_yards", "FLOAT"),
        ]

        out, report = coerce_dataframe_to_existing_schema(
            df,
            table_name="play_by_play",
            write_disposition="WRITE_APPEND",
            existing_schema=schema,
        )

        self.assertTrue(pd.api.types.is_numeric_dtype(out["passing_yards"]))
        self.assertEqual(report["safe_to_proceed"], True)

    def test_incompatible_schema_mismatch_fails_clearly(self):
        df = pd.DataFrame({"season": [2025], "yards_gained": ["not-a-number"]})
        schema = [
            bigquery.SchemaField("season", "INTEGER"),
            bigquery.SchemaField("yards_gained", "FLOAT"),
        ]

        _out, report = coerce_dataframe_to_existing_schema(
            df,
            table_name="play_by_play",
            write_disposition="WRITE_APPEND",
            existing_schema=schema,
        )

        self.assertFalse(report["safe_to_proceed"])
        self.assertEqual(report["incompatible_fields"][0]["field"], "yards_gained")

    def test_append_load_uses_existing_schema_and_coerced_dataframe(self):
        schema = [
            bigquery.SchemaField("season", "INTEGER"),
            bigquery.SchemaField("lateral_sack_player_id", "STRING"),
            bigquery.SchemaField("passing_yards", "FLOAT"),
        ]
        client = FakeBigQueryClient(schema)
        df = pd.DataFrame(
            {
                "season": [2025],
                "lateral_sack_player_id": [12345],
                "passing_yards": [250.5],
            }
        )

        load_df_to_partitioned_table(
            client=client,
            df=df,
            dataset_id="fantasy-football-498121.fantasy_football_brain",
            table_name="play_by_play",
            write_disposition="WRITE_APPEND",
        )

        self.assertEqual(client.loaded_df["lateral_sack_player_id"].astype(object).tolist(), ["12345"])
        self.assertFalse(client.job_config.autodetect)
        self.assertEqual([field.name for field in client.job_config.schema], ["season", "lateral_sack_player_id", "passing_yards"])


if __name__ == "__main__":
    unittest.main()
