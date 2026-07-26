-- Validation helper. Render placeholders before running manually.
-- Expected result: backtest_summary_rows should be reviewed

SELECT
    COUNT(*) AS backtest_summary_rows,
    COUNT(DISTINCT backtest_run_id) AS backtest_run_count,
    MAX(created_at) AS latest_summary_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_summary`;
