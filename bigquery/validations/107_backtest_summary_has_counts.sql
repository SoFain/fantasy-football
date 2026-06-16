-- Validation helper. Render placeholders before running manually.
-- Expected result: empty_summary_rows = 0

SELECT COUNTIF(player_count IS NULL OR player_count <= 0) AS empty_summary_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_summary`;
