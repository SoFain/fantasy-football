-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_job_run_rows = 0

WITH grain AS (
    SELECT job_run_id, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs`
    GROUP BY job_run_id
)
SELECT COUNTIF(row_count > 1) AS duplicate_job_run_rows
FROM grain;
