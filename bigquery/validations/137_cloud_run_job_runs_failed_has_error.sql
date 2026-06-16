-- Validation helper. Render placeholders before running manually.
-- Expected result: failed_rows_missing_error = 0

SELECT COUNT(*) AS failed_rows_missing_error
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs`
WHERE started_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
  AND status IN ('failed', 'trigger_failed')
  AND (error_message IS NULL OR TRIM(error_message) = '');
