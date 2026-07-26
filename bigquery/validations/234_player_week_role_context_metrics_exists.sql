-- Validation: player-week role context metrics table exists.
-- Expected result: missing_table_count = 0.

SELECT COUNT(1) AS missing_table_count
FROM (
  SELECT 'player_week_role_context_metrics' AS table_name
) required_tables
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES` table_meta
  ON table_meta.table_name = required_tables.table_name
WHERE table_meta.table_name IS NULL;
