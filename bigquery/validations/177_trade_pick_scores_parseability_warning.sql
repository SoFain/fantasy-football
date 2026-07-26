-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_parse_rows = 0

SELECT COUNT(*) AS invalid_parse_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
WHERE pick_class NOT IN ('exact_slot', 'round_only')
    OR parse_confidence NOT IN ('high', 'medium')
    OR pick_bucket NOT IN ('exact', 'round_only');
