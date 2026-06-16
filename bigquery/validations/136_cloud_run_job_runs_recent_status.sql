-- Validation helper. Render placeholders before running manually.
-- Expected result: recent_rows_missing_status = 0

SELECT COUNT(*) AS recent_rows_missing_status
FROM (
    SELECT job_run_id, job_name, status
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs`
    WHERE started_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    ORDER BY started_at DESC
    LIMIT 200
)
WHERE job_run_id IS NULL
   OR job_name IS NULL
   OR status IS NULL;
