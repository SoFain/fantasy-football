-- Validation helper. Render placeholders before running manually.
-- Expected result: orphaned_model_run_rows = 0 for rows with model_run_id.

SELECT
    'compat_sleeper_watch_candidates_model_run_join' AS validation_name,
    COUNTIF(c.model_run_id IS NOT NULL AND mr.model_run_id IS NULL) AS orphaned_model_run_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_sleeper_watch_candidates` c
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` mr
    ON c.model_run_id = mr.model_run_id;
