-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_component_json = 0

SELECT COUNT(*) AS rows_missing_component_json
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
WHERE component_json IS NULL
    OR TRIM(component_json) = '';
