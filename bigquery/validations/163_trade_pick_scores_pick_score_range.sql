-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_pick_score_rows = 0

SELECT COUNT(*) AS invalid_pick_score_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
WHERE pick_score IS NULL
    OR pick_score < 0
    OR pick_score > 100;
