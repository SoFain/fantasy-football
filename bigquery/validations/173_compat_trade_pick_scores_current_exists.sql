-- Validation helper. Render placeholders before running manually.
-- Expected result: view_count = 1

SELECT COUNT(*) AS view_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name = 'compat_trade_pick_scores_current';
