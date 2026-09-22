-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_rows = 0

WITH grain AS (
  SELECT situation_for_season, player_id_internal, COUNT(*) AS row_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_situation`
  GROUP BY situation_for_season, player_id_internal
)
SELECT COUNTIF(row_count > 1) AS duplicate_grain_rows
FROM grain;
