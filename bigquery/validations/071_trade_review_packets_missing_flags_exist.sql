-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_flags_null_rows = 0

SELECT
    COUNTIF(missing_data_flags IS NULL) AS missing_flags_null_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packets`;
