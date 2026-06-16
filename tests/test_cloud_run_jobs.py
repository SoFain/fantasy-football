from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from src import cloud_run_jobs


class FakeQueryJob:
    def result(self):
        return []


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
        return FakeQueryJob()


class CloudRunJobsTests(unittest.TestCase):
    def test_known_job_mapping(self):
        self.assertEqual(
            cloud_run_jobs.map_data_ops_action_to_job("statistics_ingestion"),
            "ingest-nflverse",
        )
        self.assertEqual(
            cloud_run_jobs.map_data_ops_action_to_job("pigskin_rankings"),
            "generate-pigskin-rankings",
        )
        self.assertIsNone(cloud_run_jobs.map_data_ops_action_to_job("not-real"))

    def test_unknown_job_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown Cloud Run job"):
            cloud_run_jobs.build_job_overrides("not-real", {})

    def test_dry_run_command_generated(self):
        with patch.dict(os.environ, {
            "CLOUD_RUN_PROJECT": "test-project",
            "CLOUD_RUN_REGION": "us-central1",
        }, clear=True):
            result = cloud_run_jobs.trigger_cloud_run_job(
                "run-projections",
                {"season": 2026, "week": 1, "horizon": "weekly"},
                dry_run=True,
            )

        self.assertEqual(result["status"], "dry_run")
        self.assertIn("gcloud run jobs execute run-projections", result["command_preview"])
        self.assertIn("--job-name,run-projections", result["command_preview"])
        self.assertIn("--season,2026", result["command_preview"])

    def test_secrets_redacted_and_sensitive_env_refused(self):
        payload = cloud_run_jobs.redact_payload({"GEMINI_API_KEY": "secret", "safe": "ok"})

        self.assertEqual(payload["GEMINI_API_KEY"], "[REDACTED]")
        self.assertEqual(payload["safe"], "ok")
        with self.assertRaisesRegex(ValueError, "sensitive environment override"):
            cloud_run_jobs.build_job_overrides(
                "validate-warehouse",
                {},
                env_overrides={"GEMINI_API_KEY": "secret"},
            )

    def test_flags_default_false(self):
        self.assertFalse(cloud_run_jobs.cloud_run_jobs_feature_enabled({}))
        self.assertFalse(cloud_run_jobs.data_ops_job_trigger_allowed({}))
        self.assertFalse(cloud_run_jobs.should_use_cloud_run_jobs_for_data_ops({}))

    def test_streamlit_helper_keeps_legacy_path_when_flag_false(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("render_cloud_run_jobs_data_ops_panel()", app_source)
        self.assertIn("Cloud Run Job execution is not active", app_source)
        self.assertIn("run_subprocess_live(cmd_args", app_source)
        self.assertFalse(cloud_run_jobs.should_use_cloud_run_jobs_for_data_ops({}))

    def test_trigger_requires_explicit_allow_flag(self):
        with patch.dict(os.environ, {
            "USE_CLOUD_RUN_JOBS_FOR_DATA_OPS": "true",
            "CLOUD_RUN_JOBS_ENABLED": "true",
            "DATA_OPS_ALLOW_JOB_TRIGGER": "false",
            "CLOUD_RUN_PROJECT": "test-project",
        }, clear=True):
            with self.assertRaisesRegex(PermissionError, "requires USE_CLOUD_RUN_JOBS_FOR_DATA_OPS"):
                cloud_run_jobs.trigger_cloud_run_job(
                    "validate-warehouse",
                    {},
                    dry_run=False,
                    allow_trigger=False,
                )

    def test_argument_validation(self):
        with self.assertRaisesRegex(ValueError, "is required"):
            cloud_run_jobs.build_job_overrides("run-projections", {"season": 2026})
        with self.assertRaisesRegex(ValueError, "not allowed"):
            cloud_run_jobs.build_job_overrides("validate-warehouse", {"season": 2026})
        with self.assertRaisesRegex(ValueError, "must be one of"):
            cloud_run_jobs.build_job_overrides("run-projections", {"season": 2026, "week": 1, "horizon": "forever"})

    def test_recent_job_status_query_uses_metadata_table(self):
        client = FakeClient()

        cloud_run_jobs.get_recent_cloud_run_job_runs(limit=5, client=client)

        self.assertEqual(len(client.query_calls), 1)
        self.assertIn("cloud_run_job_runs", client.query_calls[0][0])
        params = {param.name: param.value for param in client.query_calls[0][1].query_parameters}
        self.assertEqual(params["limit"], 5)


if __name__ == "__main__":
    unittest.main()
