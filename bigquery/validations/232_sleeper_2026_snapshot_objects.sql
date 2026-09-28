-- Validation: Sleeper 2026 snapshot table and current context view exist.
-- Expected result: missing_object_count = 0.

WITH required_objects AS (
  SELECT 'raw_sleeper_players_snapshot' AS table_name
  UNION ALL
  SELECT 'sleeper_player_context_current' AS table_name
),
existing_objects AS (
  SELECT table_name
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
  WHERE table_name IN ('raw_sleeper_players_snapshot', 'sleeper_player_context_current')
)
SELECT COUNT(1) AS missing_object_count
FROM required_objects
LEFT JOIN existing_objects
  USING (table_name)
WHERE existing_objects.table_name IS NULL;
