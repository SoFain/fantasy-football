-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_round_only_rows = 0

SELECT COUNT(*) AS invalid_round_only_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
WHERE pick_class = 'round_only'
    AND (
        pick_slot IS NOT NULL
        OR estimated_overall_pick IS NOT NULL
        OR pick_bucket != 'round_only'
        OR parse_confidence != 'medium'
    );
