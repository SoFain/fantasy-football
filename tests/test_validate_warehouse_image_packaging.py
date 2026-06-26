from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from src import job_runner


class FakeClient:
    project = "test-project"


def parse(*extra: str):
    return job_runner.parse_args([
        "--job-name",
        "validate-warehouse",
        "--project",
        "test-project",
        "--dataset",
        "test_dataset",
        *extra,
    ])


class ValidateWarehouseImagePackagingTests(unittest.TestCase):
    def test_dockerfile_packages_validation_runner_and_sql(self):
        dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

        self.assertIn(
            "COPY scripts/run_bigquery_validations.py ./scripts/run_bigquery_validations.py",
            dockerfile,
        )
        self.assertIn(
            "COPY bigquery/validations/ ./bigquery/validations/",
            dockerfile,
        )

    def test_validate_warehouse_dispatch_uses_packaged_script_path(self):
        self.assertTrue(Path("scripts/run_bigquery_validations.py").is_file())
        self.assertTrue(Path("bigquery/validations").is_dir())

        args = parse("--pattern", "model_runs")

        with patch("src.job_runner.subprocess.run") as run:
            run.return_value.returncode = 0
            result = job_runner.dispatch_validate_warehouse(args, FakeClient())

        cmd = run.call_args.args[0]
        self.assertIn("scripts/run_bigquery_validations.py", cmd)
        self.assertIn("--run", cmd)
        self.assertIn("--pattern", cmd)
        self.assertIn("model_runs", cmd)
        self.assertEqual(result["pattern"], "model_runs")


if __name__ == "__main__":
    unittest.main()
