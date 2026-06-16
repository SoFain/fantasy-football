-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_score_count = 0.

SELECT
    'compat_trade_player_history_no_absurd_scores' AS validation_name,
    COUNT(*) AS invalid_score_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_player_history`
WHERE total_fantasy_points IS NULL
    OR IS_NAN(total_fantasy_points)
    OR ABS(total_fantasy_points) > 200;
