-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_table_count = 0

WITH expected_tables AS (
  SELECT 'raw_ffopportunity_pbp_pass' AS table_name UNION ALL
  SELECT 'raw_ffopportunity_pbp_rush' UNION ALL
  SELECT 'player_week_pbp_opportunity_metrics'
),
actual_tables AS (
  SELECT table_name
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
)
SELECT COUNT(*) AS missing_table_count
FROM expected_tables
LEFT JOIN actual_tables USING (table_name)
WHERE actual_tables.table_name IS NULL;
