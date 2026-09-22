-- Validation helper. Render placeholders before running manually.
-- Expected result: denominator_flag_warning_rows = 0

SELECT COUNT(*) AS denominator_flag_warning_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
WHERE (
        target_share IS NULL
        OR air_yards_share IS NULL
        OR opportunity_share IS NULL
    )
    AND (
        missing_data_flags IS NULL
        OR NOT REGEXP_CONTAINS(LOWER(missing_data_flags), r'(denominator|missing|sample)')
    );
