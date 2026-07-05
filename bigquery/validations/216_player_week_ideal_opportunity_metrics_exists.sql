-- Validation helper. Render placeholders before running manually.
-- Expected result: table_count = 1

SELECT COUNT(*) AS table_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
WHERE table_name = 'player_week_ideal_opportunity_metrics';
