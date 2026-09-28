-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_trade_score_rows = 0

SELECT COUNT(*) AS invalid_trade_score_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
WHERE trade_score IS NULL
    OR trade_score < 0
    OR trade_score > 100;
