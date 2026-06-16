-- Validation helper. Render placeholders before running manually.
-- Expected result: value_delta_null_rows = 0

SELECT
    COUNTIF(value_delta IS NULL OR recommended_winner IS NULL OR confidence_score IS NULL) AS value_delta_null_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packets`;
