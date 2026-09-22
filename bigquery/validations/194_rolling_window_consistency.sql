-- Validation helper. Render placeholders before running manually.
-- Expected result: review

SELECT
    COUNT(*) AS current_player_rows,
    COUNTIF(sample_size_flags IS NULL) AS rows_missing_sample_size_flags
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_recent_advanced_metrics_current`;
