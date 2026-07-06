from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import pandas as pd

from src import nflverse_backfill
from src import nflverse_ngs_metrics as ngs
from src.nflverse_backfill_plan import SOURCE_FAMILY_REGISTRY


class _Done:
    def result(self):
        return []


class _FakeClient:
    def __init__(self):
        self.queries = []

    def query(self, sql, job_config=None):
        self.queries.append((sql, job_config))
        return _Done()


class _Field:
    def __init__(self, name: str, field_type: str = "STRING"):
        self.name = name
        self.field_type = field_type


class NflverseNgsMetricsTest(unittest.TestCase):
    def test_write_requires_ngs_specific_gate(self):
        with self.assertRaisesRegex(PermissionError, "ALLOW_NFLVERSE_NGS_METRICS_MATERIALIZATION"):
            ngs.materialize_ngs_metrics(client=_FakeClient(), write=True, env={})

        with self.assertRaisesRegex(PermissionError, "ALLOW_NFLVERSE_NGS_METRICS_MATERIALIZATION"):
            ngs.materialize_ngs_metrics(
                client=_FakeClient(),
                write=True,
                env={"ALLOW_RANKING_FORMULA_BACKTEST_WRITE": "true"},
            )

    def test_dry_run_does_not_query_bigquery(self):
        fake = _FakeClient()
        result = ngs.materialize_ngs_metrics(client=fake, write=False)

        self.assertTrue(result["dry_run"])
        self.assertFalse(result["write"])
        self.assertEqual(fake.queries, [])

    def test_materialization_sql_is_bounded_and_preserves_missing_ngs_flags(self):
        delete_sql = ngs.build_ngs_metrics_delete_sql(project_id="p", dataset_id="d").lower()
        insert_sql = ngs.build_ngs_metrics_insert_sql(project_id="p", dataset_id="d").lower()

        self.assertIn("where source_version = @source_version", delete_sql)
        self.assertIn("season between @season_start and @season_end", delete_sql)
        self.assertIn("raw_nflverse_ngs_receiving", insert_sql)
        self.assertIn("raw_nflverse_ngs_rushing", insert_sql)
        self.assertIn("raw_nflverse_ngs_passing", insert_sql)
        self.assertIn("week between 1 and 23", insert_sql)
        self.assertIn("ngs_expected_catch_percentage_unavailable", insert_sql)
        self.assertIn("ngs_catch_over_expected_unavailable", insert_sql)
        self.assertNotIn("truncate", insert_sql)
        self.assertNotIn("ranking_backtest_results", insert_sql)
        self.assertNotIn("ranking_formula_champions", insert_sql)
        self.assertNotIn("analytics_pigskin_rankings", insert_sql)

    def test_ngs_source_aliases_map_public_nflreadpy_columns(self):
        family = SOURCE_FAMILY_REGISTRY["ngs_receiving"]
        source = pd.DataFrame(
            [
                {
                    "season": 2025,
                    "week": 1,
                    "player_gsis_id": "00-1",
                    "player_display_name": "Test Receiver",
                    "player_position": "WR",
                    "team_abbr": "ABC",
                    "avg_expected_yac": 4.2,
                }
            ]
        )
        schema = [
            _Field("season", "INTEGER"),
            _Field("week", "INTEGER"),
            _Field("player_gsis_id"),
            _Field("player_name"),
            _Field("position"),
            _Field("team"),
            _Field("expected_yac", "FLOAT"),
            _Field("source_system"),
            _Field("source_loader"),
            _Field("source_version"),
            _Field("source_season", "INTEGER"),
            _Field("source_week", "INTEGER"),
            _Field("source_refresh_id"),
            _Field("loaded_at", "TIMESTAMP"),
            _Field("loaded_by"),
            _Field("row_hash"),
            _Field("raw_payload_json"),
        ]

        prepared = nflverse_backfill.prepare_rows(
            source,
            family,
            schema,
            source_refresh_id="refresh",
            source_version="test",
            loaded_at=pd.Timestamp("2026-01-01T00:00:00Z"),
            loaded_by="test",
            season_start=2025,
            season_end=2025,
        )

        row = prepared.dataframe.iloc[0]
        self.assertEqual(row["player_name"], "Test Receiver")
        self.assertEqual(row["position"], "WR")
        self.assertEqual(row["team"], "ABC")
        self.assertEqual(float(row["expected_yac"]), 4.2)

    def test_authorized_write_submits_delete_then_insert(self):
        fake = _FakeClient()
        ngs.materialize_ngs_metrics(
            client=fake,
            write=True,
            source_version="test_version",
            season_start=2024,
            season_end=2025,
            env={ngs.WRITE_GATE: "true"},
        )

        self.assertEqual(len(fake.queries), 2)
        self.assertIn("DELETE FROM", fake.queries[0][0])
        self.assertIn("INSERT INTO", fake.queries[1][0])


if __name__ == "__main__":
    unittest.main()
