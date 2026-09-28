-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_flags = 0

SELECT COUNT(*) AS rows_missing_flags
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
WHERE missing_flags_json IS NULL
    OR TRIM(missing_flags_json) = '';
