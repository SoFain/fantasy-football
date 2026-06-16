-- Validation helper. Render placeholders before running manually.
-- Expected result: row_count > 0 after materialization.

SELECT
    'compat_sleeper_watch_candidates_recent_rows_exist' AS validation_name,
    MAX(season) AS max_season,
    MAX(week) AS max_week,
    COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_sleeper_watch_candidates`;
