-- Validation helper. Render placeholders before running manually.
-- Expected result: future_leakage_warning_rows = 0
-- This flags rows whose result metadata says the target week could not be matched.

SELECT COUNTIF(
    projection_horizon = 'weekly'
    AND (
        season IS NULL
        OR week IS NULL
        OR LOWER(COALESCE(result_json, '')) LIKE '%future_leakage_warning%'
    )
) AS future_leakage_warning_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_player_week`;
