-- Validation helper. Render placeholders before running manually.
-- Expected result: orphaned_model_run_rows = 0

SELECT
    COUNTIF(j.model_run_id IS NOT NULL AND mr.model_run_id IS NULL) AS orphaned_model_run_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.cloud_run_job_runs` j
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` mr
    ON j.model_run_id = mr.model_run_id;
