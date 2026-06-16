-- Validation helper. Render placeholders before running manually.
-- Expected result: null_actual_rows = 0

SELECT COUNTIF(actual_points IS NULL) AS null_actual_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_player_week`;
