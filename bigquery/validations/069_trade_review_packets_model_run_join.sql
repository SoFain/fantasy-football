-- Validation helper. Render placeholders before running manually.
-- Expected result: orphaned_model_run_rows = 0

SELECT
    COUNTIF(p.model_run_id IS NOT NULL AND mr.model_run_id IS NULL) AS orphaned_model_run_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packets` p
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` mr
    ON p.model_run_id = mr.model_run_id;
