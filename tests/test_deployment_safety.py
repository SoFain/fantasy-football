from __future__ import annotations

import unittest

from scripts import check_deployment_safety


class DeploymentSafetyTests(unittest.TestCase):
    def test_required_files_include_cloud_run_hardening_artifacts(self):
        required = set(check_deployment_safety.REQUIRED_FILES)

        self.assertIn("src/job_runner.py", required)
        self.assertIn("src/cloud_run_jobs.py", required)
        self.assertIn("scripts/deploy_cloud_run_jobs.ps1", required)
        self.assertIn("scripts/deploy_cloud_run_jobs.sh", required)
        self.assertIn("docs/rebuild/secret-manager-plan.md", required)
        self.assertIn("docs/rebuild/iam-hardening-plan.md", required)
        self.assertIn("docs/rebuild/cloud-scheduler-plan.md", required)
        self.assertIn("docs/rebuild/deployment-readiness-checklist.md", required)

    def test_feature_flags_default_off(self):
        self.assertTrue(check_deployment_safety._feature_flags_default_off())

    def test_firebase_artifact_detector(self):
        self.assertEqual(
            check_deployment_safety._firebase_artifacts(["firebase.json", "docs/readme.md"]),
            ["firebase.json"],
        )

    def test_secret_file_detector(self):
        matches = check_deployment_safety._tracked_secret_files([
            ".env",
            "config/service-account.json",
            "docs/readme.md",
        ])

        self.assertEqual(matches, [".env", "config/service-account.json"])

    def test_pigskin_sql_tool_still_removed(self):
        self.assertTrue(check_deployment_safety._pigskin_sql_tool_removed())


if __name__ == "__main__":
    unittest.main()
