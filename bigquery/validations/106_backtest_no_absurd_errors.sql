-- Validation helper. Render placeholders before running manually.
-- Expected result: absurd_error_rows = 0

SELECT COUNTIF(
    absolute_error > 100
    OR squared_error > 10000
    OR projected_points < -20
    OR actual_points < -20
) AS absurd_error_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_player_week`;
