-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_score_rows = 0

SELECT COUNT(*) AS invalid_score_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_results`
WHERE (predicted_score IS NOT NULL AND (predicted_score < 0 OR predicted_score > 100))
   OR (win_rate IS NOT NULL AND (win_rate < 0 OR win_rate > 1))
   OR (predicted_rank_position IS NOT NULL AND predicted_rank_position < 1)
   OR (actual_rank_position IS NOT NULL AND actual_rank_position < 1);
