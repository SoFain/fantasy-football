-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_result_rows = 0

SELECT COUNT(*) AS duplicate_result_rows
FROM (
    SELECT backtest_run_id, candidate_id, season, week, player_id_internal, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_results`
    GROUP BY 1, 2, 3, 4, 5
    HAVING row_count > 1
);
