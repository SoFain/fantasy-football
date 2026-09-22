-- Validation helper. Render placeholders before running manually.
-- Expected result: row_count > 0

SELECT COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name = 'compat_trade_player_scores_current';
