from __future__ import annotations

import unittest

from src import model_runs


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

    def __init__(self):
        self.insert_calls = []
        self.query_calls = []

    def insert_rows_json(self, table_id, rows):
        self.insert_calls.append((table_id, rows))
        return []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        if "__TABLES__" in sql:
            return FakeJob([
                FakeRow(
                    table_name="analytics_player_weekly_truth",
                    row_count=10,
                    last_modified_time="2026-06-15 00:00:00 UTC",
                )
            ])
        if "INFORMATION_SCHEMA.COLUMNS" in sql:
            return FakeJob([
                FakeRow(table_name="analytics_player_weekly_truth", column_name="season"),
                FakeRow(table_name="analytics_player_weekly_truth", column_name="week"),
            ])
        if "MAX(season)" in sql:
            return FakeJob([FakeRow(max_season=2025, max_week=17)])
        return FakeJob()


class ModelRunHelperTests(unittest.TestCase):
    def test_create_model_run_inserts_running_row(self):
        client = FakeClient()

        model_run_id = model_runs.create_model_run(
            client=client,
            dataset_id="test_dataset",
            model_run_id="run-123",
            run_type="rankings",
            model_name="pigskin",
            model_version="v1",
            season=2026,
            week=1,
            scoring_profile_id="ppr",
        )

        self.assertEqual(model_run_id, "run-123")
        sql, job_config = client.query_calls[0]
        self.assertIn("INSERT INTO `test-project.test_dataset.model_runs`", sql)
        self.assertIn("'running'", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["model_run_id"], "run-123")
        self.assertEqual(params["model_version"], "v1")
        self.assertEqual(params["scoring_profile_id"], "ppr")

    def test_mark_model_run_complete_sets_status_and_completed_at(self):
        client = FakeClient()

        model_runs.mark_model_run_complete(
            "run-123",
            client=client,
            dataset_id="test_dataset",
            notes="done",
        )

        sql, job_config = client.query_calls[0]
        self.assertIn("status = 'complete'", sql)
        self.assertIn("completed_at = CURRENT_TIMESTAMP()", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["model_run_id"], "run-123")
        self.assertEqual(params["notes"], "done")

    def test_mark_model_run_failed_preserves_error_message(self):
        client = FakeClient()

        model_runs.mark_model_run_failed(
            "run-123",
            "bad ranking context",
            client=client,
            dataset_id="test_dataset",
        )

        sql, job_config = client.query_calls[0]
        self.assertIn("status = 'failed'", sql)
        self.assertIn("error_message = @error_message", sql)
        params = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(params["model_run_id"], "run-123")
        self.assertEqual(params["error_message"], "bad ranking context")

    def test_create_source_freshness_snapshot_uses_bounded_metadata(self):
        client = FakeClient()

        snapshot_id = model_runs.create_source_freshness_snapshot(
            client=client,
            dataset_id="test_dataset",
            source_table_names=("analytics_player_weekly_truth", "missing_table"),
            max_rows_for_column_scan=100,
        )

        self.assertTrue(snapshot_id.startswith("freshness-"))
        self.assertTrue(any("__TABLES__" in sql for sql, _ in client.query_calls))
        self.assertTrue(any("INFORMATION_SCHEMA.COLUMNS" in sql for sql, _ in client.query_calls))
        self.assertTrue(any("INSERT INTO `test-project.test_dataset.source_freshness_snapshots`" in sql for sql, _ in client.query_calls))

    def test_source_freshness_rejects_unsafe_table_names(self):
        client = FakeClient()

        with self.assertRaises(ValueError):
            model_runs.create_source_freshness_snapshot(
                client=client,
                dataset_id="test_dataset",
                source_table_names=("weekly_metrics`; DROP TABLE x; --",),
            )


if __name__ == "__main__":
    unittest.main()
