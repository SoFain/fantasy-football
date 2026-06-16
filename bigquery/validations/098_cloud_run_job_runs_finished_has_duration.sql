-- Validation helper. Render placeholders before running manually.
-- Expected result: finished_without_duration_rows = 0

SELECT
    COUNTIF(status IN ('success', 'failed') AND (finished_at IS NULL OR duration_seconds IS NULL)) AS finished_without_duration_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs`;
