-- Validation helper. Render placeholders before running manually.
-- Expected result: recent_row_count > 0 after fantasy points are materialized.

SELECT
    'compat_trade_player_history_recent_rows_exist' AS validation_name,
    COUNT(*) AS recent_row_count,
    MAX(season) AS max_season,
    MAX(week) AS max_week
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_player_history`
WHERE season >= EXTRACT(YEAR FROM CURRENT_DATE()) - 2;
