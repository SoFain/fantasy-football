-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_source_freshness = 0

SELECT COUNT(*) AS rows_missing_source_freshness
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
WHERE source_freshness_json IS NULL
    OR TRIM(source_freshness_json) = ''
    OR NOT STARTS_WITH(TRIM(source_freshness_json), '{');
