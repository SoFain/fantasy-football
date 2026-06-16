-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_weekly_metrics_reference_count = 0.

SELECT
    'compat_trade_player_history_no_raw_weekly_metrics_reference' AS validation_name,
    COUNTIF(REGEXP_CONTAINS(LOWER(view_definition), r'\bweekly_metrics\b')) AS raw_weekly_metrics_reference_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name = 'compat_trade_player_history';
