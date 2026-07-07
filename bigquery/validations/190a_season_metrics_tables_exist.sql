-- Validation helper. Render placeholders before running manually.
-- Expected result: table_count = 2

SELECT COUNT(*) AS table_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN (
    'player_season_advanced_metrics',
    'player_metric_source_coverage'
);
