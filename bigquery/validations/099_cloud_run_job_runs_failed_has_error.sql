-- Validation helper. Render placeholders before running manually.
-- Expected result: failed_without_error_rows = 0

SELECT
    COUNTIF(status = 'failed' AND (error_message IS NULL OR error_message = '')) AS failed_without_error_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs`;
