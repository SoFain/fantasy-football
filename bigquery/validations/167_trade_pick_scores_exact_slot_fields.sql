-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_exact_slot_rows = 0

SELECT COUNT(*) AS invalid_exact_slot_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
WHERE pick_class = 'exact_slot'
    AND (
        pick_slot IS NULL
        OR estimated_overall_pick IS NULL
        OR pick_bucket != 'exact'
        OR parse_confidence != 'high'
    );
