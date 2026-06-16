from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from unittest.mock import patch

from src import job_runner


class FakeJob:
    errors = None

    def result(self):
        return []


class FakeClient:
    project = "test-project"

    def __init__(self, *, query_error: Exception | None = None):
        self.insert_calls = []
        self.query_calls = []
        self.query_error = query_error

    def insert_rows_json(self, table_id, rows):
        self.insert_calls.append((table_id, rows))
        return []

    def query(self, sql, job_config=None):
        self.query_calls.append((sql, job_config))
        if self.query_error:
            raise self.query_error
        return FakeJob()


class FakeLoadClient(FakeClient):
    def __init__(self, *, query_error: Exception | None = None):
        super().__init__(query_error=query_error)
        self.load_calls = []

    def load_table_from_json(self, rows, table_id, job_config=None):
        self.load_calls.append((table_id, rows, job_config))
        return FakeJob()


def parse(*extra: str):
    return job_runner.parse_args([
        "--job-name",
        "run-backtests",
        "--project",
        "test-project",
        "--dataset",
        "test_dataset",
        *extra,
    ])


def query_params(call):
    _, job_config = call
    return {param.name: param.value for param in job_config.query_parameters}


class JobRunnerTests(unittest.TestCase):
    def test_parse_common_args(self):
        args = job_runner.parse_args([
            "--job-name",
            "run-projections",
            "--project",
            "test-project",
            "--dataset",
            "test_dataset",
            "--season",
            "2026",
            "--week",
            "3",
            "--league-id",
            "123",
            "--scoring-profile",
            "half_ppr",
            "--league-type",
            "dynasty",
            "--roster-format",
            "superflex",
            "--model-run-id",
            "model-1",
            "--dry-run",
            "--limit",
            "25",
            "--fail-fast",
        ])

        self.assertEqual(args.job_name, "run-projections")
        self.assertEqual(args.project, "test-project")
        self.assertEqual(args.dataset, "test_dataset")
        self.assertEqual(args.season, 2026)
        self.assertEqual(args.week, 3)
        self.assertEqual(args.league_id, "123")
        self.assertEqual(args.scoring_profile, "half_ppr")
        self.assertEqual(args.league_type, "dynasty")
        self.assertEqual(args.roster_format, "superflex")
        self.assertEqual(args.model_run_id, "model-1")
        self.assertTrue(args.dry_run)
        self.assertEqual(args.limit, 25)
        self.assertTrue(args.fail_fast)

    def test_all_known_job_names_have_dispatchers(self):
        self.assertEqual(set(job_runner.VALID_JOB_NAMES), set(job_runner.JOB_DISPATCHERS))
        for dispatcher in job_runner.JOB_DISPATCHERS.values():
            self.assertTrue(callable(dispatcher))

    def test_dispatches_known_job_name(self):
        client = FakeClient()
        args = parse("--dry-run")

        result = job_runner.run_job(
            args,
            client=client,
            dispatchers={"run-backtests": lambda parsed, passed_client: {"row_count": 2, "dry_run": parsed.dry_run}},
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"]["row_count"], 2)
        self.assertEqual(len(client.insert_calls), 1)
        self.assertEqual(len(client.query_calls), 1)

    def test_rejects_unknown_job_name_from_parser(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                job_runner.parse_args(["--job-name", "unknown"])

    def test_rejects_unknown_job_name_from_dispatch(self):
        args = parse()
        args.job_name = "unknown"

        with self.assertRaisesRegex(ValueError, "Unknown job name"):
            job_runner.run_job(args, client=FakeClient(), dispatchers={})

    def test_records_success_metadata(self):
        client = FakeClient()
        args = parse("--job-run-id", "job-1")

        result = job_runner.run_job(
            args,
            client=client,
            dispatchers={"run-backtests": lambda _args, _client: {"row_count": 5, "model_run_id": "model-1"}},
        )

        self.assertEqual(result["job_run_id"], "job-1")
        self.assertEqual(client.insert_calls[0][0], "test-project.test_dataset.cloud_run_job_runs")
        start_row = client.insert_calls[0][1][0]
        self.assertEqual(start_row["status"], "running")
        self.assertEqual(start_row["job_name"], "run-backtests")
        params = query_params(client.query_calls[0])
        self.assertEqual(params["status"], "success")
        self.assertEqual(params["row_count"], 5)
        self.assertEqual(params["model_run_id"], "model-1")

    def test_records_start_metadata_with_load_job_when_available(self):
        client = FakeLoadClient()
        args = parse("--job-run-id", "job-load")

        job_runner.run_job(
            args,
            client=client,
            dispatchers={"run-backtests": lambda _args, _client: {"row_count": 1}},
        )

        self.assertEqual(len(client.load_calls), 1)
        self.assertEqual(client.load_calls[0][0], "test-project.test_dataset.cloud_run_job_runs")
        self.assertEqual(client.insert_calls, [])
        self.assertEqual(len(client.query_calls), 1)

    def test_records_failure_metadata_and_reraises(self):
        client = FakeClient()
        args = parse("--job-run-id", "job-2")

        with self.assertRaisesRegex(RuntimeError, "primary failure"):
            job_runner.run_job(
                args,
                client=client,
                dispatchers={"run-backtests": lambda _args, _client: (_ for _ in ()).throw(RuntimeError("primary failure"))},
            )

        params = query_params(client.query_calls[0])
        self.assertEqual(params["status"], "failed")
        self.assertEqual(params["error_message"], "primary failure")

    def test_failed_metadata_update_does_not_mask_original_exception(self):
        args = parse("--job-run-id", "job-3")

        with patch("src.job_runner.logger.exception"):
            with self.assertRaisesRegex(RuntimeError, "primary failure"):
                job_runner.run_job(
                    args,
                    client=FakeClient(query_error=RuntimeError("metadata failure")),
                    dispatchers={"run-backtests": lambda _args, _client: (_ for _ in ()).throw(RuntimeError("primary failure"))},
                )

    def test_main_exits_nonzero_when_job_fails(self):
        with patch("src.job_runner.run_job", side_effect=RuntimeError("boom")):
            with patch("src.job_runner.logger.exception"):
                with self.assertRaises(SystemExit) as exc:
                    job_runner.main(["--job-name", "run-backtests", "--project", "test-project", "--dataset", "test_dataset"])

        self.assertEqual(exc.exception.code, 1)

    def test_dry_run_reaches_dispatcher_without_mutating_business_logic(self):
        client = FakeClient()
        args = parse("--dry-run")
        seen = {}

        def dispatcher(parsed, _client):
            seen["dry_run"] = parsed.dry_run
            return {"row_count": 0, "dry_run": parsed.dry_run}

        job_runner.run_job(args, client=client, dispatchers={"run-backtests": dispatcher})

        self.assertTrue(seen["dry_run"])
        params = query_params(client.query_calls[0])
        self.assertEqual(params["status"], "success")

    def test_generate_pigskin_rankings_dispatch_preserves_model_run_behavior(self):
        args = parse("--dry-run")
        args.job_name = "generate-pigskin-rankings"
        args.positions = "QB,WR"
        args.position_limit = 10
        args.refresh_sleeper = True

        with patch("src.generate_pigskin_rankings.parse_positions", return_value=["QB", "WR"]) as parse_positions:
            with patch("src.generate_pigskin_rankings.generate_rankings", return_value=("rank-v1", 20)) as generate:
                result = job_runner.dispatch_generate_pigskin_rankings(args, FakeClient())

        parse_positions.assert_called_once_with("QB,WR")
        generate.assert_called_once()
        call_kwargs = generate.call_args.kwargs
        self.assertEqual(call_kwargs["dataset_id"], "test_dataset")
        self.assertEqual(call_kwargs["project_id"], "test-project")
        self.assertEqual(call_kwargs["scoring_profile_id"], "ppr")
        self.assertEqual(call_kwargs["league_type_id"], "redraft")
        self.assertEqual(call_kwargs["roster_format_id"], "one_qb")
        self.assertEqual(call_kwargs["positions"], ["QB", "WR"])
        self.assertEqual(call_kwargs["position_limit"], 10)
        self.assertTrue(call_kwargs["refresh_sleeper"])
        self.assertTrue(call_kwargs["dry_run"])
        self.assertEqual(result["ranking_version"], "rank-v1")
        self.assertEqual(result["row_count"], 20)

    def test_run_projections_dispatch_passes_horizon_and_context(self):
        args = parse("--season", "2026", "--week", "4", "--horizon", "ros", "--dry-run", "--limit", "7")
        args.job_name = "run-projections"

        with patch("src.projection_engine.run_projection", return_value={
            "projection_rows": 7,
            "ranking_rows": 7,
            "model_run_id": "dry-run",
            "source_freshness_snapshot_id": "dry-run",
            "feature_config_version_id": "projection-v1",
        }) as run_projection:
            result = job_runner.dispatch_run_projections(args, FakeClient())

        run_projection.assert_called_once()
        call_kwargs = run_projection.call_args.kwargs
        self.assertEqual(call_kwargs["horizon"], "ros")
        self.assertEqual(call_kwargs["season"], 2026)
        self.assertEqual(call_kwargs["week"], 4)
        self.assertEqual(call_kwargs["scoring_profile_id"], "ppr")
        self.assertEqual(call_kwargs["league_type_id"], "redraft")
        self.assertEqual(call_kwargs["roster_format_id"], "one_qb")
        self.assertTrue(call_kwargs["dry_run"])
        self.assertEqual(call_kwargs["limit"], 7)
        self.assertEqual(call_kwargs["dataset_id"], "test_dataset")
        self.assertEqual(result["row_count"], 7)
        self.assertEqual(result["model_run_id"], "dry-run")

    def test_run_backtests_dispatch_passes_window_and_context(self):
        args = parse("--season-start", "2023", "--season-end", "2024", "--week-start", "1", "--week-end", "17", "--dry-run")
        args.job_name = "run-backtests"

        with patch("src.backtesting.run_backtest", return_value={
            "backtest_run_id": "dry-run",
            "model_run_id": None,
            "status": "dry_run",
            "player_week_rows": 20,
            "summary_rows": 4,
            "calibration_rows": 12,
            "missing_data_flags": [],
        }) as run_backtest:
            result = job_runner.dispatch_run_backtests(args, FakeClient())

        run_backtest.assert_called_once()
        call_kwargs = run_backtest.call_args.kwargs
        self.assertEqual(call_kwargs["season_start"], 2023)
        self.assertEqual(call_kwargs["season_end"], 2024)
        self.assertEqual(call_kwargs["week_start"], 1)
        self.assertEqual(call_kwargs["week_end"], 17)
        self.assertTrue(call_kwargs["dry_run"])
        self.assertEqual(call_kwargs["dataset_id"], "test_dataset")
        self.assertEqual(result["row_count"], 20)
        self.assertEqual(result["backtest_run_id"], "dry-run")

    def test_validate_warehouse_dispatch_supports_pattern(self):
        args = parse("--dry-run", "--pattern", "^096_")
        args.job_name = "validate-warehouse"

        with patch("src.job_runner.subprocess.run") as run:
            run.return_value.returncode = 0
            result = job_runner.dispatch_validate_warehouse(args, FakeClient())

        cmd = run.call_args.args[0]
        self.assertIn("--dry-run", cmd)
        self.assertIn("--pattern", cmd)
        self.assertIn("^096_", cmd)
        self.assertEqual(result["pattern"], "^096_")

    def test_generate_content_briefs_dry_run_does_not_call_builder(self):
        args = parse("--season", "2026", "--brief-type", "fraud_watch_show", "--dry-run")
        args.job_name = "generate-content-briefs"

        with patch("src.job_runner._call_module_main") as call_module:
            result = job_runner.dispatch_generate_content_briefs(args, FakeClient())

        call_module.assert_not_called()
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["brief_type"], "fraud_watch_show")
        self.assertEqual(result["season"], 2026)

    def test_grade_claims_dispatch_passes_context(self):
        args = parse("--season", "2026", "--week", "3", "--claim-id", "claim-1", "--dry-run")
        args.job_name = "grade-claims"

        with patch("src.claim_grading.run_claim_grading", return_value={
            "run": {"claim_grading_run_id": "grade-run-1"},
            "grade_count": 3,
            "scorecard_count": 2,
        }) as run_claim_grading:
            result = job_runner.dispatch_grade_claims(args, FakeClient())

        run_claim_grading.assert_called_once()
        call_kwargs = run_claim_grading.call_args.kwargs
        self.assertEqual(call_kwargs["claim_id"], "claim-1")
        self.assertEqual(call_kwargs["season"], 2026)
        self.assertEqual(call_kwargs["week"], 3)
        self.assertEqual(call_kwargs["scoring_profile_id"], "ppr")
        self.assertEqual(call_kwargs["league_type_id"], "redraft")
        self.assertEqual(call_kwargs["roster_format_id"], "one_qb")
        self.assertTrue(call_kwargs["dry_run"])
        self.assertEqual(call_kwargs["dataset_id"], "test_dataset")
        self.assertEqual(result["row_count"], 3)
        self.assertEqual(result["claim_grading_run_id"], "grade-run-1")

    def test_no_disallowed_platform_artifacts_added(self):
        touched_paths = [
            Path("src/job_runner.py"),
            Path("bigquery/migrations/0019__cloud_run_job_runs.sql"),
            Path("docs/rebuild/cloud-run-jobs.md"),
            Path("docs/rebuild/cloud-scheduler-plan.md"),
        ]
        disallowed = "fire" + "base"

        for path in touched_paths:
            self.assertTrue(path.exists(), f"Missing expected artifact: {path}")
            self.assertNotIn(disallowed, path.as_posix().lower())


if __name__ == "__main__":
    unittest.main()
