-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_status_rows = 0

SELECT
    COUNTIF(status NOT IN ('running', 'success', 'failed')) AS invalid_status_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs`;
