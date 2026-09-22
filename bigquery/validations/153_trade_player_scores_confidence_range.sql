-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_confidence_rows = 0

SELECT COUNT(*) AS invalid_confidence_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
WHERE confidence_score IS NULL
    OR confidence_score < 0
    OR confidence_score > 100;
