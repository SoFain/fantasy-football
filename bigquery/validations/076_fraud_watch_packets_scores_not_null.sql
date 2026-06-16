-- Validation helper. Render placeholders before running manually.
-- Expected result: score_null_rows = 0

SELECT
    COUNTIF(fraud_score IS NULL OR confidence_score IS NULL) AS score_null_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fraud_watch_packets`;
