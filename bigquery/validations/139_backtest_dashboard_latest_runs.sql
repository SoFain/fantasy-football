-- Validation helper. Render placeholders before running manually.
-- Expected result: latest_backtest_runs should be reviewed

SELECT
    COUNT(*) AS latest_backtest_runs,
    MAX(created_at) AS latest_backtest_run_at
FROM (
    SELECT backtest_run_id, status, created_at
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_runs`
    ORDER BY created_at DESC
    LIMIT 50
);
